"""Bounded post-commit Telegram delivery with repository-local failure state."""

from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from papertrader.config import Settings
from papertrader.issues import record_issue, resolve_issue
from papertrader.tables import read_table
from papertrader.utils import CanonicalValueError, stable_id

TELEGRAM_MARKDOWN_V2_SPECIAL = "_*[]()~`>#+-=|{}.!\\"
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
CHAT_ID = re.compile(r"^(?:-?[0-9]{1,20}|@[A-Za-z0-9_]{5,32})$")
REPORT_PATH = re.compile(r"^data/wiki/daily-reports/daily-report_[0-9]{8}\.md$")
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
REPOSITORY_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMMITTED_REPORT_URL = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repository>[A-Za-z0-9_.-]+)/"
    r"blob/(?P<commit>[0-9a-f]{40})/"
    r"data/wiki/daily-reports/daily-report_[0-9]{8}\.md$"
)
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\n]*?))?\]\]")
MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^)\n]+)\)")
INVESTOR_BRIEF_START = "<!-- papertrader-investor-brief:start -->"
INVESTOR_BRIEF_END = "<!-- papertrader-investor-brief:end -->"
DELIVERY_ISSUE_TITLE = "Telegram delivery unavailable"


class TelegramDeliveryError(RuntimeError):
    """Raised for a transport or Telegram API rejection."""


class TelegramTransport(Protocol):
    """Minimal injectable boundary around Telegram's HTTPS endpoint."""

    def send(
        self,
        token: str,
        payload: Mapping[str, str],
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]: ...


class UrllibTelegramTransport:
    """Send one form-encoded rich message using only the Python standard library."""

    def _request(
        self,
        token: str,
        method: str,
        payload: Mapping[str, str],
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        endpoint = f"https://api.telegram.org/bot{token}/{method}"
        request = urllib.request.Request(
            endpoint,
            data=urllib.parse.urlencode(payload).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise TelegramDeliveryError(
                f"Telegram HTTP {exc.code}: {' '.join(body.split())[:500]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise TelegramDeliveryError(f"Telegram transport failed: {exc.reason}") from exc
        try:
            value = json.loads(body.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise TelegramDeliveryError("Telegram returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise TelegramDeliveryError("Telegram returned a non-object response")
        return value

    def preflight(self, token: str, chat_id: str, *, timeout_seconds: int) -> None:
        """Verify the bot credential and destination without sending a message."""

        for method, payload in (("getMe", {}), ("getChat", {"chat_id": chat_id})):
            response = self._request(token, method, payload, timeout_seconds=timeout_seconds)
            if response.get("ok") is not True:
                raise TelegramDeliveryError(
                    str(response.get("description", f"Telegram {method} preflight failed"))
                )

    def send(
        self,
        token: str,
        payload: Mapping[str, str],
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        return self._request(
            token,
            "sendRichMessage",
            payload,
            timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True, slots=True)
class TelegramDeliveryResult:
    """Non-sensitive outcome suitable for workflow output and tests."""

    status: str
    commit_sha: str
    report_path: str
    chunks_sent: int
    total_chunks: int
    issue_id: str
    error: str


def escape_markdown_v2(value: str) -> str:
    """Escape every Telegram MarkdownV2 metacharacter exactly once."""

    return "".join(
        f"\\{character}" if character in TELEGRAM_MARKDOWN_V2_SPECIAL else character
        for character in value
    )


def _trailing_escape_is_open(value: str) -> bool:
    count = 0
    for character in reversed(value):
        if character != "\\":
            break
        count += 1
    return count % 2 == 1


def split_message(value: str, *, limit: int = 4096) -> tuple[str, ...]:
    """Split losslessly while avoiding an open MarkdownV2 escape at a boundary."""

    if limit <= 0:
        raise ValueError("message limit must be positive")
    if not value:
        return ("",)
    chunks: list[str] = []
    remaining = value
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit
        else:
            split_at += 1
        while split_at > 0 and _trailing_escape_is_open(remaining[:split_at]):
            split_at -= 1
        if split_at <= 0:
            raise ValueError("message limit cannot preserve a Markdown escape sequence")
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:]
    chunks.append(remaining)
    return tuple(chunks)


def _report_markdown(report: str, *, committed_url: str) -> str:
    if report.startswith("---\n") and "\n---\n" in report[4:]:
        _, report = report[4:].split("\n---\n", maxsplit=1)
    start_count = report.count(INVESTOR_BRIEF_START)
    end_count = report.count(INVESTOR_BRIEF_END)
    if start_count != end_count or start_count > 1:
        raise CanonicalValueError("committed report has invalid investor-brief markers")
    if start_count == 1:
        start = report.index(INVESTOR_BRIEF_START) + len(INVESTOR_BRIEF_START)
        end = report.index(INVESTOR_BRIEF_END, start)
        report = report[start:end]
    report = report.strip()
    match = COMMITTED_REPORT_URL.fullmatch(committed_url)
    if match is None:
        raise CanonicalValueError("committed report URL is not canonical")
    owner = match.group("owner")
    repository = match.group("repository")
    if repository.casefold() == f"{owner}.github.io".casefold():
        pages_base = f"https://{repository.casefold()}"
    else:
        pages_base = (
            f"https://{owner.casefold()}.github.io/{urllib.parse.quote(repository, safe='')}"
        )

    def pages_url(target: str) -> str | None:
        raw_path, separator, fragment = target.partition("#")
        normalized = raw_path.strip().removesuffix(".md")
        path = Path(normalized)
        if (
            not normalized
            or path.is_absolute()
            or ".." in path.parts
            or any(marker in normalized for marker in "\r\n")
        ):
            return None
        suffix = "" if normalized == "index" else f"/{urllib.parse.quote(normalized, safe='/')}"
        url = f"{pages_base}{suffix}"
        if separator and fragment:
            url += f"#{urllib.parse.quote(fragment, safe='-_.')}"
        return url

    def replace_wikilink(link: re.Match[str]) -> str:
        target = link.group(1).strip().removesuffix(".md")
        if not target or ".." in Path(target).parts or target.startswith("/"):
            return link.group(0)
        label = (link.group(2) or Path(target).name).strip()
        label = label.replace("[", "\\[").replace("]", "\\]")
        url = pages_url(target)
        if url is None:
            return link.group(0)
        return f"[{label}]({url})"

    report = WIKI_LINK.sub(replace_wikilink, report)

    def replace_markdown_link(link: re.Match[str]) -> str:
        target = link.group(2).strip()
        if urllib.parse.urlsplit(target).scheme or target.startswith(("/", "#")):
            return link.group(0)
        url = pages_url(target)
        return f"[{link.group(1)}]({url})" if url is not None else link.group(0)

    report = MARKDOWN_LINK.sub(replace_markdown_link, report)
    report_path = committed_url.rsplit("/data/wiki/", maxsplit=1)[1].removesuffix(".md")
    public_report_url = pages_url(report_path)
    assert public_report_url is not None
    return f"{report}\n\n[View the daily report]({public_report_url})"


def _split_rich_markdown(value: str, *, limit: int) -> tuple[str, ...]:
    """Pack complete Markdown blocks so formatting never spans Telegram messages."""

    if limit <= 0:
        raise ValueError("message limit must be positive")
    blocks = re.split(r"\n{2,}", value)
    chunks: list[str] = []
    current = ""
    for block in blocks:
        if not block:
            continue
        candidates = (block,) if len(block) <= limit else split_message(block, limit=limit)
        for candidate in candidates:
            separator = "\n\n" if current else ""
            if len(current) + len(separator) + len(candidate) <= limit:
                current += separator + candidate
                continue
            if current:
                chunks.append(current)
            current = candidate
    if current:
        chunks.append(current)
    return tuple(chunks) or ("",)


def telegram_messages(
    report: str,
    *,
    committed_url: str,
    limit: int = 32768,
) -> tuple[str, ...]:
    """Build bounded rich Markdown whose internal links resolve to GitHub Pages."""

    markdown = _report_markdown(report, committed_url=committed_url)
    return _split_rich_markdown(markdown, limit=limit)


def _committed_report(
    repository_root: Path,
    *,
    commit_sha: str,
    report_path: str,
) -> str:
    if not COMMIT_SHA.fullmatch(commit_sha):
        raise CanonicalValueError("Telegram commit SHA must contain 40 lowercase hex characters")
    if not REPORT_PATH.fullmatch(report_path):
        raise CanonicalValueError("Telegram report path is not canonical")
    result = subprocess.run(
        ["git", "show", f"{commit_sha}:{report_path}"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        raise CanonicalValueError(f"committed Telegram report is unavailable: {error}")
    try:
        report = result.stdout.decode("utf-8")
    except UnicodeError as exc:
        raise CanonicalValueError("committed Telegram report is not UTF-8") from exc
    if not report.strip():
        raise CanonicalValueError("committed Telegram report is empty")
    return report


def committed_run_report_path(repository_root: Path, *, commit_sha: str, run_id: str) -> str:
    """Resolve a completed run's canonical report from the exact selected commit."""

    if not COMMIT_SHA.fullmatch(commit_sha) or not RUN_ID.fullmatch(run_id):
        raise CanonicalValueError("committed run identity is not canonical")
    manifest_path = f"data/runs/{run_id}/daily_run.json"
    result = subprocess.run(
        ["git", "show", f"{commit_sha}:{manifest_path}"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise CanonicalValueError("committed completed-run manifest is unavailable")
    try:
        value = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CanonicalValueError("committed completed-run manifest is invalid") from exc
    if (
        not isinstance(value, dict)
        or value.get("run_id") != run_id
        or value.get("status") not in {"succeeded", "degraded"}
        or not isinstance(value.get("report_path"), str)
        or not REPORT_PATH.fullmatch(value["report_path"])
    ):
        raise CanonicalValueError("committed run does not identify a completed canonical report")
    report_path = value["report_path"]
    assert isinstance(report_path, str)
    return report_path


def _safe_error(error: BaseException | str, *secrets: str) -> str:
    value = " ".join(str(error).split())
    for secret in secrets:
        if secret:
            value = value.replace(secret, "<redacted>")
    return value[:1000] or "unknown Telegram delivery failure"


def _delivery_issue(repository_root: Path) -> Mapping[str, str] | None:
    issue_id = stable_id("issue", DELIVERY_ISSUE_TITLE.casefold(), "")
    return next(
        (row for row in read_table(repository_root, "issues") if row["issue_id"] == issue_id),
        None,
    )


def _resume_chunk(issue: Mapping[str, str] | None, commit_sha: str, total_chunks: int) -> int:
    if issue is None or issue["status"] != "open":
        return 0
    if f"commit={commit_sha}" not in issue["description"]:
        return 0
    match = re.search(r"(?:^| )next_chunk=([0-9]+)(?: |$)", issue["description"])
    if match is None:
        return 0
    value = int(match.group(1))
    return value if 0 <= value < total_chunks else 0


def deliver_committed_report(
    repository_root: Path,
    settings: Settings,
    *,
    commit_sha: str,
    report_path: str,
    repository_url: str,
    run_id: str,
    token: str,
    chat_id: str,
    transport: TelegramTransport | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    now: datetime | None = None,
) -> TelegramDeliveryResult:
    """Deliver one exact committed report and retain a bounded retry cursor on failure."""

    if not REPOSITORY_URL.fullmatch(repository_url):
        raise CanonicalValueError("Telegram repository URL must identify a github.com repository")
    report = _committed_report(
        repository_root,
        commit_sha=commit_sha,
        report_path=report_path,
    )
    committed_url = (
        f"{repository_url}/blob/{commit_sha}/{urllib.parse.quote(report_path, safe='/')}"
    )
    messages = telegram_messages(
        report,
        committed_url=committed_url,
        limit=settings.telegram.message_limit,
    )
    prior_issue = _delivery_issue(repository_root)
    start_at = _resume_chunk(prior_issue, commit_sha, len(messages))
    selected_transport = transport or UrllibTelegramTransport()
    sent = 0
    failure = ""
    failed_at = start_at
    if not token or not CHAT_ID.fullmatch(chat_id):
        failure = "Telegram bot token and canonical chat ID are required"
    else:
        preflight = getattr(selected_transport, "preflight", None)
        if callable(preflight):
            try:
                preflight(
                    token,
                    chat_id,
                    timeout_seconds=settings.telegram.timeout_seconds,
                )
            except (OSError, TelegramDeliveryError, ValueError) as exc:
                failure = _safe_error(exc, token, chat_id)
        for index in range(start_at, len(messages)):
            if failure:
                break
            failed_at = index
            message_failure = ""
            for attempt in range(1, settings.telegram.maximum_attempts + 1):
                try:
                    response = selected_transport.send(
                        token,
                        {
                            "chat_id": chat_id,
                            "rich_message": json.dumps(
                                {"markdown": messages[index]},
                                ensure_ascii=False,
                                separators=(",", ":"),
                            ),
                        },
                        timeout_seconds=settings.telegram.timeout_seconds,
                    )
                    if response.get("ok") is not True:
                        description = response.get("description", "Telegram rejected the message")
                        raise TelegramDeliveryError(str(description))
                    sent += 1
                    message_failure = ""
                    break
                except (OSError, TelegramDeliveryError, ValueError) as exc:
                    message_failure = _safe_error(exc, token, chat_id)
                    if attempt < settings.telegram.maximum_attempts:
                        sleeper(float(2 ** (attempt - 1)))
            if message_failure:
                failure = message_failure
                break
    if failure:
        issue_id = record_issue(
            repository_root,
            severity="warning",
            title=DELIVERY_ISSUE_TITLE,
            description=(
                f"report={report_path} commit={commit_sha} next_chunk={failed_at} "
                f"total_chunks={len(messages)} error={failure}"
            ),
            owner="delivery",
            related_run_id=run_id,
            now=now,
        )
        return TelegramDeliveryResult(
            status="failed",
            commit_sha=commit_sha,
            report_path=report_path,
            chunks_sent=sent,
            total_chunks=len(messages),
            issue_id=issue_id,
            error=failure,
        )
    issue_id = ""
    open_delivery_issues = [
        row
        for row in read_table(repository_root, "issues")
        if row["status"] == "open"
        and row["owner"] == "delivery"
        and (
            row["title"] == DELIVERY_ISSUE_TITLE
            or row["title"].startswith("Telegram delivery failed:")
        )
    ]
    for issue in open_delivery_issues:
        issue_id = issue["issue_id"] if issue["title"] == DELIVERY_ISSUE_TITLE else issue_id
        resolve_issue(
            repository_root,
            issue["issue_id"],
            f"Latest committed report {commit_sha} delivered successfully; "
            "older reports were not replayed.",
            now=now,
        )
    return TelegramDeliveryResult(
        status="sent",
        commit_sha=commit_sha,
        report_path=report_path,
        chunks_sent=sent,
        total_chunks=len(messages),
        issue_id=issue_id,
        error="",
    )

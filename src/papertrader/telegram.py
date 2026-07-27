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
REPOSITORY_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMMITTED_REPORT_URL = re.compile(
    r"^(https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/blob/[0-9a-f]{40})/"
    r"data/wiki/daily-reports/daily-report_[0-9]{8}\.md$"
)
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\n]*?))?\]\]")


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

    def send(
        self,
        token: str,
        payload: Mapping[str, str],
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        endpoint = f"https://api.telegram.org/bot{token}/sendRichMessage"
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
    report = report.strip()
    match = COMMITTED_REPORT_URL.fullmatch(committed_url)
    if match is None:
        raise CanonicalValueError("committed report URL is not canonical")
    wiki_base = f"{match.group(1)}/data/wiki"

    def replace_wikilink(link: re.Match[str]) -> str:
        target = link.group(1).strip().removesuffix(".md")
        if not target or ".." in Path(target).parts or target.startswith("/"):
            return link.group(0)
        label = (link.group(2) or Path(target).name).strip()
        label = label.replace("[", "\\[").replace("]", "\\]")
        url = f"{wiki_base}/{urllib.parse.quote(target, safe='/')}.md"
        return f"[{label}]({url})"

    report = WIKI_LINK.sub(replace_wikilink, report)
    return f"{report}\n\n[View the committed report]({committed_url})"


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
    """Build bounded GitHub-compatible Markdown for Telegram rich messages."""

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


def _safe_error(error: BaseException | str, *secrets: str) -> str:
    value = " ".join(str(error).split())
    for secret in secrets:
        if secret:
            value = value.replace(secret, "<redacted>")
    return value[:1000] or "unknown Telegram delivery failure"


def _delivery_issue(repository_root: Path, commit_sha: str) -> Mapping[str, str] | None:
    issue_id = stable_id("issue", f"telegram delivery failed: {commit_sha}", "")
    return next(
        (row for row in read_table(repository_root, "issues") if row["issue_id"] == issue_id),
        None,
    )


def _resume_chunk(issue: Mapping[str, str] | None, total_chunks: int) -> int:
    if issue is None or issue["status"] != "open":
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
    title = f"Telegram delivery failed: {commit_sha}"
    prior_issue = _delivery_issue(repository_root, commit_sha)
    start_at = _resume_chunk(prior_issue, len(messages))
    selected_transport = transport or UrllibTelegramTransport()
    sent = 0
    failure = ""
    failed_at = start_at
    if not token or not CHAT_ID.fullmatch(chat_id):
        failure = "Telegram bot token and canonical chat ID are required"
    else:
        for index in range(start_at, len(messages)):
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
            title=title,
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
    if prior_issue is not None and prior_issue["status"] == "open":
        issue_id = prior_issue["issue_id"]
        resolve_issue(
            repository_root,
            issue_id,
            f"Committed report delivered in {len(messages)} chunks.",
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

"""Bounded post-commit Telegram delivery with repository-local failure state."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from papertrader.config import Settings
from papertrader.issues import record_issue, resolve_issue
from papertrader.podcast import PodcastError, spoken_transcript
from papertrader.tables import read_table
from papertrader.utils import CanonicalValueError, content_hash, stable_id

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
AUDIO_DELIVERY_ISSUE_TITLE = "Telegram podcast audio delivery unavailable"
SCRIPT_DELIVERY_ISSUE_TITLE = "Telegram podcast script delivery unavailable"
PODCAST_PATH = re.compile(r"^data/wiki/podcasts/daily-podcast_[0-9]{8}T[0-9]{6}Z\.md$")


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

    def send_audio(
        self,
        token: str,
        payload: Mapping[str, str],
        audio_path: Path,
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

    def send_audio(
        self,
        token: str,
        payload: Mapping[str, str],
        audio_path: Path,
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        """Send one bounded MP3 using Telegram's multipart sendAudio endpoint."""

        boundary = f"papertrader-{hashlib.sha256(audio_path.name.encode()).hexdigest()[:24]}"
        body = bytearray()
        for name, value in sorted(payload.items()):
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            body.extend(value.encode("utf-8"))
            body.extend(b"\r\n")
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            (
                f'Content-Disposition: form-data; name="audio"; filename="{audio_path.name}"\r\n'
            ).encode()
        )
        media_type = mimetypes.guess_type(audio_path.name)[0] or "audio/mpeg"
        body.extend(f"Content-Type: {media_type}\r\n\r\n".encode())
        body.extend(audio_path.read_bytes())
        body.extend(f"\r\n--{boundary}--\r\n".encode())
        endpoint = f"https://api.telegram.org/bot{token}/sendAudio"
        request = urllib.request.Request(
            endpoint,
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                response_body = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise TelegramDeliveryError(
                f"Telegram HTTP {exc.code}: {' '.join(detail.split())[:500]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise TelegramDeliveryError(f"Telegram transport failed: {exc.reason}") from exc
        try:
            value = json.loads(response_body.decode("utf-8"))
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


@dataclass(frozen=True, slots=True)
class TelegramAudioDeliveryResult:
    status: str
    daily_cycle_id: str
    script_commit: str
    audio_sha256: str
    issue_id: str
    error: str


@dataclass(frozen=True, slots=True)
class TelegramPodcastScriptDeliveryResult:
    status: str
    daily_cycle_id: str
    script_commit: str
    script_path: str
    chunks_sent: int
    total_chunks: int
    issue_id: str
    error: str


def record_podcast_audio_failure(
    repository_root: Path,
    *,
    daily_cycle_id: str,
    script_commit: str,
    error: str,
    now: datetime | None = None,
) -> TelegramAudioDeliveryResult:
    """Persist one stable latest-only issue for a failed ephemeral audio boundary."""

    if not RUN_ID.fullmatch(daily_cycle_id) or not COMMIT_SHA.fullmatch(script_commit):
        raise CanonicalValueError("podcast audio failure identity is invalid")
    safe_error = " ".join(error.split())[:500]
    if not safe_error:
        raise CanonicalValueError("podcast audio failure requires a reason")
    issue_id = record_issue(
        repository_root,
        severity="warning",
        title=AUDIO_DELIVERY_ISSUE_TITLE,
        description=(f"cycle={daily_cycle_id} commit={script_commit} error={safe_error}"),
        owner="delivery",
        related_run_id=daily_cycle_id,
        now=now,
    )
    return TelegramAudioDeliveryResult(
        "failed", daily_cycle_id, script_commit, "", issue_id, safe_error
    )


def record_podcast_script_failure(
    repository_root: Path,
    *,
    daily_cycle_id: str,
    script_commit: str,
    error: str,
    now: datetime | None = None,
) -> TelegramPodcastScriptDeliveryResult:
    """Persist redacted retry state when committed-script delivery cannot start."""

    if not RUN_ID.fullmatch(daily_cycle_id) or not COMMIT_SHA.fullmatch(script_commit):
        raise CanonicalValueError("podcast script failure identity is invalid")
    safe_error = " ".join(error.split())[:500]
    if not safe_error:
        raise CanonicalValueError("podcast script failure requires a reason")
    issue_id = record_issue(
        repository_root,
        severity="warning",
        title=SCRIPT_DELIVERY_ISSUE_TITLE,
        description=(f"cycle={daily_cycle_id} commit={script_commit} error={safe_error}"),
        owner="delivery",
        related_run_id=daily_cycle_id,
        now=now,
    )
    return TelegramPodcastScriptDeliveryResult(
        "failed", daily_cycle_id, script_commit, "", 0, 0, issue_id, safe_error
    )


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


def _committed_podcast_script(
    repository_root: Path,
    *,
    commit_sha: str,
    script_path: str,
    daily_cycle_id: str,
) -> str:
    if not COMMIT_SHA.fullmatch(commit_sha):
        raise CanonicalValueError("podcast script commit must contain 40 lowercase hex characters")
    if (
        not RUN_ID.fullmatch(daily_cycle_id)
        or not PODCAST_PATH.fullmatch(script_path)
        or script_path
        != f"data/wiki/podcasts/daily-podcast_{daily_cycle_id.removeprefix('daily-')}.md"
    ):
        raise CanonicalValueError("podcast script identity is not canonical")
    result = subprocess.run(
        ["git", "show", f"{commit_sha}:{script_path}"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise CanonicalValueError("committed podcast script is unavailable")
    try:
        markdown = result.stdout.decode("utf-8")
    except UnicodeError as exc:
        raise CanonicalValueError("committed podcast script is not UTF-8") from exc
    try:
        spoken_transcript(markdown)
    except PodcastError as exc:
        raise CanonicalValueError(f"committed podcast script is invalid: {exc}") from exc
    return markdown


def podcast_script_messages(
    markdown: str,
    *,
    committed_url: str,
    limit: int,
) -> tuple[str, ...]:
    """Pack exact spoken paragraphs in order and append one committed-transcript link."""

    if limit <= 0:
        raise ValueError("message limit must be positive")
    try:
        transcript = spoken_transcript(markdown)
    except PodcastError as exc:
        raise CanonicalValueError(str(exc)) from exc
    if not re.fullmatch(
        r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/blob/[0-9a-f]{40}/data/wiki/podcasts/daily-podcast_[0-9]{8}T[0-9]{6}Z\.md",
        committed_url,
    ):
        raise CanonicalValueError("committed podcast URL is not canonical")
    paragraphs = [value.strip() for value in re.split(r"\n\s*\n", transcript) if value.strip()]
    paragraphs.append(f"[Committed transcript]({committed_url})")
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > limit:
            raise CanonicalValueError(
                "one committed podcast paragraph exceeds the Telegram message limit"
            )
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if current and len(candidate) > limit:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        chunks.append(current)
    return tuple(chunks)


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


def _podcast_script_delivery_issue(repository_root: Path) -> Mapping[str, str] | None:
    issue_id = stable_id("issue", SCRIPT_DELIVERY_ISSUE_TITLE.casefold(), "")
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


def deliver_podcast_script(
    repository_root: Path,
    settings: Settings,
    *,
    commit_sha: str,
    script_path: str,
    daily_cycle_id: str,
    repository_url: str,
    token: str,
    chat_id: str,
    transport: TelegramTransport | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    now: datetime | None = None,
) -> TelegramPodcastScriptDeliveryResult:
    """Deliver only exact committed spoken paragraphs with independent retry state."""

    if not REPOSITORY_URL.fullmatch(repository_url):
        raise CanonicalValueError("Telegram repository URL must identify a github.com repository")
    markdown = _committed_podcast_script(
        repository_root,
        commit_sha=commit_sha,
        script_path=script_path,
        daily_cycle_id=daily_cycle_id,
    )
    committed_url = f"{repository_url}/blob/{commit_sha}/{script_path}"
    messages = podcast_script_messages(
        markdown,
        committed_url=committed_url,
        limit=settings.telegram.message_limit,
    )
    prior_issue = _podcast_script_delivery_issue(repository_root)
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
                preflight(token, chat_id, timeout_seconds=settings.telegram.timeout_seconds)
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
                        raise TelegramDeliveryError(
                            str(response.get("description", "Telegram rejected the script"))
                        )
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
            title=SCRIPT_DELIVERY_ISSUE_TITLE,
            description=(
                f"cycle={daily_cycle_id} script={script_path} commit={commit_sha} "
                f"next_chunk={failed_at} total_chunks={len(messages)} error={failure}"
            ),
            owner="delivery",
            related_run_id=daily_cycle_id,
            now=now,
        )
        return TelegramPodcastScriptDeliveryResult(
            "failed",
            daily_cycle_id,
            commit_sha,
            script_path,
            sent,
            len(messages),
            issue_id,
            failure,
        )
    issue_id = stable_id("issue", SCRIPT_DELIVERY_ISSUE_TITLE.casefold(), "")
    issue = next(
        (
            row
            for row in read_table(repository_root, "issues")
            if row["issue_id"] == issue_id and row["status"] == "open"
        ),
        None,
    )
    if issue is not None:
        resolve_issue(
            repository_root,
            issue_id,
            f"Podcast script for {daily_cycle_id} at {commit_sha} delivered successfully.",
            now=now,
        )
    return TelegramPodcastScriptDeliveryResult(
        "sent",
        daily_cycle_id,
        commit_sha,
        script_path,
        sent,
        len(messages),
        issue_id,
        "",
    )


def _deliver_podcast_audio(
    repository_root: Path,
    settings: Settings,
    *,
    manifest_path: Path,
    audio_path: Path,
    repository_url: str,
    token: str,
    chat_id: str,
    transport: TelegramTransport | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    now: datetime | None = None,
) -> TelegramAudioDeliveryResult:
    """Verify an ephemeral artifact against committed script bytes, then call sendAudio."""

    if not REPOSITORY_URL.fullmatch(repository_url):
        raise CanonicalValueError("Telegram repository URL must identify a github.com repository")
    if manifest_path.is_symlink() or audio_path.is_symlink():
        raise CanonicalValueError("podcast audio handoff must not use symlinks")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanonicalValueError(f"ephemeral audio manifest is invalid: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("audio_manifest_version") != 2:
        raise CanonicalValueError("ephemeral audio manifest contract is invalid")
    cycle_id = manifest.get("daily_cycle_id")
    script_commit = manifest.get("script_commit")
    script_path = manifest.get("script_path")
    if (
        not isinstance(cycle_id, str)
        or not RUN_ID.fullmatch(cycle_id)
        or not isinstance(script_commit, str)
        or not COMMIT_SHA.fullmatch(script_commit)
        or not isinstance(script_path, str)
        or not PODCAST_PATH.fullmatch(script_path)
        or script_path != f"data/wiki/podcasts/daily-podcast_{cycle_id.removeprefix('daily-')}.md"
    ):
        raise CanonicalValueError("audio manifest script/cycle identity is invalid")
    if audio_path.name != manifest.get("audio_filename") or audio_path.suffix != ".mp3":
        raise CanonicalValueError("audio artifact filename differs from its manifest")
    if not audio_path.is_file() or audio_path.stat().st_size == 0:
        raise CanonicalValueError("ephemeral podcast audio is missing or empty")
    if audio_path.stat().st_size > settings.telegram.audio_maximum_bytes:
        raise CanonicalValueError("ephemeral podcast audio exceeds its delivery limit")
    if manifest.get("audio_size") != audio_path.stat().st_size:
        raise CanonicalValueError("ephemeral podcast audio size differs from its manifest")
    duration = manifest.get("duration_seconds")
    if (
        isinstance(duration, bool)
        or not isinstance(duration, int)
        or not settings.podcast.minimum_duration_seconds
        <= duration
        <= settings.podcast.maximum_duration_seconds
    ):
        raise CanonicalValueError("ephemeral podcast duration is outside configured bounds")
    audio_sha = content_hash(audio_path.read_bytes())
    if manifest.get("audio_sha256") != audio_sha:
        raise CanonicalValueError("ephemeral podcast audio hash differs from its manifest")
    script = subprocess.run(
        ["git", "show", f"{script_commit}:{script_path}"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if script.returncode != 0 or content_hash(script.stdout) != manifest.get("script_sha256"):
        raise CanonicalValueError("audio manifest is not bound to the exact committed transcript")
    report_path = committed_run_report_path(
        repository_root, commit_sha=script_commit, run_id=cycle_id
    )
    caption = (
        "PaperTrader daily podcast\n"
        f"Transcript: {repository_url}/blob/{script_commit}/{script_path}\n"
        f"Daily report: {repository_url}/blob/{script_commit}/{report_path}"
    )
    selected_transport = transport or UrllibTelegramTransport()
    failure = ""
    if not token or not CHAT_ID.fullmatch(chat_id):
        failure = "Telegram bot token and canonical chat ID are required"
    else:
        preflight = getattr(selected_transport, "preflight", None)
        if callable(preflight):
            try:
                preflight(token, chat_id, timeout_seconds=settings.telegram.timeout_seconds)
            except (OSError, TelegramDeliveryError, ValueError) as exc:
                failure = _safe_error(exc, token, chat_id)
        if not failure:
            for attempt in range(1, settings.telegram.maximum_attempts + 1):
                try:
                    response = selected_transport.send_audio(
                        token,
                        {"chat_id": chat_id, "caption": caption},
                        audio_path,
                        timeout_seconds=settings.telegram.timeout_seconds,
                    )
                    if response.get("ok") is not True:
                        raise TelegramDeliveryError(
                            str(response.get("description", "Telegram rejected the audio"))
                        )
                    failure = ""
                    break
                except (OSError, TelegramDeliveryError, ValueError) as exc:
                    failure = _safe_error(exc, token, chat_id)
                    if attempt < settings.telegram.maximum_attempts:
                        sleeper(float(2 ** (attempt - 1)))
    issue_id = stable_id("issue", AUDIO_DELIVERY_ISSUE_TITLE.casefold(), "")
    if failure:
        issue_id = record_issue(
            repository_root,
            severity="warning",
            title=AUDIO_DELIVERY_ISSUE_TITLE,
            description=(
                f"cycle={cycle_id} commit={script_commit} audio_sha256={audio_sha} error={failure}"
            ),
            owner="delivery",
            related_run_id=cycle_id,
            now=now,
        )
        return TelegramAudioDeliveryResult(
            "failed", cycle_id, script_commit, audio_sha, issue_id, failure
        )
    issue = next(
        (
            row
            for row in read_table(repository_root, "issues")
            if row["issue_id"] == issue_id and row["status"] == "open"
        ),
        None,
    )
    if issue is not None:
        resolve_issue(
            repository_root,
            issue_id,
            f"Podcast audio for {cycle_id} at {script_commit} delivered successfully.",
            now=now,
        )
    return TelegramAudioDeliveryResult("sent", cycle_id, script_commit, audio_sha, issue_id, "")


def deliver_podcast_audio(
    repository_root: Path,
    settings: Settings,
    *,
    manifest_path: Path,
    audio_path: Path,
    repository_url: str,
    token: str,
    chat_id: str,
    transport: TelegramTransport | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    now: datetime | None = None,
) -> TelegramAudioDeliveryResult:
    """Deliver sealed audio and immediately remove the ephemeral media handoff."""

    try:
        return _deliver_podcast_audio(
            repository_root,
            settings,
            manifest_path=manifest_path,
            audio_path=audio_path,
            repository_url=repository_url,
            token=token,
            chat_id=chat_id,
            transport=transport,
            sleeper=sleeper,
            now=now,
        )
    finally:
        for path in (audio_path, manifest_path):
            if path.is_file() and not path.is_symlink():
                path.unlink(missing_ok=True)
        if audio_path.parent == manifest_path.parent:
            with suppress(OSError):
                audio_path.parent.rmdir()

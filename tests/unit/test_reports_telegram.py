from __future__ import annotations

import subprocess
from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path

from papertrader.config import Settings
from papertrader.reports import NarrativeItem, generate_daily_report
from papertrader.tables import read_table
from papertrader.telegram import (
    TelegramDeliveryError,
    deliver_committed_report,
    escape_markdown_v2,
    split_message,
)
from papertrader.wiki import lint_wiki


def test_daily_report_matches_reference_and_registers_one_canonical_page(
    sandbox_repository: Path,
    repository_root: Path,
) -> None:
    generated_at = datetime(2026, 7, 24, 22, tzinfo=UTC)
    arguments = {
        "run_id": "run-report",
        "run_status": "succeeded",
        "report_date": date(2026, 7, 24),
        "narrative_items": (
            NarrativeItem(
                "No material market move required a research follow-up.",
                ("data/market/latest.csv",),
            ),
        ),
        "github_report_url": (
            "https://github.com/example/PaperTrader/blob/main/"
            "data/wiki/daily-reports/daily-report_20260724.md"
        ),
        "generated_at": generated_at,
    }

    path = generate_daily_report(sandbox_repository, **arguments)
    generate_daily_report(sandbox_repository, **arguments)

    expected = (
        repository_root / "tests" / "reference_outputs" / "daily_report_empty.md"
    ).read_text(encoding="utf-8")
    assert path.read_text(encoding="utf-8") == expected
    index = (sandbox_repository / "data" / "wiki" / "index.md").read_text(encoding="utf-8")
    log = (sandbox_repository / "data" / "wiki" / "log.md").read_text(encoding="utf-8")
    assert index.count("[[daily-reports/daily-report_20260724") == 1
    assert log.count("Generated canonical [[daily-reports/daily-report_20260724]]") == 1
    assert lint_wiki(sandbox_repository / "data" / "wiki") == []


def test_telegram_markdown_escaping_and_bounded_lossless_splitting() -> None:
    raw = r"P/L +1.2% [paper] (only)! #safe \\"
    escaped = escape_markdown_v2(raw)

    assert escaped == r"P/L \+1\.2% \[paper\] \(only\)\! \#safe \\\\"
    message = "first line\n" + "word " * 20 + "tail"
    chunks = split_message(message, limit=25)
    assert "".join(chunks) == message
    assert all(len(chunk) <= 25 for chunk in chunks)

    escaped_pair = escape_markdown_v2("x" * 24 + "!")
    escaped_chunks = split_message(escaped_pair, limit=25)
    assert "".join(escaped_chunks) == escaped_pair
    assert all(not chunk.endswith("\\") for chunk in escaped_chunks[:-1])


class _FakeTelegram:
    def __init__(self, events: list[Mapping[str, object] | BaseException]) -> None:
        self.events = events
        self.calls: list[Mapping[str, str]] = []

    def send(
        self,
        token: str,
        payload: Mapping[str, str],
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        assert token == "secret-token"
        assert timeout_seconds > 0
        self.calls.append(payload)
        event = self.events.pop(0) if self.events else {"ok": True}
        if isinstance(event, BaseException):
            raise event
        return event


def _commit_report(repository: Path) -> tuple[str, str]:
    report_path = "data/wiki/daily-reports/daily-report_20260724.md"
    (repository / report_path).write_text(
        "# PaperTrader daily report — 2026-07-24\n\n" + "Position update.\n" * 20,
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=repository, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repository, check=True)
    subprocess.run(["git", "add", "--all"], cwd=repository, check=True)
    subprocess.run(
        ["git", "commit", "-m", "report"], cwd=repository, check=True, capture_output=True
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip(), report_path


def test_telegram_failure_is_redacted_persisted_and_resumed(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    commit_sha, report_path = _commit_report(sandbox_repository)
    failed_transport = _FakeTelegram(
        [
            {"ok": True},
            TelegramDeliveryError("temporary failure for secret-token"),
            TelegramDeliveryError("temporary failure for secret-token"),
            TelegramDeliveryError("temporary failure for secret-token"),
        ]
    )

    failed = deliver_committed_report(
        sandbox_repository,
        sandbox_settings,
        commit_sha=commit_sha,
        report_path=report_path,
        repository_url="https://github.com/example/PaperTrader",
        run_id="telegram-test",
        token="secret-token",
        chat_id="-123",
        transport=failed_transport,
        sleeper=lambda _: None,
        now=datetime(2026, 7, 24, 23, tzinfo=UTC),
    )

    assert failed.status == "failed"
    assert failed.chunks_sent == 1
    assert "secret-token" not in failed.error
    issue = next(
        row
        for row in read_table(sandbox_repository, "issues")
        if row["issue_id"] == failed.issue_id
    )
    assert issue["status"] == "open"
    assert "next_chunk=1" in issue["description"]
    assert "secret-token" not in issue["description"]

    retry_transport = _FakeTelegram([])
    sent = deliver_committed_report(
        sandbox_repository,
        sandbox_settings,
        commit_sha=commit_sha,
        report_path=report_path,
        repository_url="https://github.com/example/PaperTrader",
        run_id="telegram-test-retry",
        token="secret-token",
        chat_id="-123",
        transport=retry_transport,
        sleeper=lambda _: None,
        now=datetime(2026, 7, 25, tzinfo=UTC),
    )

    assert sent.status == "sent"
    assert len(retry_transport.calls) == sent.total_chunks - 1
    resolved = next(
        row
        for row in read_table(sandbox_repository, "issues")
        if row["issue_id"] == failed.issue_id
    )
    assert resolved["status"] == "resolved"

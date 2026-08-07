from __future__ import annotations

import json
import subprocess
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from papertrader.advice import ResearchAlertView, refresh_advice
from papertrader.config import Settings
from papertrader.execution import ensure_initial_capital
from papertrader.investor_pages import (
    ResearchDecisionView,
    investor_brief_markdown,
)
from papertrader.reports import NarrativeItem, generate_daily_report
from papertrader.tables import read_table
from papertrader.telegram import (
    TelegramDeliveryError,
    UrllibTelegramTransport,
    deliver_committed_report,
    deliver_podcast_audio,
    escape_markdown_v2,
    record_podcast_audio_failure,
    split_message,
    telegram_messages,
)
from papertrader.utils import content_hash
from papertrader.wiki import lint_wiki


def test_daily_report_matches_reference_and_registers_one_canonical_page(
    sandbox_repository: Path,
    repository_root: Path,
    sandbox_settings: Settings,
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
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id="run-report",
        occurred_at=generated_at,
    )
    snapshot = refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="run-report",
        as_of=generated_at,
    )

    path = generate_daily_report(sandbox_repository, **arguments)
    generate_daily_report(sandbox_repository, **arguments)

    expected = (
        repository_root / "tests" / "reference_outputs" / "daily_report_empty.md"
    ).read_text(encoding="utf-8")
    assert path.read_text(encoding="utf-8") == expected
    index = (sandbox_repository / "data" / "wiki" / "index.md").read_text(encoding="utf-8")
    log = (sandbox_repository / "data" / "wiki" / "log.md").read_text(encoding="utf-8")
    assert index.count("[[daily-reports/daily-report_20260724") == 1
    assert index.count(snapshot.snapshot_id) == 1
    assert "No trade — hold 100% cash" in index
    assert "**No actionable trade signals.**" in index
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


def test_telegram_builds_one_rich_markdown_report_with_linked_wiki_pages() -> None:
    commit = "a" * 40
    committed_url = (
        "https://github.com/example/PaperTrader/blob/"
        f"{commit}/data/wiki/daily-reports/daily-report_20260724.md"
    )
    report = (
        "---\ntitle: Example\n---\n\n# Daily report\n\n"
        "## Portfolio\n\n- **Cash:** `100000 EUR`\n- [[securities/sec_a|EXM]]\n"
    )

    messages = telegram_messages(report, committed_url=committed_url)

    assert len(messages) == 1
    assert messages[0].startswith("# Daily report")
    assert "title: Example" not in messages[0]
    assert "**Cash:** `100000 EUR`" in messages[0]
    assert "[EXM](https://example.github.io/PaperTrader/securities/sec_a)" in messages[0]
    assert messages[0].endswith(
        "[View the daily report](https://example.github.io/PaperTrader/"
        "daily-reports/daily-report_20260724)"
    )


def test_telegram_uses_only_the_committed_investor_brief_when_marked() -> None:
    commit = "b" * 40
    committed_url = (
        "https://github.com/example/PaperTrader/blob/"
        f"{commit}/data/wiki/daily-reports/daily-report_20260724.md"
    )
    report = (
        "---\ntitle: Example\n---\n\n# Full daily report\n\n"
        "<!-- papertrader-investor-brief:start -->\n"
        "# No trade — hold 100% cash\n\n"
        "- **Snapshot:** `decision_0123456789abcdefabcd`\n"
        "- [[model-portfolio|Model portfolio]]\n"
        "<!-- papertrader-investor-brief:end -->\n\n"
        "## Complete active queue\n\n- `operation_secret`\n"
    )

    messages = telegram_messages(report, committed_url=committed_url)
    delivered = "".join(messages)

    assert delivered.startswith("# No trade — hold 100% cash")
    assert "decision_0123456789abcdefabcd" in delivered
    assert "Complete active queue" not in delivered
    assert "operation_secret" not in delivered
    assert ("[Model portfolio](https://example.github.io/PaperTrader/model-portfolio)") in delivered
    assert delivered.endswith(
        "[View the daily report](https://example.github.io/PaperTrader/"
        "daily-reports/daily-report_20260724)"
    )


def test_telegram_converts_relative_security_idea_and_report_links_to_pages() -> None:
    commit = "c" * 40
    committed_url = (
        "https://github.com/Kabutojira/PaperTrader/blob/"
        f"{commit}/data/wiki/daily-reports/daily-report_20260729.md"
    )
    report = "# Result\n\n- [ALB](securities/security_alb)\n- [Lithium](ideas/idea_lithium)\n"

    delivered = "".join(telegram_messages(report, committed_url=committed_url))

    assert "[ALB](https://kabutojira.github.io/PaperTrader/securities/security_alb)" in delivered
    assert "[Lithium](https://kabutojira.github.io/PaperTrader/ideas/idea_lithium)" in delivered
    assert delivered.endswith(
        "[View the daily report](https://kabutojira.github.io/PaperTrader/"
        "daily-reports/daily-report_20260729)"
    )


def test_investor_brief_contains_every_price_alert_and_run_research_decision(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    now = datetime(2026, 7, 29, 20, tzinfo=UTC)
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id="run-alert-brief",
        occurred_at=now,
    )
    snapshot = refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="run-alert-brief",
        as_of=now,
    )
    snapshot = replace(
        snapshot,
        research_alerts=(
            ResearchAlertView(
                alert_id="alert_example",
                security_id="security_example",
                ticker="EXM",
                company_name="Example Corp",
                alert_type="volume_anomaly",
                observed_at="2026-07-29T20:00:00Z",
                market_data_date="2026-07-29",
                research_status="succeeded",
                research_conclusion="The volume spike was event-driven; no trade was warranted.",
                research_page=("data/wiki/security-catalog.md#security-security_example"),
            ),
        ),
    )
    decisions = (
        ResearchDecisionView(
            operation_id="operation_example",
            operation_type="idea_research",
            label="Lithium supply reset",
            research_page="data/wiki/ideas/idea_lithium.md",
            status="succeeded",
            conclusion="The idea remains valid, but valuation support is incomplete.",
        ),
    )

    brief = investor_brief_markdown(snapshot, decisions)

    assert "## Price action alerts" in brief
    assert "[EXM — Example Corp](security-catalog#security-security_example)" in brief
    assert "The volume spike was event-driven; no trade was warranted." in brief
    assert "## Research decisions this run" in brief
    assert "[Lithium supply reset](ideas/idea_lithium)" in brief
    assert "valuation support is incomplete" in brief

    long_decision = replace(decisions[0], conclusion="x" * 600)
    bounded_brief = investor_brief_markdown(snapshot, (long_decision,))
    decision_line = next(
        line for line in bounded_brief.splitlines() if "Lithium supply reset" in line
    )
    assert decision_line.endswith("…")
    assert len(decision_line) < 600


def test_telegram_transport_calls_rich_message_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[urllib.request.Request] = []

    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"ok":true}'

    def urlopen(request: urllib.request.Request, *, timeout: int) -> Response:
        assert timeout == 15
        requests.append(request)
        return Response()

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    rich_message = json.dumps({"markdown": "# Formatted"})

    response = UrllibTelegramTransport().send(
        "test-token",
        {"chat_id": "-123", "rich_message": rich_message},
        timeout_seconds=15,
    )

    assert response == {"ok": True}
    assert requests[0].full_url.endswith("/bottest-token/sendRichMessage")
    payload = urllib.parse.parse_qs(requests[0].data.decode("utf-8"))
    assert payload == {"chat_id": ["-123"], "rich_message": [rich_message]}


def test_telegram_transport_preflights_bot_and_destination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[urllib.request.Request] = []

    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"ok":true}'

    def urlopen(request: urllib.request.Request, *, timeout: int) -> Response:
        assert timeout == 15
        requests.append(request)
        return Response()

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)

    UrllibTelegramTransport().preflight("test-token", "-123", timeout_seconds=15)

    assert [request.full_url.rsplit("/", maxsplit=1)[-1] for request in requests] == [
        "getMe",
        "getChat",
    ]
    assert urllib.parse.parse_qs(requests[0].data.decode("utf-8")) == {}
    assert urllib.parse.parse_qs(requests[1].data.decode("utf-8")) == {"chat_id": ["-123"]}


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


class _FakeAudioTelegram:
    def __init__(self, events: list[Mapping[str, object] | BaseException]) -> None:
        self.events = events
        self.calls: list[tuple[Mapping[str, str], Path]] = []

    def preflight(self, token: str, chat_id: str, *, timeout_seconds: int) -> None:
        assert token == "secret-token"
        assert chat_id == "-123"
        assert timeout_seconds > 0

    def send_audio(
        self,
        token: str,
        payload: Mapping[str, str],
        audio_path: Path,
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        assert token == "secret-token"
        assert timeout_seconds > 0
        self.calls.append((payload, audio_path))
        event = self.events.pop(0) if self.events else {"ok": True}
        if isinstance(event, BaseException):
            raise event
        return event


def _commit_podcast_handoff(repository: Path) -> tuple[str, Path, Path, str]:
    cycle_id = "daily-20260724T220000Z"
    report_path = "data/wiki/daily-reports/daily-report_20260724.md"
    script_path = "data/wiki/podcasts/daily-podcast_20260724T220000Z.md"
    (repository / report_path).write_text("# Daily report\n", encoding="utf-8")
    script = (
        f"---\ndaily_cycle_id: {cycle_id}\n---\n\n"
        "<!-- papertrader-spoken-transcript:start -->\nDaily portfolio review.\n"
        "<!-- papertrader-spoken-transcript:end -->\n"
    )
    (repository / script_path).parent.mkdir(parents=True, exist_ok=True)
    (repository / script_path).write_text(script, encoding="utf-8")
    run_directory = repository / "data" / "runs" / cycle_id
    run_directory.mkdir(parents=True)
    (run_directory / "daily_run.json").write_text(
        json.dumps(
            {
                "run_id": cycle_id,
                "status": "succeeded",
                "report_path": report_path,
            }
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=repository, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repository, check=True)
    subprocess.run(["git", "add", "--all"], cwd=repository, check=True)
    subprocess.run(
        ["git", "commit", "-m", "podcast"], cwd=repository, check=True, capture_output=True
    )
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    audio = repository.parent / f"{cycle_id}.mp3"
    audio.write_bytes(b"ID3-ephemeral-audio")
    manifest = repository.parent / f"{cycle_id}.audio-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "audio_manifest_version": 1,
                "daily_cycle_id": cycle_id,
                "script_commit": commit,
                "script_path": script_path,
                "script_sha256": content_hash(script.encode()),
                "spoken_transcript_sha256": content_hash("Daily portfolio review."),
                "audio_filename": audio.name,
                "audio_size": audio.stat().st_size,
                "audio_sha256": content_hash(audio.read_bytes()),
                "duration_seconds": 1200,
                "format": "mp3",
            }
        ),
        encoding="utf-8",
    )
    return commit, manifest, audio, cycle_id


def test_verified_ephemeral_podcast_audio_is_delivered_and_failures_are_stable(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    commit, manifest, audio, cycle_id = _commit_podcast_handoff(sandbox_repository)
    transport = _FakeAudioTelegram([])

    delivered = deliver_podcast_audio(
        sandbox_repository,
        sandbox_settings,
        manifest_path=manifest,
        audio_path=audio,
        repository_url="https://github.com/example/PaperTrader",
        token="secret-token",
        chat_id="-123",
        transport=transport,
        sleeper=lambda _: None,
    )

    assert delivered.status == "sent"
    assert delivered.script_commit == commit
    assert transport.calls[0][1] == audio
    assert f"/blob/{commit}/data/wiki/podcasts/" in transport.calls[0][0]["caption"]

    first = record_podcast_audio_failure(
        sandbox_repository,
        daily_cycle_id=cycle_id,
        script_commit=commit,
        error="render failed",
    )
    second = record_podcast_audio_failure(
        sandbox_repository,
        daily_cycle_id=cycle_id,
        script_commit=commit,
        error="artifact expired",
    )
    assert first.issue_id == second.issue_id
    issues = [
        row for row in read_table(sandbox_repository, "issues") if row["issue_id"] == first.issue_id
    ]
    assert len(issues) == 1
    assert "artifact expired" in issues[0]["description"]


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
    bounded_settings = replace(
        sandbox_settings,
        telegram=replace(sandbox_settings.telegram, message_limit=100),
    )
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
        bounded_settings,
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
    assert failed_transport.calls[0]["chat_id"] == "-123"
    first_message = json.loads(failed_transport.calls[0]["rich_message"])
    assert first_message["markdown"].startswith("# PaperTrader daily report")
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
        bounded_settings,
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


def test_latest_commit_restarts_delivery_instead_of_replaying_an_old_cursor(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    old_commit, report_path = _commit_report(sandbox_repository)
    bounded_settings = replace(
        sandbox_settings,
        telegram=replace(sandbox_settings.telegram, message_limit=100),
    )
    failed = deliver_committed_report(
        sandbox_repository,
        bounded_settings,
        commit_sha=old_commit,
        report_path=report_path,
        repository_url="https://github.com/example/PaperTrader",
        run_id="telegram-old",
        token="secret-token",
        chat_id="-123",
        transport=_FakeTelegram(
            [
                {"ok": True},
                TelegramDeliveryError("temporary failure"),
                TelegramDeliveryError("temporary failure"),
                TelegramDeliveryError("temporary failure"),
            ]
        ),
        sleeper=lambda _: None,
        now=datetime(2026, 7, 24, 23, tzinfo=UTC),
    )
    assert failed.status == "failed"
    assert failed.chunks_sent == 1

    (sandbox_repository / report_path).write_text(
        "# Newest daily report\n\n" + "Latest position update.\n" * 20,
        encoding="utf-8",
    )
    subprocess.run(["git", "add", report_path], cwd=sandbox_repository, check=True)
    subprocess.run(
        ["git", "commit", "-m", "newest report"],
        cwd=sandbox_repository,
        check=True,
        capture_output=True,
    )
    latest_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=sandbox_repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    transport = _FakeTelegram([])

    sent = deliver_committed_report(
        sandbox_repository,
        bounded_settings,
        commit_sha=latest_commit,
        report_path=report_path,
        repository_url="https://github.com/example/PaperTrader",
        run_id="telegram-latest",
        token="secret-token",
        chat_id="-123",
        transport=transport,
        sleeper=lambda _: None,
        now=datetime(2026, 7, 25, tzinfo=UTC),
    )

    assert sent.status == "sent"
    assert sent.chunks_sent == sent.total_chunks
    assert len(transport.calls) == sent.total_chunks
    first = json.loads(transport.calls[0]["rich_message"])
    assert first["markdown"].startswith("# Newest daily report")

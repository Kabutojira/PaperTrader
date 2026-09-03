from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.issues import (
    reconcile_issues,
    record_issue,
    resolve_issue,
    validate_issue_state,
)
from papertrader.logs import append_event, regenerate_log_tail
from papertrader.market_data import write_fx_cache
from papertrader.models import FxRate
from papertrader.tables import append_unique, contract_by_name, read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    deterministic_ulid,
    parse_timestamp,
    required_decimal,
    validate_ulid,
)


def test_decimal_helpers_reject_binary_float_and_render_without_exponents() -> None:
    with pytest.raises(CanonicalValueError, match="binary float"):
        required_decimal(1.25, label="money")  # type: ignore[arg-type]

    assert decimal_text(Decimal("1.230000")) == "1.23"
    assert decimal_text(Decimal("-0.000")) == "0"


def test_timestamp_requires_timezone_and_ulid_is_stable() -> None:
    with pytest.raises(CanonicalValueError, match="timezone"):
        parse_timestamp("2026-07-24T12:00:00")

    instant = datetime(2026, 7, 24, 12, tzinfo=UTC)
    first = deterministic_ulid(instant, "queue", "same")
    second = deterministic_ulid(instant, "queue", "same")

    validate_ulid(first)
    assert first == second
    assert len(first) == 26


def test_append_unique_is_idempotent_and_rejects_immutable_conflict(
    sandbox_repository: Path,
) -> None:
    row = {
        "run_id": "run-1",
        "started_at": "2026-07-24T10:00:00Z",
        "completed_at": "2026-07-24T10:01:00Z",
        "status": "succeeded",
        "trigger": "test",
        "operation_count": "0",
        "model_budget_limit": "5",
        "model_budget_used": "0",
        "commit_sha": "",
        "summary": "done",
    }

    with pytest.raises(CanonicalValueError, match="cannot replace append-only table"):
        write_table(sandbox_repository, "runs", [row])
    assert append_unique(sandbox_repository, "runs", [row], key_columns=("run_id",)) == 1
    assert append_unique(sandbox_repository, "runs", [row], key_columns=("run_id",)) == 0
    with pytest.raises(CanonicalValueError, match="immutable runs row conflicts"):
        append_unique(
            sandbox_repository,
            "runs",
            [row | {"summary": "different"}],
            key_columns=("run_id",),
        )


def test_issue_upsert_resolution_and_dashboard(sandbox_repository: Path) -> None:
    first_seen = datetime(2026, 7, 24, 9, tzinfo=UTC)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="stale_option_quote",
        impact="blocks_action",
        severity="warning",
        title="Stale quote",
        description="Option quote exceeded its freshness window.",
        entity_type="option_quote",
        entity_id="fixture-contract",
        related_run_id="first-run",
        now=first_seen,
    )
    assert (
        record_issue(
            sandbox_repository,
            issue_code="stale_option_quote",
            impact="blocks_action",
            severity="error",
            title="Stale quote",
            description="Option quote is still stale.",
            entity_type="option_quote",
            entity_id="fixture-contract",
            related_run_id="later-run",
            now=datetime(2026, 7, 24, 10, tzinfo=UTC),
        )
        == issue_id
    )
    row = read_table(sandbox_repository, "issues")[0]
    assert row["first_seen_at"] == "2026-07-24T09:00:00Z"
    assert row["last_seen_at"] == "2026-07-24T10:00:00Z"
    assert row["severity"] == "error"
    assert row["related_run_id"] == "first-run"
    assert issue_id in (sandbox_repository / "data" / "issues.md").read_text(encoding="utf-8")

    resolve_issue(
        sandbox_repository,
        issue_id,
        "Fresh quote retrieved.",
        now=datetime(2026, 7, 24, 11, tzinfo=UTC),
    )

    assert read_table(sandbox_repository, "issues")[0]["status"] == "resolved"
    assert "No open issues." in (sandbox_repository / "data" / "issues.md").read_text(
        encoding="utf-8"
    )


def test_issue_reconciliation_requires_later_canonical_recovery(
    sandbox_repository: Path,
) -> None:
    failed_at = datetime(2026, 7, 24, 9, tzinfo=UTC)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="daily_market_retrieval_failed",
        impact="affects_candidate",
        severity="warning",
        title="Market retrieval failed",
        description="The latest candidate quote was unavailable.",
        entity_type="security",
        entity_id="security_fixture",
        now=failed_at,
    )
    assert (
        reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(minutes=1))[
            "resolved_count"
        ]
        == 0
    )
    write_table(
        sandbox_repository,
        "market_latest",
        [
            {
                "security_id": "security_fixture",
                "provider_symbol": "FIX",
                "price_date": "2026-07-24",
                "retrieved_at": "2026-07-24T10:00:00Z",
                "open": "10",
                "high": "11",
                "low": "9",
                "close": "10",
                "adjusted_close": "10",
                "volume": "100",
                "currency": "USD",
                "source": "fixture",
                "status": "ok",
                "error": "",
            }
        ],
    )

    result = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=2))

    row = read_table(sandbox_repository, "issues")[0]
    assert result["resolved_issue_ids"] == (issue_id,)
    assert row["status"] == "resolved"
    assert row["last_seen_at"] == "2026-07-24T09:00:00Z"
    assert row["resolution"].startswith("current_state_recovered:")
    assert validate_issue_state(sandbox_repository) == []


def test_issue_reconciliation_closes_recovered_fx_pair(sandbox_repository: Path) -> None:
    failed_at = datetime(2026, 7, 24, 9, tzinfo=UTC)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="daily_fx_retrieval_failed",
        impact="affects_candidate",
        severity="warning",
        title="Daily preparation degraded: FX GBP/EUR",
        description="FX GBP/EUR was unavailable.",
        entity_type="fx_pair",
        entity_id="GBP_EUR",
        now=failed_at,
    )
    write_fx_cache(
        sandbox_repository,
        "GBP",
        "EUR",
        (
            FxRate(
                date=date(2026, 7, 24),
                currency="GBP",
                base_currency="EUR",
                rate_to_base=Decimal("1.15"),
                retrieved_at=failed_at + timedelta(hours=1),
                source="fixture",
            ),
        ),
    )

    result = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=2))

    row = read_table(sandbox_repository, "issues")[0]
    assert result["resolved_issue_ids"] == (issue_id,)
    assert row["status"] == "resolved"
    assert "FX retrieval succeeded" in row["resolution"]


def _append_assessment_version(
    repository: Path,
    *,
    assessment_id: str,
    security_id: str,
    recorded_at: str,
) -> None:
    row = {
        column: "" for column in contract_by_name(repository, "security_assessment_history").columns
    }
    row.update(
        {
            "assessment_id": assessment_id,
            "assessment_schema_version": "2",
            "security_id": security_id,
            "assessed_at": recorded_at,
            "expires_at": "2026-09-01T00:00:00Z",
            "recorded_at": recorded_at,
        }
    )
    append_unique(
        repository,
        "security_assessment_history",
        [row],
        key_columns=("assessment_id",),
    )


def _append_operation_history(
    repository: Path,
    *,
    operation_id: str,
    operation_type: str,
    entity_id: str,
    completed_at: str,
    terminal_status: str = "succeeded",
    terminal_reason: str = "completed",
    source: str = "fixture",
) -> None:
    row = {column: "" for column in contract_by_name(repository, "operations_history").columns}
    row.update(
        {
            "operation_id": operation_id,
            "created_at": "2026-07-24T09:30:00Z",
            "updated_at": completed_at,
            "status": "running",
            "priority": "50",
            "operation_type": operation_type,
            "entity_type": "run" if operation_type == "daily_podcast" else "security",
            "entity_id": entity_id,
            "dedupe_key": f"{operation_type}:{entity_id}:fixture",
            "freshness_days": "0",
            "prompt": "Fixture recovery operation.",
            "payload_path": f"data/operations/payloads/{operation_id}.json",
            "source": source,
            "attempt_count": "1",
            "max_attempts": "3",
            "terminal_status": terminal_status,
            "completed_at": completed_at,
            "terminal_reason": terminal_reason,
        }
    )
    append_unique(repository, "operations_history", [row], key_columns=("operation_id",))


def test_later_assessment_version_resolves_candidate_validation_failure(
    sandbox_repository: Path,
) -> None:
    failed_at = datetime(2026, 7, 24, 9, tzinfo=UTC)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="assessment_update_failed",
        impact="affects_candidate",
        severity="warning",
        title="Assessment update failed",
        description="The candidate assessment request was invalid.",
        entity_type="security",
        entity_id="security_recovered",
        now=failed_at,
    )
    _append_assessment_version(
        sandbox_repository,
        assessment_id="assessment_recovered",
        security_id="security_recovered",
        recorded_at="2026-07-24T10:00:00Z",
    )

    result = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=2))

    assert result["resolved_issue_ids"] == (issue_id,)
    issue = read_table(sandbox_repository, "issues")[0]
    assert issue["resolution"] == "superseded_by_assessment: assessment_recovered"


def test_duplicate_assessment_incident_requires_its_clean_remediation_review(
    sandbox_repository: Path,
) -> None:
    failed_at = datetime(2026, 7, 24, 9, tzinfo=UTC)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="security_assessment_duplicate_operation_versions",
        impact="affects_candidate",
        severity="error",
        title="Duplicate assessment versions",
        description="One operation produced conflicting immutable versions.",
        entity_type="security",
        entity_id="security_duplicate",
        now=failed_at,
    )

    first = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(minutes=1))
    remediation_id = first["remediation_operation_ids"][0]
    remediation = read_table(sandbox_repository, "operations_todo")[0]
    assert remediation["operation_id"] == remediation_id
    assert remediation["priority"] == "98"
    assert remediation["source"] == "issue-remediation:duplicate-assessment"
    _append_assessment_version(
        sandbox_repository,
        assessment_id="assessment_clean",
        security_id="security_duplicate",
        recorded_at="2026-07-24T10:00:00Z",
    )
    _append_operation_history(
        sandbox_repository,
        operation_id="01K00000000000000000000001",
        operation_type="security_research",
        entity_id="security_duplicate",
        completed_at="2026-07-24T10:05:00Z",
        source="unrelated-review",
    )
    assert (
        reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=2))["resolved_count"]
        == 0
    )
    _append_operation_history(
        sandbox_repository,
        operation_id="01K00000000000000000000002",
        operation_type="security_research",
        entity_id="security_duplicate",
        completed_at="2026-07-24T10:10:00Z",
        source="issue-remediation:duplicate-assessment",
    )

    result = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=3))

    assert result["resolved_issue_ids"] == (issue_id,)
    issue = read_table(sandbox_repository, "issues")[0]
    assert issue["resolution"] == "clean_review_succeeded: assessment_clean"


def test_later_successful_podcast_cycle_resolves_older_incident(
    sandbox_repository: Path,
) -> None:
    failed_at = datetime(2026, 7, 24, 9, tzinfo=UTC)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="daily_podcast_terminal",
        impact="publication_only",
        severity="warning",
        title="Daily podcast failed",
        description="The earlier podcast cycle failed.",
        entity_type="operation",
        entity_id="old-podcast-operation",
        now=failed_at,
    )
    _append_operation_history(
        sandbox_repository,
        operation_id="01K00000000000000000000003",
        operation_type="daily_podcast",
        entity_id="later-podcast-cycle",
        completed_at="2026-07-24T10:00:00Z",
    )

    result = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=2))

    assert result["resolved_issue_ids"] == (issue_id,)
    issue = read_table(sandbox_repository, "issues")[0]
    assert issue["resolution"].startswith("superseded_by_successful_podcast_cycle:")


def test_audited_watcher_retirement_resolves_old_youtube_issue(
    sandbox_repository: Path,
) -> None:
    failed_at = datetime(2026, 7, 24, 9, tzinfo=UTC)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="youtube_discovery_failed",
        impact="operational_only",
        severity="warning",
        title="YouTube discovery failed",
        description="The now-retired automated watcher failed.",
        entity_type="channel",
        entity_id="channel_fixture",
        now=failed_at,
    )
    _append_operation_history(
        sandbox_repository,
        operation_id="01K00000000000000000000004",
        operation_type="wiki_ingest",
        entity_id="youtube_fixture",
        completed_at="2026-07-24T10:00:00Z",
        terminal_status="cancelled",
        terminal_reason="source_watch_retired_manual_ideas",
        source="youtube_ingest:fixture",
    )

    result = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=2))

    assert result["resolved_issue_ids"] == (issue_id,)
    issue = read_table(sandbox_repository, "issues")[0]
    assert issue["resolution"].startswith("source_watch_retired:")


def test_audited_watcher_retirement_resolves_youtube_validation_incident(
    sandbox_repository: Path,
) -> None:
    failed_at = datetime(2026, 7, 24, 9, tzinfo=UTC)
    failed_operation_id = "01K00000000000000000000005"
    _append_operation_history(
        sandbox_repository,
        operation_id=failed_operation_id,
        operation_type="wiki_ingest",
        entity_id="youtube_failed_fixture",
        completed_at="2026-07-24T09:05:00Z",
        terminal_status="skipped",
        terminal_reason="youtube_transcript_unavailable",
        source="youtube_backfill:fixture",
    )
    issue_id = record_issue(
        sandbox_repository,
        issue_code="agent_result_validation_failed",
        impact="operational_only",
        severity="error",
        title="Local YouTube ingest validation failed",
        description="The retired watcher produced a stale result manifest.",
        entity_type="operation",
        entity_id=failed_operation_id,
        now=failed_at + timedelta(minutes=10),
    )
    _append_operation_history(
        sandbox_repository,
        operation_id="01K00000000000000000000006",
        operation_type="wiki_ingest",
        entity_id="youtube_retired_fixture",
        completed_at="2026-07-24T10:00:00Z",
        terminal_status="cancelled",
        terminal_reason="source_watch_retired_manual_ideas",
        source="youtube_ingest:fixture",
    )

    result = reconcile_issues(sandbox_repository, as_of=failed_at + timedelta(hours=2))

    assert result["resolved_issue_ids"] == (issue_id,)
    issue = read_table(sandbox_repository, "issues")[0]
    assert issue["resolution"].startswith("source_watch_retired:")


def test_structured_log_is_append_only_and_tail_is_bounded(sandbox_repository: Path) -> None:
    event_id = append_event(
        sandbox_repository,
        event_type="queue.claimed",
        message="Claimed operation",
        run_id="run-1",
        operation_id="operation-1",
        occurred_at=datetime(2026, 7, 24, 9, tzinfo=UTC),
    )
    assert event_id.startswith("event_")
    structured = sandbox_repository / "data" / "logs" / "operations-2026.ndjson"
    event = json.loads(structured.read_text(encoding="utf-8"))
    assert event["event_id"] == event_id

    lines = [
        json.dumps(
            {
                "event_id": f"event_{index:04d}",
                "occurred_at": f"2026-07-25T00:{index // 60:02d}:{index % 60:02d}Z",
                "event_type": "test",
                "run_id": "",
                "operation_id": "",
                "message": str(index),
                "data": {},
            },
            sort_keys=True,
        )
        for index in range(1005)
    ]
    structured.write_text("\n".join(lines) + "\n", encoding="utf-8")
    regenerate_log_tail(sandbox_repository)

    tail = (sandbox_repository / "data" / "logs" / "log.txt").read_text(encoding="utf-8")
    assert len(tail.splitlines()) == 1000
    assert structured.read_text(encoding="utf-8").count("\n") == 1005

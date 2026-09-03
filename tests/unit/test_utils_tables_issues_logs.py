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
from papertrader.tables import append_unique, read_table, write_table
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
    assert reconcile_issues(
        sandbox_repository, as_of=failed_at + timedelta(minutes=1)
    )["resolved_count"] == 0
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

    result = reconcile_issues(
        sandbox_repository, as_of=failed_at + timedelta(hours=2)
    )

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

    result = reconcile_issues(
        sandbox_repository, as_of=failed_at + timedelta(hours=2)
    )

    row = read_table(sandbox_repository, "issues")[0]
    assert result["resolved_issue_ids"] == (issue_id,)
    assert row["status"] == "resolved"
    assert "FX retrieval succeeded" in row["resolution"]


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

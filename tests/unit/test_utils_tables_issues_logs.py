from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.issues import record_issue, resolve_issue
from papertrader.logs import append_event, regenerate_log_tail
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
        severity="warning",
        title="Stale quote",
        description="Option quote exceeded its freshness window.",
        now=first_seen,
    )
    assert (
        record_issue(
            sandbox_repository,
            severity="error",
            title="Stale quote",
            description="Option quote is still stale.",
            now=datetime(2026, 7, 24, 10, tzinfo=UTC),
        )
        == issue_id
    )
    row = read_table(sandbox_repository, "issues")[0]
    assert row["first_seen_at"] == "2026-07-24T09:00:00Z"
    assert row["last_seen_at"] == "2026-07-24T10:00:00Z"
    assert row["severity"] == "error"
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

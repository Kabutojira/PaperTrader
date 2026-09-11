from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from test_execution_accounting import _security_row

from papertrader.queue import Operation, RunBudget, claim_next, enqueue_operation, prepare_queue
from papertrader.scheduling import attention_key
from papertrader.tables import contract_by_name, read_table, write_table

NOW = datetime(2026, 7, 24, 10, tzinfo=UTC)


def seed(root, settings, *, rsi="20", as_of="2026-07-23"):
    write_table(root, "securities", [_security_row()])
    row = {name: "" for name in contract_by_name(root, "indicators").columns}
    row.update(
        security_id="sec_a",
        as_of_date=as_of,
        calculated_at="2026-07-23T21:00:00Z",
        observation_count="220",
        rsi_14=rsi,
        source_price_hash="a" * 64,
    )
    write_table(root, "indicators", [row])
    for security, priority in [("ordinary", 100), ("sec_a", 10)]:
        enqueue_operation(
            root,
            settings,
            operation_type="security_research",
            entity_type="security",
            entity_id=security,
            dedupe_key=f"research:{security}",
            prompt="Research fixture",
            inputs={"security_id": security},
            priority=priority,
            source="fixture",
            now=NOW,
        )
    prepare_queue(root, now=NOW)
    return [Operation.from_row(row) for row in read_table(root, "operations_todo")]


def test_oversold_class_beats_accumulated_numeric_priority(sandbox_repository, sandbox_settings):
    seed(sandbox_repository, sandbox_settings)
    selected = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="attention",
        budget=RunBudget(maximum_operations=1, maximum_cost=Decimal("5")),
        now=NOW,
    )
    assert selected is not None and selected.entity_id == "sec_a"


def test_recovery_downgrades_urgency_without_deleting_question(
    sandbox_repository, sandbox_settings
):
    operations = seed(sandbox_repository, sandbox_settings, rsi="45")
    selected = min(
        operations, key=lambda op: attention_key(sandbox_repository, sandbox_settings, op, now=NOW)
    )
    assert selected.entity_id == "ordinary"
    assert len(read_table(sandbox_repository, "operations_todo")) == 2


def test_stale_or_non_session_data_does_not_create_urgency(sandbox_repository, sandbox_settings):
    operations = seed(sandbox_repository, sandbox_settings, as_of="2026-07-19")
    assert all(
        attention_key(sandbox_repository, sandbox_settings, op, now=NOW)[0] == 3
        for op in operations
    )
    seed_rows = read_table(sandbox_repository, "indicators")
    seed_rows[0]["as_of_date"] = "2026-07-23"
    write_table(sandbox_repository, "indicators", seed_rows)
    assert all(
        attention_key(sandbox_repository, sandbox_settings, op, now=NOW + timedelta(days=5))[0] == 3
        for op in operations
    )


def test_rsi_merge_preserves_original_age_and_exact_cause(sandbox_repository, sandbox_settings):
    operations = seed(sandbox_repository, sandbox_settings)
    original = next(op for op in operations if op.entity_id == "sec_a")
    source_price_hash = "b" * 64
    observed = {
        "rsi": "19",
        "threshold": "30",
        "observed_session": "2026-07-23",
        "source_price_hash": source_price_hash,
        "episode_id": "rsi_" + "c" * 24,
        "transitions": ["entered"],
        "original_created_at": "2026-07-24T10:02:00Z",
    }
    operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec_a",
        dedupe_key="rsi:new-observation",
        prompt="Investigate fresh oversold cause",
        inputs={
            "security_id": "sec_a",
            "rsi_attention": observed,
            "trigger_types": ["rsi_oversold"],
            "market_data_as_of": "2026-07-23T21:00:00Z",
            "market_data_date": "2026-07-23",
            "period_start": "2026-07-20",
            "period_end": "2026-07-23",
            "source_price_hash": source_price_hash,
        },
        source="deterministic-price-alert",
        now=NOW + timedelta(minutes=2),
    )
    assert operation_id == original.operation_id and not created
    updated = next(
        Operation.from_row(row)
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == operation_id
    )
    assert updated.created_at == original.created_at
    payload = json.loads((sandbox_repository / updated.payload_path).read_text())
    assert payload["inputs"]["research_reasons"][-1]["rsi_attention"] == observed

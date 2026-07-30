from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.config import Settings
from papertrader.dedupe import SemanticDisposition, build_dedupe_key
from papertrader.opportunity import _alert_research_type
from papertrader.queue import (
    QueueError,
    RunBudget,
    claim_next,
    complete_operation,
    enqueue_operation,
    prepare_queue,
    release_expired_leases,
    resolve_blocked_operation,
    validate_queue,
)
from papertrader.tables import read_table, write_table

NOW = datetime(2026, 7, 24, 10, tzinfo=UTC)


def _enqueue(
    repository: Path,
    settings: Settings,
    *,
    entity_id: str,
    catalyst: str,
    priority: int = 50,
    freshness_days: int = 0,
    depends_on: tuple[str, ...] = (),
    max_attempts: int | None = None,
    now: datetime = NOW,
) -> tuple[str, bool]:
    return enqueue_operation(
        repository,
        settings,
        operation_type="security_research",
        entity_type="security",
        entity_id=entity_id,
        dedupe_key=build_dedupe_key(
            "security_research", entity_id, catalyst, now.date().isoformat()
        ),
        prompt=f"Research security {entity_id}.",
        inputs={"security_id": entity_id},
        source="test",
        priority=priority,
        freshness_days=freshness_days,
        depends_on=depends_on,
        source_refs=(),
        max_attempts=max_attempts,
        now=now,
    )


def _complete(repository: Path, operation_id: str, run_id: str, now: datetime) -> None:
    result_path = f"data/runs/{run_id}/{operation_id}/agent_result.json"
    complete_operation(
        repository,
        operation_id=operation_id,
        run_id=run_id,
        terminal_status="succeeded",
        result_path=result_path,
        result_summary="Completed test operation.",
        terminal_reason="completed",
        now=now,
    )


def _allocation_target(plan_id: str) -> dict[str, str]:
    return {
        "allocation_plan_id": plan_id,
        "run_id": "allocation-current",
        "as_of": "2026-07-24T10:00:00Z",
        "security_id": "sec_a",
        "strategy_id": "strategy_a",
        "sleeve": "baseline",
        "rank": "1",
        "effective_score": "70",
        "candidate_edge": "10",
        "current_weight_pct": "0",
        "pending_weight_pct": "0",
        "target_weight_pct": "2",
        "target_value_base": "2000",
        "delta_value_base": "2000",
        "disposition": "open",
        "reason": "above_cash_hurdle",
        "assessment_as_of": "2026-07-24T09:00:00Z",
    }


def _enqueue_plan_strategy(
    repository: Path,
    settings: Settings,
    *,
    plan_id: str,
    catalyst: str,
    now: datetime,
) -> str:
    operation_id, created = enqueue_operation(
        repository,
        settings,
        operation_type="strategy_research",
        entity_type="strategy",
        entity_id="strategy_a",
        dedupe_key=f"strategy_research:strategy_a:{catalyst}:2026-07-24",
        prompt="Research one plan-bound baseline strategy.",
        inputs={
            "allocation_plan_id": plan_id,
            "assessment_as_of": "2026-07-24T09:00:00Z",
            "current_weight_pct": "0",
            "disposition": "open",
            "effective_score": "70",
            "maximum_weight_pct": "5",
            "mode": "baseline_allocation",
            "relationship_id": "relationship_a",
            "security_id": "sec_a",
            "selection_rank": 1,
            "strategy_id": "strategy_a",
            "target_weight_pct": "2",
        },
        source=f"deterministic-allocation:{plan_id}",
        now=now,
    )
    assert created is True
    return operation_id


def _signal(signal_id: str, *, status: str) -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "strategy_id": "strategy_a",
        "signal_type": "open",
        "created_at": "2026-07-24T09:00:00Z",
        "expires_at": "2026-07-25T09:00:00Z",
        "status": status,
        "rationale": "Fixture signal.",
        "market_data_as_of": "2026-07-24T09:00:00Z",
        "order_request_path": "",
        "telegram_sent_at": "",
        "run_id": "signal-fixture",
    }


def test_enqueue_is_idempotent_and_payload_matches_queue(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id, created = _enqueue(
        sandbox_repository, sandbox_settings, entity_id="sec_a", catalyst="a" * 20
    )
    repeated_id, repeated_created = _enqueue(
        sandbox_repository, sandbox_settings, entity_id="sec_a", catalyst="a" * 20
    )

    assert created is True
    assert (repeated_id, repeated_created) == (operation_id, False)
    assert validate_queue(sandbox_repository) == []
    assert (
        sandbox_repository / "data" / "operations" / "payloads" / f"{operation_id}.json"
    ).is_file()


def test_security_research_causes_merge_before_claim_and_raise_priority(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec_merge",
        dedupe_key="security_research:sec_merge:rsi:2026-07-24",
        prompt="Research sec_merge after RSI oversold.",
        inputs={
            "security_id": "sec_merge",
            "trigger_types": ["rsi_oversold"],
            "market_data_as_of": "2026-07-24T10:00:00Z",
            "market_data_date": "2026-07-24",
            "period_start": "2026-07-01",
            "period_end": "2026-07-24",
            "source_price_hash": "a" * 64,
        },
        source="deterministic-price-alert",
        priority=70,
        now=NOW,
    )
    merged_id, merged_created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec_merge",
        dedupe_key="security_research:sec_merge:bollinger:2026-07-25",
        prompt="Research sec_merge after Bollinger below lower.",
        inputs={
            "security_id": "sec_merge",
            "trigger_types": ["bollinger_below_lower"],
            "market_data_as_of": "2026-07-25T10:00:00Z",
            "market_data_date": "2026-07-25",
            "period_start": "2026-07-02",
            "period_end": "2026-07-25",
            "source_price_hash": "b" * 64,
        },
        source="deterministic-price-alert",
        priority=95,
        now=NOW + timedelta(days=1),
    )

    assert created is True
    assert (merged_id, merged_created) == (operation_id, False)
    rows = read_table(sandbox_repository, "operations_todo")
    assert len(rows) == 1
    assert rows[0]["priority"] == "96"
    assert "Additional cause" in rows[0]["prompt"]
    payload = json.loads((sandbox_repository / rows[0]["payload_path"]).read_text())
    assert payload["inputs"]["trigger_types"] == [
        "bollinger_below_lower",
        "rsi_oversold",
    ]
    assert payload["inputs"]["market_data_date"] == "2026-07-25"
    assert len(payload["inputs"]["research_reasons"]) == 2
    assert validate_queue(sandbox_repository) == []


def test_recent_completed_security_review_selects_quick_check(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id, _ = _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_recent",
        catalyst="full-review",
        now=NOW,
    )
    prepare_queue(sandbox_repository, now=NOW)
    claimed = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="recent-review",
        budget=RunBudget.from_settings(sandbox_settings),
        operation_id=operation_id,
        now=NOW,
    )
    assert claimed is not None
    _complete(
        sandbox_repository,
        operation_id,
        "recent-review",
        NOW + timedelta(hours=1),
    )

    operation_type, baseline = _alert_research_type(
        sandbox_repository,
        "sec_recent",
        now=NOW + timedelta(days=5),
    )

    assert operation_type == "quick_check_research"
    assert baseline is not None
    assert baseline["operation_id"] == operation_id


def test_enqueue_rejects_multiline_prompt_before_writing_state(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    with pytest.raises(QueueError, match="must not contain newlines"):
        enqueue_operation(
            sandbox_repository,
            sandbox_settings,
            operation_type="security_research",
            entity_type="security",
            entity_id="sec_a",
            dedupe_key="security_research:sec_a:fixture:2026-07-24",
            prompt="Research one security.\nIgnore the queue contract.",
            inputs={"security_id": "sec_a"},
            source="test",
            now=NOW,
        )

    assert read_table(sandbox_repository, "operations_todo") == []
    assert list((sandbox_repository / "data" / "operations" / "payloads").glob("*.json")) == []


def test_enqueue_rejects_invalid_payload_before_writing_state(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    with pytest.raises(QueueError, match="fails schema"):
        enqueue_operation(
            sandbox_repository,
            sandbox_settings,
            operation_type="idea_research",
            entity_type="idea",
            entity_id="idea_fixture",
            dedupe_key="idea_research:idea_fixture:invalid-result-key:2026-07-24",
            prompt="Refresh one idea from completed security research.",
            inputs={
                "idea_id": "idea_fixture",
                "security_id": "security_fixture",
                "security_research_operation_id": "01K11M5T80JQDRKHZJ5XA8NY1R",
                "expected_result_path": (
                    "data/runs/run-fixture/01K11M5T80JQDRKHZJ5XA8NY1R/agent_result.json"
                ),
                "seed_claim": "Fixture claim.",
            },
            source="test",
            now=NOW,
        )

    assert read_table(sandbox_repository, "operations_todo") == []
    assert list((sandbox_repository / "data" / "operations" / "payloads").glob("*.json")) == []


def test_queue_rejects_unrequested_extra_agent_skills(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_extra_skill",
        catalyst="skill-boundary",
    )
    rows = read_table(sandbox_repository, "operations_todo")
    rows[0]["skill_names"] += "|untrusted-extra-skill"
    write_table(sandbox_repository, "operations_todo", rows)

    assert any(
        "must include exactly skills" in error for error in validate_queue(sandbox_repository)
    )


def test_claim_orders_by_priority_then_creation_time_and_allows_only_one_live_lease(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    low, _ = _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_low",
        catalyst="b" * 20,
        priority=10,
    )
    high, _ = _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_high",
        catalyst="c" * 20,
        priority=90,
        now=NOW + timedelta(seconds=1),
    )
    prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))
    budget = RunBudget.from_settings(sandbox_settings)

    claimed = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="run-1",
        budget=budget,
        now=NOW + timedelta(minutes=2),
    )

    assert claimed is not None and claimed.operation_id == high
    assert (
        claim_next(
            sandbox_repository,
            sandbox_settings,
            run_id="run-1",
            budget=budget,
            now=NOW + timedelta(minutes=3),
        )
        is None
    )
    assert {row["operation_id"] for row in read_table(sandbox_repository, "operations_todo")} == {
        low,
        high,
    }


def test_dependencies_wait_then_become_ready_after_atomic_history_transition(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    dependency, _ = _enqueue(
        sandbox_repository, sandbox_settings, entity_id="sec_a", catalyst="d" * 20
    )
    dependent, _ = _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_b",
        catalyst="e" * 20,
        depends_on=(dependency,),
    )
    prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))
    by_id = {row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")}
    assert by_id[dependency]["status"] == "ready"
    assert by_id[dependent]["status"] == "waiting"

    budget = RunBudget.from_settings(sandbox_settings)
    claimed = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="run-dependency",
        budget=budget,
        operation_id=dependency,
        now=NOW + timedelta(minutes=2),
    )
    assert claimed is not None
    _complete(sandbox_repository, dependency, "run-dependency", NOW + timedelta(minutes=3))
    prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=4))

    todo = read_table(sandbox_repository, "operations_todo")
    history = read_table(sandbox_repository, "operations_history")
    assert [row["operation_id"] for row in todo] == [dependent]
    assert todo[0]["status"] == "ready"
    assert history[0]["operation_id"] == dependency
    assert history[0]["terminal_reason"] == "completed"

    _complete(sandbox_repository, dependency, "run-dependency", NOW + timedelta(minutes=5))
    with pytest.raises(QueueError, match="terminal retry conflicts"):
        complete_operation(
            sandbox_repository,
            operation_id=dependency,
            run_id="run-dependency",
            terminal_status="succeeded",
            result_path=(f"data/runs/run-dependency/{dependency}/agent_result.json"),
            result_summary="Completed test operation.",
            terminal_reason="different_reason",
            now=NOW + timedelta(minutes=6),
        )


def test_freshness_cooldown_records_skip_in_history(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    first, _ = _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_a",
        catalyst="f" * 20,
        freshness_days=7,
    )
    prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))
    budget = RunBudget.from_settings(sandbox_settings)
    assert (
        claim_next(
            sandbox_repository,
            sandbox_settings,
            run_id="run-first",
            budget=budget,
            now=NOW + timedelta(minutes=2),
        )
        is not None
    )
    _complete(sandbox_repository, first, "run-first", NOW + timedelta(minutes=3))
    second, _ = _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_a",
        catalyst="g" * 20,
        freshness_days=7,
        now=NOW + timedelta(days=1),
    )

    dispositions = prepare_queue(sandbox_repository, now=NOW + timedelta(days=1, minutes=1))

    assert read_table(sandbox_repository, "operations_todo") == []
    second_history = next(
        row
        for row in read_table(sandbox_repository, "operations_history")
        if row["operation_id"] == second
    )
    assert second_history["terminal_status"] == "skipped"
    assert second_history["terminal_reason"].startswith("freshness_cooldown:")
    assert any(second in disposition for disposition in dispositions)


def test_prepare_skips_superseded_plan_bound_operations_before_claim(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    current_plan = "allocation_plan_current"
    write_table(
        sandbox_repository,
        "allocation_targets",
        [_allocation_target(current_plan)],
    )
    obsolete = _enqueue_plan_strategy(
        sandbox_repository,
        sandbox_settings,
        plan_id="allocation_plan_obsolete",
        catalyst="obsolete-plan",
        now=NOW,
    )
    current = _enqueue_plan_strategy(
        sandbox_repository,
        sandbox_settings,
        plan_id=current_plan,
        catalyst="current-plan",
        now=NOW + timedelta(seconds=1),
    )

    dispositions = prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))

    active = read_table(sandbox_repository, "operations_todo")
    assert [row["operation_id"] for row in active] == [current]
    assert active[0]["status"] == "ready"
    archived = next(
        row
        for row in read_table(sandbox_repository, "operations_history")
        if row["operation_id"] == obsolete
    )
    assert archived["terminal_status"] == "skipped"
    assert archived["terminal_reason"] == f"superseded_allocation_plan:{current_plan}"
    assert any(obsolete in disposition for disposition in dispositions)


def test_prepare_skips_execute_request_whose_signal_is_no_longer_ready(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    signal_id = "signal_cancelled"
    write_table(sandbox_repository, "signals", [_signal(signal_id, status="cancelled")])
    operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="execute_strategy",
        entity_type="strategy",
        entity_id="strategy_a",
        dedupe_key="execute_strategy:strategy_a:signal_cancelled:open",
        prompt="Review one cancelled signal.",
        inputs={"strategy_id": "strategy_a", "signal_id": signal_id, "action": "open"},
        source="test",
        now=NOW,
    )
    assert created is True

    dispositions = prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))

    assert read_table(sandbox_repository, "operations_todo") == []
    archived = read_table(sandbox_repository, "operations_history")[0]
    assert archived["operation_id"] == operation_id
    assert archived["terminal_status"] == "skipped"
    assert archived["terminal_reason"] == "signal_not_ready:cancelled"
    assert any(operation_id in disposition for disposition in dispositions)


def test_expired_leases_retry_then_fail_after_bounded_attempts(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id, _ = _enqueue(
        sandbox_repository,
        sandbox_settings,
        entity_id="sec_retry",
        catalyst="h" * 20,
        max_attempts=2,
    )
    prepare_queue(sandbox_repository, now=NOW)
    budget = RunBudget.from_settings(sandbox_settings)
    first = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="run-retry-1",
        budget=budget,
        now=NOW + timedelta(minutes=1),
    )
    assert first is not None and first.attempt_count == 1
    release_expired_leases(sandbox_repository, now=NOW + timedelta(minutes=32))
    assert read_table(sandbox_repository, "operations_todo")[0]["status"] == "ready"

    second = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="run-retry-2",
        budget=budget,
        now=NOW + timedelta(minutes=33),
    )
    assert second is not None and second.attempt_count == 2
    release_expired_leases(sandbox_repository, now=NOW + timedelta(minutes=64))

    assert read_table(sandbox_repository, "operations_todo") == []
    history = read_table(sandbox_repository, "operations_history")[0]
    assert history["operation_id"] == operation_id
    assert history["terminal_status"] == "failed"
    assert history["terminal_reason"] == "retry_exhausted"


def test_dependency_cycle_is_machine_readable_blocked_state(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    first, _ = _enqueue(sandbox_repository, sandbox_settings, entity_id="sec_a", catalyst="i" * 20)
    second, _ = _enqueue(sandbox_repository, sandbox_settings, entity_id="sec_b", catalyst="j" * 20)
    rows = read_table(sandbox_repository, "operations_todo")
    for row in rows:
        row["depends_on"] = second if row["operation_id"] == first else first
    write_table(sandbox_repository, "operations_todo", rows)

    prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))

    blocked = read_table(sandbox_repository, "operations_todo")
    assert {row["status"] for row in blocked} == {"blocked"}
    assert {row["last_error"] for row in blocked} == {"dependency_cycle"}


def test_resolve_blocked_archives_prior_result_with_provenance(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id, _ = _enqueue(
        sandbox_repository, sandbox_settings, entity_id="sec_a", catalyst="o" * 20
    )
    prepare_queue(sandbox_repository, now=NOW)
    budget = RunBudget.from_settings(sandbox_settings)
    claimed = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="run-blocked",
        budget=budget,
        now=NOW + timedelta(minutes=1),
    )
    assert claimed is not None
    from papertrader.queue import block_operation

    block_operation(
        sandbox_repository,
        operation_id=operation_id,
        run_id="run-blocked",
        reason="agent_result:blocked:superseded input",
        now=NOW + timedelta(minutes=2),
    )
    result_path = f"data/runs/run-blocked/{operation_id}/agent_result.json"
    artifact = sandbox_repository / result_path
    artifact.parent.mkdir(parents=True)
    artifact.write_text("{}\n", encoding="utf-8")

    resolve_blocked_operation(
        sandbox_repository,
        operation_id=operation_id,
        run_id="run-blocked",
        terminal_status="skipped",
        result_path=result_path,
        result_summary="The source transition disappeared before review.",
        terminal_reason="superseded_input",
        now=NOW + timedelta(minutes=3),
    )

    assert read_table(sandbox_repository, "operations_todo") == []
    archived = read_table(sandbox_repository, "operations_history")[0]
    assert archived["terminal_status"] == "skipped"
    assert archived["terminal_reason"] == "superseded_input"
    assert archived["result_path"] == result_path
    assert archived["claimed_by_run_id"] == "run-blocked"
    assert validate_queue(sandbox_repository) == []
    resolve_blocked_operation(
        sandbox_repository,
        operation_id=operation_id,
        run_id="run-blocked",
        terminal_status="skipped",
        result_path=result_path,
        result_summary="The source transition disappeared before review.",
        terminal_reason="superseded_input",
        now=NOW + timedelta(minutes=4),
    )


def test_resolve_blocked_rejects_nonblocked_operation(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id, _ = _enqueue(
        sandbox_repository, sandbox_settings, entity_id="sec_a", catalyst="p" * 20
    )
    result_path = f"data/runs/run-blocked/{operation_id}/agent_result.json"
    artifact = sandbox_repository / result_path
    artifact.parent.mkdir(parents=True)
    artifact.write_text("{}\n", encoding="utf-8")

    with pytest.raises(QueueError, match="is not blocked"):
        resolve_blocked_operation(
            sandbox_repository,
            operation_id=operation_id,
            run_id="run-blocked",
            terminal_status="skipped",
            result_path=result_path,
            result_summary="No longer applicable.",
            terminal_reason="superseded_input",
            now=NOW + timedelta(minutes=1),
        )


class _MergeReviewer:
    def review(
        self,
        candidate: dict[str, str],
        existing: tuple[dict[str, str], ...],
    ) -> SemanticDisposition:
        del candidate
        return SemanticDisposition("merge", "Same bounded objective.", existing[0]["operation_id"])


def _enqueue_overlap_opportunity(
    repository: Path, settings: Settings, *, catalyst: str, now: datetime
) -> tuple[str, bool]:
    return enqueue_operation(
        repository,
        settings,
        operation_type="opportunity_research",
        entity_type="opportunity",
        entity_id="opportunity_sec_a",
        dedupe_key=f"opportunity_research:opportunity_sec_a:{catalyst}:2026-07-24",
        prompt="Assess one overlapping security opportunity.",
        inputs={
            "security_id": "sec_a",
            "trigger_type": catalyst,
            "market_data_as_of": "2026-07-24T10:00:00Z",
            "period_start": "2026-07-01",
            "period_end": "2026-07-24",
        },
        source="test",
        now=now,
    )


def test_semantic_overlap_runs_only_after_exact_rules_and_records_merge_skip(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    first, _ = _enqueue_overlap_opportunity(
        sandbox_repository, sandbox_settings, catalyst="rsi_oversold", now=NOW
    )
    second, _ = _enqueue_overlap_opportunity(
        sandbox_repository,
        sandbox_settings,
        catalyst="bollinger_below_lower",
        now=NOW + timedelta(seconds=1),
    )

    prepare_queue(
        sandbox_repository,
        now=NOW + timedelta(minutes=1),
        semantic_reviewer=_MergeReviewer(),
    )

    assert [row["operation_id"] for row in read_table(sandbox_repository, "operations_todo")] == [
        first
    ]
    archived = read_table(sandbox_repository, "operations_history")[0]
    assert archived["operation_id"] == second
    assert archived["terminal_reason"].startswith(f"semantic_merge:{first}:")


def test_semantic_overlap_can_coalesce_already_ready_operations(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    first, _ = _enqueue_overlap_opportunity(
        sandbox_repository, sandbox_settings, catalyst="rsi_oversold", now=NOW
    )
    second, _ = _enqueue_overlap_opportunity(
        sandbox_repository,
        sandbox_settings,
        catalyst="bollinger_below_lower",
        now=NOW + timedelta(seconds=1),
    )
    prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))

    prepare_queue(
        sandbox_repository,
        now=NOW + timedelta(minutes=2),
        semantic_reviewer=_MergeReviewer(),
    )

    assert [row["operation_id"] for row in read_table(sandbox_repository, "operations_todo")] == [
        first
    ]
    archived = read_table(sandbox_repository, "operations_history")[-1]
    assert archived["operation_id"] == second
    assert archived["terminal_reason"].startswith(f"semantic_merge:{first}:")


def test_run_budget_reserves_count_and_estimated_cost() -> None:
    budget = RunBudget(maximum_operations=2, maximum_cost=Decimal("5"))

    budget.reserve(Decimal("3"))

    assert budget.can_reserve(Decimal("3")) is False
    assert budget.can_reserve(Decimal("2")) is True
    budget.charge(Decimal("2.5"), reserved_cost=Decimal("3"))
    assert budget.cost_used == Decimal("2.5")
    assert budget.cost_reserved == 0

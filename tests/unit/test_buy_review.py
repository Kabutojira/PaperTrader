from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from test_execution_accounting import START, _empty_state, _leg, _reference, _setup_strategy

from papertrader.atomic_io import atomic_write_json
from papertrader.buy_review import (
    PACKETS,
    REVIEWS,
    BuyReviewError,
    BuyReviewPending,
    accept_review,
    packet_for_operation,
    requires_review,
    submit_approved_packet,
    validate_clearance,
    validate_fill_envelope,
)
from papertrader.config import Settings
from papertrader.execution import process_order_fill
from papertrader.models import MarketBar, RiskPosition
from papertrader.orders import create_paper_order, create_signal
from papertrader.queue import Operation
from papertrader.tables import read_table, write_table
from papertrader.utils import format_timestamp


def pending(root: Path, settings: Settings) -> tuple[Operation, dict]:
    leg = _leg(action="buy", side="long")
    _setup_strategy(root, settings, "strategy_review", leg)
    signal_id, _ = create_signal(
        root,
        settings,
        strategy_id="strategy_review",
        signal_type="open",
        rationale="Fixture concrete purchase",
        market_data_as_of=START,
        run_id="fixture",
        now=START,
    )
    kwargs = dict(
        signal_id=signal_id,
        strategy_id="strategy_review",
        legs=(leg,),
        references=(_reference(price="100", as_of=START),),
        risk_state=_empty_state(),
        run_id="fixture",
        now=START,
    )
    with pytest.raises(BuyReviewPending):
        create_paper_order(root, settings, **kwargs)
    operation = Operation.from_row(read_table(root, "operations_todo")[0])
    return operation, kwargs


def reviewed(
    root: Path,
    settings: Settings,
    operation: Operation,
    *,
    decision: str = "APPROVE",
    model: str = "gpt-6-astra",
    accepted_at=START + timedelta(minutes=5),
) -> dict:
    """Mock the trusted runner's artifacts, never an agent-supplied model-name field."""
    packet = packet_for_operation(root, operation)
    review = dict(
        review_request_id=packet["review_request_id"],
        packet_hash=packet["packet_hash"],
        decision=decision,
        reason="Independent fixture review",
        examined_evidence=["fixture:primary"],
        counterevidence="Competing explanation examined",
        material_issues=[],
        uncertainty="Demand may miss assumptions",
        reconsideration_conditions=[],
    )
    result = {"status": "succeeded", "final_buy_review": review}
    directory = root / "data/runs/reviewer" / operation.operation_id
    directory.mkdir(parents=True, exist_ok=True)
    provenance = dict(
        run_id="reviewer",
        operation_id=operation.operation_id,
        profile="final_review",
        completed_at=format_timestamp(accepted_at),
    )
    for filename, value in {
        "hermes_run.json": {
            **provenance,
            "model": model,
            "provider": "openai-codex",
            "reasoning_effort": "high",
            "returncode": 0,
        },
        "validation_report.json": {**provenance, "passed": True},
        "agent_result.json": result,
    }.items():
        atomic_write_json(directory / filename, value, allowed_root=root)
    return accept_review(root, settings, operation, result, run_id="reviewer", now=accepted_at)


def test_preflight_enqueues_once_without_persisting_order(sandbox_repository, sandbox_settings):
    operation, kwargs = pending(sandbox_repository, sandbox_settings)
    with pytest.raises(BuyReviewPending):
        create_paper_order(sandbox_repository, sandbox_settings, **kwargs)
    assert len(read_table(sandbox_repository, "operations_todo")) == 1
    assert len(list((sandbox_repository / PACKETS).glob("*.json"))) == 1
    assert read_table(sandbox_repository, "orders") == []
    assert read_table(sandbox_repository, "order_legs") == []
    assert read_table(sandbox_repository, "signals")[0]["status"] == "ready"
    assert operation.operation_type == "final_buy_review"


@pytest.mark.parametrize("decision", ["REJECT", "DEFER"])
def test_unchanged_veto_never_requeues_or_orders(sandbox_repository, sandbox_settings, decision):
    operation, kwargs = pending(sandbox_repository, sandbox_settings)
    reviewed(sandbox_repository, sandbox_settings, operation, decision=decision)
    with pytest.raises(BuyReviewPending, match="final_review_" + decision.lower()):
        create_paper_order(sandbox_repository, sandbox_settings, **kwargs)
    assert len(read_table(sandbox_repository, "operations_todo")) == 1
    assert read_table(sandbox_repository, "orders") == []


def test_lower_model_cannot_authenticate_approval(sandbox_repository, sandbox_settings):
    operation, _ = pending(sandbox_repository, sandbox_settings)
    with pytest.raises(BuyReviewError, match="successful Astra"):
        reviewed(sandbox_repository, sandbox_settings, operation, model="gpt-5.6-sol")
    assert not list((sandbox_repository / REVIEWS).glob("*.json"))


def test_pre_review_revalidation_rejects_material_change_without_order(
    sandbox_repository, sandbox_settings
):
    from papertrader.buy_review import revalidate_packet

    operation, _ = pending(sandbox_repository, sandbox_settings)
    packet = packet_for_operation(sandbox_repository, operation)
    rows = read_table(sandbox_repository, "strategies")
    rows[0]["thesis"] = "Changed material investment mechanism"
    write_table(sandbox_repository, "strategies", rows)
    with pytest.raises(BuyReviewError, match="material_state_changed"):
        revalidate_packet(
            sandbox_repository, sandbox_settings, packet, now=START + timedelta(minutes=2)
        )
    assert not read_table(sandbox_repository, "orders")


def test_price_only_projection_does_not_rewrite_review_substance(
    sandbox_repository, sandbox_settings
):
    from papertrader.buy_review import material_state

    pending(sandbox_repository, sandbox_settings)
    before = material_state(sandbox_repository, {"sec_a"}, "strategy_review")
    rows = read_table(sandbox_repository, "security_assessments")
    for row in rows:
        row["reference_price"] = "99"
        row["expected_return_pct"] = "31"
    write_table(sandbox_repository, "security_assessments", rows)
    assert material_state(sandbox_repository, {"sec_a"}, "strategy_review") == before


def test_acceptance_resumes_and_submission_is_idempotent(sandbox_repository, sandbox_settings):
    operation, _ = pending(sandbox_repository, sandbox_settings)
    reviewed(sandbox_repository, sandbox_settings, operation)
    assert read_table(sandbox_repository, "orders") == []  # crash boundary
    submit_approved_packet(
        sandbox_repository, sandbox_settings, operation, now=START + timedelta(minutes=6)
    )
    original = read_table(sandbox_repository, "orders")
    submit_approved_packet(
        sandbox_repository, sandbox_settings, operation, now=START + timedelta(days=2)
    )
    assert len(original) == 1
    assert read_table(sandbox_repository, "orders") == original
    assert original[0]["not_before"] == format_timestamp(START + timedelta(minutes=6))


def test_parent_restart_uses_prior_acceptance_without_model(sandbox_repository, sandbox_settings):
    from papertrader.buy_review import finish_review_operation
    from papertrader.queue import RunBudget, claim_next, prepare_queue

    operation, _ = pending(sandbox_repository, sandbox_settings)
    reviewed(sandbox_repository, sandbox_settings, operation)
    instant = START + timedelta(minutes=6)
    prepare_queue(sandbox_repository, now=instant)
    claimed = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="resumed",
        budget=RunBudget(1, Decimal("5")),
        now=instant,
    )
    assert claimed is not None
    assert (
        finish_review_operation(
            sandbox_repository, sandbox_settings, claimed, run_id="resumed", now=instant
        )
        == "succeeded"
    )
    assert len(read_table(sandbox_repository, "orders")) == 1
    history = read_table(sandbox_repository, "operations_history")
    assert (
        history[0]["result_path"] == f"data/runs/resumed/{operation.operation_id}/agent_result.json"
    )
    assert (
        sandbox_repository / "data/runs/reviewer" / operation.operation_id / "agent_result.json"
    ).exists()


def test_material_state_and_provenance_cannot_change(sandbox_repository, sandbox_settings):
    operation, _ = pending(sandbox_repository, sandbox_settings)
    review = reviewed(sandbox_repository, sandbox_settings, operation)
    packet = packet_for_operation(sandbox_repository, operation)
    rows = read_table(sandbox_repository, "strategies")
    rows[0]["updated_at"] = format_timestamp(START + timedelta(minutes=7))
    write_table(sandbox_repository, "strategies", rows)
    validate_clearance(sandbox_repository, packet, review, now=START + timedelta(minutes=8))
    rows[0]["thesis"] = "Changed investment premise"
    write_table(sandbox_repository, "strategies", rows)
    with pytest.raises(BuyReviewError, match="material state"):
        validate_clearance(sandbox_repository, packet, review, now=START + timedelta(minutes=8))
    review["invocation_path"] = "data/runs/another/hermes_run.json"
    with pytest.raises(BuyReviewError, match="provenance path"):
        validate_clearance(sandbox_repository, packet, review, now=START + timedelta(minutes=8))


def test_price_fx_and_quantity_envelope(sandbox_repository, sandbox_settings):
    operation, _ = pending(sandbox_repository, sandbox_settings)
    packet = packet_for_operation(sandbox_repository, operation)
    leg = _leg(action="buy", side="long")
    validate_fill_envelope(packet, leg, price=Decimal("100"), fx=Decimal("1"))
    for price, fx in [("101", "1"), ("100", "1.01")]:
        with pytest.raises(BuyReviewError, match="envelope"):
            validate_fill_envelope(packet, leg, price=Decimal(price), fx=Decimal(fx))
    with pytest.raises(BuyReviewError, match="quantity"):
        validate_fill_envelope(
            packet, replace(leg, quantity=Decimal("11")), price=Decimal("100"), fx=Decimal("1")
        )


def test_next_open_does_not_fill_before_approval(sandbox_repository, sandbox_settings):
    operation, _ = pending(sandbox_repository, sandbox_settings)
    reviewed(sandbox_repository, sandbox_settings, operation)
    submit_approved_packet(
        sandbox_repository, sandbox_settings, operation, now=START + timedelta(minutes=6)
    )
    order = read_table(sandbox_repository, "orders")[0]

    def bar(minutes):
        return MarketBar(
            "sec_a",
            "",
            START + timedelta(minutes=minutes),
            Decimal("100"),
            Decimal("101"),
            Decimal("99"),
            Decimal("100"),
            "USD",
            Decimal("1"),
        )

    status, ids = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order["order_id"],
        bars=(bar(2),),
        quotes=(),
        risk_state=_empty_state(),
        risk_references=(_reference(price="100", as_of=START),),
        run_id="fill",
        now=START + timedelta(minutes=10),
    )
    assert status == "pending" and not ids
    status, ids = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order["order_id"],
        bars=(bar(2), bar(8)),
        quotes=(),
        risk_state=_empty_state(),
        risk_references=(_reference(price="100", as_of=START),),
        run_id="fill",
        now=START + timedelta(minutes=10),
    )
    assert status == "filled" and len(ids) == 1
    assert read_table(sandbox_repository, "executions")[0]["executed_at"] == format_timestamp(
        START + timedelta(minutes=8)
    )


def test_reduction_and_cover_quantity_classification():
    long = RiskPosition(
        "sec_a", "", "long", "equity", Decimal("10"), Decimal("1"), "USD", "", None, None
    )
    short = replace(long, side="short")
    state = replace(_empty_state(), positions=(long, short))
    assert not requires_review((_leg(action="sell", side="long"),), state)
    assert not requires_review((_leg(action="buy", side="short"),), state)
    assert requires_review(
        (replace(_leg(action="buy", side="short"), quantity=Decimal("11")),), state
    )
    assert requires_review(
        (_leg(action="sell", side="long"), _leg(action="buy", side="long")), state
    )

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.advice import (
    AdviceError,
    build_decision_snapshot,
    reason_label,
    refresh_advice,
    snapshot_document,
    validate_advice,
)
from papertrader.config import Settings
from papertrader.execution import ensure_initial_capital, process_order_fill
from papertrader.issues import record_issue
from papertrader.models import MarketBar, OrderLegSpec, ReferencePrice
from papertrader.orders import create_paper_order, create_signal
from papertrader.portfolio import build_risk_state
from papertrader.tables import read_table, write_table
from papertrader.utils import required_decimal

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def _security(
    index: int = 0,
    *,
    company_name: str | None = None,
    research_page: str = "",
) -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "security_id": f"sec_{suffix}",
        "issuer_id": f"issuer_{suffix}",
        "company_name": company_name or f"Decision Candidate {suffix}",
        "instrument_name": f"Decision Candidate {suffix} common stock",
        "instrument_type": "equity",
        "ticker": f"D{suffix}",
        "exchange_code": "XETR",
        "venue_mic": "XETR",
        "provider_symbol": f"D{suffix}.DE",
        "broker_symbol": "",
        "currency": "EUR",
        "country": "DE",
        "sector": f"Sector {suffix}",
        "industry": "Decision fixture",
        "status": "active",
        "watchlist_reason": "Decision-publication fixture.",
        "research_summary": "Evidence-backed deterministic fixture.",
        "research_page": research_page,
        "last_research_at": "2026-07-24T10:00:00Z",
        "next_review_at": "2026-08-24T10:00:00Z",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-24T10:00:00Z",
        "source": "fixture",
    }


def _strategy(index: int = 0) -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "strategy_id": f"strategy_{suffix}",
        "idea_id": f"idea_{suffix}",
        "security_id": f"sec_{suffix}",
        "relationship_id": "",
        "name": f"Decision strategy {suffix}",
        "status": "ready",
        "direction": "long",
        "instrument_type": "equity",
        "thesis": "The current evidence supports one bounded paper position.",
        "entry_rule": "Enter only through a validated paper order.",
        "exit_rule": "Exit when the evidence or valuation changes.",
        "invalidation": "The evidence-backed mechanism fails.",
        "risk_budget_pct": "5",
        "sleeve": "conviction",
        "allocation_plan_id": "",
        "not_before": "",
        "expires_at": "2026-08-24T12:00:00Z",
        "research_page": "",
        "created_at": "2026-07-24T10:00:00Z",
        "updated_at": "2026-07-24T10:00:00Z",
    }


def _strategy_leg(index: int = 0, *, quantity: str = "10") -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "strategy_id": f"strategy_{suffix}",
        "leg_id": f"leg_{suffix}",
        "action": "buy",
        "side": "long",
        "instrument_type": "equity",
        "security_id": f"sec_{suffix}",
        "provider_contract_id": "",
        "option_type": "",
        "expiry": "",
        "strike": "",
        "quantity": quantity,
        "contract_multiplier": "1",
        "order_type": "market",
        "limit_price": "",
        "currency": "EUR",
    }


def _relationship(*, next_review_at: str = "2026-08-24T12:00:00Z") -> dict[str, str]:
    return {
        "relationship_id": "relationship_00",
        "idea_id": "idea_00",
        "security_id": "sec_00",
        "relationship_type": "beneficiary",
        "direction": "positive",
        "mechanism": "The evidence-backed mechanism benefits this security.",
        "sensitivity": "medium",
        "confidence": "high",
        "catalyst": "The modeled catalyst occurs.",
        "invalidation": "The modeled mechanism fails.",
        "status": "accepted",
        "research_page": "",
        "last_reviewed_at": "2026-07-24T10:00:00Z",
        "next_review_at": next_review_at,
        "created_at": "2026-07-24T10:00:00Z",
        "updated_at": "2026-07-24T10:00:00Z",
    }


def _market_latest(
    index: int = 0, *, status: str = "ok", retrieved_at: datetime = NOW
) -> dict[str, str]:
    suffix = f"{index:02d}"
    failed = status != "ok"
    return {
        "security_id": f"sec_{suffix}",
        "provider_symbol": f"D{suffix}.DE",
        "price_date": retrieved_at.date().isoformat(),
        "retrieved_at": retrieved_at.isoformat().replace("+00:00", "Z"),
        "open": "99" if not failed else "",
        "high": "101" if not failed else "",
        "low": "98" if not failed else "",
        "close": "100" if not failed else "",
        "adjusted_close": "100" if not failed else "",
        "volume": "1000000" if not failed else "",
        "currency": "EUR",
        "source": "fixture",
        "status": status,
        "error": "retrieval failed" if failed else "",
    }


def _assessment(index: int = 0) -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "security_id": f"sec_{suffix}",
        "assessed_at": "2026-07-24T11:00:00Z",
        "expires_at": "2026-08-24T11:00:00Z",
        "eligibility": "baseline",
        "confidence": "high",
        "thesis_score": "80",
        "business_quality_score": "80",
        "balance_sheet_score": "80",
        "valuation_score": "80",
        "timing_score": "80",
        "liquidity_score": "80",
        "risk_penalty": "0",
        "downside_pct": "-20",
        "base_upside_pct": "25",
        "valuation_horizon_months": "12",
        "hard_blockers": "",
        "soft_gaps": "",
        "evidence_refs": "",
        "run_id": "assessment-fixture",
    }


def _allocation_target(
    index: int = 0,
    *,
    reason: str = "assessment_missing",
    run_id: str = "allocation-fixture",
    as_of: str = "2026-07-24T12:00:00Z",
) -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "allocation_plan_id": "allocation_fixture",
        "run_id": run_id,
        "as_of": as_of,
        "security_id": f"sec_{suffix}",
        "strategy_id": "",
        "sleeve": "baseline",
        "rank": "",
        "effective_score": "80" if reason != "assessment_missing" else "",
        "candidate_edge": "20" if reason != "assessment_missing" else "",
        "current_weight_pct": "0",
        "pending_weight_pct": "0",
        "target_weight_pct": "0",
        "target_value_base": "0",
        "delta_value_base": "0",
        "disposition": "excluded",
        "reason": reason,
        "assessment_as_of": "2026-07-24T11:00:00Z" if reason != "assessment_missing" else "",
    }


def _indicator(index: int = 0) -> dict[str, str]:
    return {
        "security_id": f"sec_{index:02d}",
        "as_of_date": "2026-07-24",
        "calculated_at": "2026-07-24T12:00:00Z",
        "observation_count": "220",
        "sma_20": "90",
        "sma_50": "85",
        "sma_200": "80",
        "rsi_14": "75",
        "bollinger_mid": "90",
        "bollinger_upper": "99",
        "bollinger_lower": "81",
        "macd": "2",
        "macd_signal": "1",
        "macd_histogram": "1",
        "return_1d": "2",
        "return_5d": "4",
        "return_20d": "8",
        "volume_zscore": "1",
        "volatility_20d": "20",
        "trigger_state": "bollinger_above_upper",
        "source_price_hash": "a" * 64,
    }


def _initialize(repository: Path, settings: Settings, *, run_id: str) -> None:
    ensure_initial_capital(
        repository,
        settings,
        run_id=run_id,
        occurred_at=NOW - timedelta(hours=1),
    )


def _seed_signal(
    repository: Path,
    settings: Settings,
    *,
    with_order: bool,
) -> tuple[str, str, OrderLegSpec, ReferencePrice]:
    research_page = "data/wiki/securities/sec_00.md"
    page = repository / research_page
    page.write_text(
        "---\ntitle: Decision Candidate 00\ntype: security\nstatus: maintained\n"
        "tags:\n  - security\n---\n\n# Decision Candidate 00\n",
        encoding="utf-8",
    )
    write_table(repository, "securities", [_security(research_page=research_page)])
    write_table(repository, "strategies", [_strategy()])
    write_table(repository, "strategy_legs", [_strategy_leg()])
    write_table(repository, "market_latest", [_market_latest()])
    _initialize(repository, settings, run_id="signal-fixture")
    signal_id, created = create_signal(
        repository,
        settings,
        strategy_id="strategy_00",
        signal_type="open",
        rationale="Open the bounded deterministic fixture.",
        market_data_as_of=NOW,
        expires_at=NOW + timedelta(days=3),
        run_id="signal-fixture",
        now=NOW,
    )
    assert created
    leg = OrderLegSpec(
        leg_id="leg_00",
        action="buy",
        side="long",
        instrument_type="equity",
        security_id="sec_00",
        provider_contract_id="",
        option_type="",
        expiry=None,
        strike=None,
        quantity=Decimal("10"),
        contract_multiplier=Decimal("1"),
        limit_price=None,
        currency="EUR",
    )
    reference = ReferencePrice(
        security_id="sec_00",
        provider_contract_id="",
        price=Decimal("100"),
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=NOW,
    )
    order_id = ""
    if with_order:
        order_id, order_created, _ = create_paper_order(
            repository,
            settings,
            signal_id=signal_id,
            strategy_id="strategy_00",
            legs=(leg,),
            references=(reference,),
            risk_state=build_risk_state(repository, (reference,), as_of=NOW),
            run_id="signal-fixture",
            now=NOW,
        )
        assert order_created
    return signal_id, order_id, leg, reference


def test_all_cash_snapshot_is_explicit_idempotent_and_exported(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="cash-fixture")

    first = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="cash-fixture",
        as_of=NOW,
    )
    second = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="cash-fixture",
        as_of=NOW,
    )

    assert snapshot_document(first) == snapshot_document(second)
    assert first.stance == "hold_cash"
    assert first.data_status == "current"
    assert len(first.current_portfolio.rows) == 1
    cash = first.current_portfolio.rows[0]
    assert (cash.holding_type, cash.ticker, cash.current_weight_pct) == ("cash", "CASH", "100")
    assert cash.approved_target_weight_pct == "100"

    published = refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="cash-fixture",
        as_of=NOW,
    )
    assert published.snapshot_id == first.snapshot_id
    assert validate_advice(sandbox_repository, strict=True) == []
    exported = read_table(sandbox_repository, "published_model_portfolio")
    assert exported[0]["snapshot_id"] == published.snapshot_id
    assert exported[0]["holding_type"] == "cash"
    assert read_table(sandbox_repository, "published_actionable_signals") == []
    homepage = (sandbox_repository / "data" / "wiki" / "index.md").read_text(encoding="utf-8")
    assert "No trade — hold 100% cash" in homepage
    assert published.snapshot_id in homepage


def test_publication_is_deterministic_under_input_permutation_and_ignores_generated_inputs(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="permutation-fixture")
    securities = [_security(0), _security(1)]
    targets = [
        _allocation_target(0, run_id="permutation-fixture"),
        _allocation_target(1, run_id="permutation-fixture"),
    ]
    write_table(sandbox_repository, "securities", securities)
    write_table(sandbox_repository, "allocation_targets", targets)
    first = snapshot_document(
        build_decision_snapshot(
            sandbox_repository,
            sandbox_settings,
            run_id="permutation-fixture",
            as_of=NOW,
        )
    )

    published_path = sandbox_repository / "data" / "published" / "decision_snapshot.json"
    published_path.write_text('{"generated":"must not become input"}\n', encoding="utf-8")
    write_table(sandbox_repository, "securities", list(reversed(securities)))
    write_table(sandbox_repository, "allocation_targets", list(reversed(targets)))
    second = snapshot_document(
        build_decision_snapshot(
            sandbox_repository,
            sandbox_settings,
            run_id="permutation-fixture",
            as_of=NOW,
        )
    )

    assert second == first
    assert [row["security_id"] for row in second["candidate_pipeline"]] == ["sec_00", "sec_01"]


def test_allocation_candidate_and_indicator_remain_non_actionable_research(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="research-fixture")
    security = _security(research_page="data/wiki/securities/sec_00.md")
    write_table(sandbox_repository, "securities", [security])
    write_table(
        sandbox_repository,
        "allocation_targets",
        [_allocation_target(run_id="research-fixture")],
    )
    write_table(sandbox_repository, "indicators", [_indicator()])

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="research-fixture",
        as_of=NOW,
    )

    assert snapshot.actionable_signals == ()
    assert snapshot.candidate_pipeline[0].classification == "assessment_pending"
    assert snapshot.candidate_pipeline[0].reason_labels == (
        "No current comparable assessment is available.",
    )
    assert snapshot.research_alerts[0].visible_label == "Research alert — not a trade signal"
    assert snapshot.research_alerts[0].ticker == "D00"
    assert snapshot.research_alerts[0].alert_type == "bollinger_above_upper"


def test_active_signal_without_order_is_not_copy_ready_and_stale_signal_is_hidden(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    signal_id, _, _, _ = _seed_signal(
        sandbox_repository,
        sandbox_settings,
        with_order=False,
    )
    current = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="active-signal-fixture",
        as_of=NOW,
    )

    assert len(current.actionable_signals) == 1
    signal = current.actionable_signals[0]
    assert signal.signal_id == signal_id
    assert signal.action_status == "awaiting_order_validation"
    assert signal.copy_ready is False
    assert signal.quantity == ""
    assert current.approved_target_portfolio.cash_weight_pct == "100"

    stale = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="stale-signal-fixture",
        as_of=NOW + timedelta(hours=37),
    )
    assert stale.actionable_signals == ()


def test_pending_order_projects_target_and_is_copy_ready_without_mutating_accounting(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    signal_id, order_id, _, _ = _seed_signal(
        sandbox_repository,
        sandbox_settings,
        with_order=True,
    )
    cash_before = tuple(read_table(sandbox_repository, "cash_ledger"))
    executions_before = tuple(read_table(sandbox_repository, "executions"))

    snapshot = refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="pending-order-fixture",
        as_of=NOW,
        render_pages=False,
    )

    assert snapshot.stance == "deploy"
    assert snapshot.current_portfolio.cash_base == "100000"
    assert required_decimal(snapshot.approved_target_portfolio.cash_base, label="cash") > 0
    security = next(
        row for row in snapshot.current_portfolio.rows if row.holding_type == "security"
    )
    assert security.action == "buy"
    assert security.action_status == "pending_order"
    assert security.current_quantity == "0"
    assert security.approved_target_quantity == "10"
    assert security.order_id == order_id
    assert sum(
        required_decimal(row.approved_target_weight_pct, label="weight")
        for row in snapshot.approved_target_portfolio.rows
    ) == Decimal("100")
    signal = snapshot.actionable_signals[0]
    assert (signal.signal_id, signal.order_id, signal.copy_ready, signal.quantity) == (
        signal_id,
        order_id,
        True,
        "10",
    )
    assert signal.legs[0]["security_id"] == "sec_00"
    assert tuple(read_table(sandbox_repository, "cash_ledger")) == cash_before
    assert tuple(read_table(sandbox_repository, "executions")) == executions_before
    assert validate_advice(sandbox_repository, strict=True) == []


def test_stale_pending_order_is_not_partially_projected_or_copy_ready(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_signal(sandbox_repository, sandbox_settings, with_order=True)
    write_table(
        sandbox_repository,
        "market_latest",
        [_market_latest(retrieved_at=NOW - timedelta(days=2))],
    )

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="stale-pending-fixture",
        as_of=NOW,
    )

    assert snapshot.data_status == "blocked"
    assert snapshot.stance == "blocked"
    assert snapshot.stance_reason_codes == ("market_data_stale",)
    assert snapshot.actionable_signals == ()
    assert snapshot.approved_target_portfolio.cash_base == "100000"
    assert snapshot.approved_target_portfolio.cash_weight_pct == "100"
    assert all(row.holding_type == "cash" for row in snapshot.current_portfolio.rows)


def test_expired_nonterminal_order_blocks_copy_and_target_projection(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_signal(sandbox_repository, sandbox_settings, with_order=True)

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="expired-pending-fixture",
        as_of=NOW + timedelta(hours=25),
    )

    assert snapshot.stance == "blocked"
    assert snapshot.stance_reason_codes == ("pending_order_state_unsafe",)
    assert snapshot.actionable_signals == ()
    assert snapshot.approved_target_portfolio.cash_weight_pct == "100"


def test_action_issue_suppresses_signal_and_current_position_market_failure_blocks_snapshot(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _, order_id, _, reference = _seed_signal(
        sandbox_repository,
        sandbox_settings,
        with_order=True,
    )
    fill_time = NOW + timedelta(hours=2)
    fill_reference = ReferencePrice(
        security_id="sec_00",
        provider_contract_id="",
        price=Decimal("101"),
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=fill_time,
    )
    status, _ = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=(
            MarketBar(
                security_id="sec_00",
                provider_contract_id="",
                timestamp=NOW + timedelta(hours=1),
                open=Decimal("100"),
                high=Decimal("102"),
                low=Decimal("99"),
                close=Decimal("101"),
                currency="EUR",
                fx_rate_to_base=Decimal("1"),
            ),
        ),
        quotes=(),
        risk_state=build_risk_state(
            sandbox_repository,
            (fill_reference,),
            as_of=fill_time,
        ),
        risk_references=(fill_reference,),
        run_id="fill-fixture",
        now=fill_time,
    )
    assert status == "filled"
    reduce_signal_id, reduce_created = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id="strategy_00",
        signal_type="reduce",
        rationale="Reduce the filled fixture through a validated paper order.",
        market_data_as_of=fill_time,
        expires_at=fill_time + timedelta(days=2),
        run_id="reduce-fixture",
        now=fill_time,
    )
    assert reduce_created
    reduce_leg = OrderLegSpec(
        leg_id="leg_00",
        action="sell",
        side="long",
        instrument_type="equity",
        security_id="sec_00",
        provider_contract_id="",
        option_type="",
        expiry=None,
        strike=None,
        quantity=Decimal("4"),
        contract_multiplier=Decimal("1"),
        limit_price=None,
        currency="EUR",
    )
    reduce_order_id, reduce_order_created, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=reduce_signal_id,
        strategy_id="strategy_00",
        legs=(reduce_leg,),
        references=(fill_reference,),
        risk_state=build_risk_state(
            sandbox_repository,
            (fill_reference,),
            as_of=fill_time,
        ),
        run_id="reduce-fixture",
        now=fill_time,
    )
    assert reduce_order_created
    reduced = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="reduce-fixture",
        as_of=fill_time,
    )
    reduced_row = next(
        row for row in reduced.current_portfolio.rows if row.holding_type == "security"
    )
    assert reduced_row.current_quantity == "10"
    assert reduced_row.approved_target_quantity == "6"
    assert reduced_row.action == "trim"
    assert reduced.actionable_signals[0].order_id == reduce_order_id
    assert reduced.actionable_signals[0].copy_ready is True
    assert required_decimal(reduced.approved_target_portfolio.cash_base, label="target cash") > (
        required_decimal(reduced.current_portfolio.cash_base, label="current cash")
    )
    write_table(
        sandbox_repository,
        "market_latest",
        [_market_latest(status="error", retrieved_at=fill_time)],
    )

    blocked = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="blocked-position-fixture",
        as_of=fill_time,
    )
    assert blocked.data_status == "blocked"
    assert blocked.stance == "blocked"
    assert blocked.stance_reason_codes == ("market_data_not_ok",)
    assert blocked.actionable_signals == ()
    assert blocked.current_portfolio.gross_exposure_base != "0"
    assert reference.currency == "EUR"


def test_global_action_issue_blocks_active_recommendation(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_signal(sandbox_repository, sandbox_settings, with_order=False)
    record_issue(
        sandbox_repository,
        severity="error",
        title="Order validation unavailable",
        description="The deterministic order gate is unavailable for current signals.",
        now=NOW,
    )

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="issue-block-fixture",
        as_of=NOW,
    )
    assert snapshot.actionable_signals == ()
    assert snapshot.data_status == "degraded"
    assert any(impact.impact == "blocks_action" for impact in snapshot.system_impacts)


def test_candidate_market_failure_degrades_without_blocking_cash_portfolio(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="candidate-failure-fixture")
    write_table(sandbox_repository, "securities", [_security()])
    write_table(sandbox_repository, "security_assessments", [_assessment()])
    write_table(
        sandbox_repository,
        "allocation_targets",
        [_allocation_target(reason="market_data_not_ok", run_id="candidate-failure-fixture")],
    )
    write_table(sandbox_repository, "market_latest", [_market_latest(status="error")])

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="candidate-failure-fixture",
        as_of=NOW,
    )
    assert snapshot.data_status == "degraded"
    assert snapshot.stance == "hold_cash"
    assert snapshot.candidate_pipeline[0].classification == "market_data_blocked"
    assert snapshot.current_portfolio.gross_exposure_base == "0"


def test_stale_plan_and_relationship_cannot_publish_an_approved_candidate(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    run_id = "candidate-current-fixture"
    _initialize(sandbox_repository, sandbox_settings, run_id=run_id)
    target = _allocation_target(reason="above_cash_hurdle", run_id=run_id)
    target["strategy_id"] = "strategy_00"
    target["target_weight_pct"] = "5"
    write_table(sandbox_repository, "securities", [_security()])
    write_table(sandbox_repository, "security_assessments", [_assessment()])
    write_table(sandbox_repository, "relationships", [_relationship()])
    write_table(sandbox_repository, "strategies", [_strategy()])
    write_table(sandbox_repository, "market_latest", [_market_latest()])
    write_table(sandbox_repository, "allocation_targets", [target])

    current = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=NOW,
    )
    assert current.candidate_pipeline[0].classification == "approved"
    assert current.coverage.current_relationship_count == 1

    stale = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="candidate-later-fixture",
        as_of=NOW,
    )
    assert stale.candidate_pipeline[0].classification == "research_blocked"
    assert stale.candidate_pipeline[0].target_weight_pct == "0"
    assert "allocation_plan_stale" in stale.candidate_pipeline[0].reason_codes

    write_table(
        sandbox_repository,
        "relationships",
        [_relationship(next_review_at="2026-07-24T12:00:00Z")],
    )
    missing_relationship = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=NOW,
    )
    assert missing_relationship.candidate_pipeline[0].classification == "relationship_pending"
    assert missing_relationship.coverage.current_relationship_count == 0


def test_reason_translation_is_complete_and_unknown_codes_fail_closed() -> None:
    assert reason_label("conviction_exposure_present").startswith(
        "The security is already represented"
    )
    assert reason_label("hard_blocker:valuation_unsupported") == (
        "A supportable valuation is unavailable."
    )
    with pytest.raises(AdviceError, match="unknown decision reason code"):
        reason_label("not_a_canonical_reason")


def test_published_snapshot_tampering_is_detected(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="tamper-fixture")
    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="tamper-fixture",
        as_of=NOW,
        render_pages=False,
    )
    path = sandbox_repository / "data" / "published" / "decision_snapshot.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["stance"] = "maintain"
    path.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")

    assert "published decision snapshot differs from its immutable run artifact" in validate_advice(
        sandbox_repository, strict=True
    )


def test_in_flight_validation_defers_only_current_source_state(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="in-flight-fixture")
    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="in-flight-fixture",
        as_of=NOW,
        render_pages=False,
    )
    write_table(sandbox_repository, "securities", [_security()])

    assert "published decision snapshot does not match current authoritative state" in (
        validate_advice(sandbox_repository, strict=True)
    )
    assert (
        validate_advice(
            sandbox_repository,
            strict=True,
            require_current_state=False,
        )
        == []
    )


def test_post_publication_delivery_issue_does_not_stale_decision_snapshot(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="delivery-fixture")
    record_issue(
        sandbox_repository,
        severity="warning",
        title="Telegram delivery failed: prior",
        description="A prior committed investor brief awaits retry.",
        owner="delivery",
        related_run_id="prior-fixture",
        now=NOW - timedelta(minutes=1),
    )
    snapshot = refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="delivery-fixture",
        as_of=NOW,
        render_pages=False,
    )
    assert len(snapshot.system_impacts) == 1
    assert snapshot.system_impacts[0].impact == "publication_only"
    assert "bounded retry" in snapshot.system_impacts[0].summary

    record_issue(
        sandbox_repository,
        severity="warning",
        title="Telegram delivery failed: deadbeef",
        description="The committed investor brief could not be delivered.",
        owner="delivery",
        related_run_id="delivery-fixture",
        now=NOW + timedelta(minutes=1),
    )

    assert validate_advice(sandbox_repository, strict=True) == []
    assert len(snapshot.system_impacts) == 1

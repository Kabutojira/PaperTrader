from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.advice import (
    AdviceError,
    _candidate_classification,
    _decision_csv_contract_bytes,
    _validate_snapshot_object,
    build_decision_snapshot,
    load_published_snapshot,
    reason_label,
    refresh_advice,
    snapshot_document,
    validate_advice,
)
from papertrader.config import Settings
from papertrader.dedupe import build_dedupe_key
from papertrader.execution import ensure_initial_capital, process_order_fill
from papertrader.investor_pages import _public_snapshot
from papertrader.issues import record_issue, resolve_issue
from papertrader.models import MarketBar, OrderLegSpec, ReferencePrice
from papertrader.orders import create_paper_order, create_signal
from papertrader.portfolio import build_risk_state
from papertrader.queue import enqueue_operation
from papertrader.tables import append_unique, read_table, write_table
from papertrader.utils import deterministic_ulid, format_timestamp, required_decimal
from papertrader.wiki import lint_wiki

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def test_technical_series_contract_does_not_change_decision_identity(tmp_path: Path) -> None:
    contracts = tmp_path / "csv_contracts.yaml"
    contracts.write_text(
        """version: 1
dynamic_contracts:
  price_cache:
    glob: data/market/prices/*.csv
    columns: [date]
  technical_series:
    glob: data/market/technical/*.csv
    columns: [date, adjusted_close]
contracts:
  securities:
    path: data/tables/securities.csv
    columns: [security_id]
""",
        encoding="utf-8",
    )

    assert (
        _decision_csv_contract_bytes(contracts).decode("utf-8")
        == """version: 1
dynamic_contracts:
  price_cache:
    glob: data/market/prices/*.csv
    columns: [date]
contracts:
  securities:
    path: data/tables/securities.csv
    columns: [security_id]
"""
    )


def _legacy_v3(document: dict[str, object]) -> dict[str, object]:
    legacy = json.loads(json.dumps(document))
    legacy["version"] = 3
    legacy["approved_target_portfolio"] = legacy.pop("target_portfolio")
    for key in ("current_portfolio", "approved_target_portfolio"):
        portfolio = legacy[key]
        assert isinstance(portfolio, dict)
        if portfolio["portfolio_kind"] == "target":
            portfolio["portfolio_kind"] = "approved_target"
        for row in portfolio["rows"]:
            row["approved_target_weight_pct"] = row.pop("target_weight_pct")
            row["approved_target_value_base"] = row.pop("target_value_base")
            row["approved_target_quantity"] = row.pop("target_quantity")
    for signal in legacy["actionable_signals"]:
        signal["approved_target_weight_pct"] = signal.pop("target_weight_pct")
    for candidate in legacy["candidate_pipeline"]:
        if candidate["classification"] == "strategy_ready":
            candidate["classification"] = "approved"
    benchmark = legacy["research_benchmark"]
    benchmark["non_approved"] = benchmark.pop("comparison_only")
    return legacy


_V5_PORTFOLIO_FIELDS = {
    "tier",
    "allocation_intent_id",
    "assessment_id",
    "valuation_mark",
    "valuation_mark_currency",
    "valuation_mark_as_of",
    "position_cap_pct",
    "margin_of_safety_pct",
    "bear_base_payoff_ratio",
    "expected_bear_payoff_ratio",
}
_V5_CANDIDATE_FIELDS = _V5_PORTFOLIO_FIELDS | {"target_quantity"}
_V3_VALUATION_FIELDS = {
    "bear_fair_value",
    "bear_return_pct",
    "bear_probability_pct",
    "base_fair_value",
    "base_return_pct",
    "base_probability_pct",
    "bull_fair_value",
    "bull_return_pct",
    "bull_probability_pct",
    "expected_return_pct",
    "confidence_adjusted_expected_return_pct",
    "buy_below_price",
    "canonical_rating",
    "portfolio_action",
    "evidence_state",
    "rating_change_conditions",
}


def _legacy_snapshot(document: dict[str, object], version: int) -> dict[str, object]:
    legacy = json.loads(json.dumps(document))
    if version < 4:
        legacy = _legacy_v3(legacy)
    else:
        legacy["version"] = version

    target_key = "target_portfolio" if version >= 4 else "approved_target_portfolio"
    for key in ("current_portfolio", target_key):
        for row in legacy[key]["rows"]:
            for field in _V5_PORTFOLIO_FIELDS:
                row.pop(field, None)
            if version < 3:
                for field in _V3_VALUATION_FIELDS:
                    row.pop(field, None)
            if version == 1:
                for field in (
                    "mark_base",
                    "fx_as_of",
                    "security_research_page",
                    "strategy_research_page",
                ):
                    row.pop(field, None)
    for signal in legacy["actionable_signals"]:
        signal.pop("allocation_intent_id", None)
        if version == 1:
            signal.pop("security_research_page", None)
            signal.pop("strategy_research_page", None)
    for candidate in legacy["candidate_pipeline"]:
        for field in _V5_CANDIDATE_FIELDS:
            candidate.pop(field, None)
        if version < 3:
            for field in _V3_VALUATION_FIELDS | {
                "eligibility_frontier",
                "research_conclusion",
            }:
                candidate.pop(field, None)

    legacy["version"] = version
    if version < 3:
        legacy.pop("evidence_state", None)
        legacy.pop("research_benchmark", None)
    if version == 1:
        legacy["data_status"] = legacy.pop("investment_data_status")
        legacy.pop("operations_status")
        coverage = legacy["coverage"]
        coverage["current_relationship_count"] = coverage.pop("accepted_relationship_count")
        coverage["required_relationship_count"] = coverage.pop("required_relationship_review_count")
        coverage.pop("reviewed_relationship_count")
        performance = legacy["performance"]
        for field in (
            "performance_epoch_id",
            "epoch_started_at",
            "epoch_opening_equity_base",
            "prior_epoch_count",
        ):
            performance.pop(field)
    return legacy


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


@pytest.mark.parametrize(
    ("reason", "tier", "target_quantity", "expected"),
    [
        (
            "quality_score_not_above_minimum|relationship_missing_or_stale",
            "watch",
            "0",
            "allocation_constrained",
        ),
        (
            "bear_base_payoff_below_starter_minimum|relationship_missing_or_stale",
            "watch",
            "0",
            "valuation_unattractive",
        ),
        ("relationship_missing_or_stale", "watch", "0", "relationship_pending"),
        ("insufficient_diversification", "full", "3", "strategy_pending"),
    ],
)
def test_candidate_classification_reports_the_precise_primary_constraint(
    reason: str,
    tier: str,
    target_quantity: str,
    expected: str,
) -> None:
    target = {"reason": reason, "tier": tier, "target_quantity": target_quantity}
    assessment = {"research_status": "complete", "canonical_rating": "buy"}

    assert _candidate_classification(target, assessment, None) == expected


def test_candidate_classification_requires_the_strategy_to_match_the_current_intent() -> None:
    target = {
        "reason": "insufficient_diversification",
        "tier": "full",
        "target_quantity": "4",
        "allocation_intent_id": "allocation_intent_current",
    }
    assessment = {"research_status": "complete", "canonical_rating": "buy"}
    strategy = {
        "status": "ready",
        "allocation_intent_id": "allocation_intent_prior",
    }

    assert _candidate_classification(target, assessment, strategy) == "strategy_pending"


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
    _validate_snapshot_object(sandbox_repository, _legacy_v3(snapshot_document(first)))
    assert first.stance == "hold_cash"
    assert first.data_status == "current"
    assert len(first.current_portfolio.rows) == 1
    cash = first.current_portfolio.rows[0]
    assert (cash.holding_type, cash.ticker, cash.current_weight_pct) == ("cash", "CASH", "100")
    assert cash.target_weight_pct == "100"

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


@pytest.mark.parametrize("version", [1, 2, 3, 4])
def test_load_published_snapshot_preserves_v1_through_v4_compatibility(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    version: int,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id=f"legacy-v{version}")
    current = snapshot_document(
        build_decision_snapshot(
            sandbox_repository,
            sandbox_settings,
            run_id=f"legacy-v{version}",
            as_of=NOW,
        )
    )
    legacy = _legacy_snapshot(current, version)
    _validate_snapshot_object(sandbox_repository, legacy)
    published_path = sandbox_repository / "data" / "published" / "decision_snapshot.json"
    published_path.write_text(json.dumps(legacy) + "\n", encoding="utf-8")

    loaded = load_published_snapshot(sandbox_repository, expected_run_id=f"legacy-v{version}")

    assert loaded.version == version
    assert loaded.target_portfolio.portfolio_kind == "target"
    assert loaded.target_portfolio.rows[0].tier == ""
    assert loaded.target_portfolio.rows[0].allocation_intent_id == ""
    if version == 1:
        assert loaded.operations_status == "current"
        assert loaded.performance.performance_epoch_id == ""
    if version < 3:
        assert loaded.research_benchmark.policy_version == "legacy_unavailable"


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
    assert snapshot.candidate_pipeline[0].classification == "research_incomplete"
    assert snapshot.candidate_pipeline[0].reason_labels == (
        "No current comparable assessment is available.",
    )
    assert snapshot.research_alerts[0].visible_label == "Research alert — not a trade signal"
    assert snapshot.research_alerts[0].ticker == "D00"
    assert snapshot.research_alerts[0].alert_type == "bollinger_above_upper"


def test_public_snapshot_humanizes_research_alert_operation_identity(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="public-alert-fixture")
    write_table(
        sandbox_repository,
        "securities",
        [_security(research_page="data/wiki/securities/sec_00.md")],
    )
    write_table(sandbox_repository, "indicators", [_indicator()])
    operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="quick_check_research",
        entity_type="security",
        entity_id="sec_00",
        dedupe_key=build_dedupe_key(
            "quick_check_research",
            "sec_00",
            "public-alert-fixture",
            NOW.date().isoformat(),
        ),
        prompt="Review the deterministic price alert.",
        inputs={
            "security_id": "sec_00",
            "baseline_operation_id": deterministic_ulid(NOW - timedelta(days=1), "baseline"),
            "baseline_result_path": "data/runs/baseline/result.json",
            "baseline_completed_at": format_timestamp(NOW - timedelta(days=1)),
            "trigger_types": ["bollinger_above_upper"],
            "market_data_as_of": format_timestamp(NOW),
            "market_data_date": NOW.date().isoformat(),
            "period_start": (NOW - timedelta(days=20)).date().isoformat(),
            "period_end": NOW.date().isoformat(),
            "source_price_hash": "0" * 64,
        },
        source="test",
        now=NOW,
    )
    assert created
    active = read_table(sandbox_repository, "operations_todo")
    active[0]["status"] = "blocked"
    active[0]["last_error"] = f"Waiting for dependent operation {operation_id}."
    write_table(sandbox_repository, "operations_todo", active)

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="public-alert-fixture",
        as_of=NOW,
    )

    assert operation_id in snapshot.research_alerts[0].research_conclusion
    public_snapshot = _public_snapshot(sandbox_repository, snapshot)
    conclusion = public_snapshot.research_alerts[0].research_conclusion
    assert operation_id not in conclusion
    assert "Quick check research for D00" in conclusion


def test_public_snapshot_humanizes_actionable_signal_rules(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    signal_id, _, _, _ = _seed_signal(sandbox_repository, sandbox_settings, with_order=True)
    relationship_id = "relationship_0123456789abcdefabcd"
    relationship_page = f"data/wiki/relationships/{relationship_id}.md"
    (sandbox_repository / relationship_page).write_text(
        "---\ntitle: Decision relationship\ntype: relationship\nstatus: maintained\n"
        "tags:\n  - relationship\n---\n\n# Decision relationship\n",
        encoding="utf-8",
    )
    write_table(
        sandbox_repository,
        "relationships",
        [
            {
                **_relationship(),
                "relationship_id": relationship_id,
                "research_page": relationship_page,
            }
        ],
    )
    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="active-signal-fixture",
        as_of=NOW,
    )
    signal = replace(
        snapshot.actionable_signals[0],
        entry_rule=(
            "Use allocation_plan_0123456789abcdefabcd while "
            f"{signal_id} and {relationship_id} remain current."
        ),
    )

    public_snapshot = _public_snapshot(
        sandbox_repository,
        replace(snapshot, actionable_signals=(signal,)),
    )

    entry_rule = public_snapshot.actionable_signals[0].entry_rule
    assert "allocation_plan_" not in entry_rule
    assert signal_id not in entry_rule
    assert relationship_id not in entry_rule
    assert "current allocation plan" in entry_rule
    assert "Decision relationship" in entry_rule


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
    assert current.target_portfolio.cash_weight_pct == "100"

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
    assert required_decimal(snapshot.target_portfolio.cash_base, label="cash") > 0
    security = next(
        row for row in snapshot.current_portfolio.rows if row.holding_type == "security"
    )
    assert security.action == "buy"
    assert security.action_status == "pending_order"
    assert security.current_quantity == "0"
    assert security.target_quantity == "10"
    assert security.order_id == order_id
    assert sum(
        required_decimal(row.target_weight_pct, label="weight")
        for row in snapshot.target_portfolio.rows
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
    assert snapshot.target_portfolio.cash_base == "100000"
    assert snapshot.target_portfolio.cash_weight_pct == "100"
    assert all(row.holding_type == "cash" for row in snapshot.current_portfolio.rows)


def test_plan_mismatched_baseline_order_is_not_projected_or_copy_ready(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_signal(
        sandbox_repository,
        sandbox_settings,
        with_order=True,
    )
    strategies = read_table(sandbox_repository, "strategies")
    strategies[0]["sleeve"] = "baseline"
    strategies[0]["allocation_plan_id"] = "allocation_original"
    write_table(sandbox_repository, "strategies", strategies)
    write_table(
        sandbox_repository,
        "allocation_targets",
        [
            {
                **_allocation_target(reason="above_cash_hurdle"),
                "allocation_plan_id": "allocation_replacement",
                "strategy_id": "strategy_00",
                "target_weight_pct": "1",
                "target_value_base": "1000",
                "delta_value_base": "0",
                "disposition": "hold",
            }
        ],
    )

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="mismatched-baseline-plan-fixture",
        as_of=NOW,
    )

    assert snapshot.stance == "blocked"
    assert snapshot.stance_reason_codes == ("pending_order_state_unsafe",)
    assert snapshot.actionable_signals == ()
    assert snapshot.target_portfolio.cash_weight_pct == "100"
    assert all(not row.order_id for row in snapshot.current_portfolio.rows)


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
    assert snapshot.target_portfolio.cash_weight_pct == "100"


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
    assert reduced_row.target_quantity == "6"
    assert reduced_row.action == "trim"
    assert reduced.actionable_signals[0].order_id == reduce_order_id
    assert reduced.actionable_signals[0].copy_ready is True
    assert required_decimal(reduced.target_portfolio.cash_base, label="target cash") > (
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
        issue_code="action_validation_failed",
        impact="blocks_action",
        severity="error",
        title="Order validation unavailable",
        description="The deterministic order gate is unavailable for current signals.",
        entity_type="system",
        entity_id="paper_execution",
        now=NOW,
    )

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="issue-block-fixture",
        as_of=NOW,
    )
    assert snapshot.actionable_signals == ()
    assert snapshot.investment_data_status == "current"
    assert snapshot.operations_status == "blocked"
    assert any(impact.impact == "blocks_action" for impact in snapshot.system_impacts)


def test_candidate_issue_text_cannot_become_a_portfolio_blocker(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _initialize(sandbox_repository, sandbox_settings, run_id="candidate-issue-fixture")
    record_issue(
        sandbox_repository,
        issue_code="assessment_update_failed",
        impact="affects_candidate",
        severity="error",
        title="Assessment retry required",
        description=(
            "No portfolio, strategy, signal, order, execution, cash, or ledger state changed."
        ),
        entity_type="security",
        entity_id="security_fixture",
        now=NOW,
    )

    snapshot = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="candidate-issue-fixture",
        as_of=NOW,
    )

    assert snapshot.investment_data_status == "degraded"
    assert snapshot.operations_status == "current"
    assert snapshot.stance == "hold_cash"
    assert all(impact.impact != "blocks_portfolio" for impact in snapshot.system_impacts)


def test_system_status_escapes_wikilinks_embedded_in_issue_diagnostics(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    run_id = "issue-markdown-fixture"
    _initialize(sandbox_repository, sandbox_settings, run_id=run_id)
    record_issue(
        sandbox_repository,
        issue_code="research_validation_failed",
        impact="affects_candidate",
        severity="error",
        title="Research validation failed",
        description=(
            "Post-run wiki lint rejected [[concepts/missing-page]] while validating research."
        ),
        entity_type="system",
        entity_id="research",
        now=NOW,
    )

    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=NOW,
    )

    system_status = (sandbox_repository / "data" / "wiki" / "system-status.md").read_text(
        encoding="utf-8"
    )
    assert r"\[\[concepts/missing-page\]\]" in system_status
    assert lint_wiki(sandbox_repository / "data" / "wiki") == []


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
    assert current.candidate_pipeline[0].classification == "strategy_ready"
    assert current.coverage.reviewed_relationship_count == 1
    assert current.coverage.accepted_relationship_count == 1

    stale = build_decision_snapshot(
        sandbox_repository,
        sandbox_settings,
        run_id="candidate-later-fixture",
        as_of=NOW,
    )
    assert stale.candidate_pipeline[0].classification == "research_incomplete"
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
    assert missing_relationship.coverage.reviewed_relationship_count == 0
    assert missing_relationship.coverage.accepted_relationship_count == 0


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


def test_interrupted_open_cycle_can_replace_snapshot_until_finalization(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    run_id = "daily-20260724T120000Z"
    _initialize(sandbox_repository, sandbox_settings, run_id=run_id)
    run_directory = sandbox_repository / "data" / "runs" / run_id
    run_directory.mkdir(parents=True)
    manifest_path = run_directory / "daily_run.json"
    manifest = {
        "daily_run_version": 2,
        "daily_cycle_id": run_id,
        "status": "running",
        "finalization_at": "",
        "completion_at": "",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    first = refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=NOW,
        render_pages=False,
    )
    record_issue(
        sandbox_repository,
        issue_code="daily_finalization_interrupted",
        impact="operational_only",
        severity="error",
        title="Interrupted finalization fixture",
        description="The open cycle must refresh its incomplete snapshot.",
        entity_type="daily_run",
        entity_id=run_id,
        owner="controller",
        related_run_id=run_id,
        now=NOW,
    )

    replaced = refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=NOW,
        render_pages=False,
    )

    assert replaced.snapshot_id != first.snapshot_id
    assert (
        json.loads((run_directory / "decision_snapshot.json").read_text(encoding="utf-8"))[
            "snapshot_id"
        ]
        == replaced.snapshot_id
    )
    manifest["finalization_at"] = "2026-07-24T12:00:00Z"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    record_issue(
        sandbox_repository,
        issue_code="daily_finalization_completed_fixture",
        impact="operational_only",
        severity="error",
        title="Completed finalization fixture",
        description="A finalized cycle must retain its immutable snapshot.",
        entity_type="daily_run",
        entity_id=run_id,
        owner="controller",
        related_run_id=run_id,
        now=NOW + timedelta(minutes=1),
    )

    with pytest.raises(AdviceError, match="immutable decision snapshot conflicts"):
        refresh_advice(
            sandbox_repository,
            sandbox_settings,
            run_id=run_id,
            as_of=NOW,
            render_pages=False,
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
        issue_code="telegram_report_delivery_failed",
        impact="publication_only",
        severity="warning",
        title="Telegram delivery failed: prior",
        description="A prior committed investor brief awaits retry.",
        entity_type="delivery",
        entity_id="daily_report",
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
        issue_code="telegram_report_delivery_failed",
        impact="publication_only",
        severity="warning",
        title="Telegram delivery failed: deadbeef",
        description="The committed investor brief could not be delivered.",
        entity_type="delivery",
        entity_id="daily_report",
        owner="delivery",
        related_run_id="delivery-fixture",
        now=NOW + timedelta(minutes=1),
    )

    assert validate_advice(sandbox_repository, strict=True) == []
    assert len(snapshot.system_impacts) == 1


def test_post_publication_reopened_delivery_issue_does_not_stale_decision_snapshot(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    run_id = "reopened-delivery-fixture"
    _initialize(sandbox_repository, sandbox_settings, run_id=run_id)
    issue_id = record_issue(
        sandbox_repository,
        issue_code="telegram_podcast_audio_delivery_failed",
        impact="publication_only",
        severity="warning",
        title="Telegram podcast audio delivery unavailable",
        description="A prior podcast audio delivery failed.",
        entity_type="delivery",
        entity_id="podcast_audio",
        owner="delivery",
        related_run_id="prior-delivery-fixture",
        now=NOW - timedelta(minutes=2),
    )
    resolve_issue(
        sandbox_repository,
        issue_id,
        "The prior podcast audio was delivered.",
        now=NOW - timedelta(minutes=1),
    )
    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=NOW,
        render_pages=False,
    )

    reopened_id = record_issue(
        sandbox_repository,
        issue_code="telegram_podcast_audio_delivery_failed",
        impact="publication_only",
        severity="warning",
        title="Telegram podcast audio delivery unavailable",
        description="The current podcast audio draft was unavailable.",
        entity_type="delivery",
        entity_id="podcast_audio",
        owner="delivery",
        related_run_id=run_id,
        now=NOW + timedelta(minutes=1),
    )

    assert reopened_id == issue_id
    assert validate_advice(sandbox_repository, strict=True) == []


def test_legacy_post_publication_podcast_bookkeeping_does_not_stale_snapshot(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    run_id = "legacy-podcast-fixture"
    _initialize(sandbox_repository, sandbox_settings, run_id=run_id)
    operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec_legacy_queue",
        dedupe_key=build_dedupe_key(
            "security_research",
            "sec_legacy_queue",
            "legacy-queue",
            NOW.date().isoformat(),
        ),
        prompt="Research the legacy queue fixture.",
        inputs={"security_id": "sec_legacy_queue"},
        source="test",
        now=NOW,
    )
    assert created
    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=NOW,
        render_pages=False,
    )

    active = read_table(sandbox_repository, "operations_todo")
    assert len(active) == 1
    active[0]["updated_at"] = format_timestamp(NOW + timedelta(minutes=5))
    write_table(sandbox_repository, "operations_todo", active)

    podcast_operation_id = deterministic_ulid(
        NOW + timedelta(minutes=5), "legacy-podcast-bookkeeping"
    )
    podcast_time = format_timestamp(NOW + timedelta(minutes=5))
    podcast_history = {
        **active[0],
        "operation_id": podcast_operation_id,
        "created_at": podcast_time,
        "updated_at": podcast_time,
        "status": "running",
        "priority": "100",
        "operation_type": "daily_podcast",
        "entity_type": "run",
        "entity_id": run_id,
        "dedupe_key": f"daily_podcast:{run_id}:text-v2",
        "skill_names": "llm-wiki|papertrader-daily-podcast",
        "prompt": "Create the completed run's daily podcast.",
        "source": "test",
        "attempt_count": "1",
        "max_attempts": "1",
        "claimed_by_run_id": run_id,
        "last_error": "agent_validation_failed:fixture",
        "terminal_status": "failed",
        "completed_at": podcast_time,
        "result_path": "",
        "result_summary": "",
        "terminal_reason": "agent_validation_failed:fixture",
    }
    append_unique(
        sandbox_repository,
        "operations_history",
        [podcast_history],
        key_columns=("operation_id",),
    )
    record_issue(
        sandbox_repository,
        issue_code="agent_result_validation_failed",
        impact="publication_only",
        severity="error",
        title=f"Hermes operation validation failed: {podcast_operation_id}",
        description="Legacy controller classification for a contained podcast failure.",
        entity_type="operation",
        entity_id=podcast_operation_id,
        owner="controller",
        related_run_id=run_id,
        related_operation_id=podcast_operation_id,
        now=NOW + timedelta(minutes=5),
    )

    assert operation_id == active[0]["operation_id"]
    assert validate_advice(sandbox_repository, strict=True) == []

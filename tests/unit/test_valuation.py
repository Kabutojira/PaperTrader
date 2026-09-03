from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.allocation import baseline_strategy_id, plan_allocation, write_calibration_report
from papertrader.config import Settings
from papertrader.execution import ensure_initial_capital
from papertrader.queue import (
    RunBudget,
    claim_next,
    complete_operation,
    enqueue_operation,
    prepare_queue,
    validate_queue,
)
from papertrader.ratings import canonical_rating
from papertrader.research import ResearchStateError, upsert_assessment, upsert_strategy
from papertrader.tables import read_table, write_table
from papertrader.valuation import (
    ValuationError,
    live_valuation_projection,
    validate_research_rubrics,
    valuation_templates,
)

NOW = datetime(2026, 7, 24, 22, tzinfo=UTC)
TEMPLATES = {
    "mature_compounder": "dcf",
    "cyclical_commodity": "normalized_earnings",
    "financial_company": "excess_return",
    "pre_profit_growth": "probability_weighted_dcf",
    "biotechnology_binary": "risk_adjusted_npv",
    "private_illiquid": "nav",
    "other": "other",
}


def _security() -> dict[str, str]:
    return {
        "security_id": "sec_valuation",
        "issuer_id": "issuer_valuation",
        "company_name": "Valuation Corp",
        "instrument_name": "Valuation Corp common stock",
        "instrument_type": "equity",
        "ticker": "VAL",
        "exchange_code": "XETR",
        "venue_mic": "XETR",
        "provider_symbol": "VAL.DE",
        "broker_symbol": "",
        "currency": "EUR",
        "country": "DE",
        "sector": "Industrials",
        "industry": "Testing",
        "status": "watching",
        "watchlist_reason": "Valuation fixture.",
        "research_summary": "Valuation fixture.",
        "research_page": "data/wiki/securities/sec_valuation.md",
        "last_research_at": "2026-07-24T21:00:00Z",
        "next_review_at": "2026-08-23T21:00:00Z",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-24T21:00:00Z",
        "source": "fixture",
    }


def _source() -> dict[str, str]:
    return {
        "source_id": "source_valuation",
        "url": "https://example.test/valuation",
        "canonical_url": "https://example.test/valuation",
        "source_type": "filing",
        "title": "Valuation filing",
        "publisher": "Valuation Corp",
        "license": "public-record",
        "status": "available",
        "content_hash": "cd" * 32,
        "first_seen_at": "2026-07-24T20:00:00Z",
        "last_checked_at": "2026-07-24T21:30:00Z",
        "last_changed_at": "2026-07-24T21:30:00Z",
        "related_entity_ids": "sec_valuation",
    }


def _market() -> dict[str, str]:
    return {
        "security_id": "sec_valuation",
        "provider_symbol": "VAL.DE",
        "price_date": "2026-07-24",
        "retrieved_at": "2026-07-24T22:00:00Z",
        "open": "99",
        "high": "101",
        "low": "98",
        "close": "100",
        "adjusted_close": "100",
        "volume": "1000000",
        "currency": "EUR",
        "source": "fixture",
        "status": "ok",
        "error": "",
    }


def _request(template: str, method: str) -> dict[str, str]:
    return {
        "assessment_schema_version": "2",
        "security_id": "sec_valuation",
        "assessed_at": "2026-07-24T22:00:00Z",
        "expires_at": "2026-08-23T22:00:00Z",
        "confidence": "medium",
        "thesis_score": "80",
        "business_quality_score": "80",
        "balance_sheet_score": "60",
        "valuation_score": "80",
        "timing_score": "60",
        "liquidity_score": "80",
        "risk_penalty": "40",
        "valuation_method": method,
        "valuation_template": template,
        "valuation_template_rationale": "No specialized template fits."
        if template == "other"
        else "",
        "reference_price": "100",
        "reference_currency": "EUR",
        "market_data_as_of": "2026-07-24T22:00:00Z",
        "fx_rate_to_base": "1",
        "fx_as_of": "2026-07-24T22:00:00Z",
        "valuation_horizon_months": "12",
        "valuation_supported": "true",
        "bear_fair_value": "80",
        "bear_probability_pct": "25",
        "bear_assumptions": "Lower growth and margins.",
        "base_fair_value": "120",
        "base_probability_pct": "50",
        "base_assumptions": "Normalized growth and margins.",
        "bull_fair_value": "160",
        "bull_probability_pct": "25",
        "bull_assumptions": "Higher growth and margins.",
        "research_completeness": "complete",
        "rating_change_conditions": (
            "Reassess if growth, margins, or balance-sheet evidence changes."
        ),
        "hard_blockers": "",
        "soft_gaps": "confidence_medium",
        "evidence_refs": "source_valuation",
        "run_id": "valuation-run",
    }


def _seed(repository: Path) -> None:
    page = repository / "data/wiki/securities/sec_valuation.md"
    page.write_text("# Valuation\n", encoding="utf-8")
    write_table(repository, "securities", [_security()])
    write_table(repository, "source_registry", [_source()])
    write_table(repository, "market_latest", [_market()])
    write_table(
        repository,
        "relationships",
        [
            {
                "relationship_id": "relationship_valuation",
                "idea_id": "idea_valuation",
                "security_id": "sec_valuation",
                "relationship_type": "beneficiary",
                "direction": "positive",
                "mechanism": "The fixture benefits from its validated mechanism.",
                "sensitivity": "medium",
                "confidence": "high",
                "catalyst": "Evidence converts into cash flow.",
                "invalidation": "The mechanism fails.",
                "status": "accepted",
                "research_page": "",
                "last_reviewed_at": "2026-07-24T21:00:00Z",
                "next_review_at": "2026-08-24T21:00:00Z",
                "created_at": "2026-07-24T21:00:00Z",
                "updated_at": "2026-07-24T21:00:00Z",
            }
        ],
    )


def _live_projection(
    repository: Path,
    settings: Settings,
    *,
    assessment_changes: dict[str, str] | None = None,
    relationship_accepted: bool = True,
    evidence_fresh: bool = True,
) -> dict[str, str]:
    assert upsert_assessment(
        repository,
        settings,
        _request("mature_compounder", "dcf"),
        now=NOW,
    )
    assessment = read_table(repository, "security_assessments")[0]
    if assessment_changes:
        assessment = assessment | assessment_changes
    return live_valuation_projection(
        repository,
        settings,
        _security(),
        assessment,
        now=NOW,
        relationship_accepted=relationship_accepted,
        evidence_fresh=evidence_fresh,
    )


def test_live_projection_uses_adjusted_mark_and_exact_full_boundaries(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)

    projection = _live_projection(sandbox_repository, sandbox_settings)

    assert projection["valuation_mark"] == "100"
    assert projection["bear_return_pct"] == "-20"
    assert projection["base_return_pct"] == "20"
    assert projection["bull_return_pct"] == "60"
    assert projection["expected_return_pct"] == "20"
    assert projection["confidence_adjusted_expected_return_pct"] == "15"
    assert projection["margin_of_safety_pct"] == "16.66666666666666666666666667"
    assert projection["bear_base_payoff_ratio"] == "1"
    assert projection["expected_bear_payoff_ratio"] == "0.75"
    assert projection["tier"] == "full"
    assert projection["position_cap_pct"] == "5"


def test_live_projection_accepts_exact_starter_payoff_boundaries(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)

    projection = _live_projection(
        sandbox_repository,
        sandbox_settings,
        assessment_changes={
            "confidence": "high",
            "bear_fair_value": "75",
            "base_fair_value": "112.5",
            "bull_fair_value": "140",
        },
    )

    assert projection["bear_base_payoff_ratio"] == "0.5"
    assert projection["expected_bear_payoff_ratio"] == "0.4"
    assert projection["confidence_adjusted_expected_return_pct"] == "10"
    assert projection["tier"] == "starter"
    assert projection["position_cap_pct"] == "2"


def test_repricing_to_watch_cancels_pending_only_exposure_without_close_research(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)
    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        _request("mature_compounder", "dcf"),
        now=NOW,
    )
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id="valuation-allocation-seed",
        occurred_at=NOW,
    )
    active = replace(
        sandbox_settings,
        allocation=replace(
            sandbox_settings.allocation,
            mode="active",
            minimum_diversified_candidates=1,
        ),
    )
    initial = plan_allocation(
        sandbox_repository,
        active,
        run_id="valuation-allocation-initial",
        now=NOW,
    )
    target = read_table(sandbox_repository, "allocation_targets")[0]
    assert target["tier"] == "full"
    assert Decimal(target["target_quantity"]) > 0
    strategy_id = baseline_strategy_id("sec_valuation")
    strategy_page = sandbox_repository / "data" / "wiki" / "strategies" / f"{strategy_id}.md"
    strategy_page.write_text("# Valuation baseline strategy\n", encoding="utf-8")
    assert upsert_strategy(
        sandbox_repository,
        active,
        {
            "strategy": {
                "strategy_id": strategy_id,
                "idea_id": "idea_valuation",
                "security_id": "sec_valuation",
                "relationship_id": "relationship_valuation",
                "name": "Valuation baseline strategy",
                "status": "ready",
                "direction": "long",
                "instrument_type": "equity",
                "thesis": "The validated valuation supports bounded paper exposure.",
                "entry_rule": "Follow the deterministic allocation target.",
                "exit_rule": "Close when the live target falls to zero.",
                "invalidation": "A failed live allocation gate invalidates exposure.",
                "risk_budget_pct": target["position_cap_pct"],
                "sleeve": "baseline",
                "allocation_plan_id": initial.allocation_plan_id,
                "allocation_intent_id": target["allocation_intent_id"],
                "not_before": "",
                "expires_at": "",
                "research_page": f"data/wiki/strategies/{strategy_id}.md",
            },
            "legs": [
                {
                    "leg_id": "leg_valuation",
                    "action": "buy",
                    "side": "long",
                    "instrument_type": "equity",
                    "security_id": "sec_valuation",
                    "provider_contract_id": "",
                    "option_type": "",
                    "expiry": "",
                    "strike": "",
                    "quantity": target["target_quantity"],
                    "contract_multiplier": "1",
                    "order_type": "market",
                    "limit_price": "",
                    "currency": "EUR",
                }
            ],
        },
        now=NOW,
    )
    write_table(
        sandbox_repository,
        "signals",
        [
            {
                "signal_id": "signal_valuation_pending",
                "strategy_id": strategy_id,
                "allocation_intent_id": target["allocation_intent_id"],
                "signal_type": "open",
                "created_at": "2026-07-24T22:00:00Z",
                "expires_at": "2026-07-25T22:00:00Z",
                "status": "ordered",
                "rationale": "Exercise pending-order cancellation after live repricing.",
                "market_data_as_of": "2026-07-24T22:00:00Z",
                "order_request_path": "",
                "telegram_sent_at": "",
                "run_id": "valuation-allocation-initial",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "orders",
        [
            {
                "order_id": "order_valuation_pending",
                "signal_id": "signal_valuation_pending",
                "strategy_id": strategy_id,
                "allocation_intent_id": target["allocation_intent_id"],
                "created_at": "2026-07-24T22:00:00Z",
                "status": "pending",
                "fill_policy": "next_open",
                "not_before": "2026-07-24T22:00:00Z",
                "expires_at": "2026-07-25T22:00:00Z",
                "order_type": "market",
                "limit_price": "",
                "slippage_bps": "5",
                "fee_model": "fixed_plus_bps",
                "currency": "EUR",
                "run_id": "valuation-allocation-initial",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "order_legs",
        [
            {
                "order_id": "order_valuation_pending",
                "leg_id": "leg_valuation",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": "sec_valuation",
                "provider_contract_id": "",
                "option_type": "",
                "expiry": "",
                "strike": "",
                "quantity": target["target_quantity"],
                "contract_multiplier": "1",
                "limit_price": "",
                "currency": "EUR",
            }
        ],
    )
    repriced_market = _market() | {
        "open": "129",
        "high": "131",
        "low": "128",
        "close": "130",
        "adjusted_close": "130",
        "retrieved_at": "2026-07-24T22:01:00Z",
    }
    write_table(sandbox_repository, "market_latest", [repriced_market])

    plan_allocation(
        sandbox_repository,
        active,
        run_id="valuation-allocation-repriced",
        now=NOW.replace(minute=1),
    )
    prepare_queue(sandbox_repository, now=NOW.replace(minute=2))

    repriced_target = read_table(sandbox_repository, "allocation_targets")[0]
    assert repriced_target["tier"] == "watch"
    assert repriced_target["target_quantity"] == "0"
    assert repriced_target["disposition"] == "close"
    assert read_table(sandbox_repository, "signals")[0]["status"] == "cancelled"
    assert read_table(sandbox_repository, "orders")[0]["status"] == "cancelled"
    assert not any(
        row["entity_id"] == strategy_id for row in read_table(sandbox_repository, "operations_todo")
    )
    assert validate_queue(sandbox_repository) == []


def test_live_projection_accepts_inclusive_negative_35_bear_boundary(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)

    projection = _live_projection(
        sandbox_repository,
        sandbox_settings,
        assessment_changes={
            "confidence": "high",
            "bear_fair_value": "65",
            "base_fair_value": "117.5",
            "bull_fair_value": "156",
        },
    )

    assert projection["bear_return_pct"] == "-35"
    assert projection["bear_base_payoff_ratio"] == "0.5"
    assert projection["expected_bear_payoff_ratio"] == "0.4"
    assert projection["tier"] == "starter"


def test_live_projection_quality_must_be_strictly_above_60(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)

    projection = _live_projection(
        sandbox_repository,
        sandbox_settings,
        assessment_changes={
            "thesis_score": "60",
            "business_quality_score": "60",
            "balance_sheet_score": "60",
            "liquidity_score": "60",
        },
    )

    assert projection["quality_score"] == "60"
    assert projection["tier"] == "watch"
    assert "quality_score_not_above_minimum" in projection["eligibility_reason_codes"]


def test_live_projection_zero_bear_loss_has_unbounded_payoff_ratios(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)

    projection = _live_projection(
        sandbox_repository,
        sandbox_settings,
        assessment_changes={"bear_fair_value": "100", "bull_fair_value": "140"},
    )

    assert projection["bear_return_pct"] == "0"
    assert projection["bear_base_payoff_ratio"] == "999999"
    assert projection["expected_bear_payoff_ratio"] == "999999"
    assert projection["tier"] == "full"


def test_live_projection_reprices_both_directions_without_mutating_assessment(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)
    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        _request("mature_compounder", "dcf"),
        now=NOW,
    )
    frozen = read_table(sandbox_repository, "security_assessments")[0]
    market = _market()
    market["adjusted_close"] = "80"
    write_table(sandbox_repository, "market_latest", [market])
    lower = live_valuation_projection(
        sandbox_repository,
        sandbox_settings,
        _security(),
        frozen,
        now=NOW,
        relationship_accepted=True,
        evidence_fresh=True,
    )
    market["adjusted_close"] = "110"
    write_table(sandbox_repository, "market_latest", [market])
    higher = live_valuation_projection(
        sandbox_repository,
        sandbox_settings,
        _security(),
        frozen,
        now=NOW,
        relationship_accepted=True,
        evidence_fresh=True,
    )

    assert Decimal(lower["base_return_pct"]) > Decimal(frozen["base_return_pct"])
    assert Decimal(higher["base_return_pct"]) < Decimal(frozen["base_return_pct"])
    assert higher["tier"] == "watch"
    assert read_table(sandbox_repository, "security_assessments")[0] == frozen


def test_live_projection_falls_back_to_close_when_adjusted_close_is_missing(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)
    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        _request("mature_compounder", "dcf"),
        now=NOW,
    )
    market = _market() | {"adjusted_close": "", "close": "90"}
    write_table(sandbox_repository, "market_latest", [market])

    projection = live_valuation_projection(
        sandbox_repository,
        sandbox_settings,
        _security(),
        read_table(sandbox_repository, "security_assessments")[0],
        now=NOW,
        relationship_accepted=True,
        evidence_fresh=True,
    )

    assert projection["valuation_mark"] == "90"


@pytest.mark.parametrize(
    ("market_changes", "message"),
    [
        ({"retrieved_at": "2026-07-23T08:00:00Z"}, "market_data_stale"),
        ({"retrieved_at": "2026-07-24T22:00:01Z"}, "market_data_stale"),
        ({"provider_symbol": "WRONG.DE"}, "market_data_identity_mismatch"),
        ({"currency": "USD"}, "market_data_identity_mismatch"),
    ],
)
def test_live_projection_fails_closed_for_invalid_marks(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    market_changes: dict[str, str],
    message: str,
) -> None:
    _seed(sandbox_repository)
    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        _request("mature_compounder", "dcf"),
        now=NOW,
    )
    write_table(sandbox_repository, "market_latest", [_market() | market_changes])

    with pytest.raises(ValuationError, match=message):
        live_valuation_projection(
            sandbox_repository,
            sandbox_settings,
            _security(),
            read_table(sandbox_repository, "security_assessments")[0],
            now=NOW,
            relationship_accepted=True,
            evidence_fresh=True,
        )


@pytest.mark.parametrize(
    ("assessment_changes", "evidence_fresh", "reason"),
    [
        (
            {
                "assessed_at": "2026-06-01T00:00:00Z",
                "expires_at": "2026-08-23T22:00:00Z",
            },
            True,
            "assessment_stale",
        ),
        ({}, False, "assessment_evidence_stale"),
    ],
)
def test_live_projection_does_not_refresh_stale_research(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    assessment_changes: dict[str, str],
    evidence_fresh: bool,
    reason: str,
) -> None:
    _seed(sandbox_repository)
    settings = replace(
        sandbox_settings,
        allocation=replace(sandbox_settings.allocation, maximum_assessment_age_days=30),
    )

    projection = _live_projection(
        sandbox_repository,
        settings,
        assessment_changes=assessment_changes,
        evidence_fresh=evidence_fresh,
    )

    assert projection["tier"] == "watch"
    assert reason in projection["eligibility_reason_codes"]


@pytest.mark.parametrize(
    (
        "ticker",
        "mark",
        "fair_values",
        "probabilities",
        "scores",
        "assessed_at",
        "expires_at",
        "relationship_accepted",
        "expected_tier",
        "expected_rating",
        "expected_reason",
    ),
    [
        (
            "PRX",
            "36.85499954223633",
            ("30", "52", "70"),
            ("30", "50", "20"),
            ("80", "60", "60", "80"),
            "2026-08-28T19:18:00Z",
            "2026-09-27T19:18:00Z",
            True,
            "full",
            "buy",
            "",
        ),
        (
            "UBER",
            "76.44999694824219",
            ("55", "90", "120"),
            ("25", "50", "25"),
            ("80", "80", "80", "100"),
            "2026-08-28T19:27:50Z",
            "2026-09-27T19:27:50Z",
            True,
            "starter",
            "buy",
            "",
        ),
        (
            "TCEHY",
            "56.09000015258789",
            ("40", "65", "90"),
            ("25", "50", "25"),
            ("80", "80", "80", "60"),
            "2026-08-28T19:23:20Z",
            "2026-09-27T19:23:20Z",
            True,
            "starter",
            "buy",
            "",
        ),
        (
            "NVDA",
            "224.41000366210938",
            ("180", "252", "374"),
            ("25", "50", "25"),
            ("80", "100", "100", "100"),
            "2026-08-07T09:23:01Z",
            "2026-08-19T18:27:18Z",
            True,
            "watch",
            "buy",
            "assessment_stale",
        ),
        (
            "CROX",
            "115.79000091552734",
            ("88", "145.425", "205.8"),
            ("30", "50", "20"),
            ("60", "60", "60", "100"),
            "2026-09-03T12:48:08Z",
            "2026-10-03T12:48:08Z",
            False,
            "watch",
            "buy",
            "relationship_missing_or_stale",
        ),
        (
            "CSIQ",
            "13.359999656677246",
            ("10.16", "18.28", "26.41"),
            ("35", "50", "15"),
            ("60", "40", "40", "80"),
            "2026-08-31T08:45:47Z",
            "2026-09-30T08:45:47Z",
            False,
            "watch",
            "buy",
            "quality_score_not_above_minimum",
        ),
        (
            "NOMD",
            "11.59000015258789",
            ("9", "15", "20"),
            ("30", "50", "20"),
            ("40", "40", "40", "80"),
            "2026-08-28T19:32:10Z",
            "2026-09-27T19:32:10Z",
            False,
            "watch",
            "buy",
            "quality_score_not_above_minimum",
        ),
        (
            "FISV",
            "51.97999954223633",
            ("35", "65", "95"),
            ("30", "50", "20"),
            ("40", "60", "40", "100"),
            "2026-08-28T19:25:00Z",
            "2026-09-27T19:25:00Z",
            False,
            "watch",
            "buy",
            "quality_score_not_above_minimum",
        ),
        (
            "DPZ",
            "346.67999267578125",
            ("270", "380", "500"),
            ("25", "50", "25"),
            ("60", "80", "40", "100"),
            "2026-08-28T19:34:25Z",
            "2026-09-27T19:34:25Z",
            True,
            "watch",
            "hold",
            "base_return_below_minimum",
        ),
        (
            "MELI",
            "2006.5799560546875",
            ("1400", "2200", "3000"),
            ("25", "50", "25"),
            ("80", "80", "60", "100"),
            "2026-08-28T20:09:00Z",
            "2026-09-27T20:09:00Z",
            True,
            "watch",
            "hold",
            "base_return_below_minimum",
        ),
    ],
)
def test_supplied_september_3_live_valuation_regression(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    ticker: str,
    mark: str,
    fair_values: tuple[str, str, str],
    probabilities: tuple[str, str, str],
    scores: tuple[str, str, str, str],
    assessed_at: str,
    expires_at: str,
    relationship_accepted: bool,
    expected_tier: str,
    expected_rating: str,
    expected_reason: str,
) -> None:
    _seed(sandbox_repository)
    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        _request("mature_compounder", "dcf"),
        now=NOW,
    )
    assessment = read_table(sandbox_repository, "security_assessments")[0] | {
        "assessed_at": assessed_at,
        "expires_at": expires_at,
        "thesis_score": scores[0],
        "business_quality_score": scores[1],
        "balance_sheet_score": scores[2],
        "liquidity_score": scores[3],
        "bear_fair_value": fair_values[0],
        "bear_probability_pct": probabilities[0],
        "base_fair_value": fair_values[1],
        "base_probability_pct": probabilities[1],
        "bull_fair_value": fair_values[2],
        "bull_probability_pct": probabilities[2],
    }
    as_of = datetime(2026, 9, 3, 13, 3, tzinfo=UTC)
    write_table(
        sandbox_repository,
        "market_latest",
        [
            _market()
            | {
                "adjusted_close": mark,
                "close": mark,
                "price_date": "2026-09-02",
                "retrieved_at": "2026-09-03T12:29:04Z",
            }
        ],
    )

    projection = live_valuation_projection(
        sandbox_repository,
        sandbox_settings,
        _security(),
        assessment,
        now=as_of,
        relationship_accepted=relationship_accepted,
        evidence_fresh=True,
    )
    rating = canonical_rating(assessment | projection, sandbox_settings)

    assert projection["tier"] == expected_tier, ticker
    assert rating == expected_rating, ticker
    assert expected_reason in projection["eligibility_reason_codes"], ticker


@pytest.mark.parametrize(("template", "method"), sorted(TEMPLATES.items()))
def test_every_valuation_template_produces_reconciled_scenarios(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    template: str,
    method: str,
) -> None:
    _seed(sandbox_repository)
    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        _request(template, method),
        now=NOW,
    )
    row = read_table(sandbox_repository, "security_assessments")[0]
    assert row["assessment_schema_version"] == "2"
    assert row["bear_return_pct"] == "-20"
    assert row["base_return_pct"] == "20"
    assert row["bull_return_pct"] == "60"
    assert row["probability_weighted_fair_value"] == "120"
    assert row["expected_return_pct"] == "20"
    assert row["confidence_adjusted_expected_return_pct"] == "15"
    assert row["buy_below_price"] == "96"
    assert row["margin_of_safety_pct"] == "16.66666666666666666666666667"
    assert row["research_status"] == "complete"
    assert row["allocation_eligibility"] == "eligible"
    assert row["conviction_tier"] == "baseline"
    assert row["eligibility_reason_codes"] == ""
    assert row["canonical_rating"] == "buy"
    assert row["portfolio_action"] == "initiate"
    assert row["research_conclusion"].startswith("Rating: Buy. Portfolio action: Initiate.")


def test_named_template_canonicalizes_omitted_rationale_to_empty(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)
    request = _request("mature_compounder", "dcf")
    request.pop("valuation_template_rationale")

    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        request,
        now=NOW,
    )
    row = read_table(sandbox_repository, "security_assessments")[0]
    assert row["valuation_template"] == "mature_compounder"
    assert row["valuation_template_rationale"] == ""


def test_v2_assessment_requires_exact_provenance_when_run_has_two_reviews(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)
    budget = RunBudget(maximum_operations=2, maximum_cost=Decimal("1"))
    first_id, _ = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec_valuation",
        dedupe_key="security_research:sec_valuation:first-review:2026-07-24",
        prompt="Complete the first valuation review.",
        inputs={"security_id": "sec_valuation"},
        source="fixture",
        now=NOW,
    )
    prepare_queue(sandbox_repository, now=NOW)
    first = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="valuation-run",
        budget=budget,
        operation_id=first_id,
        now=NOW,
    )
    assert first is not None
    complete_operation(
        sandbox_repository,
        operation_id=first_id,
        run_id="valuation-run",
        terminal_status="succeeded",
        result_path=f"data/runs/valuation-run/{first_id}/agent_result.json",
        result_summary="First review completed.",
        terminal_reason="completed",
        now=NOW,
    )
    second_id, _ = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec_valuation",
        dedupe_key="security_research:sec_valuation:second-review:2026-07-24",
        prompt="Complete the second valuation review.",
        inputs={"security_id": "sec_valuation"},
        source="fixture",
        now=NOW,
    )
    prepare_queue(sandbox_repository, now=NOW)
    second = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id="valuation-run",
        budget=budget,
        operation_id=second_id,
        now=NOW,
    )
    assert second is not None

    with pytest.raises(ResearchStateError, match="source operation is ambiguous"):
        upsert_assessment(
            sandbox_repository,
            sandbox_settings,
            _request("mature_compounder", "dcf"),
            now=NOW,
        )

    assert upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        _request("mature_compounder", "dcf") | {"source_operation_id": second_id},
        now=NOW,
    )
    history = read_table(sandbox_repository, "security_assessment_history")
    assert history[-1]["source_operation_id"] == second_id


def test_other_template_still_requires_explicit_rationale_field(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed(sandbox_repository)
    request = _request("other", "other")
    request.pop("valuation_template_rationale")

    with pytest.raises(ResearchStateError, match="valuation_template_rationale"):
        upsert_assessment(
            sandbox_repository,
            sandbox_settings,
            request,
            now=NOW,
        )


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"bear_probability_pct": "20"}, "sum exactly to 100"),
        ({"bear_fair_value": "130"}, "bear <= base <= bull"),
        ({"valuation_template": "unknown"}, "unknown valuation_template"),
        ({"reference_price": "101"}, "does not match the current mark"),
        ({"thesis_score": "70"}, "anchored 20/40/60/80/100"),
    ],
)
def test_v2_rejects_inconsistent_or_unanchored_inputs(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    changes: dict[str, str],
    message: str,
) -> None:
    _seed(sandbox_repository)
    with pytest.raises(ResearchStateError, match=message):
        upsert_assessment(
            sandbox_repository,
            sandbox_settings,
            _request("mature_compounder", "dcf") | changes,
            now=NOW,
        )


def test_unsupported_valuation_stores_no_invented_scenarios(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed(sandbox_repository)
    request = _request("mature_compounder", "dcf")
    for field in (
        "bear_fair_value",
        "bear_probability_pct",
        "bear_assumptions",
        "base_fair_value",
        "base_probability_pct",
        "base_assumptions",
        "bull_fair_value",
        "bull_probability_pct",
        "bull_assumptions",
    ):
        request[field] = ""
    request.update(
        {
            "valuation_supported": "false",
            "research_completeness": "unsupported",
            "hard_blockers": "valuation_unsupported",
        }
    )
    assert upsert_assessment(sandbox_repository, sandbox_settings, request, now=NOW)
    row = read_table(sandbox_repository, "security_assessments")[0]
    assert row["bear_fair_value"] == row["expected_return_pct"] == ""
    assert row["valuation_supported"] == "false"
    assert row["canonical_rating"] == "unrated"
    assert row["portfolio_action"] == "watch"


def test_repository_valuation_contracts_are_complete(repository_root: Path) -> None:
    assert set(valuation_templates(repository_root)) == set(TEMPLATES)
    assert validate_research_rubrics(repository_root) == []


def test_calibration_frontier_separates_attractive_and_blocked_cases(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    path = write_calibration_report(
        sandbox_repository,
        sandbox_settings,
        run_id="calibration-fixture",
    )
    document = json.loads(path.read_text(encoding="utf-8"))
    fixtures = document["fixtures"]
    assert fixtures["clearly_attractive"]["allocation_eligibility"] == "eligible"
    assert fixtures["fair"]["allocation_eligibility"] == "ineligible"
    assert "expected_return_below_minimum" in fixtures["fair"]["eligibility_reason_codes"]
    assert "hard_blocker:solvency_risk" in fixtures["distressed"]["eligibility_reason_codes"]
    assert "hard_blocker:liquidity_insufficient" in fixtures["illiquid"]["eligibility_reason_codes"]
    assert fixtures["incomplete"]["research_status"] == "unsupported"
    assert int(fixtures["clearly_attractive"]["frontier_confidence_levels"]) >= 0

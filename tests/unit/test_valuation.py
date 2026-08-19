from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.allocation import write_calibration_report
from papertrader.config import Settings
from papertrader.research import ResearchStateError, upsert_assessment
from papertrader.tables import read_table, write_table
from papertrader.valuation import validate_research_rubrics, valuation_templates

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

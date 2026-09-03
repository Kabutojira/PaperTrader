"""Scenario-complete, Decimal-safe valuation normalization and anchored rubrics."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import yaml

from papertrader.config import Settings
from papertrader.market_data import MarketDataError, latest_fx_rate_record
from papertrader.tables import read_table
from papertrader.utils import (
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    required_decimal,
)

ASSESSMENT_V2_AGENT_FIELDS = (
    "assessment_schema_version",
    "security_id",
    "assessed_at",
    "expires_at",
    "confidence",
    "thesis_score",
    "business_quality_score",
    "balance_sheet_score",
    "valuation_score",
    "timing_score",
    "liquidity_score",
    "risk_penalty",
    "valuation_method",
    "valuation_template",
    "valuation_template_rationale",
    "reference_price",
    "reference_currency",
    "market_data_as_of",
    "fx_rate_to_base",
    "fx_as_of",
    "valuation_horizon_months",
    "valuation_supported",
    "bear_fair_value",
    "bear_probability_pct",
    "bear_assumptions",
    "base_fair_value",
    "base_probability_pct",
    "base_assumptions",
    "bull_fair_value",
    "bull_probability_pct",
    "bull_assumptions",
    "research_completeness",
    "rating_change_conditions",
    "hard_blockers",
    "soft_gaps",
    "evidence_refs",
    "run_id",
)

ASSESSMENT_V2_OUTPUT_FIELDS = (
    "assessment_schema_version",
    "valuation_method",
    "valuation_template",
    "valuation_template_rationale",
    "reference_price",
    "reference_currency",
    "market_data_as_of",
    "fx_rate_to_base",
    "fx_as_of",
    "valuation_supported",
    "bear_fair_value",
    "bear_return_pct",
    "bear_probability_pct",
    "bear_assumptions",
    "base_fair_value",
    "base_return_pct",
    "base_probability_pct",
    "base_assumptions",
    "bull_fair_value",
    "bull_return_pct",
    "bull_probability_pct",
    "bull_assumptions",
    "probability_weighted_fair_value",
    "expected_return_pct",
    "confidence_adjusted_expected_return_pct",
    "buy_below_price",
    "margin_of_safety_pct",
    "research_completeness",
    "research_status",
    "allocation_eligibility",
    "conviction_tier",
    "quality_score",
    "eligibility_reason_codes",
    "frontier_expected_return_pct",
    "frontier_base_return_pct",
    "frontier_bear_base_payoff_ratio",
    "frontier_expected_bear_payoff_ratio",
    "frontier_margin_of_safety_pct",
    "frontier_confidence_levels",
    "frontier_relationship_status",
    "frontier_hard_blockers",
    "canonical_rating",
    "portfolio_action",
    "rating_change_conditions",
    "research_conclusion",
)

RUBRIC_SCORES = frozenset(
    {Decimal("20"), Decimal("40"), Decimal("60"), Decimal("80"), Decimal("100")}
)
CONFIDENCE_FACTORS = {"low": Decimal("0.5"), "medium": Decimal("0.75"), "high": Decimal("1")}
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
QUALITY_WEIGHTS = {
    "thesis_score": Decimal("0.30"),
    "business_quality_score": Decimal("0.30"),
    "balance_sheet_score": Decimal("0.20"),
    "liquidity_score": Decimal("0.20"),
}


class ValuationError(ValueError):
    """Raised when a scenario assessment cannot be normalized safely."""


def _yaml_mapping(path: Path, label: str) -> Mapping[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1:
        raise ValuationError(f"{label} must be a version-1 mapping")
    return raw


def valuation_templates(repository_root: Path) -> Mapping[str, Mapping[str, object]]:
    raw = _yaml_mapping(repository_root / "schemas/valuation_templates.yaml", "valuation templates")
    templates = raw.get("templates")
    if not isinstance(templates, dict) or not templates:
        raise ValuationError("valuation templates must define templates")
    return templates


def validate_research_rubrics(repository_root: Path) -> list[str]:
    try:
        raw = _yaml_mapping(repository_root / "schemas/research_rubrics.yaml", "research rubrics")
        dimensions = raw.get("dimensions")
        if not isinstance(dimensions, dict):
            raise ValuationError("research rubrics must define dimensions")
        errors: list[str] = []
        for field in (
            "thesis_score",
            "business_quality_score",
            "balance_sheet_score",
            "valuation_score",
            "timing_score",
            "liquidity_score",
            "risk_penalty",
        ):
            anchors = dimensions.get(field)
            if not isinstance(anchors, dict) or set(anchors) != {20, 40, 60, 80, 100}:
                errors.append(f"research rubric {field} must define 20/40/60/80/100 anchors")
            elif any(not isinstance(value, str) or not value.strip() for value in anchors.values()):
                errors.append(f"research rubric {field} contains an empty anchor")
        return errors
    except (OSError, yaml.YAMLError, ValuationError) as exc:
        return [str(exc)]


def _return_pct(fair_value: Decimal, reference_price: Decimal) -> Decimal:
    return ((fair_value / reference_price) - Decimal("1")) * Decimal("100")


def live_valuation_projection(
    repository_root: Path,
    settings: Settings,
    security: Mapping[str, str],
    assessment: Mapping[str, str],
    *,
    now: datetime,
    relationship_accepted: bool,
    evidence_fresh: bool,
) -> dict[str, str]:
    """Reprice immutable scenario research at one validated native-currency mark.

    The assessment remains an audit record.  This projection is deliberately derived
    from its fair values and probabilities and never mutates or refreshes that record.
    """

    instant = ensure_utc(now).replace(microsecond=0)
    latest = next(
        (
            row
            for row in read_table(repository_root, "market_latest")
            if row["security_id"] == security["security_id"]
        ),
        None,
    )
    if latest is None:
        raise ValuationError("market_data_missing")
    if latest["status"] != "ok":
        raise ValuationError("market_data_not_ok")
    if (
        latest["provider_symbol"] != security["provider_symbol"]
        or latest["currency"] != security["currency"]
        or assessment.get("reference_currency") != security["currency"]
    ):
        raise ValuationError("market_data_identity_mismatch")
    observed = parse_timestamp(latest["retrieved_at"])
    assert observed is not None
    if observed > instant or instant - observed > settings.market_data.stale_price_after:
        raise ValuationError("market_data_stale")
    raw_mark = latest["adjusted_close"] or latest["close"]
    mark = required_decimal(raw_mark, label="live valuation mark")
    if mark <= 0:
        raise ValuationError("market_data_invalid")

    reasons: list[str] = []
    is_v2 = assessment.get("assessment_schema_version") == "2"
    supported = assessment.get("valuation_supported") == "true"
    complete = assessment.get("research_completeness") == "complete"
    if not is_v2 or not supported:
        reasons.append("valuation_unsupported")
    elif not complete:
        reasons.append("research_incomplete")

    assessed = parse_timestamp(assessment["assessed_at"])
    expires = parse_timestamp(assessment["expires_at"])
    assert assessed is not None and expires is not None
    if (
        assessed > instant
        or instant - assessed > timedelta(days=settings.allocation.maximum_assessment_age_days)
        or expires <= instant
    ):
        reasons.append("assessment_stale")
    if not evidence_fresh:
        reasons.append("assessment_evidence_stale")
    confidence = assessment.get("confidence", "")
    confidence_factor = CONFIDENCE_FACTORS.get(confidence)
    if confidence_factor is None:
        reasons.append("confidence_below_minimum")
        confidence_factor = Decimal("0")
    elif CONFIDENCE_RANK[confidence] < CONFIDENCE_RANK[settings.allocation.minimum_confidence]:
        reasons.append("confidence_below_minimum")
    quality = sum(
        (
            required_decimal(assessment[field], label=field) * weight
            for field, weight in QUALITY_WEIGHTS.items()
        ),
        Decimal("0"),
    )
    if quality <= settings.allocation.minimum_quality_score:
        reasons.append("quality_score_not_above_minimum")
    if not relationship_accepted:
        reasons.append("relationship_missing_or_stale")
    hard_blockers = tuple(
        sorted(part for part in assessment.get("hard_blockers", "").split("|") if part)
    )
    if hard_blockers:
        reasons.append(f"hard_blocker:{','.join(hard_blockers)}")

    output = {
        "valuation_mark": decimal_text(mark),
        "valuation_mark_currency": security["currency"],
        "valuation_mark_as_of": format_timestamp(observed),
        "quality_score": decimal_text(quality),
        "tier": "watch",
        "position_cap_pct": "0",
        "allocation_eligibility": "ineligible",
        "frontier_confidence_levels": str(
            CONFIDENCE_RANK.get(confidence, -1)
            - CONFIDENCE_RANK[settings.allocation.minimum_confidence]
        ),
        "frontier_relationship_status": "complete" if relationship_accepted else "pending",
        "frontier_hard_blockers": "|".join(hard_blockers),
        "eligibility_reason_codes": "|".join(sorted(set(reasons))),
    }
    if not is_v2 or not supported or not complete:
        return output

    fair_values = {
        case: required_decimal(assessment[f"{case}_fair_value"], label=f"{case}_fair_value")
        for case in ("bear", "base", "bull")
    }
    probabilities = {
        case: required_decimal(
            assessment[f"{case}_probability_pct"], label=f"{case}_probability_pct"
        )
        for case in ("bear", "base", "bull")
    }
    scenario_returns = {case: _return_pct(value, mark) for case, value in fair_values.items()}
    expected_fair = sum(
        (fair_values[case] * probabilities[case] for case in ("bear", "base", "bull")),
        Decimal("0"),
    ) / Decimal("100")
    expected = _return_pct(expected_fair, mark)
    adjusted = expected * confidence_factor
    margin = (fair_values["base"] - mark) / fair_values["base"] * Decimal("100")
    downside = max(-scenario_returns["bear"], Decimal("0"))
    base_ratio = (
        Decimal("999999")
        if downside == 0
        else max(scenario_returns["base"], Decimal("0")) / downside
    )
    expected_ratio = Decimal("999999") if downside == 0 else max(adjusted, Decimal("0")) / downside
    output.update(
        {
            **{
                f"{case}_return_pct": decimal_text(scenario_returns[case])
                for case in ("bear", "base", "bull")
            },
            "downside_pct": decimal_text(scenario_returns["bear"]),
            "base_upside_pct": decimal_text(scenario_returns["base"]),
            "probability_weighted_fair_value": decimal_text(expected_fair),
            "expected_return_pct": decimal_text(expected),
            "confidence_adjusted_expected_return_pct": decimal_text(adjusted),
            "margin_of_safety_pct": decimal_text(margin),
            "bear_base_payoff_ratio": decimal_text(base_ratio),
            "expected_bear_payoff_ratio": decimal_text(expected_ratio),
            "frontier_expected_return_pct": decimal_text(
                adjusted - settings.allocation.minimum_confidence_adjusted_expected_return_pct
            ),
            "frontier_base_return_pct": decimal_text(
                scenario_returns["base"] - settings.allocation.minimum_base_upside_pct
            ),
            "frontier_bear_base_payoff_ratio": decimal_text(
                base_ratio - settings.allocation.minimum_upside_downside_ratio
            ),
            "frontier_expected_bear_payoff_ratio": decimal_text(
                expected_ratio - settings.allocation.minimum_expected_bear_payoff_ratio
            ),
            "frontier_margin_of_safety_pct": decimal_text(
                margin - settings.allocation.minimum_margin_of_safety_pct
            ),
        }
    )

    common_safe = not reasons
    common_economic = (
        scenario_returns["base"] >= settings.allocation.minimum_base_upside_pct
        and adjusted >= settings.allocation.minimum_confidence_adjusted_expected_return_pct
    )
    full = (
        common_safe
        and common_economic
        and base_ratio >= settings.allocation.minimum_upside_downside_ratio
        and expected_ratio >= settings.allocation.minimum_expected_bear_payoff_ratio
        and margin >= settings.allocation.minimum_margin_of_safety_pct
    )
    starter = (
        common_safe
        and common_economic
        and base_ratio >= settings.allocation.starter_minimum_upside_downside_ratio
        and expected_ratio >= settings.allocation.starter_minimum_expected_bear_payoff_ratio
        and margin >= settings.allocation.starter_minimum_margin_of_safety_pct
        and scenario_returns["bear"] >= settings.allocation.starter_minimum_bear_return_pct
    )
    if full:
        output["tier"] = "full"
        output["position_cap_pct"] = decimal_text(settings.allocation.maximum_baseline_position_pct)
        output["allocation_eligibility"] = "eligible"
    elif starter:
        output["tier"] = "starter"
        output["position_cap_pct"] = decimal_text(settings.allocation.maximum_starter_position_pct)
        output["allocation_eligibility"] = "eligible"
    else:
        if scenario_returns["base"] < settings.allocation.minimum_base_upside_pct:
            reasons.append("base_return_below_minimum")
        if adjusted < settings.allocation.minimum_confidence_adjusted_expected_return_pct:
            reasons.append("expected_return_below_minimum")
        if base_ratio < settings.allocation.starter_minimum_upside_downside_ratio:
            reasons.append("bear_base_payoff_below_starter_minimum")
        if expected_ratio < settings.allocation.starter_minimum_expected_bear_payoff_ratio:
            reasons.append("expected_bear_payoff_below_starter_minimum")
        if margin < settings.allocation.starter_minimum_margin_of_safety_pct:
            reasons.append("margin_of_safety_below_starter_minimum")
        if scenario_returns["bear"] < settings.allocation.starter_minimum_bear_return_pct:
            reasons.append("bear_return_below_starter_minimum")
    output["eligibility_reason_codes"] = "|".join(sorted(set(reasons)))
    return output


def derive_assessment_dimensions(
    values: Mapping[str, str],
    settings: Settings,
    *,
    relationship_accepted: bool,
) -> dict[str, str]:
    """Derive research state, eligibility, conviction, and every gate distance once."""

    supported = values.get("valuation_supported") == "true"
    completeness = values.get("research_completeness", "")
    research_status = (
        "unsupported" if not supported else "complete" if completeness == "complete" else "partial"
    )
    confidence = values.get("confidence", "")
    confidence_rank = CONFIDENCE_RANK.get(confidence, -1)
    minimum_rank = CONFIDENCE_RANK[settings.allocation.minimum_confidence]
    quality = sum(
        (
            required_decimal(values[field], label=field) * weight
            for field, weight in QUALITY_WEIGHTS.items()
        ),
        Decimal("0"),
    )
    hard_blockers = tuple(part for part in values.get("hard_blockers", "").split("|") if part)
    reasons: list[str] = []
    expected = Decimal("0")
    base_return = Decimal("0")
    bear_return = Decimal("0")
    margin = Decimal("0")
    base_ratio = Decimal("0")
    expected_ratio = Decimal("0")
    if research_status != "complete":
        reasons.append(
            "valuation_unsupported" if research_status == "unsupported" else "research_incomplete"
        )
    else:
        expected = required_decimal(
            values["confidence_adjusted_expected_return_pct"],
            label="confidence_adjusted_expected_return_pct",
        )
        base_return = required_decimal(values["base_return_pct"], label="base_return_pct")
        bear_return = required_decimal(values["bear_return_pct"], label="bear_return_pct")
        margin = required_decimal(values["margin_of_safety_pct"], label="margin_of_safety_pct")
        downside = max(-bear_return, Decimal("0"))
        base_ratio = (
            Decimal("999999") if downside == 0 else max(base_return, Decimal("0")) / downside
        )
        expected_ratio = (
            Decimal("999999") if downside == 0 else max(expected, Decimal("0")) / downside
        )
        if expected < settings.allocation.minimum_confidence_adjusted_expected_return_pct:
            reasons.append("expected_return_below_minimum")
        if base_return < settings.allocation.minimum_base_upside_pct:
            reasons.append("base_return_below_minimum")
        if base_ratio < settings.allocation.minimum_upside_downside_ratio:
            reasons.append("bear_base_payoff_below_minimum")
        if expected_ratio < settings.allocation.minimum_expected_bear_payoff_ratio:
            reasons.append("expected_bear_payoff_below_minimum")
        if margin < settings.allocation.minimum_margin_of_safety_pct:
            reasons.append("margin_of_safety_below_minimum")
    if confidence_rank < minimum_rank:
        reasons.append("confidence_below_minimum")
    if not relationship_accepted:
        reasons.append("relationship_pending")
    if hard_blockers:
        reasons.append(f"hard_blocker:{','.join(hard_blockers)}")
    eligible = not reasons
    conviction = (
        eligible
        and quality >= settings.allocation.conviction_quality_score
        and required_decimal(values["expected_return_pct"], label="expected_return_pct")
        >= settings.allocation.conviction_expected_return_pct
        and confidence_rank >= CONFIDENCE_RANK[settings.allocation.conviction_minimum_confidence]
    )
    return {
        "research_status": research_status,
        "allocation_eligibility": "eligible" if eligible else "ineligible",
        "conviction_tier": ("conviction" if conviction else "baseline" if eligible else "watch"),
        "quality_score": decimal_text(quality),
        "eligibility_reason_codes": "|".join(sorted(reasons)),
        "frontier_expected_return_pct": decimal_text(
            expected - settings.allocation.minimum_confidence_adjusted_expected_return_pct
        ),
        "frontier_base_return_pct": decimal_text(
            base_return - settings.allocation.minimum_base_upside_pct
        ),
        "frontier_bear_base_payoff_ratio": decimal_text(
            base_ratio - settings.allocation.minimum_upside_downside_ratio
        ),
        "frontier_expected_bear_payoff_ratio": decimal_text(
            expected_ratio - settings.allocation.minimum_expected_bear_payoff_ratio
        ),
        "frontier_margin_of_safety_pct": decimal_text(
            margin - settings.allocation.minimum_margin_of_safety_pct
        ),
        "frontier_confidence_levels": str(confidence_rank - minimum_rank),
        "frontier_relationship_status": "complete" if relationship_accepted else "pending",
        "frontier_hard_blockers": "|".join(hard_blockers),
    }


def _validate_market_references(
    repository_root: Path,
    settings: Settings,
    values: Mapping[str, str],
) -> None:
    assessed_at = parse_timestamp(values["assessed_at"])
    market_as_of = parse_timestamp(values["market_data_as_of"])
    fx_as_of = parse_timestamp(values["fx_as_of"])
    assert assessed_at is not None and market_as_of is not None and fx_as_of is not None
    latest = next(
        (
            row
            for row in read_table(repository_root, "market_latest")
            if row["security_id"] == values["security_id"]
        ),
        None,
    )
    security = next(
        row
        for row in read_table(repository_root, "securities")
        if row["security_id"] == values["security_id"]
    )
    if latest is None or latest["status"] != "ok":
        raise ValuationError("assessment v2 requires a successful current market mark")
    if (
        latest["provider_symbol"] != security["provider_symbol"]
        or latest["currency"] != security["currency"]
    ):
        raise ValuationError("assessment market mark does not match immutable instrument identity")
    if values["reference_currency"] != security["currency"]:
        raise ValuationError("assessment reference currency does not match immutable identity")
    latest_mark = latest["adjusted_close"] or latest["close"]
    if required_decimal(values["reference_price"], label="reference_price") != required_decimal(
        latest_mark, label="latest valuation mark"
    ):
        raise ValuationError("assessment reference price does not match the current mark")
    if values["market_data_as_of"] != latest["retrieved_at"]:
        raise ValuationError("assessment market_data_as_of does not match the current mark")
    if (
        assessed_at - market_as_of < timedelta(0)
        or assessed_at - market_as_of > settings.market_data.stale_price_after
    ):
        raise ValuationError("assessment market reference is stale")
    try:
        fx = latest_fx_rate_record(
            repository_root,
            security["currency"],
            settings.portfolio.base_currency,
            now=assessed_at,
            maximum_age=settings.market_data.stale_price_after,
        )
    except MarketDataError as exc:
        raise ValuationError(str(exc)) from exc
    if required_decimal(values["fx_rate_to_base"], label="fx_rate_to_base") != fx.rate_to_base:
        raise ValuationError("assessment FX rate does not match the current canonical rate")
    if values["fx_as_of"] != values["assessed_at"] and values[
        "fx_as_of"
    ] != fx.retrieved_at.isoformat().replace("+00:00", "Z"):
        raise ValuationError("assessment fx_as_of does not match the current canonical rate")


def normalize_v2_assessment(
    repository_root: Path,
    settings: Settings,
    values: Mapping[str, str],
) -> dict[str, str]:
    """Validate agent inputs and calculate every canonical scenario derivative."""

    if set(values) != set(ASSESSMENT_V2_AGENT_FIELDS):
        raise ValuationError("assessment v2 fields differ from the canonical agent contract")
    if values["assessment_schema_version"] != "2":
        raise ValuationError("assessment_schema_version must be 2")
    templates = valuation_templates(repository_root)
    template = templates.get(values["valuation_template"])
    if not isinstance(template, dict):
        raise ValuationError("unknown valuation_template")
    if values["valuation_template"] == "other" and not values["valuation_template_rationale"]:
        raise ValuationError("other valuation template requires an explicit rationale")
    if values["valuation_template"] != "other" and values["valuation_template_rationale"]:
        raise ValuationError("valuation_template_rationale is allowed only for other")
    allowed_methods = template.get("allowed_methods")
    if not isinstance(allowed_methods, list) or values["valuation_method"] not in allowed_methods:
        raise ValuationError("valuation_method is not allowed by valuation_template")
    for field in (
        "thesis_score",
        "business_quality_score",
        "balance_sheet_score",
        "valuation_score",
        "timing_score",
        "liquidity_score",
        "risk_penalty",
    ):
        if required_decimal(values[field], label=field) not in RUBRIC_SCORES:
            raise ValuationError(f"{field} must use an anchored 20/40/60/80/100 score")
    _validate_market_references(repository_root, settings, values)
    reference = required_decimal(values["reference_price"], label="reference_price")
    if reference <= 0:
        raise ValuationError("reference_price must be positive")
    supported = values["valuation_supported"] == "true"
    if values["valuation_supported"] not in {"true", "false"}:
        raise ValuationError("valuation_supported must be true or false")
    output = {field: values.get(field, "") for field in ASSESSMENT_V2_OUTPUT_FIELDS}
    if not supported:
        forbidden = (
            "bear_fair_value",
            "bear_probability_pct",
            "bear_assumptions",
            "base_fair_value",
            "base_probability_pct",
            "base_assumptions",
            "bull_fair_value",
            "bull_probability_pct",
            "bull_assumptions",
        )
        if any(values[field] for field in forbidden):
            raise ValuationError("unsupported valuation must not invent scenario values")
        if values[
            "research_completeness"
        ] != "unsupported" or "valuation_unsupported" not in values["hard_blockers"].split("|"):
            raise ValuationError("unsupported valuation requires exact completeness and blocker")
        return output
    if values["research_completeness"] != "complete":
        raise ValuationError("supported valuation requires research_completeness=complete")
    fair_values = [
        required_decimal(values[f"{case}_fair_value"], label=f"{case}_fair_value")
        for case in ("bear", "base", "bull")
    ]
    probabilities = [
        required_decimal(values[f"{case}_probability_pct"], label=f"{case}_probability_pct")
        for case in ("bear", "base", "bull")
    ]
    if any(value < 0 for value in probabilities) or sum(probabilities) != Decimal("100"):
        raise ValuationError("scenario probabilities must be non-negative and sum exactly to 100")
    if fair_values != sorted(fair_values) or any(value <= 0 for value in fair_values):
        raise ValuationError("scenario fair values must be positive and bear <= base <= bull")
    if any(not values[f"{case}_assumptions"] for case in ("bear", "base", "bull")):
        raise ValuationError("every supported scenario requires key assumptions")
    returns = [_return_pct(value, reference) for value in fair_values]
    expected_fair = sum(
        (
            value * probability
            for value, probability in zip(fair_values, probabilities, strict=True)
        ),
        Decimal("0"),
    ) / Decimal("100")
    expected_return = _return_pct(expected_fair, reference)
    confidence_factor = CONFIDENCE_FACTORS.get(values["confidence"])
    if confidence_factor is None:
        raise ValuationError("assessment confidence is not canonical")
    buy_below = fair_values[1] * (
        Decimal("1") - settings.risk.margin_of_safety_pct / Decimal("100")
    )
    margin_of_safety = ((fair_values[1] - reference) / fair_values[1]) * Decimal("100")
    for case, fair, probability, assumptions, case_return in zip(
        ("bear", "base", "bull"),
        fair_values,
        probabilities,
        (values["bear_assumptions"], values["base_assumptions"], values["bull_assumptions"]),
        returns,
        strict=True,
    ):
        output[f"{case}_fair_value"] = decimal_text(fair)
        output[f"{case}_return_pct"] = decimal_text(case_return)
        output[f"{case}_probability_pct"] = decimal_text(probability)
        output[f"{case}_assumptions"] = assumptions
    output.update(
        {
            "probability_weighted_fair_value": decimal_text(expected_fair),
            "expected_return_pct": decimal_text(expected_return),
            "confidence_adjusted_expected_return_pct": decimal_text(
                expected_return * confidence_factor
            ),
            "buy_below_price": decimal_text(buy_below),
            "margin_of_safety_pct": decimal_text(margin_of_safety),
        }
    )
    return output

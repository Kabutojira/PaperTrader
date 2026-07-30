"""Scenario-complete, Decimal-safe valuation normalization and anchored rubrics."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import yaml

from papertrader.config import Settings
from papertrader.market_data import MarketDataError, latest_fx_rate_record
from papertrader.tables import read_table
from papertrader.utils import decimal_text, parse_timestamp, required_decimal

ASSESSMENT_V2_AGENT_FIELDS = (
    "assessment_schema_version",
    "security_id",
    "assessed_at",
    "expires_at",
    "eligibility",
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
)

RUBRIC_SCORES = frozenset(
    {Decimal("20"), Decimal("40"), Decimal("60"), Decimal("80"), Decimal("100")}
)
CONFIDENCE_FACTORS = {"low": Decimal("0.5"), "medium": Decimal("0.75"), "high": Decimal("1")}


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
    if required_decimal(values["reference_price"], label="reference_price") != required_decimal(
        latest["adjusted_close"], label="latest adjusted close"
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

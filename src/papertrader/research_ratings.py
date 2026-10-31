"""Native-currency, current-price research opinions; no account or trade inputs."""

from __future__ import annotations

import configparser
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from papertrader.research_market import completed_session
from papertrader.research_state import decimal, timestamp, validate_scores

CONFIDENCE = {"low": Decimal("0.4"), "medium": Decimal("0.7"), "high": Decimal("1")}

VALUATION_RESEARCH_FIELDS = (
    "method",
    "method_rationale",
    "source_ids",
    "thesis",
    "key_assumptions",
    "downside",
    "catalysts",
    "invalidation_conditions",
    "horizon_months",
    "bear_assumptions",
    "base_assumptions",
    "bull_assumptions",
)


def valuation_coverage(assessment: Mapping[str, str] | None) -> str:
    """Baseline research completeness, independent of price or assessment freshness.

    Callers validate canonical scenario mathematics and citations separately.
    Old complete research counts as baseline coverage, never as a current rating.
    """
    if assessment is None:
        return "missing_research"
    if assessment.get("research_status") != "supported":
        return "valuation_unsupported"
    fields = (
        *VALUATION_RESEARCH_FIELDS,
        *(
            f"{case}_{field}"
            for case in ("bear", "base", "bull")
            for field in ("fair_value", "probability_pct")
        ),
    )
    return "complete" if all(assessment.get(field) for field in fields) else "incomplete_research"


@dataclass(frozen=True)
class RatingThresholds:
    strong_buy: Decimal = Decimal("40")
    buy: Decimal = Decimal("20")
    sell: Decimal = Decimal("-10")
    strong_sell: Decimal = Decimal("-25")
    buy_minimum_base_return: Decimal = Decimal("10")
    strong_buy_minimum_base_return: Decimal = Decimal("20")
    short: Decimal = Decimal("-30")
    short_maximum_base_return: Decimal = Decimal("-20")
    short_maximum_business_quality: Decimal = Decimal("25")
    short_maximum_balance_sheet: Decimal = Decimal("25")
    short_minimum_risk_penalty: Decimal = Decimal("75")
    short_minimum_confidence: str = "medium"
    minimum_confidence: str = "medium"
    strong_buy_minimum_confidence: str = "high"


DEFAULT_RATING_THRESHOLDS = RatingThresholds()


def rating_thresholds(root: Path) -> RatingThresholds:
    config = configparser.ConfigParser()
    config.read(root / "research.ini")
    defaults = DEFAULT_RATING_THRESHOLDS
    values = {
        key: decimal(
            config.get("ratings", f"{key}_return_pct", fallback=str(getattr(defaults, key)))
        )
        for key in ("strong_buy", "buy", "sell", "strong_sell", "short")
    }
    values["buy_minimum_base_return"] = decimal(
        config.get(
            "ratings",
            "buy_minimum_base_return_pct",
            fallback=str(defaults.buy_minimum_base_return),
        )
    )
    values["strong_buy_minimum_base_return"] = decimal(
        config.get(
            "ratings",
            "strong_buy_minimum_base_return_pct",
            fallback=str(defaults.strong_buy_minimum_base_return),
        )
    )
    for key in (
        "short_maximum_base_return",
        "short_maximum_business_quality",
        "short_maximum_balance_sheet",
        "short_minimum_risk_penalty",
    ):
        values[key] = decimal(config.get("ratings", key, fallback=str(getattr(defaults, key))))
    short_minimum = config.get("ratings", "short_minimum_confidence", fallback="medium")
    minimum = config.get("ratings", "minimum_confidence", fallback="medium")
    strong_minimum = config.get("ratings", "strong_buy_minimum_confidence", fallback="high")
    if (
        not -100 <= values["short"] < values["strong_sell"]
        or not -100 <= values["short_maximum_base_return"] < 0
        or any(
            not 0 <= values[key] <= 100
            for key in (
                "short_maximum_business_quality",
                "short_maximum_balance_sheet",
                "short_minimum_risk_penalty",
            )
        )
        or short_minimum not in {"medium", "high"}
        or not values["strong_sell"] < values["sell"] < values["buy"] < values["strong_buy"]
        or not 0 <= values["buy_minimum_base_return"] <= values["strong_buy_minimum_base_return"]
        or minimum not in CONFIDENCE
        or strong_minimum not in CONFIDENCE
    ):
        raise ValueError("invalid rating thresholds")
    return RatingThresholds(
        **values,
        minimum_confidence=minimum,
        strong_buy_minimum_confidence=strong_minimum,
        short_minimum_confidence=short_minimum,
    )


def reprice(
    assessment: Mapping[str, str],
    market: Mapping[str, str],
    *,
    now: datetime,
    thresholds: RatingThresholds = DEFAULT_RATING_THRESHOLDS,
    latest_split_date: str = "",
    research_role: str = "long",
    sources: Mapping[str, dict[str, str]] | None = None,
) -> dict[str, str]:
    """Shrink expected return toward zero by confidence; never mutate research facts."""

    result = {
        "rating": "unrated",
        "reason": "",
        "weighted_fair_value": "",
        "expected_return_pct": "",
        "adjusted_return_pct": "",
        "base_return_pct": "",
    }
    if assessment.get("research_status") != "supported":
        result["reason"] = "valuation_unsupported"
        return result
    if (
        not assessment.get("security_id")
        or not market.get("security_id")
        or assessment["security_id"] != market["security_id"]
    ):
        result["reason"] = "market_identity_mismatch"
        return result
    if timestamp(assessment["valid_until"]) <= now or timestamp(assessment["assessed_at"]) > now:
        result["reason"] = "research_expired_or_future"
        return result
    if (
        latest_split_date
        and latest_split_date > timestamp(assessment["assessed_at"]).date().isoformat()
    ):
        result["reason"] = "split_requires_research"
        return result
    try:
        expected_session = completed_session(market["venue_mic"], now).isoformat()
    except (KeyError, ValueError):
        result["reason"] = "market_stale_or_unavailable"
        return result
    if market.get("status") != "current" or market.get("price_date") != expected_session:
        result["reason"] = "market_stale_or_unavailable"
        return result
    if market.get("currency") != assessment["currency"]:
        result["reason"] = "currency_mismatch"
        return result
    if sources is not None and any(
        ref not in sources
        or sources[ref]["status"] not in {"available", "valid"}
        or not sources[ref]["checked_at"]
        or timestamp(sources[ref]["checked_at"])
        < timestamp(assessment["assessed_at"]) - timedelta(hours=1)
        or timestamp(sources[ref]["checked_at"]) > now
        for ref in filter(None, assessment["source_ids"].split("|"))
    ):
        result["reason"] = "source_evidence_unavailable"
        return result
    confidence = CONFIDENCE[assessment["confidence"]]
    if confidence < CONFIDENCE[thresholds.minimum_confidence]:
        result["reason"] = "insufficient_confidence"
        return result
    price = decimal(market["close"])
    if price <= 0:
        result["reason"] = "invalid_price"
        return result
    values = [decimal(assessment[f"{case}_fair_value"]) for case in ("bear", "base", "bull")]
    probabilities = [
        decimal(assessment[f"{case}_probability_pct"]) for case in ("bear", "base", "bull")
    ]
    if (
        min(values) < 0
        or values != sorted(values)
        or min(probabilities) < 0
        or sum(probabilities) != 100
    ):
        raise ValueError("invalid scenario math")
    if valuation_coverage(assessment) != "complete":
        result["reason"] = "incomplete_research"
        return result
    if assessment.get("limitations", "").strip().lower().startswith("blocker:"):
        result["reason"] = "valuation_blocked"
        return result
    weighted = sum(
        (
            value * probability / 100
            for value, probability in zip(values, probabilities, strict=True)
        ),
        Decimal(0),
    )
    expected = 100 * (weighted / price - 1)
    adjusted = expected * confidence
    base = 100 * (values[1] / price - 1)
    weak = False
    score_fields = ("business_quality_score", "balance_sheet_score", "risk_penalty")
    if (
        research_role == "short_candidate"
        and sources is not None
        and all(assessment.get(field) for field in score_fields)
    ):
        try:
            validate_scores(dict(assessment), {"venue_mic": market["venue_mic"]}, sources)
            weak = (
                decimal(assessment["business_quality_score"])
                <= thresholds.short_maximum_business_quality
                or decimal(assessment["balance_sheet_score"])
                <= thresholds.short_maximum_balance_sheet
            ) and decimal(assessment["risk_penalty"]) >= thresholds.short_minimum_risk_penalty
        except (ValueError, KeyError, TypeError):
            weak = False
    if (
        weak
        and adjusted <= thresholds.short
        and base <= thresholds.short_maximum_base_return
        and confidence >= CONFIDENCE[thresholds.short_minimum_confidence]
    ):
        rating = "short"
    elif adjusted <= thresholds.strong_sell:
        rating = "strong_sell"
    elif adjusted <= thresholds.sell:
        rating = "sell"
    elif (
        adjusted >= thresholds.strong_buy
        and base >= thresholds.strong_buy_minimum_base_return
        and confidence >= CONFIDENCE[thresholds.strong_buy_minimum_confidence]
    ):
        rating = "strong_buy"
    elif adjusted >= thresholds.buy and base >= thresholds.buy_minimum_base_return:
        rating = "buy"
    else:
        rating = "hold"
    result.update(
        rating=rating,
        weighted_fair_value=str(weighted),
        expected_return_pct=str(expected),
        adjusted_return_pct=str(adjusted),
        base_return_pct=str(base),
    )
    return result

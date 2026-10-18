"""Native-currency, current-price research opinions; no account or trade inputs."""

from __future__ import annotations

import configparser
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from papertrader.research_market import completed_session
from papertrader.research_state import decimal, timestamp

CONFIDENCE = {"low": Decimal("0.4"), "medium": Decimal("0.7"), "high": Decimal("1")}


@dataclass(frozen=True)
class RatingThresholds:
    strong_buy: Decimal = Decimal("40")
    buy: Decimal = Decimal("20")
    sell: Decimal = Decimal("-10")
    strong_sell: Decimal = Decimal("-25")
    buy_minimum_base_return: Decimal = Decimal("10")
    strong_buy_minimum_base_return: Decimal = Decimal("20")
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
        for key in ("strong_buy", "buy", "sell", "strong_sell")
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
    minimum = config.get("ratings", "minimum_confidence", fallback="medium")
    strong_minimum = config.get("ratings", "strong_buy_minimum_confidence", fallback="high")
    if (
        not values["strong_sell"] < values["sell"] < values["buy"] < values["strong_buy"]
        or not 0 <= values["buy_minimum_base_return"] <= values["strong_buy_minimum_base_return"]
        or minimum not in CONFIDENCE
        or strong_minimum not in CONFIDENCE
    ):
        raise ValueError("invalid rating thresholds")
    return RatingThresholds(
        **values, minimum_confidence=minimum, strong_buy_minimum_confidence=strong_minimum
    )


def reprice(
    assessment: Mapping[str, str],
    market: Mapping[str, str],
    *,
    now: datetime,
    thresholds: RatingThresholds = DEFAULT_RATING_THRESHOLDS,
    latest_split_date: str = "",
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
    if not all(
        assessment.get(field)
        for field in (
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
    ):
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
    if adjusted <= thresholds.strong_sell:
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

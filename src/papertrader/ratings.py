"""Deterministic canonical investment ratings and context-aware portfolio actions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal

from papertrader.config import Settings
from papertrader.utils import required_decimal

RATINGS = frozenset({"strong_buy", "buy", "hold", "sell", "strong_sell", "unrated"})
ACTIONS = frozenset(
    {"initiate", "add", "hold", "trim", "exit", "avoid", "watch", "short_candidate"}
)
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def canonical_rating(assessment: Mapping[str, str], settings: Settings) -> str:
    """Map one scenario-complete assessment to exactly one canonical rating."""

    if (
        assessment.get("assessment_schema_version") != "2"
        or assessment.get("research_status") != "complete"
        or assessment.get("valuation_supported") != "true"
    ):
        return "unrated"
    expected = required_decimal(
        assessment["confidence_adjusted_expected_return_pct"],
        label="confidence_adjusted_expected_return_pct",
    )
    base_return = required_decimal(assessment["base_return_pct"], label="base_return_pct")
    confidence = assessment["confidence"]
    blockers = set(part for part in assessment["hard_blockers"].split("|") if part)
    if expected <= settings.ratings.strong_sell_expected_return_pct or (
        "thesis_invalidated" in blockers and expected < 0
    ):
        return "strong_sell"
    if expected <= settings.ratings.sell_expected_return_pct:
        return "sell"
    if blockers:
        return "hold" if expected >= 0 else "sell"
    if (
        expected >= settings.ratings.strong_buy_expected_return_pct
        and base_return >= settings.ratings.strong_buy_base_return_pct
        and CONFIDENCE_RANK.get(confidence, -1)
        >= CONFIDENCE_RANK[settings.ratings.strong_buy_minimum_confidence]
    ):
        return "strong_buy"
    if (
        expected >= settings.ratings.buy_expected_return_pct
        and base_return >= settings.ratings.buy_base_return_pct
    ):
        return "buy"
    return "hold"


def portfolio_action(
    rating: str,
    assessment: Mapping[str, str],
    *,
    current_quantity: Decimal,
    current_weight_pct: Decimal,
    target_weight_pct: Decimal,
    strategies: Sequence[Mapping[str, str]] = (),
) -> str:
    """Map a rating to an action using owned/target context without authorizing a trade."""

    if rating not in RATINGS:
        raise ValueError(f"unknown canonical rating: {rating}")
    blockers = set(part for part in assessment.get("hard_blockers", "").split("|") if part)
    owned = current_quantity != 0 or current_weight_pct != 0
    if rating == "unrated":
        return (
            "avoid" if blockers.intersection({"solvency_risk", "thesis_invalidated"}) else "watch"
        )
    if rating in {"strong_buy", "buy"}:
        if not owned:
            return "initiate"
        return "add" if current_weight_pct < target_weight_pct else "hold"
    if rating == "hold":
        return "hold" if owned else "watch"
    if rating == "sell":
        if owned:
            return "trim"
        supports_short = any(
            row.get("direction") == "short" and row.get("status") in {"ready", "active"}
            for row in strategies
        )
        return "short_candidate" if supports_short else "avoid"
    return "exit" if owned else "avoid"


def research_conclusion(
    assessment: Mapping[str, str], rating: str, action: str, conditions: str
) -> str:
    """Render the one required concise canonical research conclusion."""

    label = rating.replace("_", " ").title()
    action_label = action.replace("_", " ").title()
    if rating == "unrated":
        return (
            f"Rating: {label}. Portfolio action: {action_label}. A supportable scenario valuation "
            f"is unavailable. Upgrade or downgrade conditions: {conditions}"
        )
    return (
        f"Rating: {label}. Portfolio action: {action_label}. Bear/base/bull returns are "
        f"{assessment['bear_return_pct']}%/{assessment['base_return_pct']}%/"
        f"{assessment['bull_return_pct']}% over {assessment['valuation_horizon_months']} months; "
        f"probability-weighted expected return is {assessment['expected_return_pct']}% with "
        f"{assessment['confidence']} confidence. Upgrade or downgrade conditions: {conditions}"
    )

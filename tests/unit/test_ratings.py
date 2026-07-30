from __future__ import annotations

from decimal import Decimal

import pytest

from papertrader.config import Settings
from papertrader.ratings import canonical_rating, portfolio_action


def _assessment(**overrides: str) -> dict[str, str]:
    value = {
        "assessment_schema_version": "2",
        "research_status": "complete",
        "valuation_supported": "true",
        "confidence_adjusted_expected_return_pct": "20",
        "base_return_pct": "20",
        "confidence": "high",
        "hard_blockers": "",
    }
    value.update(overrides)
    return value


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({}, "strong_buy"),
        ({"confidence": "medium"}, "buy"),
        ({"confidence_adjusted_expected_return_pct": "10"}, "buy"),
        ({"confidence_adjusted_expected_return_pct": "9.99"}, "hold"),
        ({"confidence_adjusted_expected_return_pct": "-10"}, "sell"),
        ({"confidence_adjusted_expected_return_pct": "-25"}, "strong_sell"),
        ({"valuation_supported": "false"}, "unrated"),
    ],
)
def test_canonical_rating_thresholds_are_inclusive_and_deterministic(
    sandbox_settings: Settings,
    overrides: dict[str, str],
    expected: str,
) -> None:
    assert canonical_rating(_assessment(**overrides), sandbox_settings) == expected


def test_portfolio_action_uses_position_context_without_creating_authority() -> None:
    assessment = _assessment()
    assert (
        portfolio_action(
            "buy",
            assessment,
            current_quantity=Decimal("0"),
            current_weight_pct=Decimal("0"),
            target_weight_pct=Decimal("5"),
        )
        == "initiate"
    )
    assert (
        portfolio_action(
            "sell",
            assessment,
            current_quantity=Decimal("10"),
            current_weight_pct=Decimal("5"),
            target_weight_pct=Decimal("0"),
        )
        == "trim"
    )
    assert (
        portfolio_action(
            "sell",
            assessment,
            current_quantity=Decimal("0"),
            current_weight_pct=Decimal("0"),
            target_weight_pct=Decimal("0"),
        )
        == "avoid"
    )

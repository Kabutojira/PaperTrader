"""Pure Decimal risk policy for proposed paper-order legs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from decimal import Decimal

from papertrader.config import Settings
from papertrader.models import (
    OrderLegSpec,
    ReferencePrice,
    RiskAssessment,
    RiskPosition,
    RiskState,
)
from papertrader.utils import CanonicalValueError, ensure_utc


class RiskRejected(RuntimeError):
    """Raised when deterministic policy rejects a paper order."""


def _limit(equity: Decimal, percentage: Decimal) -> Decimal:
    return equity * percentage / Decimal("100")


def _key(security_id: str, provider_contract_id: str, side: str) -> tuple[str, str, str]:
    return security_id, provider_contract_id, side


def _reference_key(security_id: str, provider_contract_id: str) -> tuple[str, str]:
    return security_id, provider_contract_id


def _quantity_delta(leg: OrderLegSpec) -> Decimal:
    if leg.side == "long":
        return leg.quantity if leg.action == "buy" else -leg.quantity
    return leg.quantity if leg.action == "sell" else -leg.quantity


def _cash_delta(leg: OrderLegSpec, reference: ReferencePrice) -> Decimal:
    notional = leg.quantity * leg.contract_multiplier * reference.price * reference.fx_rate_to_base
    return -notional if leg.action == "buy" else notional


def _option_group_max_loss(
    legs: Sequence[tuple[OrderLegSpec, ReferencePrice]],
) -> Decimal | None:
    """Return finite expiry max loss in base currency, or ``None`` when unbounded."""

    strikes = sorted({leg.strike for leg, _ in legs if leg.strike is not None})
    if not strikes:
        raise CanonicalValueError("option risk group has no strikes")
    call_high_slope = Decimal("0")
    for leg, _ in legs:
        if leg.option_type == "call":
            direction = Decimal("1") if leg.action == "buy" else Decimal("-1")
            call_high_slope += direction * leg.quantity * leg.contract_multiplier
    if call_high_slope < 0:
        return None
    spots = [Decimal("0"), *strikes]
    pnl_values: list[Decimal] = []
    for spot in spots:
        pnl = Decimal("0")
        for leg, reference in legs:
            assert leg.strike is not None
            intrinsic = (
                max(Decimal("0"), spot - leg.strike)
                if leg.option_type == "call"
                else max(Decimal("0"), leg.strike - spot)
            )
            direction = Decimal("1") if leg.action == "buy" else Decimal("-1")
            local_pnl = (
                direction * leg.quantity * leg.contract_multiplier * (intrinsic - reference.price)
            )
            pnl += local_pnl * reference.fx_rate_to_base
        pnl_values.append(pnl)
    return max(Decimal("0"), -min(pnl_values))


def option_max_loss(
    legs: Sequence[OrderLegSpec],
    references: Mapping[tuple[str, str], ReferencePrice],
) -> tuple[Decimal | None, tuple[str, ...]]:
    """Calculate bounded option risk by underlying, expiry, and currency."""

    groups: dict[tuple[str, object, str], list[tuple[OrderLegSpec, ReferencePrice]]] = defaultdict(
        list
    )
    violations: list[str] = []
    for leg in legs:
        if leg.instrument_type != "option":
            continue
        # Closing legs release risk; existing structures remain represented in RiskState.
        opens = (leg.side == "long" and leg.action == "buy") or (
            leg.side == "short" and leg.action == "sell"
        )
        if not opens:
            continue
        if (
            leg.option_type not in {"call", "put"}
            or leg.expiry is None
            or leg.strike is None
            or not leg.strike.is_finite()
            or not leg.quantity.is_finite()
            or not leg.contract_multiplier.is_finite()
            or leg.strike <= 0
            or leg.quantity <= 0
            or leg.contract_multiplier <= 0
        ):
            violations.append(f"invalid_option_leg:{leg.leg_id}")
            continue
        reference = references.get(_reference_key(leg.security_id, leg.provider_contract_id))
        if reference is None:
            violations.append(f"missing_reference:{leg.leg_id}")
            continue
        if (
            not reference.price.is_finite()
            or not reference.fx_rate_to_base.is_finite()
            or reference.price <= 0
            or reference.fx_rate_to_base <= 0
        ):
            violations.append(f"invalid_reference:{leg.leg_id}")
            continue
        groups[(leg.security_id, leg.expiry, leg.currency)].append((leg, reference))
    total = Decimal("0")
    for group_key, group in groups.items():
        loss = _option_group_max_loss(group)
        if loss is None:
            violations.append(f"unbounded_option_risk:{group_key[0]}:{group_key[1]}")
        else:
            total += loss
    return (
        None if any(value.startswith("unbounded_option_risk") for value in violations) else total
    ), tuple(violations)


def assess_order_risk(
    settings: Settings,
    state: RiskState,
    legs: Sequence[OrderLegSpec],
    references: Sequence[ReferencePrice],
    security_venues: Mapping[str, str],
    *,
    now: datetime,
    activates_new_strategy: bool,
) -> RiskAssessment:
    """Evaluate cash, identity, freshness, exposure, turnover, options, and concentration."""

    instant = ensure_utc(now)
    violations: list[str] = []
    state_values = (
        state.equity_base,
        state.cash_base,
        state.gross_exposure_base,
        state.short_exposure_base,
        state.options_risk_base,
        state.daily_turnover_base,
    )
    if any(not value.is_finite() for value in state_values):
        return RiskAssessment(
            violations=("non_finite_risk_state",),
            projected_cash_base=state.cash_base,
            projected_gross_exposure_base=state.gross_exposure_base,
            projected_short_exposure_base=state.short_exposure_base,
            projected_options_risk_base=state.options_risk_base,
        )
    if state.equity_base <= 0:
        violations.append("non_positive_equity")
    if (
        state.gross_exposure_base < 0
        or state.short_exposure_base < 0
        or state.options_risk_base < 0
        or state.daily_turnover_base < 0
        or state.active_strategy_count < 0
    ):
        violations.append("invalid_risk_state")
    reference_map: dict[tuple[str, str], ReferencePrice] = {}
    for supplied_reference in references:
        reference_key = _reference_key(
            supplied_reference.security_id, supplied_reference.provider_contract_id
        )
        if reference_key in reference_map:
            violations.append(f"duplicate_reference:{reference_key[0]}:{reference_key[1]}")
        reference_map[reference_key] = supplied_reference
    position_quantities: dict[tuple[str, str, str], Decimal] = {
        _key(position.security_id, position.provider_contract_id, position.side): position.quantity
        for position in state.positions
    }
    position_metadata: dict[tuple[str, str, str], RiskPosition | OrderLegSpec] = {
        _key(position.security_id, position.provider_contract_id, position.side): position
        for position in state.positions
    }
    if len(position_quantities) != len(state.positions):
        violations.append("duplicate_risk_position")
    for position in state.positions:
        if (
            position.side not in {"long", "short"}
            or position.instrument_type not in {"equity", "option"}
            or not position.quantity.is_finite()
            or not position.contract_multiplier.is_finite()
            or position.quantity <= 0
            or position.contract_multiplier <= 0
        ):
            violations.append(
                f"invalid_risk_position:{position.security_id}:{position.provider_contract_id}"
            )
    if any(
        violation == "duplicate_risk_position" or violation.startswith("invalid_risk_position:")
        for violation in violations
    ):
        return RiskAssessment(
            violations=tuple(sorted(set(violations))),
            projected_cash_base=state.cash_base,
            projected_gross_exposure_base=state.gross_exposure_base,
            projected_short_exposure_base=state.short_exposure_base,
            projected_options_risk_base=state.options_risk_base,
        )
    projected_cash = state.cash_base
    turnover_increment = Decimal("0")
    for leg in legs:
        invalid_structure = False
        if leg.action not in {"buy", "sell"}:
            violations.append(f"invalid_action:{leg.leg_id}")
            invalid_structure = True
        if leg.side not in {"long", "short"}:
            violations.append(f"invalid_side:{leg.leg_id}")
            invalid_structure = True
        if (
            not leg.quantity.is_finite()
            or not leg.contract_multiplier.is_finite()
            or leg.quantity <= 0
            or leg.contract_multiplier <= 0
        ):
            violations.append(f"invalid_quantity:{leg.leg_id}")
            invalid_structure = True
        if invalid_structure:
            continue
        if leg.instrument_type not in settings.risk.allowed_instruments:
            violations.append(f"instrument_not_allowed:{leg.leg_id}:{leg.instrument_type}")
        if leg.currency not in settings.risk.allowed_currencies:
            violations.append(f"currency_not_allowed:{leg.leg_id}:{leg.currency}")
        venue = security_venues.get(leg.security_id)
        if venue is None:
            violations.append(f"unknown_security:{leg.leg_id}:{leg.security_id}")
        elif venue not in settings.risk.allowed_exchanges:
            violations.append(f"exchange_not_allowed:{leg.leg_id}:{venue}")
        leg_reference = reference_map.get(_reference_key(leg.security_id, leg.provider_contract_id))
        if leg_reference is None:
            violations.append(f"missing_reference:{leg.leg_id}")
            continue
        if (
            leg_reference.currency != leg.currency
            or not leg_reference.price.is_finite()
            or not leg_reference.fx_rate_to_base.is_finite()
            or leg_reference.price <= 0
            or leg_reference.fx_rate_to_base <= 0
        ):
            violations.append(f"invalid_reference_identity:{leg.leg_id}")
            continue
        age = instant - ensure_utc(leg_reference.as_of)
        if age < timedelta(0):
            violations.append(f"future_reference:{leg.leg_id}")
        freshness = (
            settings.orders.option_quote_freshness
            if leg.instrument_type == "option"
            else settings.market_data.stale_price_after
        )
        if age > freshness:
            violations.append(f"stale_reference:{leg.leg_id}")
        if leg.instrument_type == "option":
            if leg_reference.bid is None or leg_reference.ask is None:
                violations.append(f"missing_bid_ask:{leg.leg_id}")
            elif (
                not leg_reference.bid.is_finite()
                or not leg_reference.ask.is_finite()
                or leg_reference.bid < 0
                or leg_reference.ask <= 0
                or leg_reference.bid > leg_reference.ask
            ):
                violations.append(f"invalid_bid_ask:{leg.leg_id}")
            if (
                leg_reference.open_interest is None
                or leg_reference.open_interest < settings.risk.minimum_option_open_interest
            ):
                violations.append(f"insufficient_open_interest:{leg.leg_id}")
            if (
                leg_reference.volume is None
                or leg_reference.volume < settings.risk.minimum_option_volume
            ):
                violations.append(f"insufficient_option_volume:{leg.leg_id}")
            if leg.expiry is None or leg.expiry <= instant.date():
                violations.append(f"invalid_option_expiry:{leg.leg_id}")
        position_key = _key(leg.security_id, leg.provider_contract_id, leg.side)
        existing_metadata = position_metadata.get(position_key)
        if existing_metadata is not None and any(
            getattr(existing_metadata, field) != getattr(leg, field)
            for field in (
                "instrument_type",
                "contract_multiplier",
                "currency",
                "option_type",
                "expiry",
                "strike",
            )
        ):
            violations.append(f"position_identity_conflict:{leg.leg_id}")
        position_quantities[position_key] = position_quantities.get(
            position_key, Decimal("0")
        ) + _quantity_delta(leg)
        position_metadata[position_key] = leg
        if position_quantities[position_key] < 0:
            violations.append(f"position_overclose:{leg.leg_id}")
        cash_delta = _cash_delta(leg, leg_reference)
        projected_cash += cash_delta
        turnover_increment += abs(cash_delta)

    variable_fees = turnover_increment * settings.orders.variable_fee_bps / Decimal("10000")
    estimated_fees = (settings.orders.fixed_fee if legs else Decimal("0")) + variable_fees
    projected_cash -= estimated_fees
    if projected_cash < 0:
        violations.append("insufficient_cash")

    projected_by_position: dict[tuple[str, str, str], Decimal] = {}
    for position_key, quantity in position_quantities.items():
        if quantity == 0:
            continue
        metadata = position_metadata[position_key]
        position_reference = reference_map.get(_reference_key(position_key[0], position_key[1]))
        if position_reference is None:
            violations.append(f"missing_position_reference:{position_key[0]}:{position_key[1]}")
            continue
        if (
            position_reference.currency != metadata.currency
            or not position_reference.price.is_finite()
            or not position_reference.fx_rate_to_base.is_finite()
            or position_reference.price <= 0
            or position_reference.fx_rate_to_base <= 0
        ):
            violations.append(f"invalid_position_reference:{position_key[0]}:{position_key[1]}")
            continue
        reference_age = instant - ensure_utc(position_reference.as_of)
        reference_freshness = (
            settings.orders.option_quote_freshness
            if metadata.instrument_type == "option"
            else settings.market_data.stale_price_after
        )
        if reference_age < timedelta(0):
            violations.append(f"future_position_reference:{position_key[0]}:{position_key[1]}")
        if reference_age > reference_freshness:
            violations.append(f"stale_position_reference:{position_key[0]}:{position_key[1]}")
        notional = (
            quantity
            * metadata.contract_multiplier
            * position_reference.price
            * position_reference.fx_rate_to_base
        )
        projected_by_position[position_key] = notional
    projected_gross = sum((abs(value) for value in projected_by_position.values()), Decimal("0"))
    projected_short = sum(
        (abs(value) for key, value in projected_by_position.items() if key[2] == "short"),
        Decimal("0"),
    )
    if state.equity_base > 0:
        single_limit = _limit(state.equity_base, settings.risk.maximum_single_position_pct)
        for key, value in projected_by_position.items():
            if abs(value) > single_limit:
                violations.append(f"single_position_limit:{key[0]}:{key[1]}")
        if projected_gross > _limit(
            state.equity_base, settings.risk.maximum_total_gross_exposure_pct
        ):
            violations.append("total_gross_exposure_limit")
        if projected_short > _limit(state.equity_base, settings.risk.maximum_short_position_pct):
            violations.append("short_exposure_limit")
        if state.daily_turnover_base + turnover_increment > _limit(
            state.equity_base, settings.risk.maximum_daily_turnover_pct
        ):
            violations.append("daily_turnover_limit")
        if len(legs) > 1 and turnover_increment > _limit(
            state.equity_base, settings.risk.maximum_pair_gross_exposure_pct
        ):
            violations.append("pair_gross_exposure_limit")
    if activates_new_strategy and (
        state.active_strategy_count + 1 > settings.risk.maximum_active_strategies
    ):
        violations.append("active_strategy_limit")
    projected_option_legs = tuple(
        OrderLegSpec(
            leg_id=f"projected-{index}",
            action="buy" if key[2] == "long" else "sell",
            side=key[2],
            instrument_type=metadata.instrument_type,
            security_id=key[0],
            provider_contract_id=key[1],
            option_type=metadata.option_type,
            expiry=metadata.expiry,
            strike=metadata.strike,
            quantity=position_quantities[key],
            contract_multiplier=metadata.contract_multiplier,
            limit_price=None,
            currency=metadata.currency,
        )
        for index, (key, metadata) in enumerate(sorted(position_metadata.items()))
        if metadata.instrument_type == "option" and position_quantities.get(key, Decimal("0")) > 0
    )
    projected_options_risk, option_violations = option_max_loss(
        projected_option_legs, reference_map
    )
    violations.extend(option_violations)
    reported_options_risk = (
        projected_options_risk if projected_options_risk is not None else state.options_risk_base
    )
    if state.equity_base > 0 and reported_options_risk > _limit(
        state.equity_base, settings.risk.maximum_options_premium_risk_pct
    ):
        violations.append("options_premium_risk_limit")
    return RiskAssessment(
        violations=tuple(sorted(set(violations))),
        projected_cash_base=projected_cash,
        projected_gross_exposure_base=projected_gross,
        projected_short_exposure_base=projected_short,
        projected_options_risk_base=reported_options_risk,
    )


def require_risk_clearance(assessment: RiskAssessment) -> None:
    """Fail closed with stable machine-readable violations."""

    if not assessment.passed:
        raise RiskRejected(";".join(assessment.violations))

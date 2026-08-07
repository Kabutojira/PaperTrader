"""Signals and normalized paper orders; neither may mutate accounting ledgers."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path, PurePosixPath

from papertrader.config import Settings
from papertrader.models import OrderLegSpec, ReferencePrice, RiskAssessment, RiskState
from papertrader.risk import assess_order_risk, require_risk_clearance
from papertrader.tables import read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    content_hash,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_iso_date,
    parse_timestamp,
    required_decimal,
    stable_id,
    utc_now,
)

SIGNAL_TYPES = frozenset({"open", "reduce", "close", "roll", "cancel"})
SIGNAL_STATUSES = frozenset({"ready", "ordered", "filled", "cancelled", "expired"})
ORDER_STATUSES = frozenset({"pending", "partially_filled", "filled", "cancelled", "expired"})
FILL_POLICIES = frozenset({"next_open", "limit_touch", "quote_mid"})


class OrderError(RuntimeError):
    """Raised when a signal or paper-order transition violates its contract."""


def _assert_paper_only(settings: Settings) -> None:
    if not settings.paper_trading_only:
        raise OrderError("paper order creation is disabled by repository configuration")


def _request_decimal(value: object, *, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, str | int | Decimal):
        raise OrderError(f"{label} must be a decimal string or integer")
    return required_decimal(value, label=label)


def _safe_request_path(value: str) -> str:
    if not value:
        return ""
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".json":
        raise OrderError(f"invalid order request path: {value!r}")
    if path.parts[:2] not in {("data", "runs"), ("data", "operations")}:
        raise OrderError("order request path must be under data/runs or data/operations")
    return path.as_posix()


def validate_leg(leg: OrderLegSpec) -> None:
    """Validate identity, quantity, option completeness, and multiplier semantics."""

    if not leg.leg_id or "|" in leg.leg_id or "\n" in leg.leg_id:
        raise OrderError("leg_id must be a non-empty single value")
    if leg.action not in {"buy", "sell"} or leg.side not in {"long", "short"}:
        raise OrderError(f"leg {leg.leg_id} has invalid action/side")
    if leg.instrument_type not in {"equity", "option"}:
        raise OrderError(f"leg {leg.leg_id} has unsupported instrument type")
    if (
        not leg.security_id
        or any(marker in leg.security_id for marker in "|\r\n")
        or any(marker in leg.provider_contract_id for marker in "|\r\n")
        or not leg.quantity.is_finite()
        or not leg.contract_multiplier.is_finite()
        or leg.quantity <= 0
        or leg.contract_multiplier <= 0
    ):
        raise OrderError(f"leg {leg.leg_id} has invalid identity, quantity, or multiplier")
    if len(leg.currency) != 3 or leg.currency != leg.currency.upper():
        raise OrderError(f"leg {leg.leg_id} currency must be an uppercase ISO code")
    if leg.limit_price is not None and (not leg.limit_price.is_finite() or leg.limit_price <= 0):
        raise OrderError(f"leg {leg.leg_id} limit price must be positive")
    if leg.instrument_type == "equity":
        if (
            leg.provider_contract_id
            or leg.option_type
            or leg.expiry is not None
            or leg.strike is not None
            or leg.contract_multiplier != 1
        ):
            raise OrderError(f"equity leg {leg.leg_id} contains option-only fields")
    else:
        if (
            not leg.provider_contract_id
            or leg.option_type not in {"call", "put"}
            or leg.expiry is None
            or leg.strike is None
            or not leg.strike.is_finite()
            or leg.strike <= 0
            or leg.quantity != leg.quantity.to_integral_value()
        ):
            raise OrderError(f"option leg {leg.leg_id} lacks complete contract identity")


def leg_from_mapping(raw: Mapping[str, object]) -> OrderLegSpec:
    """Parse a JSON-compatible order-leg request without accepting binary floats."""

    expected = {
        "leg_id",
        "action",
        "side",
        "instrument_type",
        "security_id",
        "provider_contract_id",
        "option_type",
        "expiry",
        "strike",
        "quantity",
        "contract_multiplier",
        "limit_price",
        "currency",
    }
    if set(raw) != expected:
        raise OrderError(
            f"order leg fields differ; missing={sorted(expected - set(raw))}, "
            f"extra={sorted(set(raw) - expected)}"
        )
    expiry_raw = raw["expiry"]
    strike_raw = raw["strike"]
    limit_raw = raw["limit_price"]
    leg = OrderLegSpec(
        leg_id=str(raw["leg_id"]),
        action=str(raw["action"]),
        side=str(raw["side"]),
        instrument_type=str(raw["instrument_type"]),
        security_id=str(raw["security_id"]),
        provider_contract_id=str(raw["provider_contract_id"]),
        option_type=str(raw["option_type"]),
        expiry=parse_iso_date(str(expiry_raw)) if expiry_raw else None,
        strike=_request_decimal(strike_raw, label="strike") if strike_raw != "" else None,
        quantity=_request_decimal(raw["quantity"], label="quantity"),
        contract_multiplier=_request_decimal(
            raw["contract_multiplier"], label="contract_multiplier"
        ),
        limit_price=(_request_decimal(limit_raw, label="limit_price") if limit_raw != "" else None),
        currency=str(raw["currency"]),
    )
    validate_leg(leg)
    return leg


def leg_from_row(row: Mapping[str, str]) -> OrderLegSpec:
    """Parse one canonical ``order_legs.csv`` row."""

    return leg_from_mapping(
        {
            key: row[key]
            for key in (
                "leg_id",
                "action",
                "side",
                "instrument_type",
                "security_id",
                "provider_contract_id",
                "option_type",
                "expiry",
                "strike",
                "quantity",
                "contract_multiplier",
                "limit_price",
                "currency",
            )
        }
    )


def leg_row(order_id: str, leg: OrderLegSpec) -> dict[str, str]:
    """Serialize one normalized order leg."""

    return {
        "order_id": order_id,
        "leg_id": leg.leg_id,
        "action": leg.action,
        "side": leg.side,
        "instrument_type": leg.instrument_type,
        "security_id": leg.security_id,
        "provider_contract_id": leg.provider_contract_id,
        "option_type": leg.option_type,
        "expiry": leg.expiry.isoformat() if leg.expiry else "",
        "strike": decimal_text(leg.strike) if leg.strike is not None else "",
        "quantity": decimal_text(leg.quantity),
        "contract_multiplier": decimal_text(leg.contract_multiplier),
        "limit_price": decimal_text(leg.limit_price) if leg.limit_price is not None else "",
        "currency": leg.currency,
    }


def _leg_identity(leg: OrderLegSpec) -> tuple[object, ...]:
    """Return immutable structure fields; action and quantity remain lifecycle-specific."""

    return (
        leg.leg_id,
        leg.side,
        leg.instrument_type,
        leg.security_id,
        leg.provider_contract_id,
        leg.option_type,
        leg.expiry,
        leg.strike,
        leg.contract_multiplier,
        leg.currency,
    )


def _require_canonical_strategy_legs(
    repository_root: Path,
    strategy_id: str,
    signal_type: str,
    legs: Sequence[OrderLegSpec],
) -> None:
    rows = [
        row
        for row in read_table(repository_root, "strategy_legs")
        if row["strategy_id"] == strategy_id
    ]
    if not rows:
        raise OrderError(f"strategy {strategy_id} has no canonical legs")
    canonical = tuple(sorted((leg_from_row(row) for row in rows), key=lambda leg: leg.leg_id))
    supplied = tuple(sorted(legs, key=lambda leg: leg.leg_id))
    if tuple(_leg_identity(leg) for leg in canonical) != tuple(
        _leg_identity(leg) for leg in supplied
    ):
        raise OrderError("submitted legs differ from canonical strategy leg identities")
    if signal_type == "cancel":
        raise OrderError("a cancellation signal cannot create a new order")
    for left, right in zip(canonical, supplied, strict=True):
        expected_action = left.action
        if signal_type in {"reduce", "close"}:
            expected_action = "sell" if left.action == "buy" else "buy"
        if right.action != expected_action:
            raise OrderError("submitted leg actions differ from the signal lifecycle")


def _reference_map(
    references: Sequence[ReferencePrice],
) -> dict[tuple[str, str], ReferencePrice]:
    result = {
        (reference.security_id, reference.provider_contract_id): reference
        for reference in references
    }
    if len(result) != len(references):
        raise OrderError("duplicate order references")
    return result


def _opening_notional(
    legs: Sequence[OrderLegSpec], references: Sequence[ReferencePrice]
) -> Decimal:
    by_identity = _reference_map(references)
    total = Decimal("0")
    for leg in legs:
        opens = (leg.side == "long" and leg.action == "buy") or (
            leg.side == "short" and leg.action == "sell"
        )
        if not opens:
            continue
        reference = by_identity.get((leg.security_id, leg.provider_contract_id))
        if reference is None:
            raise OrderError(f"missing reference for strategy risk budget leg {leg.leg_id}")
        total += (
            leg.quantity * leg.contract_multiplier * reference.price * reference.fx_rate_to_base
        )
    return total


def _require_sleeve_isolation(
    repository_root: Path,
    strategy: Mapping[str, str],
    legs: Sequence[OrderLegSpec],
) -> None:
    """Prevent aggregated positions from mixing baseline and conviction ownership."""

    strategies = {row["strategy_id"]: row for row in read_table(repository_root, "strategies")}
    target_sleeve = strategy["sleeve"]
    identities = {(leg.security_id, leg.provider_contract_id) for leg in legs}
    for position in read_table(repository_root, "portfolio"):
        identity = (position["security_id"], position["provider_contract_id"])
        if identity not in identities:
            continue
        for strategy_id in (part for part in position["strategy_ids"].split("|") if part):
            owner = strategies.get(strategy_id)
            if owner is None:
                raise OrderError(f"portfolio position references missing strategy {strategy_id}")
            if owner["sleeve"] != target_sleeve:
                raise OrderError("an instrument position cannot mix allocation sleeves")
    pending_orders = {
        row["order_id"]: row
        for row in read_table(repository_root, "orders")
        if row["status"] in {"pending", "partially_filled"}
    }
    for row in read_table(repository_root, "order_legs"):
        pending_order = pending_orders.get(row["order_id"])
        if pending_order is None:
            continue
        if (row["security_id"], row["provider_contract_id"]) not in identities:
            continue
        owner = strategies.get(pending_order["strategy_id"])
        if owner is None:
            raise OrderError(
                f"pending order references missing strategy {pending_order['strategy_id']}"
            )
        if owner["sleeve"] != target_sleeve:
            raise OrderError("pending instrument exposure cannot mix allocation sleeves")


def _pending_strategy_quantity(
    repository_root: Path, strategy_id: str, security_id: str
) -> Decimal:
    pending_orders = {
        row["order_id"]
        for row in read_table(repository_root, "orders")
        if row["strategy_id"] == strategy_id and row["status"] in {"pending", "partially_filled"}
    }
    executed: defaultdict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for row in read_table(repository_root, "executions"):
        if row["order_id"] in pending_orders:
            executed[(row["order_id"], row["leg_id"])] += required_decimal(
                row["quantity"], label="executed pending quantity"
            )
    quantity = Decimal("0")
    for row in read_table(repository_root, "order_legs"):
        if row["order_id"] not in pending_orders or row["security_id"] != security_id:
            continue
        leg = leg_from_row(row)
        remaining = leg.quantity - executed[(row["order_id"], row["leg_id"])]
        if remaining <= 0:
            continue
        opening = (leg.side == "long" and leg.action == "buy") or (
            leg.side == "short" and leg.action == "sell"
        )
        quantity += remaining if opening else -remaining
    return quantity


def _whole_target_quantity(target_value: Decimal, unit_value: Decimal) -> Decimal:
    """Recover an allocator-owned whole quantity without precision-edge under-sizing."""

    if target_value < 0 or unit_value <= 0:
        raise OrderError("baseline target and unit values must be non-negative")
    raw_quantity = target_value / unit_value
    nearest = raw_quantity.to_integral_value(rounding=ROUND_HALF_EVEN)
    if abs(raw_quantity - nearest) > Decimal("1e-18"):
        raise OrderError("baseline target value is not an exact whole-unit allocation")
    return nearest


def _baseline_order_legs(
    repository_root: Path,
    strategy_id: str,
    references: Sequence[ReferencePrice],
    risk_state: RiskState,
) -> tuple[OrderLegSpec, ...]:
    """Derive the exact current-plan whole-share delta for one baseline strategy."""

    strategy = next(
        (
            row
            for row in read_table(repository_root, "strategies")
            if row["strategy_id"] == strategy_id
        ),
        None,
    )
    if strategy is None or strategy["sleeve"] != "baseline":
        raise OrderError(f"strategy {strategy_id} is not a baseline strategy")
    canonical_rows = [
        row
        for row in read_table(repository_root, "strategy_legs")
        if row["strategy_id"] == strategy_id
    ]
    if len(canonical_rows) != 1:
        raise OrderError("baseline strategy requires exactly one canonical leg")
    canonical = leg_from_row(canonical_rows[0])
    if canonical.instrument_type != "equity" or canonical.side != "long":
        raise OrderError("baseline strategy requires one long equity leg")
    from papertrader.allocation import latest_allocation_target

    target = latest_allocation_target(repository_root, strategy_id)
    if target is None or target["allocation_plan_id"] != strategy["allocation_plan_id"]:
        raise OrderError("baseline strategy has no current allocation target")
    reference = _reference_map(references).get(
        (canonical.security_id, canonical.provider_contract_id)
    )
    if reference is None:
        raise OrderError("baseline order lacks its equity reference")
    unit_value = reference.price * reference.fx_rate_to_base * canonical.contract_multiplier
    if unit_value <= 0:
        raise OrderError("baseline order unit value must be positive")
    target_value = required_decimal(target["target_value_base"], label="baseline target value")
    target_quantity = _whole_target_quantity(target_value, unit_value)
    current_quantity = sum(
        (
            position.quantity
            for position in risk_state.positions
            if position.security_id == canonical.security_id
            and position.provider_contract_id == canonical.provider_contract_id
            and position.side == "long"
        ),
        Decimal("0"),
    )
    pending_quantity = _pending_strategy_quantity(
        repository_root, strategy_id, canonical.security_id
    )
    required_delta = target_quantity - current_quantity - pending_quantity
    if required_delta == 0:
        raise OrderError("baseline allocation target requires no order")
    return (
        replace(
            canonical,
            action="buy" if required_delta > 0 else "sell",
            quantity=abs(required_delta),
        ),
    )


def _require_baseline_target(
    repository_root: Path,
    settings: Settings,
    strategy: Mapping[str, str],
    signal_type: str,
    legs: Sequence[OrderLegSpec],
    references: Sequence[ReferencePrice],
    risk_state: RiskState,
    *,
    now: datetime,
) -> None:
    from papertrader.allocation import assessment_payoff_reasons, latest_allocation_target

    target = latest_allocation_target(repository_root, strategy["strategy_id"])
    if target is None or target["allocation_plan_id"] != strategy["allocation_plan_id"]:
        raise OrderError("baseline strategy has no current allocation target")
    plan_time = parse_timestamp(target["as_of"])
    assert plan_time is not None
    if plan_time > now or now - plan_time > settings.market_data.stale_price_after:
        raise OrderError("baseline allocation plan is stale or future-dated")
    if len(legs) != 1 or legs[0].instrument_type != "equity" or legs[0].side != "long":
        raise OrderError("baseline allocation supports one long equity leg")
    disposition = target["disposition"]
    expected_signal = {
        "open": "open",
        "increase": "open",
        "reduce": "reduce",
        "close": "close",
    }.get(disposition)
    if expected_signal is None or signal_type != expected_signal:
        raise OrderError("baseline order differs from its current allocation disposition")
    assessment = next(
        (
            row
            for row in read_table(repository_root, "security_assessments")
            if row["security_id"] == strategy["security_id"]
        ),
        None,
    )
    if assessment is None or assessment["assessed_at"] != target["assessment_as_of"]:
        raise OrderError("baseline order assessment is missing or superseded")
    if disposition in {"open", "increase"} and (
        assessment["hard_blockers"] or assessment["eligibility"] not in {"baseline", "conviction"}
    ):
        raise OrderError("blocked assessment cannot increase baseline exposure")
    payoff_reasons = assessment_payoff_reasons(assessment, settings)
    if disposition in {"open", "increase"} and payoff_reasons:
        raise OrderError(
            "baseline assessment fails configured payoff gates: " + "|".join(payoff_reasons)
        )
    leg = legs[0]
    reference = _reference_map(references).get((leg.security_id, leg.provider_contract_id))
    if reference is None:
        raise OrderError("baseline order lacks its fresh equity reference")
    unit_value = reference.price * reference.fx_rate_to_base * leg.contract_multiplier
    if unit_value <= 0:
        raise OrderError("baseline order unit value must be positive")
    target_value = required_decimal(target["target_value_base"], label="baseline target value")
    risk_budget = required_decimal(strategy["risk_budget_pct"], label="strategy risk budget")
    if disposition in {"open", "increase"} and target_value > (
        risk_state.equity_base * risk_budget / Decimal("100")
    ):
        raise OrderError("baseline target exceeds the strategy risk budget")
    target_quantity = _whole_target_quantity(target_value, unit_value)
    current_quantity = sum(
        (
            position.quantity
            for position in risk_state.positions
            if position.security_id == leg.security_id
            and position.provider_contract_id == leg.provider_contract_id
            and position.side == "long"
        ),
        Decimal("0"),
    )
    pending_quantity = _pending_strategy_quantity(
        repository_root, strategy["strategy_id"], leg.security_id
    )
    required_delta = target_quantity - current_quantity - pending_quantity
    expected_action = "buy" if required_delta > 0 else "sell"
    if required_delta == 0:
        raise OrderError("baseline allocation target requires no order")
    if leg.action != expected_action or leg.quantity != abs(required_delta):
        raise OrderError("baseline order quantity is not the deterministic target quantity")
    if required_decimal(target["target_weight_pct"], label="baseline target weight") > (
        settings.allocation.maximum_baseline_position_pct
    ):
        raise OrderError("baseline target exceeds the configured position cap")
    plan_rows = read_table(repository_root, "allocation_targets")
    if any(row["allocation_plan_id"] != target["allocation_plan_id"] for row in plan_rows):
        raise OrderError("current allocation targets contain multiple plans")
    planned_baseline = sum(
        (
            required_decimal(row["target_value_base"], label="baseline plan target")
            for row in plan_rows
            if row["sleeve"] == "baseline"
        ),
        Decimal("0"),
    )
    if planned_baseline > (
        risk_state.equity_base * settings.allocation.maximum_baseline_sleeve_pct / Decimal("100")
    ):
        raise OrderError("allocation plan exceeds the baseline sleeve cap")


def create_signal(
    repository_root: Path,
    settings: Settings,
    *,
    strategy_id: str,
    signal_type: str,
    rationale: str,
    market_data_as_of: datetime,
    run_id: str,
    order_request_path: str = "",
    expires_at: datetime | None = None,
    now: datetime | None = None,
) -> tuple[str, bool]:
    """Create one time-bounded decision record without touching orders or portfolio state."""

    _assert_paper_only(settings)
    if signal_type not in SIGNAL_TYPES:
        raise OrderError(f"unsupported signal type: {signal_type}")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    as_of = ensure_utc(market_data_as_of).replace(microsecond=0)
    expiry = ensure_utc(expires_at or instant + settings.orders.order_expiry).replace(microsecond=0)
    strategies = read_table(repository_root, "strategies")
    strategy = next((row for row in strategies if row["strategy_id"] == strategy_id), None)
    if strategy is None:
        raise OrderError(f"unknown strategy {strategy_id}")
    normalized_rationale = " ".join(rationale.split())
    if not normalized_rationale:
        raise OrderError("signal rationale is required")
    signal_id = stable_id(
        "signal",
        strategy_id,
        signal_type,
        format_timestamp(as_of),
        content_hash(normalized_rationale),
    )
    request_path = _safe_request_path(order_request_path)
    row = {
        "signal_id": signal_id,
        "strategy_id": strategy_id,
        "signal_type": signal_type,
        "created_at": format_timestamp(instant),
        "expires_at": format_timestamp(expiry),
        "status": "ready",
        "rationale": normalized_rationale,
        "market_data_as_of": format_timestamp(as_of),
        "order_request_path": request_path,
        "telegram_sent_at": "",
        "run_id": run_id,
    }
    rows = read_table(repository_root, "signals")
    previous = next((candidate for candidate in rows if candidate["signal_id"] == signal_id), None)
    if previous is not None:
        immutable_fields = {
            "signal_id",
            "strategy_id",
            "signal_type",
            "rationale",
            "market_data_as_of",
            "order_request_path",
        }
        expiry_mismatch = expires_at is not None and previous["expires_at"] != row["expires_at"]
        if any(previous[field] != row[field] for field in immutable_fields) or expiry_mismatch:
            raise OrderError(f"signal identity collision: {signal_id}")
        superseded = False
        for candidate in rows:
            if (
                candidate["signal_id"] != signal_id
                and candidate["strategy_id"] == strategy_id
                and candidate["status"] == "ready"
            ):
                candidate["status"] = "cancelled"
                superseded = True
        if superseded:
            write_table(repository_root, "signals", rows)
        return signal_id, False
    if as_of > instant or instant - as_of > settings.market_data.stale_price_after:
        raise OrderError("signal market data is future-dated or stale")
    if expiry <= instant:
        raise OrderError("signal expiry must follow creation")
    if strategy["status"] not in {"ready", "active"}:
        raise OrderError(f"strategy {strategy_id} is not ready or active")
    if strategy["sleeve"] == "baseline":
        from papertrader.allocation import assessment_payoff_reasons, latest_allocation_target

        target = latest_allocation_target(repository_root, strategy_id)
        if (
            target is None
            or target["allocation_plan_id"] != strategy["allocation_plan_id"]
            or target["disposition"] not in {"open", "increase", "reduce", "close"}
        ):
            raise OrderError("baseline signal requires a material current allocation target")
        expected_signal = {
            "open": "open",
            "increase": "open",
            "reduce": "reduce",
            "close": "close",
        }[target["disposition"]]
        if signal_type != expected_signal:
            raise OrderError("baseline signal type differs from its allocation disposition")
        plan_time = parse_timestamp(target["as_of"])
        assert plan_time is not None
        if instant - plan_time > settings.market_data.stale_price_after or plan_time > instant:
            raise OrderError("baseline allocation plan is stale or future-dated")
        assessment = next(
            (
                row
                for row in read_table(repository_root, "security_assessments")
                if row["security_id"] == strategy["security_id"]
            ),
            None,
        )
        if assessment is None or assessment["assessed_at"] != target["assessment_as_of"]:
            raise OrderError("baseline signal assessment is missing or superseded")
        if target["disposition"] in {"open", "increase"} and (
            assessment["hard_blockers"]
            or assessment["eligibility"] not in {"baseline", "conviction"}
        ):
            raise OrderError("blocked assessment cannot increase baseline exposure")
        payoff_reasons = assessment_payoff_reasons(assessment, settings)
        if target["disposition"] in {"open", "increase"} and payoff_reasons:
            raise OrderError(
                "baseline assessment fails configured payoff gates: " + "|".join(payoff_reasons)
            )
    for candidate in rows:
        if candidate["strategy_id"] == strategy_id and candidate["status"] == "ready":
            candidate["status"] = "cancelled"
    rows.append(row)
    rows.sort(key=lambda candidate: candidate["signal_id"])
    write_table(repository_root, "signals", rows)
    return signal_id, True


def create_baseline_paper_order(
    repository_root: Path,
    settings: Settings,
    *,
    signal_id: str,
    strategy_id: str,
    references: Sequence[ReferencePrice],
    risk_state: RiskState,
    run_id: str,
    fill_policy: str | None = None,
    order_type: str | None = None,
    limit_price: Decimal | None = None,
    not_before: datetime | None = None,
    expires_at: datetime | None = None,
    now: datetime | None = None,
) -> tuple[str, bool, RiskAssessment]:
    """Create one baseline order whose exact quantity is owned by deterministic state."""

    legs = _baseline_order_legs(repository_root, strategy_id, references, risk_state)
    return create_paper_order(
        repository_root,
        settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=legs,
        references=references,
        risk_state=risk_state,
        run_id=run_id,
        fill_policy=fill_policy,
        order_type=order_type,
        limit_price=limit_price,
        not_before=not_before,
        expires_at=expires_at,
        now=now,
    )


def create_paper_order(
    repository_root: Path,
    settings: Settings,
    *,
    signal_id: str,
    strategy_id: str,
    legs: Sequence[OrderLegSpec],
    references: Sequence[ReferencePrice],
    risk_state: RiskState,
    run_id: str,
    fill_policy: str | None = None,
    order_type: str | None = None,
    limit_price: Decimal | None = None,
    not_before: datetime | None = None,
    expires_at: datetime | None = None,
    now: datetime | None = None,
) -> tuple[str, bool, RiskAssessment]:
    """Validate and persist a pending paper order; no fill or accounting write occurs here."""

    _assert_paper_only(settings)
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    selected_fill_policy = fill_policy or settings.orders.default_fill_policy
    selected_order_type = order_type or settings.orders.default_order_type
    if selected_fill_policy not in FILL_POLICIES:
        raise OrderError(f"unsupported fill policy: {selected_fill_policy}")
    if selected_order_type not in {"market", "limit"}:
        raise OrderError(f"unsupported order type: {selected_order_type}")
    if not legs or len({leg.leg_id for leg in legs}) != len(legs):
        raise OrderError("order requires one or more uniquely identified legs")
    normalized_legs = tuple(sorted(legs, key=lambda leg: leg.leg_id))
    for leg in normalized_legs:
        validate_leg(leg)
    currencies = {leg.currency for leg in normalized_legs}
    if len(currencies) != 1:
        raise OrderError("version-1 order legs must use one currency")
    if selected_fill_policy == "next_open" and selected_order_type != "market":
        raise OrderError("next_open requires a market order")
    if selected_fill_policy == "quote_mid" and any(
        leg.instrument_type != "option" for leg in normalized_legs
    ):
        raise OrderError("quote_mid is supported only for option legs")
    if selected_fill_policy == "limit_touch" and (
        selected_order_type != "limit"
        or any(leg.limit_price is None and limit_price is None for leg in normalized_legs)
    ):
        raise OrderError("limit_touch requires a limit on every leg")
    if limit_price is not None and (not limit_price.is_finite() or limit_price <= 0):
        raise OrderError("aggregate limit price must be positive")
    start = ensure_utc(not_before or instant).replace(microsecond=0)
    expiry = ensure_utc(expires_at or instant + settings.orders.order_expiry).replace(microsecond=0)
    identity = [leg_row("", leg) for leg in normalized_legs]
    order_id = stable_id(
        "order",
        signal_id,
        strategy_id,
        selected_fill_policy,
        selected_order_type,
        content_hash(identity),
    )
    order_row = {
        "order_id": order_id,
        "signal_id": signal_id,
        "strategy_id": strategy_id,
        "created_at": format_timestamp(instant),
        "status": "pending",
        "fill_policy": selected_fill_policy,
        "not_before": format_timestamp(start),
        "expires_at": format_timestamp(expiry),
        "order_type": selected_order_type,
        "limit_price": decimal_text(limit_price) if limit_price is not None else "",
        "slippage_bps": decimal_text(settings.orders.slippage_bps),
        "fee_model": settings.orders.fee_model,
        "currency": next(iter(currencies)),
        "run_id": run_id,
    }
    orders = read_table(repository_root, "orders")
    other_for_signal = next(
        (row for row in orders if row["signal_id"] == signal_id and row["order_id"] != order_id),
        None,
    )
    if other_for_signal is not None:
        raise OrderError(f"signal {signal_id} already has order {other_for_signal['order_id']}")
    existing_order = next((row for row in orders if row["order_id"] == order_id), None)
    all_leg_rows = read_table(repository_root, "order_legs")
    expected_leg_rows = [leg_row(order_id, leg) for leg in normalized_legs]
    existing_leg_rows = [row for row in all_leg_rows if row["order_id"] == order_id]
    signals = read_table(repository_root, "signals")
    signal = next((row for row in signals if row["signal_id"] == signal_id), None)
    if signal is None or signal["strategy_id"] != strategy_id:
        raise OrderError(f"signal {signal_id} does not belong to strategy {strategy_id}")
    if existing_order is not None:
        immutable_fields = {
            "order_id",
            "signal_id",
            "strategy_id",
            "fill_policy",
            "order_type",
            "limit_price",
            "slippage_bps",
            "fee_model",
            "currency",
        }
        schedule_mismatch = (
            not_before is not None and existing_order["not_before"] != order_row["not_before"]
        ) or (expires_at is not None and existing_order["expires_at"] != order_row["expires_at"])
        if (
            any(existing_order[field] != order_row[field] for field in immutable_fields)
            or schedule_mismatch
            or existing_leg_rows != expected_leg_rows
        ):
            raise OrderError(f"order identity collision: {order_id}")
        repaired_signal_status = {
            "filled": "filled",
            "cancelled": "cancelled",
            "expired": "expired",
        }.get(existing_order["status"], "ordered")
        if signal["status"] != repaired_signal_status:
            signal["status"] = repaired_signal_status
            write_table(repository_root, "signals", signals)
        accepted = RiskAssessment(
            violations=(),
            projected_cash_base=risk_state.cash_base,
            projected_gross_exposure_base=risk_state.gross_exposure_base,
            projected_short_exposure_base=risk_state.short_exposure_base,
            projected_options_risk_base=risk_state.options_risk_base,
        )
        return order_id, False, accepted

    if signal["status"] != "ready":
        raise OrderError(f"signal {signal_id} is not ready for strategy {strategy_id}")
    if start < instant or expiry <= start:
        raise OrderError("order scheduling window is invalid")
    signal_expiry = parse_timestamp(signal["expires_at"])
    assert signal_expiry is not None
    if signal_expiry <= instant:
        raise OrderError(f"signal {signal_id} has expired")
    if expires_at is None and expiry > signal_expiry:
        expiry = signal_expiry
        order_row["expires_at"] = format_timestamp(expiry)
    if start >= signal_expiry or expiry > signal_expiry:
        raise OrderError("order scheduling window must remain inside the signal window")
    strategies = read_table(repository_root, "strategies")
    strategy = next((row for row in strategies if row["strategy_id"] == strategy_id), None)
    if strategy is None or strategy["status"] not in {"ready", "active"}:
        raise OrderError(f"strategy {strategy_id} is not orderable")
    if strategy["sleeve"] not in {"conviction", "baseline"}:
        raise OrderError(f"strategy {strategy_id} has an invalid sleeve")
    _require_sleeve_isolation(repository_root, strategy, normalized_legs)
    _require_canonical_strategy_legs(
        repository_root,
        strategy_id,
        signal["signal_type"],
        normalized_legs,
    )
    opening_notional = _opening_notional(normalized_legs, references)
    risk_budget = required_decimal(strategy["risk_budget_pct"], label="strategy risk budget")
    if opening_notional > risk_state.equity_base * risk_budget / Decimal("100"):
        raise OrderError("order exceeds the strategy risk budget")
    if strategy["sleeve"] == "baseline":
        _require_baseline_target(
            repository_root,
            settings,
            strategy,
            signal["signal_type"],
            normalized_legs,
            references,
            risk_state,
            now=instant,
        )
    venues = {
        row["security_id"]: row["venue_mic"] for row in read_table(repository_root, "securities")
    }
    assessment = assess_order_risk(
        settings,
        risk_state,
        normalized_legs,
        references,
        venues,
        now=instant,
        activates_new_strategy=strategy["status"] != "active",
    )
    require_risk_clearance(assessment)
    if strategy["sleeve"] == "baseline":
        required_reserve = (
            risk_state.equity_base * settings.allocation.minimum_cash_reserve_pct / Decimal("100")
        )
        if assessment.projected_cash_base < required_reserve:
            raise OrderError("baseline order would breach the minimum cash reserve")
    # Legs are written first so a crash cannot expose a fillable order without its full leg set.
    all_leg_rows = [row for row in all_leg_rows if row["order_id"] != order_id]
    all_leg_rows.extend(expected_leg_rows)
    all_leg_rows.sort(key=lambda row: (row["order_id"], row["leg_id"]))
    write_table(repository_root, "order_legs", all_leg_rows)
    orders.append(order_row)
    orders.sort(key=lambda row: row["order_id"])
    write_table(repository_root, "orders", orders)
    for row in signals:
        if row["signal_id"] == signal_id:
            row["status"] = "ordered"
    write_table(repository_root, "signals", signals)
    return order_id, True, assessment


def _canonical_row_timestamp(
    value: str, *, label: str, allow_empty: bool = False
) -> datetime | None:
    parsed = parse_timestamp(value, allow_empty=allow_empty)
    if parsed is not None and value != format_timestamp(parsed):
        raise OrderError(f"{label} must use canonical UTC form")
    return parsed


def validate_order_state(repository_root: Path) -> list[str]:
    """Validate signal, order, leg, and execution identities and lifecycle links."""

    try:
        signals = read_table(repository_root, "signals")
        orders = read_table(repository_root, "orders")
        leg_rows = read_table(repository_root, "order_legs")
        executions = read_table(repository_root, "executions")
        strategies = read_table(repository_root, "strategies")
        securities = read_table(repository_root, "securities")
    except (CanonicalValueError, OSError) as exc:
        return [str(exc)]
    errors: list[str] = []
    strategy_ids = {row["strategy_id"] for row in strategies}
    security_ids = {row["security_id"] for row in securities}
    signal_by_id: dict[str, dict[str, str]] = {}
    for row in signals:
        signal_id = row["signal_id"]
        if signal_id in signal_by_id:
            errors.append(f"duplicate signal_id: {signal_id}")
            continue
        signal_by_id[signal_id] = row
        try:
            created = _canonical_row_timestamp(row["created_at"], label="signal created_at")
            expiry = _canonical_row_timestamp(row["expires_at"], label="signal expires_at")
            market_as_of = _canonical_row_timestamp(
                row["market_data_as_of"], label="signal market_data_as_of"
            )
            _canonical_row_timestamp(
                row["telegram_sent_at"],
                label="signal telegram_sent_at",
                allow_empty=True,
            )
            assert created is not None and expiry is not None and market_as_of is not None
            if row["status"] not in SIGNAL_STATUSES or row["signal_type"] not in SIGNAL_TYPES:
                raise OrderError(f"signal {signal_id} has an invalid status or type")
            if row["strategy_id"] not in strategy_ids:
                raise OrderError(f"signal {signal_id} references a missing strategy")
            if market_as_of > created or expiry <= created:
                raise OrderError(f"signal {signal_id} has an invalid time window")
            _safe_request_path(row["order_request_path"])
            expected_id = stable_id(
                "signal",
                row["strategy_id"],
                row["signal_type"],
                row["market_data_as_of"],
                content_hash(row["rationale"]),
            )
            if signal_id != expected_id:
                raise OrderError(f"signal identity is invalid: {signal_id}")
        except (CanonicalValueError, OrderError, AssertionError) as exc:
            errors.append(str(exc))

    order_by_id: dict[str, dict[str, str]] = {}
    order_by_signal: dict[str, str] = {}
    for row in orders:
        order_id = row["order_id"]
        if order_id in order_by_id:
            errors.append(f"duplicate order_id: {order_id}")
            continue
        order_by_id[order_id] = row
        prior_order = order_by_signal.get(row["signal_id"])
        if prior_order is not None:
            errors.append(f"signal {row['signal_id']} has multiple orders")
        order_by_signal[row["signal_id"]] = order_id

    legs_by_order: dict[str, list[OrderLegSpec]] = {}
    seen_leg_keys: set[tuple[str, str]] = set()
    for row in leg_rows:
        key = (row["order_id"], row["leg_id"])
        if key in seen_leg_keys:
            errors.append(f"duplicate order leg: {key!r}")
            continue
        seen_leg_keys.add(key)
        if row["order_id"] not in order_by_id:
            errors.append(f"orphan order leg: {key!r}")
        try:
            leg = leg_from_row(row)
            if leg.security_id not in security_ids:
                raise OrderError(f"order leg {key!r} references a missing security")
            legs_by_order.setdefault(row["order_id"], []).append(leg)
        except (CanonicalValueError, OrderError) as exc:
            errors.append(str(exc))

    execution_legs: dict[str, set[str]] = {}
    for row in executions:
        key = (row["order_id"], row["leg_id"])
        if row["order_id"] not in order_by_id:
            errors.append(f"execution {row['execution_id']} references a missing order")
        if key not in seen_leg_keys:
            errors.append(f"execution {row['execution_id']} references a missing order leg")
        if row["leg_id"] in execution_legs.setdefault(row["order_id"], set()):
            errors.append(f"order {row['order_id']} has multiple executions for one leg")
        execution_legs[row["order_id"]].add(row["leg_id"])

    for order_id, row in order_by_id.items():
        try:
            created = _canonical_row_timestamp(row["created_at"], label="order created_at")
            start = _canonical_row_timestamp(row["not_before"], label="order not_before")
            expiry = _canonical_row_timestamp(row["expires_at"], label="order expires_at")
            assert created is not None and start is not None and expiry is not None
            signal = signal_by_id.get(row["signal_id"])
            if signal is None or signal["strategy_id"] != row["strategy_id"]:
                raise OrderError(f"order {order_id} conflicts with its signal")
            signal_created = parse_timestamp(signal["created_at"])
            signal_expiry = parse_timestamp(signal["expires_at"])
            assert signal_created is not None and signal_expiry is not None
            if (
                created < signal_created
                or start < created
                or expiry <= start
                or expiry > signal_expiry
            ):
                raise OrderError(f"order {order_id} has an invalid time window")
            if row["status"] not in ORDER_STATUSES or row["fill_policy"] not in FILL_POLICIES:
                raise OrderError(f"order {order_id} has an invalid status or fill policy")
            if row["order_type"] not in {"market", "limit"}:
                raise OrderError(f"order {order_id} has an invalid order type")
            aggregate_limit = (
                required_decimal(row["limit_price"], label="order limit")
                if row["limit_price"]
                else None
            )
            if aggregate_limit is not None and aggregate_limit <= 0:
                raise OrderError(f"order {order_id} has a non-positive limit")
            slippage = required_decimal(row["slippage_bps"], label="order slippage")
            if slippage < 0:
                raise OrderError(f"order {order_id} has negative slippage")
            normalized_legs = sorted(legs_by_order.get(order_id, []), key=lambda leg: leg.leg_id)
            if not normalized_legs:
                raise OrderError(f"order {order_id} has no legs")
            if {leg.currency for leg in normalized_legs} != {row["currency"]}:
                raise OrderError(f"order {order_id} currency differs from its legs")
            if row["fill_policy"] == "next_open" and row["order_type"] != "market":
                raise OrderError(f"next-open order {order_id} is not a market order")
            if row["fill_policy"] == "quote_mid" and any(
                leg.instrument_type != "option" for leg in normalized_legs
            ):
                raise OrderError(f"quote-mid order {order_id} contains a non-option leg")
            if row["fill_policy"] == "limit_touch" and (
                row["order_type"] != "limit"
                or any(
                    leg.limit_price is None and aggregate_limit is None for leg in normalized_legs
                )
            ):
                raise OrderError(f"limit-touch order {order_id} lacks a limit")
            identity = [leg_row("", leg) for leg in normalized_legs]
            expected_id = stable_id(
                "order",
                row["signal_id"],
                row["strategy_id"],
                row["fill_policy"],
                row["order_type"],
                content_hash(identity),
            )
            if order_id != expected_id:
                raise OrderError(f"order identity is invalid: {order_id}")
            filled_legs = execution_legs.get(order_id, set())
            all_leg_ids = {leg.leg_id for leg in normalized_legs}
            if row["status"] == "filled" and filled_legs != all_leg_ids:
                raise OrderError(f"filled order {order_id} lacks executions")
            if row["status"] == "partially_filled" and not (
                filled_legs and filled_legs < all_leg_ids
            ):
                raise OrderError(f"partially filled order {order_id} has inconsistent executions")
            if row["status"] in {"pending", "cancelled", "expired"} and filled_legs:
                raise OrderError(f"unfilled order {order_id} has executions")
            expected_signal_status = {
                "pending": "ordered",
                "partially_filled": "ordered",
                "filled": "filled",
                "cancelled": "cancelled",
                "expired": "expired",
            }[row["status"]]
            if signal["status"] != expected_signal_status:
                raise OrderError(f"order {order_id} and signal statuses differ")
        except (CanonicalValueError, OrderError, AssertionError) as exc:
            errors.append(str(exc))
    return errors


def update_order_status(repository_root: Path, order_id: str, status: str) -> None:
    """Update only the mutable order state after deterministic fill/cancel processing."""

    if status not in ORDER_STATUSES:
        raise OrderError(f"invalid order status: {status}")
    rows = read_table(repository_root, "orders")
    found = False
    for row in rows:
        if row["order_id"] == order_id:
            row["status"] = status
            found = True
    if not found:
        raise OrderError(f"unknown order: {order_id}")
    write_table(repository_root, "orders", rows)


def update_signal_status(repository_root: Path, signal_id: str, status: str) -> None:
    """Update only the mutable lifecycle state of an existing signal."""

    if status not in SIGNAL_STATUSES:
        raise OrderError(f"invalid signal status: {status}")
    rows = read_table(repository_root, "signals")
    found = False
    for row in rows:
        if row["signal_id"] == signal_id:
            row["status"] = status
            found = True
    if not found:
        raise OrderError(f"unknown signal: {signal_id}")
    write_table(repository_root, "signals", rows)


def cancel_paper_order(repository_root: Path, order_id: str) -> None:
    """Cancel an unfilled paper order without fabricating any accounting entry."""

    rows = read_table(repository_root, "orders")
    order = next((row for row in rows if row["order_id"] == order_id), None)
    if order is None or order["status"] != "pending":
        raise OrderError(f"order {order_id} is not pending")
    update_order_status(repository_root, order_id, "cancelled")
    update_signal_status(repository_root, order["signal_id"], "cancelled")


def cancel_unauthorized_baseline_orders(
    repository_root: Path,
    settings: Settings,
    *,
    now: datetime,
) -> tuple[tuple[str, str], ...]:
    """Cancel pending baseline entries that the latest canonical state no longer authorizes.

    Fill processing calls this immediately before selecting any market bar.  It closes the
    timing gap between allocation/assessment changes and a previously-created next-open order,
    while leaving conviction and reduction orders untouched.
    """

    from papertrader.allocation import assessment_payoff_reasons, latest_allocation_target

    instant = ensure_utc(now)
    strategies = {row["strategy_id"]: row for row in read_table(repository_root, "strategies")}
    assessments = {
        row["security_id"]: row for row in read_table(repository_root, "security_assessments")
    }
    legs_by_order: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_table(repository_root, "order_legs"):
        legs_by_order[row["order_id"]].append(row)
    cancelled: list[tuple[str, str]] = []
    for order in sorted(read_table(repository_root, "orders"), key=lambda row: row["order_id"]):
        if order["status"] != "pending":
            continue
        strategy = strategies.get(order["strategy_id"])
        if strategy is None or strategy["sleeve"] != "baseline":
            continue
        order_legs = legs_by_order.get(order["order_id"], [])
        opening_buy = bool(order_legs) and all(
            leg["instrument_type"] == "equity" and leg["side"] == "long" and leg["action"] == "buy"
            for leg in order_legs
        )
        if not opening_buy:
            continue
        reason = ""
        target = latest_allocation_target(repository_root, strategy["strategy_id"])
        if strategy["status"] not in {"ready", "active"}:
            reason = "strategy_not_active"
        elif target is None or target["allocation_plan_id"] != strategy["allocation_plan_id"]:
            reason = "allocation_plan_superseded"
        elif target["disposition"] not in {"open", "increase", "hold"}:
            reason = f"allocation_disposition_{target['disposition']}"
        else:
            plan_time = parse_timestamp(target["as_of"])
            if (
                plan_time is None
                or plan_time > instant
                or instant - plan_time > settings.market_data.stale_price_after
            ):
                reason = "allocation_plan_stale"
            else:
                assessment = assessments.get(strategy["security_id"])
                if assessment is None or assessment["assessed_at"] != target["assessment_as_of"]:
                    reason = "assessment_superseded"
                elif assessment["hard_blockers"]:
                    reason = "assessment_hard_blocked"
                elif assessment["eligibility"] not in {"baseline", "conviction"}:
                    reason = "assessment_ineligible"
                else:
                    payoff_reasons = assessment_payoff_reasons(assessment, settings)
                    if payoff_reasons:
                        reason = "payoff_gate_" + "_and_".join(payoff_reasons)
        if reason:
            cancel_paper_order(repository_root, order["order_id"])
            cancelled.append((order["order_id"], reason))
    return tuple(cancelled)

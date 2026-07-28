"""Ledger replay, generated positions, risk snapshots, and exact reconciliation."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import cast

from papertrader.execution import cash_rows_for_execution
from papertrader.models import OrderLegSpec, PositionMark, ReferencePrice, RiskPosition, RiskState
from papertrader.orders import leg_from_row
from papertrader.tables import read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_iso_date,
    parse_timestamp,
    required_decimal,
    stable_id,
)


class PortfolioError(RuntimeError):
    """Raised when immutable accounting records cannot be reconciled."""


@dataclass(slots=True)
class _Position:
    security_id: str
    provider_contract_id: str
    instrument_type: str
    side: str
    currency: str
    contract_multiplier: Decimal
    option_type: str
    expiry: date | None
    strike: Decimal | None
    quantity: Decimal = Decimal("0")
    local_basis: Decimal = Decimal("0")
    base_basis: Decimal = Decimal("0")
    realized_base: Decimal = Decimal("0")
    opened_at: datetime | None = None
    strategy_ids: set[str] = field(default_factory=set)


@dataclass(frozen=True, slots=True)
class AccountingReplay:
    """Complete deterministic replay result before marks are rendered."""

    positions: tuple[_Position, ...]
    realized_pnl_base: Decimal
    cash_base: Decimal


def _parse_actions(repository_root: Path) -> list[dict[str, object]]:
    actions: list[dict[str, object]] = []
    for row in read_table(repository_root, "corporate_actions"):
        action_type = row["action_type"]
        if action_type not in {"split", "dividend"}:
            raise PortfolioError(f"unsupported corporate action: {action_type}")
        value = required_decimal(row["value"], label="corporate action value")
        if value <= 0:
            raise PortfolioError(f"corporate action {row['corporate_action_id']} is non-positive")
        action_date = parse_iso_date(row["action_date"])
        expected_id = stable_id("action", row["security_id"], action_date, action_type)
        if row["corporate_action_id"] != expected_id:
            raise PortfolioError(
                f"corporate action identity is invalid: {row['corporate_action_id']}"
            )
        if len(row["currency"]) != 3 or row["currency"] != row["currency"].upper():
            raise PortfolioError(
                f"corporate action {row['corporate_action_id']} has invalid currency"
            )
        if not row["source"] or not re.fullmatch(r"[a-f0-9]{64}", row["source_price_hash"]):
            raise PortfolioError(
                f"corporate action {row['corporate_action_id']} lacks valid provenance"
            )
        parse_timestamp(row["recorded_at"])
        actions.append(
            {
                "id": row["corporate_action_id"],
                "security_id": row["security_id"],
                "date": action_date,
                "type": action_type,
                "value": value,
            }
        )
    return actions


def _cash_total(repository_root: Path) -> Decimal:
    total = Decimal("0")
    seen: set[str] = set()
    allowed_types = {
        "initial_capital",
        "buy",
        "sell",
        "fee",
        "dividend",
        "interest",
        "correction",
        "capital_contribution",
        "capital_withdrawal",
    }
    for row in read_table(repository_root, "cash_ledger"):
        if row["cash_entry_id"] in seen:
            raise PortfolioError(f"duplicate cash entry: {row['cash_entry_id']}")
        seen.add(row["cash_entry_id"])
        if row["entry_type"] not in allowed_types:
            raise PortfolioError(
                f"cash entry {row['cash_entry_id']} has unsupported type {row['entry_type']!r}"
            )
        parse_timestamp(row["occurred_at"])
        if len(row["currency"]) != 3 or row["currency"] != row["currency"].upper():
            raise PortfolioError(f"cash entry {row['cash_entry_id']} has invalid currency")
        amount = required_decimal(row["amount"], label="cash amount")
        fx_rate = required_decimal(row["fx_rate_to_base"], label="cash fx rate")
        base_amount = required_decimal(row["base_amount"], label="cash base amount")
        if fx_rate <= 0 or amount * fx_rate != base_amount:
            raise PortfolioError(f"cash entry {row['cash_entry_id']} has inconsistent FX math")
        total += base_amount
    return total


def replay_accounting(repository_root: Path) -> AccountingReplay:
    """Replay executions and durable splits; no generated CSV is used as input."""

    order_leg_rows = read_table(repository_root, "order_legs")
    legs = {(row["order_id"], row["leg_id"]): leg_from_row(row) for row in order_leg_rows}
    if len(legs) != len(order_leg_rows):
        raise PortfolioError("duplicate order leg identity")
    order_rows = read_table(repository_root, "orders")
    strategy_by_order = {row["order_id"]: row["strategy_id"] for row in order_rows}
    if len(strategy_by_order) != len(order_rows):
        raise PortfolioError("duplicate order identity")
    events: list[tuple[datetime, int, str, Mapping[str, object] | Mapping[str, str]]] = []
    for action in _parse_actions(repository_root):
        event_time = datetime.combine(action["date"], time.min, UTC)  # type: ignore[arg-type]
        events.append((event_time, 0, str(action["id"]), action))
    execution_rows = read_table(repository_root, "executions")
    seen_execution_ids: set[str] = set()
    for row in execution_rows:
        if row["execution_id"] in seen_execution_ids:
            raise PortfolioError(f"duplicate execution: {row['execution_id']}")
        seen_execution_ids.add(row["execution_id"])
        executed_at = parse_timestamp(row["executed_at"])
        source_time = parse_timestamp(row["source_bar_time"])
        assert executed_at is not None and source_time is not None
        expected_execution_id = stable_id("execution", row["order_id"], row["leg_id"])
        if row["execution_id"] != expected_execution_id:
            raise PortfolioError(f"execution identity is invalid: {row['execution_id']}")
        if executed_at != source_time:
            raise PortfolioError(
                f"execution {row['execution_id']} time differs from its fill source"
            )
        events.append((executed_at, 1, row["execution_id"], row))
    events.sort(key=lambda event: (event[0], event[1], event[2]))
    positions: dict[tuple[str, str, str], _Position] = {}
    for event_time, kind, _, raw in events:
        if kind == 0:
            if raw["type"] != "split":
                continue
            security_id = str(raw["security_id"])
            factor = raw["value"]
            assert isinstance(factor, Decimal)
            for position in positions.values():
                if position.security_id != security_id or position.quantity == 0:
                    continue
                if position.instrument_type != "equity":
                    raise PortfolioError(
                        f"split for {security_id} requires explicit option contract adjustment"
                    )
                position.quantity *= factor
            continue
        execution = cast(Mapping[str, str], raw)
        order_id = execution["order_id"]
        leg_id = execution["leg_id"]
        leg = legs.get((order_id, leg_id))
        if leg is None:
            raise PortfolioError(f"execution {execution['execution_id']} has no order leg")
        if (
            execution["security_id"] != leg.security_id
            or execution["provider_contract_id"] != leg.provider_contract_id
            or execution["side"] != leg.action
            or execution["currency"] != leg.currency
        ):
            raise PortfolioError(
                f"execution {execution['execution_id']} conflicts with its order leg"
            )
        quantity = required_decimal(execution["quantity"], label="execution quantity")
        price = required_decimal(execution["fill_price"], label="execution price")
        multiplier = required_decimal(
            execution["contract_multiplier"], label="execution multiplier"
        )
        fees = required_decimal(execution["fees"], label="execution fees")
        fx_rate = required_decimal(execution["fx_rate_to_base"], label="execution FX")
        if (
            quantity <= 0
            or price <= 0
            or multiplier != leg.contract_multiplier
            or fees < 0
            or fx_rate <= 0
        ):
            raise PortfolioError(
                f"execution {execution['execution_id']} has invalid numeric values"
            )
        gross = quantity * price * multiplier
        expected_cash = -gross if leg.action == "buy" else gross
        if required_decimal(execution["cash_effect"], label="cash effect") != expected_cash:
            raise PortfolioError(
                f"execution {execution['execution_id']} cash effect is inconsistent"
            )
        position_key = (leg.security_id, leg.provider_contract_id, leg.side)
        current_position = positions.get(position_key)
        if current_position is None:
            current_position = _Position(
                security_id=leg.security_id,
                provider_contract_id=leg.provider_contract_id,
                instrument_type=leg.instrument_type,
                side=leg.side,
                currency=leg.currency,
                contract_multiplier=leg.contract_multiplier,
                option_type=leg.option_type,
                expiry=leg.expiry,
                strike=leg.strike,
            )
            positions[position_key] = current_position
        if (
            current_position.instrument_type != leg.instrument_type
            or current_position.currency != leg.currency
            or current_position.contract_multiplier != multiplier
            or current_position.option_type != leg.option_type
            or current_position.expiry != leg.expiry
            or current_position.strike != leg.strike
        ):
            raise PortfolioError(
                f"position identity changed for execution {execution['execution_id']}"
            )
        strategy_id = strategy_by_order.get(order_id)
        if strategy_id is None:
            raise PortfolioError(f"execution {execution['execution_id']} references missing order")
        current_position.strategy_ids.add(strategy_id)
        opening = (leg.side == "long" and leg.action == "buy") or (
            leg.side == "short" and leg.action == "sell"
        )
        if opening:
            if current_position.quantity == 0:
                current_position.opened_at = event_time
                current_position.local_basis = Decimal("0")
                current_position.base_basis = Decimal("0")
            basis = gross + fees if leg.side == "long" else gross - fees
            if basis < 0:
                raise PortfolioError(f"fees exceed proceeds in {execution['execution_id']}")
            current_position.quantity += quantity
            current_position.local_basis += basis
            current_position.base_basis += basis * fx_rate
            continue
        if current_position.quantity <= 0 or quantity > current_position.quantity:
            raise PortfolioError(f"execution {execution['execution_id']} over-closes its position")
        fraction = quantity / current_position.quantity
        allocated_local_basis = current_position.local_basis * fraction
        allocated_base_basis = current_position.base_basis * fraction
        close_value = gross - fees if leg.side == "long" else gross + fees
        close_value_base = close_value * fx_rate
        if leg.side == "long":
            current_position.realized_base += close_value_base - allocated_base_basis
        else:
            current_position.realized_base += allocated_base_basis - close_value_base
        current_position.quantity -= quantity
        current_position.local_basis -= allocated_local_basis
        current_position.base_basis -= allocated_base_basis
        if current_position.quantity == 0:
            current_position.local_basis = Decimal("0")
            current_position.base_basis = Decimal("0")
            current_position.opened_at = None
    ordered = tuple(
        positions[key]
        for key in sorted(positions)
        if positions[key].quantity != 0 or positions[key].realized_base != 0
    )
    realized = sum((position.realized_base for position in positions.values()), Decimal("0"))
    return AccountingReplay(
        positions=ordered, realized_pnl_base=realized, cash_base=_cash_total(repository_root)
    )


def _mark_map(marks: Sequence[PositionMark]) -> dict[tuple[str, str], PositionMark]:
    result: dict[tuple[str, str], PositionMark] = {}
    for mark in marks:
        key = (mark.security_id, mark.provider_contract_id)
        if key in result:
            raise PortfolioError(f"duplicate mark: {key!r}")
        if (
            not mark.price.is_finite()
            or not mark.fx_rate_to_base.is_finite()
            or mark.price <= 0
            or mark.fx_rate_to_base <= 0
        ):
            raise PortfolioError(f"non-positive mark or FX: {key!r}")
        if mark.marked_at.tzinfo is None or mark.marked_at.utcoffset() is None:
            raise PortfolioError(f"mark must be timezone-aware: {key!r}")
        result[key] = mark
    return result


def _portfolio_rows(
    replay: AccountingReplay,
    marks: Sequence[PositionMark],
    *,
    as_of: datetime,
) -> list[dict[str, str]]:
    mark_by_key = _mark_map(marks)
    normalized_as_of = ensure_utc(as_of)
    output: list[dict[str, str]] = []
    for position in replay.positions:
        if position.quantity == 0:
            continue
        key = (position.security_id, position.provider_contract_id)
        mark = mark_by_key.get(key)
        if mark is None:
            raise PortfolioError(f"missing current mark for {key!r}")
        if mark.currency != position.currency or ensure_utc(mark.marked_at) > normalized_as_of:
            raise PortfolioError(f"mark identity/time mismatch for {key!r}")
        unsigned_value = (
            position.quantity * position.contract_multiplier * mark.price * mark.fx_rate_to_base
        )
        market_value = unsigned_value if position.side == "long" else -unsigned_value
        unrealized = (
            unsigned_value - position.base_basis
            if position.side == "long"
            else position.base_basis - unsigned_value
        )
        average_cost = position.local_basis / (position.quantity * position.contract_multiplier)
        assert position.opened_at is not None
        output.append(
            {
                "position_id": stable_id(
                    "position",
                    position.security_id,
                    position.provider_contract_id,
                    position.side,
                ),
                "security_id": position.security_id,
                "provider_contract_id": position.provider_contract_id,
                "instrument_type": position.instrument_type,
                "side": position.side,
                "quantity": decimal_text(position.quantity),
                "average_cost": decimal_text(average_cost),
                "currency": position.currency,
                "current_price": decimal_text(mark.price),
                "market_value_base": decimal_text(market_value),
                "unrealized_pnl_base": decimal_text(unrealized),
                "realized_pnl_base": decimal_text(position.realized_base),
                "opened_at": format_timestamp(position.opened_at),
                "last_mark_at": format_timestamp(mark.marked_at),
                "strategy_ids": "|".join(sorted(position.strategy_ids)),
            }
        )
    output.sort(key=lambda row: row["position_id"])
    return output


def rebuild_portfolio(
    repository_root: Path,
    *,
    marks: Sequence[PositionMark],
    run_id: str,
    as_of: datetime,
) -> list[dict[str, str]]:
    """Regenerate portfolio entirely from immutable state and current marks."""

    del run_id  # provenance is carried by executions, cash rows, and performance.
    replay = replay_accounting(repository_root)
    rows = _portfolio_rows(replay, marks, as_of=as_of)
    write_table(repository_root, "portfolio", rows)
    return rows


def build_risk_state(
    repository_root: Path,
    references: Sequence[ReferencePrice],
    *,
    as_of: datetime,
) -> RiskState:
    """Build a pre-order state snapshot from ledgers plus supplied fresh reference prices."""

    instant = ensure_utc(as_of)
    replay = replay_accounting(repository_root)
    reference_map = {
        (reference.security_id, reference.provider_contract_id): reference
        for reference in references
    }
    if len(reference_map) != len(references):
        raise PortfolioError("duplicate risk reference")
    risk_positions: list[RiskPosition] = []
    gross = Decimal("0")
    short = Decimal("0")
    signed_market_value = Decimal("0")
    for position in replay.positions:
        if position.quantity == 0:
            continue
        key = (position.security_id, position.provider_contract_id)
        reference = reference_map.get(key)
        if (
            reference is None
            or reference.currency != position.currency
            or not reference.price.is_finite()
            or not reference.fx_rate_to_base.is_finite()
            or reference.price <= 0
            or reference.fx_rate_to_base <= 0
            or ensure_utc(reference.as_of) > instant
        ):
            raise PortfolioError(f"missing risk reference for {key!r}")
        value = (
            position.quantity
            * position.contract_multiplier
            * reference.price
            * reference.fx_rate_to_base
        )
        gross += abs(value)
        signed_market_value += value if position.side == "long" else -value
        if position.side == "short":
            short += abs(value)
        risk_positions.append(
            RiskPosition(
                security_id=position.security_id,
                provider_contract_id=position.provider_contract_id,
                side=position.side,
                instrument_type=position.instrument_type,
                quantity=position.quantity,
                contract_multiplier=position.contract_multiplier,
                currency=position.currency,
                option_type=position.option_type,
                expiry=position.expiry,
                strike=position.strike,
            )
        )
    from papertrader.risk import option_max_loss

    option_legs = tuple(
        OrderLegSpec(
            leg_id=f"position-{index}",
            action="buy" if position.side == "long" else "sell",
            side=position.side,
            instrument_type=position.instrument_type,
            security_id=position.security_id,
            provider_contract_id=position.provider_contract_id,
            option_type=position.option_type,
            expiry=position.expiry,
            strike=position.strike,
            quantity=position.quantity,
            contract_multiplier=position.contract_multiplier,
            limit_price=None,
            currency=position.currency,
        )
        for index, position in enumerate(risk_positions)
        if position.instrument_type == "option"
    )
    option_risk, option_violations = option_max_loss(option_legs, reference_map)
    if option_violations or option_risk is None:
        raise PortfolioError(
            "existing option positions are not bounded: " + ";".join(option_violations)
        )
    options_risk = option_risk
    turnover = Decimal("0")
    for row in read_table(repository_root, "executions"):
        executed = parse_timestamp(row["executed_at"])
        assert executed is not None
        if executed.date() == instant.date():
            turnover += abs(
                required_decimal(row["cash_effect"], label="cash effect")
                * required_decimal(row["fx_rate_to_base"], label="execution FX")
            )
    active_strategies = sum(
        1 for row in read_table(repository_root, "strategies") if row["status"] == "active"
    )
    return RiskState(
        equity_base=replay.cash_base + signed_market_value,
        cash_base=replay.cash_base,
        gross_exposure_base=gross,
        short_exposure_base=short,
        options_risk_base=options_risk,
        daily_turnover_base=turnover,
        active_strategy_count=active_strategies,
        positions=tuple(risk_positions),
    )


def _reconcile_execution_cash(repository_root: Path) -> list[str]:
    errors: list[str] = []
    executions = read_table(repository_root, "executions")
    cash = read_table(repository_root, "cash_ledger")
    cash_by_id = {row["cash_entry_id"]: row for row in cash}
    execution_ids = {row["execution_id"] for row in executions}
    for execution in executions:
        for expected in cash_rows_for_execution(execution):
            actual = cash_by_id.get(expected["cash_entry_id"])
            if actual is None:
                errors.append(
                    f"execution {execution['execution_id']} lacks cash entry "
                    f"{expected['cash_entry_id']}"
                )
            elif actual != expected:
                errors.append(
                    f"cash entry {expected['cash_entry_id']} differs from execution-derived value"
                )
    for row in cash:
        if row["entry_type"] in {"buy", "sell", "fee"} and row["reference_id"] not in execution_ids:
            errors.append(f"cash entry {row['cash_entry_id']} references no execution")
    return errors


def reconcile_portfolio(repository_root: Path) -> list[str]:
    """Validate ledgers, corporate actions, cash linkage, and generated position arithmetic."""

    try:
        errors = _reconcile_execution_cash(repository_root)
        replay = replay_accounting(repository_root)
        actual = read_table(repository_root, "portfolio")
    except (CanonicalValueError, PortfolioError, OSError) as exc:
        return [str(exc)]
    actual_by_identity = {
        (row["security_id"], row["provider_contract_id"], row["side"]): row for row in actual
    }
    if len(actual_by_identity) != len(actual):
        errors.append("portfolio contains duplicate position identities")
    open_positions = [position for position in replay.positions if position.quantity != 0]
    expected_keys = {
        (position.security_id, position.provider_contract_id, position.side)
        for position in open_positions
    }
    if set(actual_by_identity) != expected_keys:
        errors.append(
            "portfolio identities differ from ledger replay: "
            f"expected={sorted(expected_keys)}, actual={sorted(actual_by_identity)}"
        )
        return errors
    for position in open_positions:
        key = (position.security_id, position.provider_contract_id, position.side)
        row = actual_by_identity[key]
        try:
            quantity = required_decimal(row["quantity"], label="portfolio quantity")
            average_cost = required_decimal(row["average_cost"], label="portfolio average cost")
            current_price = required_decimal(row["current_price"], label="portfolio price")
            market_value = required_decimal(
                row["market_value_base"], label="portfolio market value"
            )
            unrealized = required_decimal(row["unrealized_pnl_base"], label="portfolio unrealized")
            realized = required_decimal(row["realized_pnl_base"], label="portfolio realized")
            opened_at = parse_timestamp(row["opened_at"])
            last_mark_at = parse_timestamp(row["last_mark_at"])
            assert opened_at is not None and last_mark_at is not None
        except (CanonicalValueError, AssertionError) as exc:
            errors.append(f"portfolio values are invalid for {key!r}: {exc}")
            continue
        expected_position_id = stable_id(
            "position",
            position.security_id,
            position.provider_contract_id,
            position.side,
        )
        if row["position_id"] != expected_position_id:
            errors.append(f"portfolio position_id differs for {key!r}")
        if row["instrument_type"] != position.instrument_type:
            errors.append(f"portfolio instrument type differs for {key!r}")
        if row["currency"] != position.currency:
            errors.append(f"portfolio currency differs for {key!r}")
        if opened_at != position.opened_at:
            errors.append(f"portfolio opened_at differs for {key!r}")
        if last_mark_at < opened_at:
            errors.append(f"portfolio mark predates position open for {key!r}")
        expected_strategies = "|".join(sorted(position.strategy_ids))
        if row["strategy_ids"] != expected_strategies:
            errors.append(f"portfolio strategy_ids differ for {key!r}")
        if quantity != position.quantity:
            errors.append(f"portfolio quantity differs for {key!r}")
        expected_average = position.local_basis / (position.quantity * position.contract_multiplier)
        if average_cost != expected_average:
            errors.append(f"portfolio average cost differs for {key!r}")
        # Infer the effective generated FX from market value and verify P/L identities.
        local_value = position.quantity * position.contract_multiplier * current_price
        if local_value <= 0:
            errors.append(f"portfolio mark is non-positive for {key!r}")
            continue
        signed_unsigned = market_value if position.side == "long" else -market_value
        if signed_unsigned <= 0:
            errors.append(f"portfolio market value sign differs for {key!r}")
            continue
        expected_unrealized = (
            signed_unsigned - position.base_basis
            if position.side == "long"
            else position.base_basis - signed_unsigned
        )
        if unrealized != expected_unrealized:
            errors.append(f"portfolio unrealized P/L differs for {key!r}")
        if realized != position.realized_base:
            errors.append(f"portfolio realized P/L differs for {key!r}")
    return errors

"""Corporate-action extraction and Decimal-safe split/dividend primitives."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from decimal import Decimal
from pathlib import Path

from papertrader.models import PriceBar
from papertrader.orders import leg_from_row
from papertrader.tables import append_unique, read_table
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    format_timestamp,
    parse_iso_date,
    parse_timestamp,
    required_decimal,
    stable_id,
)


@dataclass(frozen=True, slots=True)
class CorporateAction:
    """A normalized provider action retained in the canonical rolling price cache."""

    security_id: str
    action_date: date
    action_type: str
    value: Decimal
    currency: str
    source: str


def actions_from_bars(
    security_id: str,
    bars: Sequence[PriceBar],
) -> tuple[CorporateAction, ...]:
    """Extract ordered split and cash-dividend actions from normalized bars."""

    actions: list[CorporateAction] = []
    for bar in bars:
        if bar.stock_splits:
            if bar.stock_splits <= 0:
                raise CanonicalValueError("stock split factor must be positive")
            actions.append(
                CorporateAction(
                    security_id=security_id,
                    action_date=bar.date,
                    action_type="split",
                    value=bar.stock_splits,
                    currency=bar.currency,
                    source=bar.source,
                )
            )
        if bar.dividends:
            if bar.dividends < 0:
                raise CanonicalValueError("cash dividend must not be negative")
            actions.append(
                CorporateAction(
                    security_id=security_id,
                    action_date=bar.date,
                    action_type="dividend",
                    value=bar.dividends,
                    currency=bar.currency,
                    source=bar.source,
                )
            )
    return tuple(sorted(actions, key=lambda action: (action.action_date, action.action_type)))


def split_factor_between(
    actions: Sequence[CorporateAction],
    *,
    after: date,
    through: date,
) -> Decimal:
    """Return the product of split factors after one date through another."""

    if through < after:
        raise CanonicalValueError("split range ends before it starts")
    factor = Decimal("1")
    for action in actions:
        if action.action_type == "split" and after < action.action_date <= through:
            factor *= action.value
    return factor


def apply_split(
    quantity: Decimal, average_cost: Decimal, factor: Decimal
) -> tuple[Decimal, Decimal]:
    """Adjust quantity and per-unit cost while preserving aggregate basis exactly."""

    if factor <= 0:
        raise CanonicalValueError("split factor must be positive")
    return quantity * factor, average_cost / factor


def persist_actions(
    repository_root: Path,
    security_id: str,
    bars: Sequence[PriceBar],
    *,
    source_price_hash: str,
) -> int:
    """Append newly observed actions so portfolio replay outlives rolling price retention."""

    rows = []
    existing = {
        row["corporate_action_id"]: row for row in read_table(repository_root, "corporate_actions")
    }
    for action in actions_from_bars(security_id, bars):
        action_id = stable_id(
            "action",
            action.security_id,
            action.action_date,
            action.action_type,
        )
        prior = existing.get(action_id)
        if prior is not None:
            expected_fields = {
                "corporate_action_id": action_id,
                "security_id": action.security_id,
                "action_date": action.action_date.isoformat(),
                "action_type": action.action_type,
                "value": decimal_text(action.value),
                "currency": action.currency,
            }
            if any(prior[field] != value for field, value in expected_fields.items()):
                raise CanonicalValueError(
                    f"corporate action correction requires a compensating entry: {action_id}"
                )
            continue
        rows.append(
            {
                "corporate_action_id": action_id,
                "security_id": action.security_id,
                "action_date": action.action_date.isoformat(),
                "action_type": action.action_type,
                "value": decimal_text(action.value),
                "currency": action.currency,
                "source": action.source,
                "source_price_hash": source_price_hash,
                "recorded_at": format_timestamp(bars[-1].retrieved_at),
            }
        )
    return append_unique(
        repository_root,
        "corporate_actions",
        rows,
        key_columns=("corporate_action_id",),
    )


def accrue_dividends(
    repository_root: Path,
    *,
    through: date,
    fx_rates_to_base: Mapping[tuple[str, date], Decimal],
    base_currency: str,
    run_id: str,
) -> int:
    """Append cash dividends/debits for positions held before each recorded ex-date."""

    order_leg_rows = read_table(repository_root, "order_legs")
    legs = {(row["order_id"], row["leg_id"]): leg_from_row(row) for row in order_leg_rows}
    if len(legs) != len(order_leg_rows):
        raise CanonicalValueError("duplicate order leg identity")
    events: list[tuple[datetime, int, Mapping[str, str]]] = []
    for row in read_table(repository_root, "corporate_actions"):
        action_date = parse_iso_date(row["action_date"])
        if action_date <= through:
            events.append((datetime.combine(action_date, time.min, UTC), 0, row))
    for row in read_table(repository_root, "executions"):
        executed_at = parse_timestamp(row["executed_at"])
        assert executed_at is not None
        if executed_at.date() <= through:
            events.append((executed_at, 1, row))
    events.sort(key=lambda event: (event[0], event[1], event[2].get("execution_id", "")))
    quantities: dict[tuple[str, str], Decimal] = {}
    rows: list[dict[str, str]] = []
    existing_cash = {
        row["cash_entry_id"]: row for row in read_table(repository_root, "cash_ledger")
    }
    for occurred_at, kind, event_row in events:
        if kind == 1:
            leg = legs.get((event_row["order_id"], event_row["leg_id"]))
            if leg is None or leg.instrument_type != "equity":
                continue
            key = (leg.security_id, leg.side)
            delta = required_decimal(event_row["quantity"], label="execution quantity")
            opening = (leg.side == "long" and leg.action == "buy") or (
                leg.side == "short" and leg.action == "sell"
            )
            quantities[key] = quantities.get(key, Decimal("0")) + (delta if opening else -delta)
            if quantities[key] < 0:
                raise CanonicalValueError(
                    f"execution {event_row['execution_id']} over-closes its position"
                )
            continue
        action_type = event_row["action_type"]
        security_id = event_row["security_id"]
        value = required_decimal(event_row["value"], label="corporate action value")
        if action_type == "split":
            for side in ("long", "short"):
                key = (security_id, side)
                if key in quantities:
                    quantities[key] *= value
            continue
        if action_type != "dividend":
            continue
        action_date = occurred_at.date()
        eligible_quantities = {
            side: quantities.get((security_id, side), Decimal("0")) for side in ("long", "short")
        }
        if not any(quantity > 0 for quantity in eligible_quantities.values()):
            continue
        currency = event_row["currency"]
        fx_rate = (
            Decimal("1")
            if currency == base_currency
            else fx_rates_to_base.get((currency, action_date))
        )
        if fx_rate is None or fx_rate <= 0:
            raise CanonicalValueError(f"missing dividend FX rate for {currency} on {action_date}")
        for side, quantity in eligible_quantities.items():
            if quantity <= 0:
                continue
            amount = quantity * value * (Decimal("1") if side == "long" else Decimal("-1"))
            entry_id = stable_id("cash", event_row["corporate_action_id"], side)
            candidate = {
                "cash_entry_id": entry_id,
                "occurred_at": format_timestamp(occurred_at),
                "entry_type": "dividend",
                "reference_id": event_row["corporate_action_id"],
                "currency": currency,
                "amount": decimal_text(amount),
                "fx_rate_to_base": decimal_text(fx_rate),
                "base_amount": decimal_text(amount * fx_rate),
                "run_id": run_id,
                "notes": f"Paper dividend for {security_id} {side} position",
            }
            prior = existing_cash.get(entry_id)
            if prior is not None:
                economic_fields = (
                    "occurred_at",
                    "entry_type",
                    "reference_id",
                    "currency",
                    "amount",
                    "fx_rate_to_base",
                    "base_amount",
                )
                if any(prior[field] != candidate[field] for field in economic_fields):
                    raise CanonicalValueError(
                        f"dividend correction requires a compensating entry: {entry_id}"
                    )
                continue
            rows.append(candidate)
    return append_unique(
        repository_root,
        "cash_ledger",
        rows,
        key_columns=("cash_entry_id",),
    )

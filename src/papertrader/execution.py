"""Paper-only fill policies and append-only execution/cash ledger transitions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from papertrader.config import Settings
from papertrader.models import (
    Fill,
    MarketBar,
    OptionQuote,
    OrderLegSpec,
    PositionMark,
    ReferencePrice,
    RiskState,
)
from papertrader.orders import leg_from_row, update_order_status, update_signal_status
from papertrader.risk import assess_order_risk, require_risk_approval
from papertrader.tables import append_unique, read_table, write_table
from papertrader.utils import (
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    required_decimal,
    stable_id,
    utc_now,
)


class ExecutionError(RuntimeError):
    """Raised when deterministic paper fill or ledger validation fails."""


def assert_paper_execution_enabled(settings: Settings) -> None:
    """Fail closed at the execution boundary if paper mode was not asserted."""

    if not settings.paper_trading_only:
        raise RuntimeError("execution requires PAPER_TRADING_ONLY=true")


def ensure_initial_capital(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    occurred_at: datetime,
) -> str:
    """Append exactly one immutable initial-capital entry in the base currency."""

    assert_paper_execution_enabled(settings)
    entry_id = stable_id(
        "cash",
        "initial_capital",
        settings.portfolio.base_currency,
        settings.portfolio.initial_capital,
    )
    rows = read_table(repository_root, "cash_ledger")
    initial = [row for row in rows if row["entry_type"] == "initial_capital"]
    expected = {
        "cash_entry_id": entry_id,
        "occurred_at": format_timestamp(ensure_utc(occurred_at)),
        "entry_type": "initial_capital",
        "reference_id": "",
        "currency": settings.portfolio.base_currency,
        "amount": decimal_text(settings.portfolio.initial_capital),
        "fx_rate_to_base": "1",
        "base_amount": decimal_text(settings.portfolio.initial_capital),
        "run_id": run_id,
        "notes": "Configured initial paper capital",
    }
    if initial:
        row = initial[0]
        economic_fields = {
            "cash_entry_id",
            "entry_type",
            "reference_id",
            "currency",
            "amount",
            "fx_rate_to_base",
            "base_amount",
            "notes",
        }
        if len(initial) != 1 or any(row[field] != expected[field] for field in economic_fields):
            raise ExecutionError("initial-capital ledger invariant is violated")
        return row["cash_entry_id"]
    append_unique(
        repository_root,
        "cash_ledger",
        [expected],
        key_columns=("cash_entry_id",),
    )
    return entry_id


def _eligible_bars(
    leg: OrderLegSpec,
    bars: Sequence[MarketBar],
    *,
    after: datetime,
    through: datetime,
) -> list[MarketBar]:
    eligible: list[MarketBar] = []
    for bar in bars:
        if (
            bar.security_id != leg.security_id
            or bar.provider_contract_id != leg.provider_contract_id
        ):
            continue
        timestamp = ensure_utc(bar.timestamp)
        prices = (bar.open, bar.high, bar.low, bar.close)
        if (
            any(not price.is_finite() for price in prices)
            or not bar.fx_rate_to_base.is_finite()
            or min(prices) <= 0
            or bar.high < max(bar.open, bar.low, bar.close)
            or bar.low > min(bar.open, bar.high, bar.close)
            or bar.fx_rate_to_base <= 0
        ):
            raise ExecutionError(f"invalid market bar for leg {leg.leg_id}")
        if after < timestamp <= through and bar.currency == leg.currency:
            eligible.append(bar)
    return sorted(eligible, key=lambda bar: ensure_utc(bar.timestamp))


def select_fill(
    order: Mapping[str, str],
    leg: OrderLegSpec,
    *,
    bars: Sequence[MarketBar],
    quotes: Sequence[OptionQuote],
    signal_created_at: datetime,
    now: datetime,
    settings: Settings,
) -> Fill | None:
    """Select one no-look-ahead next-open, limit-touch, or fresh quote-mid fill."""

    not_before = parse_timestamp(order["not_before"])
    expires_at = parse_timestamp(order["expires_at"])
    assert not_before is not None and expires_at is not None
    instant = ensure_utc(now)
    after = max(ensure_utc(signal_created_at), not_before)
    through = min(instant, expires_at)
    if through <= after:
        return None
    policy = order["fill_policy"]
    slippage = required_decimal(order["slippage_bps"], label="slippage_bps") / Decimal("10000")
    if not slippage.is_finite() or slippage < 0:
        raise ExecutionError("order slippage must be finite and non-negative")
    fill_price: Decimal
    source_time: datetime
    fx_rate: Decimal
    if policy in {"next_open", "limit_touch"}:
        candidates = _eligible_bars(leg, bars, after=after, through=through)
        if policy == "next_open":
            if not candidates:
                return None
            bar = candidates[0]
            fill_price = (
                bar.open * (Decimal("1") + slippage)
                if leg.action == "buy"
                else bar.open * (Decimal("1") - slippage)
            )
        else:
            limit = leg.limit_price
            if limit is None and order["limit_price"]:
                limit = required_decimal(order["limit_price"], label="limit_price")
            if limit is None or not limit.is_finite() or limit <= 0:
                raise ExecutionError(f"limit_touch leg {leg.leg_id} has no limit")
            touched_bar = next(
                (
                    candidate
                    for candidate in candidates
                    if (leg.action == "buy" and candidate.low <= limit)
                    or (leg.action == "sell" and candidate.high >= limit)
                ),
                None,
            )
            if touched_bar is None:
                return None
            if leg.action == "buy":
                base = touched_bar.open if touched_bar.open <= limit else limit
                fill_price = min(base * (Decimal("1") + slippage), limit)
            else:
                base = touched_bar.open if touched_bar.open >= limit else limit
                fill_price = max(base * (Decimal("1") - slippage), limit)
            bar = touched_bar
        source_time = ensure_utc(bar.timestamp)
        fx_rate = bar.fx_rate_to_base
    elif policy == "quote_mid":
        eligible_quotes = [
            quote
            for quote in quotes
            if quote.provider_contract_id == leg.provider_contract_id
            and after < ensure_utc(quote.timestamp) <= through
            and instant - ensure_utc(quote.timestamp) <= settings.orders.option_quote_freshness
            and quote.currency == leg.currency
        ]
        eligible_quotes.sort(key=lambda quote: ensure_utc(quote.timestamp))
        if not eligible_quotes:
            return None
        quote = eligible_quotes[-1]
        if (
            not quote.bid.is_finite()
            or not quote.ask.is_finite()
            or not quote.fx_rate_to_base.is_finite()
            or quote.bid < 0
            or quote.ask <= 0
            or quote.bid > quote.ask
            or quote.fx_rate_to_base <= 0
            or quote.open_interest < settings.risk.minimum_option_open_interest
            or quote.volume < settings.risk.minimum_option_volume
        ):
            raise ExecutionError(f"invalid quote for leg {leg.leg_id}")
        fill_price = (quote.bid + quote.ask) / Decimal("2")
        limit = leg.limit_price
        if limit is None and order["limit_price"]:
            limit = required_decimal(order["limit_price"], label="limit_price")
        if limit is not None and (
            (leg.action == "buy" and fill_price > limit)
            or (leg.action == "sell" and fill_price < limit)
        ):
            return None
        source_time = ensure_utc(quote.timestamp)
        fx_rate = quote.fx_rate_to_base
    else:
        raise ExecutionError(f"unsupported fill policy: {policy}")
    if not fill_price.is_finite() or fill_price <= 0:
        raise ExecutionError(f"calculated non-positive fill for leg {leg.leg_id}")
    return Fill(
        order_id=order["order_id"],
        leg_id=leg.leg_id,
        executed_at=source_time,
        security_id=leg.security_id,
        provider_contract_id=leg.provider_contract_id,
        action=leg.action,
        side=leg.side,
        instrument_type=leg.instrument_type,
        quantity=leg.quantity,
        fill_price=fill_price,
        contract_multiplier=leg.contract_multiplier,
        fees=Decimal("0"),
        currency=leg.currency,
        fx_rate_to_base=fx_rate,
        source_time=source_time,
    )


def _execution_row(fill: Fill, *, execution_id: str, run_id: str) -> dict[str, str]:
    gross = fill.quantity * fill.fill_price * fill.contract_multiplier
    cash_effect = -gross if fill.action == "buy" else gross
    return {
        "execution_id": execution_id,
        "order_id": fill.order_id,
        "leg_id": fill.leg_id,
        "executed_at": format_timestamp(fill.executed_at),
        "security_id": fill.security_id,
        "provider_contract_id": fill.provider_contract_id,
        "side": fill.action,
        "quantity": decimal_text(fill.quantity),
        "fill_price": decimal_text(fill.fill_price),
        "contract_multiplier": decimal_text(fill.contract_multiplier),
        "fees": decimal_text(fill.fees),
        "currency": fill.currency,
        "fx_rate_to_base": decimal_text(fill.fx_rate_to_base),
        "cash_effect": decimal_text(cash_effect),
        "source_bar_time": format_timestamp(fill.source_time),
        "run_id": run_id,
    }


def cash_rows_for_execution(execution: Mapping[str, str]) -> tuple[dict[str, str], ...]:
    """Derive separate immutable trade and fee cash rows from one execution."""

    execution_id = execution["execution_id"]
    amount = required_decimal(execution["cash_effect"], label="cash_effect")
    fx_rate = required_decimal(execution["fx_rate_to_base"], label="fx_rate_to_base")
    fees = required_decimal(execution["fees"], label="fees")
    action = execution["side"]
    rows = [
        {
            "cash_entry_id": stable_id("cash", execution_id, "trade"),
            "occurred_at": execution["executed_at"],
            "entry_type": action,
            "reference_id": execution_id,
            "currency": execution["currency"],
            "amount": decimal_text(amount),
            "fx_rate_to_base": decimal_text(fx_rate),
            "base_amount": decimal_text(amount * fx_rate),
            "run_id": execution["run_id"],
            "notes": f"Paper {action} for order {execution['order_id']} leg {execution['leg_id']}",
        }
    ]
    if fees:
        rows.append(
            {
                "cash_entry_id": stable_id("cash", execution_id, "fee"),
                "occurred_at": execution["executed_at"],
                "entry_type": "fee",
                "reference_id": execution_id,
                "currency": execution["currency"],
                "amount": decimal_text(-fees),
                "fx_rate_to_base": decimal_text(fx_rate),
                "base_amount": decimal_text(-fees * fx_rate),
                "run_id": execution["run_id"],
                "notes": f"Paper execution fee for {execution_id}",
            }
        )
    return tuple(rows)


def _repair_cash_for_executions(
    repository_root: Path, executions: Sequence[Mapping[str, str]]
) -> None:
    rows = [cash for execution in executions for cash in cash_rows_for_execution(execution)]
    if rows:
        append_unique(
            repository_root,
            "cash_ledger",
            rows,
            key_columns=("cash_entry_id",),
        )


def _finalize_filled_order(
    repository_root: Path,
    settings: Settings,
    *,
    order: Mapping[str, str],
    signal: Mapping[str, str],
    risk_references: Sequence[ReferencePrice],
    run_id: str,
    instant: datetime,
) -> None:
    """Rebuild generated views and finish mutable states after durable executions."""

    if signal["strategy_id"] != order["strategy_id"]:
        raise ExecutionError(f"order {order['order_id']} conflicts with its signal strategy")
    strategies = read_table(repository_root, "strategies")
    strategy = next(
        (row for row in strategies if row["strategy_id"] == order["strategy_id"]),
        None,
    )
    if strategy is None:
        raise ExecutionError(f"order {order['order_id']} references missing strategy")
    marks = [
        PositionMark(
            security_id=reference.security_id,
            provider_contract_id=reference.provider_contract_id,
            price=reference.price,
            currency=reference.currency,
            fx_rate_to_base=reference.fx_rate_to_base,
            marked_at=ensure_utc(reference.as_of),
        )
        for reference in risk_references
    ]
    from papertrader.performance import update_performance
    from papertrader.portfolio import rebuild_portfolio

    rebuild_portfolio(repository_root, marks=marks, run_id=run_id, as_of=instant)
    update_performance(repository_root, settings, run_id=run_id, generated_at=instant)
    update_order_status(repository_root, order["order_id"], "filled")

    signals = read_table(repository_root, "signals")
    found_signal = False
    for row in signals:
        if row["signal_id"] == signal["signal_id"]:
            row["status"] = "filled"
            found_signal = True
    if not found_signal:
        raise ExecutionError(f"order {order['order_id']} references missing signal")
    write_table(repository_root, "signals", signals)

    if signal["signal_type"] == "open":
        for row in strategies:
            if row["strategy_id"] == order["strategy_id"]:
                row["status"] = "active"
                row["updated_at"] = format_timestamp(instant)
        write_table(repository_root, "strategies", strategies)


def process_order_fill(
    repository_root: Path,
    settings: Settings,
    *,
    order_id: str,
    bars: Sequence[MarketBar],
    quotes: Sequence[OptionQuote],
    risk_state: RiskState,
    risk_references: Sequence[ReferencePrice],
    run_id: str,
    now: datetime | None = None,
) -> tuple[str, tuple[str, ...]]:
    """Fill all remaining legs atomically in policy terms, then rebuild derived state."""

    assert_paper_execution_enabled(settings)
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    orders = read_table(repository_root, "orders")
    order = next((row for row in orders if row["order_id"] == order_id), None)
    if order is None:
        raise ExecutionError(f"unknown order: {order_id}")
    leg_rows = [
        row for row in read_table(repository_root, "order_legs") if row["order_id"] == order_id
    ]
    if not leg_rows:
        raise ExecutionError(f"order {order_id} has no normalized legs")
    legs = [leg_from_row(row) for row in leg_rows]
    signal = next(
        (
            row
            for row in read_table(repository_root, "signals")
            if row["signal_id"] == order["signal_id"]
        ),
        None,
    )
    if signal is None:
        raise ExecutionError(f"order {order_id} references missing signal")
    existing = [
        row for row in read_table(repository_root, "executions") if row["order_id"] == order_id
    ]
    valid_leg_ids = {leg.leg_id for leg in legs}
    existing_leg_ids = [row["leg_id"] for row in existing]
    if len(existing_leg_ids) != len(set(existing_leg_ids)) or not set(existing_leg_ids).issubset(
        valid_leg_ids
    ):
        raise ExecutionError(f"order {order_id} has inconsistent execution legs")
    _repair_cash_for_executions(repository_root, existing)
    remaining = [leg for leg in legs if leg.leg_id not in set(existing_leg_ids)]
    if not remaining:
        _finalize_filled_order(
            repository_root,
            settings,
            order=order,
            signal=signal,
            risk_references=risk_references,
            run_id=run_id,
            instant=instant,
        )
        return "filled", tuple(row["execution_id"] for row in existing)
    if order["status"] not in {"pending", "partially_filled"}:
        return order["status"], tuple(row["execution_id"] for row in existing)
    expiry = parse_timestamp(order["expires_at"])
    assert expiry is not None
    signal_created = parse_timestamp(signal["created_at"])
    assert signal_created is not None
    fills: list[Fill] = []
    for leg in remaining:
        fill = select_fill(
            order,
            leg,
            bars=bars,
            quotes=quotes,
            signal_created_at=signal_created,
            now=instant,
            settings=settings,
        )
        if fill is None:
            if instant >= expiry:
                update_order_status(repository_root, order_id, "expired")
                update_signal_status(repository_root, order["signal_id"], "expired")
                return "expired", tuple(row["execution_id"] for row in existing)
            return "pending", tuple(row["execution_id"] for row in existing)
        fills.append(fill)
    venues = {
        row["security_id"]: row["venue_mic"] for row in read_table(repository_root, "securities")
    }
    strategy = next(
        (
            row
            for row in read_table(repository_root, "strategies")
            if row["strategy_id"] == order["strategy_id"]
        ),
        None,
    )
    if strategy is None:
        raise ExecutionError(f"order {order_id} references missing strategy")
    assessment = assess_order_risk(
        settings,
        risk_state,
        remaining,
        risk_references,
        venues,
        now=instant,
        activates_new_strategy=strategy["status"] != "active",
    )
    require_risk_approval(assessment)
    notionals = [fill.quantity * fill.fill_price * fill.contract_multiplier for fill in fills]
    variable_fees = [
        notional * settings.orders.variable_fee_bps / Decimal("10000") for notional in notionals
    ]
    if fills and not existing:
        variable_fees[0] += settings.orders.fixed_fee
    fills = [replace(fill, fees=fee) for fill, fee in zip(fills, variable_fees, strict=True)]
    execution_rows = [
        _execution_row(
            fill,
            execution_id=stable_id("execution", fill.order_id, fill.leg_id),
            run_id=run_id,
        )
        for fill in fills
    ]
    append_unique(
        repository_root,
        "executions",
        execution_rows,
        key_columns=("execution_id",),
    )
    _repair_cash_for_executions(repository_root, execution_rows)

    _finalize_filled_order(
        repository_root,
        settings,
        order=order,
        signal=signal,
        risk_references=risk_references,
        run_id=run_id,
        instant=instant,
    )
    return "filled", tuple(row["execution_id"] for row in [*existing, *execution_rows])

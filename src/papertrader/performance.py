"""Flow-adjusted performance epochs derived from reconciled paper-account state."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from papertrader.config import Settings
from papertrader.portfolio import reconcile_portfolio, replay_accounting
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

EXTERNAL_FLOW_TYPES = frozenset({"capital_contribution", "capital_withdrawal"})


class PerformanceError(RuntimeError):
    """Raised when a performance epoch or external capital flow is invalid."""


def _initial_epoch(repository_root: Path, settings: Settings) -> dict[str, str]:
    initial = [
        row
        for row in read_table(repository_root, "cash_ledger")
        if row["entry_type"] == "initial_capital"
    ]
    if len(initial) != 1:
        raise PerformanceError("performance requires exactly one initial-capital entry")
    cash = initial[0]
    if cash["currency"] != settings.portfolio.base_currency:
        raise PerformanceError("initial capital uses the wrong base currency")
    return {
        "performance_epoch_id": stable_id("performance_epoch", cash["cash_entry_id"]),
        "started_at": cash["occurred_at"],
        "opening_equity_base": cash["base_amount"],
        "base_currency": cash["currency"],
        "reason": "Initial capital",
        "run_id": cash["run_id"],
    }


def ensure_performance_epoch(repository_root: Path, settings: Settings) -> dict[str, str]:
    """Return the latest epoch, seeding the immutable initial epoch when necessary."""

    epochs = read_table(repository_root, "performance_epochs")
    if not epochs:
        epoch = _initial_epoch(repository_root, settings)
        append_unique(
            repository_root,
            "performance_epochs",
            [epoch],
            key_columns=("performance_epoch_id",),
        )
        return epoch
    for epoch in epochs:
        started = parse_timestamp(epoch["started_at"])
        opening = required_decimal(epoch["opening_equity_base"], label="epoch opening equity")
        if (
            started is None
            or opening <= 0
            or epoch["base_currency"] != settings.portfolio.base_currency
            or not epoch["reason"].strip()
        ):
            raise PerformanceError(f"invalid performance epoch {epoch['performance_epoch_id']}")
    return max(epochs, key=lambda row: (row["started_at"], row["performance_epoch_id"]))


def _equity_base(repository_root: Path) -> Decimal:
    replay = replay_accounting(repository_root)
    market_value = sum(
        (
            required_decimal(row["market_value_base"], label="market value")
            for row in read_table(repository_root, "portfolio")
        ),
        Decimal("0"),
    )
    return replay.cash_base + market_value


def rebase_performance(
    repository_root: Path,
    settings: Settings,
    *,
    target_equity_base: Decimal,
    reason: str,
    run_id: str,
    effective_at: datetime,
) -> tuple[str, str | None]:
    """Append one external capital flow and start an immutable performance epoch.

    Accounting history remains intact.  The capital-flow entry changes cash to the requested
    account size, and the new epoch makes subsequent return figures independent from the old
    capital base.
    """

    if not settings.paper_trading_only:
        raise PerformanceError("performance rebase requires PAPER_TRADING_ONLY=true")
    if not target_equity_base.is_finite() or target_equity_base <= 0:
        raise PerformanceError("target equity must be a positive decimal")
    normalized_reason = " ".join(reason.split())
    if not normalized_reason:
        raise PerformanceError("performance epoch reason is required")
    instant = ensure_utc(effective_at).replace(microsecond=0)
    if any(
        row["status"] in {"pending", "partially_filled"}
        for row in read_table(repository_root, "orders")
    ):
        raise PerformanceError("cancel or fill every live order before changing account capital")
    reconciliation = reconcile_portfolio(repository_root)
    if reconciliation:
        raise PerformanceError("portfolio does not reconcile: " + "; ".join(reconciliation))

    epoch_id = stable_id(
        "performance_epoch",
        run_id,
        decimal_text(target_equity_base),
        normalized_reason,
    )
    expected_epoch = {
        "performance_epoch_id": epoch_id,
        "started_at": format_timestamp(instant),
        "opening_equity_base": decimal_text(target_equity_base),
        "base_currency": settings.portfolio.base_currency,
        "reason": normalized_reason,
        "run_id": run_id,
    }
    existing_epoch = next(
        (
            row
            for row in read_table(repository_root, "performance_epochs")
            if row["performance_epoch_id"] == epoch_id
        ),
        None,
    )
    if existing_epoch is not None:
        if existing_epoch != expected_epoch:
            raise PerformanceError(f"performance epoch identity collision: {epoch_id}")
        return epoch_id, next(
            (
                row["cash_entry_id"]
                for row in read_table(repository_root, "cash_ledger")
                if row["reference_id"] == epoch_id and row["entry_type"] in EXTERNAL_FLOW_TYPES
            ),
            None,
        )

    current_equity = _equity_base(repository_root)
    flow = target_equity_base - current_equity
    replay = replay_accounting(repository_root)
    if flow < 0 and replay.cash_base + flow < 0:
        raise PerformanceError("requested withdrawal exceeds available base-currency cash")
    cash_entry_id: str | None = None
    if flow != 0:
        entry_type = "capital_contribution" if flow > 0 else "capital_withdrawal"
        cash_entry_id = stable_id("cash", entry_type, epoch_id)
        append_unique(
            repository_root,
            "cash_ledger",
            [
                {
                    "cash_entry_id": cash_entry_id,
                    "occurred_at": format_timestamp(instant),
                    "entry_type": entry_type,
                    "reference_id": epoch_id,
                    "currency": settings.portfolio.base_currency,
                    "amount": decimal_text(flow),
                    "fx_rate_to_base": "1",
                    "base_amount": decimal_text(flow),
                    "run_id": run_id,
                    "notes": (
                        f"External capital flow starting performance epoch: {normalized_reason}"
                    ),
                }
            ],
            key_columns=("cash_entry_id",),
        )
    if _equity_base(repository_root) != target_equity_base:
        raise PerformanceError("capital flow did not produce the requested reconciled equity")
    append_unique(
        repository_root,
        "performance_epochs",
        [expected_epoch],
        key_columns=("performance_epoch_id",),
    )
    return epoch_id, cash_entry_id


def _external_flow(
    repository_root: Path,
    *,
    after: datetime,
    through: datetime,
) -> Decimal:
    total = Decimal("0")
    for row in read_table(repository_root, "cash_ledger"):
        if row["entry_type"] not in EXTERNAL_FLOW_TYPES:
            continue
        occurred = parse_timestamp(row["occurred_at"])
        assert occurred is not None
        if after < occurred <= through:
            total += required_decimal(row["base_amount"], label="external capital flow")
    return total


def update_performance(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    generated_at: datetime | None = None,
) -> dict[str, str]:
    """Insert or replace today's flow-adjusted row in the current performance epoch."""

    instant = ensure_utc(generated_at or utc_now()).replace(microsecond=0)
    replay = replay_accounting(repository_root)
    positions = read_table(repository_root, "portfolio")
    market_value = sum(
        (required_decimal(row["market_value_base"], label="market value") for row in positions),
        Decimal("0"),
    )
    gross_exposure = sum(
        (
            abs(required_decimal(row["market_value_base"], label="market value"))
            for row in positions
        ),
        Decimal("0"),
    )
    unrealized = sum(
        (required_decimal(row["unrealized_pnl_base"], label="unrealized P/L") for row in positions),
        Decimal("0"),
    )
    equity = replay.cash_base + market_value
    epoch = ensure_performance_epoch(repository_root, settings)
    epoch_started = parse_timestamp(epoch["started_at"])
    assert epoch_started is not None
    if instant < epoch_started:
        raise PerformanceError("performance time precedes the current epoch")
    epoch_id = epoch["performance_epoch_id"]
    opening_equity = required_decimal(epoch["opening_equity_base"], label="epoch opening equity")
    rows = read_table(repository_root, "performance_daily")
    today = instant.date().isoformat()
    earlier = sorted(
        (row for row in rows if row["performance_epoch_id"] == epoch_id and row["date"] < today),
        key=lambda row: (row["date"], row["generated_at"], row["run_id"]),
    )
    previous = earlier[-1] if earlier else None
    period_start = (
        parse_timestamp(previous["generated_at"]) if previous is not None else epoch_started
    )
    assert period_start is not None
    external_flow = _external_flow(repository_root, after=period_start, through=instant)
    previous_equity = (
        required_decimal(previous["equity_base"], label="previous equity")
        if previous is not None
        else opening_equity
    )
    daily_pnl = equity - previous_equity - external_flow
    daily_return = (
        daily_pnl / previous_equity * Decimal("100") if previous_equity != 0 else Decimal("0")
    )
    cumulative_external_flow = _external_flow(repository_root, after=epoch_started, through=instant)
    cumulative_return = (
        (equity - opening_equity - cumulative_external_flow) / opening_equity * Decimal("100")
    )
    row = {
        "date": today,
        "performance_epoch_id": epoch_id,
        "base_currency": settings.portfolio.base_currency,
        "cash_base": decimal_text(replay.cash_base),
        "market_value_base": decimal_text(market_value),
        "equity_base": decimal_text(equity),
        "gross_exposure_base": decimal_text(gross_exposure),
        "net_exposure_base": decimal_text(market_value),
        "realized_pnl_base": decimal_text(replay.realized_pnl_base),
        "unrealized_pnl_base": decimal_text(unrealized),
        "net_external_flow_base": decimal_text(external_flow),
        "daily_pnl_base": decimal_text(daily_pnl),
        "daily_return_pct": decimal_text(daily_return),
        "cumulative_return_pct": decimal_text(cumulative_return),
        "run_id": run_id,
        "generated_at": format_timestamp(instant),
    }
    previous_today = next(
        (
            candidate
            for candidate in rows
            if candidate["date"] == today and candidate["performance_epoch_id"] == epoch_id
        ),
        None,
    )
    economic_columns = tuple(column for column in row if column not in {"run_id", "generated_at"})
    if previous_today is not None and all(
        previous_today[column] == row[column] for column in economic_columns
    ):
        row = previous_today
    output = [
        candidate
        for candidate in rows
        if not (candidate["date"] == today and candidate["performance_epoch_id"] == epoch_id)
    ]
    output.append(row)
    output.sort(
        key=lambda candidate: (
            candidate["date"],
            candidate["performance_epoch_id"],
            candidate["generated_at"],
        )
    )
    write_table(repository_root, "performance_daily", output)
    return row

"""Generated daily performance from reconciled cash and position state."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from papertrader.config import Settings
from papertrader.portfolio import replay_accounting
from papertrader.tables import read_table, write_table
from papertrader.utils import decimal_text, ensure_utc, format_timestamp, required_decimal, utc_now


def update_performance(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    generated_at: datetime | None = None,
) -> dict[str, str]:
    """Insert or replace today's deterministic performance row without timestamp-only churn."""

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
    rows = read_table(repository_root, "performance_daily")
    today = instant.date().isoformat()
    earlier = sorted((row for row in rows if row["date"] < today), key=lambda row: row["date"])
    previous_equity = (
        required_decimal(earlier[-1]["equity_base"], label="previous equity")
        if earlier
        else settings.portfolio.initial_capital
    )
    daily_pnl = equity - previous_equity
    daily_return = (
        daily_pnl / previous_equity * Decimal("100") if previous_equity != 0 else Decimal("0")
    )
    cumulative_return = (
        (equity - settings.portfolio.initial_capital)
        / settings.portfolio.initial_capital
        * Decimal("100")
    )
    row = {
        "date": today,
        "base_currency": settings.portfolio.base_currency,
        "cash_base": decimal_text(replay.cash_base),
        "market_value_base": decimal_text(market_value),
        "equity_base": decimal_text(equity),
        "gross_exposure_base": decimal_text(gross_exposure),
        "net_exposure_base": decimal_text(market_value),
        "realized_pnl_base": decimal_text(replay.realized_pnl_base),
        "unrealized_pnl_base": decimal_text(unrealized),
        "daily_pnl_base": decimal_text(daily_pnl),
        "daily_return_pct": decimal_text(daily_return),
        "cumulative_return_pct": decimal_text(cumulative_return),
        "run_id": run_id,
        "generated_at": format_timestamp(instant),
    }
    previous_today = next((candidate for candidate in rows if candidate["date"] == today), None)
    economic_columns = tuple(column for column in row if column not in {"run_id", "generated_at"})
    if previous_today is not None and all(
        previous_today[column] == row[column] for column in economic_columns
    ):
        row = previous_today
    output = [candidate for candidate in rows if candidate["date"] != today]
    output.append(row)
    output.sort(key=lambda candidate: candidate["date"])
    write_table(repository_root, "performance_daily", output)
    return row

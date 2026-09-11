"""Controller-derived attention classes shared by all sequential queue consumers."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TYPE_CHECKING

from papertrader.config import Settings
from papertrader.market_data import MarketDataError, session_close
from papertrader.tables import read_table
from papertrader.utils import parse_timestamp

if TYPE_CHECKING:
    from papertrader.queue import Operation

type AttentionKey = tuple[int, Decimal, float, int, datetime, str]


def attention_key(
    root: Path, settings: Settings, operation: Operation, *, now: datetime
) -> AttentionKey:
    """Risk exits > ready final review > current oversold > ordinary work.

    Priority class is not accepted from prose or a source label. RSI is read from the
    deterministic indicator table; a recovery or stale observation removes only urgency.
    Selecting this lane first reserves available capacity without an extra operation budget.
    """
    ordinary: AttentionKey = (
        3,
        Decimal("0"),
        0,
        -operation.priority,
        operation.created_at,
        operation.operation_id,
    )
    if operation.operation_type == "execute_strategy":
        signals = [
            row
            for row in read_table(root, "signals")
            if row["strategy_id"] == operation.entity_id and row["status"] == "ready"
        ]
        if any(row["signal_type"] in {"close", "reduce"} for row in signals):
            return (0, *ordinary[1:])
    if operation.operation_type == "final_buy_review":
        return (1, *ordinary[1:])
    if operation.operation_type == "research_triage":
        from papertrader.monitoring import monitoring_context

        if monitoring_context(root, operation) is not None:
            return (3, Decimal("-1"), *ordinary[2:])
    if operation.operation_type not in {
        "security_research",
        "quick_check_research",
        "research_triage",
        "opportunity_research",
    }:
        return ordinary
    security_id = operation.entity_id
    if operation.entity_type != "security":
        from papertrader.queue import _operation_inputs

        security_id = str(_operation_inputs(root, operation).get("security_id", ""))
    attention = rsi_attention(root, settings, security_id, now=now)
    if attention is None:
        return ordinary
    rsi, observed = attention
    return (
        2,
        rsi,
        -observed.timestamp(),
        -operation.priority,
        operation.created_at,
        operation.operation_id,
    )


def rsi_attention(
    root: Path, settings: Settings, security_id: str, *, now: datetime
) -> tuple[Decimal, datetime] | None:
    indicator = next(
        (row for row in read_table(root, "indicators") if row["security_id"] == security_id), None
    )
    if indicator is None or not indicator["source_price_hash"]:
        return None
    security = next(
        (row for row in read_table(root, "securities") if row["security_id"] == security_id), None
    )
    if security is None:
        return None
    try:
        rsi = Decimal(indicator["rsi_14"])
        observed = session_close(
            settings.market_data.calendar_for(security["venue_mic"]),
            date.fromisoformat(indicator["as_of_date"]),
        )
        calculated = parse_timestamp(indicator["calculated_at"])
        if (
            not rsi.is_finite()
            or not 0 <= rsi <= settings.indicators.rsi_oversold
            or int(indicator["observation_count"]) < 15
            or observed is None
            or calculated is None
            or observed > now
            or calculated > now
            or now - observed > settings.market_data.stale_price_after
        ):
            return None
    except (ValueError, InvalidOperation, MarketDataError):
        return None
    return rsi, observed

"""Bounded sequential equity market refresh, isolated from research and publication."""

from __future__ import annotations

import configparser
import csv
import io
import random
import re
import time
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from itertools import pairwise
from pathlib import Path
from typing import Any, Protocol

import exchange_calendars as xcals  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]
import yfinance as yf  # type: ignore[import-untyped]
from curl_cffi import requests

from papertrader.atomic_io import atomic_write_bytes
from papertrader.research_state import Row, decimal, timestamp

PRICE_COLUMNS = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "volume",
    "dividends",
    "stock_splits",
    "currency",
    "provider_symbol",
    "retrieved_at",
    "source",
)
LATEST_COLUMNS = (
    "security_id",
    "provider_symbol",
    "venue_mic",
    "price_date",
    "retrieved_at",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "volume",
    "currency",
    "source",
    "status",
    "error",
    "expected_session",
    "reconciled_at",
)
FEATURE_COLUMNS = (
    "security_id",
    "price_date",
    "change_1d_pct",
    "change_5d_pct",
    "rsi_14",
    "sma_200",
)
CALENDARS = {
    "XNAS": "XNYS",
    "XNYS": "XNYS",
    "XASE": "XNYS",
    "ARCX": "XNYS",
    "BATS": "XNYS",
    "XETR": "XETR",
    "XMIL": "XMIL",
    "XLON": "XLON",
    "XHKG": "XHKG",
    "XKRX": "XKRX",
    "XKOS": "XKRX",
    "XASX": "XASX",
    "XTKS": "XTKS",
    "XPAR": "XPAR",
    "XAMS": "XAMS",
    "XTSE": "XTSE",
    "XFRA": "XFRA",
    "XWBO": "XWBO",
    "XOTC": "XNYS",
}
MONITORED_SECURITY_STATUSES = {"active", "watching", "watchlist"}


@dataclass(frozen=True)
class MarketLimits:
    cache_days: int = 365
    batch_size: int = 8
    max_provider_calls: int = 24
    max_http_requests: int = 320
    max_attempts: int = 2
    max_runtime_seconds: int = 600
    correction_days: int = 7
    correction_window_days: int = 7
    timeout_seconds: int = 15


DEFAULT_MARKET_LIMITS = MarketLimits()


def market_limits(root: Path) -> MarketLimits:
    config = configparser.ConfigParser()
    config.read(root / "research.ini")
    values = {
        field: config.getint("market", field, fallback=getattr(DEFAULT_MARKET_LIMITS, field))
        for field in MarketLimits.__dataclass_fields__
    }
    if any(value <= 0 for value in values.values()) or values["max_attempts"] > 3:
        raise ValueError("invalid bounded market limits")
    return MarketLimits(**values)


def completed_session(mic: str, now: datetime) -> date:
    if now.utcoffset() is None:
        raise ValueError("market clock must have a timezone")
    now = now.astimezone(UTC)
    if mic not in CALENDARS:
        raise ValueError(f"unsupported_exchange_calendar:{mic}")
    calendar = xcals.get_calendar(CALENDARS[mic])
    sessions = calendar.sessions_in_range(
        (now.date() - timedelta(days=20)).isoformat(), now.date().isoformat()
    )
    completed: list[date] = []
    for session in sessions:
        if calendar.session_close(session) <= pd.Timestamp(now):
            completed.append(date.fromisoformat(str(session.date())))
    if not completed:
        raise ValueError("no_completed_session")
    return max(completed)


class Provider(Protocol):
    def fetch(self, symbols: Sequence[str], start: date, end: date) -> Mapping[str, list[Row]]: ...


class RequestBudget:
    def __init__(self, limit: int, seconds: int) -> None:
        self.limit = limit
        self.deadline = time.monotonic() + seconds
        self.used = 0

    def take(self) -> None:
        if self.used >= self.limit or time.monotonic() >= self.deadline:
            raise RuntimeError("market_request_or_runtime_budget_exhausted")
        self.used += 1


class _BoundedSession(requests.Session[Any]):
    def __init__(self, limits: MarketLimits, budget: RequestBudget) -> None:
        super().__init__(impersonate="chrome")
        self._limits = limits
        self._budget = budget

    def request(self, *args: Any, **kwargs: Any) -> Any:
        self._budget.take()
        kwargs["timeout"] = self._limits.timeout_seconds
        return super().request(*args, **kwargs)


class YFinanceResearchProvider:
    def __init__(self, limits: MarketLimits) -> None:
        self.limits = limits
        self.budget = RequestBudget(limits.max_http_requests, limits.max_runtime_seconds)
        self.session = _BoundedSession(limits, self.budget)

    def fetch(self, symbols: Sequence[str], start: date, end: date) -> Mapping[str, list[Row]]:
        frame = yf.download(
            list(symbols),
            start=start.isoformat(),
            end=end.isoformat(),
            interval="1d",
            auto_adjust=False,
            actions=True,
            repair=False,
            threads=False,
            group_by="ticker",
            progress=False,
            timeout=self.limits.timeout_seconds,
            session=self.session,
        )
        result: dict[str, list[Row]] = {}
        columns = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adjusted_close",
            "Volume": "volume",
            "Dividends": "dividends",
            "Stock Splits": "stock_splits",
        }
        for symbol in symbols:
            data = frame[symbol] if isinstance(frame.columns, pd.MultiIndex) else frame
            if data.empty:
                result[symbol] = []
                continue
            try:
                metadata = yf.Ticker(symbol, session=self.session).get_history_metadata(
                    repair=False
                )
                provider_currency = metadata["currency"]
                if provider_currency == "GBp":
                    currency, price_scale = "GBP", Decimal("0.01")
                elif isinstance(provider_currency, str) and re.fullmatch(
                    r"[A-Z]{3}", provider_currency
                ):
                    currency, price_scale = provider_currency, Decimal(1)
                else:
                    raise ValueError("invalid_provider_currency")
                rows = []
                for index, value in data.iterrows():
                    row = {"date": index.date().isoformat(), "currency": currency}
                    for source, target in columns.items():
                        number = Decimal(str(value.get(source, 0)))
                        if target in {"open", "high", "low", "close", "adjusted_close"}:
                            number *= price_scale
                        row[target] = format(number, "f")
                    rows.append(row)
                result[symbol] = rows
            except Exception:
                result[symbol] = []
        return result


def _read(path: Path, columns: Sequence[str] | None = None) -> list[Row]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if columns is not None and reader.fieldnames != list(columns):
            raise ValueError("invalid_cache_header")
        rows = list(reader)
        if any(None in row or None in row.values() for row in rows):
            raise ValueError("invalid_cache_row")
        return rows


def _write(root: Path, relative: str, columns: Sequence[str], rows: Sequence[Row]) -> bool:
    path = root / relative
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    content = buffer.getvalue().encode()
    if path.exists() and path.read_bytes() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(path, content, allowed_root=root)
    return True


def _valid_bar(row: Row, security: Row, expected: date) -> bool:
    try:
        if (
            row.get("currency", security["currency"]) != security["currency"]
            or row.get("provider_symbol", security["provider_symbol"])
            != security["provider_symbol"]
        ):
            return False
        session = date.fromisoformat(row["date"])
        if (
            session > expected
            or completed_session(
                security["venue_mic"], datetime.combine(session, datetime.max.time(), UTC)
            )
            != session
        ):
            return False
        op, high, low, close, adjusted, volume = [
            decimal(row[field])
            for field in ("open", "high", "low", "close", "adjusted_close", "volume")
        ]
        return (
            min(op, high, low, close, adjusted) > 0
            and volume >= 0
            and decimal(row.get("dividends", "0")) >= 0
            and decimal(row.get("stock_splits", "0")) >= 0
            and low <= min(op, close) <= max(op, close) <= high
        )
    except (KeyError, ValueError):
        return False


def features(security_id: str, bars: list[Row]) -> Row:
    result = dict.fromkeys(FEATURE_COLUMNS, "")
    result["security_id"] = security_id
    if not bars:
        return result
    result["price_date"] = bars[-1]["date"]
    values = [decimal(row["adjusted_close"]) for row in bars]
    if min(values) <= 0:
        raise ValueError("invalid adjusted price")
    for days in (1, 5):
        if len(values) > days:
            result[f"change_{days}d_pct"] = str(100 * (values[-1] / values[-1 - days] - 1))
    if len(values) >= 200:
        result["sma_200"] = str(sum(values[-200:]) / 200)
    if len(values) > 14:
        changes = [b - a for a, b in pairwise(values)]
        zero = Decimal(0)
        periods = Decimal(14)
        gain = (
            sum((change if change > zero else zero for change in changes[:14]), start=zero)
            / periods
        )
        loss = (
            sum((-change if change < zero else zero for change in changes[:14]), start=zero)
            / periods
        )
        for change in changes[14:]:
            gain = (gain * 13 + (change if change > zero else zero)) / periods
            loss = (loss * 13 + (-change if change < zero else zero)) / periods
        result["rsi_14"] = (
            str(Decimal(100) - Decimal(100) / (Decimal(1) + gain / loss))
            if loss
            else ("100" if gain else "50")
        )
    return result


def refresh_market(
    root: Path,
    securities: Sequence[Row],
    provider: Provider,
    *,
    now: datetime,
    limits: MarketLimits = DEFAULT_MARKET_LIMITS,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    now_text = now.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    old_latest = {row["security_id"]: row for row in _read(root / "data/market/latest.csv")}
    latest: dict[str, Row] = {}
    caches: dict[str, list[Row]] = {}
    groups: dict[tuple[date, date], list[Row]] = defaultdict(list)
    errors: dict[str, str] = {}
    changed: list[str] = []
    start_time = time.monotonic()
    calls = 0
    expected_sessions: dict[str, date] = {}
    feature_blocked: set[str] = set()
    for security in sorted(securities, key=lambda item: item["security_id"]):
        sid = security["security_id"]
        if not sid or any(
            char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
            for char in sid
        ):
            raise ValueError("unsafe security identity")
        try:
            bars = _read(root / f"data/market/prices/{sid}.csv", PRICE_COLUMNS)
        except (OSError, ValueError, csv.Error) as exc:
            bars = []
            errors[sid] = f"cache_unreadable:{type(exc).__name__}"
        caches[sid] = bars
        previous = old_latest.get(sid, {})
        latest[sid] = {key: previous.get(key, "") for key in LATEST_COLUMNS}
        latest[sid].update(
            security_id=sid,
            provider_symbol=security["provider_symbol"],
            venue_mic=security["venue_mic"],
            currency=security["currency"],
            source="yfinance",
        )
        if security.get("status", "watching") not in MONITORED_SECURITY_STATUSES:
            latest[sid].update(status="inactive", error="", expected_session="")
            continue
        try:
            expected = completed_session(security["venue_mic"], now)
            expected_sessions[sid] = expected
            latest[sid]["expected_session"] = expected.isoformat()
            valid_last = bool(bars and _valid_bar(bars[-1], security, expected))
            if valid_last:
                latest[sid].update(
                    {
                        key: bars[-1][key]
                        for key in (
                            "open",
                            "high",
                            "low",
                            "close",
                            "adjusted_close",
                            "volume",
                            "retrieved_at",
                        )
                    }
                )
                latest[sid]["price_date"] = bars[-1]["date"]
            reconciled = (
                previous.get("reconciled_at")
                if "reconciled_at" in previous
                else previous.get("retrieved_at")
            )
            correction_due = not reconciled or now - timestamp(reconciled) >= timedelta(
                days=limits.correction_days
            )
            if valid_last and bars[-1]["date"] == expected.isoformat() and not correction_due:
                latest[sid].update(status="current", error="")
                continue
            start = expected - timedelta(days=limits.cache_days)
            if bars:
                start = max(
                    start,
                    date.fromisoformat(bars[-1]["date"])
                    - timedelta(days=limits.correction_window_days),
                )
            groups[(start, expected + timedelta(days=1))].append(security)
        except (ValueError, KeyError) as exc:
            errors[sid] = str(exc)

    def retrieve(group: Sequence[Row], start: date, end: date) -> Mapping[str, list[Row]]:
        nonlocal calls
        if (
            calls >= limits.max_provider_calls
            or time.monotonic() - start_time >= limits.max_runtime_seconds
        ):
            raise RuntimeError("market_request_or_runtime_budget_exhausted")
        calls += 1
        return provider.fetch([security["provider_symbol"] for security in group], start, end)

    for (start, end), group in sorted(groups.items()):
        for offset in range(0, len(group), limits.batch_size):
            batch = group[offset : offset + limits.batch_size]
            try:
                response = retrieve(batch, start, end)
            except Exception as exc:
                response = {}
                for security in batch:
                    errors[security["security_id"]] = type(exc).__name__ + ":" + str(exc)
            for security in batch:
                sid, symbol = security["security_id"], security["provider_symbol"]
                expected = expected_sessions[sid]
                valid = [
                    row for row in response.get(symbol, []) if _valid_bar(row, security, expected)
                ]
                for attempt in range(1, limits.max_attempts):
                    if valid and max(row["date"] for row in valid) == expected.isoformat():
                        break
                    if (
                        calls >= limits.max_provider_calls
                        or time.monotonic() - start_time >= limits.max_runtime_seconds
                    ):
                        errors[sid] = "market_request_or_runtime_budget_exhausted"
                        break
                    sleep(min(2 ** (attempt - 1), 4) + random.uniform(0, 0.1))
                    try:
                        retry = retrieve([security], start, end)
                        combined = {row["date"]: row for row in valid}
                        combined.update(
                            {
                                row["date"]: row
                                for row in retry.get(symbol, [])
                                if _valid_bar(row, security, expected)
                            }
                        )
                        valid = list(combined.values())
                    except Exception as exc:
                        errors[sid] = type(exc).__name__ + ":" + str(exc)
                old_bars = {row["date"]: row for row in caches[sid]}
                action_changed = bool(old_bars) and (
                    old_latest.get(sid, {}).get("error") == "corporate_action_reconciliation_failed"
                    or any(
                        decimal(row.get(field, "0"))
                        != decimal(old_bars.get(row["date"], {}).get(field, "0"))
                        for row in valid
                        for field in ("dividends", "stock_splits")
                    )
                )
                if action_changed:
                    try:
                        full = retrieve(
                            [security], expected - timedelta(days=limits.cache_days), end
                        )
                        reconciled_bars = [
                            row
                            for row in full.get(symbol, [])
                            if _valid_bar(row, security, expected)
                        ]
                        retained_dates = {
                            day
                            for day in old_bars
                            if day >= (expected - timedelta(days=limits.cache_days)).isoformat()
                        }
                        if not retained_dates <= {row["date"] for row in reconciled_bars}:
                            raise ValueError("corporate_action_history_incomplete")
                        valid = reconciled_bars
                    except Exception:
                        errors[sid] = "corporate_action_reconciliation_failed"
                        feature_blocked.add(sid)
                        latest[sid]["reconciled_at"] = ""
                merged = dict(old_bars)
                for row in valid:
                    merged[row["date"]] = {key: row.get(key, "") for key in PRICE_COLUMNS}
                    merged[row["date"]].update(
                        currency=security["currency"],
                        provider_symbol=symbol,
                        retrieved_at=now_text,
                        source="yfinance",
                    )
                bars = [
                    row
                    for session, row in sorted(merged.items())
                    if session >= (expected - timedelta(days=limits.cache_days)).isoformat()
                ]
                if valid:
                    caches[sid] = bars
                    path = f"data/market/prices/{sid}.csv"
                    if _write(root, path, PRICE_COLUMNS, bars):
                        changed.append(path)
                    if sid not in feature_blocked:
                        latest[sid]["reconciled_at"] = now_text
                if bars:
                    latest[sid].update(
                        {
                            key: bars[-1][key]
                            for key in (
                                "open",
                                "high",
                                "low",
                                "close",
                                "adjusted_close",
                                "volume",
                                "retrieved_at",
                            )
                        }
                    )
                    latest[sid]["price_date"] = bars[-1]["date"]
                if not bars or bars[-1]["date"] != expected.isoformat():
                    errors[sid] = errors.get(sid, "required_session_missing")
                elif valid and sid not in feature_blocked:
                    errors.pop(sid, None)
    feature_rows = []
    for sid, row in latest.items():
        try:
            feature_rows.append(features(sid, [] if sid in feature_blocked else caches[sid]))
        except (ValueError, KeyError):
            errors[sid] = "invalid_historical_cache"
            feature_rows.append(features(sid, []))
        if sid in errors:
            row.update(status="stale" if row["close"] else "unavailable", error=errors[sid])
        elif row.get("price_date") == row.get("expected_session"):
            row.update(status="current", error="")
    if _write(
        root, "data/market/latest.csv", LATEST_COLUMNS, [latest[sid] for sid in sorted(latest)]
    ):
        changed.append("data/market/latest.csv")
    if _write(
        root,
        "data/market/features.csv",
        FEATURE_COLUMNS,
        sorted(feature_rows, key=lambda row: row["security_id"]),
    ):
        changed.append("data/market/features.csv")
    return {
        "status": "degraded" if errors else "succeeded",
        "exit_code": 2 if errors else 0,
        "provider_calls": calls,
        "http_requests": getattr(getattr(provider, "budget", None), "used", None),
        "failed_tickers": errors,
        "changed": changed,
    }

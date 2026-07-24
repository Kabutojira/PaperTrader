"""Normalized yfinance boundary, exchange sessions, and rolling daily-price caches."""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Protocol, cast

import exchange_calendars as xcals  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]
import yfinance as yf  # type: ignore[import-untyped]

from papertrader.atomic_io import atomic_write_csv
from papertrader.config import Settings
from papertrader.models import MarketBar, PriceBar, SecurityIdentity
from papertrader.tables import read_csv, read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    content_hash,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_iso_date,
    parse_timestamp,
    required_decimal,
    utc_now,
)

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
SAFE_SECURITY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class MarketDataError(RuntimeError):
    """Raised when provider data cannot satisfy the canonical market contract."""


class MarketDataProvider(Protocol):
    """Injectable provider interface used by network-free tests."""

    name: str

    def history(
        self,
        identity: SecurityIdentity,
        *,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        """Return provider-native daily history with actions."""


class YFinanceProvider:
    """Thin yfinance adapter; all provider values are normalized after retrieval."""

    name = "yfinance"

    def history(
        self,
        identity: SecurityIdentity,
        *,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        ticker = yf.Ticker(identity.provider_symbol)
        return ticker.history(
            start=start.isoformat(),
            end=end.isoformat(),
            interval="1d",
            auto_adjust=False,
            actions=True,
            repair=True,
            raise_errors=True,
        )


def _provider_decimal(value: object, *, label: str, default: Decimal | None = None) -> Decimal:
    if value is None or pd.isna(value):
        if default is not None:
            return default
        raise MarketDataError(f"provider field {label} is missing")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MarketDataError(f"provider field {label} is not decimal: {value!r}") from exc
    if not result.is_finite():
        raise MarketDataError(f"provider field {label} is not finite")
    return result


def _calendar(name: str) -> xcals.ExchangeCalendar:
    try:
        return xcals.get_calendar(name)
    except (KeyError, ValueError) as exc:
        raise MarketDataError(f"unknown exchange calendar {name!r}") from exc


def _session_dates(calendar_name: str, start: date, end: date) -> frozenset[date]:
    calendar = _calendar(calendar_name)
    try:
        sessions = calendar.sessions_in_range(start.isoformat(), end.isoformat())
    except ValueError as exc:
        raise MarketDataError(
            f"calendar {calendar_name} does not cover {start} through {end}"
        ) from exc
    return frozenset(timestamp.date() for timestamp in sessions)


def latest_completed_session(calendar_name: str, now: datetime) -> date:
    """Return the latest exchange session whose close is no later than ``now``."""

    if now.tzinfo is None or now.utcoffset() is None:
        raise CanonicalValueError("current time must be timezone-aware")
    instant = now.astimezone(UTC)
    calendar = _calendar(calendar_name)
    sessions = calendar.sessions_in_range(
        (instant.date() - timedelta(days=14)).isoformat(), instant.date().isoformat()
    )
    completed = [session for session in sessions if calendar.session_close(session) <= instant]
    if not completed:
        raise MarketDataError(f"no completed {calendar_name} session near {instant.date()}")
    return cast(date, completed[-1].date())


def session_open(calendar_name: str, session_date: date) -> datetime:
    """Return one exchange session's canonical UTC open timestamp."""

    calendar = _calendar(calendar_name)
    try:
        value = calendar.session_open(session_date)
    except (KeyError, ValueError) as exc:
        raise MarketDataError(
            f"{session_date.isoformat()} is not a session in {calendar_name}"
        ) from exc
    return cast(datetime, value.to_pydatetime()).astimezone(UTC)


def session_close(calendar_name: str, session_date: date) -> datetime:
    """Return one exchange session's canonical UTC close timestamp."""

    calendar = _calendar(calendar_name)
    try:
        value = calendar.session_close(session_date)
    except (KeyError, ValueError) as exc:
        raise MarketDataError(
            f"{session_date.isoformat()} is not a session in {calendar_name}"
        ) from exc
    return cast(datetime, value.to_pydatetime()).astimezone(UTC)


def load_security_identities(repository_root: Path) -> tuple[SecurityIdentity, ...]:
    """Load monitored identities and reject ticker-only or path-unsafe records."""

    identities: list[SecurityIdentity] = []
    seen_ids: set[str] = set()
    provider_keys: set[tuple[str, str, str]] = set()
    for row in read_table(repository_root, "securities"):
        if row["status"] not in {"active", "watching"}:
            continue
        required = ("security_id", "provider_symbol", "venue_mic", "currency", "instrument_type")
        missing = [field for field in required if not row[field]]
        if missing:
            raise MarketDataError(
                f"security row {row['security_id'] or '<missing>'} lacks {', '.join(missing)}"
            )
        security_id = row["security_id"]
        if not SAFE_SECURITY_ID.fullmatch(security_id):
            raise MarketDataError(f"unsafe security_id for price path: {security_id!r}")
        if not re.fullmatch(r"[A-Z0-9]{4}", row["venue_mic"]):
            raise MarketDataError(f"invalid venue MIC for {security_id}: {row['venue_mic']!r}")
        if not re.fullmatch(r"[A-Z]{3}", row["currency"]):
            raise MarketDataError(f"invalid currency for {security_id}: {row['currency']!r}")
        if any(marker in row["provider_symbol"] for marker in "\r\n"):
            raise MarketDataError(f"invalid provider symbol for {security_id}")
        if security_id in seen_ids:
            raise MarketDataError(f"duplicate security_id: {security_id}")
        provider_key = (row["provider_symbol"], row["venue_mic"], row["currency"])
        if provider_key in provider_keys:
            raise MarketDataError(f"duplicate provider identity: {provider_key!r}")
        seen_ids.add(security_id)
        provider_keys.add(provider_key)
        identities.append(
            SecurityIdentity(
                security_id=security_id,
                provider_symbol=row["provider_symbol"],
                venue_mic=row["venue_mic"],
                currency=row["currency"],
                instrument_type=row["instrument_type"],
            )
        )
    return tuple(sorted(identities, key=lambda identity: identity.security_id))


def normalize_history(
    frame: pd.DataFrame,
    identity: SecurityIdentity,
    *,
    calendar_name: str,
    retrieved_at: datetime,
    source: str,
) -> tuple[PriceBar, ...]:
    """Convert provider-native history to validated, session-aligned Decimal bars."""

    if frame.empty:
        raise MarketDataError(f"provider returned no prices for {identity.security_id}")
    if not source or any(marker in source for marker in "\r\n"):
        raise MarketDataError("market source must be a non-empty single line")
    if isinstance(frame.columns, pd.MultiIndex):
        frame = frame.copy()
        frame.columns = frame.columns.get_level_values(0)
    required_columns = {"Open", "High", "Low", "Close", "Volume"}
    missing = sorted(required_columns - set(str(column) for column in frame.columns))
    if missing:
        raise MarketDataError(f"provider history is missing columns: {missing}")
    index_dates: list[date] = []
    for raw_index in frame.index:
        try:
            timestamp = pd.Timestamp(raw_index)
        except (TypeError, ValueError) as exc:
            raise MarketDataError(f"invalid provider date index: {raw_index!r}") from exc
        index_dates.append(timestamp.date())
    sessions = _session_dates(calendar_name, min(index_dates), max(index_dates))
    by_date: dict[date, PriceBar] = {}
    normalized_retrieved_at = ensure_utc(retrieved_at)
    for (_, row), bar_date in zip(frame.iterrows(), index_dates, strict=True):
        if bar_date not in sessions:
            continue
        if bar_date in by_date:
            raise MarketDataError(
                f"provider returned duplicate session {bar_date} for {identity.security_id}"
            )
        open_price = _provider_decimal(row["Open"], label="Open")
        high = _provider_decimal(row["High"], label="High")
        low = _provider_decimal(row["Low"], label="Low")
        close = _provider_decimal(row["Close"], label="Close")
        adjusted = _provider_decimal(row.get("Adj Close"), label="Adj Close", default=close)
        raw_volume = _provider_decimal(row["Volume"], label="Volume")
        dividends = _provider_decimal(row.get("Dividends"), label="Dividends", default=Decimal("0"))
        splits = _provider_decimal(
            row.get("Stock Splits"), label="Stock Splits", default=Decimal("0")
        )
        if min(open_price, high, low, close, adjusted) <= 0:
            raise MarketDataError(f"non-positive price on {bar_date} for {identity.security_id}")
        if high < max(open_price, low, close) or low > min(open_price, high, close):
            raise MarketDataError(f"invalid OHLC range on {bar_date} for {identity.security_id}")
        if raw_volume < 0 or raw_volume != raw_volume.to_integral_value():
            raise MarketDataError(f"invalid volume on {bar_date} for {identity.security_id}")
        if dividends < 0 or splits < 0:
            raise MarketDataError(f"negative corporate action on {bar_date}")
        by_date[bar_date] = PriceBar(
            date=bar_date,
            open=open_price,
            high=high,
            low=low,
            close=close,
            adjusted_close=adjusted,
            volume=int(raw_volume),
            dividends=dividends,
            stock_splits=splits,
            currency=identity.currency,
            provider_symbol=identity.provider_symbol,
            retrieved_at=normalized_retrieved_at,
            source=source,
        )
    if not by_date:
        raise MarketDataError(f"provider returned no valid sessions for {identity.security_id}")
    return tuple(by_date[key] for key in sorted(by_date))


def price_cache_path(repository_root: Path, security_id: str) -> Path:
    """Return the safe canonical rolling price-cache path."""

    if not SAFE_SECURITY_ID.fullmatch(security_id):
        raise MarketDataError(f"unsafe security_id for price path: {security_id!r}")
    return repository_root / "data" / "market" / "prices" / f"{security_id}.csv"


def price_bar_row(bar: PriceBar) -> dict[str, object]:
    """Serialize one normalized bar in stable column order."""

    return {
        "date": bar.date.isoformat(),
        "open": decimal_text(bar.open),
        "high": decimal_text(bar.high),
        "low": decimal_text(bar.low),
        "close": decimal_text(bar.close),
        "adjusted_close": decimal_text(bar.adjusted_close),
        "volume": str(bar.volume),
        "dividends": decimal_text(bar.dividends),
        "stock_splits": decimal_text(bar.stock_splits),
        "currency": bar.currency,
        "provider_symbol": bar.provider_symbol,
        "retrieved_at": format_timestamp(bar.retrieved_at),
        "source": bar.source,
    }


def _bar_from_row(row: Mapping[str, str]) -> PriceBar:
    retrieved_at = parse_timestamp(row["retrieved_at"])
    assert retrieved_at is not None
    try:
        volume = int(row["volume"])
    except ValueError as exc:
        raise MarketDataError(f"invalid cached volume: {row['volume']!r}") from exc
    bar = PriceBar(
        date=parse_iso_date(row["date"]),
        open=required_decimal(row["open"], label="open"),
        high=required_decimal(row["high"], label="high"),
        low=required_decimal(row["low"], label="low"),
        close=required_decimal(row["close"], label="close"),
        adjusted_close=required_decimal(row["adjusted_close"], label="adjusted_close"),
        volume=volume,
        dividends=required_decimal(row["dividends"], label="dividends"),
        stock_splits=required_decimal(row["stock_splits"], label="stock_splits"),
        currency=row["currency"],
        provider_symbol=row["provider_symbol"],
        retrieved_at=retrieved_at,
        source=row["source"],
    )
    _validate_price_bar(bar)
    return bar


def _validate_price_bar(bar: PriceBar) -> None:
    prices = (bar.open, bar.high, bar.low, bar.close, bar.adjusted_close)
    if any(not price.is_finite() for price in prices) or min(prices) <= 0:
        raise MarketDataError(f"non-positive cached price on {bar.date}")
    if bar.high < max(bar.open, bar.low, bar.close) or bar.low > min(bar.open, bar.high, bar.close):
        raise MarketDataError(f"invalid cached OHLC range on {bar.date}")
    if (
        not bar.dividends.is_finite()
        or not bar.stock_splits.is_finite()
        or bar.volume < 0
        or bar.dividends < 0
        or bar.stock_splits < 0
    ):
        raise MarketDataError(f"invalid cached volume or corporate action on {bar.date}")
    if len(bar.currency) != 3 or bar.currency != bar.currency.upper():
        raise MarketDataError(f"invalid cached currency on {bar.date}")
    if (
        not bar.provider_symbol
        or not bar.source
        or any(marker in bar.provider_symbol + bar.source for marker in "\r\n")
    ):
        raise MarketDataError(f"cached bar lacks provider identity on {bar.date}")
    ensure_utc(bar.retrieved_at)


def _same_economic_bar(left: PriceBar, right: PriceBar) -> bool:
    return all(
        getattr(left, field) == getattr(right, field)
        for field in (
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
        )
    )


def read_price_cache(repository_root: Path, security_id: str) -> tuple[PriceBar, ...]:
    """Read one rolling price cache or return an empty sequence when absent."""

    path = price_cache_path(repository_root, security_id)
    if not path.exists():
        return ()
    return tuple(_bar_from_row(row) for row in read_csv(path, PRICE_COLUMNS))


def merge_price_bars(
    existing: Sequence[PriceBar],
    incoming: Sequence[PriceBar],
    *,
    retention_days: int,
) -> tuple[PriceBar, ...]:
    """Merge by trading date, choose new observations, sort, and trim the rolling window."""

    if retention_days <= 0:
        raise CanonicalValueError("price retention must be positive")
    all_bars = [*existing, *incoming]
    for bar in all_bars:
        _validate_price_bar(bar)
    identities = {(bar.currency, bar.provider_symbol) for bar in all_bars}
    if len(identities) > 1:
        raise MarketDataError("price cache contains mixed provider or currency identities")
    by_date: dict[date, PriceBar] = {}
    for bar in existing:
        if bar.date in by_date:
            raise MarketDataError(f"existing price cache contains duplicate date {bar.date}")
        by_date[bar.date] = bar
    incoming_dates: set[date] = set()
    for bar in incoming:
        if bar.date in incoming_dates:
            raise MarketDataError(f"incoming prices contain duplicate date {bar.date}")
        incoming_dates.add(bar.date)
        previous = by_date.get(bar.date)
        by_date[bar.date] = previous if previous and _same_economic_bar(previous, bar) else bar
    if not by_date:
        return ()
    newest = max(by_date)
    cutoff = newest - timedelta(days=retention_days)
    return tuple(by_date[bar_date] for bar_date in sorted(by_date) if bar_date >= cutoff)


def write_price_cache(
    repository_root: Path,
    security_id: str,
    bars: Sequence[PriceBar],
) -> None:
    """Atomically write one validated rolling cache."""

    path = price_cache_path(repository_root, security_id)
    for bar in bars:
        _validate_price_bar(bar)
    if any(bars[index - 1].date >= bars[index].date for index in range(1, len(bars))):
        raise MarketDataError("price cache must be strictly ascending and deduplicated")
    atomic_write_csv(
        path,
        PRICE_COLUMNS,
        (price_bar_row(bar) for bar in bars),
        allowed_root=repository_root,
    )


def price_content_hash(bars: Sequence[PriceBar]) -> str:
    """Hash economic values only, excluding retrieval-time formatting churn."""

    values = [
        {
            key: value
            for key, value in price_bar_row(bar).items()
            if key not in {"retrieved_at", "source"}
        }
        for bar in bars
    ]
    return content_hash(values)


def _latest_row(
    identity: SecurityIdentity,
    bar: PriceBar | None,
    *,
    retrieved_at: datetime,
    status: str,
    error: str,
    source: str,
) -> dict[str, object]:
    return {
        "security_id": identity.security_id,
        "provider_symbol": identity.provider_symbol,
        "price_date": bar.date.isoformat() if bar else "",
        "retrieved_at": format_timestamp(retrieved_at),
        "open": decimal_text(bar.open) if bar else "",
        "high": decimal_text(bar.high) if bar else "",
        "low": decimal_text(bar.low) if bar else "",
        "close": decimal_text(bar.close) if bar else "",
        "adjusted_close": decimal_text(bar.adjusted_close) if bar else "",
        "volume": str(bar.volume) if bar else "",
        "currency": identity.currency,
        "source": source,
        "status": status,
        "error": " ".join(error.split()),
    }


def update_market_data(
    repository_root: Path,
    settings: Settings,
    *,
    provider: MarketDataProvider | None = None,
    now: datetime | None = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> tuple[str, ...]:
    """Retrieve every active security sequentially and update caches without partial bad bars."""

    selected_provider = provider or YFinanceProvider()
    if selected_provider.name != settings.market_data.provider:
        raise MarketDataError(
            f"configured provider is {settings.market_data.provider}, got {selected_provider.name}"
        )
    retrieved_at = ensure_utc(now or utc_now())
    latest_rows: list[dict[str, object]] = []
    errors: list[str] = []
    for identity in load_security_identities(repository_root):
        previous = read_price_cache(repository_root, identity.security_id)
        calendar_name = settings.market_data.calendar_for(identity.venue_mic)
        expected = latest_completed_session(calendar_name, retrieved_at)
        start = (
            previous[-1].date - timedelta(days=7)
            if previous
            else retrieved_at.date()
            - timedelta(days=settings.market_data.price_retention_days + 10)
        )
        end = retrieved_at.date() + timedelta(days=1)
        failure = ""
        incoming: tuple[PriceBar, ...] = ()
        for attempt in range(1, settings.market_data.retrieval_retries + 1):
            try:
                frame = selected_provider.history(identity, start=start, end=end)
                incoming = normalize_history(
                    frame,
                    identity,
                    calendar_name=calendar_name,
                    retrieved_at=retrieved_at,
                    source=selected_provider.name,
                )
                incoming = tuple(bar for bar in incoming if bar.date <= expected)
                if not incoming:
                    raise MarketDataError(
                        f"provider returned no completed session through {expected}"
                    )
                break
            except Exception as exc:  # provider libraries expose several runtime error types
                failure = f"{type(exc).__name__}: {exc}"
                if attempt < settings.market_data.retrieval_retries:
                    sleeper(float(2 ** (attempt - 1)))
        if not incoming:
            errors.append(f"{identity.security_id}: {failure}")
            latest_rows.append(
                _latest_row(
                    identity,
                    previous[-1] if previous else None,
                    retrieved_at=retrieved_at,
                    status="error",
                    error=failure,
                    source=selected_provider.name,
                )
            )
            continue
        merged = merge_price_bars(
            previous,
            incoming,
            retention_days=settings.market_data.price_retention_days,
        )
        write_price_cache(repository_root, identity.security_id, merged)
        from papertrader.corporate_actions import persist_actions

        persist_actions(
            repository_root,
            identity.security_id,
            merged,
            source_price_hash=price_content_hash(merged),
        )
        newest = merged[-1]
        status = "ok" if newest.date >= expected else "stale"
        if status == "stale":
            errors.append(
                f"{identity.security_id}: latest price {newest.date} precedes "
                f"completed session {expected}"
            )
        latest_rows.append(
            _latest_row(
                identity,
                newest,
                retrieved_at=retrieved_at,
                status=status,
                error="" if status == "ok" else errors[-1],
                source=selected_provider.name,
            )
        )
    write_table(repository_root, "market_latest", latest_rows)
    return tuple(errors)


def daily_bar_to_market_bar(
    security_id: str,
    bar: PriceBar,
    *,
    session_open: datetime,
    fx_rate_to_base: Decimal,
) -> MarketBar:
    """Adapt a normalized daily bar to the timestamped paper-fill model."""

    normalized_open = ensure_utc(session_open)
    if normalized_open.date() != bar.date:
        raise MarketDataError("session open date does not match the daily bar")
    if not fx_rate_to_base.is_finite() or fx_rate_to_base <= 0:
        raise MarketDataError("fill FX rate must be positive")
    return MarketBar(
        security_id=security_id,
        provider_contract_id="",
        timestamp=normalized_open,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        currency=bar.currency,
        fx_rate_to_base=fx_rate_to_base,
    )

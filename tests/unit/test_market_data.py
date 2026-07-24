from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from papertrader.config import Settings
from papertrader.market_data import (
    MarketDataError,
    merge_price_bars,
    normalize_history,
    read_price_cache,
    update_market_data,
)
from papertrader.models import PriceBar, SecurityIdentity
from papertrader.tables import read_table, write_table


def _security_row(security_id: str = "sec_a") -> dict[str, str]:
    return {
        "security_id": security_id,
        "issuer_id": "issuer_a",
        "company_name": "Example Corp",
        "instrument_name": "Example common stock",
        "instrument_type": "equity",
        "ticker": "EXM",
        "exchange_code": "NYSE",
        "venue_mic": "XNYS",
        "provider_symbol": "EXM",
        "broker_symbol": "",
        "currency": "USD",
        "country": "US",
        "sector": "Industrials",
        "industry": "Testing",
        "status": "active",
        "watchlist_reason": "fixture",
        "research_summary": "Fixture security.",
        "research_page": "",
        "last_research_at": "",
        "next_review_at": "",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-20T00:00:00Z",
        "source": "fixture",
    }


def _frame(*, include_weekend: bool = False, dividend: bool = False) -> pd.DataFrame:
    dates = ["2026-07-22", "2026-07-23", "2026-07-24"]
    if include_weekend:
        dates.insert(0, "2026-07-18")
    count = len(dates)
    dividends = [Decimal("0")] * count
    if dividend:
        dividends[-2] = Decimal("0.25")
    return pd.DataFrame(
        {
            "Open": [100 + index for index in range(count)],
            "High": [102 + index for index in range(count)],
            "Low": [99 + index for index in range(count)],
            "Close": [101 + index for index in range(count)],
            "Adj Close": [101 + index for index in range(count)],
            "Volume": [1000 + index for index in range(count)],
            "Dividends": dividends,
            "Stock Splits": [0] * count,
        },
        index=pd.DatetimeIndex(dates),
    )


def _bar(day: date, retrieved_at: datetime) -> PriceBar:
    return PriceBar(
        date=day,
        open=Decimal("100"),
        high=Decimal("102"),
        low=Decimal("99"),
        close=Decimal("101"),
        adjusted_close=Decimal("101"),
        volume=1000,
        dividends=Decimal("0"),
        stock_splits=Decimal("0"),
        currency="USD",
        provider_symbol="EXM",
        retrieved_at=retrieved_at,
        source="fixture",
    )


def test_normalize_history_filters_non_sessions_and_uses_decimal_values() -> None:
    identity = SecurityIdentity("sec_a", "EXM", "XNYS", "USD", "equity")
    retrieved = datetime(2026, 7, 24, 22, tzinfo=UTC)

    bars = normalize_history(
        _frame(include_weekend=True),
        identity,
        calendar_name="XNYS",
        retrieved_at=retrieved,
        source="fake",
    )

    assert [bar.date for bar in bars] == [
        date(2026, 7, 22),
        date(2026, 7, 23),
        date(2026, 7, 24),
    ]
    assert bars[-1].close == Decimal("104")
    assert bars[-1].volume == 1003
    assert bars[-1].retrieved_at == retrieved


def test_normalize_history_rejects_invalid_ohlc() -> None:
    frame = _frame()
    frame.loc[pd.Timestamp("2026-07-24"), "High"] = 1
    identity = SecurityIdentity("sec_a", "EXM", "XNYS", "USD", "equity")

    with pytest.raises(MarketDataError, match="invalid OHLC"):
        normalize_history(
            frame,
            identity,
            calendar_name="XNYS",
            retrieved_at=datetime(2026, 7, 24, 22, tzinfo=UTC),
            source="fake",
        )


@given(st.lists(st.integers(min_value=0, max_value=800), min_size=1, unique=True))
@hypothesis_settings(max_examples=30)
def test_rolling_cache_property_never_keeps_more_than_365_calendar_days(
    ages: list[int],
) -> None:
    retrieved = datetime(2026, 7, 24, tzinfo=UTC)
    newest = date(2026, 7, 24)
    bars = [_bar(newest - timedelta(days=age), retrieved) for age in ages]

    merged = merge_price_bars(bars, (), retention_days=365)

    assert list(merged) == sorted(merged, key=lambda bar: bar.date)
    assert merged[-1].date - merged[0].date <= timedelta(days=365)
    assert len({bar.date for bar in merged}) == len(merged)


def test_merge_preserves_existing_bar_for_timestamp_only_refresh() -> None:
    first_retrieval = datetime(2026, 7, 24, 20, tzinfo=UTC)
    original = _bar(date(2026, 7, 24), first_retrieval)
    refreshed = replace(original, retrieved_at=first_retrieval + timedelta(hours=1))

    unchanged = merge_price_bars((original,), (refreshed,), retention_days=365)
    corrected = merge_price_bars(
        (original,),
        (replace(refreshed, close=Decimal("100.5")),),
        retention_days=365,
    )

    assert unchanged == (original,)
    assert corrected[0].retrieved_at == refreshed.retrieved_at
    assert corrected[0].close == Decimal("100.5")


class _FakeProvider:
    name = "yfinance"

    def __init__(self, frame: pd.DataFrame | None = None, failure: Exception | None = None) -> None:
        self.frame = frame
        self.failure = failure
        self.calls = 0

    def history(
        self,
        identity: SecurityIdentity,
        *,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        del identity, start, end
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        assert self.frame is not None
        return self.frame


def test_market_update_merges_cache_and_persists_corporate_actions(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    write_table(sandbox_repository, "securities", [_security_row()])
    provider = _FakeProvider(_frame(dividend=True))
    now = datetime(2026, 7, 24, 22, tzinfo=UTC)

    assert (
        update_market_data(
            sandbox_repository,
            sandbox_settings,
            provider=provider,
            now=now,
            sleeper=lambda _: None,
        )
        == ()
    )

    cache = read_price_cache(sandbox_repository, "sec_a")
    assert cache[-1].date == date(2026, 7, 24)
    assert cache[0].date >= cache[-1].date - timedelta(days=365)
    assert read_table(sandbox_repository, "market_latest")[0]["status"] == "ok"
    actions = read_table(sandbox_repository, "corporate_actions")
    assert [(row["action_type"], row["value"]) for row in actions] == [("dividend", "0.25")]


def test_failed_retrieval_retries_and_does_not_write_price_cache(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    write_table(sandbox_repository, "securities", [_security_row()])
    provider = _FakeProvider(failure=RuntimeError("offline"))

    errors = update_market_data(
        sandbox_repository,
        sandbox_settings,
        provider=provider,
        now=datetime(2026, 7, 24, 22, tzinfo=UTC),
        sleeper=lambda _: None,
    )

    assert provider.calls == sandbox_settings.market_data.retrieval_retries
    assert errors and "offline" in errors[0]
    assert read_price_cache(sandbox_repository, "sec_a") == ()
    assert read_table(sandbox_repository, "market_latest")[0]["status"] == "error"

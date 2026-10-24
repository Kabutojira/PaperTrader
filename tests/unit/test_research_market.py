from __future__ import annotations

import copy
import csv
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]
import pytest

import papertrader.research_market as research_market
from papertrader.research_market import (
    CALENDARS,
    LATEST_COLUMNS,
    MarketLimits,
    RequestBudget,
    YFinanceResearchProvider,
    _write,
    completed_session,
    features,
    refresh_market,
)
from papertrader.research_ratings import rating_thresholds, reprice
from papertrader.research_state import Row


def _security(sid: str = "sec_good", symbol: str = "GOOD") -> Row:
    return {"security_id": sid, "provider_symbol": symbol, "currency": "USD", "venue_mic": "XNAS"}


def _bar(day: str, price: str = "100", split: str = "0") -> Row:
    number = Decimal(price)
    return {
        "date": day,
        "open": price,
        "close": price,
        "high": str(number + 1),
        "low": str(number - 1),
        "adjusted_close": price,
        "volume": "1000",
        "dividends": "0",
        "stock_splits": split,
    }


class FakeProvider:
    def __init__(self, rows: dict[str, list[Row]]) -> None:
        self.rows = rows
        self.calls: list[tuple[list[str], date, date]] = []

    def fetch(self, symbols: list[str], start: date, end: date) -> dict[str, list[Row]]:
        self.calls.append((list(symbols), start, end))
        return {symbol: self.rows.get(symbol, []) for symbol in symbols}


class SequencedProvider:
    def __init__(self, responses: list[dict[str, list[Row]]]) -> None:
        self.responses = responses
        self.calls: list[tuple[list[str], date, date]] = []

    def fetch(self, symbols: list[str], start: date, end: date) -> dict[str, list[Row]]:
        self.calls.append((list(symbols), start, end))
        response = self.responses.pop(0)
        return {symbol: response.get(symbol, []) for symbol in symbols}


def _latest(root: Path) -> dict[str, Row]:
    with (root / "data/market/latest.csv").open() as stream:
        return {row["security_id"]: row for row in csv.DictReader(stream)}


def test_closed_market_repeat_makes_zero_calls_and_zero_writes(tmp_path: Path) -> None:
    provider = FakeProvider({"GOOD": [_bar("2026-10-16")]})
    first = refresh_market(
        tmp_path, [_security()], provider, now=datetime(2026, 10, 16, 22, tzinfo=UTC)
    )
    assert first["exit_code"] == 0 and len(provider.calls) == 1
    second = refresh_market(
        tmp_path, [_security()], provider, now=datetime(2026, 10, 18, 17, tzinfo=UTC)
    )
    assert second["provider_calls"] == 0 and second["changed"] == []
    assert len(provider.calls) == 1
    assert _latest(tmp_path)["sec_good"]["venue_mic"] == "XNAS"


def test_inactive_security_preserves_last_good_bar_without_provider_call(tmp_path: Path) -> None:
    security = {**_security(), "status": "watching"}
    provider = FakeProvider({"GOOD": [_bar("2026-10-16")]})
    refresh_market(tmp_path, [security], provider, now=datetime(2026, 10, 16, 22, tzinfo=UTC))
    cache = (tmp_path / "data/market/prices/sec_good.csv").read_bytes()

    result = refresh_market(
        tmp_path,
        [{**security, "status": "acquired"}],
        provider,
        now=datetime(2026, 10, 23, 22, tzinfo=UTC),
    )

    assert result["status"] == "succeeded" and result["provider_calls"] == 0
    assert len(provider.calls) == 1
    assert (tmp_path / "data/market/prices/sec_good.csv").read_bytes() == cache
    assert {
        "price_date": "2026-10-16",
        "close": "100",
        "status": "inactive",
        "error": "",
        "expected_session": "",
    }.items() <= _latest(tmp_path)["sec_good"].items()


def test_exchange_sessions_holidays_and_different_closes() -> None:
    assert completed_session("XNAS", datetime(2026, 7, 5, 22, tzinfo=UTC)) == date(2026, 7, 2)
    assert completed_session("XHKG", datetime(2026, 10, 16, 10, tzinfo=UTC)) == date(2026, 10, 16)
    assert completed_session("XNAS", datetime(2026, 10, 16, 10, tzinfo=UTC)) == date(2026, 10, 15)


def test_catalog_exchange_calendar_aliases_are_supported() -> None:
    assert {mic: CALENDARS[mic] for mic in ("XKOS", "XFRA", "XWBO", "XOTC")} == {
        "XKOS": "XKRX",
        "XFRA": "XFRA",
        "XWBO": "XWBO",
        "XOTC": "XNYS",
    }
    for mic in ("XKOS", "XFRA", "XWBO", "XOTC"):
        assert completed_session(mic, datetime(2026, 10, 16, 22, tzinfo=UTC)) == date(2026, 10, 16)


def test_yfinance_minor_unit_metadata_normalizes_only_that_symbol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    index = pd.DatetimeIndex(["2026-10-16"])
    anic = pd.DataFrame(
        {
            "Open": [120],
            "High": [125],
            "Low": [119],
            "Close": [123],
            "Adj Close": [123],
            "Volume": [1000],
            "Dividends": [0],
            "Stock Splits": [0],
        },
        index=index,
    )
    bad = anic.copy()
    frame = pd.concat({"ANIC.L": anic, "BAD.L": bad}, axis=1)
    metadata_sessions: list[object] = []

    class MetadataTicker:
        def __init__(self, symbol: str, session: object) -> None:
            metadata_sessions.append(session)
            self.symbol = symbol

        def get_history_metadata(self, *, repair: bool) -> dict[str, str]:
            assert repair is False
            if self.symbol == "BAD.L":
                raise KeyError("currency")
            return {"currency": "GBp"}

    monkeypatch.setattr(research_market.yf, "download", lambda *args, **kwargs: frame)
    monkeypatch.setattr(research_market.yf, "Ticker", MetadataTicker)
    provider = YFinanceResearchProvider(MarketLimits())
    rows = provider.fetch(["ANIC.L", "BAD.L"], date(2026, 10, 15), date(2026, 10, 17))
    assert rows["ANIC.L"][0]["currency"] == "GBP"
    assert rows["ANIC.L"][0]["close"] == "1.23"
    assert rows["ANIC.L"][0]["volume"] == "1000"
    assert rows["BAD.L"] == []
    assert metadata_sessions == [provider.session, provider.session]


def test_one_bad_ticker_preserves_good_cache_and_retries_only_failed_symbol(tmp_path: Path) -> None:
    securities = [_security(), _security("sec_bad", "BAD")]
    provider = FakeProvider({"GOOD": [_bar("2026-10-15")], "BAD": [_bar("2026-10-15")]})
    refresh_market(tmp_path, securities, provider, now=datetime(2026, 10, 15, 22, tzinfo=UTC))
    old_bad = (tmp_path / "data/market/prices/sec_bad.csv").read_bytes()
    invalid = _bar("2026-10-16")
    invalid["close"] = "NaN"
    provider.rows = {"GOOD": [_bar("2026-10-16", "105")], "BAD": [invalid]}
    result = refresh_market(
        tmp_path,
        securities,
        provider,
        now=datetime(2026, 10, 16, 22, tzinfo=UTC),
        sleep=lambda _: None,
    )
    assert result["exit_code"] == 2
    assert set(result["failed_tickers"]) == {"sec_bad"}
    assert provider.calls[-1][0] == ["BAD"]
    assert (tmp_path / "data/market/prices/sec_bad.csv").read_bytes() == old_bad
    assert _latest(tmp_path)["sec_good"]["close"] == "105"
    assert _latest(tmp_path)["sec_bad"]["status"] == "stale"
    assert _latest(tmp_path)["sec_bad"]["close"] == "100"


def test_periodic_correction_fetches_bounded_window_and_replaces_observed_bar(
    tmp_path: Path,
) -> None:
    provider = FakeProvider({"GOOD": [_bar("2026-10-16")]})
    refresh_market(tmp_path, [_security()], provider, now=datetime(2026, 10, 16, 22, tzinfo=UTC))
    latest = _latest(tmp_path)
    latest["sec_good"]["reconciled_at"] = "2026-10-01T22:00:00Z"
    _write(tmp_path, "data/market/latest.csv", LATEST_COLUMNS, list(latest.values()))
    provider.rows = {"GOOD": [_bar("2026-10-16", "101")]}
    result = refresh_market(
        tmp_path, [_security()], provider, now=datetime(2026, 10, 18, 22, tzinfo=UTC)
    )
    assert result["provider_calls"] == 1
    assert (provider.calls[-1][2] - provider.calls[-1][1]).days == 8
    assert _latest(tmp_path)["sec_good"]["close"] == "101"


def test_split_reconciles_only_affected_symbol_historical_cache(tmp_path: Path) -> None:
    provider = FakeProvider({"GOOD": [_bar("2026-10-15")]})
    refresh_market(tmp_path, [_security()], provider, now=datetime(2026, 10, 15, 22, tzinfo=UTC))
    provider.rows = {"GOOD": [_bar("2026-10-15", "25"), _bar("2026-10-16", "25", "4")]}
    result = refresh_market(
        tmp_path, [_security()], provider, now=datetime(2026, 10, 16, 22, tzinfo=UTC)
    )
    assert result["provider_calls"] == 2
    assert (provider.calls[-1][2] - provider.calls[-1][1]).days == 366
    assert result["exit_code"] == 0
    with (tmp_path / "data/market/prices/sec_good.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["close"] == "25"


def test_failed_corporate_action_reconciliation_forces_full_retry(tmp_path: Path) -> None:
    provider = SequencedProvider(
        [
            {"GOOD": [_bar("2026-10-15")]},
            {"GOOD": [_bar("2026-10-15", "25"), _bar("2026-10-16", "25", "4")]},
            {"GOOD": [_bar("2026-10-16", "25", "4")]},
            {"GOOD": [_bar("2026-10-16", "25", "4")]},
            {"GOOD": [_bar("2026-10-15", "25"), _bar("2026-10-16", "25", "4")]},
        ]
    )
    refresh_market(tmp_path, [_security()], provider, now=datetime(2026, 10, 15, 22, tzinfo=UTC))
    failed = refresh_market(
        tmp_path, [_security()], provider, now=datetime(2026, 10, 16, 22, tzinfo=UTC)
    )
    assert failed["failed_tickers"] == {"sec_good": "corporate_action_reconciliation_failed"}
    assert _latest(tmp_path)["sec_good"]["reconciled_at"] == ""

    retried = refresh_market(
        tmp_path, [_security()], provider, now=datetime(2026, 10, 16, 23, tzinfo=UTC)
    )
    assert retried["provider_calls"] == 2
    assert retried["exit_code"] == 0
    assert _latest(tmp_path)["sec_good"]["status"] == "current"


def test_provider_budget_stops_calls_without_starving_successful_symbol(tmp_path: Path) -> None:
    provider = FakeProvider({"GOOD": [_bar("2026-10-16")], "OTHER": [_bar("2026-10-16")]})
    result = refresh_market(
        tmp_path,
        [_security(), _security("sec_other", "OTHER")],
        provider,
        now=datetime(2026, 10, 16, 22, tzinfo=UTC),
        limits=MarketLimits(max_provider_calls=1, batch_size=1),
        sleep=lambda _: None,
    )
    assert len(provider.calls) == 1
    assert _latest(tmp_path)["sec_good"]["status"] == "current"
    assert result["failed_tickers"].keys() == {"sec_other"}
    budget = RequestBudget(1, 100)
    budget.take()
    with pytest.raises(RuntimeError, match="budget_exhausted"):
        budget.take()


def test_features_need_sufficient_observations() -> None:
    assert features("sec", [_bar("2026-10-16")])["rsi_14"] == ""
    flat = [_bar(f"2026-01-{day:02d}") for day in range(1, 21)]
    assert features("sec", flat)["rsi_14"] == "50"
    rising = [_bar(f"2026-01-{day:02d}", str(100 + day)) for day in range(1, 21)]
    assert features("sec", rising)["rsi_14"] == "100"


def _assessment() -> Row:
    return {
        "security_id": "sec_good",
        "research_status": "supported",
        "assessed_at": "2026-10-01T00:00:00Z",
        "valid_until": "2026-10-31T00:00:00Z",
        "currency": "USD",
        "confidence": "medium",
        "bear_fair_value": "50",
        "base_fair_value": "150",
        "bull_fair_value": "200",
        "bear_probability_pct": "30",
        "base_probability_pct": "50",
        "bull_probability_pct": "20",
        "method": "earnings_multiple",
        "method_rationale": "Normalized issuer earnings at a stated multiple",
        "source_ids": "source_fixture",
        "thesis": "Fixture thesis",
        **dict.fromkeys(
            (
                "key_assumptions",
                "downside",
                "catalysts",
                "invalidation_conditions",
                "bear_assumptions",
                "base_assumptions",
                "bull_assumptions",
            ),
            "Cited fixture assumption",
        ),
        "horizon_months": "12",
    }


def test_repricing_is_confidence_adjusted_and_does_not_rewrite_research() -> None:
    assessment = _assessment()
    before = copy.deepcopy(assessment)
    market = {
        "security_id": "sec_good",
        "venue_mic": "XNAS",
        "close": "100",
        "currency": "USD",
        "status": "current",
        "price_date": "2026-10-16",
        "expected_session": "2026-10-16",
    }
    result = reprice(assessment, market, now=datetime(2026, 10, 18, tzinfo=UTC))
    assert result["rating"] == "buy"
    assert Decimal(result["weighted_fair_value"]) == 130
    assert Decimal(result["adjusted_return_pct"]) == 21
    market["close"] = "200"
    assert reprice(assessment, market, now=datetime(2026, 10, 18, tzinfo=UTC))["rating"] == "sell"
    assert assessment == before


def test_rating_base_return_gates_are_configurable(tmp_path: Path) -> None:
    (tmp_path / "research.ini").write_text(
        """[ratings]
strong_buy_return_pct = 40
buy_return_pct = 20
sell_return_pct = -10
strong_sell_return_pct = -25
buy_minimum_base_return_pct = 15
strong_buy_minimum_base_return_pct = 30
minimum_confidence = medium
strong_buy_minimum_confidence = high
"""
    )
    thresholds = rating_thresholds(tmp_path)
    assert thresholds.buy_minimum_base_return == 15
    assert thresholds.strong_buy_minimum_base_return == 30


def test_repricing_rejects_wrong_security_identity() -> None:
    market = {
        "security_id": "sec_other",
        "venue_mic": "XNAS",
        "close": "100",
        "currency": "USD",
        "status": "current",
        "price_date": "2026-10-16",
        "expected_session": "2026-10-16",
    }
    result = reprice(_assessment(), market, now=datetime(2026, 10, 18, tzinfo=UTC))
    assert result == {
        "rating": "unrated",
        "reason": "market_identity_mismatch",
        "weighted_fair_value": "",
        "expected_return_pct": "",
        "adjusted_return_pct": "",
        "base_return_pct": "",
    }


@pytest.mark.parametrize("missing", ["security_id", "venue_mic", "price_date"])
def test_repricing_rejects_missing_market_identity_or_freshness(missing: str) -> None:
    market = {
        "security_id": "sec_good",
        "venue_mic": "XNAS",
        "close": "100",
        "currency": "USD",
        "status": "current",
        "price_date": "2026-10-16",
        "expected_session": "2026-10-16",
    }
    del market[missing]
    result = reprice(_assessment(), market, now=datetime(2026, 10, 18, tzinfo=UTC))
    assert result["rating"] == "unrated"


def test_repricing_rejects_old_session_even_when_tagged_current() -> None:
    market = {
        "security_id": "sec_good",
        "venue_mic": "XNAS",
        "close": "100",
        "currency": "USD",
        "status": "current",
        "price_date": "2026-10-13",
        "expected_session": "2026-10-13",
    }
    result = reprice(_assessment(), market, now=datetime(2026, 10, 16, 22, tzinfo=UTC))
    assert result["rating"] == "unrated"
    assert result["reason"] == "market_stale_or_unavailable"


@pytest.mark.parametrize(
    "reason", ["expired", "unsupported", "low_confidence", "stale_price", "split"]
)
def test_unsupported_or_stale_research_never_becomes_current_rating(reason: str) -> None:
    assessment = _assessment()
    market = {
        "security_id": "sec_good",
        "venue_mic": "XNAS",
        "close": "100",
        "currency": "USD",
        "status": "current",
        "price_date": "2026-10-16",
        "expected_session": "2026-10-16",
    }
    if reason == "expired":
        assessment["valid_until"] = "2026-10-17T00:00:00Z"
    if reason == "unsupported":
        assessment["research_status"] = "valuation_unsupported"
    if reason == "low_confidence":
        assessment["confidence"] = "low"
    if reason == "stale_price":
        market["status"] = "stale"
    result = reprice(
        assessment,
        market,
        now=datetime(2026, 10, 18, tzinfo=UTC),
        latest_split_date="2026-10-16" if reason == "split" else "",
    )
    assert result["rating"] == "unrated"

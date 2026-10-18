from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.config import Settings
from papertrader.financealerts import BITCOIN, sync_financealerts
from papertrader.market_data import latest_completed_session
from papertrader.models import OrderLegSpec
from papertrader.orders import OrderError, validate_leg
from papertrader.research import ResearchStateError, import_watchlist
from papertrader.tables import read_table


def metadata(symbol: str) -> dict[str, object]:
    return {
        "symbol": symbol,
        "quoteType": "EQUITY",
        "longName": "Example Inc.",
        "exchange": "NMS",
        "currency": "USD",
        "country": "United States",
        "sector": "Technology",
        "industry": "Software",
    }


def test_additive_import_aliases_and_no_research_or_portfolio_changes(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    protected = {
        path: path.read_bytes()
        for path in (sandbox_repository / "data").rglob("*")
        if path.is_file() and path.name != "securities.csv"
    }
    result = sync_financealerts(
        sandbox_repository,
        sandbox_settings,
        "GOOG\nGOOGL\nBTCUSD\nBTC-USD\nTEST\n",
        lookup=metadata,
    )
    assert result["created"] == ["BTCUSD", "GOOGL", "TEST"]
    assert result["failed"] == {}
    rows = read_table(sandbox_repository, "securities")
    assert {row["ticker"] for row in rows} == {"GOOGL", "BTCUSD", "TEST"}
    bitcoin = next(row for row in rows if row["ticker"] == "BTCUSD")
    assert bitcoin["instrument_type"] == "cryptocurrency"
    assert bitcoin["status"] == "watchlist"
    assert all(not row["research_page"] and not row["research_summary"] for row in rows)
    assert protected == {path: path.read_bytes() for path in protected}
    before = (sandbox_repository / "data/tables/securities.csv").read_bytes()
    again = sync_financealerts(
        sandbox_repository, sandbox_settings, "GOOGL\nGOOG\nBTC-USD\nTEST\n", lookup=metadata
    )
    assert again["created"] == []
    assert again["failed"] == {}
    assert before == (sandbox_repository / "data/tables/securities.csv").read_bytes()


def test_failed_imports_are_reported_without_blocking_valid_symbols(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    def lookup(symbol: str) -> dict[str, object]:
        if symbol == "BAD":
            return {"symbol": symbol}
        if symbol == "ERROR":
            raise OSError("provider unavailable")
        return metadata(symbol)

    result = sync_financealerts(
        sandbox_repository, sandbox_settings, "BAD\nERROR\n../invalid\nGOOD\n", lookup=lookup
    )
    assert result["created"] == ["GOOD"]
    assert set(result["failed"]) == {"BAD", "ERROR", "../invalid"}


def test_bitcoin_exception_does_not_allow_other_crypto_or_trading(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    assert "cryptocurrency" not in sandbox_settings.risk.allowed_instruments
    assert "XOFF" not in sandbox_settings.risk.allowed_exchanges
    assert sandbox_settings.market_data.calendar_for("XOFF") == "24/7"
    assert (
        latest_completed_session("24/7", datetime(2026, 10, 18, 12, tzinfo=UTC)).isoformat()
        == "2026-10-17"
    )
    invalid = dict(BITCOIN, ticker="ETHUSD", provider_symbol="ETH-USD")
    with pytest.raises(ResearchStateError, match="instrument_type is not allowed"):
        import_watchlist(
            sandbox_repository,
            sandbox_settings,
            {
                "source": "https://finance.yahoo.com/",
                "watchlist_reason": "Monitor",
                "securities": [invalid],
            },
        )
    with pytest.raises(OrderError, match="unsupported instrument type"):
        validate_leg(
            OrderLegSpec(
                leg_id="btc",
                action="buy",
                side="long",
                instrument_type="cryptocurrency",
                security_id="btc",
                provider_contract_id="",
                option_type="",
                expiry=None,
                strike=None,
                quantity=Decimal("1"),
                contract_multiplier=Decimal("1"),
                limit_price=None,
                currency="USD",
            )
        )

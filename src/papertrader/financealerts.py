"""Additive FinanceAlerts identity import; no research or trading side effects."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from pathlib import Path

import yfinance as yf  # type: ignore[import-untyped]

from papertrader.config import Settings
from papertrader.research import ResearchStateError, import_watchlist
from papertrader.tables import read_table

SOURCE = "https://github.com/Stell0/financealerts/blob/main/config/tickers.txt"
ALIASES = {"GOOG": "GOOGL", "BTC-USD": "BTCUSD"}
SYMBOL = re.compile(r"^[A-Z0-9][A-Z0-9.^=+-]{0,39}$")
EXCHANGES = {
    "NMS": "XNAS",
    "NGM": "XNAS",
    "NCM": "XNAS",
    "NYQ": "XNYS",
    "ASE": "XNYS",
    "PCX": "XNYS",
    "PNK": "XOTC",
    "OQB": "XOTC",
    "PAR": "XPAR",
    "AMS": "XAMS",
    "GER": "XETR",
    "FRA": "XFRA",
    "LSE": "XLON",
    "ASX": "XASX",
    "HKG": "XHKG",
    "KOE": "XKOS",
    "VIE": "XWBO",
    "MIL": "XMIL",
}
COUNTRIES = {
    "United States": "US",
    "United Kingdom": "GB",
    "France": "FR",
    "Germany": "DE",
    "Netherlands": "NL",
    "Italy": "IT",
    "Australia": "AU",
    "Canada": "CA",
    "China": "CN",
    "Hong Kong": "HK",
    "South Korea": "KR",
    "Israel": "IL",
    "Ireland": "IE",
    "Taiwan": "TW",
    "Brazil": "BR",
    "Switzerland": "CH",
    "Austria": "AT",
    "Sweden": "SE",
    "Denmark": "DK",
    "Luxembourg": "LU",
    "Belgium": "BE",
    "Singapore": "SG",
}
BITCOIN = {
    "company_name": "Bitcoin",
    "instrument_name": "Bitcoin / US Dollar (watch only)",
    "instrument_type": "cryptocurrency",
    "ticker": "BTCUSD",
    "exchange_code": "CCC",
    "venue_mic": "XOFF",
    "provider_symbol": "BTC-USD",
    "currency": "USD",
    "country": "ZZ",
    "sector": "Cryptocurrency",
    "industry": "Digital assets",
}


def canonical_ticker(value: str) -> str:
    symbol = value.strip().upper()
    if not SYMBOL.fullmatch(symbol):
        raise ResearchStateError(f"invalid FinanceAlerts ticker: {value!r}")
    return ALIASES.get(symbol, symbol)


def yahoo_identity(symbol: str) -> Mapping[str, object]:
    return dict(yf.Ticker(symbol).get_info())


def validated_identity(symbol: str, info: Mapping[str, object]) -> dict[str, str]:
    """Require provider identity, venue, currency and issuer metadata before import."""
    if info.get("symbol") != symbol or info.get("quoteType") != "EQUITY":
        raise ResearchStateError(f"unverified equity identity for {symbol}")
    values = {
        key: str(info.get(key) or "").strip()
        for key in ("longName", "exchange", "currency", "country", "sector", "industry")
    }
    if not all(values.values()):
        raise ResearchStateError(f"incomplete provider metadata for {symbol}")
    if values["exchange"] not in EXCHANGES or values["country"] not in COUNTRIES:
        raise ResearchStateError(f"unsupported provider venue/country for {symbol}")
    return {
        "company_name": values["longName"],
        "instrument_name": values["longName"],
        "instrument_type": "equity",
        "ticker": symbol,
        "exchange_code": values["exchange"],
        "venue_mic": EXCHANGES[values["exchange"]],
        "provider_symbol": symbol,
        "currency": values["currency"],
        "country": COUNTRIES[values["country"]],
        "sector": values["sector"],
        "industry": values["industry"],
    }


def sync_financealerts(
    repository_root: Path,
    settings: Settings,
    tickers: str,
    *,
    lookup: Callable[[str], Mapping[str, object]] = yahoo_identity,
) -> dict[str, object]:
    """Import each missing identity through watchlist validation and report every failure."""
    if len(tickers) > 100_000:
        raise ResearchStateError("FinanceAlerts ticker file exceeds size limit")
    existing = {
        canonical_ticker(row[field])
        for row in read_table(repository_root, "securities")
        for field in ("ticker", "provider_symbol")
    }
    created: list[str] = []
    unchanged: list[str] = []
    failed: dict[str, str] = {}
    requested: set[str] = set()
    for raw in tickers.splitlines():
        if not raw.strip():
            continue
        try:
            requested.add(canonical_ticker(raw))
        except ResearchStateError as error:
            failed[raw] = str(error)
    for symbol in sorted(requested):
        if symbol in existing:
            unchanged.append(symbol)
            continue
        try:
            fields = (
                dict(BITCOIN) if symbol == "BTCUSD" else validated_identity(symbol, lookup(symbol))
            )
            result = import_watchlist(
                repository_root,
                settings,
                {
                    "watchlist_reason": "FinanceAlerts monitoring; identity only.",
                    "source": SOURCE,
                    "securities": [fields],
                },
            )
            (created if result["created"] else unchanged).append(symbol)
            existing.add(symbol)
        except Exception as error:
            failed[symbol] = str(error)
    return {"created": created, "unchanged": unchanged, "failed": failed}

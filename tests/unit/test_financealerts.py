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


def test_committed_pull_persists_failed_import_issue_and_resolves_on_recovery(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from papertrader.financealerts import sync_committed_financealerts

    monkeypatch.setattr(
        "papertrader.financealerts.read_ticker_snapshot", lambda: ("a" * 40, "BTCUSD\n")
    )
    result = sync_committed_financealerts(sandbox_repository, sandbox_settings)
    assert result["created"] == ["BTCUSD"]
    assert result["source_revision"] == "a" * 40
    assert read_table(sandbox_repository, "securities")[0]["source"].endswith(
        "/" + "a" * 40 + "/config/tickers.txt"
    )
    before = (sandbox_repository / "data/tables/securities.csv").read_bytes()
    assert sync_committed_financealerts(sandbox_repository, sandbox_settings)["created"] == []
    assert before == (sandbox_repository / "data/tables/securities.csv").read_bytes()

    def unavailable() -> tuple[str, str]:
        raise OSError("source unavailable")

    monkeypatch.setattr("papertrader.financealerts.read_ticker_snapshot", unavailable)
    failed = sync_committed_financealerts(sandbox_repository, sandbox_settings)
    assert failed["failed"] == {"source": "source unavailable"}
    issues = read_table(sandbox_repository, "issues")
    assert len(issues) == 1
    assert issues[0]["issue_code"] == "financealerts_sync_failed"
    assert issues[0]["impact"] == "operational_only"
    monkeypatch.setattr(
        "papertrader.financealerts.read_ticker_snapshot", lambda: ("a" * 40, "BTCUSD\n")
    )
    sync_committed_financealerts(sandbox_repository, sandbox_settings)
    assert read_table(sandbox_repository, "issues")[0]["status"] == "resolved"


def test_snapshot_fetch_uses_one_immutable_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    from papertrader.financealerts import read_ticker_snapshot

    urls: list[str] = []

    def fetch(url: str) -> str:
        urls.append(url)
        return '{"sha":"' + "b" * 40 + '"}' if len(urls) == 1 else "GOOG\nBTCUSD\n"

    monkeypatch.setattr("papertrader.financealerts._remote_text", fetch)
    assert read_ticker_snapshot() == ("b" * 40, "GOOG\nBTCUSD\n")
    assert "/" + "b" * 40 + "/" in urls[1]


def test_sync_cli_failure_exit_and_research_records_unchanged(
    sandbox_repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from papertrader.cli import main

    monkeypatch.setenv("WIKI_PATH", str(sandbox_repository / "data/wiki"))
    monkeypatch.setattr(
        "papertrader.financealerts.read_ticker_snapshot", lambda: ("a" * 40, "../bad\nBTCUSD\n")
    )
    assert main(["--repository", str(sandbox_repository), "watchlist", "sync-financealerts"]) == 1
    assert {r["ticker"] for r in read_table(sandbox_repository, "securities")} == {"BTCUSD"}
    assert read_table(sandbox_repository, "security_assessments") == []
    assert read_table(sandbox_repository, "portfolio") == []


def test_real_registry_converges_without_rewriting_existing_research(
    repository_root: Path,
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    import csv

    from papertrader.tables import write_table

    fixtures = repository_root / "tests/fixtures/financealerts"
    with (fixtures / "securities.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    write_table(sandbox_repository, "securities", rows)
    protected = {
        path: path.read_bytes()
        for path in (sandbox_repository / "data").rglob("*")
        if path.is_file() and path.name != "securities.csv"
    }

    def no_lookup(symbol: str) -> dict[str, object]:
        raise AssertionError(f"Existing identity should not require a lookup: {symbol}")

    result = sync_financealerts(
        sandbox_repository,
        sandbox_settings,
        (fixtures / "tickers.txt").read_text(),
        lookup=no_lookup,
    )
    assert result["failed"] == {}
    assert result["created"] == ["BTCUSD"]
    output = read_table(sandbox_repository, "securities")
    assert len(output) == 93
    assert {row["security_id"]: row for row in output if row["ticker"] != "BTCUSD"} == {
        row["security_id"]: row for row in rows
    }
    assert {path: path.read_bytes() for path in protected} == protected
    before = (sandbox_repository / "data/tables/securities.csv").read_bytes()
    assert (
        sync_financealerts(
            sandbox_repository,
            sandbox_settings,
            (fixtures / "tickers.txt").read_text(),
            lookup=no_lookup,
        )["created"]
        == []
    )
    assert before == (sandbox_repository / "data/tables/securities.csv").read_bytes()

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.atomic_io import atomic_write_text
from papertrader.config import Settings
from papertrader.daily import (
    DailyRunError,
    execute_agent_batch,
    finalize_daily_run,
    prepare_daily_run,
)
from papertrader.execution import ensure_initial_capital
from papertrader.integrity import validate_integrity
from papertrader.market_data import write_price_cache
from papertrader.models import OrderLegSpec, PriceBar, ReferencePrice
from papertrader.orders import create_paper_order, create_signal
from papertrader.portfolio import build_risk_state
from papertrader.tables import read_table, write_table
from papertrader.wiki import lint_wiki

NOW = datetime(2026, 7, 24, 22, tzinfo=UTC)


def test_daily_preparation_enqueues_allocation_maintenance_sequentially(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    idea_id = "idea_daily_maintenance"
    security_id = "sec_daily_maintenance"
    atomic_write_text(
        sandbox_repository / "data" / "wiki" / "ideas" / f"{idea_id}.md",
        "---\ntitle: Daily maintenance idea\ntype: idea\nstatus: maintained\n---\n\n# Idea\n",
        allowed_root=sandbox_repository,
    )
    research_page = f"data/wiki/securities/{security_id}.md"
    atomic_write_text(
        sandbox_repository / research_page,
        (
            "---\ntitle: Daily maintenance security\ntype: security\nstatus: maintained\n"
            f"---\n\n# Security\n\n[[ideas/{idea_id}]]\n"
        ),
        allowed_root=sandbox_repository,
    )
    write_table(
        sandbox_repository,
        "securities",
        [
            {
                "security_id": security_id,
                "issuer_id": "issuer_daily_maintenance",
                "company_name": "Daily Maintenance SE",
                "instrument_name": "Daily Maintenance common stock",
                "instrument_type": "equity",
                "ticker": "DMT",
                "exchange_code": "XETR",
                "venue_mic": "XETR",
                "provider_symbol": "DMT.DE",
                "broker_symbol": "",
                "currency": "EUR",
                "country": "DE",
                "sector": "Industrials",
                "industry": "Testing",
                "status": "watching",
                "watchlist_reason": "Daily maintenance fixture.",
                "research_summary": "Daily maintenance fixture.",
                "research_page": research_page,
                "last_research_at": "2026-07-20T00:00:00Z",
                "next_review_at": "2026-08-20T00:00:00Z",
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
                "source": "fixture",
            }
        ],
    )
    write_price_cache(
        sandbox_repository,
        security_id,
        (
            PriceBar(
                date=NOW.date(),
                open=Decimal("100"),
                high=Decimal("101"),
                low=Decimal("99"),
                close=Decimal("100"),
                adjusted_close=Decimal("100"),
                volume=1000,
                dividends=Decimal("0"),
                stock_splits=Decimal("0"),
                currency="EUR",
                provider_symbol="DMT.DE",
                retrieved_at=NOW,
                source="fixture",
            ),
        ),
    )

    preparation = prepare_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-allocation-maintenance",
        trigger="integration",
        source_sha="b" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )
    assert preparation.errors == ()
    rows = read_table(sandbox_repository, "operations_todo")
    assert [row["operation_type"] for row in rows] == [
        "security_research",
        "relationship_research",
    ]
    assert rows[1]["depends_on"] == rows[0]["operation_id"]


def test_empty_daily_cycle_generates_one_reconciled_canonical_report(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    preparation = prepare_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-integration-1",
        trigger="integration",
        source_sha="a" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )
    batch = execute_agent_batch(
        sandbox_repository,
        sandbox_settings,
        run_id=preparation.run_id,
        hermes_home=tmp_path / "unused-hermes",
        environment={"PATH": "/usr/bin"},
        maximum_operations=0,
        now=NOW,
    )
    finalization = finalize_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id=preparation.run_id,
        github_report_url=(
            "https://github.com/example/PaperTrader/blob/main/"
            "data/wiki/daily-reports/daily-report_20260724.md"
        ),
        now=NOW,
    )

    assert preparation.errors == ()
    assert batch.operation_count == 0
    assert finalization.status == "succeeded"
    assert finalization.report_path.endswith("daily-report_20260724.md")
    assert len(read_table(sandbox_repository, "cash_ledger")) == 1
    assert read_table(sandbox_repository, "performance_daily")[0]["equity_base"] == "100000"
    assert read_table(sandbox_repository, "runs")[0]["run_id"] == preparation.run_id
    manifest = json.loads(
        (sandbox_repository / "data" / "runs" / preparation.run_id / "daily_run.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["status"] == "succeeded"
    assert manifest["report_path"] == finalization.report_path
    assert manifest["snapshot_id"] == finalization.snapshot_id
    snapshot = json.loads(
        (sandbox_repository / "data" / "published" / "decision_snapshot.json").read_text(
            encoding="utf-8"
        )
    )
    assert snapshot["snapshot_id"] == finalization.snapshot_id
    assert snapshot["run_id"] == preparation.run_id
    assert snapshot["research_benchmark"]["non_approved"] is True
    assert snapshot["research_benchmark"]["copy_ready"] is False
    assert snapshot["research_benchmark"]["rows"] == [
        {
            "company_name": "Cash",
            "currency": "",
            "rating": "unrated",
            "reference_price": "1",
            "research_page": "",
            "security_id": "",
            "ticker": "CASH",
            "weight_pct": "100",
        }
    ]
    assert (
        read_table(sandbox_repository, "published_research_benchmark")[0]["non_approved"] == "true"
    )
    assert read_table(sandbox_repository, "signals") == []
    assert read_table(sandbox_repository, "orders") == []
    assert read_table(sandbox_repository, "executions") == []
    assert finalization.snapshot_id in (sandbox_repository / finalization.report_path).read_text(
        encoding="utf-8"
    )
    assert lint_wiki(sandbox_repository / "data" / "wiki") == []
    environment = {
        "PAPER_TRADING_ONLY": "true",
        "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
    }
    assert validate_integrity(sandbox_repository, environment) == []


def test_daily_finalization_rejects_invalid_report_url_before_state_changes(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    preparation = prepare_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-invalid-report-url",
        trigger="integration",
        source_sha="d" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )
    execute_agent_batch(
        sandbox_repository,
        sandbox_settings,
        run_id=preparation.run_id,
        hermes_home=tmp_path / "unused-hermes",
        environment={"PATH": "/usr/bin"},
        maximum_operations=0,
        now=NOW,
    )

    with pytest.raises(DailyRunError, match=r"HTTPS github\.com"):
        finalize_daily_run(
            sandbox_repository,
            sandbox_settings,
            run_id=preparation.run_id,
            github_report_url="https://example.com/report",
            now=NOW,
        )

    assert read_table(sandbox_repository, "runs") == []
    assert read_table(sandbox_repository, "allocation_history") == []
    manifest = json.loads(
        (sandbox_repository / "data" / "runs" / preparation.run_id / "daily_run.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["status"] == "prepared"


def test_daily_finalization_fills_next_eligible_base_currency_open(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    security_id = "sec_daily_fill"
    write_table(
        sandbox_repository,
        "securities",
        [
            {
                "security_id": security_id,
                "issuer_id": "issuer_daily_fill",
                "company_name": "Daily Fill SE",
                "instrument_name": "Daily Fill common stock",
                "instrument_type": "equity",
                "ticker": "DFL",
                "exchange_code": "XETR",
                "venue_mic": "XETR",
                "provider_symbol": "DFL.DE",
                "broker_symbol": "",
                "currency": "EUR",
                "country": "DE",
                "sector": "Industrials",
                "industry": "Testing",
                "status": "active",
                "watchlist_reason": "Daily orchestration fixture.",
                "research_summary": "Daily orchestration fixture.",
                "research_page": "",
                "last_research_at": "",
                "next_review_at": "",
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
                "source": "fixture",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "strategies",
        [
            {
                "strategy_id": "strategy_daily_fill",
                "idea_id": "idea_daily_fill",
                "security_id": security_id,
                "relationship_id": "relationship_daily_fill",
                "name": "Daily fill strategy",
                "status": "ready",
                "direction": "long",
                "instrument_type": "equity",
                "thesis": "Exercise the daily fill controller.",
                "entry_rule": "Enter on the fixture signal.",
                "exit_rule": "Exit outside the fixture.",
                "invalidation": "The fixture fails.",
                "risk_budget_pct": "2",
                "sleeve": "conviction",
                "allocation_plan_id": "",
                "not_before": "",
                "expires_at": "",
                "research_page": "",
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ],
    )
    retrieved_at = datetime(2026, 7, 24, 22, tzinfo=UTC)
    prices = (
        PriceBar(
            date=date(2026, 7, 23),
            open=Decimal("100"),
            high=Decimal("102"),
            low=Decimal("99"),
            close=Decimal("101"),
            adjusted_close=Decimal("101"),
            volume=1000,
            dividends=Decimal("0"),
            stock_splits=Decimal("0"),
            currency="EUR",
            provider_symbol="DFL.DE",
            retrieved_at=retrieved_at,
            source="fixture",
        ),
        PriceBar(
            date=date(2026, 7, 24),
            open=Decimal("103"),
            high=Decimal("106"),
            low=Decimal("102"),
            close=Decimal("105"),
            adjusted_close=Decimal("105"),
            volume=1200,
            dividends=Decimal("0"),
            stock_splits=Decimal("0"),
            currency="EUR",
            provider_symbol="DFL.DE",
            retrieved_at=retrieved_at,
            source="fixture",
        ),
    )
    write_price_cache(sandbox_repository, security_id, prices)
    order_time = datetime(2026, 7, 23, 16, tzinfo=UTC)
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id="seed",
        occurred_at=order_time,
    )
    signal_id, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id="strategy_daily_fill",
        signal_type="open",
        rationale="Open at the next eligible XETR session.",
        market_data_as_of=datetime(2026, 7, 23, 15, 30, tzinfo=UTC),
        run_id="seed",
        now=order_time,
    )
    reference = ReferencePrice(
        security_id=security_id,
        provider_contract_id="",
        price=Decimal("101"),
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=datetime(2026, 7, 23, 15, 30, tzinfo=UTC),
    )
    write_table(
        sandbox_repository,
        "strategy_legs",
        [
            {
                "strategy_id": "strategy_daily_fill",
                "leg_id": "leg_daily_fill",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": security_id,
                "provider_contract_id": "",
                "option_type": "",
                "expiry": "",
                "strike": "",
                "quantity": "10",
                "contract_multiplier": "1",
                "order_type": "market",
                "limit_price": "",
                "currency": "EUR",
            }
        ],
    )
    order_id, _, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id="strategy_daily_fill",
        legs=(
            OrderLegSpec(
                leg_id="leg_daily_fill",
                action="buy",
                side="long",
                instrument_type="equity",
                security_id=security_id,
                provider_contract_id="",
                option_type="",
                expiry=None,
                strike=None,
                quantity=Decimal("10"),
                contract_multiplier=Decimal("1"),
                limit_price=None,
                currency="EUR",
            ),
        ),
        references=(reference,),
        risk_state=build_risk_state(sandbox_repository, (reference,), as_of=order_time),
        run_id="seed",
        now=order_time,
    )
    prepare_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-fill-1",
        trigger="integration",
        source_sha="b" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )
    execute_agent_batch(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-fill-1",
        hermes_home=tmp_path / "unused-hermes",
        environment={"PATH": "/usr/bin"},
        maximum_operations=0,
        now=NOW,
    )
    result = finalize_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-fill-1",
        github_report_url=(
            "https://github.com/example/PaperTrader/blob/main/"
            "data/wiki/daily-reports/daily-report_20260724.md"
        ),
        now=NOW,
    )

    execution = next(
        row for row in read_table(sandbox_repository, "executions") if row["order_id"] == order_id
    )
    assert execution["source_bar_time"] == "2026-07-24T07:00:00Z"
    assert execution["fill_price"] == "103.0515"
    assert read_table(sandbox_repository, "orders")[0]["status"] == "filled"
    assert read_table(sandbox_repository, "portfolio")[0]["current_price"] == "105"
    assert result.fill_outcomes[0].startswith(f"{order_id}:filled:")


def test_daily_finalization_defers_foreign_order_when_fx_is_missing(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    security_id = "sec_foreign_pending"
    strategy_id = "strategy_foreign_pending"
    signal_id = "signal_foreign_pending"
    order_id = "order_foreign_pending"
    write_table(
        sandbox_repository,
        "securities",
        [
            {
                "security_id": security_id,
                "issuer_id": "issuer_foreign_pending",
                "company_name": "Foreign Pending Corp",
                "instrument_name": "Foreign Pending common stock",
                "instrument_type": "equity",
                "ticker": "FPC",
                "exchange_code": "NYSE",
                "venue_mic": "XNYS",
                "provider_symbol": "FPC",
                "broker_symbol": "",
                "currency": "USD",
                "country": "US",
                "sector": "Industrials",
                "industry": "Testing",
                "status": "active",
                "watchlist_reason": "Foreign FX deferral fixture.",
                "research_summary": "Foreign FX deferral fixture.",
                "research_page": "",
                "last_research_at": "",
                "next_review_at": "",
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
                "source": "fixture",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "strategies",
        [
            {
                "strategy_id": strategy_id,
                "idea_id": "idea_foreign_pending",
                "security_id": security_id,
                "relationship_id": "relationship_foreign_pending",
                "name": "Foreign pending strategy",
                "status": "ready",
                "direction": "long",
                "instrument_type": "equity",
                "thesis": "Exercise deterministic FX deferral.",
                "entry_rule": "Enter only with a fresh USD/EUR rate.",
                "exit_rule": "Exit outside this fixture.",
                "invalidation": "The fixture fails.",
                "risk_budget_pct": "2",
                "sleeve": "conviction",
                "allocation_plan_id": "",
                "not_before": "",
                "expires_at": "",
                "research_page": "",
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "strategy_legs",
        [
            {
                "strategy_id": strategy_id,
                "leg_id": "leg_foreign_pending",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": security_id,
                "provider_contract_id": "",
                "option_type": "",
                "expiry": "",
                "strike": "",
                "quantity": "10",
                "contract_multiplier": "1",
                "order_type": "market",
                "limit_price": "",
                "currency": "USD",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "signals",
        [
            {
                "signal_id": signal_id,
                "strategy_id": strategy_id,
                "signal_type": "open",
                "created_at": "2026-07-24T20:00:00Z",
                "expires_at": "2026-07-25T20:00:00Z",
                "status": "ordered",
                "rationale": "Await a fresh USD/EUR conversion.",
                "market_data_as_of": "2026-07-24T20:00:00Z",
                "order_request_path": "",
                "telegram_sent_at": "",
                "run_id": "seed",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "orders",
        [
            {
                "order_id": order_id,
                "signal_id": signal_id,
                "strategy_id": strategy_id,
                "created_at": "2026-07-24T20:00:00Z",
                "status": "pending",
                "fill_policy": "next_open",
                "not_before": "2026-07-24T20:00:00Z",
                "expires_at": "2026-07-25T20:00:00Z",
                "order_type": "market",
                "limit_price": "",
                "slippage_bps": "5",
                "fee_model": "fixed_plus_bps",
                "currency": "USD",
                "run_id": "seed",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "order_legs",
        [
            {
                "order_id": order_id,
                "leg_id": "leg_foreign_pending",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": security_id,
                "provider_contract_id": "",
                "option_type": "",
                "expiry": "",
                "strike": "",
                "quantity": "10",
                "contract_multiplier": "1",
                "limit_price": "",
                "currency": "USD",
            }
        ],
    )
    write_price_cache(
        sandbox_repository,
        security_id,
        (
            PriceBar(
                date=date(2026, 7, 24),
                open=Decimal("100"),
                high=Decimal("102"),
                low=Decimal("99"),
                close=Decimal("101"),
                adjusted_close=Decimal("101"),
                volume=1000,
                dividends=Decimal("0"),
                stock_splits=Decimal("0"),
                currency="USD",
                provider_symbol="FPC",
                retrieved_at=NOW,
                source="fixture",
            ),
        ),
    )
    preparation = prepare_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-missing-fx",
        trigger="integration",
        source_sha="c" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )
    execute_agent_batch(
        sandbox_repository,
        sandbox_settings,
        run_id=preparation.run_id,
        hermes_home=tmp_path / "unused-hermes",
        environment={"PATH": "/usr/bin"},
        maximum_operations=0,
        now=NOW,
    )

    result = finalize_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id=preparation.run_id,
        github_report_url="https://github.com/example/PaperTrader/blob/main/report.md",
        now=NOW,
    )

    assert result.status == "degraded"
    assert result.fill_outcomes == (f"{order_id}:deferred:market_or_fx_unavailable",)
    assert read_table(sandbox_repository, "orders")[0]["status"] == "pending"
    assert read_table(sandbox_repository, "executions") == []
    assert len(read_table(sandbox_repository, "cash_ledger")) == 1

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from papertrader.advice import refresh_advice
from papertrader.config import Settings
from papertrader.execution import ensure_initial_capital, process_order_fill
from papertrader.indicators import update_indicators
from papertrader.integrity import validate_integrity
from papertrader.market_data import write_price_cache
from papertrader.models import (
    ClassifierDecision,
    MarketBar,
    OrderLegSpec,
    PriceBar,
    ReferencePrice,
)
from papertrader.opportunity import process_opportunity_transitions
from papertrader.orders import create_paper_order, create_signal
from papertrader.portfolio import build_risk_state, reconcile_portfolio
from papertrader.queue import prepare_queue, validate_queue
from papertrader.reports import generate_daily_report
from papertrader.tables import read_table, write_table
from papertrader.wiki import lint_wiki

NOW = datetime(2026, 7, 24, 15, tzinfo=UTC)


class _IgnoreClassifier:
    def classify(self, candidate: Mapping[str, object]) -> ClassifierDecision:
        return ClassifierDecision(
            decision="ignore",
            reason="The transition is already represented by bounded opportunity research.",
            related_entity_ids=(str(candidate["security_id"]),),
        )


def _security() -> dict[str, str]:
    return {
        "security_id": "sec_cycle",
        "issuer_id": "issuer_cycle",
        "company_name": "Cycle Corp",
        "instrument_name": "Cycle common stock",
        "instrument_type": "equity",
        "ticker": "CYC",
        "exchange_code": "NYSE",
        "venue_mic": "XNYS",
        "provider_symbol": "CYC",
        "broker_symbol": "",
        "currency": "USD",
        "country": "US",
        "sector": "Industrials",
        "industry": "Testing",
        "status": "active",
        "watchlist_reason": "End-to-end fixture.",
        "research_summary": "Deterministic integration fixture.",
        "research_page": "",
        "last_research_at": "",
        "next_review_at": "",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-20T00:00:00Z",
        "source": "fixture",
    }


def _strategy() -> dict[str, str]:
    return {
        "strategy_id": "strategy_cycle",
        "idea_id": "idea_cycle",
        "security_id": "sec_cycle",
        "relationship_id": "relationship_cycle",
        "name": "Cycle strategy",
        "status": "ready",
        "direction": "long",
        "instrument_type": "equity",
        "thesis": "Exercise the deterministic core.",
        "entry_rule": "Enter on the fixed fixture signal.",
        "exit_rule": "Exit outside this fixture.",
        "invalidation": "The fixture fails validation.",
        "risk_budget_pct": "1",
        "sleeve": "conviction",
        "allocation_plan_id": "",
        "not_before": "",
        "expires_at": "",
        "research_page": "",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-20T00:00:00Z",
    }


def _prices() -> tuple[PriceBar, ...]:
    first_day = NOW.date() - timedelta(days=219)
    return tuple(
        PriceBar(
            date=first_day + timedelta(days=index),
            open=Decimal("50") + Decimal(index) / Decimal("10"),
            high=Decimal("51") + Decimal(index) / Decimal("10"),
            low=Decimal("49") + Decimal(index) / Decimal("10"),
            close=Decimal("50.5") + Decimal(index) / Decimal("10"),
            adjusted_close=Decimal("50.5") + Decimal(index) / Decimal("10"),
            volume=1000 + index,
            dividends=Decimal("0"),
            stock_splits=Decimal("0"),
            currency="USD",
            provider_symbol="CYC",
            retrieved_at=NOW,
            source="fixture",
        )
        for index in range(220)
    )


def _reference(price: Decimal, as_of: datetime) -> ReferencePrice:
    return ReferencePrice(
        security_id="sec_cycle",
        provider_contract_id="",
        price=price,
        currency="USD",
        fx_rate_to_base=Decimal("1"),
        as_of=as_of,
    )


def test_complete_core_cycle_is_replay_safe(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    write_table(sandbox_repository, "securities", [_security()])
    write_table(sandbox_repository, "strategies", [_strategy()])
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id="run-cycle",
        occurred_at=NOW - timedelta(hours=1),
    )
    prices = _prices()
    write_price_cache(sandbox_repository, "sec_cycle", prices)

    previous, current, indicator_errors = update_indicators(
        sandbox_repository, sandbox_settings, now=NOW
    )
    assert indicator_errors == ()
    packets = process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        previous,
        current,
        {"sec_cycle": prices},
        classifier=_IgnoreClassifier(),
        now=NOW,
    )
    assert packets and all(packet.decision is not None for packet in packets)
    prepare_queue(sandbox_repository, now=NOW + timedelta(minutes=1))
    assert validate_queue(sandbox_repository) == []

    signal_id, signal_created = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id="strategy_cycle",
        signal_type="open",
        rationale="Open the deterministic integration position.",
        market_data_as_of=NOW - timedelta(minutes=5),
        run_id="run-cycle",
        now=NOW,
    )
    leg = OrderLegSpec(
        leg_id="leg_cycle",
        action="buy",
        side="long",
        instrument_type="equity",
        security_id="sec_cycle",
        provider_contract_id="",
        option_type="",
        expiry=None,
        strike=None,
        quantity=Decimal("10"),
        contract_multiplier=Decimal("1"),
        limit_price=None,
        currency="USD",
    )
    write_table(
        sandbox_repository,
        "strategy_legs",
        [
            {
                "strategy_id": "strategy_cycle",
                "leg_id": leg.leg_id,
                "action": leg.action,
                "side": leg.side,
                "instrument_type": leg.instrument_type,
                "security_id": leg.security_id,
                "provider_contract_id": leg.provider_contract_id,
                "option_type": leg.option_type,
                "expiry": "",
                "strike": "",
                "quantity": "10",
                "contract_multiplier": "1",
                "order_type": "market",
                "limit_price": "",
                "currency": leg.currency,
            }
        ],
    )
    order_reference = _reference(prices[-1].close, NOW)
    order_id, order_created, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id="strategy_cycle",
        legs=(leg,),
        references=(order_reference,),
        risk_state=build_risk_state(sandbox_repository, (order_reference,), as_of=NOW),
        run_id="run-cycle",
        now=NOW,
    )
    assert signal_created and order_created

    fill_time = NOW + timedelta(hours=2)
    mark = _reference(Decimal("75"), fill_time)
    status, _ = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=(
            MarketBar(
                security_id="sec_cycle",
                provider_contract_id="",
                timestamp=NOW + timedelta(hours=1),
                open=Decimal("72"),
                high=Decimal("74"),
                low=Decimal("71"),
                close=Decimal("73"),
                currency="USD",
                fx_rate_to_base=Decimal("1"),
            ),
        ),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (mark,), as_of=fill_time),
        risk_references=(mark,),
        run_id="run-cycle",
        now=fill_time,
    )
    assert status == "filled"
    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="run-cycle",
        as_of=fill_time,
    )
    report = generate_daily_report(
        sandbox_repository,
        run_id="run-cycle",
        run_status="succeeded",
        generated_at=fill_time,
    )
    assert report.is_file()
    assert reconcile_portfolio(sandbox_repository) == []

    first_counts = {
        name: len(read_table(sandbox_repository, name))
        for name in (
            "signals",
            "orders",
            "order_legs",
            "executions",
            "cash_ledger",
            "portfolio",
            "performance_daily",
            "operations_todo",
        )
    }
    first_report = report.read_text(encoding="utf-8")
    old, unchanged, rerun_errors = update_indicators(sandbox_repository, sandbox_settings, now=NOW)
    assert rerun_errors == ()
    assert (
        process_opportunity_transitions(
            sandbox_repository,
            sandbox_settings,
            old,
            unchanged,
            {"sec_cycle": prices},
            classifier=_IgnoreClassifier(),
            now=NOW,
        )
        == ()
    )
    assert create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id="strategy_cycle",
        signal_type="open",
        rationale="Open the deterministic integration position.",
        market_data_as_of=NOW - timedelta(minutes=5),
        run_id="run-cycle",
        now=fill_time,
    ) == (signal_id, False)
    replayed_order, replayed_created, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id="strategy_cycle",
        legs=(leg,),
        references=(mark,),
        risk_state=build_risk_state(sandbox_repository, (mark,), as_of=fill_time),
        run_id="run-cycle",
        now=fill_time,
    )
    assert (replayed_order, replayed_created) == (order_id, False)
    replay_status, _ = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=(),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (mark,), as_of=fill_time),
        risk_references=(mark,),
        run_id="run-cycle",
        now=fill_time,
    )
    assert replay_status == "filled"
    rerun_report = generate_daily_report(
        sandbox_repository,
        run_id="run-cycle",
        run_status="succeeded",
        generated_at=fill_time,
    )

    assert {
        name: len(read_table(sandbox_repository, name)) for name in first_counts
    } == first_counts
    assert rerun_report.read_text(encoding="utf-8") == first_report
    assert reconcile_portfolio(sandbox_repository) == []
    assert lint_wiki(sandbox_settings.paths.wiki) == []
    assert (
        validate_integrity(
            sandbox_repository,
            {
                "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
            },
        )
        == []
    )

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from papertrader.atomic_io import atomic_write_csv
from papertrader.config import Settings
from papertrader.corporate_actions import accrue_dividends
from papertrader.execution import (
    cash_rows_for_execution,
    ensure_initial_capital,
    process_order_fill,
    select_fill,
)
from papertrader.models import (
    MarketBar,
    OptionQuote,
    OrderLegSpec,
    PositionMark,
    ReferencePrice,
    RiskPosition,
    RiskState,
)
from papertrader.orders import cancel_paper_order, create_paper_order, create_signal
from papertrader.portfolio import build_risk_state, rebuild_portfolio, reconcile_portfolio
from papertrader.risk import assess_order_risk, option_max_loss
from papertrader.tables import append_unique, contract_by_name, read_table, write_table
from papertrader.utils import stable_id

START = datetime(2026, 7, 20, 15, tzinfo=UTC)


def _security_row() -> dict[str, str]:
    return {
        "security_id": "sec_a",
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
        "research_summary": "Fixture.",
        "research_page": "",
        "last_research_at": "",
        "next_review_at": "",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-20T00:00:00Z",
        "source": "fixture",
    }


def _strategy_row(strategy_id: str) -> dict[str, str]:
    return {
        "strategy_id": strategy_id,
        "idea_id": "idea_a",
        "security_id": "sec_a",
        "relationship_id": "relationship_a",
        "name": f"Fixture {strategy_id}",
        "status": "ready",
        "direction": "long",
        "instrument_type": "equity",
        "thesis": "Fixture thesis.",
        "entry_rule": "Fixture entry.",
        "exit_rule": "Fixture exit.",
        "invalidation": "Fixture invalidation.",
        "risk_budget_pct": "1",
        "sleeve": "conviction",
        "allocation_plan_id": "",
        "not_before": "",
        "expires_at": "",
        "research_page": "",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-20T00:00:00Z",
    }


def _reference(
    *,
    price: str,
    as_of: datetime,
    contract: str = "",
    option: bool = False,
) -> ReferencePrice:
    return ReferencePrice(
        security_id="sec_a",
        provider_contract_id=contract,
        price=Decimal(price),
        currency="USD",
        fx_rate_to_base=Decimal("1"),
        as_of=as_of,
        bid=Decimal(price) - Decimal("0.1") if option else None,
        ask=Decimal(price) + Decimal("0.1") if option else None,
        open_interest=1000 if option else None,
        volume=100 if option else None,
    )


def _empty_state() -> RiskState:
    return RiskState(
        equity_base=Decimal("100000"),
        cash_base=Decimal("100000"),
        gross_exposure_base=Decimal("0"),
        short_exposure_base=Decimal("0"),
        options_risk_base=Decimal("0"),
        daily_turnover_base=Decimal("0"),
        active_strategy_count=0,
        positions=(),
    )


def _leg(
    *,
    action: str,
    side: str,
    instrument: str = "equity",
    contract: str = "",
) -> OrderLegSpec:
    return OrderLegSpec(
        leg_id="leg_1",
        action=action,
        side=side,
        instrument_type=instrument,
        security_id="sec_a",
        provider_contract_id=contract,
        option_type="call" if instrument == "option" else "",
        expiry=date(2026, 9, 18) if instrument == "option" else None,
        strike=Decimal("100") if instrument == "option" else None,
        quantity=Decimal("2") if instrument == "option" else Decimal("10"),
        contract_multiplier=Decimal("100") if instrument == "option" else Decimal("1"),
        limit_price=None,
        currency="USD",
    )


def _setup_strategy(
    repository: Path,
    settings: Settings,
    strategy_id: str,
    leg: OrderLegSpec,
) -> None:
    write_table(repository, "securities", [_security_row()])
    write_table(repository, "strategies", [_strategy_row(strategy_id)])
    write_table(
        repository,
        "strategy_legs",
        [
            {
                "strategy_id": strategy_id,
                "leg_id": leg.leg_id,
                "action": leg.action,
                "side": leg.side,
                "instrument_type": leg.instrument_type,
                "security_id": leg.security_id,
                "provider_contract_id": leg.provider_contract_id,
                "option_type": leg.option_type,
                "expiry": leg.expiry.isoformat() if leg.expiry else "",
                "strike": str(leg.strike) if leg.strike is not None else "",
                "quantity": str(leg.quantity),
                "contract_multiplier": str(leg.contract_multiplier),
                "order_type": "market",
                "limit_price": "",
                "currency": leg.currency,
            }
        ],
    )
    ensure_initial_capital(
        repository,
        settings,
        run_id=f"run-{strategy_id}",
        occurred_at=START - timedelta(hours=1),
    )


def _order_row(policy: str, *, limit: str = "") -> dict[str, str]:
    return {
        "order_id": "order_fixture",
        "signal_id": "signal_fixture",
        "strategy_id": "strategy_fixture",
        "created_at": "2026-07-20T15:00:00Z",
        "status": "pending",
        "fill_policy": policy,
        "not_before": "2026-07-20T15:00:00Z",
        "expires_at": "2026-07-21T15:00:00Z",
        "order_type": "limit" if policy == "limit_touch" else "market",
        "limit_price": limit,
        "slippage_bps": "5",
        "fee_model": "fixed_plus_bps",
        "currency": "USD",
        "run_id": "run",
    }


def test_next_open_has_no_lookahead_and_applies_directional_slippage(
    sandbox_settings: Settings,
) -> None:
    leg = _leg(action="buy", side="long")
    exact_signal_bar = MarketBar(
        "sec_a",
        "",
        START,
        Decimal("90"),
        Decimal("92"),
        Decimal("89"),
        Decimal("91"),
        "USD",
        Decimal("1"),
    )
    next_bar = MarketBar(
        "sec_a",
        "",
        START + timedelta(hours=20),
        Decimal("100"),
        Decimal("102"),
        Decimal("99"),
        Decimal("101"),
        "USD",
        Decimal("1"),
    )

    fill = select_fill(
        _order_row("next_open"),
        leg,
        bars=(exact_signal_bar, next_bar),
        quotes=(),
        signal_created_at=START,
        now=START + timedelta(hours=21),
        settings=sandbox_settings,
    )
    late_processed_fill = select_fill(
        _order_row("next_open"),
        leg,
        bars=(exact_signal_bar, next_bar),
        quotes=(),
        signal_created_at=START,
        now=START + timedelta(days=2),
        settings=sandbox_settings,
    )

    assert fill is not None
    assert late_processed_fill is not None
    assert fill.source_time == next_bar.timestamp
    assert late_processed_fill.source_time == next_bar.timestamp
    assert fill.fill_price == Decimal("100.0500")


def test_limit_touch_uses_limit_without_worse_slippage(sandbox_settings: Settings) -> None:
    leg = _leg(action="buy", side="long")
    leg = replace(leg, limit_price=Decimal("100"))
    bar = MarketBar(
        "sec_a",
        "",
        START + timedelta(hours=20),
        Decimal("101"),
        Decimal("103"),
        Decimal("99"),
        Decimal("102"),
        "USD",
        Decimal("1"),
    )

    fill = select_fill(
        _order_row("limit_touch", limit="100"),
        leg,
        bars=(bar,),
        quotes=(),
        signal_created_at=START,
        now=START + timedelta(hours=21),
        settings=sandbox_settings,
    )

    assert fill is not None and fill.fill_price == Decimal("100")


def test_pending_paper_order_cancellation_never_mutates_accounting(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    strategy_id = "strategy_cancel"
    leg = _leg(action="buy", side="long")
    _setup_strategy(sandbox_repository, sandbox_settings, strategy_id, leg)
    reference = _reference(price="100", as_of=START)
    signal_id, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Open only if the candidate remains valid.",
        market_data_as_of=START - timedelta(minutes=10),
        run_id="run-cancel",
        now=START,
    )
    order_id, _, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(leg,),
        references=(reference,),
        risk_state=build_risk_state(sandbox_repository, (reference,), as_of=START),
        run_id="run-cancel",
        now=START,
    )
    cash_before = read_table(sandbox_repository, "cash_ledger")

    cancel_paper_order(sandbox_repository, order_id)

    assert read_table(sandbox_repository, "orders")[0]["status"] == "cancelled"
    assert read_table(sandbox_repository, "signals")[0]["status"] == "cancelled"
    assert read_table(sandbox_repository, "executions") == []
    assert read_table(sandbox_repository, "portfolio") == []
    assert read_table(sandbox_repository, "cash_ledger") == cash_before
    with pytest.raises(RuntimeError, match="is not pending"):
        cancel_paper_order(sandbox_repository, order_id)


def test_quote_mid_requires_fresh_post_signal_bid_ask(sandbox_settings: Settings) -> None:
    leg = _leg(action="buy", side="long", instrument="option", contract="OPT1")
    stale_quote = OptionQuote(
        "OPT1",
        START + timedelta(minutes=1),
        Decimal("1.9"),
        Decimal("2.1"),
        "USD",
        Decimal("1"),
        1000,
        100,
    )

    assert (
        select_fill(
            _order_row("quote_mid"),
            leg,
            bars=(),
            quotes=(stale_quote,),
            signal_created_at=START,
            now=START + timedelta(hours=1),
            settings=sandbox_settings,
        )
        is None
    )


def test_bounded_call_spread_has_finite_max_loss_and_naked_short_call_is_rejected(
    sandbox_settings: Settings,
) -> None:
    long_call = _leg(action="buy", side="long", instrument="option", contract="LONG")
    short_call = OrderLegSpec(
        leg_id="leg_2",
        action="sell",
        side="short",
        instrument_type="option",
        security_id="sec_a",
        provider_contract_id="SHORT",
        option_type="call",
        expiry=date(2026, 9, 18),
        strike=Decimal("110"),
        quantity=Decimal("2"),
        contract_multiplier=Decimal("100"),
        limit_price=None,
        currency="USD",
    )
    references = {
        ("sec_a", "LONG"): _reference(price="5", as_of=START, contract="LONG", option=True),
        ("sec_a", "SHORT"): _reference(price="2", as_of=START, contract="SHORT", option=True),
    }

    loss, violations = option_max_loss((long_call, short_call), references)
    naked_loss, naked_violations = option_max_loss((short_call,), references)

    assert loss == Decimal("600")
    assert violations == ()
    assert naked_loss is None
    assert any(value.startswith("unbounded_option_risk") for value in naked_violations)

    assessment = assess_order_risk(
        sandbox_settings,
        _empty_state(),
        (short_call,),
        tuple(references.values()),
        {"sec_a": "XNYS"},
        now=START,
        activates_new_strategy=True,
    )
    assert any(value.startswith("unbounded_option_risk") for value in assessment.violations)


def test_closing_a_spread_hedge_cannot_leave_projected_naked_short_call(
    sandbox_settings: Settings,
) -> None:
    long_call = _leg(action="buy", side="long", instrument="option", contract="LONG")
    short_call = replace(
        long_call,
        leg_id="leg_2",
        action="sell",
        side="short",
        provider_contract_id="SHORT",
        strike=Decimal("110"),
    )
    positions = tuple(
        RiskPosition(
            security_id=leg.security_id,
            provider_contract_id=leg.provider_contract_id,
            side=leg.side,
            instrument_type=leg.instrument_type,
            quantity=leg.quantity,
            contract_multiplier=leg.contract_multiplier,
            currency=leg.currency,
            option_type=leg.option_type,
            expiry=leg.expiry,
            strike=leg.strike,
        )
        for leg in (long_call, short_call)
    )
    references = (
        _reference(price="5", as_of=START, contract="LONG", option=True),
        _reference(price="2", as_of=START, contract="SHORT", option=True),
    )
    state = replace(_empty_state(), options_risk_base=Decimal("600"), positions=positions)

    assessment = assess_order_risk(
        sandbox_settings,
        state,
        (replace(long_call, action="sell"),),
        references,
        {"sec_a": "XNYS"},
        now=START,
        activates_new_strategy=False,
    )

    assert any(value.startswith("unbounded_option_risk") for value in assessment.violations)


@pytest.mark.parametrize("scenario", ["equity", "short", "option"])
def test_reference_accounting_scenarios_reconcile_exactly(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    repository_root: Path,
    scenario: str,
) -> None:
    strategy_id = f"strategy_{scenario}"
    if scenario == "equity":
        leg = _leg(action="buy", side="long")
        order_reference = _reference(price="100", as_of=START)
        process_time = START + timedelta(hours=21)
        process_reference = _reference(price="110", as_of=process_time)
        bars = (
            MarketBar(
                "sec_a",
                "",
                START + timedelta(hours=20),
                Decimal("100"),
                Decimal("102"),
                Decimal("99"),
                Decimal("101"),
                "USD",
                Decimal("1"),
            ),
        )
        quotes: tuple[OptionQuote, ...] = ()
        policy = "next_open"
    elif scenario == "short":
        leg = _leg(action="sell", side="short")
        leg = OrderLegSpec(
            leg_id=leg.leg_id,
            action=leg.action,
            side=leg.side,
            instrument_type=leg.instrument_type,
            security_id=leg.security_id,
            provider_contract_id=leg.provider_contract_id,
            option_type=leg.option_type,
            expiry=leg.expiry,
            strike=leg.strike,
            quantity=Decimal("5"),
            contract_multiplier=leg.contract_multiplier,
            limit_price=leg.limit_price,
            currency=leg.currency,
        )
        order_reference = _reference(price="50", as_of=START)
        process_time = START + timedelta(hours=21)
        process_reference = _reference(price="40", as_of=process_time)
        bars = (
            MarketBar(
                "sec_a",
                "",
                START + timedelta(hours=20),
                Decimal("50"),
                Decimal("51"),
                Decimal("49"),
                Decimal("50"),
                "USD",
                Decimal("1"),
            ),
        )
        quotes = ()
        policy = "next_open"
    else:
        leg = _leg(action="buy", side="long", instrument="option", contract="OPT1")
        order_reference = _reference(price="2", as_of=START, contract="OPT1", option=True)
        process_time = START + timedelta(hours=1, minutes=5)
        process_reference = _reference(price="3", as_of=process_time, contract="OPT1", option=True)
        bars = ()
        quotes = (
            OptionQuote(
                "OPT1",
                START + timedelta(hours=1),
                Decimal("1.9"),
                Decimal("2.1"),
                "USD",
                Decimal("1"),
                1000,
                100,
            ),
        )
        policy = "quote_mid"
    _setup_strategy(sandbox_repository, sandbox_settings, strategy_id, leg)
    signal_id, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="open",
        rationale=f"Open {scenario} fixture.",
        market_data_as_of=START - timedelta(minutes=10),
        run_id=f"run-{scenario}",
        now=START,
    )
    before_order_portfolio = read_table(sandbox_repository, "portfolio")
    state = build_risk_state(sandbox_repository, (order_reference,), as_of=START)
    order_id, created, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(leg,),
        references=(order_reference,),
        risk_state=state,
        run_id=f"run-{scenario}",
        fill_policy=policy,
        order_type="market",
        now=START,
    )

    assert created is True
    assert before_order_portfolio == read_table(sandbox_repository, "portfolio") == []
    assert read_table(sandbox_repository, "executions") == []
    process_state = build_risk_state(sandbox_repository, (process_reference,), as_of=process_time)
    status, execution_ids = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=bars,
        quotes=quotes,
        risk_state=process_state,
        risk_references=(process_reference,),
        run_id=f"run-{scenario}",
        now=process_time,
    )

    assert status == "filled"
    assert len(execution_ids) == 1
    assert reconcile_portfolio(sandbox_repository) == []
    actual = {
        "execution": read_table(sandbox_repository, "executions")[0],
        "cash": read_table(sandbox_repository, "cash_ledger"),
        "portfolio": read_table(sandbox_repository, "portfolio")[0],
        "performance": read_table(sandbox_repository, "performance_daily")[0],
    }
    expected_all = json.loads(
        (repository_root / "tests" / "reference_outputs" / "accounting_scenarios.json").read_text(
            encoding="utf-8"
        )
    )
    assert actual == expected_all[scenario]


def test_exact_replay_repairs_interrupted_fill_without_duplicate_state(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    strategy_id = "strategy_recovery"
    leg = _leg(action="buy", side="long")
    _setup_strategy(sandbox_repository, sandbox_settings, strategy_id, leg)
    order_reference = _reference(price="100", as_of=START)
    signal_id, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Open recovery fixture.",
        market_data_as_of=START - timedelta(minutes=10),
        run_id="run-recovery",
        now=START,
    )
    order_id, _, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(leg,),
        references=(order_reference,),
        risk_state=build_risk_state(sandbox_repository, (order_reference,), as_of=START),
        run_id="run-recovery",
        now=START,
    )
    fill_time = START + timedelta(hours=21)
    mark = _reference(price="110", as_of=fill_time)
    bar = MarketBar(
        "sec_a",
        "",
        START + timedelta(hours=20),
        Decimal("100"),
        Decimal("102"),
        Decimal("99"),
        Decimal("101"),
        "USD",
        Decimal("1"),
    )
    process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=(bar,),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (mark,), as_of=fill_time),
        risk_references=(mark,),
        run_id="run-recovery",
        now=fill_time,
    )

    signal_retry, signal_created = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Open recovery fixture.",
        market_data_as_of=START - timedelta(minutes=10),
        run_id="run-recovery-retry",
        now=fill_time,
    )
    order_retry, order_created, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(leg,),
        references=(mark,),
        risk_state=build_risk_state(sandbox_repository, (mark,), as_of=fill_time),
        run_id="run-recovery-retry",
        now=fill_time,
    )
    assert (signal_retry, signal_created) == (signal_id, False)
    assert (order_retry, order_created) == (order_id, False)

    executions_before = read_table(sandbox_repository, "executions")
    cash_before = read_table(sandbox_repository, "cash_ledger")
    cash_contract = contract_by_name(sandbox_repository, "cash_ledger")
    atomic_write_csv(
        sandbox_repository.joinpath(*cash_contract.path.parts),
        cash_contract.columns,
        cash_before[:-1],
        allowed_root=sandbox_repository,
    )
    write_table(sandbox_repository, "portfolio", [])
    write_table(sandbox_repository, "performance_daily", [])
    orders = read_table(sandbox_repository, "orders")
    orders[0]["status"] = "pending"
    write_table(sandbox_repository, "orders", orders)
    signals = read_table(sandbox_repository, "signals")
    signals[0]["status"] = "ordered"
    write_table(sandbox_repository, "signals", signals)
    strategies = read_table(sandbox_repository, "strategies")
    strategies[0]["status"] = "ready"
    write_table(sandbox_repository, "strategies", strategies)

    status, execution_ids = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=(),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (mark,), as_of=fill_time),
        risk_references=(mark,),
        run_id="run-recovery-retry",
        now=fill_time,
    )

    assert status == "filled"
    assert execution_ids == (executions_before[0]["execution_id"],)
    assert read_table(sandbox_repository, "executions") == executions_before
    assert read_table(sandbox_repository, "cash_ledger") == cash_before
    assert len(read_table(sandbox_repository, "portfolio")) == 1
    assert len(read_table(sandbox_repository, "performance_daily")) == 1
    assert read_table(sandbox_repository, "orders")[0]["status"] == "filled"
    assert read_table(sandbox_repository, "signals")[0]["status"] == "filled"
    assert read_table(sandbox_repository, "strategies")[0]["status"] == "active"
    assert reconcile_portfolio(sandbox_repository) == []


def test_partial_close_preserves_average_cost_and_realizes_decimal_pnl(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    strategy_id = "strategy_partial"
    opening_leg = _leg(action="buy", side="long")
    _setup_strategy(sandbox_repository, sandbox_settings, strategy_id, opening_leg)
    opening_reference = _reference(price="100", as_of=START)
    opening_signal, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Open partial-close fixture.",
        market_data_as_of=START - timedelta(minutes=10),
        run_id="run-open",
        now=START,
    )
    opening_order, _, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=opening_signal,
        strategy_id=strategy_id,
        legs=(opening_leg,),
        references=(opening_reference,),
        risk_state=build_risk_state(sandbox_repository, (opening_reference,), as_of=START),
        run_id="run-open",
        now=START,
    )
    first_mark_time = START + timedelta(hours=21)
    first_mark = _reference(price="110", as_of=first_mark_time)
    process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=opening_order,
        bars=(
            MarketBar(
                "sec_a",
                "",
                START + timedelta(hours=20),
                Decimal("100"),
                Decimal("102"),
                Decimal("99"),
                Decimal("101"),
                "USD",
                Decimal("1"),
            ),
        ),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (first_mark,), as_of=first_mark_time),
        risk_references=(first_mark,),
        run_id="run-open",
        now=first_mark_time,
    )

    close_created = first_mark_time + timedelta(hours=1)
    close_signal, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="reduce",
        rationale="Reduce four shares.",
        market_data_as_of=first_mark_time,
        run_id="run-close",
        now=close_created,
    )
    closing_leg = replace(
        opening_leg,
        action="sell",
        quantity=Decimal("4"),
    )
    close_reference = _reference(price="110", as_of=close_created)
    close_order, _, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=close_signal,
        strategy_id=strategy_id,
        legs=(closing_leg,),
        references=(close_reference,),
        risk_state=build_risk_state(sandbox_repository, (close_reference,), as_of=close_created),
        run_id="run-close",
        now=close_created,
    )
    close_process_time = close_created + timedelta(hours=23)
    final_mark = _reference(price="125", as_of=close_process_time)
    status, _ = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=close_order,
        bars=(
            MarketBar(
                "sec_a",
                "",
                close_created + timedelta(hours=22),
                Decimal("120"),
                Decimal("122"),
                Decimal("119"),
                Decimal("121"),
                "USD",
                Decimal("1"),
            ),
        ),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (final_mark,), as_of=close_process_time),
        risk_references=(final_mark,),
        run_id="run-close",
        now=close_process_time,
    )

    assert status == "filled"
    position = read_table(sandbox_repository, "portfolio")[0]
    assert position["quantity"] == "6"
    assert position["average_cost"] == "100.160005"
    assert position["realized_pnl_base"] == "78.072004"
    assert position["unrealized_pnl_base"] == "149.03997"
    assert reconcile_portfolio(sandbox_repository) == []


def test_split_and_dividend_are_replayed_from_durable_corporate_actions(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    strategy_id = "strategy_actions"
    leg = _leg(action="buy", side="long")
    _setup_strategy(sandbox_repository, sandbox_settings, strategy_id, leg)
    opening_reference = _reference(price="100", as_of=START)
    signal_id, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Open corporate-action fixture.",
        market_data_as_of=START - timedelta(minutes=10),
        run_id="run-actions",
        now=START,
    )
    order_id, _, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(leg,),
        references=(opening_reference,),
        risk_state=build_risk_state(sandbox_repository, (opening_reference,), as_of=START),
        run_id="run-actions",
        now=START,
    )
    first_mark_time = START + timedelta(hours=21)
    first_mark = _reference(price="110", as_of=first_mark_time)
    process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=(
            MarketBar(
                "sec_a",
                "",
                START + timedelta(hours=20),
                Decimal("100"),
                Decimal("102"),
                Decimal("99"),
                Decimal("101"),
                "USD",
                Decimal("1"),
            ),
        ),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (first_mark,), as_of=first_mark_time),
        risk_references=(first_mark,),
        run_id="run-actions",
        now=first_mark_time,
    )
    append_unique(
        sandbox_repository,
        "corporate_actions",
        [
            {
                "corporate_action_id": stable_id("action", "sec_a", date(2026, 7, 22), "split"),
                "security_id": "sec_a",
                "action_date": "2026-07-22",
                "action_type": "split",
                "value": "2",
                "currency": "USD",
                "source": "fixture",
                "source_price_hash": "a" * 64,
                "recorded_at": "2026-07-23T22:00:00Z",
            },
            {
                "corporate_action_id": stable_id("action", "sec_a", date(2026, 7, 23), "dividend"),
                "security_id": "sec_a",
                "action_date": "2026-07-23",
                "action_type": "dividend",
                "value": "0.5",
                "currency": "USD",
                "source": "fixture",
                "source_price_hash": "b" * 64,
                "recorded_at": "2026-07-23T22:00:00Z",
            },
        ],
        key_columns=("corporate_action_id",),
    )

    assert (
        accrue_dividends(
            sandbox_repository,
            through=date(2026, 7, 23),
            fx_rates_to_base={("USD", date(2026, 7, 23)): Decimal("0.9")},
            base_currency="EUR",
            run_id="run-actions",
        )
        == 1
    )
    as_of = datetime(2026, 7, 23, 22, tzinfo=UTC)
    rebuild_portfolio(
        sandbox_repository,
        marks=(
            PositionMark(
                "sec_a",
                "",
                Decimal("60"),
                "USD",
                Decimal("0.9"),
                as_of,
            ),
        ),
        run_id="run-actions",
        as_of=as_of,
    )

    position = read_table(sandbox_repository, "portfolio")[0]
    dividend = next(
        row
        for row in read_table(sandbox_repository, "cash_ledger")
        if row["entry_type"] == "dividend"
    )
    assert position["quantity"] == "20"
    assert position["average_cost"] == "50.0800025"
    assert dividend["amount"] == "10"
    assert dividend["base_amount"] == "9"
    assert reconcile_portfolio(sandbox_repository) == []


def test_unheld_foreign_dividend_does_not_require_an_fx_rate(
    sandbox_repository: Path,
) -> None:
    append_unique(
        sandbox_repository,
        "corporate_actions",
        [
            {
                "corporate_action_id": stable_id(
                    "action", "unheld_security", date(2026, 7, 23), "dividend"
                ),
                "security_id": "unheld_security",
                "action_date": "2026-07-23",
                "action_type": "dividend",
                "value": "0.5",
                "currency": "USD",
                "source": "fixture",
                "source_price_hash": "c" * 64,
                "recorded_at": "2026-07-23T22:00:00Z",
            }
        ],
        key_columns=("corporate_action_id",),
    )

    assert (
        accrue_dividends(
            sandbox_repository,
            through=date(2026, 7, 23),
            fx_rates_to_base={},
            base_currency="EUR",
            run_id="run-unheld-action",
        )
        == 0
    )


@given(
    quantity=st.integers(min_value=1, max_value=1000),
    price_cents=st.integers(min_value=1, max_value=100000),
    multiplier=st.sampled_from([1, 10, 100]),
    fee_cents=st.integers(min_value=0, max_value=1000),
    fx_millis=st.integers(min_value=1, max_value=3000),
    action=st.sampled_from(["buy", "sell"]),
)
@hypothesis_settings(max_examples=50)
def test_execution_cash_rows_reconcile_decimal_trade_and_fee_property(
    quantity: int,
    price_cents: int,
    multiplier: int,
    fee_cents: int,
    fx_millis: int,
    action: str,
) -> None:
    price = Decimal(price_cents) / Decimal("100")
    fees = Decimal(fee_cents) / Decimal("100")
    fx_rate = Decimal(fx_millis) / Decimal("1000")
    gross = Decimal(quantity) * price * Decimal(multiplier)
    cash_effect = -gross if action == "buy" else gross
    execution = {
        "execution_id": "execution_property",
        "order_id": "order_property",
        "leg_id": "leg_property",
        "executed_at": "2026-07-24T10:00:00Z",
        "security_id": "sec_a",
        "provider_contract_id": "",
        "side": action,
        "quantity": str(quantity),
        "fill_price": str(price),
        "contract_multiplier": str(multiplier),
        "fees": str(fees),
        "currency": "EUR",
        "fx_rate_to_base": str(fx_rate),
        "cash_effect": str(cash_effect),
        "source_bar_time": "2026-07-24T10:00:00Z",
        "run_id": "run-property",
    }

    rows = cash_rows_for_execution(execution)

    assert Decimal(rows[0]["base_amount"]) == cash_effect * fx_rate
    fee_total = sum(
        (Decimal(row["base_amount"]) for row in rows if row["entry_type"] == "fee"),
        Decimal("0"),
    )
    assert fee_total == -fees * fx_rate

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from papertrader.allocation import (
    allocation_readiness,
    assessment_payoff_reasons,
    baseline_strategy_id,
    maintain_allocation_research,
    plan_allocation,
    score_assessment,
    validate_allocation_state,
)
from papertrader.atomic_io import atomic_write_csv, atomic_write_text
from papertrader.config import Settings
from papertrader.execution import ensure_initial_capital, process_order_fill
from papertrader.market_data import write_price_cache
from papertrader.models import (
    MarketBar,
    OrderLegSpec,
    PositionMark,
    PriceBar,
    ReferencePrice,
    RiskPosition,
    RiskState,
)
from papertrader.orders import (
    OrderError,
    create_baseline_paper_order,
    create_paper_order,
    create_signal,
)
from papertrader.portfolio import build_risk_state, rebuild_portfolio, reconcile_portfolio
from papertrader.research import ResearchStateError, upsert_assessment, upsert_strategy
from papertrader.tables import contract_by_name, read_table, write_table
from papertrader.utils import decimal_text, format_timestamp, required_decimal

NOW = datetime(2026, 7, 24, 22, tzinfo=UTC)


def _security(index: int, *, sector: str | None = None) -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "security_id": f"sec_{suffix}",
        "issuer_id": f"issuer_{suffix}",
        "company_name": f"Allocation Candidate {suffix}",
        "instrument_name": f"Allocation Candidate {suffix} common stock",
        "instrument_type": "equity",
        "ticker": f"A{suffix}",
        "exchange_code": "XETR",
        "venue_mic": "XETR",
        "provider_symbol": f"A{suffix}.DE",
        "broker_symbol": "",
        "currency": "EUR",
        "country": "DE",
        "sector": sector or f"Sector {suffix}",
        "industry": "Allocation fixture",
        "status": "active",
        "watchlist_reason": "Opportunity-cost allocation fixture.",
        "research_summary": "Evidence-backed allocation fixture.",
        "research_page": "",
        "last_research_at": "2026-07-24T21:00:00Z",
        "next_review_at": "2026-08-23T21:00:00Z",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-24T21:00:00Z",
        "source": "fixture",
    }


def _source(index: int) -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "source_id": f"source_{suffix}",
        "url": f"https://example.test/{suffix}",
        "canonical_url": f"https://example.test/{suffix}",
        "source_type": "filing",
        "title": f"Candidate {suffix} filing",
        "publisher": f"Allocation Candidate {suffix}",
        "license": "public-record",
        "status": "available",
        "content_hash": suffix * 32,
        "first_seen_at": "2026-07-24T20:00:00Z",
        "last_checked_at": "2026-07-24T20:00:00Z",
        "last_changed_at": "2026-07-24T20:00:00Z",
        "related_entity_ids": f"sec_{suffix}",
    }


def _relationship(index: int, *, common_theme: bool = False) -> dict[str, str]:
    suffix = f"{index:02d}"
    idea_id = "idea_common" if common_theme else f"idea_{suffix}"
    return {
        "relationship_id": f"relationship_{suffix}",
        "idea_id": idea_id,
        "security_id": f"sec_{suffix}",
        "relationship_type": "beneficiary",
        "direction": "positive",
        "mechanism": "The candidate benefits from the researched demand mechanism.",
        "sensitivity": "medium",
        "confidence": "high",
        "catalyst": "Evidence converts into durable cash flow.",
        "invalidation": "The demand mechanism fails.",
        "status": "accepted",
        "research_page": "",
        "last_reviewed_at": "2026-07-24T21:00:00Z",
        "next_review_at": "2026-08-23T21:00:00Z",
        "created_at": "2026-07-24T21:00:00Z",
        "updated_at": "2026-07-24T21:00:00Z",
    }


def _assessment(
    index: int,
    *,
    eligibility: str = "baseline",
    confidence: str = "high",
    score: int = 80,
    hard_blockers: str = "",
    soft_gaps: str = "",
    assessed_at: str = "2026-07-24T21:00:00Z",
) -> dict[str, str]:
    suffix = f"{index:02d}"
    return {
        "security_id": f"sec_{suffix}",
        "assessed_at": assessed_at,
        "expires_at": "2026-08-23T21:00:00Z",
        "eligibility": eligibility,
        "confidence": confidence,
        "thesis_score": str(score),
        "business_quality_score": str(score),
        "balance_sheet_score": str(score),
        "valuation_score": str(score),
        "timing_score": str(score),
        "liquidity_score": str(score),
        "risk_penalty": "0",
        "downside_pct": "-20",
        "base_upside_pct": "25",
        "valuation_horizon_months": "12",
        "hard_blockers": hard_blockers,
        "soft_gaps": soft_gaps,
        "evidence_refs": f"source_{suffix}",
        "run_id": "assessment-run",
    }


def _bar(
    index: int,
    *,
    close: str = "100",
    bar_date: date = date(2026, 7, 24),
    retrieved_at: datetime = NOW,
) -> PriceBar:
    suffix = f"{index:02d}"
    value = Decimal(close)
    return PriceBar(
        date=bar_date,
        open=value,
        high=value + Decimal("1"),
        low=value - Decimal("1"),
        close=value,
        adjusted_close=value,
        volume=1_000_000,
        dividends=Decimal("0"),
        stock_splits=Decimal("0"),
        currency="EUR",
        provider_symbol=f"A{suffix}.DE",
        retrieved_at=retrieved_at,
        source="fixture",
    )


def _write_price(repository: Path, security_id: str, bar: PriceBar) -> None:
    write_price_cache(repository, security_id, (bar,))
    rows = [
        row for row in read_table(repository, "market_latest") if row["security_id"] != security_id
    ]
    rows.append(
        {
            "security_id": security_id,
            "provider_symbol": bar.provider_symbol,
            "price_date": bar.date.isoformat(),
            "retrieved_at": format_timestamp(bar.retrieved_at),
            "open": decimal_text(bar.open),
            "high": decimal_text(bar.high),
            "low": decimal_text(bar.low),
            "close": decimal_text(bar.close),
            "adjusted_close": decimal_text(bar.adjusted_close),
            "volume": str(bar.volume),
            "currency": bar.currency,
            "source": bar.source,
            "status": "ok",
            "error": "",
        }
    )
    write_table(repository, "market_latest", sorted(rows, key=lambda row: row["security_id"]))


def _seed_candidates(
    repository: Path,
    settings: Settings,
    count: int,
    *,
    common_sector: bool = False,
    common_theme: bool = False,
    blocked: frozenset[int] = frozenset(),
    soft_gaps: frozenset[int] = frozenset(),
) -> None:
    ensure_initial_capital(
        repository,
        settings,
        run_id="allocation-seed",
        occurred_at=NOW - timedelta(hours=2),
    )
    write_table(
        repository,
        "securities",
        [
            _security(index, sector="Shared sector" if common_sector else None)
            for index in range(count)
        ],
    )
    write_table(repository, "source_registry", [_source(index) for index in range(count)])
    write_table(
        repository,
        "relationships",
        [_relationship(index, common_theme=common_theme) for index in range(count)],
    )
    for index in range(count):
        blocker = "valuation_unsupported" if index in blocked else ""
        upsert_assessment(
            repository,
            settings,
            _assessment(
                index,
                eligibility="ineligible" if blocker else "baseline",
                hard_blockers=blocker,
                soft_gaps="confidence_medium" if index in soft_gaps else "",
            ),
            now=NOW,
        )
        _write_price(repository, f"sec_{index:02d}", _bar(index))


def _settings(settings: Settings, **changes: object) -> Settings:
    return replace(settings, allocation=replace(settings.allocation, **changes))


def test_payoff_gates_reject_low_upside_and_asymmetric_downside(
    sandbox_settings: Settings,
) -> None:
    assessment = _assessment(0)
    assessment["base_upside_pct"] = "2.5"
    assessment["downside_pct"] = "-23.2"

    assert assessment_payoff_reasons(assessment, sandbox_settings) == (
        "base_upside_below_minimum",
        "upside_downside_ratio_below_minimum",
    )


def _maintained_security_page(
    repository: Path, security: dict[str, str], idea_id: str
) -> dict[str, str]:
    page = f"data/wiki/securities/{security['security_id']}.md"
    idea_page = repository / "data" / "wiki" / "ideas" / f"{idea_id}.md"
    if not idea_page.exists():
        atomic_write_text(
            idea_page,
            f"---\ntitle: {idea_id}\ntype: idea\nstatus: maintained\n---\n\n# {idea_id}\n",
            allowed_root=repository,
        )
    atomic_write_text(
        repository / page,
        (
            f"---\ntitle: {security['company_name']}\ntype: security\nstatus: maintained\n"
            f"---\n\n# {security['company_name']}\n\n[[ideas/{idea_id}]]\n"
        ),
        allowed_root=repository,
    )
    return {**security, "research_page": page}


def test_maintenance_backfill_is_stable_and_relationships_depend_on_security_refresh(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    researched = [
        _maintained_security_page(sandbox_repository, _security(index), f"idea_{index:02d}")
        for index in range(2)
    ]
    write_table(sandbox_repository, "securities", [*researched, _security(2)])

    first = maintain_allocation_research(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-backfill",
        backfill=True,
        now=NOW,
    )
    assert first.researched_security_count == 2
    assert first.relationship_pair_count == 2
    assert len(first.security_operations) == 2
    assert len(first.relationship_operations) == 2
    assert len(first.operations_created) == 4
    rows = {row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")}
    for operation_id in first.relationship_operations:
        relationship = rows[operation_id]
        dependency = relationship["depends_on"]
        assert dependency in first.security_operations
        assert rows[dependency]["entity_id"] in relationship["prompt"]

    repeated = maintain_allocation_research(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-backfill-repeat",
        backfill=True,
        now=NOW,
    )
    assert repeated.operations_created == ()
    assert repeated.security_operations == first.security_operations
    assert repeated.relationship_operations == first.relationship_operations


def test_maintenance_backfill_reuses_equivalent_active_refresh_work(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    security = _maintained_security_page(sandbox_repository, _security(0), "idea_00")
    write_table(sandbox_repository, "securities", [security])

    refresh = maintain_allocation_research(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-refresh-first",
        now=NOW,
    )
    backfill = maintain_allocation_research(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-backfill-second",
        backfill=True,
        now=NOW + timedelta(seconds=1),
    )

    assert backfill.operations_created == ()
    assert backfill.security_operations == refresh.security_operations
    assert backfill.relationship_operations == refresh.relationship_operations
    assert len(read_table(sandbox_repository, "operations_todo")) == 2


def test_maintenance_refresh_lead_enqueues_near_expiry_assessment(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    security = _maintained_security_page(sandbox_repository, _security(0), "idea_00")
    write_table(sandbox_repository, "securities", [security])
    write_table(sandbox_repository, "source_registry", [_source(0)])
    assessment = _assessment(0)
    assessment["expires_at"] = "2026-07-30T21:00:00Z"
    upsert_assessment(sandbox_repository, sandbox_settings, assessment, now=NOW)
    write_table(sandbox_repository, "relationships", [_relationship(0)])

    result = maintain_allocation_research(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-refresh",
        now=NOW,
    )
    assert len(result.security_operations) == 1
    assert result.relationship_operations == ()


def test_readiness_requires_current_assessment_evidence_relationship_and_finished_backfill(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    security = _maintained_security_page(sandbox_repository, _security(0), "idea_00")
    write_table(sandbox_repository, "securities", [security])
    missing = allocation_readiness(sandbox_repository, sandbox_settings, now=NOW)
    assert not missing.ready
    assert missing.researched_security_count == 1
    assert "assessment_missing:sec_00" in missing.errors

    write_table(sandbox_repository, "source_registry", [_source(0)])
    upsert_assessment(sandbox_repository, sandbox_settings, _assessment(0), now=NOW)
    write_table(sandbox_repository, "relationships", [_relationship(0)])
    ready = allocation_readiness(sandbox_repository, sandbox_settings, now=NOW)
    assert ready.ready
    assert ready.current_assessment_count == 1
    assert ready.fresh_evidence_assessment_count == 1
    assert ready.current_relationship_pair_count == 1

    rejected_relationship = _relationship(0)
    rejected_relationship["status"] = "rejected"
    write_table(sandbox_repository, "relationships", [rejected_relationship])
    rejected = allocation_readiness(sandbox_repository, sandbox_settings, now=NOW)
    assert "rejected_relationship_unreconciled:relationship_00" in rejected.errors

    reconciled_assessment = _assessment(
        0,
        eligibility="ineligible",
        hard_blockers="valuation_unsupported",
        assessed_at="2026-07-24T22:00:00Z",
    )
    upsert_assessment(
        sandbox_repository,
        sandbox_settings,
        reconciled_assessment,
        now=NOW,
    )
    reconciled = allocation_readiness(sandbox_repository, sandbox_settings, now=NOW)
    assert reconciled.ready

    maintain_allocation_research(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-readiness-backfill",
        backfill=True,
        now=NOW,
    )
    active = allocation_readiness(sandbox_repository, sandbox_settings, now=NOW)
    assert not active.ready
    assert any(error.startswith("backfill_operation_active:") for error in active.errors)


def test_allocation_plans_researched_security_without_assessment_only(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id="researched-universe-seed",
        occurred_at=NOW - timedelta(hours=1),
    )
    researched = _maintained_security_page(sandbox_repository, _security(0), "idea_00")
    write_table(sandbox_repository, "securities", [researched, _security(1)])

    result = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="researched-universe",
        now=NOW,
    )
    rows = read_table(sandbox_repository, "allocation_targets")
    assert result.target_count == 1
    assert [row["security_id"] for row in rows] == ["sec_00"]
    assert "assessment_missing" in rows[0]["reason"]


def test_score_aggregation_is_exact_decimal_and_cash_aware() -> None:
    assessment: dict[str, object] = {
        "thesis_score": "80",
        "business_quality_score": "70",
        "balance_sheet_score": "60",
        "valuation_score": "90",
        "timing_score": "50",
        "liquidity_score": "100",
        "risk_penalty": "5",
        "confidence": "medium",
    }

    score = score_assessment(assessment, Decimal("50"))

    assert score.raw_score == Decimal("75.50")
    assert score.effective_score == Decimal("55.40")
    assert score.candidate_edge == Decimal("5.40")
    assert score_assessment(assessment, Decimal("60")).candidate_edge == 0


def test_assessment_upsert_enforces_lifecycle_evidence_and_blockers(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    write_table(sandbox_repository, "securities", [_security(0)])
    write_table(sandbox_repository, "source_registry", [_source(0)])
    request = _assessment(0, soft_gaps="confidence_medium")

    assert upsert_assessment(sandbox_repository, sandbox_settings, request, now=NOW)
    assert not upsert_assessment(sandbox_repository, sandbox_settings, request, now=NOW)
    sources = read_table(sandbox_repository, "source_registry")
    sources[0]["last_checked_at"] = "2026-07-24T22:00:00Z"
    write_table(sandbox_repository, "source_registry", sources)
    assert validate_allocation_state(sandbox_repository, sandbox_settings) == []
    sources[0]["last_checked_at"] = "2026-07-24T20:00:00Z"
    write_table(sandbox_repository, "source_registry", sources)
    with pytest.raises(ResearchStateError, match="hard blocker forces"):
        upsert_assessment(
            sandbox_repository,
            sandbox_settings,
            request | {"hard_blockers": "solvency_risk"},
            now=NOW,
        )
    with pytest.raises(ResearchStateError, match="non-canonical"):
        upsert_assessment(
            sandbox_repository,
            sandbox_settings,
            request | {"soft_gaps": "made_up_gap"},
            now=NOW,
        )
    with pytest.raises(ResearchStateError, match="future-dated"):
        upsert_assessment(
            sandbox_repository,
            sandbox_settings,
            request | {"assessed_at": "2026-07-25T00:00:00Z"},
            now=NOW,
        )
    with pytest.raises(ResearchStateError, match="older than current"):
        upsert_assessment(
            sandbox_repository,
            sandbox_settings,
            request
            | {
                "assessed_at": "2026-07-24T20:30:00Z",
                "expires_at": "2026-08-22T20:30:00Z",
            },
            now=NOW,
        )


def test_strict_allocation_state_rejects_noncanonical_assessment_values(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 1)
    assert validate_allocation_state(sandbox_repository, sandbox_settings) == []
    rows = read_table(sandbox_repository, "security_assessments")
    rows[0]["soft_gaps"] = "made_up_gap"
    write_table(sandbox_repository, "security_assessments", rows)

    assert any(
        "assessment soft gaps are invalid" in error
        for error in validate_allocation_state(sandbox_repository, sandbox_settings)
    )
    rows[0]["soft_gaps"] = ""
    write_table(sandbox_repository, "security_assessments", rows)
    plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-integrity-history",
        now=NOW,
    )
    history = read_table(sandbox_repository, "allocation_history")
    history[0]["target_weight_pct"] = "101"
    history_contract = contract_by_name(sandbox_repository, "allocation_history")
    atomic_write_csv(
        sandbox_repository.joinpath(*history_contract.path.parts),
        history_contract.columns,
        history,
        allowed_root=sandbox_repository,
    )

    assert any(
        "invalid allocation history" in error
        for error in validate_allocation_state(sandbox_repository, sandbox_settings)
    )


ALLOCATION_PERMUTATIONS = (
    (0, 1, 2, 3, 4, 5),
    (5, 4, 3, 2, 1, 0),
    (2, 5, 1, 4, 0, 3),
    (3, 0, 4, 1, 5, 2),
)


@given(st.sampled_from(ALLOCATION_PERMUTATIONS))
@hypothesis_settings(
    max_examples=len(ALLOCATION_PERMUTATIONS),
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_allocation_targets_are_order_independent_and_obey_portfolio_properties(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    permutation: tuple[int, ...],
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    accounting_before = {
        name: read_table(sandbox_repository, name)
        for name in (
            "cash_ledger",
            "executions",
            "orders",
            "portfolio",
            "signals",
            "strategies",
            "operations_todo",
        )
    }
    canonical = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-property",
        now=NOW,
    )
    canonical_rows = read_table(sandbox_repository, "allocation_targets")

    securities = {row["security_id"]: row for row in read_table(sandbox_repository, "securities")}
    assessments = {
        row["security_id"]: row for row in read_table(sandbox_repository, "security_assessments")
    }
    relationships = {
        row["security_id"]: row for row in read_table(sandbox_repository, "relationships")
    }
    order = [f"sec_{index:02d}" for index in permutation]
    write_table(sandbox_repository, "securities", [securities[value] for value in order])
    write_table(
        sandbox_repository,
        "security_assessments",
        [assessments[value] for value in order],
    )
    write_table(
        sandbox_repository,
        "relationships",
        [relationships[value] for value in order],
    )
    repeated = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-property",
        now=NOW,
    )
    rows = read_table(sandbox_repository, "allocation_targets")

    assert repeated == canonical
    assert rows == canonical_rows
    assert [row["rank"] for row in rows] == ["1", "2", "3", "4", "5", "6"]
    target_values = [required_decimal(row["target_value_base"]) for row in rows]
    positive_deltas = [max(required_decimal(row["delta_value_base"]), Decimal("0")) for row in rows]
    assert sum(target_values) <= Decimal("30000")
    assert all(value <= Decimal("5000") for value in target_values)
    assert sum(positive_deltas) <= required_decimal(canonical.deployment_budget_base)
    assert Decimal(canonical.cash_base) - sum(positive_deltas) >= Decimal("25000")
    assert sum(positive_deltas) == Decimal("15000")
    assert len(read_table(sandbox_repository, "allocation_history")) == 6
    assert read_table(sandbox_repository, "operations_todo") == []
    assert {
        name: read_table(sandbox_repository, name) for name in accounting_before
    } == accounting_before


def test_allocation_plan_matches_reference_output(
    repository_root: Path,
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)

    result = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-reference",
        now=NOW,
    )
    summary_fields = (
        "as_of",
        "mode",
        "equity_base",
        "cash_base",
        "minimum_cash_reserve_base",
        "current_gross_exposure_base",
        "target_invested_exposure_base",
        "current_conviction_exposure_base",
        "current_baseline_exposure_base",
        "maximum_baseline_exposure_base",
        "pending_gross_exposure_base",
        "deployment_budget_base",
        "diversified_budget_base",
        "capital_allocated_base",
        "capital_unallocated_base",
        "unallocated_reasons",
        "eligible_candidate_count",
        "excluded_candidate_count",
        "target_count",
    )
    target_fields = (
        "security_id",
        "sleeve",
        "rank",
        "effective_score",
        "candidate_edge",
        "current_weight_pct",
        "pending_weight_pct",
        "target_weight_pct",
        "target_value_base",
        "delta_value_base",
        "disposition",
        "reason",
        "assessment_as_of",
    )
    actual = {
        "summary": {field: getattr(result, field) for field in summary_fields},
        "targets": [
            {field: row[field] for field in target_fields}
            for row in read_table(sandbox_repository, "allocation_targets")
        ],
    }
    actual["summary"]["unallocated_reasons"] = list(result.unallocated_reasons)
    expected = json.loads(
        (repository_root / "tests" / "reference_outputs" / "allocation_plan.json").read_text(
            encoding="utf-8"
        )
    )

    assert actual == expected


def test_allocation_plan_identity_binds_corrected_market_inputs(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    original = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-market-identity",
        now=NOW,
    )

    _write_price(sandbox_repository, "sec_00", _bar(0, close="101"))
    corrected = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-market-identity",
        now=NOW,
    )

    assert corrected.allocation_plan_id != original.allocation_plan_id
    assert len(read_table(sandbox_repository, "allocation_history")) == 12


def test_allocation_plan_identity_ignores_run_metadata_when_inputs_are_unchanged(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    original = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-first-publication",
        now=NOW,
    )
    repeated = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-second-publication",
        now=NOW + timedelta(minutes=5),
    )

    assert repeated.allocation_plan_id == original.allocation_plan_id
    history = read_table(sandbox_repository, "allocation_history")
    assert len(history) == 12
    assert {row["allocation_plan_id"] for row in history} == {original.allocation_plan_id}
    assert {row["run_id"] for row in history} == {
        "allocation-first-publication",
        "allocation-second-publication",
    }
    assert validate_allocation_state(sandbox_repository, sandbox_settings) == []


def test_same_run_allocation_retry_reuses_first_immutable_observation(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    original = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-retry",
        now=NOW,
    )
    original_targets = read_table(sandbox_repository, "allocation_targets")

    repeated = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-retry",
        now=NOW + timedelta(minutes=5),
    )

    assert repeated.allocation_plan_id == original.allocation_plan_id
    assert repeated.as_of == original.as_of
    assert read_table(sandbox_repository, "allocation_targets") == original_targets
    assert len(read_table(sandbox_repository, "allocation_history")) == 6
    assert validate_allocation_state(sandbox_repository, sandbox_settings) == []


def test_terminal_order_history_does_not_change_economic_plan_identity(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    original = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-before-cancelled-order",
        now=NOW,
    )
    write_table(
        sandbox_repository,
        "orders",
        [
            {
                "order_id": "order_cancelled",
                "signal_id": "signal_cancelled",
                "strategy_id": "strategy_cancelled",
                "created_at": "2026-07-24T09:00:00Z",
                "status": "cancelled",
                "fill_policy": "next_open",
                "not_before": "2026-07-24T09:00:00Z",
                "expires_at": "2026-07-25T09:00:00Z",
                "order_type": "market",
                "limit_price": "",
                "slippage_bps": "5",
                "fee_model": "fixed_plus_bps",
                "currency": "EUR",
                "run_id": "cancelled-order-fixture",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "order_legs",
        [
            {
                "order_id": "order_cancelled",
                "leg_id": "leg_1",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": "sec_00",
                "provider_contract_id": "",
                "option_type": "",
                "expiry": "",
                "strike": "",
                "quantity": "1",
                "contract_multiplier": "1",
                "limit_price": "",
                "currency": "EUR",
            }
        ],
    )

    repeated = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-after-cancelled-order",
        now=NOW,
    )

    assert repeated.allocation_plan_id == original.allocation_plan_id


@pytest.mark.parametrize(
    ("count", "blocked", "expected_budget", "expected_eligible"),
    [
        (0, frozenset(), "0", 0),
        (1, frozenset(), "2500", 1),
        (1, frozenset({0}), "0", 0),
        (3, frozenset(), "7500", 3),
    ],
)
def test_diversification_and_hard_blockers_leave_capital_in_cash(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    count: int,
    blocked: frozenset[int],
    expected_budget: str,
    expected_eligible: int,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, count, blocked=blocked)

    result = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-diversification",
        now=NOW,
    )
    rows = read_table(sandbox_repository, "allocation_targets")

    assert result.eligible_candidate_count == expected_eligible
    assert result.capital_allocated_base == expected_budget
    assert all(
        required_decimal(row["target_value_base"]) == 0
        for row in rows
        if "hard_blocker:" in row["reason"]
    )
    if 0 < expected_eligible < 6:
        assert all("insufficient_diversification" in row["reason"] for row in rows if row["rank"])


@pytest.mark.parametrize(
    ("common_sector", "common_theme", "setting_name"),
    [
        (True, False, "maximum_sector_pct"),
        (False, True, "maximum_theme_pct"),
    ],
)
def test_shared_concentration_caps_force_partial_deployment(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    common_sector: bool,
    common_theme: bool,
    setting_name: str,
) -> None:
    _seed_candidates(
        sandbox_repository,
        sandbox_settings,
        6,
        common_sector=common_sector,
        common_theme=common_theme,
    )
    settings = _settings(sandbox_settings, **{setting_name: Decimal("12")})

    result = plan_allocation(
        sandbox_repository,
        settings,
        run_id=f"allocation-{setting_name}",
        now=NOW,
    )
    targets = read_table(sandbox_repository, "allocation_targets")
    target_total = sum(
        (required_decimal(row["target_value_base"]) for row in targets), Decimal("0")
    )

    if common_theme:
        # Securities connected by one accepted idea are one diversification
        # component, so a single-theme universe cannot unlock deployment.
        assert target_total == 0
    else:
        assert Decimal("0") < target_total <= Decimal("12000")
    assert required_decimal(result.capital_allocated_base) == target_total
    assert required_decimal(result.capital_unallocated_base) >= Decimal("3000")


def test_minimum_trade_threshold_prevents_dust_positions(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(
        sandbox_repository,
        sandbox_settings,
        6,
        common_sector=True,
    )
    settings = _settings(sandbox_settings, maximum_sector_pct=Decimal("5"))

    result = plan_allocation(
        sandbox_repository,
        settings,
        run_id="allocation-minimum-trade",
        now=NOW,
    )
    rows = read_table(sandbox_repository, "allocation_targets")

    assert result.capital_allocated_base == "0"
    assert all(row["disposition"] == "below_minimum_trade" for row in rows)
    assert all("minimum_trade_threshold" in row["reason"] for row in rows)


def test_stale_assessment_is_excluded_with_zero_target(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 1)
    rows = read_table(sandbox_repository, "security_assessments")
    rows[0]["assessed_at"] = "2026-06-20T21:00:00Z"
    write_table(sandbox_repository, "security_assessments", rows)

    plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-stale-assessment",
        now=NOW,
    )
    target = read_table(sandbox_repository, "allocation_targets")[0]

    assert target["target_value_base"] == "0"
    assert target["disposition"] == "excluded"
    assert "assessment_stale" in target["reason"]


def test_pending_conviction_order_reduces_cash_and_target_exposure_capacity(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    write_table(
        sandbox_repository,
        "strategies",
        [
            {
                "strategy_id": "strategy_pending_conviction",
                "idea_id": "idea_00",
                "security_id": "sec_00",
                "relationship_id": "relationship_00",
                "name": "Pending conviction fixture",
                "status": "ready",
                "direction": "long",
                "instrument_type": "equity",
                "thesis": "Exercise committed pending exposure.",
                "entry_rule": "Use the pending fixture order.",
                "exit_rule": "Exit outside this fixture.",
                "invalidation": "The fixture fails.",
                "risk_budget_pct": "10",
                "sleeve": "conviction",
                "allocation_plan_id": "",
                "not_before": "",
                "expires_at": "",
                "research_page": "",
                "created_at": "2026-07-24T20:00:00Z",
                "updated_at": "2026-07-24T20:00:00Z",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "orders",
        [
            {
                "order_id": "order_pending_conviction",
                "signal_id": "signal_pending_conviction",
                "strategy_id": "strategy_pending_conviction",
                "created_at": "2026-07-24T20:00:00Z",
                "status": "pending",
                "fill_policy": "next_open",
                "not_before": "2026-07-24T20:00:00Z",
                "expires_at": "2026-07-25T20:00:00Z",
                "order_type": "market",
                "limit_price": "",
                "slippage_bps": "5",
                "fee_model": "fixed_plus_bps",
                "currency": "EUR",
                "run_id": "pending-seed",
            }
        ],
    )
    write_table(
        sandbox_repository,
        "order_legs",
        [
            {
                "order_id": "order_pending_conviction",
                "leg_id": "leg_pending_conviction",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": "sec_00",
                "provider_contract_id": "",
                "option_type": "",
                "expiry": "",
                "strike": "",
                "quantity": "500",
                "contract_multiplier": "1",
                "limit_price": "",
                "currency": "EUR",
            }
        ],
    )

    result = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-pending",
        now=NOW,
    )
    targets = read_table(sandbox_repository, "allocation_targets")
    pending_security = next(row for row in targets if row["security_id"] == "sec_00")

    assert result.pending_gross_exposure_base == "50000"
    assert result.deployment_budget_base == "10000"
    assert result.capital_allocated_base == "8000"
    assert pending_security["target_value_base"] == "0"
    assert pending_security["disposition"] == "excluded"
    assert "conviction_pending_exposure" in pending_security["reason"]


def _create_baseline_strategy(
    repository: Path,
    settings: Settings,
    *,
    security_id: str,
    allocation_plan_id: str,
    quantity: Decimal,
    status: str = "ready",
    now: datetime = NOW,
    risk_budget_pct: str = "5",
) -> str:
    strategy_id = baseline_strategy_id(security_id)
    page = repository / "data" / "wiki" / "strategies" / f"{strategy_id}.md"
    atomic_write_text(
        page,
        "---\ntitle: Baseline allocation fixture\ntype: strategy\nstatus: maintained\n"
        "tags:\n  - strategy\ncreated: 2026-07-24\nupdated: 2026-07-24\n"
        "provenance: test\n---\n\n# Baseline allocation fixture\n",
        allowed_root=repository,
    )
    assert upsert_strategy(
        repository,
        settings,
        {
            "strategy": {
                "strategy_id": strategy_id,
                "idea_id": "idea_00",
                "security_id": security_id,
                "relationship_id": "relationship_00",
                "name": "Baseline allocation fixture",
                "status": status,
                "direction": "long",
                "instrument_type": "equity",
                "thesis": "The evidence-backed candidate clears the cash hurdle.",
                "entry_rule": "Follow the current deterministic allocation target.",
                "exit_rule": "Reduce or close when the allocation target requires it.",
                "invalidation": "A hard blocker or superseding plan invalidates the target.",
                "risk_budget_pct": risk_budget_pct,
                "sleeve": "baseline",
                "allocation_plan_id": allocation_plan_id,
                "not_before": "",
                "expires_at": "",
                "research_page": f"data/wiki/strategies/{strategy_id}.md",
            },
            "legs": [
                {
                    "leg_id": "leg_1",
                    "action": "buy",
                    "side": "long",
                    "instrument_type": "equity",
                    "security_id": security_id,
                    "provider_contract_id": "",
                    "option_type": "",
                    "expiry": "",
                    "strike": "",
                    "quantity": str(quantity),
                    "contract_multiplier": "1",
                    "order_type": "market",
                    "limit_price": "",
                    "currency": "EUR",
                }
            ],
        },
        now=now,
    )
    return strategy_id


def _create_conviction_strategy(
    repository: Path,
    settings: Settings,
    *,
    security_id: str,
    quantity: Decimal,
    now: datetime = NOW,
) -> str:
    strategy_id = f"strategy_conviction_{security_id}"
    page = repository / "data" / "wiki" / "strategies" / f"{strategy_id}.md"
    atomic_write_text(
        page,
        "---\ntitle: Conviction allocation fixture\ntype: strategy\nstatus: maintained\n"
        "tags:\n  - strategy\ncreated: 2026-07-24\nupdated: 2026-07-24\n"
        "provenance: test\n---\n\n# Conviction allocation fixture\n",
        allowed_root=repository,
    )
    assert upsert_strategy(
        repository,
        settings,
        {
            "strategy": {
                "strategy_id": strategy_id,
                "idea_id": "idea_00",
                "security_id": security_id,
                "relationship_id": "relationship_00",
                "name": "Conviction allocation fixture",
                "status": "ready",
                "direction": "long",
                "instrument_type": "equity",
                "thesis": "The candidate passes the independent conviction process.",
                "entry_rule": "Enter only through the conviction strategy lifecycle.",
                "exit_rule": "Exit through the conviction strategy lifecycle.",
                "invalidation": "The conviction thesis fails.",
                "risk_budget_pct": "5",
                "sleeve": "conviction",
                "allocation_plan_id": "",
                "not_before": "",
                "expires_at": "",
                "research_page": f"data/wiki/strategies/{strategy_id}.md",
            },
            "legs": [
                {
                    "leg_id": "leg_1",
                    "action": "buy",
                    "side": "long",
                    "instrument_type": "equity",
                    "security_id": security_id,
                    "provider_contract_id": "",
                    "option_type": "",
                    "expiry": "",
                    "strike": "",
                    "quantity": str(quantity),
                    "contract_multiplier": "1",
                    "order_type": "market",
                    "limit_price": "",
                    "currency": "EUR",
                }
            ],
        },
        now=now,
    )
    return strategy_id


def test_active_handoff_is_idempotent_and_order_quantity_is_code_owned(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    active = _settings(sandbox_settings, mode="active")
    result = plan_allocation(
        sandbox_repository,
        active,
        run_id="allocation-active",
        now=NOW,
    )
    assert len(result.operations_created) == 6
    assert len(read_table(sandbox_repository, "operations_todo")) == 6
    repeated = plan_allocation(
        sandbox_repository,
        active,
        run_id="allocation-active",
        now=NOW,
    )
    assert repeated.operations_created == ()
    assert len(read_table(sandbox_repository, "operations_todo")) == 6

    target = next(
        row
        for row in read_table(sandbox_repository, "allocation_targets")
        if row["security_id"] == "sec_00"
    )
    target_quantity = required_decimal(target["target_value_base"]) / Decimal("100")
    strategy_id = _create_baseline_strategy(
        sandbox_repository,
        active,
        security_id="sec_00",
        allocation_plan_id=target["allocation_plan_id"],
        quantity=target_quantity,
    )
    signal_id, _ = create_signal(
        sandbox_repository,
        active,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Use the current deterministic baseline target.",
        market_data_as_of=NOW,
        run_id="allocation-active",
        expires_at=NOW + timedelta(days=5),
        now=NOW,
    )
    reference = ReferencePrice(
        security_id="sec_00",
        provider_contract_id="",
        price=Decimal("100"),
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=NOW,
    )
    risk_state = build_risk_state(sandbox_repository, (reference,), as_of=NOW)

    def leg(quantity: Decimal, *, security_id: str = "sec_00") -> OrderLegSpec:
        return OrderLegSpec(
            leg_id="leg_1",
            action="buy",
            side="long",
            instrument_type="equity",
            security_id=security_id,
            provider_contract_id="",
            option_type="",
            expiry=None,
            strike=None,
            quantity=quantity,
            contract_multiplier=Decimal("1"),
            limit_price=None,
            currency="EUR",
        )

    with pytest.raises(OrderError, match="deterministic target quantity"):
        create_paper_order(
            sandbox_repository,
            active,
            signal_id=signal_id,
            strategy_id=strategy_id,
            legs=(leg(target_quantity - 1),),
            references=(reference,),
            risk_state=risk_state,
            run_id="allocation-active",
            now=NOW,
        )
    with pytest.raises(OrderError, match="canonical strategy leg identities"):
        create_paper_order(
            sandbox_repository,
            active,
            signal_id=signal_id,
            strategy_id=strategy_id,
            legs=(leg(target_quantity, security_id="sec_01"),),
            references=(reference,),
            risk_state=risk_state,
            run_id="allocation-active",
            now=NOW,
        )
    with pytest.raises(OrderError, match="minimum cash reserve"):
        create_paper_order(
            sandbox_repository,
            active,
            signal_id=signal_id,
            strategy_id=strategy_id,
            legs=(leg(target_quantity),),
            references=(reference,),
            risk_state=replace(risk_state, cash_base=Decimal("26000")),
            run_id="allocation-active",
            now=NOW,
        )
    order_id, created, assessment = create_baseline_paper_order(
        sandbox_repository,
        active,
        signal_id=signal_id,
        strategy_id=strategy_id,
        references=(reference,),
        risk_state=risk_state,
        run_id="allocation-active",
        expires_at=NOW + timedelta(days=5),
        now=NOW,
    )
    assert created and order_id
    assert assessment.violations == ()
    assert read_table(sandbox_repository, "order_legs")[0]["quantity"] == str(target_quantity)
    assert read_table(sandbox_repository, "cash_ledger")[0]["base_amount"] == "100000"
    assert read_table(sandbox_repository, "executions") == []

    pending_replan = plan_allocation(
        sandbox_repository,
        active,
        run_id="allocation-pending-replan",
        now=NOW + timedelta(minutes=1),
    )
    pending_target = next(
        row
        for row in read_table(sandbox_repository, "allocation_targets")
        if row["security_id"] == "sec_00"
    )
    assert pending_replan.pending_gross_exposure_base == pending_target["target_value_base"]
    assert pending_replan.allocation_plan_id == result.allocation_plan_id
    assert pending_target["delta_value_base"] == "0"
    assert pending_target["disposition"] == "hold"

    _write_price(
        sandbox_repository,
        "sec_00",
        _bar(0, close="99", retrieved_at=NOW + timedelta(minutes=2)),
    )
    repriced = plan_allocation(
        sandbox_repository,
        active,
        run_id="allocation-pending-repriced",
        now=NOW + timedelta(minutes=2),
    )
    repriced_target = next(
        row
        for row in read_table(sandbox_repository, "allocation_targets")
        if row["security_id"] == "sec_00"
    )
    assert repriced.allocation_plan_id != result.allocation_plan_id
    assert repriced_target["allocation_intent_id"] == target["allocation_intent_id"]
    assert repriced_target["target_quantity"] == target["target_quantity"]
    assert repriced_target["disposition"] == "hold"
    assert read_table(sandbox_repository, "orders")[0]["status"] == "pending"
    strategy = next(
        row
        for row in read_table(sandbox_repository, "strategies")
        if row["strategy_id"] == strategy_id
    )
    assert strategy["allocation_plan_id"] == repriced.allocation_plan_id

    fill_time = datetime(2026, 7, 27, 8, tzinfo=UTC)
    fill_reference = replace(reference, as_of=fill_time)
    status, execution_ids = process_order_fill(
        sandbox_repository,
        active,
        order_id=order_id,
        bars=(
            MarketBar(
                security_id="sec_00",
                provider_contract_id="",
                timestamp=datetime(2026, 7, 27, 7, tzinfo=UTC),
                open=Decimal("100"),
                high=Decimal("101"),
                low=Decimal("99"),
                close=Decimal("100"),
                currency="EUR",
                fx_rate_to_base=Decimal("1"),
            ),
        ),
        quotes=(),
        risk_state=build_risk_state(
            sandbox_repository,
            (fill_reference,),
            as_of=fill_time,
        ),
        risk_references=(fill_reference,),
        run_id="allocation-fill",
        now=fill_time,
    )
    assert status == "filled" and len(execution_ids) == 1
    rebuild_portfolio(
        sandbox_repository,
        marks=(
            PositionMark(
                security_id="sec_00",
                provider_contract_id="",
                price=Decimal("100"),
                currency="EUR",
                fx_rate_to_base=Decimal("1"),
                marked_at=fill_time,
            ),
        ),
        run_id="allocation-fill",
        as_of=fill_time,
    )
    assert reconcile_portfolio(sandbox_repository) == []
    for index in range(6):
        _write_price(
            sandbox_repository,
            f"sec_{index:02d}",
            _bar(
                index,
                bar_date=date(2026, 7, 27),
                retrieved_at=fill_time,
            ),
        )
    second = plan_allocation(
        sandbox_repository,
        replace(active, allocation=replace(active.allocation, mode="report_only")),
        run_id="allocation-second-stage",
        now=fill_time,
    )
    second_targets = read_table(sandbox_repository, "allocation_targets")
    current_target = next(row for row in second_targets if row["security_id"] == "sec_00")

    assert second.current_baseline_exposure_base == "2500"
    assert second.current_conviction_exposure_base == "0"
    assert current_target["disposition"] == "increase"
    assert required_decimal(current_target["target_value_base"]) <= Decimal("5000")
    assert len(read_table(sandbox_repository, "allocation_history")) == 24

    increase_quantity = required_decimal(current_target["target_value_base"]) / Decimal(
        "100"
    ) - Decimal("25")
    assert increase_quantity > 0
    with pytest.raises(ResearchStateError, match="must equal the configured position cap"):
        _create_baseline_strategy(
            sandbox_repository,
            active,
            security_id="sec_00",
            allocation_plan_id=current_target["allocation_plan_id"],
            quantity=increase_quantity,
            status="active",
            now=fill_time,
            risk_budget_pct="3",
        )
    _create_baseline_strategy(
        sandbox_repository,
        active,
        security_id="sec_00",
        allocation_plan_id=current_target["allocation_plan_id"],
        quantity=increase_quantity,
        status="active",
        now=fill_time,
    )
    increase_signal, signal_created = create_signal(
        sandbox_repository,
        active,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Increase only to the second-stage deterministic target.",
        market_data_as_of=fill_time,
        run_id="allocation-second-stage",
        expires_at=fill_time + timedelta(days=5),
        now=fill_time,
    )
    assert signal_created
    increase_order, increase_created, _ = create_paper_order(
        sandbox_repository,
        active,
        signal_id=increase_signal,
        strategy_id=strategy_id,
        legs=(leg(increase_quantity),),
        references=(fill_reference,),
        risk_state=build_risk_state(
            sandbox_repository,
            (fill_reference,),
            as_of=fill_time,
        ),
        run_id="allocation-second-stage",
        expires_at=fill_time + timedelta(days=5),
        now=fill_time,
    )
    assert increase_created and increase_order

    conviction_strategy = _create_conviction_strategy(
        sandbox_repository,
        active,
        security_id="sec_00",
        quantity=Decimal("1"),
        now=fill_time,
    )
    conviction_signal, _ = create_signal(
        sandbox_repository,
        active,
        strategy_id=conviction_strategy,
        signal_type="open",
        rationale="A mixed-sleeve order must fail closed.",
        market_data_as_of=fill_time,
        run_id="allocation-sleeve-isolation",
        expires_at=fill_time + timedelta(days=5),
        now=fill_time,
    )
    with pytest.raises(OrderError, match="cannot mix allocation sleeves"):
        create_paper_order(
            sandbox_repository,
            active,
            signal_id=conviction_signal,
            strategy_id=conviction_strategy,
            legs=(leg(Decimal("1")),),
            references=(fill_reference,),
            risk_state=build_risk_state(
                sandbox_repository,
                (fill_reference,),
                as_of=fill_time,
            ),
            run_id="allocation-sleeve-isolation",
            now=fill_time,
        )


def test_existing_conviction_exposure_is_not_managed_by_baseline_allocator(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    strategy_id = _create_conviction_strategy(
        sandbox_repository,
        sandbox_settings,
        security_id="sec_00",
        quantity=Decimal("20"),
    )
    signal_id, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="open",
        rationale="Open the independent conviction fixture.",
        market_data_as_of=NOW,
        run_id="allocation-conviction",
        expires_at=NOW + timedelta(days=5),
        now=NOW,
    )
    reference = ReferencePrice(
        security_id="sec_00",
        provider_contract_id="",
        price=Decimal("100"),
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=NOW,
    )
    leg = OrderLegSpec(
        leg_id="leg_1",
        action="buy",
        side="long",
        instrument_type="equity",
        security_id="sec_00",
        provider_contract_id="",
        option_type="",
        expiry=None,
        strike=None,
        quantity=Decimal("20"),
        contract_multiplier=Decimal("1"),
        limit_price=None,
        currency="EUR",
    )
    order_id, _, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(leg,),
        references=(reference,),
        risk_state=build_risk_state(sandbox_repository, (reference,), as_of=NOW),
        run_id="allocation-conviction",
        expires_at=NOW + timedelta(days=5),
        now=NOW,
    )
    fill_time = datetime(2026, 7, 25, 8, tzinfo=UTC)
    fill_reference = replace(reference, as_of=fill_time)
    status, _ = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order_id,
        bars=(
            MarketBar(
                security_id="sec_00",
                provider_contract_id="",
                timestamp=datetime(2026, 7, 25, 7, tzinfo=UTC),
                open=Decimal("100"),
                high=Decimal("101"),
                low=Decimal("99"),
                close=Decimal("100"),
                currency="EUR",
                fx_rate_to_base=Decimal("1"),
            ),
        ),
        quotes=(),
        risk_state=build_risk_state(
            sandbox_repository,
            (fill_reference,),
            as_of=fill_time,
        ),
        risk_references=(fill_reference,),
        run_id="allocation-conviction-fill",
        now=fill_time,
    )
    assert status == "filled"
    rebuild_portfolio(
        sandbox_repository,
        marks=(
            PositionMark(
                security_id="sec_00",
                provider_contract_id="",
                price=Decimal("100"),
                currency="EUR",
                fx_rate_to_base=Decimal("1"),
                marked_at=fill_time,
            ),
        ),
        run_id="allocation-conviction-fill",
        as_of=fill_time,
    )
    for index in range(6):
        _write_price(
            sandbox_repository,
            f"sec_{index:02d}",
            _bar(
                index,
                bar_date=date(2026, 7, 25),
                retrieved_at=fill_time,
            ),
        )
    executions_before = read_table(sandbox_repository, "executions")

    result = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-after-conviction",
        now=fill_time,
    )
    target = next(
        row
        for row in read_table(sandbox_repository, "allocation_targets")
        if row["security_id"] == "sec_00"
    )

    assert result.current_conviction_exposure_base == "2000"
    assert result.current_baseline_exposure_base == "0"
    assert target["target_value_base"] == "0"
    assert target["disposition"] == "excluded"
    assert "conviction_exposure_present" in target["reason"]
    assert read_table(sandbox_repository, "executions") == executions_before


def test_hold_and_stale_baseline_plans_cannot_create_signal_churn(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 6)
    result = plan_allocation(
        sandbox_repository,
        sandbox_settings,
        run_id="allocation-signal-guards",
        now=NOW,
    )
    target = next(
        row
        for row in read_table(sandbox_repository, "allocation_targets")
        if row["security_id"] == "sec_00"
    )
    strategy_id = _create_baseline_strategy(
        sandbox_repository,
        sandbox_settings,
        security_id="sec_00",
        allocation_plan_id=result.allocation_plan_id,
        quantity=Decimal("25"),
    )
    rows = read_table(sandbox_repository, "allocation_targets")
    for row in rows:
        if row["security_id"] == "sec_00":
            row["disposition"] = "hold"
            row["delta_value_base"] = "0"
    write_table(sandbox_repository, "allocation_targets", rows)

    with pytest.raises(OrderError, match="material current allocation target"):
        create_signal(
            sandbox_repository,
            sandbox_settings,
            strategy_id=strategy_id,
            signal_type="open",
            rationale="A hold must not churn.",
            market_data_as_of=NOW,
            run_id="allocation-signal-guards",
            now=NOW,
        )
    assert read_table(sandbox_repository, "signals") == []

    for row in rows:
        if row["security_id"] == "sec_00":
            row["disposition"] = "open"
            row["delta_value_base"] = target["delta_value_base"]
    write_table(sandbox_repository, "allocation_targets", rows)
    stale_time = NOW + sandbox_settings.market_data.stale_price_after + timedelta(seconds=1)
    with pytest.raises(OrderError, match="stale or future-dated"):
        create_signal(
            sandbox_repository,
            sandbox_settings,
            strategy_id=strategy_id,
            signal_type="open",
            rationale="A stale plan must not trade.",
            market_data_as_of=stale_time,
            run_id="allocation-signal-guards-stale",
            now=stale_time,
        )
    assert read_table(sandbox_repository, "signals") == []


def test_baseline_reduce_uses_target_owned_quantity_and_normal_order_lifecycle(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 1)
    strategy_id = baseline_strategy_id("sec_00")
    plan_id = "allocation_plan_reduce"
    assessment = read_table(sandbox_repository, "security_assessments")[0]
    write_table(
        sandbox_repository,
        "allocation_targets",
        [
            {
                "allocation_plan_id": plan_id,
                "run_id": "allocation-reduce",
                "as_of": "2026-07-24T22:00:00Z",
                "security_id": "sec_00",
                "strategy_id": strategy_id,
                "sleeve": "baseline",
                "rank": "1",
                "effective_score": "80",
                "candidate_edge": "20",
                "current_weight_pct": "2.5",
                "pending_weight_pct": "0",
                "target_weight_pct": "1.5",
                "target_value_base": "1500",
                "delta_value_base": "-1000",
                "disposition": "reduce",
                "reason": "capital_has_better_use",
                "assessment_as_of": assessment["assessed_at"],
            }
        ],
    )
    _create_baseline_strategy(
        sandbox_repository,
        sandbox_settings,
        security_id="sec_00",
        allocation_plan_id=plan_id,
        quantity=Decimal("10"),
    )
    signal_id, _ = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="reduce",
        rationale="Reduce exactly to the deterministic target.",
        market_data_as_of=NOW,
        run_id="allocation-reduce",
        now=NOW,
    )
    reference = ReferencePrice(
        security_id="sec_00",
        provider_contract_id="",
        price=Decimal("100"),
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=NOW,
    )
    risk_state = RiskState(
        equity_base=Decimal("100000"),
        cash_base=Decimal("97500"),
        gross_exposure_base=Decimal("2500"),
        short_exposure_base=Decimal("0"),
        options_risk_base=Decimal("0"),
        daily_turnover_base=Decimal("0"),
        active_strategy_count=1,
        positions=(
            RiskPosition(
                security_id="sec_00",
                provider_contract_id="",
                side="long",
                instrument_type="equity",
                quantity=Decimal("25"),
                contract_multiplier=Decimal("1"),
                currency="EUR",
                option_type="",
                expiry=None,
                strike=None,
            ),
        ),
    )
    reducing_leg = OrderLegSpec(
        leg_id="leg_1",
        action="sell",
        side="long",
        instrument_type="equity",
        security_id="sec_00",
        provider_contract_id="",
        option_type="",
        expiry=None,
        strike=None,
        quantity=Decimal("10"),
        contract_multiplier=Decimal("1"),
        limit_price=None,
        currency="EUR",
    )

    order_id, created, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(reducing_leg,),
        references=(reference,),
        risk_state=risk_state,
        run_id="allocation-reduce",
        now=NOW,
    )

    assert created and order_id
    assert read_table(sandbox_repository, "executions") == []


def test_hard_blocked_baseline_target_can_only_close_existing_exposure(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _seed_candidates(sandbox_repository, sandbox_settings, 1)
    assessment_rows = read_table(sandbox_repository, "security_assessments")
    assessment_rows[0]["eligibility"] = "ineligible"
    assessment_rows[0]["hard_blockers"] = "thesis_invalidated"
    write_table(sandbox_repository, "security_assessments", assessment_rows)
    strategy_id = baseline_strategy_id("sec_00")
    plan_id = "allocation_plan_blocked_close"
    write_table(
        sandbox_repository,
        "allocation_targets",
        [
            {
                "allocation_plan_id": plan_id,
                "run_id": "allocation-blocked-close",
                "as_of": "2026-07-24T22:00:00Z",
                "security_id": "sec_00",
                "strategy_id": strategy_id,
                "sleeve": "baseline",
                "rank": "",
                "effective_score": "0",
                "candidate_edge": "0",
                "current_weight_pct": "2.5",
                "pending_weight_pct": "0",
                "target_weight_pct": "0",
                "target_value_base": "0",
                "delta_value_base": "-2500",
                "disposition": "close",
                "reason": "hard_blocker:thesis_invalidated",
                "assessment_as_of": assessment_rows[0]["assessed_at"],
            }
        ],
    )
    strategy_id = _create_baseline_strategy(
        sandbox_repository,
        sandbox_settings,
        security_id="sec_00",
        allocation_plan_id=plan_id,
        quantity=Decimal("25"),
    )
    signal_id, created = create_signal(
        sandbox_repository,
        sandbox_settings,
        strategy_id=strategy_id,
        signal_type="close",
        rationale="Close exposure after deterministic thesis invalidation.",
        market_data_as_of=NOW,
        run_id="allocation-blocked-close",
        now=NOW,
    )
    assert created
    reference = ReferencePrice(
        security_id="sec_00",
        provider_contract_id="",
        price=Decimal("100"),
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=NOW,
    )
    risk_state = RiskState(
        equity_base=Decimal("100000"),
        cash_base=Decimal("97500"),
        gross_exposure_base=Decimal("2500"),
        short_exposure_base=Decimal("0"),
        options_risk_base=Decimal("0"),
        daily_turnover_base=Decimal("0"),
        active_strategy_count=1,
        positions=(
            RiskPosition(
                security_id="sec_00",
                provider_contract_id="",
                side="long",
                instrument_type="equity",
                quantity=Decimal("25"),
                contract_multiplier=Decimal("1"),
                currency="EUR",
                option_type="",
                expiry=None,
                strike=None,
            ),
        ),
    )
    closing_leg = OrderLegSpec(
        leg_id="leg_1",
        action="sell",
        side="long",
        instrument_type="equity",
        security_id="sec_00",
        provider_contract_id="",
        option_type="",
        expiry=None,
        strike=None,
        quantity=Decimal("25"),
        contract_multiplier=Decimal("1"),
        limit_price=None,
        currency="EUR",
    )

    order_id, order_created, _ = create_paper_order(
        sandbox_repository,
        sandbox_settings,
        signal_id=signal_id,
        strategy_id=strategy_id,
        legs=(closing_leg,),
        references=(reference,),
        risk_state=risk_state,
        run_id="allocation-blocked-close",
        now=NOW,
    )

    assert order_created and order_id
    assert read_table(sandbox_repository, "executions") == []

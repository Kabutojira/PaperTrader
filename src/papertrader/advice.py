"""Deterministic investor-facing projection over canonical PaperTrader state.

The publication snapshot is a read-only view.  Nothing in this module is an input to
research, allocation, signal, order, fill, accounting, or reconciliation code.
"""

from __future__ import annotations

import configparser
import csv
import json
import re
import subprocess
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path, PurePosixPath
from typing import Any, cast

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from papertrader.allocation import (
    CONFIDENCE_RANK,
    AllocationError,
    assessment_payoff_reasons,
    latest_allocation_target,
    score_assessment,
)
from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.market_data import MarketDataError, latest_fx_rate, latest_fx_rate_record
from papertrader.orders import leg_from_row
from papertrader.portfolio import reconcile_portfolio, replay_accounting
from papertrader.tables import contract_by_name, read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    canonical_json,
    content_hash,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    required_decimal,
    stable_id,
)

SNAPSHOT_VERSION = 4
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
MONEY_QUANTUM = Decimal("0.01")
PERCENT_QUANTUM = Decimal("0.000001")
WEIGHT_TOLERANCE = Decimal("0.00001")
NON_TERMINAL_ORDERS = frozenset({"pending", "partially_filled"})
ACTIVE_SIGNAL_STATUSES = frozenset({"ready", "ordered"})
ACTIVE_STRATEGY_STATUSES = frozenset({"ready", "active"})
CURRENT_SOURCE_STATUSES = frozenset({"available", "ok", "current"})
RESEARCH_ALERT_LABEL = "Research alert — not a trade signal"

AUTHORITATIVE_TABLES = (
    "allocation_targets",
    "cash_ledger",
    "executions",
    "indicators",
    "issues",
    "market_latest",
    "operations_history",
    "operations_todo",
    "order_legs",
    "orders",
    "performance_daily",
    "performance_epochs",
    "portfolio",
    "relationships",
    "runs",
    "securities",
    "security_assessments",
    "signals",
    "source_registry",
    "strategies",
    "strategy_legs",
)

MODEL_PORTFOLIO_COLUMNS = (
    "snapshot_id",
    "as_of",
    "holding_type",
    "security_id",
    "ticker",
    "company_name",
    "instrument_type",
    "sleeve",
    "current_weight_pct",
    "target_weight_pct",
    "current_value_base",
    "target_value_base",
    "delta_value_base",
    "current_quantity",
    "target_quantity",
    "mark",
    "mark_currency",
    "mark_base",
    "fx_rate_to_base",
    "fx_as_of",
    "market_data_as_of",
    "action",
    "action_status",
    "strategy_id",
    "signal_id",
    "order_id",
    "confidence",
    "effective_score",
    "downside_pct",
    "base_upside_pct",
    "bear_fair_value",
    "bear_return_pct",
    "bear_probability_pct",
    "base_fair_value",
    "base_return_pct",
    "base_probability_pct",
    "bull_fair_value",
    "bull_return_pct",
    "bull_probability_pct",
    "expected_return_pct",
    "confidence_adjusted_expected_return_pct",
    "buy_below_price",
    "canonical_rating",
    "portfolio_action",
    "evidence_state",
    "rating_change_conditions",
    "valuation_horizon_months",
    "thesis_summary",
    "entry_rule",
    "exit_rule",
    "invalidation",
    "review_at",
    "security_research_page",
    "strategy_research_page",
    "research_page",
    "reason_codes",
)

ACTIONABLE_SIGNAL_COLUMNS = (
    "snapshot_id",
    "as_of",
    "signal_id",
    "strategy_id",
    "order_id",
    "security_id",
    "ticker",
    "company_name",
    "action",
    "action_status",
    "copy_ready",
    "quantity",
    "order_type",
    "limit_price",
    "currency",
    "created_at",
    "expires_at",
    "market_data_as_of",
    "current_weight_pct",
    "target_weight_pct",
    "strategy_name",
    "entry_rule",
    "exit_rule",
    "invalidation",
    "rationale",
    "security_research_page",
    "strategy_research_page",
    "research_page",
    "reason_codes",
)

RESEARCH_BENCHMARK_COLUMNS = (
    "snapshot_id",
    "as_of",
    "policy_version",
    "comparison_only",
    "copy_ready",
    "security_id",
    "ticker",
    "company_name",
    "rating",
    "weight_pct",
    "reference_price",
    "currency",
    "research_page",
)

REASON_LABELS = {
    "above_cash_hurdle": "The evidence-backed score clears the configured cash hurdle.",
    "assessment_ineligible": "The current assessment marks the security ineligible.",
    "assessment_missing": "No current comparable assessment is available.",
    "assessment_stale": "The comparable assessment is stale or expired.",
    "allocation_plan_stale": "No current allocation plan supports this candidate.",
    "base_upside_not_positive": "The assessed base case has no positive upside.",
    "base_upside_below_minimum": "Base-case upside is below the configured entry minimum.",
    "baseline_sleeve_cap": "The baseline sleeve exposure cap prevents additional allocation.",
    "candidate_inputs": "Candidate inputs are incomplete.",
    "candidate_or_rounding_constraints": (
        "Candidate capacity or whole-unit rounding prevents deployment."
    ),
    "concentration_cap": "A portfolio, sector, or theme concentration cap applies.",
    "confidence_below_minimum": "Assessment confidence is below the configured minimum.",
    "conviction_exposure_present": (
        "The security is already represented in the conviction sleeve."
    ),
    "conviction_pending_exposure": (
        "A validated pending conviction-sleeve order already represents the security."
    ),
    "currency_not_allowed": "The instrument currency is outside the configured mandate.",
    "deployment_budget_exhausted": "The per-run deployment budget is exhausted.",
    "exchange_not_allowed": "The venue is outside the configured mandate.",
    "fx_unavailable": "A fresh required foreign-exchange rate is unavailable.",
    "insufficient_diversification": "The eligible set is not sufficiently diversified.",
    "insufficient_eligible_candidates": "Too few eligible candidates clear all allocation gates.",
    "instrument_not_allowed": "The instrument is outside the configured mandate.",
    "instrument_unsupported": "The allocator does not support this instrument.",
    "maintenance_mode": "Allocation is not active.",
    "market_data_missing": "A required current market price is unavailable.",
    "market_data_identity_mismatch": (
        "The market reference does not match the security's canonical currency identity."
    ),
    "market_data_not_ok": "The latest market retrieval did not succeed.",
    "market_data_stale": "The required market reference is stale.",
    "minimum_cash_reserve_or_pending_cash": (
        "The cash reserve or committed pending cash limits deployment."
    ),
    "minimum_trade_threshold": "The proposed change is below the minimum trade threshold.",
    "no_actionable_signals": "No strategy has produced a current actionable trade signal.",
    "pending_exposure_unpriced": "Pending exposure cannot be projected from fresh references.",
    "pending_order_state_unsafe": "A pending order is expired or has inconsistent state.",
    "portfolio_all_cash": "The reconciled model portfolio is entirely cash.",
    "portfolio_issue_open": "An open operational issue blocks safe portfolio publication.",
    "relationship_missing_or_stale": (
        "A current accepted idea-to-security relationship is unavailable."
    ),
    "relationship_rejected": (
        "The current relationship review rejected the idea-to-security mechanism."
    ),
    "score_below_cash_hurdle": "The effective score does not beat the configured cash hurdle.",
    "security_status_not_orderable": "The security is not currently orderable.",
    "target_unchanged": "The target does not require a trade.",
    "upside_downside_ratio_below_minimum": (
        "Modeled base upside does not match the configured downside-risk ratio."
    ),
    "expected_return_below_minimum": "Confidence-adjusted expected return is below threshold.",
    "base_return_below_minimum": "Base-case return is below threshold.",
    "bear_base_payoff_below_minimum": "Bear/base payoff is below threshold.",
    "expected_bear_payoff_below_minimum": "Expected/bear payoff is below threshold.",
    "margin_of_safety_below_minimum": "Margin of safety is below threshold.",
    "research_incomplete": "Scenario-complete research remains incomplete.",
    "valuation_unsupported": "A supportable scenario valuation is unavailable.",
    "validated_open_actions": "Validated opening actions are pending.",
    "validated_reduce_actions": "Validated actions reduce existing exposure.",
    "validated_rebalance_actions": (
        "Validated opening and reduction actions rebalance the portfolio."
    ),
}

HARD_BLOCKER_LABELS = {
    "accounting_uncertain": "Accounting evidence is uncertain.",
    "currency_unsupported": "The assessment currency is unsupported.",
    "exchange_unsupported": "The assessment venue is unsupported.",
    "fx_unavailable": "Required foreign-exchange data is unavailable.",
    "identity_uncertain": "The instrument identity is uncertain.",
    "instrument_unsupported": "The assessment instrument is unsupported.",
    "liquidity_insufficient": "Liquidity is insufficient.",
    "market_data_stale": "Market data is stale.",
    "research_stale": "The underlying research is stale.",
    "solvency_risk": "Solvency risk blocks eligibility.",
    "thesis_invalidated": "The investment thesis has been invalidated.",
    "valuation_unsupported": "A supportable valuation is unavailable.",
}


class AdviceError(RuntimeError):
    """Raised when authoritative state cannot produce a safe public projection."""


@dataclass(frozen=True, slots=True)
class ModelPortfolioRow:
    snapshot_id: str
    as_of: str
    holding_type: str
    security_id: str
    ticker: str
    company_name: str
    instrument_type: str
    sleeve: str
    current_weight_pct: str
    target_weight_pct: str
    current_value_base: str
    target_value_base: str
    delta_value_base: str
    current_quantity: str
    target_quantity: str
    mark: str
    mark_currency: str
    mark_base: str
    fx_rate_to_base: str
    fx_as_of: str
    market_data_as_of: str
    action: str
    action_status: str
    strategy_id: str
    signal_id: str
    order_id: str
    confidence: str
    effective_score: str
    downside_pct: str
    base_upside_pct: str
    bear_fair_value: str
    bear_return_pct: str
    bear_probability_pct: str
    base_fair_value: str
    base_return_pct: str
    base_probability_pct: str
    bull_fair_value: str
    bull_return_pct: str
    bull_probability_pct: str
    expected_return_pct: str
    confidence_adjusted_expected_return_pct: str
    buy_below_price: str
    canonical_rating: str
    portfolio_action: str
    evidence_state: str
    rating_change_conditions: str
    valuation_horizon_months: str
    thesis_summary: str
    entry_rule: str
    exit_rule: str
    invalidation: str
    review_at: str
    security_research_page: str
    strategy_research_page: str
    research_page: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PortfolioSummary:
    portfolio_kind: str
    equity_base: str
    cash_base: str
    cash_weight_pct: str
    invested_value_base: str
    invested_weight_pct: str
    gross_exposure_base: str
    net_exposure_base: str
    realized_pnl_base: str
    unrealized_pnl_base: str
    rows: tuple[ModelPortfolioRow, ...]


@dataclass(frozen=True, slots=True)
class ActionableSignalView:
    signal_id: str
    strategy_id: str
    order_id: str
    security_id: str
    ticker: str
    company_name: str
    action: str
    action_status: str
    copy_ready: bool
    quantity: str
    order_type: str
    limit_price: str
    currency: str
    created_at: str
    expires_at: str
    market_data_as_of: str
    current_weight_pct: str
    target_weight_pct: str
    strategy_name: str
    entry_rule: str
    exit_rule: str
    invalidation: str
    rationale: str
    security_research_page: str
    strategy_research_page: str
    research_page: str
    reason_codes: tuple[str, ...]
    legs: tuple[Mapping[str, str], ...]


@dataclass(frozen=True, slots=True)
class CandidateView:
    security_id: str
    ticker: str
    company_name: str
    research_page: str
    classification: str
    rank: str
    effective_score: str
    candidate_edge: str
    target_weight_pct: str
    confidence: str
    downside_pct: str
    base_upside_pct: str
    review_at: str
    reason_codes: tuple[str, ...]
    reason_labels: tuple[str, ...]
    bear_fair_value: str
    bear_return_pct: str
    bear_probability_pct: str
    base_fair_value: str
    base_return_pct: str
    base_probability_pct: str
    bull_fair_value: str
    bull_return_pct: str
    bull_probability_pct: str
    expected_return_pct: str
    confidence_adjusted_expected_return_pct: str
    buy_below_price: str
    canonical_rating: str
    portfolio_action: str
    evidence_state: str
    eligibility_frontier: Mapping[str, str]
    rating_change_conditions: str
    research_conclusion: str


@dataclass(frozen=True, slots=True)
class ResearchBenchmarkRow:
    security_id: str
    ticker: str
    company_name: str
    rating: str
    weight_pct: str
    reference_price: str
    currency: str
    research_page: str


@dataclass(frozen=True, slots=True)
class ResearchBenchmark:
    policy_version: str
    comparison_only: bool
    copy_ready: bool
    rows: tuple[ResearchBenchmarkRow, ...]


@dataclass(frozen=True, slots=True)
class ResearchAlertView:
    alert_id: str
    security_id: str
    ticker: str
    company_name: str
    alert_type: str
    observed_at: str
    market_data_date: str
    research_status: str
    research_conclusion: str
    research_page: str
    visible_label: str = RESEARCH_ALERT_LABEL


@dataclass(frozen=True, slots=True)
class CoverageSummary:
    allocation_candidate_count: int
    current_assessment_count: int
    fresh_evidence_assessment_count: int
    reviewed_relationship_count: int
    accepted_relationship_count: int
    required_relationship_review_count: int
    ready_or_active_strategy_count: int
    active_signal_count: int
    pending_order_count: int
    market_data_success_count: int
    market_data_failure_count: int
    research_backlog_count: int
    blocking_issue_count: int
    non_blocking_issue_count: int
    last_successful_daily_run: str


@dataclass(frozen=True, slots=True)
class PerformanceSummary:
    performance_epoch_id: str
    epoch_started_at: str
    epoch_opening_equity_base: str
    prior_epoch_count: int
    daily_return_pct: str
    cumulative_return_pct: str
    running_drawdown_pct: str
    realized_pnl_base: str
    unrealized_pnl_base: str
    conviction_exposure_base: str
    baseline_exposure_base: str
    largest_position_weight_pct: str
    largest_sector_weight_pct: str
    history: tuple[Mapping[str, str], ...]


@dataclass(frozen=True, slots=True)
class SystemImpact:
    issue_id: str
    severity: str
    impact: str
    title: str
    summary: str
    security_id: str
    ticker: str
    company_name: str


@dataclass(frozen=True, slots=True)
class DecisionSnapshot:
    version: int
    snapshot_id: str
    run_id: str
    as_of: str
    report_date: str
    investment_data_status: str
    operations_status: str
    stance: str
    stance_reason_codes: tuple[str, ...]
    evidence_state: str
    base_currency: str
    current_portfolio: PortfolioSummary
    target_portfolio: PortfolioSummary
    actionable_signals: tuple[ActionableSignalView, ...]
    candidate_pipeline: tuple[CandidateView, ...]
    research_benchmark: ResearchBenchmark
    research_alerts: tuple[ResearchAlertView, ...]
    coverage: CoverageSummary
    performance: PerformanceSummary
    system_impacts: tuple[SystemImpact, ...]
    source_state_hashes: Mapping[str, str]

    @property
    def data_status(self) -> str:
        """Compatibility accessor for Python callers during the v1-to-v2 transition."""

        return self.investment_data_status


@dataclass(slots=True)
class _Holding:
    security_id: str
    provider_contract_id: str
    side: str
    instrument_type: str
    sleeve: str
    currency: str
    multiplier: Decimal
    current_quantity: Decimal
    target_quantity: Decimal
    mark: Decimal
    fx_rate: Decimal
    fx_as_of: datetime
    market_data_as_of: datetime
    strategy_ids: set[str]
    signal_ids: set[str]
    order_ids: set[str]
    reason_codes: set[str]
    pending_delta_value: Decimal = Decimal("0")

    @property
    def current_value(self) -> Decimal:
        direction = Decimal("-1") if self.side == "short" else Decimal("1")
        return self.current_quantity * self.multiplier * self.mark * self.fx_rate * direction

    @property
    def target_value(self) -> Decimal:
        direction = Decimal("-1") if self.side == "short" else Decimal("1")
        return self.target_quantity * self.multiplier * self.mark * self.fx_rate * direction


def reason_label(code: str) -> str:
    """Translate one canonical reason code or fail instead of leaking machine text."""

    if code.startswith("hard_blocker:"):
        blockers = tuple(part for part in code.split(":", maxsplit=1)[1].split(",") if part)
        if not blockers or any(blocker not in HARD_BLOCKER_LABELS for blocker in blockers):
            raise AdviceError(f"unknown hard-blocker reason code: {code}")
        return " ".join(HARD_BLOCKER_LABELS[blocker] for blocker in blockers)
    try:
        return REASON_LABELS[code]
    except KeyError as exc:
        raise AdviceError(f"unknown decision reason code: {code}") from exc


def _percent(value: Decimal, total: Decimal) -> Decimal:
    if total == 0:
        return Decimal("0")
    return (value / total * Decimal("100")).quantize(PERCENT_QUANTUM, rounding=ROUND_HALF_EVEN)


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_EVEN)


def _delivery_issue_open_at(issue: Mapping[str, str], *, as_of: datetime) -> bool:
    first_seen = parse_timestamp(issue["first_seen_at"])
    resolved = parse_timestamp(issue["resolved_at"], allow_empty=True)
    return first_seen is not None and first_seen <= as_of and (resolved is None or resolved > as_of)


def _canonical_rows(
    repository_root: Path,
    name: str,
    *,
    as_of: datetime | None = None,
) -> list[dict[str, str]]:
    rows = read_table(repository_root, name)
    if name in {"operations_todo", "operations_history"}:
        # The podcast is a generated delivery view. Its queue lifecycle must never feed back
        # into an already-published investment decision or invalidate that immutable snapshot.
        rows = [row for row in rows if row["operation_type"] != "daily_podcast"]
    if name == "issues" and as_of is not None:
        projected: list[dict[str, str]] = []
        for row in rows:
            if row["owner"] != "delivery":
                projected.append(row)
            elif _delivery_issue_open_at(row, as_of=as_of):
                projected.append(
                    {
                        "issue_id": row["issue_id"],
                        "status": "open",
                        "severity": row["severity"],
                        "title": row["title"],
                        "owner": row["owner"],
                        "first_seen_at": row["first_seen_at"],
                        "related_run_id": row["related_run_id"],
                        "related_operation_id": row["related_operation_id"],
                    }
                )
        rows = projected
    return sorted(rows, key=canonical_json)


def _dynamic_csv_hashes(directory: Path) -> Mapping[str, str]:
    values: dict[str, str] = {}
    if not directory.exists():
        return values
    for path in sorted(directory.glob("*.csv")):
        if path.is_symlink() or not path.is_file():
            raise AdviceError(f"publication input is not a regular CSV: {path}")
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise AdviceError(f"publication input lacks a CSV header: {path}")
            rows = sorted((dict(row) for row in reader), key=canonical_json)
        values[path.stem.lower()] = content_hash(rows)
    return values


def _decision_csv_contract_bytes(path: Path) -> bytes:
    """Exclude presentation-only technical-series metadata from decision identity."""

    raw = path.read_text(encoding="utf-8")
    try:
        document = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise AdviceError("CSV contracts are not valid YAML") from exc
    dynamic = document.get("dynamic_contracts") if isinstance(document, dict) else None
    if not isinstance(dynamic, dict) or "technical_series" not in dynamic:
        return raw.encode("utf-8")
    scrubbed, count = re.subn(
        r"^  technical_series:\n.*?(?=^contracts:\n)",
        "",
        raw,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    if count != 1:
        raise AdviceError("technical-series CSV contract is not in canonical location")
    return scrubbed.encode("utf-8")


def _source_hashes(repository_root: Path, *, as_of: datetime) -> Mapping[str, str]:
    hashes = {
        name: content_hash(_canonical_rows(repository_root, name, as_of=as_of))
        for name in AUTHORITATIVE_TABLES
    }
    for name, relative in (
        ("configuration", "config.ini"),
        ("csv_contracts", "schemas/csv_contracts.yaml"),
        ("decision_schema", "schemas/decision_snapshot.schema.json"),
    ):
        path = repository_root / relative
        if path.is_symlink() or not path.is_file():
            raise AdviceError(f"decision input must be a regular file: {relative}")
        content = (
            _decision_csv_contract_bytes(path) if name == "csv_contracts" else path.read_bytes()
        )
        hashes[name] = content_hash(content)
    inbox: list[tuple[str, str]] = []
    for path in sorted((repository_root / "data" / "wiki" / "inbox").glob("*.md")):
        if path.is_symlink() or not path.is_file():
            raise AdviceError("research-alert packet must be a regular Markdown file")
        inbox.append((path.name, content_hash(path.read_bytes())))
    hashes["wiki_inbox"] = content_hash(inbox)
    payloads: list[tuple[str, str]] = []
    payload_root = repository_root / "data" / "operations" / "payloads"
    if payload_root.is_symlink() or not payload_root.is_dir():
        raise AdviceError("operation payload input must be a regular directory")
    for path in sorted(payload_root.rglob("*.json")):
        if path.is_symlink() or not path.is_file():
            raise AdviceError("operation payload input must be a regular JSON file")
        raw = path.read_bytes()
        try:
            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AdviceError(f"operation payload is not valid JSON: {path.name}") from exc
        if isinstance(payload, dict) and payload.get("operation_type") == "daily_podcast":
            continue
        payloads.append((path.relative_to(payload_root).as_posix(), content_hash(raw)))
    hashes["operation_payloads"] = content_hash(payloads)
    hashes.update(
        {
            f"fx_{key}": value
            for key, value in _dynamic_csv_hashes(
                repository_root / "data" / "market" / "fx"
            ).items()
        }
    )
    if not all(HASH.fullmatch(value) for value in hashes.values()):
        raise AdviceError("source-state hashing produced a non-canonical digest")
    return dict(sorted(hashes.items()))


def _configuration_only_runtime_changed(
    repository_root: Path,
    *,
    run_id: str,
    expected_hash: str,
) -> bool:
    """Accept profile/delivery config migration without weakening investment freshness."""

    manifest_path = repository_root / "data" / "runs" / run_id / "daily_run.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    source_sha = manifest.get("source_sha") if isinstance(manifest, dict) else None
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        return False
    historical = subprocess.run(
        ["git", "show", f"{source_sha}:config.ini"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if historical.returncode != 0 or content_hash(historical.stdout) != expected_hash:
        return False
    try:
        old = configparser.ConfigParser(interpolation=None)
        old.read_string(historical.stdout.decode("utf-8"))
        current = configparser.ConfigParser(interpolation=None)
        current.read(repository_root / "config.ini", encoding="utf-8")
    except (UnicodeError, configparser.Error, OSError):
        return False
    investment_sections = (
        "safety",
        "market_data",
        "calendars",
        "indicators",
        "portfolio",
        "risk",
        "allocation",
        "ratings",
        "orders",
    )
    return all(
        old.has_section(section)
        and current.has_section(section)
        and dict(old.items(section)) == dict(current.items(section))
        for section in investment_sections
    )


def _legacy_publication_contracts_changed(
    repository_root: Path,
    *,
    snapshot: DecisionSnapshot,
    differing: set[str],
) -> bool:
    """Accept only the v4 schema/header migration for an immutable legacy publication."""

    if snapshot.version >= SNAPSHOT_VERSION or differing != {"csv_contracts", "decision_schema"}:
        return False
    manifest_path = repository_root / "data" / "runs" / snapshot.run_id / "daily_run.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    source_sha = manifest.get("source_sha") if isinstance(manifest, dict) else None
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        return False
    for key, relative in (
        ("csv_contracts", "schemas/csv_contracts.yaml"),
        ("decision_schema", "schemas/decision_snapshot.schema.json"),
    ):
        historical = subprocess.run(
            ["git", "show", f"{source_sha}:{relative}"],
            cwd=repository_root,
            check=False,
            capture_output=True,
        )
        expected_hash = snapshot.source_state_hashes.get(key)
        if historical.returncode != 0 or content_hash(historical.stdout) != expected_hash:
            return False
    return True


def _post_publication_delivery_issue_reopened(
    repository_root: Path,
    *,
    as_of: datetime,
    expected_hashes: Mapping[str, str],
    differing: set[str],
) -> bool:
    """Recognize a delivery-only issue episode reopened after publication.

    Delivery issues use stable latest-only rows. Reopening a resolved issue clears its
    prior ``resolved_at``, so the current row alone can make that issue appear open at
    an earlier snapshot cutoff. Accept the transition only when removing a bounded
    subset of delivery rows refreshed after the cutoff reconstructs the stored issue
    hash exactly. Every non-delivery or otherwise substantive change still fails closed.
    """

    if differing != {"issues"}:
        return False
    rows = _canonical_rows(repository_root, "issues", as_of=as_of)
    projected_ids = {row["issue_id"] for row in rows}
    candidates: list[str] = []
    for row in read_table(repository_root, "issues"):
        if (
            row["issue_id"] not in projected_ids
            or row["owner"] != "delivery"
            or row["status"] != "open"
        ):
            continue
        last_seen = parse_timestamp(row["last_seen_at"])
        if last_seen is not None and last_seen > as_of:
            candidates.append(row["issue_id"])
    # The delivery boundary currently owns only a few stable issue identities. Keep
    # reconstruction explicitly bounded so malformed input cannot cause exponential work.
    if not candidates or len(candidates) > 8:
        return False
    for mask in range(1, 1 << len(candidates)):
        removed = {issue_id for index, issue_id in enumerate(candidates) if mask & (1 << index)}
        reconstructed = [row for row in rows if row["issue_id"] not in removed]
        if content_hash(reconstructed) == expected_hashes.get("issues"):
            return True
    return False


def _post_publication_podcast_only_changed(
    repository_root: Path,
    *,
    run_id: str,
    as_of: datetime,
    expected_hashes: Mapping[str, str],
    differing: set[str],
) -> bool:
    """Recognize legacy podcast bookkeeping that cannot affect a decision snapshot.

    Older queue triage rewrote every active row's ``updated_at`` while preparing the
    post-publication podcast, and older controller code classified a contained podcast
    failure as an investment-system issue. Reconstructing the pre-podcast rows must match
    the stored hashes exactly; any substantive or unrelated change still fails closed.
    """

    if not differing or not differing <= {"issues", "operations_todo"}:
        return False
    podcast_operation_ids: set[str] = set()
    for row in read_table(repository_root, "operations_history"):
        if row["operation_type"] != "daily_podcast" or row["entity_id"] != run_id:
            continue
        completed_at = parse_timestamp(row["completed_at"], allow_empty=True)
        if completed_at is not None and completed_at > as_of:
            podcast_operation_ids.add(row["operation_id"])
    if not podcast_operation_ids:
        return False

    if "issues" in differing:
        rows = _canonical_rows(repository_root, "issues", as_of=as_of)
        reconstructed: list[dict[str, str]] = []
        removed = False
        for row in rows:
            first_seen = parse_timestamp(row["first_seen_at"])
            if (
                row["related_operation_id"] in podcast_operation_ids
                and row["related_run_id"] == run_id
                and row["owner"] == "controller"
                and row["title"]
                == f"Hermes operation validation failed: {row['related_operation_id']}"
                and first_seen is not None
                and first_seen > as_of
            ):
                removed = True
                continue
            reconstructed.append(row)
        if not removed or content_hash(
            sorted(reconstructed, key=canonical_json)
        ) != expected_hashes.get("issues"):
            return False

    if "operations_todo" in differing:
        rows = _canonical_rows(repository_root, "operations_todo", as_of=as_of)
        reconstructed = []
        rewound = False
        for row in rows:
            updated_at = parse_timestamp(row["updated_at"])
            if updated_at is not None and updated_at > as_of:
                row = {**row, "updated_at": format_timestamp(as_of)}
                rewound = True
            reconstructed.append(row)
        if not rewound or content_hash(
            sorted(reconstructed, key=canonical_json)
        ) != expected_hashes.get("operations_todo"):
            return False

    return True


def _snapshot_as_of(
    repository_root: Path,
    run_id: str,
    supplied: datetime | None,
) -> datetime:
    matches = [row for row in read_table(repository_root, "runs") if row["run_id"] == run_id]
    if len(matches) > 1:
        raise AdviceError(f"duplicate selected daily run: {run_id}")
    if matches:
        completed = parse_timestamp(matches[0]["completed_at"])
        if completed is None:
            raise AdviceError("selected daily run is not complete")
        if supplied is not None and ensure_utc(supplied).replace(microsecond=0) != completed:
            raise AdviceError("supplied snapshot time differs from the completed run")
        return completed
    if supplied is None:
        raise AdviceError(f"selected daily run is unavailable: {run_id}")
    return ensure_utc(supplied).replace(microsecond=0)


def _current_performance(
    repository_root: Path, settings: Settings, *, as_of: datetime
) -> Mapping[str, str] | None:
    rows: list[Mapping[str, str]] = []
    for row in read_table(repository_root, "performance_daily"):
        generated = parse_timestamp(row["generated_at"])
        if generated is not None and generated <= as_of and row["date"] <= as_of.date().isoformat():
            rows.append(row)
    if not rows:
        return None
    latest = max(rows, key=lambda row: (row["date"], row["generated_at"], row["run_id"]))
    if latest["base_currency"] != settings.portfolio.base_currency:
        raise AdviceError("latest performance snapshot uses the wrong base currency")
    return latest


def _current_assessment(
    assessment: Mapping[str, str] | None, settings: Settings, *, as_of: datetime
) -> bool:
    if assessment is None:
        return False
    assessed = parse_timestamp(assessment["assessed_at"])
    expires = parse_timestamp(assessment["expires_at"])
    assert assessed is not None and expires is not None
    return assessed <= as_of < expires and as_of - assessed <= timedelta(
        days=settings.allocation.maximum_assessment_age_days
    )


def _current_relationship(row: Mapping[str, str], *, as_of: datetime) -> bool:
    reviewed = parse_timestamp(row["last_reviewed_at"])
    next_review = parse_timestamp(row["next_review_at"])
    return (
        row["status"] == "accepted"
        and reviewed is not None
        and next_review is not None
        and reviewed <= as_of < next_review
    )


def _current_relationship_review(row: Mapping[str, str], *, as_of: datetime) -> bool:
    """Return whether an accepted or rejected relationship has a current review."""

    reviewed = parse_timestamp(row["last_reviewed_at"])
    next_review = parse_timestamp(row["next_review_at"])
    return (
        row["status"] in {"accepted", "rejected"}
        and reviewed is not None
        and next_review is not None
        and reviewed <= as_of < next_review
    )


def _fresh_evidence(
    assessment: Mapping[str, str],
    sources: Mapping[str, Mapping[str, str]],
    settings: Settings,
) -> bool:
    assessed = parse_timestamp(assessment["assessed_at"])
    assert assessed is not None
    evidence = tuple(part for part in assessment["evidence_refs"].split("|") if part)
    if not evidence:
        return False
    for source_id in evidence:
        source = sources.get(source_id)
        checked = parse_timestamp(source["last_checked_at"]) if source else None
        if (
            source is None
            or checked is None
            or source["status"] not in CURRENT_SOURCE_STATUSES
            or checked > assessed
            or assessed - checked > timedelta(days=settings.allocation.maximum_assessment_age_days)
        ):
            return False
    return True


def _impact_category(issue: Mapping[str, str]) -> str:
    text = f"{issue['title']} {issue['description']}".lower()
    if any(token in text for token in ("telegram", "pages", "publication", "deploy")):
        return "publication_only"
    if any(token in text for token in ("reconcil", "accounting", "portfolio", "ledger")):
        return "blocks_portfolio"
    if any(token in text for token in ("order", "signal", "strategy", "fill", "execution")):
        return "blocks_action"
    if any(
        token in text
        for token in (
            "market",
            "price",
            "classifier",
            "assessment",
            "relationship",
            "research",
            "security_",
        )
    ):
        return "affects_candidate"
    return "operational_only"


def _system_impacts(
    repository_root: Path,
    securities: Mapping[str, Mapping[str, str]],
    *,
    as_of: datetime,
) -> tuple[SystemImpact, ...]:
    impacts: list[SystemImpact] = []
    for issue in read_table(repository_root, "issues"):
        delivery_issue = issue["owner"] == "delivery"
        if delivery_issue:
            if not _delivery_issue_open_at(issue, as_of=as_of):
                continue
        elif issue["status"] != "open":
            continue
        combined = issue["title"] if delivery_issue else f"{issue['title']} {issue['description']}"
        security_id = next((key for key in sorted(securities) if key in combined), "")
        security = securities.get(security_id, {})
        impacts.append(
            SystemImpact(
                issue_id=issue["issue_id"],
                severity=issue["severity"],
                impact=_impact_category(issue),
                title=" ".join(issue["title"].split()),
                summary=(
                    "Committed Telegram delivery is awaiting a bounded retry."
                    if delivery_issue
                    else " ".join(issue["description"].split())[:500]
                ),
                security_id=security_id,
                ticker=security.get("ticker", ""),
                company_name=security.get("company_name", ""),
            )
        )
    return tuple(sorted(impacts, key=lambda value: (value.impact, value.severity, value.issue_id)))


def _position_multiplier(
    position: Mapping[str, str],
    _strategies: Mapping[str, Mapping[str, str]],
    strategy_legs: Sequence[Mapping[str, str]],
    order_legs: Sequence[Mapping[str, str]],
) -> Decimal:
    if position["instrument_type"] == "equity":
        return Decimal("1")
    strategy_ids = {part for part in position["strategy_ids"].split("|") if part}
    values = {
        required_decimal(row["contract_multiplier"], label="position multiplier")
        for row in strategy_legs
        if row["strategy_id"] in strategy_ids
        and row["security_id"] == position["security_id"]
        and row["provider_contract_id"] == position["provider_contract_id"]
    }
    if not values:
        values = {
            required_decimal(row["contract_multiplier"], label="position multiplier")
            for row in order_legs
            if row["security_id"] == position["security_id"]
            and row["provider_contract_id"] == position["provider_contract_id"]
        }
    if len(values) != 1:
        raise AdviceError(f"cannot resolve option multiplier for {position['position_id']}")
    return next(iter(values))


def _position_sleeve(
    position: Mapping[str, str], strategies: Mapping[str, Mapping[str, str]]
) -> str:
    strategy_ids = tuple(part for part in position["strategy_ids"].split("|") if part)
    sleeves = {
        strategies[strategy_id]["sleeve"]
        for strategy_id in strategy_ids
        if strategy_id in strategies
    }
    if strategy_ids and len(sleeves) != 1:
        raise AdviceError(f"position has unresolved allocation sleeve: {position['position_id']}")
    return next(iter(sleeves)) if sleeves else "conviction"


def _holding_key(row: Mapping[str, str]) -> tuple[str, str, str]:
    return row["security_id"], row["provider_contract_id"], row["side"]


def _current_holdings(
    repository_root: Path,
    settings: Settings,
    strategies: Mapping[str, Mapping[str, str]],
    *,
    as_of: datetime,
) -> tuple[dict[tuple[str, str, str], _Holding], list[str]]:
    holdings: dict[tuple[str, str, str], _Holding] = {}
    blockers: list[str] = []
    strategy_legs = read_table(repository_root, "strategy_legs")
    order_legs = read_table(repository_root, "order_legs")
    latest = {row["security_id"]: row for row in read_table(repository_root, "market_latest")}
    for position in sorted(read_table(repository_root, "portfolio"), key=_holding_key):
        marked = parse_timestamp(position["last_mark_at"])
        assert marked is not None
        if marked > as_of or as_of - marked > settings.market_data.stale_price_after:
            blockers.append("market_data_stale")
        latest_state = latest.get(position["security_id"])
        if latest_state is not None and latest_state["status"] != "ok":
            blockers.append("market_data_not_ok")
        quantity = required_decimal(position["quantity"], label="portfolio quantity")
        mark = required_decimal(position["current_price"], label="portfolio mark")
        market_value = required_decimal(position["market_value_base"], label="portfolio value")
        multiplier = _position_multiplier(position, strategies, strategy_legs, order_legs)
        denominator = quantity * multiplier * mark
        if denominator <= 0 or market_value == 0:
            raise AdviceError(
                f"position cannot produce a valid FX reference: {position['position_id']}"
            )
        fx_rate = abs(market_value / denominator)
        try:
            fx_record = latest_fx_rate_record(
                repository_root,
                position["currency"],
                settings.portfolio.base_currency,
                now=as_of,
                maximum_age=settings.market_data.stale_price_after,
            )
        except MarketDataError:
            # A reconciled historical position can predate the retained FX cache. The
            # conversion itself remains provable from the generated position value; leave
            # its separate FX observation timestamp blank by using the mark timestamp.
            fx_as_of = marked
        else:
            if fx_record.rate_to_base != fx_rate:
                blockers.append("fx_reference_differs_from_position_mark")
            fx_as_of = fx_record.retrieved_at
        strategy_ids = {part for part in position["strategy_ids"].split("|") if part}
        holdings[_holding_key(position)] = _Holding(
            security_id=position["security_id"],
            provider_contract_id=position["provider_contract_id"],
            side=position["side"],
            instrument_type=position["instrument_type"],
            sleeve=_position_sleeve(position, strategies),
            currency=position["currency"],
            multiplier=multiplier,
            current_quantity=quantity,
            target_quantity=quantity,
            mark=mark,
            fx_rate=fx_rate,
            fx_as_of=fx_as_of,
            market_data_as_of=marked,
            strategy_ids=strategy_ids,
            signal_ids=set(),
            order_ids=set(),
            reason_codes=set(),
        )
    return holdings, blockers


def _pending_reference(
    repository_root: Path,
    settings: Settings,
    security: Mapping[str, str],
    leg: Mapping[str, str],
    signal: Mapping[str, str],
    order: Mapping[str, str],
    latest: Mapping[str, Mapping[str, str]],
    *,
    as_of: datetime,
) -> tuple[Decimal, Decimal, datetime, datetime]:
    if leg["instrument_type"] == "equity":
        market = latest.get(leg["security_id"])
        if market is None or market["status"] != "ok":
            raise AdviceError("market_data_not_ok")
        observed = parse_timestamp(market["retrieved_at"])
        assert observed is not None
        if observed > as_of or as_of - observed > settings.market_data.stale_price_after:
            raise AdviceError("market_data_stale")
        raw_mark = market["adjusted_close"] or market["close"]
        mark = required_decimal(raw_mark, label="pending equity mark")
    else:
        observed = parse_timestamp(signal["market_data_as_of"])
        assert observed is not None
        if observed > as_of or as_of - observed > settings.orders.option_quote_freshness:
            raise AdviceError("market_data_stale")
        raw_mark = leg["limit_price"] or order["limit_price"]
        if not raw_mark:
            raise AdviceError("market_data_missing")
        mark = required_decimal(raw_mark, label="pending option mark")
    try:
        fx_record = latest_fx_rate_record(
            repository_root,
            security["currency"],
            settings.portfolio.base_currency,
            now=as_of,
            maximum_age=settings.market_data.stale_price_after,
        )
    except MarketDataError as exc:
        raise AdviceError("fx_unavailable") from exc
    return mark, fx_record.rate_to_base, observed, fx_record.retrieved_at


def _apply_pending_orders(
    repository_root: Path,
    settings: Settings,
    holdings: dict[tuple[str, str, str], _Holding],
    securities: Mapping[str, Mapping[str, str]],
    strategies: Mapping[str, Mapping[str, str]],
    signals: Mapping[str, Mapping[str, str]],
    *,
    as_of: datetime,
) -> tuple[Decimal, list[str]]:
    orders: dict[str, Mapping[str, str]] = {}
    blockers: list[str] = []
    for row in read_table(repository_root, "orders"):
        if row["status"] not in NON_TERMINAL_ORDERS:
            continue
        created = parse_timestamp(row["created_at"])
        expires = parse_timestamp(row["expires_at"])
        if created is None or expires is None or created > as_of or expires <= as_of:
            blockers.append("pending_order_state_unsafe")
            continue
        orders[row["order_id"]] = row
    latest = {row["security_id"]: row for row in read_table(repository_root, "market_latest")}
    executed: defaultdict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for row in read_table(repository_root, "executions"):
        if row["order_id"] in orders:
            executed[(row["order_id"], row["leg_id"])] += required_decimal(
                row["quantity"], label="pending executed quantity"
            )
    order_gross: defaultdict[str, Decimal] = defaultdict(Decimal)
    order_cash: defaultdict[str, Decimal] = defaultdict(Decimal)
    orders_with_legs: set[str] = set()
    for row in sorted(
        read_table(repository_root, "order_legs"),
        key=lambda value: (value["order_id"], value["leg_id"]),
    ):
        order = orders.get(row["order_id"])
        if order is None:
            continue
        orders_with_legs.add(row["order_id"])
        signal = signals.get(order["signal_id"])
        strategy = strategies.get(order["strategy_id"])
        security = securities.get(row["security_id"])
        if signal is None or strategy is None or security is None:
            blockers.append("pending_order_state_unsafe")
            continue
        signal_created = parse_timestamp(signal["created_at"])
        signal_expires = parse_timestamp(signal["expires_at"])
        strategy_not_before = parse_timestamp(strategy["not_before"], allow_empty=True)
        strategy_expires = parse_timestamp(strategy["expires_at"], allow_empty=True)
        if (
            signal["status"] not in ACTIVE_SIGNAL_STATUSES
            or strategy["status"] not in ACTIVE_STRATEGY_STATUSES
            or signal_created is None
            or signal_expires is None
            or signal_created > as_of
            or signal_expires <= as_of
            or (strategy_not_before is not None and strategy_not_before > as_of)
            or (strategy_expires is not None and strategy_expires <= as_of)
        ):
            blockers.append("pending_order_state_unsafe")
            continue
        if strategy["sleeve"] == "baseline":
            target = latest_allocation_target(repository_root, strategy["strategy_id"])
            if (
                target is None
                or target["allocation_plan_id"] != strategy["allocation_plan_id"]
                or target["disposition"] not in {"open", "increase", "hold"}
            ):
                blockers.append("pending_order_state_unsafe")
                continue
        remaining = (
            required_decimal(row["quantity"], label="order quantity")
            - executed[(row["order_id"], row["leg_id"])]
        )
        if remaining <= 0:
            continue
        try:
            mark, fx_rate, observed, fx_as_of = _pending_reference(
                repository_root,
                settings,
                security,
                row,
                signal,
                order,
                latest,
                as_of=as_of,
            )
        except AdviceError as exc:
            blockers.append(str(exc))
            continue
        multiplier = required_decimal(row["contract_multiplier"], label="order multiplier")
        key = (row["security_id"], row["provider_contract_id"], row["side"])
        holding = holdings.get(key)
        if holding is None:
            holding = _Holding(
                security_id=row["security_id"],
                provider_contract_id=row["provider_contract_id"],
                side=row["side"],
                instrument_type=row["instrument_type"],
                sleeve=strategy["sleeve"],
                currency=row["currency"],
                multiplier=multiplier,
                current_quantity=Decimal("0"),
                target_quantity=Decimal("0"),
                mark=mark,
                fx_rate=fx_rate,
                fx_as_of=fx_as_of,
                market_data_as_of=observed,
                strategy_ids=set(),
                signal_ids=set(),
                order_ids=set(),
                reason_codes=set(),
            )
            holdings[key] = holding
        else:
            # Keep current and projected values on the reconciled position mark. The fresh
            # reference above is a safety gate, not permission to re-mark accounting here.
            mark = holding.mark
            fx_rate = holding.fx_rate
            fx_as_of = holding.fx_as_of
            observed = holding.market_data_as_of
        if (
            holding.currency != row["currency"]
            or holding.instrument_type != row["instrument_type"]
            or holding.multiplier != multiplier
        ):
            raise AdviceError(f"pending order changes holding identity: {row['order_id']}")
        opening = (row["side"] == "long" and row["action"] == "buy") or (
            row["side"] == "short" and row["action"] == "sell"
        )
        holding.target_quantity += remaining if opening else -remaining
        if holding.target_quantity < 0:
            blockers.append("pending_exposure_unpriced")
            holding.target_quantity = Decimal("0")
        local_value = remaining * multiplier * mark
        base_value = local_value * fx_rate
        order_gross[row["order_id"]] += base_value
        order_cash[row["order_id"]] += -base_value if row["action"] == "buy" else base_value
        holding.pending_delta_value += base_value if opening else -base_value
        holding.strategy_ids.add(order["strategy_id"])
        holding.signal_ids.add(order["signal_id"])
        holding.order_ids.add(order["order_id"])
    if set(orders).difference(orders_with_legs):
        blockers.append("pending_order_state_unsafe")
    cash_delta = Decimal("0")
    for order_id, amount in order_cash.items():
        fee = settings.orders.fixed_fee + (
            order_gross[order_id] * settings.orders.variable_fee_bps / Decimal("10000")
        )
        cash_delta += amount - fee
    return cash_delta, sorted(set(blockers))


def _discard_pending_projection(
    holdings: Mapping[tuple[str, str, str], _Holding],
    strategy_ids: Mapping[tuple[str, str, str], set[str]],
) -> None:
    """Restore the reconciled portfolio when any pending-order projection is unsafe."""

    for key, holding in holdings.items():
        holding.target_quantity = holding.current_quantity
        holding.pending_delta_value = Decimal("0")
        holding.signal_ids.clear()
        holding.order_ids.clear()
        holding.reason_codes.clear()
        holding.strategy_ids = set(strategy_ids.get(key, set()))


def _action_for_holding(holding: _Holding) -> tuple[str, str]:
    delta = holding.target_quantity - holding.current_quantity
    if holding.order_ids:
        if delta > 0:
            return ("add" if holding.current_quantity > 0 else "buy"), "pending_order"
        if delta < 0:
            return ("exit" if holding.target_quantity == 0 else "trim"), "pending_order"
    if holding.current_quantity > 0:
        return "hold", "filled"
    return "no_trade", "no_action"


def _row_metadata(
    holding: _Holding,
    securities: Mapping[str, Mapping[str, str]],
    strategies: Mapping[str, Mapping[str, str]],
    assessments: Mapping[str, Mapping[str, str]],
) -> tuple[Mapping[str, str], Mapping[str, str], Mapping[str, str]]:
    security = securities.get(holding.security_id)
    if security is None or not security["ticker"] or not security["company_name"]:
        raise AdviceError(f"public holding lacks a human-readable security: {holding.security_id}")
    strategy = next(
        (strategies[value] for value in sorted(holding.strategy_ids) if value in strategies), {}
    )
    assessment = assessments.get(holding.security_id, {})
    return security, strategy, assessment


def _portfolio_rows(
    snapshot_id: str,
    as_of: datetime,
    holdings: Mapping[tuple[str, str, str], _Holding],
    securities: Mapping[str, Mapping[str, str]],
    strategies: Mapping[str, Mapping[str, str]],
    assessments: Mapping[str, Mapping[str, str]],
    settings: Settings,
    current_equity: Decimal,
    target_equity: Decimal,
    current_cash: Decimal,
    target_cash: Decimal,
) -> tuple[ModelPortfolioRow, ...]:
    timestamp = format_timestamp(as_of)
    rows: list[ModelPortfolioRow] = []
    target_security_weights: list[Decimal] = []
    ordered_holdings = sorted(
        holdings.values(),
        key=lambda value: (value.security_id, value.provider_contract_id, value.side),
    )
    for holding in ordered_holdings:
        if holding.current_quantity == 0 and holding.target_quantity == 0:
            continue
        security, strategy, assessment = _row_metadata(holding, securities, strategies, assessments)
        action, action_status = _action_for_holding(holding)
        current_weight = _percent(holding.current_value, current_equity)
        target_weight = _percent(holding.target_value, target_equity)
        target_security_weights.append(target_weight)
        reason_codes = tuple(sorted(holding.reason_codes))
        for code in reason_codes:
            reason_label(code)
        effective_score = ""
        if assessment:
            try:
                effective_score = decimal_text(
                    score_assessment(
                        assessment, settings.allocation.cash_hurdle_score
                    ).effective_score
                )
            except (AllocationError, CanonicalValueError, KeyError) as exc:
                raise AdviceError(
                    f"holding has an invalid assessment: {holding.security_id}: {exc}"
                ) from exc
        rows.append(
            ModelPortfolioRow(
                snapshot_id=snapshot_id,
                as_of=timestamp,
                holding_type="security",
                security_id=holding.security_id,
                ticker=security["ticker"],
                company_name=security["company_name"],
                instrument_type=holding.instrument_type,
                sleeve=holding.sleeve,
                current_weight_pct=decimal_text(current_weight),
                target_weight_pct=decimal_text(target_weight),
                current_value_base=decimal_text(_money(holding.current_value)),
                target_value_base=decimal_text(_money(holding.target_value)),
                delta_value_base=decimal_text(_money(holding.target_value - holding.current_value)),
                current_quantity=decimal_text(holding.current_quantity),
                target_quantity=decimal_text(holding.target_quantity),
                mark=decimal_text(holding.mark),
                mark_currency=holding.currency,
                mark_base=decimal_text(holding.mark * holding.fx_rate),
                fx_rate_to_base=decimal_text(holding.fx_rate),
                fx_as_of=format_timestamp(holding.fx_as_of),
                market_data_as_of=format_timestamp(holding.market_data_as_of),
                action=action,
                action_status=action_status,
                strategy_id="|".join(sorted(holding.strategy_ids)),
                signal_id="|".join(sorted(holding.signal_ids)),
                order_id="|".join(sorted(holding.order_ids)),
                confidence=assessment.get("confidence", ""),
                effective_score=effective_score,
                downside_pct=assessment.get("downside_pct", ""),
                base_upside_pct=assessment.get("base_upside_pct", ""),
                bear_fair_value=assessment.get("bear_fair_value", ""),
                bear_return_pct=assessment.get("bear_return_pct", ""),
                bear_probability_pct=assessment.get("bear_probability_pct", ""),
                base_fair_value=assessment.get("base_fair_value", ""),
                base_return_pct=assessment.get("base_return_pct", ""),
                base_probability_pct=assessment.get("base_probability_pct", ""),
                bull_fair_value=assessment.get("bull_fair_value", ""),
                bull_return_pct=assessment.get("bull_return_pct", ""),
                bull_probability_pct=assessment.get("bull_probability_pct", ""),
                expected_return_pct=assessment.get("expected_return_pct", ""),
                confidence_adjusted_expected_return_pct=assessment.get(
                    "confidence_adjusted_expected_return_pct", ""
                ),
                buy_below_price=assessment.get("buy_below_price", ""),
                canonical_rating=assessment.get("canonical_rating", "") or "unrated",
                portfolio_action=assessment.get("portfolio_action", "") or "watch",
                evidence_state=assessment.get("evidence_state", "") or "research_incomplete",
                rating_change_conditions=assessment.get("rating_change_conditions", ""),
                valuation_horizon_months=assessment.get("valuation_horizon_months", ""),
                thesis_summary=strategy.get("thesis", security["research_summary"]),
                entry_rule=strategy.get("entry_rule", ""),
                exit_rule=strategy.get("exit_rule", ""),
                invalidation=strategy.get("invalidation", ""),
                review_at=assessment.get("expires_at", "") or security["next_review_at"],
                security_research_page=security["research_page"],
                strategy_research_page=strategy.get("research_page", ""),
                research_page=strategy.get("research_page", "") or security["research_page"],
                reason_codes=reason_codes,
            )
        )
    current_cash_weight = (
        _percent(current_cash, current_equity) if current_equity else Decimal("100")
    )
    target_cash_weight = Decimal("100") - sum(target_security_weights, Decimal("0"))
    rows.append(
        ModelPortfolioRow(
            snapshot_id=snapshot_id,
            as_of=timestamp,
            holding_type="cash",
            security_id="",
            ticker="CASH",
            company_name="Cash",
            instrument_type="cash",
            sleeve="cash",
            current_weight_pct=decimal_text(current_cash_weight),
            target_weight_pct=decimal_text(target_cash_weight),
            current_value_base=decimal_text(_money(current_cash)),
            target_value_base=decimal_text(_money(target_cash)),
            delta_value_base=decimal_text(_money(target_cash - current_cash)),
            current_quantity=decimal_text(_money(current_cash)),
            target_quantity=decimal_text(_money(target_cash)),
            mark="1",
            mark_currency="",
            mark_base="1",
            fx_rate_to_base="1",
            fx_as_of=timestamp,
            market_data_as_of=timestamp,
            action="no_trade"
            if current_cash == target_cash
            else ("trim" if target_cash < current_cash else "add"),
            action_status="no_action" if current_cash == target_cash else "pending_order",
            strategy_id="",
            signal_id="",
            order_id="",
            confidence="",
            effective_score="",
            downside_pct="",
            base_upside_pct="",
            bear_fair_value="",
            bear_return_pct="",
            bear_probability_pct="",
            base_fair_value="",
            base_return_pct="",
            base_probability_pct="",
            bull_fair_value="",
            bull_return_pct="",
            bull_probability_pct="",
            expected_return_pct="",
            confidence_adjusted_expected_return_pct="",
            buy_below_price="",
            canonical_rating="unrated",
            portfolio_action="hold",
            evidence_state="cash",
            rating_change_conditions="",
            valuation_horizon_months="",
            thesis_summary="Capital retained as the configured portfolio alternative.",
            entry_rule="",
            exit_rule="",
            invalidation="",
            review_at="",
            security_research_page="",
            strategy_research_page="",
            research_page="",
            reason_codes=(),
        )
    )
    return tuple(
        sorted(
            rows,
            key=lambda value: (
                value.holding_type != "cash",
                value.ticker,
                value.security_id,
                value.strategy_id,
            ),
        )
    )


def _portfolio_summaries(
    rows: tuple[ModelPortfolioRow, ...],
    performance: Mapping[str, str] | None,
    current_equity: Decimal,
    target_equity: Decimal,
    current_cash: Decimal,
    target_cash: Decimal,
) -> tuple[PortfolioSummary, PortfolioSummary]:
    security_rows = tuple(row for row in rows if row.holding_type == "security")
    current_values = [
        required_decimal(row.current_value_base, label="current value") for row in security_rows
    ]
    target_values = [
        required_decimal(row.target_value_base, label="target value") for row in security_rows
    ]
    current_gross = sum((abs(value) for value in current_values), Decimal("0"))
    target_gross = sum((abs(value) for value in target_values), Decimal("0"))
    current_net = sum(current_values, Decimal("0"))
    target_net = sum(target_values, Decimal("0"))
    realized = performance["realized_pnl_base"] if performance else "0"
    unrealized = performance["unrealized_pnl_base"] if performance else "0"
    current = PortfolioSummary(
        portfolio_kind="current",
        equity_base=decimal_text(_money(current_equity)),
        cash_base=decimal_text(_money(current_cash)),
        cash_weight_pct=decimal_text(
            _percent(current_cash, current_equity) if current_equity else Decimal("100")
        ),
        invested_value_base=decimal_text(_money(current_net)),
        invested_weight_pct=decimal_text(
            _percent(current_net, current_equity) if current_equity else Decimal("0")
        ),
        gross_exposure_base=decimal_text(_money(current_gross)),
        net_exposure_base=decimal_text(_money(current_net)),
        realized_pnl_base=realized,
        unrealized_pnl_base=unrealized,
        rows=rows,
    )
    target = PortfolioSummary(
        portfolio_kind="target",
        equity_base=decimal_text(_money(target_equity)),
        cash_base=decimal_text(_money(target_cash)),
        cash_weight_pct=next(row.target_weight_pct for row in rows if row.holding_type == "cash"),
        invested_value_base=decimal_text(_money(target_net)),
        invested_weight_pct=decimal_text(
            _percent(target_net, target_equity) if target_equity else Decimal("0")
        ),
        gross_exposure_base=decimal_text(_money(target_gross)),
        net_exposure_base=decimal_text(_money(target_net)),
        realized_pnl_base=realized,
        unrealized_pnl_base=unrealized,
        rows=rows,
    )
    return current, target


def _signal_action(signal_type: str, current_quantity: Decimal) -> str:
    if signal_type == "open":
        return "add" if current_quantity > 0 else "buy"
    if signal_type == "reduce":
        return "trim"
    if signal_type == "close":
        return "exit"
    return "no_trade"


def _actionable_signals(
    repository_root: Path,
    settings: Settings,
    rows: Sequence[ModelPortfolioRow],
    securities: Mapping[str, Mapping[str, str]],
    strategies: Mapping[str, Mapping[str, str]],
    assessments: Mapping[str, Mapping[str, str]],
    relationships: Sequence[Mapping[str, str]],
    impacts: Sequence[SystemImpact],
    *,
    as_of: datetime,
) -> tuple[ActionableSignalView, ...]:
    orders_by_signal: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for order_row in read_table(repository_root, "orders"):
        if order_row["status"] in NON_TERMINAL_ORDERS:
            orders_by_signal[order_row["signal_id"]].append(order_row)
    order_legs = read_table(repository_root, "order_legs")
    strategy_legs = read_table(repository_root, "strategy_legs")
    latest = {row["security_id"]: row for row in read_table(repository_root, "market_latest")}
    rows_by_security: defaultdict[str, list[ModelPortfolioRow]] = defaultdict(list)
    for row in rows:
        if row.holding_type == "security":
            rows_by_security[row.security_id].append(row)
    current_relationships = {
        (row["relationship_id"], row["security_id"])
        for row in relationships
        if _current_relationship(row, as_of=as_of)
    }
    views: list[ActionableSignalView] = []
    for signal in sorted(
        read_table(repository_root, "signals"), key=lambda value: value["signal_id"]
    ):
        if signal["status"] not in ACTIVE_SIGNAL_STATUSES:
            continue
        expires = parse_timestamp(signal["expires_at"])
        created = parse_timestamp(signal["created_at"])
        market_as_of = parse_timestamp(signal["market_data_as_of"])
        assert expires is not None and created is not None and market_as_of is not None
        if not (created <= as_of < expires) or market_as_of > as_of:
            continue
        strategy = strategies.get(signal["strategy_id"])
        if strategy is None or strategy["status"] not in ACTIVE_STRATEGY_STATUSES:
            continue
        not_before = parse_timestamp(strategy["not_before"], allow_empty=True)
        strategy_expires = parse_timestamp(strategy["expires_at"], allow_empty=True)
        if (not_before is not None and as_of < not_before) or (
            strategy_expires is not None and as_of >= strategy_expires
        ):
            continue
        security = securities.get(strategy["security_id"])
        if security is None or not security["ticker"] or not security["company_name"]:
            raise AdviceError(f"actionable signal lacks a public security: {signal['signal_id']}")
        if strategy["sleeve"] == "baseline" and not _current_assessment(
            assessments.get(strategy["security_id"]), settings, as_of=as_of
        ):
            continue
        if (
            strategy["relationship_id"]
            and (strategy["relationship_id"], strategy["security_id"]) not in current_relationships
        ):
            continue
        canonical_strategy_legs = tuple(
            sorted(
                (row for row in strategy_legs if row["strategy_id"] == strategy["strategy_id"]),
                key=lambda value: value["leg_id"],
            )
        )
        if not canonical_strategy_legs:
            continue
        try:
            normalized_strategy_legs = tuple(leg_from_row(row) for row in canonical_strategy_legs)
        except (CanonicalValueError, KeyError, ValueError):
            continue
        affected_security_ids = {leg.security_id for leg in normalized_strategy_legs}
        if any(
            impact.impact in {"blocks_portfolio", "blocks_action"}
            and (not impact.security_id or impact.security_id in affected_security_ids)
            for impact in impacts
        ):
            continue
        matching_orders = sorted(
            orders_by_signal[signal["signal_id"]], key=lambda value: value["order_id"]
        )
        if len(matching_orders) > 1:
            raise AdviceError(f"signal has multiple non-terminal orders: {signal['signal_id']}")
        selected_order: Mapping[str, str] | None = matching_orders[0] if matching_orders else None
        canonical_legs = tuple(
            sorted(
                (
                    row
                    for row in order_legs
                    if selected_order and row["order_id"] == selected_order["order_id"]
                ),
                key=lambda value: value["leg_id"],
            )
        )
        for leg in canonical_legs:
            leg_from_row(leg)
        portfolio_rows = rows_by_security.get(strategy["security_id"], [])
        projected_order_ids = {
            order_id
            for portfolio_row in portfolio_rows
            for order_id in portfolio_row.order_id.split("|")
            if order_id
        }
        if selected_order and selected_order["order_id"] not in projected_order_ids:
            continue
        signal_maximum_age = (
            settings.orders.option_quote_freshness
            if any(leg.instrument_type != "equity" for leg in normalized_strategy_legs)
            else settings.market_data.stale_price_after
        )
        if as_of - market_as_of > signal_maximum_age:
            continue
        if selected_order is None:
            fresh_inputs = True
            for normalized_leg in normalized_strategy_legs:
                leg_security = securities.get(normalized_leg.security_id)
                if leg_security is None or normalized_leg.currency != leg_security["currency"]:
                    fresh_inputs = False
                    break
                if normalized_leg.instrument_type != "equity":
                    fresh_inputs = False
                    break
                market = latest.get(normalized_leg.security_id)
                observed = parse_timestamp(market["retrieved_at"]) if market else None
                if (
                    market is None
                    or market["status"] != "ok"
                    or observed is None
                    or observed > as_of
                    or as_of - observed > settings.market_data.stale_price_after
                ):
                    fresh_inputs = False
                    break
                try:
                    latest_fx_rate(
                        repository_root,
                        normalized_leg.currency,
                        settings.portfolio.base_currency,
                        now=as_of,
                        maximum_age=settings.market_data.stale_price_after,
                    )
                except MarketDataError:
                    fresh_inputs = False
                    break
            if not fresh_inputs:
                continue
        current_quantity = sum(
            (
                required_decimal(row.current_quantity, label="signal current quantity")
                for row in portfolio_rows
            ),
            Decimal("0"),
        )
        action = _signal_action(signal["signal_type"], current_quantity)
        action_status = "pending_order" if selected_order else "awaiting_order_validation"
        copy_ready = bool(selected_order and canonical_legs)
        quantity = ""
        if copy_ready and len(canonical_legs) == 1:
            quantity = decimal_text(
                required_decimal(canonical_legs[0]["quantity"], label="copy quantity")
            )
        views.append(
            ActionableSignalView(
                signal_id=signal["signal_id"],
                strategy_id=strategy["strategy_id"],
                order_id=selected_order["order_id"] if selected_order else "",
                security_id=security["security_id"],
                ticker=security["ticker"],
                company_name=security["company_name"],
                action=action,
                action_status=action_status,
                copy_ready=copy_ready,
                quantity=quantity,
                order_type=selected_order["order_type"] if selected_order else "",
                limit_price=selected_order["limit_price"] if selected_order else "",
                currency=selected_order["currency"] if selected_order else security["currency"],
                created_at=signal["created_at"],
                expires_at=signal["expires_at"],
                market_data_as_of=signal["market_data_as_of"],
                current_weight_pct=decimal_text(
                    sum(
                        (
                            required_decimal(row.current_weight_pct, label="signal current weight")
                            for row in portfolio_rows
                        ),
                        Decimal("0"),
                    )
                ),
                target_weight_pct=decimal_text(
                    sum(
                        (
                            required_decimal(
                                row.target_weight_pct,
                                label="signal target weight",
                            )
                            for row in portfolio_rows
                        ),
                        Decimal("0"),
                    )
                ),
                strategy_name=strategy["name"],
                entry_rule=strategy["entry_rule"],
                exit_rule=strategy["exit_rule"],
                invalidation=strategy["invalidation"],
                rationale=signal["rationale"],
                security_research_page=security["research_page"],
                strategy_research_page=strategy["research_page"],
                research_page=strategy["research_page"] or security["research_page"],
                reason_codes=(),
                legs=tuple({key: leg[key] for key in leg} for leg in canonical_legs),
            )
        )
    return tuple(sorted(views, key=lambda value: (value.expires_at, value.ticker, value.signal_id)))


def _candidate_classification(
    target: Mapping[str, str],
    assessment: Mapping[str, str] | None,
    strategy: Mapping[str, str] | None,
) -> str:
    reasons = set(part for part in target["reason"].split("|") if part)
    if assessment is not None and assessment.get("research_status") == "unsupported":
        return "valuation_unsupported"
    if assessment is not None and assessment.get("research_status") in {"partial", "stale"}:
        return "research_incomplete"
    if assessment is None or "assessment_missing" in reasons or "assessment_stale" in reasons:
        return "research_incomplete"
    if "allocation_plan_stale" in reasons:
        return "research_incomplete"
    if reasons.intersection(
        {
            "market_data_identity_mismatch",
            "market_data_missing",
            "market_data_not_ok",
            "market_data_stale",
            "fx_unavailable",
        }
    ):
        return "market_data_blocked"
    if reasons.intersection(
        {
            "score_below_cash_hurdle",
            "base_upside_not_positive",
            "base_upside_below_minimum",
            "upside_downside_ratio_below_minimum",
            "assessment_ineligible",
            "expected_return_below_minimum",
            "base_return_below_minimum",
            "bear_base_payoff_below_minimum",
            "expected_bear_payoff_below_minimum",
            "margin_of_safety_below_minimum",
        }
    ):
        return "valuation_unattractive"
    if "relationship_rejected" in reasons:
        return "relationship_pending"
    if "relationship_missing_or_stale" in reasons:
        return "relationship_pending"
    if any(
        reason
        in {
            "concentration_cap",
            "insufficient_diversification",
            "insufficient_eligible_candidates",
            "deployment_budget_exhausted",
            "minimum_trade_threshold",
            "baseline_sleeve_cap",
        }
        or reason.startswith("hard_blocker:")
        for reason in reasons
    ):
        blockers = "|".join(reasons)
        if "liquidity_insufficient" in blockers:
            return "liquidity_blocked"
        if "solvency_risk" in blockers:
            return "solvency_blocked"
        return "research_incomplete"
    if strategy is None or strategy["status"] not in ACTIVE_STRATEGY_STATUSES:
        if assessment is not None and assessment.get("allocation_eligibility") == "eligible":
            return "strategy_pending"
        if assessment is not None and assessment.get("canonical_rating") in {"buy", "strong_buy"}:
            return "valuation_attractive"
        return "valuation_unattractive"
    return "strategy_ready"


def _candidate_pipeline(
    repository_root: Path,
    settings: Settings,
    securities: Mapping[str, Mapping[str, str]],
    strategies: Mapping[str, Mapping[str, str]],
    assessments: Mapping[str, Mapping[str, str]],
    relationships: Sequence[Mapping[str, str]],
    *,
    run_id: str,
    as_of: datetime,
) -> tuple[CandidateView, ...]:
    values: list[CandidateView] = []
    targets = read_table(repository_root, "allocation_targets")
    plan_keys = {
        (target["allocation_plan_id"], target["run_id"], target["as_of"]) for target in targets
    }
    current_plan = len(plan_keys) <= 1 and all(
        target["run_id"] == run_id and parse_timestamp(target["as_of"]) == as_of
        for target in targets
    )
    latest = {row["security_id"]: row for row in read_table(repository_root, "market_latest")}
    current_relationship_ids = {
        row["security_id"] for row in relationships if _current_relationship(row, as_of=as_of)
    }
    rejected_relationship_ids = {
        row["security_id"]
        for row in relationships
        if row["status"] == "rejected" and _current_relationship_review(row, as_of=as_of)
    }
    for target in targets:
        security = securities.get(target["security_id"])
        if security is None or not security["ticker"] or not security["company_name"]:
            raise AdviceError(f"allocation target lacks a public security: {target['security_id']}")
        assessment = assessments.get(target["security_id"])
        reasons = set(part for part in target["reason"].split("|") if part)
        assessment_is_current = _current_assessment(assessment, settings, as_of=as_of)
        if not current_plan:
            reasons.add("allocation_plan_stale")
        if assessment is None:
            reasons.add("assessment_missing")
        elif not assessment_is_current:
            reasons.add("assessment_stale")
        else:
            is_v2 = assessment.get("assessment_schema_version") == "2"
            if not is_v2 and assessment["eligibility"] == "ineligible":
                reasons.add("assessment_ineligible")
            blockers = tuple(
                sorted(part for part in assessment["hard_blockers"].split("|") if part)
            )
            if blockers:
                reasons.add(f"hard_blocker:{','.join(blockers)}")
            reasons.update(assessment_payoff_reasons(assessment, settings))
            if not is_v2 and (
                score_assessment(assessment, settings.allocation.cash_hurdle_score).effective_score
                < settings.allocation.cash_hurdle_score
            ):
                reasons.add("score_below_cash_hurdle")
            market = latest.get(target["security_id"])
            if market is None:
                reasons.add("market_data_missing")
            elif market["status"] != "ok":
                reasons.add("market_data_not_ok")
            else:
                observed = parse_timestamp(market["retrieved_at"])
                assert observed is not None
                if observed > as_of or as_of - observed > settings.market_data.stale_price_after:
                    reasons.add("market_data_stale")
                if (
                    market["provider_symbol"] != security["provider_symbol"]
                    or market["currency"] != security["currency"]
                ):
                    reasons.add("market_data_identity_mismatch")
                try:
                    latest_fx_rate(
                        repository_root,
                        security["currency"],
                        settings.portfolio.base_currency,
                        now=as_of,
                        maximum_age=settings.market_data.stale_price_after,
                    )
                except MarketDataError:
                    reasons.add("fx_unavailable")
            if target["security_id"] not in current_relationship_ids:
                reasons.add(
                    "relationship_rejected"
                    if target["security_id"] in rejected_relationship_ids
                    else "relationship_missing_or_stale"
                )
        ordered_reasons = tuple(
            sorted(
                reasons,
                key=lambda reason: (
                    reason in {"above_cash_hurdle", "target_unchanged"},
                    reason,
                ),
            )
        )
        labels = tuple(reason_label(reason) for reason in ordered_reasons)
        strategy = strategies.get(target["strategy_id"])
        projected_target_weight = target["target_weight_pct"] if current_plan else "0"
        frontier = (
            {
                "expected_return_pct": assessment["frontier_expected_return_pct"],
                "base_return_pct": assessment["frontier_base_return_pct"],
                "bear_base_payoff_ratio": assessment["frontier_bear_base_payoff_ratio"],
                "expected_bear_payoff_ratio": assessment["frontier_expected_bear_payoff_ratio"],
                "margin_of_safety_pct": assessment["frontier_margin_of_safety_pct"],
                "confidence_levels": assessment["frontier_confidence_levels"],
                "relationship_status": assessment["frontier_relationship_status"],
                "hard_blockers": assessment["frontier_hard_blockers"],
            }
            if assessment and assessment.get("assessment_schema_version") == "2"
            else {}
        )
        values.append(
            CandidateView(
                security_id=security["security_id"],
                ticker=security["ticker"],
                company_name=security["company_name"],
                research_page=security["research_page"],
                classification=_candidate_classification(
                    {**target, "reason": "|".join(ordered_reasons)}, assessment, strategy
                ),
                rank=target["rank"],
                effective_score=target["effective_score"],
                candidate_edge=target["candidate_edge"],
                target_weight_pct=projected_target_weight,
                confidence=assessment["confidence"] if assessment else "",
                downside_pct=assessment["downside_pct"] if assessment else "",
                base_upside_pct=assessment["base_upside_pct"] if assessment else "",
                review_at=assessment["expires_at"] if assessment else security["next_review_at"],
                reason_codes=ordered_reasons,
                reason_labels=labels,
                bear_fair_value=assessment.get("bear_fair_value", "") if assessment else "",
                bear_return_pct=assessment.get("bear_return_pct", "") if assessment else "",
                bear_probability_pct=(
                    assessment.get("bear_probability_pct", "") if assessment else ""
                ),
                base_fair_value=assessment.get("base_fair_value", "") if assessment else "",
                base_return_pct=assessment.get("base_return_pct", "") if assessment else "",
                base_probability_pct=(
                    assessment.get("base_probability_pct", "") if assessment else ""
                ),
                bull_fair_value=assessment.get("bull_fair_value", "") if assessment else "",
                bull_return_pct=assessment.get("bull_return_pct", "") if assessment else "",
                bull_probability_pct=(
                    assessment.get("bull_probability_pct", "") if assessment else ""
                ),
                expected_return_pct=(
                    assessment.get("expected_return_pct", "") if assessment else ""
                ),
                confidence_adjusted_expected_return_pct=(
                    assessment.get("confidence_adjusted_expected_return_pct", "")
                    if assessment
                    else ""
                ),
                buy_below_price=assessment.get("buy_below_price", "") if assessment else "",
                canonical_rating=(
                    assessment.get("canonical_rating", "") or "unrated" if assessment else "unrated"
                ),
                portfolio_action=(
                    assessment.get("portfolio_action", "") or "watch" if assessment else "watch"
                ),
                evidence_state=(
                    assessment.get("research_status", "") or "unsupported"
                    if assessment
                    else "incomplete"
                ),
                eligibility_frontier=frontier,
                rating_change_conditions=(
                    assessment.get("rating_change_conditions", "") if assessment else ""
                ),
                research_conclusion=(
                    assessment.get("research_conclusion", "") if assessment else ""
                ),
            )
        )

    def key(value: CandidateView) -> tuple[object, ...]:
        assessed = bool(value.effective_score)
        edge = required_decimal(value.candidate_edge or "0", label="candidate edge")
        score = required_decimal(value.effective_score or "0", label="effective score")
        confidence = CONFIDENCE_RANK.get(value.confidence, -1)
        upside = required_decimal(value.base_upside_pct or "0", label="candidate upside")
        return (not assessed, -edge, -score, -confidence, -upside, value.security_id)

    return tuple(sorted(values, key=key))


def _packet_document(path: Path) -> Mapping[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise AdviceError(f"candidate packet lacks frontmatter: {path.name}")
    raw, _ = text[4:].split("\n---\n", maxsplit=1)
    value = yaml.safe_load(raw)
    if not isinstance(value, Mapping):
        raise AdviceError(f"candidate packet frontmatter is invalid: {path.name}")
    return value


@dataclass(frozen=True, slots=True)
class _AlertResearchState:
    status: str
    conclusion: str
    updated_at: str


def _alert_operation_inputs(
    repository_root: Path, row: Mapping[str, str]
) -> Mapping[str, object] | None:
    """Read trusted operation inputs used to join alerts with research outcomes."""

    if row["operation_type"] not in {
        "opportunity_research",
        "quick_check_research",
        "security_research",
    }:
        return None
    path = PurePosixPath(row["payload_path"])
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.parts[:3] != ("data", "operations", "payloads")
        or path.suffix != ".json"
    ):
        return None
    absolute = repository_root.joinpath(*path.parts)
    if absolute.is_symlink() or not absolute.is_file():
        return None
    try:
        payload = json.loads(absolute.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    inputs = payload.get("inputs") if isinstance(payload, dict) else None
    return inputs if isinstance(inputs, dict) else None


def _operation_conclusions(
    repository_root: Path,
) -> Mapping[tuple[str, str, str], _AlertResearchState]:
    states: dict[tuple[str, str, str], _AlertResearchState] = {}

    def retain(
        *,
        security_id: str,
        trigger: str,
        market_date: str,
        status: str,
        conclusion: str,
        updated_at: str,
    ) -> None:
        state = _AlertResearchState(status, " ".join(conclusion.split())[:1000], updated_at)
        for key in ((security_id, trigger, market_date), (security_id, trigger, "")):
            previous = states.get(key)
            if previous is None or previous.updated_at <= updated_at:
                states[key] = state

    for row in read_table(repository_root, "operations_history"):
        inputs = _alert_operation_inputs(repository_root, row)
        if inputs is None:
            continue
        security_id = inputs.get("security_id")
        raw_triggers: object = (
            inputs.get("trigger_types")
            if row["operation_type"] in {"security_research", "quick_check_research"}
            else [inputs.get("trigger_type")]
        )
        market_date = inputs.get("market_data_date") or inputs.get("period_end")
        if (
            not isinstance(security_id, str)
            or not isinstance(raw_triggers, list)
            or not isinstance(market_date, str)
        ):
            continue
        conclusion = row["result_summary"] or row["terminal_reason"]
        if not conclusion:
            continue
        for trigger in raw_triggers:
            if isinstance(trigger, str) and trigger:
                retain(
                    security_id=security_id,
                    trigger=trigger,
                    market_date=market_date,
                    status=row["terminal_status"],
                    conclusion=conclusion,
                    updated_at=row["completed_at"],
                )
    active_labels = {
        "queued": "High-priority security research is queued.",
        "ready": "High-priority security research is ready to run.",
        "running": "High-priority security research is running.",
        "waiting": "High-priority security research is waiting on its scheduling constraints.",
        "blocked": "High-priority security research is blocked.",
    }
    for row in read_table(repository_root, "operations_todo"):
        inputs = _alert_operation_inputs(repository_root, row)
        if inputs is None or row["operation_type"] not in {
            "security_research",
            "quick_check_research",
        }:
            continue
        security_id = inputs.get("security_id")
        raw_triggers = inputs.get("trigger_types")
        market_date = inputs.get("market_data_date")
        if (
            not isinstance(security_id, str)
            or not isinstance(raw_triggers, list)
            or not isinstance(market_date, str)
        ):
            continue
        conclusion = active_labels.get(row["status"], "Security research is pending.")
        if row["status"] == "blocked" and row["last_error"]:
            conclusion = f"{conclusion} {row['last_error']}"
        for trigger in raw_triggers:
            if isinstance(trigger, str) and trigger:
                retain(
                    security_id=security_id,
                    trigger=trigger,
                    market_date=market_date,
                    status=row["status"],
                    conclusion=conclusion,
                    updated_at=row["updated_at"],
                )
    return states


def _candidate_packets(
    repository_root: Path,
) -> Mapping[tuple[str, str], tuple[str, Mapping[str, object], Path]]:
    packets: dict[tuple[str, str], tuple[str, Mapping[str, object], Path]] = {}
    for path in sorted((repository_root / "data" / "wiki" / "inbox").glob("*.md")):
        document = _packet_document(path)
        facts = document.get("candidate_facts")
        if not isinstance(facts, Mapping):
            continue
        security_id = facts.get("security_id")
        trigger = facts.get("trigger")
        market_date = facts.get("as_of_date")
        if not all(
            isinstance(value, str) and value for value in (security_id, trigger, market_date)
        ):
            continue
        key = (str(security_id), str(trigger))
        previous = packets.get(key)
        if previous is None or previous[0] <= str(market_date):
            packets[key] = (str(market_date), document, path)
    return packets


def _research_alerts(
    repository_root: Path, securities: Mapping[str, Mapping[str, str]]
) -> tuple[ResearchAlertView, ...]:
    conclusions = _operation_conclusions(repository_root)
    packets = _candidate_packets(repository_root)
    alerts: list[ResearchAlertView] = []
    seen: set[tuple[str, str]] = set()
    latest_dates = {
        row["security_id"]: row["as_of_date"] for row in read_table(repository_root, "indicators")
    }

    def append_alert(*, security_id: str, trigger: str, market_date: str, observed_at: str) -> None:
        security = securities.get(security_id)
        if security is None or not security["ticker"] or not security["company_name"]:
            raise AdviceError(f"research alert lacks a public security: {security_id}")
        packet = packets.get((security_id, trigger))
        packet_date = packet[0] if packet is not None else ""
        document = packet[1] if packet is not None else {}
        state = (
            conclusions.get((security_id, trigger, market_date))
            or conclusions.get((security_id, trigger, packet_date))
            or conclusions.get((security_id, trigger, ""))
        )
        decision = str(document.get("classifier_decision", "pending"))
        reason = " ".join(str(document.get("classifier_reason", "")).split())
        research_page = security["research_page"] or (
            f"data/wiki/security-catalog.md#security-{security_id}"
        )
        alerts.append(
            ResearchAlertView(
                alert_id=stable_id("alert", security_id, trigger, market_date),
                security_id=security_id,
                ticker=security["ticker"],
                company_name=security["company_name"],
                alert_type=trigger,
                observed_at=observed_at,
                market_data_date=market_date,
                research_status=state.status if state is not None else decision,
                research_conclusion=(
                    state.conclusion
                    if state is not None
                    else reason or "Deterministic price alert awaits bounded research review."
                ),
                research_page=research_page,
            )
        )
        seen.add((security_id, trigger))

    for indicator in read_table(repository_root, "indicators"):
        for trigger in sorted(part for part in indicator["trigger_state"].split("|") if part):
            append_alert(
                security_id=indicator["security_id"],
                trigger=trigger,
                market_date=indicator["as_of_date"],
                observed_at=indicator["calculated_at"],
            )
    for (security_id, trigger), (market_date, _, _) in packets.items():
        if (security_id, trigger) in seen or latest_dates.get(security_id) != market_date:
            continue
        append_alert(
            security_id=security_id,
            trigger=trigger,
            market_date=market_date,
            observed_at=f"{market_date}T00:00:00Z",
        )
    return tuple(
        sorted(
            alerts,
            key=lambda value: (value.observed_at, value.ticker, value.alert_id),
            reverse=True,
        )
    )


def _coverage(
    repository_root: Path,
    settings: Settings,
    assessments: Mapping[str, Mapping[str, str]],
    relationships: Sequence[Mapping[str, str]],
    impacts: Sequence[SystemImpact],
    *,
    as_of: datetime,
) -> CoverageSummary:
    targets = read_table(repository_root, "allocation_targets")
    candidate_ids = {row["security_id"] for row in targets}
    sources = {row["source_id"]: row for row in read_table(repository_root, "source_registry")}
    current_assessments = [
        row
        for security_id, row in assessments.items()
        if security_id in candidate_ids and _current_assessment(row, settings, as_of=as_of)
    ]
    reviewed_relationship_security_ids = {
        row["security_id"]
        for row in relationships
        if row["security_id"] in candidate_ids and _current_relationship_review(row, as_of=as_of)
    }
    accepted_relationship_security_ids = {
        row["security_id"]
        for row in relationships
        if row["security_id"] in candidate_ids and _current_relationship(row, as_of=as_of)
    }
    strategies = read_table(repository_root, "strategies")
    signals = read_table(repository_root, "signals")
    active_signals = 0
    for row in signals:
        created = parse_timestamp(row["created_at"])
        expires = parse_timestamp(row["expires_at"])
        if (
            row["status"] in ACTIVE_SIGNAL_STATUSES
            and created is not None
            and created <= as_of
            and expires is not None
            and expires > as_of
        ):
            active_signals += 1
    latest = read_table(repository_root, "market_latest")
    current_strategies = []
    for row in strategies:
        not_before = parse_timestamp(row["not_before"], allow_empty=True)
        expires = parse_timestamp(row["expires_at"], allow_empty=True)
        if (
            row["status"] in ACTIVE_STRATEGY_STATUSES
            and (not_before is None or not_before <= as_of)
            and (expires is None or expires > as_of)
        ):
            current_strategies.append(row)
    pending_orders = []
    for row in read_table(repository_root, "orders"):
        created = parse_timestamp(row["created_at"])
        expires = parse_timestamp(row["expires_at"])
        if (
            row["status"] in NON_TERMINAL_ORDERS
            and created is not None
            and created <= as_of
            and expires is not None
            and expires > as_of
        ):
            pending_orders.append(row)
    successful_runs = [
        row
        for row in read_table(repository_root, "runs")
        if row["status"] == "succeeded" and (parse_timestamp(row["completed_at"]) or as_of) <= as_of
    ]
    blocking = sum(impact.impact in {"blocks_portfolio", "blocks_action"} for impact in impacts)
    return CoverageSummary(
        allocation_candidate_count=len(candidate_ids),
        current_assessment_count=len(current_assessments),
        fresh_evidence_assessment_count=sum(
            _fresh_evidence(row, sources, settings) for row in current_assessments
        ),
        reviewed_relationship_count=len(reviewed_relationship_security_ids),
        accepted_relationship_count=len(accepted_relationship_security_ids),
        required_relationship_review_count=len(candidate_ids),
        ready_or_active_strategy_count=len(current_strategies),
        active_signal_count=active_signals,
        pending_order_count=len(pending_orders),
        market_data_success_count=sum(row["status"] == "ok" for row in latest),
        market_data_failure_count=sum(row["status"] != "ok" for row in latest),
        research_backlog_count=len(read_table(repository_root, "operations_todo")),
        blocking_issue_count=blocking,
        non_blocking_issue_count=len(impacts) - blocking,
        last_successful_daily_run=(
            max(successful_runs, key=lambda row: (row["completed_at"], row["run_id"]))[
                "completed_at"
            ]
            if successful_runs
            else ""
        ),
    )


def _performance_summary(
    repository_root: Path,
    rows: Sequence[ModelPortfolioRow],
    securities: Mapping[str, Mapping[str, str]],
    performance: Mapping[str, str] | None,
    *,
    as_of: datetime,
) -> PerformanceSummary:
    current_epoch_id = performance["performance_epoch_id"] if performance is not None else ""
    epochs = read_table(repository_root, "performance_epochs")
    current_epoch = next(
        (row for row in epochs if row["performance_epoch_id"] == current_epoch_id), None
    )
    history_rows = sorted(
        (
            row
            for row in read_table(repository_root, "performance_daily")
            if row["performance_epoch_id"] == current_epoch_id
            and (parse_timestamp(row["generated_at"]) or as_of) <= as_of
            and row["date"] <= as_of.date().isoformat()
        ),
        key=lambda value: value["date"],
    )
    high_water = Decimal("0")
    history: list[Mapping[str, str]] = []
    running_drawdown = Decimal("0")
    for row in history_rows:
        equity = required_decimal(row["equity_base"], label="performance equity")
        high_water = max(high_water, equity)
        drawdown = (
            ((equity - high_water) / high_water * Decimal("100")) if high_water else Decimal("0")
        )
        running_drawdown = drawdown
        history.append(
            {
                "date": row["date"],
                "equity_base": row["equity_base"],
                "cash_base": row["cash_base"],
                "gross_exposure_base": row["gross_exposure_base"],
                "daily_return_pct": row["daily_return_pct"],
                "cumulative_return_pct": row["cumulative_return_pct"],
                "drawdown_pct": decimal_text(
                    drawdown.quantize(PERCENT_QUANTUM, rounding=ROUND_HALF_EVEN)
                ),
            }
        )
    security_rows = [row for row in rows if row.holding_type == "security"]
    baseline = sum(
        (
            abs(required_decimal(row.current_value_base, label="baseline exposure"))
            for row in security_rows
            if row.sleeve == "baseline"
        ),
        Decimal("0"),
    )
    conviction = sum(
        (
            abs(required_decimal(row.current_value_base, label="conviction exposure"))
            for row in security_rows
            if row.sleeve == "conviction"
        ),
        Decimal("0"),
    )
    equity = (
        required_decimal(performance["equity_base"], label="latest equity")
        if performance
        else Decimal("0")
    )
    largest_position = max(
        (
            abs(required_decimal(row.current_value_base, label="position concentration"))
            for row in security_rows
        ),
        default=Decimal("0"),
    )
    sectors: defaultdict[str, Decimal] = defaultdict(Decimal)
    for portfolio_row in security_rows:
        sectors[securities[portfolio_row.security_id]["sector"] or "Unclassified"] += abs(
            required_decimal(portfolio_row.current_value_base, label="sector exposure")
        )
    largest_sector = max(sectors.values(), default=Decimal("0"))
    return PerformanceSummary(
        performance_epoch_id=current_epoch_id,
        epoch_started_at=current_epoch["started_at"] if current_epoch is not None else "",
        epoch_opening_equity_base=(
            current_epoch["opening_equity_base"] if current_epoch is not None else "0"
        ),
        prior_epoch_count=max(len(epochs) - (1 if current_epoch is not None else 0), 0),
        daily_return_pct=performance["daily_return_pct"] if performance else "0",
        cumulative_return_pct=performance["cumulative_return_pct"] if performance else "0",
        running_drawdown_pct=decimal_text(running_drawdown),
        realized_pnl_base=performance["realized_pnl_base"] if performance else "0",
        unrealized_pnl_base=performance["unrealized_pnl_base"] if performance else "0",
        conviction_exposure_base=decimal_text(_money(conviction)),
        baseline_exposure_base=decimal_text(_money(baseline)),
        largest_position_weight_pct=decimal_text(
            _percent(largest_position, equity) if equity else Decimal("0")
        ),
        largest_sector_weight_pct=decimal_text(
            _percent(largest_sector, equity) if equity else Decimal("0")
        ),
        history=tuple(history),
    )


def _investment_data_status(
    holdings: Mapping[tuple[str, str, str], _Holding],
    pending_blockers: Sequence[str],
    current_blockers: Sequence[str],
    coverage: CoverageSummary,
    impacts: Sequence[SystemImpact],
) -> str:
    if (
        current_blockers
        or pending_blockers
        or any(impact.impact == "blocks_portfolio" for impact in impacts)
    ):
        return "blocked"
    data_gaps = (
        coverage.current_assessment_count < coverage.allocation_candidate_count
        or coverage.reviewed_relationship_count < coverage.required_relationship_review_count
        or coverage.market_data_failure_count > 0
        or any(impact.impact == "affects_candidate" for impact in impacts)
    )
    if data_gaps:
        return "degraded"
    return "current"


def _operations_status(impacts: Sequence[SystemImpact]) -> str:
    if any(impact.impact in {"blocks_portfolio", "blocks_action"} for impact in impacts):
        return "blocked"
    if any(impact.impact in {"publication_only", "operational_only"} for impact in impacts):
        return "degraded"
    return "current"


def _stance(
    status: str,
    current: PortfolioSummary,
    actions: Sequence[ActionableSignalView],
    blocked_reason_codes: Sequence[str],
) -> tuple[str, tuple[str, ...]]:
    if status == "blocked":
        return "blocked", tuple(sorted(set(blocked_reason_codes)))
    openings = [action for action in actions if action.action in {"buy", "add"}]
    reductions = [action for action in actions if action.action in {"trim", "exit"}]
    if reductions and not openings and all(action.action == "exit" for action in reductions):
        return "exit", ("validated_reduce_actions",)
    if reductions and openings:
        return "rebalance", ("validated_rebalance_actions",)
    if reductions:
        return "reduce_risk", ("validated_reduce_actions",)
    if openings and required_decimal(current.invested_value_base, label="invested value") == 0:
        return "deploy", ("validated_open_actions",)
    if openings:
        return "rebalance", ("validated_open_actions",)
    if required_decimal(current.gross_exposure_base, label="gross exposure") == 0:
        return "hold_cash", ("portfolio_all_cash", "no_actionable_signals")
    return "maintain", ("no_actionable_signals",)


def _research_benchmark(
    securities: Mapping[str, Mapping[str, str]],
    assessments: Mapping[str, Mapping[str, str]],
) -> ResearchBenchmark:
    """Build a one-way equal-weight research benchmark with no trading authority."""

    rating_rank = {"strong_buy": 2, "buy": 1}
    ranked = sorted(
        (
            assessment
            for assessment in assessments.values()
            if assessment.get("canonical_rating") in rating_rank
            and assessment.get("valuation_supported") == "true"
            and assessment.get("research_status") == "complete"
        ),
        key=lambda row: (
            -rating_rank[row["canonical_rating"]],
            -required_decimal(
                row["confidence_adjusted_expected_return_pct"], label="benchmark return"
            ),
            row["security_id"],
        ),
    )[:10]
    # Fix the equal security weight before applying the sector cap; rejected slots remain cash.
    security_weight = min(
        Decimal("25"),
        Decimal("100") / Decimal(len(ranked)) if ranked else Decimal("0"),
    )
    selected: list[Mapping[str, str]] = []
    sector_weights: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for row in ranked:
        security = securities[row["security_id"]]
        sector = security.get("sector") or f"unclassified:{row['security_id']}"
        if sector_weights[sector] + security_weight > Decimal("25"):
            continue
        selected.append(row)
        sector_weights[sector] += security_weight
    rows = [
        ResearchBenchmarkRow(
            security_id=row["security_id"],
            ticker=securities[row["security_id"]]["ticker"],
            company_name=securities[row["security_id"]]["company_name"],
            rating=row["canonical_rating"],
            weight_pct=decimal_text(security_weight),
            reference_price=row["reference_price"],
            currency=row["reference_currency"],
            research_page=securities[row["security_id"]]["research_page"],
        )
        for row in selected
    ]
    cash_weight = Decimal("100") - security_weight * len(rows)
    rows.append(
        ResearchBenchmarkRow(
            security_id="",
            ticker="CASH",
            company_name="Cash",
            rating="unrated",
            weight_pct=decimal_text(cash_weight),
            reference_price="1",
            currency="",
            research_page="",
        )
    )
    return ResearchBenchmark(
        policy_version="equal_weight_rated_v1",
        comparison_only=True,
        copy_ready=False,
        rows=tuple(rows),
    )


def _evidence_state(
    investment_status: str,
    stance: str,
    candidates: Sequence[CandidateView],
) -> str:
    if investment_status == "blocked":
        return "portfolio_blocked"
    if stance != "hold_cash":
        return "invested_or_actionable"
    if any(candidate.classification == "valuation_unsupported" for candidate in candidates):
        return "provisional_cash_valuation_unsupported"
    if any(candidate.classification == "research_incomplete" for candidate in candidates):
        return "provisional_cash_research_incomplete"
    if any(
        candidate.classification in {"strategy_pending", "valuation_attractive"}
        for candidate in candidates
    ):
        return "provisional_cash_strategy_pending"
    return "definitive_cash_preference"


def build_decision_snapshot(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    as_of: datetime | None = None,
) -> DecisionSnapshot:
    """Build one immutable snapshot without writing publication state."""

    if not RUN_ID.fullmatch(run_id):
        raise AdviceError(f"invalid decision run_id: {run_id!r}")
    instant = _snapshot_as_of(repository_root, run_id, as_of)
    reconciliation = reconcile_portfolio(repository_root)
    if reconciliation:
        raise AdviceError("portfolio is not reconciled: " + "; ".join(reconciliation))
    source_hashes = _source_hashes(repository_root, as_of=instant)
    snapshot_id = stable_id("decision", run_id, format_timestamp(instant), source_hashes)
    securities = {row["security_id"]: row for row in read_table(repository_root, "securities")}
    strategies = {row["strategy_id"]: row for row in read_table(repository_root, "strategies")}
    assessments = {
        row["security_id"]: row for row in read_table(repository_root, "security_assessments")
    }
    relationships = read_table(repository_root, "relationships")
    signals = {row["signal_id"]: row for row in read_table(repository_root, "signals")}
    performance = _current_performance(repository_root, settings, as_of=instant)
    replay = replay_accounting(repository_root)
    holdings, current_blockers = _current_holdings(
        repository_root, settings, strategies, as_of=instant
    )
    current_net = sum((holding.current_value for holding in holdings.values()), Decimal("0"))
    current_cash = replay.cash_base
    current_equity = current_cash + current_net
    if performance is not None and (
        required_decimal(performance["cash_base"], label="performance cash") != current_cash
        or required_decimal(performance["equity_base"], label="performance equity")
        != current_equity
    ):
        raise AdviceError("latest performance snapshot does not reconcile with accounting")
    reconciled_strategy_ids = {key: set(holding.strategy_ids) for key, holding in holdings.items()}
    cash_delta, pending_blockers = _apply_pending_orders(
        repository_root,
        settings,
        holdings,
        securities,
        strategies,
        signals,
        as_of=instant,
    )
    target_cash = current_cash + cash_delta
    if target_cash < 0:
        pending_blockers.append("pending_exposure_unpriced")
    if pending_blockers or current_blockers:
        _discard_pending_projection(holdings, reconciled_strategy_ids)
        target_cash = current_cash
    target_net = sum((holding.target_value for holding in holdings.values()), Decimal("0"))
    target_equity = target_cash + target_net
    rows = _portfolio_rows(
        snapshot_id,
        instant,
        holdings,
        securities,
        strategies,
        assessments,
        settings,
        current_equity,
        target_equity,
        current_cash,
        target_cash,
    )
    current, target = _portfolio_summaries(
        rows,
        performance,
        current_equity,
        target_equity,
        current_cash,
        target_cash,
    )
    impacts = _system_impacts(repository_root, securities, as_of=instant)
    candidates = _candidate_pipeline(
        repository_root,
        settings,
        securities,
        strategies,
        assessments,
        relationships,
        run_id=run_id,
        as_of=instant,
    )
    alerts = _research_alerts(repository_root, securities)
    coverage = _coverage(
        repository_root,
        settings,
        assessments,
        relationships,
        impacts,
        as_of=instant,
    )
    investment_status = _investment_data_status(
        holdings, pending_blockers, current_blockers, coverage, impacts
    )
    operations_status = _operations_status(impacts)
    actions = (
        ()
        if investment_status == "blocked"
        else _actionable_signals(
            repository_root,
            settings,
            rows,
            securities,
            strategies,
            assessments,
            relationships,
            impacts,
            as_of=instant,
        )
    )
    blocked_reasons = {
        *current_blockers,
        *pending_blockers,
        *(
            ("portfolio_issue_open",)
            if any(impact.impact == "blocks_portfolio" for impact in impacts)
            else ()
        ),
    }
    stance, stance_reasons = _stance(investment_status, current, actions, tuple(blocked_reasons))
    for code in stance_reasons:
        reason_label(code)
    snapshot = DecisionSnapshot(
        version=SNAPSHOT_VERSION,
        snapshot_id=snapshot_id,
        run_id=run_id,
        as_of=format_timestamp(instant),
        report_date=instant.date().isoformat(),
        investment_data_status=investment_status,
        operations_status=operations_status,
        stance=stance,
        stance_reason_codes=stance_reasons,
        evidence_state=_evidence_state(investment_status, stance, candidates),
        base_currency=settings.portfolio.base_currency,
        current_portfolio=current,
        target_portfolio=target,
        actionable_signals=actions,
        candidate_pipeline=candidates,
        research_benchmark=_research_benchmark(securities, assessments),
        research_alerts=alerts,
        coverage=coverage,
        performance=_performance_summary(
            repository_root, rows, securities, performance, as_of=instant
        ),
        system_impacts=impacts,
        source_state_hashes=source_hashes,
    )
    _validate_snapshot_object(repository_root, snapshot_document(snapshot))
    return snapshot


def _schema(repository_root: Path) -> Mapping[str, object]:
    path = repository_root / "schemas" / "decision_snapshot.schema.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdviceError("decision snapshot schema must contain an object")
    return value


def _validate_snapshot_object(repository_root: Path, value: Mapping[str, object]) -> None:
    validator = Draft202012Validator(_schema(repository_root), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        raise AdviceError(
            "decision snapshot schema: "
            + "; ".join(
                f"{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
                for error in errors
            )
        )
    if value.get("version") == 2:
        row_fields = {
            "mark_base",
            "fx_as_of",
            "security_research_page",
            "strategy_research_page",
        }
        for portfolio_key in ("current_portfolio", "approved_target_portfolio"):
            portfolio = value.get(portfolio_key)
            if not isinstance(portfolio, Mapping) or not isinstance(portfolio.get("rows"), list):
                continue
            for index, row in enumerate(portfolio["rows"]):
                if not isinstance(row, Mapping) or not row_fields.issubset(row):
                    raise AdviceError(
                        f"decision snapshot schema: {portfolio_key}/rows/{index}: "
                        "version 2 FX and research-link fields are required"
                    )
        signal_fields = {"security_research_page", "strategy_research_page"}
        raw_signals = value.get("actionable_signals")
        if not isinstance(raw_signals, list):
            raise AdviceError("decision snapshot schema: actionable_signals must be an array")
        for index, signal in enumerate(raw_signals):
            if not isinstance(signal, Mapping) or not signal_fields.issubset(signal):
                raise AdviceError(
                    f"decision snapshot schema: actionable_signals/{index}: "
                    "version 2 research-link fields are required"
                )


def snapshot_document(snapshot: DecisionSnapshot) -> dict[str, object]:
    """Return the canonical JSON-compatible representation of a typed snapshot."""

    value = json.loads(canonical_json(asdict(snapshot)))
    assert isinstance(value, dict)
    return value


def _portfolio_csv_rows(snapshot: DecisionSnapshot) -> list[dict[str, object]]:
    values: list[dict[str, object]] = []
    for row in snapshot.current_portfolio.rows:
        value = asdict(row)
        value["reason_codes"] = "|".join(row.reason_codes)
        values.append(value)
    return values


def _benchmark_csv_rows(snapshot: DecisionSnapshot) -> list[dict[str, object]]:
    return [
        {
            "snapshot_id": snapshot.snapshot_id,
            "as_of": snapshot.as_of,
            "policy_version": snapshot.research_benchmark.policy_version,
            "comparison_only": "true",
            "copy_ready": "false",
            **asdict(row),
        }
        for row in snapshot.research_benchmark.rows
    ]


def _signal_csv_rows(snapshot: DecisionSnapshot) -> list[dict[str, object]]:
    values: list[dict[str, object]] = []
    for signal in snapshot.actionable_signals:
        raw = asdict(signal)
        value = {
            key: (
                snapshot.snapshot_id
                if key == "snapshot_id"
                else snapshot.as_of
                if key == "as_of"
                else raw[key]
            )
            for key in ACTIONABLE_SIGNAL_COLUMNS
        }
        value["copy_ready"] = "true" if signal.copy_ready else "false"
        value["reason_codes"] = "|".join(signal.reason_codes)
        values.append(value)
    return values


def _open_cycle_snapshot_is_replaceable(repository_root: Path, run_id: str) -> bool:
    """Return whether a run artifact belongs to an interrupted, unfinished cycle."""

    manifest_path = repository_root / "data" / "runs" / run_id / "daily_run.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        isinstance(manifest, dict)
        and manifest.get("daily_run_version") == 2
        and manifest.get("daily_cycle_id") == run_id
        and manifest.get("status") in {"running", "degraded", "interrupted"}
        and not manifest.get("finalization_at")
        and not manifest.get("completion_at")
    )


def refresh_advice(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    as_of: datetime | None = None,
    render_pages: bool = True,
) -> DecisionSnapshot:
    """Atomically publish one validated immutable run snapshot and latest exports."""

    snapshot = build_decision_snapshot(repository_root, settings, run_id=run_id, as_of=as_of)
    document = snapshot_document(snapshot)
    run_path = repository_root / "data" / "runs" / run_id / "decision_snapshot.json"
    run_directory = run_path.parent
    if run_directory.exists():
        if run_directory.is_symlink() or not run_directory.is_dir():
            raise AdviceError("decision run artifact directory must be a regular directory")
    else:
        runs_directory = run_directory.parent
        if runs_directory.is_symlink() or not runs_directory.is_dir():
            raise AdviceError("data/runs must be a regular directory")
        run_directory.mkdir()
    if run_path.exists():
        if run_path.is_symlink():
            raise AdviceError("immutable decision snapshot conflicts with existing run artifact")
        try:
            existing_document = json.loads(run_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AdviceError(
                "immutable decision snapshot conflicts with existing run artifact"
            ) from exc
        if existing_document != document:
            if not _open_cycle_snapshot_is_replaceable(repository_root, run_id):
                raise AdviceError(
                    "immutable decision snapshot conflicts with existing run artifact"
                )
            atomic_write_json(run_path, document, allowed_root=repository_root)
    else:
        atomic_write_json(run_path, document, allowed_root=repository_root)
    published = repository_root / "data" / "published"
    published.mkdir(parents=True, exist_ok=True)
    if published.is_symlink():
        raise AdviceError("published data directory must not be a symlink")
    atomic_write_json(published / "decision_snapshot.json", document, allowed_root=repository_root)
    write_table(repository_root, "published_model_portfolio", _portfolio_csv_rows(snapshot))
    write_table(repository_root, "published_actionable_signals", _signal_csv_rows(snapshot))
    write_table(
        repository_root,
        "published_research_benchmark",
        _benchmark_csv_rows(snapshot),
    )
    errors = validate_advice(repository_root, strict=True)
    if errors:
        raise AdviceError("; ".join(errors))
    if render_pages:
        from papertrader.investor_pages import refresh_investor_pages

        refresh_investor_pages(repository_root, snapshot)
    return snapshot


def load_published_snapshot(
    repository_root: Path, *, expected_run_id: str | None = None
) -> DecisionSnapshot:
    """Load and validate the latest publication snapshot as typed immutable state."""

    path = repository_root / "data" / "published" / "decision_snapshot.json"
    if path.is_symlink() or not path.is_file():
        raise AdviceError("published decision snapshot is unavailable")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdviceError("published decision snapshot must contain an object")
    _validate_snapshot_object(repository_root, value)
    raw_value = cast(dict[str, Any], value)
    if expected_run_id is not None and raw_value["run_id"] != expected_run_id:
        raise AdviceError("published decision snapshot belongs to a different run")

    version = int(raw_value["version"])

    def model_row(raw: dict[str, Any]) -> ModelPortfolioRow:
        normalized = dict(raw)
        if version < 4:
            normalized.update(
                {
                    "target_weight_pct": normalized.pop("approved_target_weight_pct"),
                    "target_value_base": normalized.pop("approved_target_value_base"),
                    "target_quantity": normalized.pop("approved_target_quantity"),
                }
            )
        if version == 1:
            normalized.update(
                {
                    "mark_base": decimal_text(
                        required_decimal(raw["mark"], label="legacy mark")
                        * required_decimal(raw["fx_rate_to_base"], label="legacy FX rate")
                    ),
                    "fx_as_of": raw["market_data_as_of"],
                    "security_research_page": raw["research_page"],
                    "strategy_research_page": "",
                }
            )
        if version < 3:
            normalized.update(
                {
                    "bear_fair_value": "",
                    "bear_return_pct": "",
                    "bear_probability_pct": "",
                    "base_fair_value": "",
                    "base_return_pct": "",
                    "base_probability_pct": "",
                    "bull_fair_value": "",
                    "bull_return_pct": "",
                    "bull_probability_pct": "",
                    "expected_return_pct": "",
                    "confidence_adjusted_expected_return_pct": "",
                    "buy_below_price": "",
                    "canonical_rating": "unrated",
                    "portfolio_action": "watch" if raw["holding_type"] == "security" else "hold",
                    "evidence_state": "legacy" if raw["holding_type"] == "security" else "cash",
                    "rating_change_conditions": "",
                }
            )
        return ModelPortfolioRow(
            **{**normalized, "reason_codes": tuple(normalized["reason_codes"])}
        )

    def portfolio(raw: dict[str, Any]) -> PortfolioSummary:
        normalized = dict(raw)
        if version < 4 and normalized.get("portfolio_kind") == "approved_target":
            normalized["portfolio_kind"] = "target"
        return PortfolioSummary(
            **{**normalized, "rows": tuple(model_row(row) for row in normalized["rows"])}
        )

    def signal_view(raw: dict[str, Any]) -> ActionableSignalView:
        normalized = dict(raw)
        if version < 4:
            normalized["target_weight_pct"] = normalized.pop("approved_target_weight_pct")
        if version == 1:
            normalized.update(
                {
                    "security_research_page": raw["research_page"],
                    "strategy_research_page": "",
                }
            )
        return ActionableSignalView(
            **{
                **normalized,
                "reason_codes": tuple(normalized["reason_codes"]),
                "legs": tuple(normalized["legs"]),
            }
        )

    raw_coverage = dict(raw_value["coverage"])
    if version == 1:
        legacy_relationships = int(raw_coverage.pop("current_relationship_count"))
        legacy_required = int(raw_coverage.pop("required_relationship_count"))
        raw_coverage.update(
            {
                "reviewed_relationship_count": legacy_relationships,
                "accepted_relationship_count": legacy_relationships,
                "required_relationship_review_count": legacy_required,
            }
        )
    candidate_defaults: dict[str, object] = {
        "bear_fair_value": "",
        "bear_return_pct": "",
        "bear_probability_pct": "",
        "base_fair_value": "",
        "base_return_pct": "",
        "base_probability_pct": "",
        "bull_fair_value": "",
        "bull_return_pct": "",
        "bull_probability_pct": "",
        "expected_return_pct": "",
        "confidence_adjusted_expected_return_pct": "",
        "buy_below_price": "",
        "canonical_rating": "unrated",
        "portfolio_action": "watch",
        "evidence_state": "unsupported",
        "eligibility_frontier": {},
        "rating_change_conditions": "",
        "research_conclusion": "",
    }
    raw_benchmark = raw_value.get("research_benchmark")
    benchmark = (
        ResearchBenchmark(
            policy_version=str(raw_benchmark["policy_version"]),
            comparison_only=bool(
                raw_benchmark["comparison_only" if version >= 4 else "non_approved"]
            ),
            copy_ready=bool(raw_benchmark["copy_ready"]),
            rows=tuple(ResearchBenchmarkRow(**row) for row in raw_benchmark["rows"]),
        )
        if isinstance(raw_benchmark, dict)
        else ResearchBenchmark(
            policy_version="legacy_unavailable",
            comparison_only=True,
            copy_ready=False,
            rows=(),
        )
    )
    return DecisionSnapshot(
        version=version,
        snapshot_id=str(raw_value["snapshot_id"]),
        run_id=str(raw_value["run_id"]),
        as_of=str(raw_value["as_of"]),
        report_date=str(raw_value["report_date"]),
        investment_data_status=str(
            raw_value["data_status" if version == 1 else "investment_data_status"]
        ),
        operations_status=("current" if version == 1 else str(raw_value["operations_status"])),
        stance=str(raw_value["stance"]),
        stance_reason_codes=tuple(raw_value["stance_reason_codes"]),
        evidence_state=str(raw_value.get("evidence_state", "provisional_cash_research_incomplete")),
        base_currency=str(raw_value["base_currency"]),
        current_portfolio=portfolio(raw_value["current_portfolio"]),
        target_portfolio=portfolio(
            raw_value["target_portfolio" if version >= 4 else "approved_target_portfolio"]
        ),
        actionable_signals=tuple(signal_view(raw) for raw in raw_value["actionable_signals"]),
        candidate_pipeline=tuple(
            CandidateView(
                **{
                    **{
                        **raw,
                        "classification": (
                            "strategy_ready"
                            if version < 4 and raw["classification"] == "approved"
                            else raw["classification"]
                        ),
                    },
                    **({} if version >= 3 else candidate_defaults),
                    "reason_codes": tuple(raw["reason_codes"]),
                    "reason_labels": tuple(raw["reason_labels"]),
                }
            )
            for raw in raw_value["candidate_pipeline"]
        ),
        research_benchmark=benchmark,
        research_alerts=tuple(ResearchAlertView(**raw) for raw in raw_value["research_alerts"]),
        coverage=CoverageSummary(**raw_coverage),
        performance=PerformanceSummary(
            **{
                **(
                    {
                        "performance_epoch_id": "",
                        "epoch_started_at": "",
                        "epoch_opening_equity_base": "0",
                        "prior_epoch_count": 0,
                    }
                    if version == 1
                    else {}
                ),
                **raw_value["performance"],
                "history": tuple(raw_value["performance"]["history"]),
            }
        ),
        system_impacts=tuple(SystemImpact(**raw) for raw in raw_value["system_impacts"]),
        source_state_hashes=dict(raw_value["source_state_hashes"]),
    )


def validate_advice(
    repository_root: Path,
    *,
    strict: bool = False,
    require_current_state: bool = True,
) -> list[str]:
    """Validate snapshot identity, immutable copy, and exact generated CSV exports.

    A prepared daily run may advance canonical inputs before it publishes its final snapshot.
    Such an in-flight operation can defer only the source-state freshness comparison; all other
    publication invariants remain mandatory.
    """

    errors: list[str] = []
    path = repository_root / "data" / "published" / "decision_snapshot.json"
    portfolio_path = repository_root / "data" / "published" / "model_portfolio.csv"
    signals_path = repository_root / "data" / "published" / "actionable_signals.csv"
    if not path.exists():
        if strict:
            return ["published decision snapshot is missing"]
        return []
    if any(
        value.is_symlink() or not value.is_file() for value in (path, portfolio_path, signals_path)
    ):
        return ["published decision artifacts must be regular files"]
    try:
        snapshot = load_published_snapshot(repository_root)
    except (AdviceError, OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return [str(exc)]
    try:
        snapshot_as_of = parse_timestamp(snapshot.as_of)
        assert snapshot_as_of is not None
        current_source_hashes = _source_hashes(repository_root, as_of=snapshot_as_of)
    except (AdviceError, CanonicalValueError, OSError, UnicodeError) as exc:
        errors.append(f"cannot validate decision source state: {exc}")
    else:
        if require_current_state and dict(snapshot.source_state_hashes) != current_source_hashes:
            previous = dict(snapshot.source_state_hashes)
            differing = {
                key
                for key in set(previous) | set(current_source_hashes)
                if previous.get(key) != current_source_hashes.get(key)
            }
            configuration_only = differing == {"configuration"} and (
                _configuration_only_runtime_changed(
                    repository_root,
                    run_id=snapshot.run_id,
                    expected_hash=previous.get("configuration", ""),
                )
            )
            podcast_only = _post_publication_podcast_only_changed(
                repository_root,
                run_id=snapshot.run_id,
                as_of=snapshot_as_of,
                expected_hashes=previous,
                differing=differing,
            )
            delivery_only = _post_publication_delivery_issue_reopened(
                repository_root,
                as_of=snapshot_as_of,
                expected_hashes=previous,
                differing=differing,
            )
            legacy_contracts_only = _legacy_publication_contracts_changed(
                repository_root,
                snapshot=snapshot,
                differing=differing,
            )
            if (
                not configuration_only
                and not podcast_only
                and not delivery_only
                and not legacy_contracts_only
            ):
                errors.append(
                    "published decision snapshot does not match current authoritative state"
                )
        expected_snapshot_id = stable_id(
            "decision", snapshot.run_id, snapshot.as_of, snapshot.source_state_hashes
        )
        if snapshot.snapshot_id != expected_snapshot_id:
            errors.append("published decision snapshot ID does not match its source state")
    run_path = repository_root / "data" / "runs" / snapshot.run_id / "decision_snapshot.json"
    if run_path.is_symlink() or not run_path.is_file():
        errors.append("published decision snapshot lacks its immutable run artifact")
    elif run_path.read_bytes() != path.read_bytes():
        errors.append("published decision snapshot differs from its immutable run artifact")
    if (
        tuple(contract_by_name(repository_root, "published_model_portfolio").columns)
        != MODEL_PORTFOLIO_COLUMNS
    ):
        errors.append("model portfolio CSV contract differs from the publication model")
    if (
        tuple(contract_by_name(repository_root, "published_actionable_signals").columns)
        != ACTIONABLE_SIGNAL_COLUMNS
    ):
        errors.append("actionable signal CSV contract differs from the publication model")
    if tuple(contract_by_name(repository_root, "published_research_benchmark").columns) != (
        "snapshot_id",
        "as_of",
        "policy_version",
        "comparison_only",
        "copy_ready",
        "security_id",
        "ticker",
        "company_name",
        "rating",
        "weight_pct",
        "reference_price",
        "currency",
        "research_page",
    ):
        errors.append("research benchmark CSV contract differs from the publication model")
    try:
        expected_portfolio = [
            {column: str(value) for column, value in row.items()}
            for row in _portfolio_csv_rows(snapshot)
        ]
        expected_signals = [
            {column: str(value) for column, value in row.items()}
            for row in _signal_csv_rows(snapshot)
        ]
        expected_benchmark = [
            {column: str(value) for column, value in row.items()}
            for row in _benchmark_csv_rows(snapshot)
        ]
        if read_table(repository_root, "published_model_portfolio") != expected_portfolio:
            errors.append("model portfolio CSV differs from the decision snapshot")
        if read_table(repository_root, "published_actionable_signals") != expected_signals:
            errors.append("actionable signal CSV differs from the decision snapshot")
        if read_table(repository_root, "published_research_benchmark") != expected_benchmark:
            errors.append("research benchmark CSV differs from the decision snapshot")
    except (CanonicalValueError, OSError) as exc:
        errors.append(str(exc))
    target_weights = sum(
        (
            required_decimal(row.target_weight_pct, label="target weight")
            for row in snapshot.target_portfolio.rows
        ),
        Decimal("0"),
    )
    if abs(target_weights - Decimal("100")) > WEIGHT_TOLERANCE:
        errors.append("target weights do not reconcile to 100%")
    current_weights = sum(
        (
            required_decimal(row.current_weight_pct, label="current weight")
            for row in snapshot.current_portfolio.rows
        ),
        Decimal("0"),
    )
    if abs(current_weights - Decimal("100")) > WEIGHT_TOLERANCE:
        errors.append("current portfolio weights do not reconcile to 100%")
    if required_decimal(snapshot.target_portfolio.cash_base, label="target cash") < 0:
        errors.append("target cash is negative")
    if snapshot.current_portfolio.rows != snapshot.target_portfolio.rows:
        errors.append("current and target portfolio views do not share one row projection")
    cash_rows = [row for row in snapshot.current_portfolio.rows if row.holding_type == "cash"]
    if len(cash_rows) != 1:
        errors.append("decision portfolio must contain exactly one cash row")
    for row in snapshot.current_portfolio.rows:
        if row.snapshot_id != snapshot.snapshot_id or row.as_of != snapshot.as_of:
            errors.append("decision portfolio row identity differs from its snapshot")
            break
    for portfolio in (snapshot.current_portfolio, snapshot.target_portfolio):
        equity = required_decimal(portfolio.equity_base, label="portfolio equity")
        cash = required_decimal(portfolio.cash_base, label="portfolio cash")
        net = required_decimal(portfolio.net_exposure_base, label="portfolio net exposure")
        invested = required_decimal(portfolio.invested_value_base, label="invested value")
        if abs(equity - cash - net) > MONEY_QUANTUM:
            errors.append(f"{portfolio.portfolio_kind} equity does not reconcile")
        if invested != net:
            errors.append(f"{portfolio.portfolio_kind} invested value differs from net exposure")
    for signal in snapshot.actionable_signals:
        if signal.copy_ready and (
            not signal.order_id
            or not signal.legs
            or (len(signal.legs) == 1 and not signal.quantity)
        ):
            errors.append(f"copy-ready signal lacks a validated order export: {signal.signal_id}")
    for candidate in snapshot.candidate_pipeline:
        for code, label in zip(candidate.reason_codes, candidate.reason_labels, strict=True):
            try:
                if reason_label(code) != label:
                    errors.append(
                        f"candidate reason translation differs: {candidate.security_id}:{code}"
                    )
            except AdviceError as exc:
                errors.append(str(exc))
    if not snapshot.research_benchmark.comparison_only or snapshot.research_benchmark.copy_ready:
        errors.append("research benchmark trading boundary is invalid")
    benchmark_weight = sum(
        (
            required_decimal(row.weight_pct, label="research benchmark weight")
            for row in snapshot.research_benchmark.rows
        ),
        Decimal("0"),
    )
    if snapshot.version >= 3 and abs(benchmark_weight - Decimal("100")) > WEIGHT_TOLERANCE:
        errors.append("research benchmark weights do not reconcile to 100%")
    return errors

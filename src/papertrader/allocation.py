"""Deterministic opportunity-cost-aware baseline allocation planning.

The planner produces research targets only. It never creates a signal, order, fill,
execution, cash entry, position, or performance row. Decimal scores are rounded to two
places with bankers' rounding; positive monetary targets are rounded down to cents and
then down to whole equity units so neither deployment nor reserve limits can be exceeded.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal
from pathlib import Path, PurePosixPath

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.dedupe import SemanticDisposition
from papertrader.market_data import MarketDataError, latest_fx_rate
from papertrader.portfolio import reconcile_portfolio, replay_accounting
from papertrader.queue import enqueue_operation, prepare_queue
from papertrader.tables import append_unique, read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    content_hash,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    required_decimal,
    stable_id,
    utc_now,
)

SCORE_QUANTUM = Decimal("0.01")
MONEY_QUANTUM = Decimal("0.01")
ONE_HUNDRED = Decimal("100")
CONFIDENCE_MULTIPLIERS = {
    "high": Decimal("1"),
    "medium": Decimal("0.8"),
    "low": Decimal("0.5"),
}
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
SCORE_WEIGHTS = {
    "thesis_score": Decimal("0.25"),
    "business_quality_score": Decimal("0.20"),
    "balance_sheet_score": Decimal("0.15"),
    "valuation_score": Decimal("0.25"),
    "timing_score": Decimal("0.10"),
    "liquidity_score": Decimal("0.05"),
}
ELIGIBLE_ASSESSMENTS = frozenset({"baseline", "conviction"})
ELIGIBLE_SECURITY_STATUSES = frozenset({"active", "watching"})
ALLOCATABLE_DISPOSITIONS = frozenset({"open", "increase", "reduce", "close"})
SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
CANONICAL_IDEA_LINK = re.compile(r"\[\[ideas/([a-z][a-z0-9_-]{0,127})\]\]")
CURRENT_SOURCE_STATUSES = frozenset({"available", "ok", "current"})
ALLOCATION_MAINTENANCE_SOURCE = "deterministic-allocation-maintenance"
ALLOCATION_BACKFILL_SOURCE = "deterministic-allocation-backfill"
ALLOCATION_MAINTENANCE_SOURCES = frozenset(
    {ALLOCATION_MAINTENANCE_SOURCE, ALLOCATION_BACKFILL_SOURCE}
)


class AllocationError(RuntimeError):
    """Raised when authoritative inputs cannot produce a safe allocation plan."""


class _AllocationMaintenanceOverlapReviewer:
    """Merge equivalent active refresh/backfill work for one immutable entity."""

    def review(
        self,
        candidate: dict[str, str],
        existing: tuple[dict[str, str], ...],
    ) -> SemanticDisposition:
        matches = tuple(
            row
            for row in existing
            if candidate["source"] in ALLOCATION_MAINTENANCE_SOURCES
            and row["source"] in ALLOCATION_MAINTENANCE_SOURCES
        )
        if not matches:
            return SemanticDisposition(
                "execute", "The overlapping operation has a distinct non-maintenance source."
            )
        target = min(matches, key=lambda row: (row["created_at"], row["operation_id"]))
        return SemanticDisposition(
            "merge",
            "Equivalent active allocation maintenance objective for the same immutable entity.",
            target["operation_id"],
        )


@dataclass(frozen=True, slots=True)
class AssessmentScore:
    """Reproducible comparable score and edge over holding cash."""

    raw_score: Decimal
    effective_score: Decimal
    candidate_edge: Decimal


@dataclass(frozen=True, slots=True)
class AllocationPlanResult:
    """Serializable summary of one finalized allocation plan."""

    allocation_plan_id: str
    run_id: str
    as_of: str
    mode: str
    equity_base: str
    cash_base: str
    minimum_cash_reserve_base: str
    current_gross_exposure_base: str
    target_invested_exposure_base: str
    current_conviction_exposure_base: str
    current_baseline_exposure_base: str
    maximum_baseline_exposure_base: str
    pending_gross_exposure_base: str
    deployment_budget_base: str
    diversified_budget_base: str
    capital_allocated_base: str
    capital_unallocated_base: str
    unallocated_reasons: tuple[str, ...]
    evidence_state: str
    eligible_candidate_count: int
    excluded_candidate_count: int
    target_count: int
    operations_created: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AllocationMaintenanceResult:
    """Operations deterministically requested for the maintained research universe."""

    run_id: str
    as_of: str
    backfill: bool
    researched_security_count: int
    relationship_pair_count: int
    security_operations: tuple[str, ...]
    relationship_operations: tuple[str, ...]
    operations_created: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AllocationReadinessResult:
    """Machine-readable activation coverage and strict readiness errors."""

    as_of: str
    ready: bool
    researched_security_count: int
    current_assessment_count: int
    fresh_evidence_assessment_count: int
    relationship_pair_count: int
    current_relationship_pair_count: int
    errors: tuple[str, ...]


@dataclass(slots=True)
class _Candidate:
    security_id: str
    security: Mapping[str, str]
    assessment: Mapping[str, str] | None
    relationship_id: str
    themes: tuple[str, ...]
    assessment_id: str
    tier: str
    live_valuation: Mapping[str, str]
    score: AssessmentScore
    price: Decimal | None
    price_as_of: datetime | None
    fx_rate: Decimal | None
    assessment_at: datetime | None
    eligible: bool
    reasons: list[str]
    rank: int = 0
    allocation: Decimal = Decimal("0")

    @property
    def unit_value_base(self) -> Decimal | None:
        if self.price is None or self.fx_rate is None:
            return None
        return self.price * self.fx_rate


@dataclass(frozen=True, slots=True)
class _PortfolioExposure:
    current_total: Mapping[str, Decimal]
    current_baseline: Mapping[str, Decimal]
    current_conviction: Mapping[str, Decimal]
    sector_total: Mapping[str, Decimal]
    theme_total: Mapping[str, Decimal]
    baseline_total: Decimal
    conviction_total: Decimal
    gross_total: Decimal


@dataclass(frozen=True, slots=True)
class _PendingExposure:
    gross_total: Decimal
    committed_cash: Decimal
    total_by_security: Mapping[str, Decimal]
    baseline_by_security: Mapping[str, Decimal]
    conviction_by_security: Mapping[str, Decimal]
    sector_total: Mapping[str, Decimal]
    theme_total: Mapping[str, Decimal]
    baseline_total: Decimal
    unpriced: bool


def _rounded_score(value: Decimal) -> Decimal:
    return value.quantize(SCORE_QUANTUM, rounding=ROUND_HALF_EVEN)


def _money(value: Decimal) -> Decimal:
    if value <= 0:
        return Decimal("0")
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_DOWN)


def _percentage(value: Decimal, equity: Decimal) -> Decimal:
    if equity <= 0:
        return Decimal("0")
    return _rounded_score(value / equity * ONE_HUNDRED)


def score_assessment(
    assessment: Mapping[str, object], cash_hurdle_score: Decimal
) -> AssessmentScore:
    """Calculate weighted, confidence-adjusted score and positive cash edge."""

    if not cash_hurdle_score.is_finite() or not Decimal("0") <= cash_hurdle_score <= ONE_HUNDRED:
        raise AllocationError("cash hurdle must be finite and within 0-100")
    if assessment.get("assessment_schema_version") == "2":
        quality = required_decimal(assessment["quality_score"], label="quality_score")  # type: ignore[arg-type]
        if not Decimal("0") <= quality <= ONE_HUNDRED:
            raise AllocationError("quality_score must be within 0-100")
        rounded_quality = _rounded_score(quality)
        return AssessmentScore(
            rounded_quality,
            rounded_quality,
            _rounded_score(max(rounded_quality - cash_hurdle_score, Decimal("0"))),
        )
    raw = Decimal("0")
    for field, weight in SCORE_WEIGHTS.items():
        value = required_decimal(assessment[field], label=field)  # type: ignore[arg-type]
        if value != value.to_integral_value() or not Decimal("0") <= value <= ONE_HUNDRED:
            raise AllocationError(f"{field} must be an integer score within 0-100")
        raw += value * weight
    confidence = assessment.get("confidence")
    if not isinstance(confidence, str) or confidence not in CONFIDENCE_MULTIPLIERS:
        raise AllocationError("assessment confidence is not canonical")
    penalty = required_decimal(assessment["risk_penalty"], label="risk_penalty")  # type: ignore[arg-type]
    if penalty != penalty.to_integral_value() or not Decimal("0") <= penalty <= ONE_HUNDRED:
        raise AllocationError("risk_penalty must be an integer score within 0-100")
    rounded_raw = _rounded_score(raw)
    effective = _rounded_score(raw * CONFIDENCE_MULTIPLIERS[confidence] - penalty)
    edge = _rounded_score(max(effective - cash_hurdle_score, Decimal("0")))
    return AssessmentScore(rounded_raw, effective, edge)


def assessment_payoff_reasons(assessment: Mapping[str, str], settings: Settings) -> tuple[str, ...]:
    """Return deterministic long-baseline payoff gate failures."""

    if assessment.get("assessment_schema_version") == "2":
        return tuple(
            reason
            for reason in assessment["eligibility_reason_codes"].split("|")
            if reason
            and reason != "relationship_pending"
            and not reason.startswith("hard_blocker:")
        )

    base_upside = required_decimal(assessment["base_upside_pct"], label="base_upside_pct")
    downside = required_decimal(assessment["downside_pct"], label="downside_pct")
    reasons: list[str] = []
    if base_upside <= 0:
        reasons.append("base_upside_not_positive")
    elif base_upside < settings.allocation.minimum_base_upside_pct:
        reasons.append("base_upside_below_minimum")
    downside_risk = max(-downside, Decimal("0"))
    if (
        downside_risk > 0
        and base_upside / downside_risk < settings.allocation.minimum_upside_downside_ratio
    ):
        reasons.append("upside_downside_ratio_below_minimum")
    return tuple(reasons)


def calculate_assessment_score(
    assessment: Mapping[str, object], cash_hurdle_score: Decimal
) -> AssessmentScore:
    """Compatibility name for callers that describe the score as an aggregate."""

    return score_assessment(assessment, cash_hurdle_score)


def _calibration_assessment(
    name: str,
    *,
    expected: str,
    base: str,
    bear: str,
    margin: str,
    confidence: str = "medium",
    completeness: str = "complete",
    supported: str = "true",
    blockers: str = "",
) -> dict[str, str]:
    scores = {
        "clearly_attractive": "80",
        "fair": "60",
        "unattractive": "40",
        "distressed": "40",
        "incomplete": "60",
        "illiquid": "60",
    }
    score = scores[name]
    return {
        "assessment_schema_version": "2",
        "confidence": confidence,
        "thesis_score": score,
        "business_quality_score": score,
        "balance_sheet_score": score,
        "liquidity_score": score,
        "risk_penalty": "40",
        "valuation_supported": supported,
        "research_completeness": completeness,
        "expected_return_pct": expected,
        "confidence_adjusted_expected_return_pct": expected,
        "base_return_pct": base,
        "bear_return_pct": bear,
        "margin_of_safety_pct": margin,
        "hard_blockers": blockers,
    }


def write_calibration_report(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
) -> Path:
    """Write fixed-fixture and maintained-universe old/new decision comparisons."""

    if not SAFE_RUN_ID.fullmatch(run_id):
        raise AllocationError("calibration run_id is unsafe")
    from papertrader.valuation import derive_assessment_dimensions

    fixtures = {
        "clearly_attractive": _calibration_assessment(
            "clearly_attractive", expected="24", base="30", bear="-12", margin="20"
        ),
        "fair": _calibration_assessment("fair", expected="7", base="10", bear="-15", margin="0"),
        "unattractive": _calibration_assessment(
            "unattractive", expected="-5", base="0", bear="-30", margin="-20"
        ),
        "distressed": _calibration_assessment(
            "distressed",
            expected="30",
            base="50",
            bear="-80",
            margin="25",
            blockers="solvency_risk",
        ),
        "incomplete": _calibration_assessment(
            "incomplete",
            expected="0",
            base="0",
            bear="0",
            margin="0",
            completeness="partial",
            supported="false",
        ),
        "illiquid": _calibration_assessment(
            "illiquid",
            expected="25",
            base="35",
            bear="-15",
            margin="25",
            blockers="liquidity_insufficient",
        ),
    }
    fixture_results = {
        name: derive_assessment_dimensions(
            assessment,
            settings,
            relationship_accepted=True,
        )
        for name, assessment in fixtures.items()
    }
    relationships = {
        row["security_id"]
        for row in read_table(repository_root, "relationships")
        if row["status"] == "accepted"
    }
    universe: list[dict[str, object]] = []
    for assessment in read_table(repository_root, "security_assessments"):
        score = score_assessment(assessment, settings.allocation.cash_hurdle_score)
        new_dimensions = (
            derive_assessment_dimensions(
                assessment,
                settings,
                relationship_accepted=assessment["security_id"] in relationships,
            )
            if assessment.get("assessment_schema_version") == "2"
            else None
        )
        universe.append(
            {
                "security_id": assessment["security_id"],
                "assessment_schema_version": assessment.get("assessment_schema_version", "")
                or "legacy_v1",
                "old": {
                    "eligibility": assessment["eligibility"],
                    "effective_score": decimal_text(score.effective_score),
                    "candidate_edge": decimal_text(score.candidate_edge),
                },
                "new": new_dimensions,
            }
        )
    document = {
        "version": 1,
        "run_id": run_id,
        "thresholds": {
            "minimum_confidence_adjusted_expected_return_pct": decimal_text(
                settings.allocation.minimum_confidence_adjusted_expected_return_pct
            ),
            "minimum_base_return_pct": decimal_text(settings.allocation.minimum_base_upside_pct),
            "minimum_bear_base_payoff_ratio": decimal_text(
                settings.allocation.minimum_upside_downside_ratio
            ),
            "minimum_expected_bear_payoff_ratio": decimal_text(
                settings.allocation.minimum_expected_bear_payoff_ratio
            ),
            "minimum_margin_of_safety_pct": decimal_text(
                settings.allocation.minimum_margin_of_safety_pct
            ),
            "minimum_confidence": settings.allocation.minimum_confidence,
        },
        "fixtures": fixture_results,
        "maintained_universe": universe,
    }
    path = repository_root / "data" / "runs" / run_id / "allocation_calibration.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, document, allowed_root=repository_root)
    return path


def baseline_strategy_id(security_id: str) -> str:
    """Return the stable one-baseline-strategy identity for a security."""

    if not security_id or any(marker in security_id for marker in "|\r\n"):
        raise AllocationError("security_id is not safe for baseline strategy identity")
    return stable_id("strategy", "baseline", security_id)


def _researched_securities(repository_root: Path) -> tuple[Mapping[str, str], ...]:
    """Return the maintained universe: canonical securities with a research page."""

    return tuple(
        sorted(
            (row for row in read_table(repository_root, "securities") if row["research_page"]),
            key=lambda row: row["security_id"],
        )
    )


def _canonical_idea_links(repository_root: Path, security: Mapping[str, str]) -> tuple[str, ...]:
    """Extract only exact canonical idea wikilinks from one maintained security page."""

    relative = PurePosixPath(security["research_page"])
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or len(relative.parts) != 4
        or relative.parts[:3] != ("data", "wiki", "securities")
        or relative.suffix != ".md"
    ):
        raise AllocationError(
            f"researched security has invalid research_page: {security['security_id']}"
        )
    page = repository_root.joinpath(*relative.parts)
    if page.is_symlink() or not page.is_file():
        raise AllocationError(f"researched security page is unavailable: {security['security_id']}")
    idea_ids = tuple(sorted(set(CANONICAL_IDEA_LINK.findall(page.read_text(encoding="utf-8")))))
    for idea_id in idea_ids:
        idea_page = repository_root / "data" / "wiki" / "ideas" / f"{idea_id}.md"
        if idea_page.is_symlink() or not idea_page.is_file():
            raise AllocationError(
                f"security {security['security_id']} links missing canonical idea {idea_id}"
            )
    return idea_ids


def _assessment_readiness_errors(
    assessment: Mapping[str, str],
    sources: Mapping[str, Mapping[str, str]],
    settings: Settings,
    *,
    now: datetime,
) -> tuple[str, ...]:
    """Return current-assessment and registered-evidence errors at one instant."""

    security_id = assessment["security_id"]
    errors: list[str] = []
    try:
        assessed = parse_timestamp(assessment["assessed_at"])
        expires = parse_timestamp(assessment["expires_at"])
        assert assessed is not None and expires is not None
        maximum_age = timedelta(days=settings.allocation.maximum_assessment_age_days)
        if assessed > now or now - assessed > maximum_age or expires <= now:
            errors.append(f"assessment_stale:{security_id}")
        evidence = tuple(part for part in assessment["evidence_refs"].split("|") if part)
        if not evidence or evidence != tuple(sorted(set(evidence))):
            errors.append(f"assessment_evidence_invalid:{security_id}")
        for source_id in evidence:
            source = sources.get(source_id)
            if source is None:
                errors.append(f"assessment_evidence_unregistered:{security_id}:{source_id}")
                continue
            checked = parse_timestamp(source["last_checked_at"])
            if (
                checked is None
                or checked > now
                or now - checked > maximum_age
                or source["status"] not in CURRENT_SOURCE_STATUSES
            ):
                errors.append(f"assessment_evidence_stale:{security_id}:{source_id}")
    except (CanonicalValueError, KeyError, TypeError):
        errors.append(f"assessment_invalid:{security_id}")
    return tuple(sorted(set(errors)))


def _relationship_is_current(row: Mapping[str, str], now: datetime) -> bool:
    try:
        reviewed = parse_timestamp(row["last_reviewed_at"])
        next_review = parse_timestamp(row["next_review_at"])
    except (CanonicalValueError, KeyError):
        return False
    return bool(
        reviewed is not None
        and next_review is not None
        and reviewed <= now
        and next_review > now
        and row["status"] in {"accepted", "rejected"}
    )


def maintain_allocation_research(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    backfill: bool = False,
    now: datetime | None = None,
) -> AllocationMaintenanceResult:
    """Enqueue missing or near-expiry assessment and canonical relationship work."""

    if not SAFE_RUN_ID.fullmatch(run_id):
        raise AllocationError(f"invalid allocation maintenance run_id: {run_id!r}")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    reviewer = _AllocationMaintenanceOverlapReviewer()
    # Two passes resolve a relationship whose duplicate security dependency is
    # terminalized during the first pass. Queue triage preserves each merged
    # request in terminal history with its target operation ID.
    prepare_queue(repository_root, now=instant, semantic_reviewer=reviewer)
    prepare_queue(repository_root, now=instant, semantic_reviewer=reviewer)
    lead = timedelta(days=settings.allocation.research_refresh_lead_days)
    researched = _researched_securities(repository_root)
    assessments = {
        row["security_id"]: row for row in read_table(repository_root, "security_assessments")
    }
    sources = {row["source_id"]: row for row in read_table(repository_root, "source_registry")}
    relationship_rows = read_table(repository_root, "relationships")
    by_pair: defaultdict[tuple[str, str], list[Mapping[str, str]]] = defaultdict(list)
    for row in relationship_rows:
        by_pair[(row["idea_id"], row["security_id"])].append(row)
    source = ALLOCATION_BACKFILL_SOURCE if backfill else ALLOCATION_MAINTENANCE_SOURCE
    active_maintenance = {
        (row["operation_type"], row["entity_id"]): row["operation_id"]
        for row in read_table(repository_root, "operations_todo")
        if row["source"] in ALLOCATION_MAINTENANCE_SOURCES
    }
    security_operations: dict[str, str] = {}
    relationship_operations: list[str] = []
    created_ids: list[str] = []
    relationship_pair_count = 0

    for security in researched:
        security_id = security["security_id"]
        assessment = assessments.get(security_id)
        refresh = backfill or assessment is None
        assessment_marker = "missing"
        if assessment is not None:
            assessment_marker = assessment["assessed_at"]
            try:
                assessed = parse_timestamp(assessment["assessed_at"])
                expires = parse_timestamp(assessment["expires_at"])
                assert assessed is not None and expires is not None
                effective_expiry = min(
                    expires,
                    assessed + timedelta(days=settings.allocation.maximum_assessment_age_days),
                )
                for source_id in (part for part in assessment["evidence_refs"].split("|") if part):
                    source_row = sources.get(source_id)
                    if source_row is None:
                        refresh = True
                        continue
                    checked = parse_timestamp(source_row["last_checked_at"])
                    if checked is None or source_row["status"] not in CURRENT_SOURCE_STATUSES:
                        refresh = True
                        continue
                    effective_expiry = min(
                        effective_expiry,
                        checked + timedelta(days=settings.allocation.maximum_assessment_age_days),
                    )
                refresh = refresh or effective_expiry <= instant + lead
            except (CanonicalValueError, KeyError):
                refresh = True
        if refresh:
            cycle = "backfill-v1" if backfill else assessment_marker
            operation_id = active_maintenance.get(("security_research", security_id), "")
            created = False
            if not operation_id:
                operation_id, created = enqueue_operation(
                    repository_root,
                    settings,
                    operation_type="security_research",
                    entity_type="security",
                    entity_id=security_id,
                    dedupe_key=f"security_research:{security_id}:allocation-maintenance:{cycle}",
                    prompt=(
                        f"Revalidate {security_id} with current primary evidence and write one "
                        "comparable allocation assessment."
                    ),
                    inputs={
                        "security_id": security_id,
                        "maintenance_mode": "backfill" if backfill else "refresh",
                        "assessment_state": assessment_marker,
                        "research_page": security["research_page"],
                    },
                    source=source,
                    priority=75 if backfill else 65,
                    freshness_days=0,
                    source_refs=(
                        tuple(part for part in assessment["evidence_refs"].split("|") if part)
                        if assessment is not None
                        else ()
                    ),
                    now=instant,
                )
                active_maintenance[("security_research", security_id)] = operation_id
            security_operations[security_id] = operation_id
            if created:
                created_ids.append(operation_id)

        for idea_id in _canonical_idea_links(repository_root, security):
            relationship_pair_count += 1
            matches = sorted(
                by_pair.get((idea_id, security_id), ()), key=lambda row: row["relationship_id"]
            )
            if len(matches) > 1:
                raise AllocationError(
                    f"multiple relationships exist for canonical pair {idea_id}:{security_id}"
                )
            relationship = matches[0] if matches else None
            review = backfill or relationship is None
            relationship_marker = "missing"
            if relationship is not None:
                relationship_marker = relationship["last_reviewed_at"] or "unreviewed"
                review = review or not _relationship_is_current(relationship, instant)
                try:
                    next_review = parse_timestamp(relationship["next_review_at"], allow_empty=True)
                    review = review or next_review is None or next_review <= instant + lead
                except CanonicalValueError:
                    review = True
            if not review:
                continue
            relationship_id = (
                relationship["relationship_id"]
                if relationship is not None
                else stable_id("relationship", idea_id, security_id)
            )
            cycle = "backfill-v1" if backfill else relationship_marker
            dependency = security_operations.get(security_id)
            operation_id = active_maintenance.get(("relationship_research", relationship_id), "")
            created = False
            if not operation_id:
                operation_id, created = enqueue_operation(
                    repository_root,
                    settings,
                    operation_type="relationship_research",
                    entity_type="relationship",
                    entity_id=relationship_id,
                    dedupe_key=(
                        f"relationship_research:{relationship_id}:allocation-maintenance:{cycle}"
                    ),
                    prompt=(
                        f"Review the canonical relationship from {idea_id} to {security_id} and "
                        "accept or reject it with current evidence."
                    ),
                    inputs={
                        "relationship_id": relationship_id,
                        "idea_id": idea_id,
                        "security_id": security_id,
                        "maintenance_mode": "backfill" if backfill else "refresh",
                    },
                    source=source,
                    priority=70 if backfill else 60,
                    freshness_days=0,
                    depends_on=(dependency,) if dependency else (),
                    source_refs=(
                        tuple(part for part in assessment["evidence_refs"].split("|") if part)
                        if assessment is not None
                        else ()
                    ),
                    now=instant,
                )
                active_maintenance[("relationship_research", relationship_id)] = operation_id
            relationship_operations.append(operation_id)
            if created:
                created_ids.append(operation_id)

    return AllocationMaintenanceResult(
        run_id=run_id,
        as_of=format_timestamp(instant),
        backfill=backfill,
        researched_security_count=len(researched),
        relationship_pair_count=relationship_pair_count,
        security_operations=tuple(sorted(security_operations.values())),
        relationship_operations=tuple(sorted(set(relationship_operations))),
        operations_created=tuple(sorted(created_ids)),
    )


def allocation_readiness(
    repository_root: Path,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> AllocationReadinessResult:
    """Report whether the maintained universe satisfies activation invariants."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    researched = _researched_securities(repository_root)
    assessments = {
        row["security_id"]: row for row in read_table(repository_root, "security_assessments")
    }
    sources = {row["source_id"]: row for row in read_table(repository_root, "source_registry")}
    relationship_rows = read_table(repository_root, "relationships")
    by_pair: defaultdict[tuple[str, str], list[Mapping[str, str]]] = defaultdict(list)
    for row in relationship_rows:
        by_pair[(row["idea_id"], row["security_id"])].append(row)
    errors: list[str] = []
    current_assessments = 0
    fresh_evidence = 0
    current_relationships = 0
    relationship_pairs = 0

    for security in researched:
        security_id = security["security_id"]
        assessment = assessments.get(security_id)
        assessment_errors: tuple[str, ...] = ()
        if assessment is None:
            errors.append(f"assessment_missing:{security_id}")
        else:
            assessment_errors = _assessment_readiness_errors(
                assessment, sources, settings, now=instant
            )
            errors.extend(assessment_errors)
            if not any(
                error.startswith(("assessment_stale:", "assessment_invalid:"))
                for error in assessment_errors
            ):
                current_assessments += 1
            if not assessment_errors:
                fresh_evidence += 1

        accepted_current = False
        for idea_id in _canonical_idea_links(repository_root, security):
            relationship_pairs += 1
            matches = sorted(
                by_pair.get((idea_id, security_id), ()), key=lambda row: row["relationship_id"]
            )
            if len(matches) != 1:
                errors.append(f"relationship_missing_or_ambiguous:{idea_id}:{security_id}")
                continue
            relationship = matches[0]
            if not _relationship_is_current(relationship, instant):
                errors.append(f"relationship_stale:{relationship['relationship_id']}")
                continue
            current_relationships += 1
            accepted_current = accepted_current or relationship["status"] == "accepted"
            if relationship["status"] == "rejected" and assessment is not None:
                reviewed = parse_timestamp(relationship["last_reviewed_at"])
                assessed = parse_timestamp(assessment["assessed_at"])
                assert reviewed is not None and assessed is not None
                if assessment["eligibility"] != "ineligible" or assessed < reviewed:
                    errors.append(
                        f"rejected_relationship_unreconciled:{relationship['relationship_id']}"
                    )
        if (
            assessment is not None
            and assessment["eligibility"] in ELIGIBLE_ASSESSMENTS
            and not accepted_current
        ):
            errors.append(f"eligible_assessment_lacks_relationship:{security_id}")

    backfill_active = [
        row
        for row in read_table(repository_root, "operations_todo")
        if row["source"] == ALLOCATION_BACKFILL_SOURCE
    ]
    errors.extend(
        f"backfill_operation_active:{row['operation_id']}:{row['status']}"
        for row in backfill_active
    )
    latest_backfill: dict[tuple[str, str], Mapping[str, str]] = {}
    for row in read_table(repository_root, "operations_history"):
        if row["source"] != ALLOCATION_BACKFILL_SOURCE:
            continue
        key = (row["operation_type"], row["entity_id"])
        previous = latest_backfill.get(key)
        if previous is None or (row["completed_at"], row["operation_id"]) > (
            previous["completed_at"],
            previous["operation_id"],
        ):
            latest_backfill[key] = row
    errors.extend(
        f"backfill_operation_failed:{row['operation_id']}"
        for row in latest_backfill.values()
        if row["terminal_status"] == "failed"
    )
    canonical_errors = tuple(sorted(set(errors)))
    return AllocationReadinessResult(
        as_of=format_timestamp(instant),
        ready=not canonical_errors,
        researched_security_count=len(researched),
        current_assessment_count=current_assessments,
        fresh_evidence_assessment_count=fresh_evidence,
        relationship_pair_count=relationship_pairs,
        current_relationship_pair_count=current_relationships,
        errors=canonical_errors,
    )


def _current_relationships(
    repository_root: Path, now: datetime
) -> tuple[dict[str, tuple[Mapping[str, str], ...]], dict[str, str]]:
    by_security: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    relationship_by_id: dict[str, str] = {}
    for row in read_table(repository_root, "relationships"):
        if row["status"] != "accepted":
            continue
        reviewed = parse_timestamp(row["last_reviewed_at"], allow_empty=True)
        next_review = parse_timestamp(row["next_review_at"], allow_empty=True)
        if reviewed is None or next_review is None or reviewed > now or next_review <= now:
            continue
        by_security[row["security_id"]].append(row)
        relationship_by_id[row["relationship_id"]] = row["idea_id"]
    return (
        {
            security_id: tuple(sorted(rows, key=lambda row: row["relationship_id"]))
            for security_id, rows in by_security.items()
        },
        relationship_by_id,
    )


def _themes_for_security(
    security_id: str,
    relationships: Mapping[str, Sequence[Mapping[str, str]]],
) -> tuple[str, ...]:
    return tuple(sorted({row["idea_id"] for row in relationships.get(security_id, ())}))


def _diversification_component_count(candidates: Sequence[_Candidate]) -> int:
    """Count connected candidates, treating every shared accepted idea as one component."""

    remaining = {candidate.security_id: candidate for candidate in candidates}
    components = 0
    while remaining:
        components += 1
        seed_id = min(remaining)
        stack = [remaining.pop(seed_id)]
        themes: set[str] = set()
        while stack:
            current = stack.pop()
            themes.update(current.themes)
            connected = [
                security_id
                for security_id, candidate in remaining.items()
                if themes.intersection(candidate.themes)
            ]
            for security_id in connected:
                stack.append(remaining.pop(security_id))
    return components


def _strategy_sleeves(repository_root: Path) -> dict[str, str]:
    sleeves: dict[str, str] = {}
    for row in read_table(repository_root, "strategies"):
        sleeve = row["sleeve"]
        if sleeve not in {"conviction", "baseline"}:
            raise AllocationError(f"strategy {row['strategy_id']} has invalid sleeve {sleeve!r}")
        sleeves[row["strategy_id"]] = sleeve
    return sleeves


def _portfolio_exposure(
    repository_root: Path,
    securities: Mapping[str, Mapping[str, str]],
    relationships: Mapping[str, Sequence[Mapping[str, str]]],
    strategy_sleeves: Mapping[str, str],
) -> _PortfolioExposure:
    current_total: defaultdict[str, Decimal] = defaultdict(Decimal)
    current_baseline: defaultdict[str, Decimal] = defaultdict(Decimal)
    current_conviction: defaultdict[str, Decimal] = defaultdict(Decimal)
    sector_total: defaultdict[str, Decimal] = defaultdict(Decimal)
    theme_total: defaultdict[str, Decimal] = defaultdict(Decimal)
    for row in read_table(repository_root, "portfolio"):
        security_id = row["security_id"]
        value = abs(required_decimal(row["market_value_base"], label="portfolio market value"))
        current_total[security_id] += value
        security = securities.get(security_id)
        if security is not None:
            sector_total[security["sector"] or "unclassified"] += value
        for theme in _themes_for_security(security_id, relationships):
            theme_total[theme] += value
        strategy_ids = tuple(part for part in row["strategy_ids"].split("|") if part)
        exclusively_baseline = bool(strategy_ids) and all(
            strategy_sleeves.get(strategy_id) == "baseline" for strategy_id in strategy_ids
        )
        if exclusively_baseline:
            current_baseline[security_id] += value
        else:
            current_conviction[security_id] += value
    baseline_total = sum(current_baseline.values(), Decimal("0"))
    conviction_total = sum(current_conviction.values(), Decimal("0"))
    return _PortfolioExposure(
        current_total=dict(current_total),
        current_baseline=dict(current_baseline),
        current_conviction=dict(current_conviction),
        sector_total=dict(sector_total),
        theme_total=dict(theme_total),
        baseline_total=baseline_total,
        conviction_total=conviction_total,
        gross_total=sum(current_total.values(), Decimal("0")),
    )


def _fresh_price_and_fx(
    repository_root: Path,
    settings: Settings,
    security: Mapping[str, str],
    *,
    now: datetime,
) -> tuple[Decimal, Decimal, datetime]:
    latest_rows = {row["security_id"]: row for row in read_table(repository_root, "market_latest")}
    latest = latest_rows.get(security["security_id"])
    if latest is None:
        raise AllocationError("market_data_missing")
    if (
        latest["provider_symbol"] != security["provider_symbol"]
        or latest["currency"] != security["currency"]
    ):
        raise AllocationError("market_data_identity_mismatch")
    if latest["status"] != "ok":
        raise AllocationError("market_data_not_ok")
    observed = parse_timestamp(latest["retrieved_at"])
    assert observed is not None
    age = now - observed
    if age < timedelta(0) or age > settings.market_data.stale_price_after:
        raise AllocationError("market_data_stale")
    raw_price = latest["adjusted_close"] or latest["close"]
    price = required_decimal(raw_price, label="allocation valuation mark")
    if price <= 0:
        raise AllocationError("market_data_invalid")
    try:
        fx_rate = latest_fx_rate(
            repository_root,
            security["currency"],
            settings.portfolio.base_currency,
            now=now,
            maximum_age=settings.market_data.stale_price_after,
        )
    except MarketDataError as exc:
        raise AllocationError("fx_unavailable") from exc
    return price, fx_rate, observed


def _candidate(
    repository_root: Path,
    settings: Settings,
    security: Mapping[str, str],
    assessment: Mapping[str, str] | None,
    assessment_id: str,
    relationships: Mapping[str, Sequence[Mapping[str, str]]],
    sources: Mapping[str, Mapping[str, str]],
    *,
    now: datetime,
) -> _Candidate:
    reasons: list[str] = []
    tier = "watch"
    live_valuation: Mapping[str, str] = {}
    if assessment is None:
        score = AssessmentScore(Decimal("0"), Decimal("0"), Decimal("0"))
        reasons.append("assessment_missing")
        assessed_at = None
    else:
        try:
            score = score_assessment(assessment, settings.allocation.minimum_quality_score)
        except (AllocationError, CanonicalValueError, KeyError) as exc:
            raise AllocationError(
                f"invalid assessment for {security['security_id']}: {exc}"
            ) from exc
        assessed_at = parse_timestamp(assessment["assessed_at"])
        expires_at = parse_timestamp(assessment["expires_at"])
        assert assessed_at is not None and expires_at is not None
        is_v2 = assessment.get("assessment_schema_version") == "2"
        if not is_v2 and assessment["eligibility"] not in ELIGIBLE_ASSESSMENTS:
            reasons.append("assessment_ineligible")
        age = now - assessed_at
        if (
            age < timedelta(0)
            or age > timedelta(days=settings.allocation.maximum_assessment_age_days)
            or expires_at <= now
        ):
            reasons.append("assessment_stale")
        confidence = assessment["confidence"]
        if not is_v2 and (
            confidence not in CONFIDENCE_RANK
            or CONFIDENCE_RANK[confidence] < CONFIDENCE_RANK[settings.allocation.minimum_confidence]
        ):
            reasons.append("confidence_below_minimum")
        blockers = tuple(part for part in assessment["hard_blockers"].split("|") if part)
        if blockers:
            reasons.append(f"hard_blocker:{','.join(blockers)}")
        if not is_v2 and score.candidate_edge <= 0:
            reasons.append("score_below_cash_hurdle")
    if security["status"] not in ELIGIBLE_SECURITY_STATUSES:
        reasons.append("security_status_not_orderable")
    if security["instrument_type"] != "equity":
        reasons.append("instrument_unsupported")
    if security["instrument_type"] not in settings.risk.allowed_instruments:
        reasons.append("instrument_not_allowed")
    if security["venue_mic"] not in settings.risk.allowed_exchanges:
        reasons.append("exchange_not_allowed")
    if security["currency"] not in settings.risk.allowed_currencies:
        reasons.append("currency_not_allowed")
    current_relationships = relationships.get(security["security_id"], ())
    if not current_relationships:
        reasons.append("relationship_missing_or_stale")
    price: Decimal | None = None
    price_as_of: datetime | None = None
    fx_rate: Decimal | None = None
    try:
        price, fx_rate, price_as_of = _fresh_price_and_fx(
            repository_root,
            settings,
            security,
            now=now,
        )
    except AllocationError as exc:
        reasons.append(str(exc))
    if assessment is not None and assessment.get("assessment_schema_version") == "2" and price:
        from papertrader.valuation import ValuationError, live_valuation_projection

        evidence_fresh = not _assessment_readiness_errors(assessment, sources, settings, now=now)
        try:
            live_valuation = live_valuation_projection(
                repository_root,
                settings,
                security,
                assessment,
                now=now,
                relationship_accepted=bool(current_relationships),
                evidence_fresh=evidence_fresh,
            )
        except (ValuationError, CanonicalValueError) as exc:
            reasons.append(str(exc))
        else:
            tier = live_valuation["tier"]
            reasons.extend(
                part for part in live_valuation["eligibility_reason_codes"].split("|") if part
            )
    if (
        assessment is not None
        and assessment.get("assessment_schema_version") != "2"
        and not reasons
    ):
        tier = "full"
        live_valuation = {
            "position_cap_pct": decimal_text(settings.allocation.maximum_baseline_position_pct)
        }
    return _Candidate(
        security_id=security["security_id"],
        security=security,
        assessment=assessment,
        relationship_id=(
            current_relationships[0]["relationship_id"] if current_relationships else ""
        ),
        themes=_themes_for_security(security["security_id"], relationships),
        assessment_id=assessment_id,
        tier=tier,
        live_valuation=live_valuation,
        score=score,
        price=price,
        price_as_of=price_as_of,
        fx_rate=fx_rate,
        assessment_at=assessed_at,
        eligible=(tier in {"full", "starter"} if assessment and is_v2 else not reasons),
        reasons=sorted(set(reasons)),
    )


def _pending_exposure(
    repository_root: Path,
    settings: Settings,
    securities: Mapping[str, Mapping[str, str]],
    relationships: Mapping[str, Sequence[Mapping[str, str]]],
    strategy_sleeves: Mapping[str, str],
    *,
    now: datetime,
) -> _PendingExposure:
    orders = {
        row["order_id"]: row
        for row in read_table(repository_root, "orders")
        if row["status"] in {"pending", "partially_filled"}
    }
    executed: defaultdict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for row in read_table(repository_root, "executions"):
        if row["order_id"] in orders:
            executed[(row["order_id"], row["leg_id"])] += required_decimal(
                row["quantity"], label="executed pending quantity"
            )
    gross = Decimal("0")
    committed_cash = Decimal("0")
    total_by_security: defaultdict[str, Decimal] = defaultdict(Decimal)
    baseline_by_security: defaultdict[str, Decimal] = defaultdict(Decimal)
    conviction_by_security: defaultdict[str, Decimal] = defaultdict(Decimal)
    sector_total: defaultdict[str, Decimal] = defaultdict(Decimal)
    theme_total: defaultdict[str, Decimal] = defaultdict(Decimal)
    baseline_total = Decimal("0")
    unpriced = False
    charged_orders: set[str] = set()
    for row in sorted(
        (row for row in read_table(repository_root, "order_legs") if row["order_id"] in orders),
        key=lambda row: (row["order_id"], row["leg_id"]),
    ):
        order = orders[row["order_id"]]
        quantity = (
            required_decimal(row["quantity"], label="pending quantity")
            - executed[(row["order_id"], row["leg_id"])]
        )
        if quantity <= 0:
            continue
        multiplier = required_decimal(row["contract_multiplier"], label="pending multiplier")
        security = securities.get(row["security_id"])
        if security is None:
            unpriced = True
            continue
        price: Decimal | None = None
        fx_rate: Decimal | None = None
        if row["instrument_type"] == "equity":
            try:
                price, fx_rate, _ = _fresh_price_and_fx(
                    repository_root, settings, security, now=now
                )
            except AllocationError:
                unpriced = True
        else:
            raw_limit = row["limit_price"] or order["limit_price"]
            if raw_limit:
                price = required_decimal(raw_limit, label="pending option limit")
                try:
                    fx_rate = latest_fx_rate(
                        repository_root,
                        row["currency"],
                        settings.portfolio.base_currency,
                        now=now,
                        maximum_age=settings.market_data.stale_price_after,
                    )
                except MarketDataError:
                    unpriced = True
            else:
                unpriced = True
        if price is None or fx_rate is None:
            continue
        value = quantity * multiplier * price * fx_rate
        sleeve = strategy_sleeves.get(order["strategy_id"], "conviction")
        opening = (row["side"] == "long" and row["action"] == "buy") or (
            row["side"] == "short" and row["action"] == "sell"
        )
        signed = abs(value) if opening else -abs(value)
        gross += signed
        total_by_security[row["security_id"]] += signed
        sector_total[security["sector"] or "unclassified"] += signed
        for theme in _themes_for_security(row["security_id"], relationships):
            theme_total[theme] += signed
        if sleeve == "baseline":
            baseline_by_security[row["security_id"]] += signed
            baseline_total += signed
        else:
            conviction_by_security[row["security_id"]] += signed
        if row["action"] == "buy":
            committed_cash += value
        if row["order_id"] not in charged_orders:
            charged_orders.add(row["order_id"])
            committed_cash += settings.orders.fixed_fee
        committed_cash += abs(value) * settings.orders.variable_fee_bps / Decimal("10000")
    return _PendingExposure(
        gross_total=gross,
        committed_cash=committed_cash,
        total_by_security=dict(total_by_security),
        baseline_by_security=dict(baseline_by_security),
        conviction_by_security=dict(conviction_by_security),
        sector_total=dict(sector_total),
        theme_total=dict(theme_total),
        baseline_total=baseline_total,
        unpriced=unpriced,
    )


def _candidate_capacity(
    candidate: _Candidate,
    settings: Settings,
    equity: Decimal,
    portfolio: _PortfolioExposure,
    pending: _PendingExposure,
    sector_used: Mapping[str, Decimal],
    theme_used: Mapping[str, Decimal],
) -> Decimal:
    security_id = candidate.security_id
    current_baseline = portfolio.current_baseline.get(security_id, Decimal("0"))
    pending_baseline = pending.baseline_by_security.get(security_id, Decimal("0"))
    position_cap_pct = (
        settings.allocation.maximum_starter_position_pct
        if candidate.tier == "starter"
        else settings.allocation.maximum_baseline_position_pct
    )
    baseline_position_room = (
        equity * position_cap_pct / ONE_HUNDRED
        - current_baseline
        - pending_baseline
        - candidate.allocation
    )
    total_security_room = (
        equity * settings.risk.maximum_single_position_pct / ONE_HUNDRED
        - portfolio.current_total.get(security_id, Decimal("0"))
        - pending.total_by_security.get(security_id, Decimal("0"))
        - candidate.allocation
    )
    sector = candidate.security["sector"] or "unclassified"
    sector_room = equity * settings.allocation.maximum_sector_pct / ONE_HUNDRED - sector_used.get(
        sector, Decimal("0")
    )
    rooms = [baseline_position_room, total_security_room, sector_room]
    rooms.extend(
        equity * settings.allocation.maximum_theme_pct / ONE_HUNDRED
        - theme_used.get(theme, Decimal("0"))
        for theme in candidate.themes
    )
    return _money(max(min(rooms), Decimal("0")))


def _allocate_capped(
    candidates: Sequence[_Candidate],
    settings: Settings,
    equity: Decimal,
    budget: Decimal,
    portfolio: _PortfolioExposure,
    pending: _PendingExposure,
) -> Decimal:
    """Apply edge-proportional capped redistribution independent of input order."""

    remaining = _money(budget)
    sector_used: defaultdict[str, Decimal] = defaultdict(Decimal, portfolio.sector_total)
    theme_used: defaultdict[str, Decimal] = defaultdict(Decimal, portfolio.theme_total)
    for key, value in pending.sector_total.items():
        sector_used[key] += value
    for key, value in pending.theme_total.items():
        theme_used[key] += value
    ordered = sorted(candidates, key=lambda item: (-item.score.candidate_edge, item.security_id))
    while remaining >= MONEY_QUANTUM:
        capacities = {
            candidate.security_id: _candidate_capacity(
                candidate,
                settings,
                equity,
                portfolio,
                pending,
                sector_used,
                theme_used,
            )
            for candidate in ordered
        }
        starter_room = max(
            equity * settings.allocation.maximum_starter_sleeve_pct / ONE_HUNDRED
            - sum(
                (candidate.allocation for candidate in ordered if candidate.tier == "starter"),
                Decimal("0"),
            ),
            Decimal("0"),
        )
        starter_capacity = sum(
            (
                value
                for security_id, value in capacities.items()
                if next(
                    candidate for candidate in ordered if candidate.security_id == security_id
                ).tier
                == "starter"
            ),
            Decimal("0"),
        )
        if starter_capacity > starter_room:
            factor = Decimal("0") if starter_capacity == 0 else starter_room / starter_capacity
            for candidate in ordered:
                if candidate.tier == "starter":
                    capacities[candidate.security_id] = _money(
                        capacities[candidate.security_id] * factor
                    )
        active = [
            candidate for candidate in ordered if capacities[candidate.security_id] >= MONEY_QUANTUM
        ]
        if not active:
            break
        edge_total = sum((candidate.score.candidate_edge for candidate in active), Decimal("0"))
        if edge_total <= 0:
            break
        proposals: dict[str, Decimal] = {}
        for candidate in active:
            share = _money(remaining * candidate.score.candidate_edge / edge_total)
            proposals[candidate.security_id] = min(share, capacities[candidate.security_id])
        if not any(value >= MONEY_QUANTUM for value in proposals.values()):
            first = active[0]
            proposals[first.security_id] = min(MONEY_QUANTUM, capacities[first.security_id])
        # Scale simultaneous proposals at shared sector and theme boundaries.
        groups: list[tuple[str, str, Decimal]] = []
        for sector in sorted(
            {candidate.security["sector"] or "unclassified" for candidate in active}
        ):
            room = max(
                equity * settings.allocation.maximum_sector_pct / ONE_HUNDRED - sector_used[sector],
                Decimal("0"),
            )
            groups.append(("sector", sector, room))
        for theme in sorted({theme for candidate in active for theme in candidate.themes}):
            room = max(
                equity * settings.allocation.maximum_theme_pct / ONE_HUNDRED - theme_used[theme],
                Decimal("0"),
            )
            groups.append(("theme", theme, room))
        for kind, group, room in groups:
            members = [
                candidate
                for candidate in active
                if (
                    (kind == "sector" and (candidate.security["sector"] or "unclassified") == group)
                    or (kind == "theme" and group in candidate.themes)
                )
            ]
            proposed = sum(
                (proposals[candidate.security_id] for candidate in members), Decimal("0")
            )
            if proposed <= room or proposed <= 0:
                continue
            factor = room / proposed
            for candidate in members:
                proposals[candidate.security_id] = _money(proposals[candidate.security_id] * factor)
        progress = sum(proposals.values(), Decimal("0"))
        if progress <= 0:
            break
        if progress > remaining:
            raise AllocationError("capped allocation exceeded remaining deployment budget")
        for candidate in active:
            addition = proposals[candidate.security_id]
            candidate.allocation += addition
            sector_used[candidate.security["sector"] or "unclassified"] += addition
            for theme in candidate.themes:
                theme_used[theme] += addition
        remaining = _money(remaining - progress)
    return _money(budget - remaining)


def _cap_final_targets(
    targets: dict[str, Decimal],
    candidates: Mapping[str, _Candidate],
    settings: Settings,
    equity: Decimal,
    portfolio: _PortfolioExposure,
    pending: _PendingExposure,
) -> None:
    """Reduce lowest-ranked baseline targets until every shared cap is satisfied."""

    for security_id in sorted(targets):
        position_cap = (
            settings.allocation.maximum_starter_position_pct
            if candidates[security_id].tier == "starter"
            else settings.allocation.maximum_baseline_position_pct
        )
        baseline_cap = equity * position_cap / ONE_HUNDRED
        fixed_security_exposure = (
            portfolio.current_total.get(security_id, Decimal("0"))
            - portfolio.current_baseline.get(security_id, Decimal("0"))
            + pending.total_by_security.get(security_id, Decimal("0"))
            - pending.baseline_by_security.get(security_id, Decimal("0"))
        )
        total_room = max(
            equity * settings.risk.maximum_single_position_pct / ONE_HUNDRED
            - fixed_security_exposure,
            Decimal("0"),
        )
        targets[security_id] = min(targets[security_id], baseline_cap, total_room)

    def reduce_group(member_ids: Sequence[str], excess: Decimal) -> None:
        for security_id in sorted(
            member_ids,
            key=lambda value: (
                candidates[value].rank if candidates[value].rank else 10**9,
                value,
            ),
            reverse=True,
        ):
            reduction = min(targets[security_id], excess)
            targets[security_id] -= reduction
            excess -= reduction
            if excess <= 0:
                return

    sectors = sorted(
        {candidate.security["sector"] or "unclassified" for candidate in candidates.values()}
    )
    for sector in sectors:
        members = [
            security_id
            for security_id, candidate in candidates.items()
            if (candidate.security["sector"] or "unclassified") == sector
        ]
        current_baseline = sum(
            (portfolio.current_baseline.get(security_id, Decimal("0")) for security_id in members),
            Decimal("0"),
        )
        pending_baseline = sum(
            (
                pending.baseline_by_security.get(security_id, Decimal("0"))
                for security_id in members
            ),
            Decimal("0"),
        )
        fixed_exposure = (
            portfolio.sector_total.get(sector, Decimal("0"))
            + pending.sector_total.get(sector, Decimal("0"))
            - current_baseline
            - pending_baseline
        )
        excess = (
            fixed_exposure
            + sum((targets[value] for value in members), Decimal("0"))
            - (equity * settings.allocation.maximum_sector_pct / ONE_HUNDRED)
        )
        if excess > 0:
            reduce_group(members, excess)
    for theme in sorted({theme for candidate in candidates.values() for theme in candidate.themes}):
        members = [
            security_id
            for security_id, candidate in candidates.items()
            if theme in candidate.themes
        ]
        current_baseline = sum(
            (portfolio.current_baseline.get(security_id, Decimal("0")) for security_id in members),
            Decimal("0"),
        )
        pending_baseline = sum(
            (
                pending.baseline_by_security.get(security_id, Decimal("0"))
                for security_id in members
            ),
            Decimal("0"),
        )
        fixed_exposure = (
            portfolio.theme_total.get(theme, Decimal("0"))
            + pending.theme_total.get(theme, Decimal("0"))
            - current_baseline
            - pending_baseline
        )
        excess = (
            fixed_exposure
            + sum((targets[value] for value in members), Decimal("0"))
            - (equity * settings.allocation.maximum_theme_pct / ONE_HUNDRED)
        )
        if excess > 0:
            reduce_group(members, excess)
    sleeve_excess = sum(targets.values(), Decimal("0")) - (
        equity * settings.allocation.maximum_baseline_sleeve_pct / ONE_HUNDRED
    )
    if sleeve_excess > 0:
        reduce_group(tuple(targets), sleeve_excess)
    starter_ids = tuple(
        security_id for security_id, candidate in candidates.items() if candidate.tier == "starter"
    )
    starter_excess = sum((targets[value] for value in starter_ids), Decimal("0")) - (
        equity * settings.allocation.maximum_starter_sleeve_pct / ONE_HUNDRED
    )
    if starter_excess > 0:
        reduce_group(starter_ids, starter_excess)


def _row_reason(
    candidate: _Candidate,
    *,
    disposition: str,
    diversified: bool,
    deployment_budget: Decimal,
) -> str:
    reasons = list(candidate.reasons)
    if candidate.eligible:
        reasons.append(
            "quality_above_minimum"
            if candidate.assessment and candidate.assessment.get("assessment_schema_version") == "2"
            else "above_cash_hurdle"
        )
        if disposition == "below_minimum_trade":
            reasons.append("minimum_trade_threshold")
        if not diversified:
            reasons.append("insufficient_diversification")
        if candidate.allocation == 0 and disposition in {"hold", "below_minimum_trade"}:
            reasons.append(
                "deployment_budget_exhausted" if deployment_budget == 0 else "concentration_cap"
            )
    return "|".join(sorted(set(reasons))) or "target_unchanged"


def _build_rows(
    candidates: Sequence[_Candidate],
    settings: Settings,
    equity: Decimal,
    portfolio: _PortfolioExposure,
    pending: _PendingExposure,
    *,
    plan_id: str,
    run_id: str,
    as_of: datetime,
    deployment_budget: Decimal,
    diversified: bool,
) -> list[dict[str, str]]:
    by_id = {candidate.security_id: candidate for candidate in candidates}
    targets: dict[str, Decimal] = {}
    for candidate in candidates:
        current = portfolio.current_baseline.get(candidate.security_id, Decimal("0"))
        pending_value = pending.baseline_by_security.get(candidate.security_id, Decimal("0"))
        if not candidate.eligible:
            targets[candidate.security_id] = Decimal("0")
            continue
        desired = max(current + pending_value + candidate.allocation, Decimal("0"))
        unit = candidate.unit_value_base
        if unit is None or unit <= 0:
            targets[candidate.security_id] = Decimal("0")
            continue
        quantity = (desired / unit).to_integral_value(rounding=ROUND_DOWN)
        targets[candidate.security_id] = quantity * unit
    _cap_final_targets(targets, by_id, settings, equity, portfolio, pending)
    rows: list[dict[str, str]] = []
    minimum_trade = equity * settings.allocation.minimum_trade_pct / ONE_HUNDRED
    rebalance_band = settings.allocation.rebalance_band_pct
    for candidate in sorted(candidates, key=lambda item: item.security_id):
        current = portfolio.current_baseline.get(candidate.security_id, Decimal("0"))
        pending_value = pending.baseline_by_security.get(candidate.security_id, Decimal("0"))
        target = max(targets[candidate.security_id], Decimal("0"))
        unit = candidate.unit_value_base
        target_quantity = (
            (target / unit).to_integral_value(rounding=ROUND_DOWN)
            if unit is not None and unit > 0
            else Decimal("0")
        )
        target = target_quantity * unit if unit is not None else Decimal("0")
        delta = target - current - pending_value
        delta_weight = abs(_percentage(delta, equity))
        current_and_pending = current + pending_value
        if not candidate.eligible:
            if current_and_pending <= 0:
                disposition = "excluded"
            else:
                disposition = "close"
                target = Decimal("0")
                delta = -current_and_pending
        elif abs(delta) < MONEY_QUANTUM:
            disposition = "hold"
            target = max(current_and_pending, Decimal("0"))
            delta = Decimal("0")
        elif current_and_pending <= 0 and abs(delta) < minimum_trade:
            disposition = "below_minimum_trade"
            target = Decimal("0")
            delta = Decimal("0")
        elif delta_weight <= rebalance_band:
            disposition = "hold"
            target = max(current_and_pending, Decimal("0"))
            delta = Decimal("0")
        elif abs(delta) < minimum_trade:
            disposition = "below_minimum_trade"
            target = max(current_and_pending, Decimal("0"))
            delta = Decimal("0")
        elif delta > 0:
            disposition = "open" if current_and_pending <= 0 else "increase"
        elif target <= 0:
            disposition = "close"
        else:
            disposition = "reduce"
        target_quantity = (
            (target / unit).to_integral_value(rounding=ROUND_DOWN)
            if unit is not None and unit > 0
            else Decimal("0")
        )
        allocation_intent_id = (
            stable_id(
                "allocation_intent",
                candidate.security_id,
                "long",
                "equity",
                candidate.assessment_id,
                candidate.relationship_id,
                candidate.tier,
                decimal_text(target_quantity),
            )
            if candidate.assessment_id and candidate.relationship_id
            else ""
        )
        rows.append(
            {
                "allocation_plan_id": plan_id,
                "allocation_intent_id": allocation_intent_id,
                "run_id": run_id,
                "as_of": format_timestamp(as_of),
                "security_id": candidate.security_id,
                "strategy_id": baseline_strategy_id(candidate.security_id),
                "sleeve": "baseline",
                "tier": candidate.tier,
                "assessment_id": candidate.assessment_id,
                "relationship_id": candidate.relationship_id,
                "valuation_mark": candidate.live_valuation.get("valuation_mark", ""),
                "valuation_mark_currency": candidate.live_valuation.get(
                    "valuation_mark_currency", ""
                ),
                "valuation_mark_as_of": candidate.live_valuation.get("valuation_mark_as_of", ""),
                "position_cap_pct": candidate.live_valuation.get("position_cap_pct", "0"),
                "target_quantity": decimal_text(target_quantity),
                "bear_return_pct": candidate.live_valuation.get("bear_return_pct", ""),
                "base_return_pct": candidate.live_valuation.get("base_return_pct", ""),
                "bull_return_pct": candidate.live_valuation.get("bull_return_pct", ""),
                "expected_return_pct": candidate.live_valuation.get("expected_return_pct", ""),
                "confidence_adjusted_expected_return_pct": candidate.live_valuation.get(
                    "confidence_adjusted_expected_return_pct", ""
                ),
                "margin_of_safety_pct": candidate.live_valuation.get("margin_of_safety_pct", ""),
                "bear_base_payoff_ratio": candidate.live_valuation.get(
                    "bear_base_payoff_ratio", ""
                ),
                "expected_bear_payoff_ratio": candidate.live_valuation.get(
                    "expected_bear_payoff_ratio", ""
                ),
                "rank": str(candidate.rank) if candidate.rank else "",
                "effective_score": decimal_text(candidate.score.effective_score),
                "candidate_edge": decimal_text(candidate.score.candidate_edge),
                "current_weight_pct": decimal_text(_percentage(current, equity)),
                "pending_weight_pct": decimal_text(_percentage(pending_value, equity)),
                "target_weight_pct": decimal_text(_percentage(target, equity)),
                "target_value_base": decimal_text(target),
                "delta_value_base": decimal_text(delta),
                "disposition": disposition,
                "reason": _row_reason(
                    candidate,
                    disposition=disposition,
                    diversified=diversified,
                    deployment_budget=deployment_budget,
                ),
                "assessment_as_of": (
                    format_timestamp(candidate.assessment_at) if candidate.assessment_at else ""
                ),
            }
        )
    return rows


def _enqueue_targets(
    repository_root: Path,
    settings: Settings,
    candidates: Mapping[str, _Candidate],
    rows: Sequence[Mapping[str, str]],
    *,
    now: datetime,
) -> tuple[str, ...]:
    created_ids: list[str] = []
    strategies = {row["strategy_id"]: row for row in read_table(repository_root, "strategies")}
    for row in sorted(rows, key=lambda value: value["security_id"]):
        if row["disposition"] not in ALLOCATABLE_DISPOSITIONS:
            continue
        if (
            row["disposition"] in {"reduce", "close"}
            and required_decimal(row["current_weight_pct"], label="current allocation weight") <= 0
        ):
            # Cancelling an incompatible unfilled order already reaches zero exposure. A close
            # strategy in this state would be a stale zero-quantity no-op.
            continue
        candidate = candidates[row["security_id"]]
        existing_strategy = strategies.get(row["strategy_id"])
        relationship_id = candidate.relationship_id or (
            existing_strategy["relationship_id"] if existing_strategy is not None else ""
        )
        if not relationship_id or candidate.assessment is None:
            continue
        inputs = {
            "mode": "baseline_allocation",
            "allocation_plan_id": row["allocation_plan_id"],
            "allocation_intent_id": row["allocation_intent_id"],
            "security_id": row["security_id"],
            "strategy_id": row["strategy_id"],
            "relationship_id": relationship_id,
            "tier": row["tier"],
            "assessment_id": row["assessment_id"],
            "target_quantity": row["target_quantity"],
            "position_cap_pct": row["position_cap_pct"],
            "current_weight_pct": row["current_weight_pct"],
            "target_weight_pct": row["target_weight_pct"],
            "maximum_weight_pct": row["position_cap_pct"],
            "selection_rank": int(row["rank"] or "0"),
            "effective_score": row["effective_score"],
            "assessment_as_of": row["assessment_as_of"],
            "disposition": row["disposition"],
        }
        if row["valuation_mark"]:
            inputs["valuation_mark"] = row["valuation_mark"]
        if row["valuation_mark_as_of"]:
            inputs["valuation_mark_as_of"] = row["valuation_mark_as_of"]
        operation_id, created = enqueue_operation(
            repository_root,
            settings,
            operation_type="strategy_research",
            entity_type="strategy",
            entity_id=row["strategy_id"],
            dedupe_key=(
                f"strategy_research:{row['strategy_id']}:"
                f"{row['allocation_intent_id']}:{row['disposition']}"
            ),
            prompt=(
                f"Research the bounded baseline allocation target for {row['security_id']} "
                f"from plan {row['allocation_plan_id']}."
            ),
            inputs=inputs,
            source=f"deterministic-allocation:{row['allocation_plan_id']}",
            priority=99,
            freshness_days=0,
            source_refs=tuple(
                part for part in candidate.assessment["evidence_refs"].split("|") if part
            ),
            now=now,
        )
        if created:
            created_ids.append(operation_id)
    return tuple(sorted(created_ids))


def _cancel_superseded_allocation_state(
    repository_root: Path, rows: Sequence[Mapping[str, str]]
) -> None:
    """Cancel unfilled baseline state only when its economic intent is no longer current."""

    targets = {row["strategy_id"]: row for row in rows}
    strategies = {row["strategy_id"]: row for row in read_table(repository_root, "strategies")}
    signals = read_table(repository_root, "signals")
    cancelled: set[str] = set()
    for signal in signals:
        if signal["status"] not in {"ready", "ordered"}:
            continue
        strategy = strategies.get(signal["strategy_id"])
        if strategy is None or strategy["sleeve"] != "baseline":
            continue
        target = targets.get(signal["strategy_id"])
        compatible = bool(
            target is not None
            and (
                (
                    signal["allocation_intent_id"]
                    and signal["allocation_intent_id"] == target["allocation_intent_id"]
                )
                or (
                    not signal["allocation_intent_id"]
                    and strategy["allocation_plan_id"] == target["allocation_plan_id"]
                )
            )
        )
        if compatible:
            continue
        signal["status"] = "cancelled"
        cancelled.add(signal["signal_id"])
    if not cancelled:
        return
    write_table(repository_root, "signals", signals)
    orders = read_table(repository_root, "orders")
    changed = False
    for order in orders:
        if order["signal_id"] in cancelled and order["status"] in {
            "pending",
            "partially_filled",
        }:
            order["status"] = "cancelled"
            changed = True
    if changed:
        write_table(repository_root, "orders", orders)


def plan_allocation(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    now: datetime | None = None,
) -> AllocationPlanResult:
    """Generate one immutable baseline target plan from authoritative current state."""

    if not SAFE_RUN_ID.fullmatch(run_id):
        raise AllocationError(f"invalid allocation run_id: {run_id!r}")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    reconciliation_errors = reconcile_portfolio(repository_root)
    if reconciliation_errors:
        raise AllocationError(
            "portfolio must reconcile before allocation: " + ";".join(reconciliation_errors)
        )
    replay = replay_accounting(repository_root)
    securities = {row["security_id"]: row for row in read_table(repository_root, "securities")}
    assessments = {
        row["security_id"]: row for row in read_table(repository_root, "security_assessments")
    }
    assessment_ids = {
        row["security_id"]: row["assessment_id"]
        for row in read_table(repository_root, "security_assessment_history")
    }
    sources = {row["source_id"]: row for row in read_table(repository_root, "source_registry")}
    relationships, _ = _current_relationships(repository_root, instant)
    strategy_sleeves = _strategy_sleeves(repository_root)
    portfolio = _portfolio_exposure(
        repository_root,
        securities,
        relationships,
        strategy_sleeves,
    )
    pending = _pending_exposure(
        repository_root,
        settings,
        securities,
        relationships,
        strategy_sleeves,
        now=instant,
    )
    equity = replay.cash_base + sum(
        (
            required_decimal(row["market_value_base"], label="portfolio market value")
            for row in read_table(repository_root, "portfolio")
        ),
        Decimal("0"),
    )
    if equity <= 0:
        raise AllocationError("allocation requires positive reconciled equity")
    researched_ids = {row["security_id"] for row in _researched_securities(repository_root)}
    candidate_ids = (
        researched_ids
        | set(assessments)
        | set(portfolio.current_baseline)
        | set(pending.baseline_by_security)
    )
    unknown = sorted(candidate_ids - set(securities))
    if unknown:
        raise AllocationError(f"allocation state references unknown securities: {unknown}")
    candidates = [
        _candidate(
            repository_root,
            settings,
            securities[security_id],
            assessments.get(security_id),
            assessment_ids.get(security_id, ""),
            relationships,
            sources,
            now=instant,
        )
        for security_id in sorted(candidate_ids)
    ]
    for candidate in candidates:
        if portfolio.current_conviction.get(candidate.security_id, Decimal("0")) > 0:
            candidate.reasons.append("conviction_exposure_present")
            candidate.eligible = False
        if pending.conviction_by_security.get(candidate.security_id, Decimal("0")) != 0:
            candidate.reasons.append("conviction_pending_exposure")
            candidate.eligible = False
    missing_baseline_assessments = sorted(
        candidate.security_id
        for candidate in candidates
        if candidate.assessment is None
        and (
            portfolio.current_baseline.get(candidate.security_id, Decimal("0")) > 0
            or pending.baseline_by_security.get(candidate.security_id, Decimal("0")) != 0
        )
    )
    if missing_baseline_assessments:
        raise AllocationError(
            "baseline exposure lacks a required assessment: "
            + ",".join(missing_baseline_assessments)
        )
    eligible = sorted(
        (candidate for candidate in candidates if candidate.eligible),
        key=lambda candidate: (
            0 if candidate.tier == "full" else 1,
            -required_decimal(
                candidate.live_valuation.get("confidence_adjusted_expected_return_pct", "0"),
                label="live expected return",
            ),
            -candidate.score.effective_score,
            candidate.security_id,
        ),
    )
    for rank, candidate in enumerate(eligible, start=1):
        candidate.rank = rank
    cash_reserve = equity * settings.allocation.minimum_cash_reserve_pct / ONE_HUNDRED
    available_cash = max(replay.cash_base - pending.committed_cash - cash_reserve, Decimal("0"))
    target_exposure_gap = max(
        equity * settings.allocation.target_invested_pct / ONE_HUNDRED
        - portfolio.gross_total
        - pending.gross_total,
        Decimal("0"),
    )
    remaining_baseline = max(
        equity * settings.allocation.maximum_baseline_sleeve_pct / ONE_HUNDRED
        - portfolio.baseline_total
        - pending.baseline_total,
        Decimal("0"),
    )
    deployment_limit = equity * settings.allocation.maximum_deployment_per_run_pct / ONE_HUNDRED
    deployment_budget = _money(
        min(available_cash, target_exposure_gap, remaining_baseline, deployment_limit)
    )
    if pending.unpriced:
        deployment_budget = Decimal("0")
        for candidate in eligible:
            candidate.reasons.append("pending_exposure_unpriced")
    diversification_components = _diversification_component_count(eligible)
    diversification_factor = min(
        Decimal(diversification_components)
        / Decimal(settings.allocation.minimum_diversified_candidates),
        Decimal("1"),
    )
    diversified_budget = _money(deployment_budget * diversification_factor)
    # Pending baseline exposure already consumes this run's diversification-adjusted
    # deployment tranche. Replanning while an order is still pending must not create
    # another tranche for unchanged evidence.
    incremental_diversified_budget = max(diversified_budget - pending.baseline_total, Decimal("0"))
    incremental_candidates = [
        candidate
        for candidate in eligible
        if pending.baseline_by_security.get(candidate.security_id, Decimal("0")) <= 0
    ]
    if (
        settings.allocation.mode != "disabled"
        and incremental_candidates
        and incremental_diversified_budget > 0
    ):
        _allocate_capped(
            incremental_candidates,
            settings,
            equity,
            incremental_diversified_budget,
            portfolio,
            pending,
        )
    # A plan identifies the economic decision, not the controller invocation that
    # happened to publish it.  Keeping run metadata out of the identity prevents
    # an unchanged plan from superseding its own in-flight strategy/signal work
    # every time a daily run is finalized.
    provisional_rows = _build_rows(
        candidates,
        settings,
        equity,
        portfolio,
        pending,
        plan_id="",
        run_id=run_id,
        as_of=instant,
        deployment_budget=deployment_budget,
        diversified=(
            diversification_components >= settings.allocation.minimum_diversified_candidates
        ),
    )
    input_identity = {
        "allocation_identity_version": 2,
        "mode": settings.allocation.mode,
        "accounting": {
            "cash_base": decimal_text(replay.cash_base),
            "equity_base": decimal_text(equity),
            "current_gross_exposure_base": decimal_text(portfolio.gross_total),
            "current_baseline_exposure_base": decimal_text(portfolio.baseline_total),
            "current_conviction_exposure_base": decimal_text(portfolio.conviction_total),
        },
        "policy": {
            "target_invested_pct": decimal_text(settings.allocation.target_invested_pct),
            "minimum_cash_reserve_pct": decimal_text(settings.allocation.minimum_cash_reserve_pct),
            "maximum_baseline_sleeve_pct": decimal_text(
                settings.allocation.maximum_baseline_sleeve_pct
            ),
            "maximum_baseline_position_pct": decimal_text(
                settings.allocation.maximum_baseline_position_pct
            ),
            "maximum_starter_position_pct": decimal_text(
                settings.allocation.maximum_starter_position_pct
            ),
            "maximum_starter_sleeve_pct": decimal_text(
                settings.allocation.maximum_starter_sleeve_pct
            ),
            "maximum_sector_pct": decimal_text(settings.allocation.maximum_sector_pct),
            "maximum_theme_pct": decimal_text(settings.allocation.maximum_theme_pct),
            "cash_hurdle_score": decimal_text(settings.allocation.cash_hurdle_score),
            "minimum_quality_score": decimal_text(settings.allocation.minimum_quality_score),
            "minimum_base_upside_pct": decimal_text(settings.allocation.minimum_base_upside_pct),
            "minimum_upside_downside_ratio": decimal_text(
                settings.allocation.minimum_upside_downside_ratio
            ),
            "minimum_confidence_adjusted_expected_return_pct": decimal_text(
                settings.allocation.minimum_confidence_adjusted_expected_return_pct
            ),
            "minimum_expected_bear_payoff_ratio": decimal_text(
                settings.allocation.minimum_expected_bear_payoff_ratio
            ),
            "minimum_margin_of_safety_pct": decimal_text(
                settings.allocation.minimum_margin_of_safety_pct
            ),
            "starter_minimum_upside_downside_ratio": decimal_text(
                settings.allocation.starter_minimum_upside_downside_ratio
            ),
            "starter_minimum_expected_bear_payoff_ratio": decimal_text(
                settings.allocation.starter_minimum_expected_bear_payoff_ratio
            ),
            "starter_minimum_margin_of_safety_pct": decimal_text(
                settings.allocation.starter_minimum_margin_of_safety_pct
            ),
            "starter_minimum_bear_return_pct": decimal_text(
                settings.allocation.starter_minimum_bear_return_pct
            ),
            "minimum_confidence": settings.allocation.minimum_confidence,
            "minimum_diversified_candidates": settings.allocation.minimum_diversified_candidates,
            "maximum_assessment_age_days": settings.allocation.maximum_assessment_age_days,
            "research_refresh_lead_days": settings.allocation.research_refresh_lead_days,
            "maximum_deployment_per_run_pct": decimal_text(
                settings.allocation.maximum_deployment_per_run_pct
            ),
            "minimum_trade_pct": decimal_text(settings.allocation.minimum_trade_pct),
            "rebalance_band_pct": decimal_text(settings.allocation.rebalance_band_pct),
            "maximum_single_position_pct": decimal_text(settings.risk.maximum_single_position_pct),
            "maximum_total_gross_exposure_pct": decimal_text(
                settings.risk.maximum_total_gross_exposure_pct
            ),
        },
        "candidate_inputs": [
            {
                "security_id": candidate.security_id,
                "relationship_id": candidate.relationship_id,
                "themes": list(candidate.themes),
                "price": decimal_text(candidate.price) if candidate.price is not None else "",
                "fx_rate": (
                    decimal_text(candidate.fx_rate) if candidate.fx_rate is not None else ""
                ),
                "effective_score": decimal_text(candidate.score.effective_score),
                "candidate_edge": decimal_text(candidate.score.candidate_edge),
                "assessment_id": candidate.assessment_id,
                "tier": candidate.tier,
                "live_valuation": dict(candidate.live_valuation),
                "eligible": candidate.eligible,
                "reasons": sorted(set(candidate.reasons)),
                "rank": candidate.rank,
            }
            for candidate in sorted(candidates, key=lambda value: value.security_id)
        ],
        "targets": [
            {
                "security_id": row["security_id"],
                "strategy_id": row["strategy_id"],
                "sleeve": row["sleeve"],
                "tier": row["tier"],
                "allocation_intent_id": row["allocation_intent_id"],
                "target_quantity": row["target_quantity"],
                "target_weight_pct": row["target_weight_pct"],
                "target_value_base": row["target_value_base"],
                "assessment_as_of": row["assessment_as_of"],
            }
            for row in provisional_rows
        ],
        "securities": [dict(securities[key]) for key in sorted(candidate_ids)],
        "assessments": [dict(assessments[key]) for key in sorted(assessments)],
        "portfolio": read_table(repository_root, "portfolio"),
        "relationships": [dict(row) for key in sorted(relationships) for row in relationships[key]],
    }
    plan_id = stable_id("allocation_plan", content_hash(input_identity))
    rows = [{**row, "allocation_plan_id": plan_id} for row in provisional_rows]
    if settings.allocation.mode == "disabled":
        rows = []
    prior_rows = [
        row
        for row in read_table(repository_root, "allocation_history")
        if row["allocation_plan_id"] == plan_id and row["run_id"] == run_id
    ]
    plan_observed_at = instant
    if prior_rows:
        prior_by_security = {row["security_id"]: row for row in prior_rows}
        current_by_security = {row["security_id"]: row for row in rows}
        comparable_prior = [
            {key: value for key, value in row.items() if key != "as_of"}
            for row in sorted(prior_rows, key=lambda value: value["security_id"])
        ]
        comparable_current = [
            {key: value for key, value in row.items() if key != "as_of"}
            for row in sorted(rows, key=lambda value: value["security_id"])
        ]
        if (
            len(prior_by_security) != len(prior_rows)
            or set(prior_by_security) != set(current_by_security)
            or comparable_prior != comparable_current
        ):
            raise AllocationError("same-run allocation retry conflicts with immutable history")
        observed_values = {row["as_of"] for row in prior_rows}
        if len(observed_values) != 1:
            raise AllocationError("same-run allocation history has inconsistent timestamps")
        observed = parse_timestamp(next(iter(observed_values)))
        assert observed is not None
        plan_observed_at = observed
        rows = sorted(prior_rows, key=lambda value: value["security_id"])
    write_table(repository_root, "allocation_targets", rows)
    _cancel_superseded_allocation_state(repository_root, rows)
    if rows:
        targets_by_strategy = {row["strategy_id"]: row for row in rows}
        strategy_rows = read_table(repository_root, "strategies")
        rebound = False
        for strategy in strategy_rows:
            target = targets_by_strategy.get(strategy["strategy_id"])
            if (
                target is not None
                and strategy["sleeve"] == "baseline"
                and strategy["allocation_intent_id"]
                and strategy["allocation_intent_id"] == target["allocation_intent_id"]
                and strategy["allocation_plan_id"] != plan_id
            ):
                strategy["allocation_plan_id"] = plan_id
                strategy["updated_at"] = format_timestamp(instant)
                rebound = True
        if rebound:
            write_table(repository_root, "strategies", strategy_rows)
    if rows:
        append_unique(
            repository_root,
            "allocation_history",
            rows,
            key_columns=("allocation_plan_id", "run_id", "security_id"),
        )
    operations_created: tuple[str, ...] = ()
    if settings.allocation.mode == "active":
        operations_created = _enqueue_targets(
            repository_root,
            settings,
            {candidate.security_id: candidate for candidate in candidates},
            rows,
            now=instant,
        )
    capital_allocated = sum(
        (
            max(required_decimal(row["delta_value_base"], label="allocation delta"), Decimal("0"))
            for row in rows
        ),
        Decimal("0"),
    )
    capital_unallocated = max(target_exposure_gap - capital_allocated, Decimal("0"))
    unallocated_reasons: set[str] = set()
    if capital_unallocated > 0:
        if settings.allocation.mode == "disabled":
            unallocated_reasons.add("allocation_disabled")
        if not eligible:
            unallocated_reasons.add("insufficient_eligible_candidates")
        if diversification_components < settings.allocation.minimum_diversified_candidates:
            unallocated_reasons.add("insufficient_diversification")
        if eligible:
            if available_cash < target_exposure_gap:
                unallocated_reasons.add("minimum_cash_reserve_or_pending_cash")
            if remaining_baseline < target_exposure_gap:
                unallocated_reasons.add("baseline_sleeve_cap")
            if deployment_limit < min(available_cash, target_exposure_gap, remaining_baseline):
                unallocated_reasons.add("deployment_limit")
        if capital_allocated < diversified_budget:
            unallocated_reasons.add("candidate_or_rounding_constraints")
    if capital_allocated > 0:
        evidence_state = "invested_or_actionable"
    elif any(
        candidate.assessment is not None
        and candidate.assessment.get("research_status") == "unsupported"
        for candidate in candidates
    ):
        evidence_state = "provisional_cash_valuation_unsupported"
    elif any(
        candidate.assessment is None
        or candidate.assessment.get("assessment_schema_version") != "2"
        or candidate.assessment.get("research_status") != "complete"
        or "relationship_missing_or_stale" in candidate.reasons
        for candidate in candidates
    ):
        evidence_state = "provisional_cash_research_incomplete"
    elif eligible:
        evidence_state = "provisional_cash_strategy_pending"
    else:
        evidence_state = "definitive_cash_preference"
    result = AllocationPlanResult(
        allocation_plan_id=plan_id,
        run_id=run_id,
        as_of=format_timestamp(plan_observed_at),
        mode=settings.allocation.mode,
        equity_base=decimal_text(equity),
        cash_base=decimal_text(replay.cash_base),
        minimum_cash_reserve_base=decimal_text(cash_reserve),
        current_gross_exposure_base=decimal_text(portfolio.gross_total),
        target_invested_exposure_base=decimal_text(
            equity * settings.allocation.target_invested_pct / ONE_HUNDRED
        ),
        current_conviction_exposure_base=decimal_text(portfolio.conviction_total),
        current_baseline_exposure_base=decimal_text(portfolio.baseline_total),
        maximum_baseline_exposure_base=decimal_text(
            equity * settings.allocation.maximum_baseline_sleeve_pct / ONE_HUNDRED
        ),
        pending_gross_exposure_base=decimal_text(pending.gross_total),
        deployment_budget_base=decimal_text(deployment_budget),
        diversified_budget_base=decimal_text(diversified_budget),
        capital_allocated_base=decimal_text(capital_allocated),
        capital_unallocated_base=decimal_text(capital_unallocated),
        unallocated_reasons=tuple(sorted(unallocated_reasons)),
        evidence_state=evidence_state,
        eligible_candidate_count=len(eligible),
        excluded_candidate_count=len(candidates) - len(eligible),
        target_count=len(rows),
        operations_created=operations_created,
    )
    run_directory = repository_root / "data" / "runs" / run_id
    if run_directory.is_symlink():
        raise AllocationError("allocation run directory must not be a symlink")
    run_directory.mkdir(parents=True, exist_ok=True)
    atomic_write_json(
        run_directory / "allocation_plan.json",
        {"allocation_plan_version": 1, **asdict(result)},
        allowed_root=repository_root,
    )
    return result


def latest_allocation_target(repository_root: Path, strategy_id: str) -> Mapping[str, str] | None:
    """Return a strategy's target only from the current generated plan."""

    matches = [
        row
        for row in read_table(repository_root, "allocation_targets")
        if row["strategy_id"] == strategy_id
    ]
    if len(matches) > 1:
        raise AllocationError(f"strategy has duplicate current allocation targets: {strategy_id}")
    return matches[0] if matches else None


def validate_allocation_state(repository_root: Path, settings: Settings) -> list[str]:
    """Validate assessment, strategy-sleeve, target, and immutable-plan relationships."""

    from papertrader.research import (
        ASSESSMENT_ELIGIBILITY,
        HARD_BLOCKERS,
        SOFT_GAPS,
    )

    errors: list[str] = []
    try:
        securities = {row["security_id"] for row in read_table(repository_root, "securities")}
        sources = {row["source_id"]: row for row in read_table(repository_root, "source_registry")}
        assessments = read_table(repository_root, "security_assessments")
        targets = read_table(repository_root, "allocation_targets")
        history = read_table(repository_root, "allocation_history")
        strategies = read_table(repository_root, "strategies")
        strategy_legs = read_table(repository_root, "strategy_legs")
        portfolio = read_table(repository_root, "portfolio")
        orders = read_table(repository_root, "orders")
        order_legs = read_table(repository_root, "order_legs")
    except (CanonicalValueError, OSError) as exc:
        return [str(exc)]
    seen_assessments: set[str] = set()
    for row in assessments:
        security_id = row["security_id"]
        if security_id in seen_assessments:
            errors.append(f"duplicate security assessment: {security_id}")
        seen_assessments.add(security_id)
        if security_id not in securities:
            errors.append(f"assessment references missing security: {security_id}")
        try:
            score_assessment(row, settings.allocation.cash_hurdle_score)
            assessed = parse_timestamp(row["assessed_at"])
            expires = parse_timestamp(row["expires_at"])
            assert assessed is not None and expires is not None
            if row["assessed_at"] != format_timestamp(assessed) or row[
                "expires_at"
            ] != format_timestamp(expires):
                errors.append(f"assessment timestamps are not canonical: {security_id}")
            if expires <= assessed:
                errors.append(f"assessment expiration does not follow assessment: {security_id}")
            blockers = tuple(part for part in row["hard_blockers"].split("|") if part)
            gaps = tuple(part for part in row["soft_gaps"].split("|") if part)
            if row["eligibility"] not in ASSESSMENT_ELIGIBILITY:
                errors.append(f"assessment eligibility is invalid: {security_id}")
            if blockers != tuple(sorted(set(blockers))) or set(blockers) - HARD_BLOCKERS:
                errors.append(f"assessment hard blockers are invalid: {security_id}")
            if gaps != tuple(sorted(set(gaps))) or set(gaps) - SOFT_GAPS:
                errors.append(f"assessment soft gaps are invalid: {security_id}")
            is_v2 = row.get("assessment_schema_version") == "2"
            if not is_v2 and bool(blockers) != (row["eligibility"] == "ineligible"):
                errors.append(f"assessment hard-blocker disposition is inconsistent: {security_id}")
            if row["downside_pct"]:
                required_decimal(row["downside_pct"], label="downside_pct")
            if row["base_upside_pct"]:
                required_decimal(row["base_upside_pct"], label="base_upside_pct")
            if is_v2:
                if row["research_status"] not in {"complete", "partial", "unsupported", "stale"}:
                    raise ValueError("invalid research status")
                if row["allocation_eligibility"] not in {"eligible", "ineligible"}:
                    raise ValueError("invalid allocation eligibility")
                if row["conviction_tier"] not in {"watch", "baseline", "conviction"}:
                    raise ValueError("invalid conviction tier")
                required_decimal(row["quality_score"], label="quality_score")
            horizon = int(row["valuation_horizon_months"])
            if horizon <= 0 or row["valuation_horizon_months"] != str(horizon):
                raise ValueError("non-positive horizon")
            if not SAFE_RUN_ID.fullmatch(row["run_id"]):
                raise ValueError("unsafe run ID")
            evidence = tuple(part for part in row["evidence_refs"].split("|") if part)
            if not evidence or evidence != tuple(sorted(set(evidence))):
                raise ValueError("invalid evidence references")
            for source_id in evidence:
                source = sources.get(source_id)
                if source is None:
                    raise ValueError(f"unregistered evidence {source_id}")
                checked = parse_timestamp(source["last_checked_at"])
                first_seen = parse_timestamp(source["first_seen_at"])
                changed = parse_timestamp(source["last_changed_at"])
                if (
                    checked is None
                    or first_seen is None
                    or changed is None
                    or first_seen > assessed
                    or changed > assessed
                    or (
                        checked <= assessed
                        and assessed - checked
                        > timedelta(days=settings.allocation.maximum_assessment_age_days)
                    )
                    or source["status"] not in {"available", "ok", "current"}
                ):
                    raise ValueError(f"unavailable or stale evidence {source_id}")
        except (AllocationError, CanonicalValueError, ValueError) as exc:
            errors.append(f"invalid assessment {security_id}: {exc}")
    strategy_by_id: dict[str, Mapping[str, str]] = {}
    target_by_strategy = {row["strategy_id"]: row for row in targets}
    for row in strategies:
        if row["strategy_id"] in strategy_by_id:
            errors.append(f"duplicate strategy: {row['strategy_id']}")
        strategy_by_id[row["strategy_id"]] = row
        if row["sleeve"] not in {"conviction", "baseline"}:
            errors.append(f"strategy has invalid sleeve: {row['strategy_id']}")
        if row["sleeve"] == "conviction" and (
            row["allocation_plan_id"] or row["allocation_intent_id"]
        ):
            errors.append(f"conviction strategy references allocation intent: {row['strategy_id']}")
        if row["sleeve"] == "baseline" and (
            not row["allocation_plan_id"]
            or row["strategy_id"] != baseline_strategy_id(row["security_id"])
        ):
            errors.append(f"baseline strategy identity is invalid: {row['strategy_id']}")
        if row["sleeve"] == "baseline":
            if row["security_id"] not in seen_assessments:
                errors.append(f"baseline strategy lacks assessment: {row['strategy_id']}")
            try:
                risk_budget = required_decimal(
                    row["risk_budget_pct"], label="baseline strategy risk budget"
                )
                target = target_by_strategy.get(row["strategy_id"])
                compatible_target = bool(
                    row["allocation_intent_id"]
                    and target is not None
                    and row["allocation_intent_id"] == target["allocation_intent_id"]
                )
                allowed_caps = {
                    settings.allocation.maximum_baseline_position_pct,
                    settings.allocation.maximum_starter_position_pct,
                }
                if compatible_target and target is not None:
                    expected_cap = required_decimal(
                        target["position_cap_pct"], label="target position cap"
                    )
                    if risk_budget != expected_cap:
                        raise ValueError("risk budget differs from allocation-tier position cap")
                elif risk_budget not in allowed_caps:
                    raise ValueError("risk budget differs from allocation-tier position cap")
            except (CanonicalValueError, ValueError) as exc:
                errors.append(f"invalid baseline strategy {row['strategy_id']}: {exc}")
            legs = [leg for leg in strategy_legs if leg["strategy_id"] == row["strategy_id"]]
            if len(legs) != 1 or any(
                leg["action"] != "buy"
                or leg["side"] != "long"
                or leg["instrument_type"] != "equity"
                or leg["security_id"] != row["security_id"]
                for leg in legs
            ):
                errors.append(f"baseline strategy legs are invalid: {row['strategy_id']}")
    sleeves_by_identity: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for row in portfolio:
        identity = (row["security_id"], row["provider_contract_id"])
        for strategy_id in (part for part in row["strategy_ids"].split("|") if part):
            strategy = strategy_by_id.get(strategy_id)
            if strategy is None:
                errors.append(f"portfolio position references missing strategy: {strategy_id}")
                continue
            sleeves_by_identity[identity].add(strategy["sleeve"])
    pending_orders = {
        row["order_id"]: row for row in orders if row["status"] in {"pending", "partially_filled"}
    }
    for row in order_legs:
        order = pending_orders.get(row["order_id"])
        if order is None:
            continue
        strategy = strategy_by_id.get(order["strategy_id"])
        if strategy is None:
            errors.append(f"pending order references missing strategy: {order['strategy_id']}")
            continue
        sleeves_by_identity[(row["security_id"], row["provider_contract_id"])].add(
            strategy["sleeve"]
        )
    for identity, sleeves in sorted(sleeves_by_identity.items()):
        if len(sleeves) > 1:
            errors.append(f"instrument exposure mixes allocation sleeves: {identity!r}")
    plan_ids = {row["allocation_plan_id"] for row in targets}
    if len(plan_ids) > 1:
        errors.append("current allocation targets contain multiple plans")
    seen_targets: set[str] = set()
    target_plan_identity: set[tuple[str, str, str]] = set()
    for row in targets:
        security_id = row["security_id"]
        if security_id in seen_targets:
            errors.append(f"duplicate current allocation target: {security_id}")
        seen_targets.add(security_id)
        if security_id not in securities:
            errors.append(f"allocation target references missing security: {security_id}")
        if row["strategy_id"] != baseline_strategy_id(security_id) or row["sleeve"] != "baseline":
            errors.append(f"allocation target strategy identity is invalid: {security_id}")
        try:
            as_of = parse_timestamp(row["as_of"])
            assert as_of is not None
            if row["as_of"] != format_timestamp(as_of):
                raise ValueError("non-canonical plan timestamp")
            if not SAFE_RUN_ID.fullmatch(row["allocation_plan_id"]) or not SAFE_RUN_ID.fullmatch(
                row["run_id"]
            ):
                raise ValueError("unsafe plan or run ID")
            if row["rank"] and int(row["rank"]) <= 0:
                raise ValueError("rank is not positive")
            legacy_target = not row["tier"] and not row["allocation_intent_id"]
            if not legacy_target:
                if row["tier"] not in {"full", "starter", "watch"}:
                    raise ValueError("invalid allocation tier")
                target_quantity = required_decimal(row["target_quantity"], label="target quantity")
                if target_quantity < 0 or target_quantity != target_quantity.to_integral_value():
                    raise ValueError("target quantity is not a non-negative whole number")
                position_cap = required_decimal(row["position_cap_pct"], label="position cap")
                expected_cap = {
                    "full": settings.allocation.maximum_baseline_position_pct,
                    "starter": settings.allocation.maximum_starter_position_pct,
                    "watch": Decimal("0"),
                }[row["tier"]]
                if position_cap != expected_cap:
                    raise ValueError("position cap differs from allocation tier")
                if not row["assessment_id"] or not row["relationship_id"]:
                    if row["allocation_intent_id"]:
                        raise ValueError("allocation intent lacks immutable inputs")
                else:
                    expected_intent = stable_id(
                        "allocation_intent",
                        row["security_id"],
                        "long",
                        "equity",
                        row["assessment_id"],
                        row["relationship_id"],
                        row["tier"],
                        row["target_quantity"],
                    )
                    if expected_intent != row["allocation_intent_id"]:
                        raise ValueError("allocation intent identity mismatch")
            target_plan_identity.add((row["allocation_plan_id"], row["run_id"], row["as_of"]))
        except (CanonicalValueError, ValueError) as exc:
            errors.append(f"invalid allocation target identity {security_id}: {exc}")
        if row["disposition"] not in {
            "open",
            "increase",
            "hold",
            "reduce",
            "close",
            "excluded",
            "below_minimum_trade",
        }:
            errors.append(f"allocation target disposition is invalid: {security_id}")
        try:
            target_weight = required_decimal(row["target_weight_pct"], label="target weight")
            target_value = required_decimal(row["target_value_base"], label="target value")
            current_weight = required_decimal(row["current_weight_pct"], label="current weight")
            required_decimal(row["pending_weight_pct"], label="pending weight")
            required_decimal(row["delta_value_base"], label="target delta")
            required_decimal(row["effective_score"], label="effective score")
            edge = required_decimal(row["candidate_edge"], label="candidate edge")
            if (
                target_weight < 0
                or target_weight
                > (
                    required_decimal(row["position_cap_pct"], label="target position cap")
                    if row["position_cap_pct"]
                    else settings.allocation.maximum_baseline_position_pct
                )
                or target_value < 0
                or current_weight < 0
                or edge < 0
            ):
                raise ValueError("target numeric limit")
        except (CanonicalValueError, ValueError) as exc:
            errors.append(f"invalid allocation target {security_id}: {exc}")
    if len(target_plan_identity) > 1:
        errors.append("current allocation targets do not share one plan identity")
    seen_history: set[tuple[str, str, str]] = set()
    for row in history:
        key = (row["allocation_plan_id"], row["run_id"], row["security_id"])
        if key in seen_history:
            errors.append(f"duplicate allocation history row: {key!r}")
        seen_history.add(key)
        try:
            if row["security_id"] not in securities:
                raise ValueError("missing security")
            if (
                row["strategy_id"] != baseline_strategy_id(row["security_id"])
                or row["sleeve"] != "baseline"
            ):
                raise ValueError("invalid strategy identity")
            if not SAFE_RUN_ID.fullmatch(row["allocation_plan_id"]) or not SAFE_RUN_ID.fullmatch(
                row["run_id"]
            ):
                raise ValueError("unsafe plan or run ID")
            as_of = parse_timestamp(row["as_of"])
            assert as_of is not None
            if row["as_of"] != format_timestamp(as_of):
                raise ValueError("non-canonical timestamp")
            if row["rank"] and int(row["rank"]) <= 0:
                raise ValueError("invalid rank")
            if row["allocation_intent_id"]:
                if row["tier"] not in {"full", "starter", "watch"}:
                    raise ValueError("invalid tier")
                target_quantity = required_decimal(
                    row["target_quantity"], label="history target quantity"
                )
                if target_quantity < 0 or target_quantity != target_quantity.to_integral_value():
                    raise ValueError("invalid target quantity")
                expected_intent = stable_id(
                    "allocation_intent",
                    row["security_id"],
                    "long",
                    "equity",
                    row["assessment_id"],
                    row["relationship_id"],
                    row["tier"],
                    row["target_quantity"],
                )
                if expected_intent != row["allocation_intent_id"]:
                    raise ValueError("allocation intent mismatch")
            if row["disposition"] not in {
                "open",
                "increase",
                "hold",
                "reduce",
                "close",
                "excluded",
                "below_minimum_trade",
            }:
                raise ValueError("invalid disposition")
            target_weight = required_decimal(
                row["target_weight_pct"], label="history target weight"
            )
            target_value = required_decimal(row["target_value_base"], label="history target value")
            edge = required_decimal(row["candidate_edge"], label="history edge")
            for field in (
                "effective_score",
                "current_weight_pct",
                "pending_weight_pct",
                "delta_value_base",
            ):
                required_decimal(row[field], label=f"history {field}")
            if (
                target_weight < 0
                or target_weight
                > (
                    required_decimal(row["position_cap_pct"], label="history position cap")
                    if row["position_cap_pct"]
                    else settings.allocation.maximum_baseline_position_pct
                )
                or target_value < 0
                or edge < 0
            ):
                raise ValueError("numeric limit")
            assessment_as_of = parse_timestamp(row["assessment_as_of"], allow_empty=True)
            if assessment_as_of is not None and row["assessment_as_of"] != format_timestamp(
                assessment_as_of
            ):
                raise ValueError("non-canonical assessment timestamp")
        except (AllocationError, CanonicalValueError, ValueError) as exc:
            errors.append(f"invalid allocation history {key!r}: {exc}")
    current_history = {
        (row["allocation_plan_id"], row["run_id"], row["security_id"]): row for row in history
    }
    for row in targets:
        key = (row["allocation_plan_id"], row["run_id"], row["security_id"])
        if current_history.get(key) != row:
            errors.append(
                f"current allocation target lacks identical immutable history: {row['security_id']}"
            )
    return errors


__all__ = [
    "AllocationError",
    "AllocationPlanResult",
    "AssessmentScore",
    "baseline_strategy_id",
    "calculate_assessment_score",
    "latest_allocation_target",
    "plan_allocation",
    "score_assessment",
    "validate_allocation_state",
]

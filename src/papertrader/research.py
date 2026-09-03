"""Validated CLI-owned structured research state transitions."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.models import OrderLegSpec
from papertrader.orders import leg_from_mapping
from papertrader.tables import append_unique, contract_by_name, read_table, write_table
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
from papertrader.valuation import (
    ASSESSMENT_V2_AGENT_FIELDS,
    ASSESSMENT_V2_OUTPUT_FIELDS,
    ValuationError,
    derive_assessment_dimensions,
    normalize_v2_assessment,
)

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
STRATEGY_STATUSES = frozenset(
    {"draft", "researching", "ready", "active", "paused", "closed", "rejected", "expired"}
)
STRATEGY_SLEEVES = frozenset({"conviction", "baseline"})
ASSESSMENT_ELIGIBILITY = frozenset({"ineligible", "baseline", "conviction"})
ASSESSMENT_CONFIDENCE = frozenset({"low", "medium", "high"})
ASSESSMENT_SCORE_FIELDS = (
    "thesis_score",
    "business_quality_score",
    "balance_sheet_score",
    "valuation_score",
    "timing_score",
    "liquidity_score",
    "risk_penalty",
)
LEGACY_ASSESSMENT_FIELDS = (
    "security_id",
    "assessed_at",
    "expires_at",
    "eligibility",
    "confidence",
    *ASSESSMENT_SCORE_FIELDS,
    "downside_pct",
    "base_upside_pct",
    "valuation_horizon_months",
    "hard_blockers",
    "soft_gaps",
    "evidence_refs",
    "run_id",
)
HARD_BLOCKERS = frozenset(
    {
        "identity_uncertain",
        "research_stale",
        "valuation_unsupported",
        "market_data_stale",
        "fx_unavailable",
        "liquidity_insufficient",
        "solvency_risk",
        "accounting_uncertain",
        "thesis_invalidated",
        "instrument_unsupported",
        "exchange_unsupported",
        "currency_unsupported",
    }
)
SOFT_GAPS = frozenset(
    {
        "margin_of_safety_below_target",
        "timing_unfavorable",
        "catalyst_missing",
        "valuation_not_compelling",
        "confidence_medium",
        "concentration_sensitive",
        "cyclical_normalization_uncertain",
    }
)
IMMUTABLE_SECURITY_FIELDS = (
    "issuer_id",
    "instrument_name",
    "instrument_type",
    "venue_mic",
    "provider_symbol",
    "currency",
)
WATCHLIST_SECURITY_FIELDS = (
    "company_name",
    "instrument_name",
    "instrument_type",
    "ticker",
    "exchange_code",
    "venue_mic",
    "provider_symbol",
    "currency",
    "country",
    "sector",
    "industry",
)


class ResearchStateError(RuntimeError):
    """Raised when a research-state mutation violates identity or schema rules."""


@dataclass(frozen=True, slots=True)
class AssessmentMigrationResult:
    """Idempotent legacy archive, exact-header rewrite, and bounded v2 refresh plan."""

    migration_version: str
    imported_history_rows: int
    existing_history_rows: int
    current_rows_rewritten: int
    refreshes_selected: tuple[str, ...]
    operations_created: tuple[str, ...]
    report_path: str


def _exact_strings(
    raw: Mapping[str, object], expected: Sequence[str], *, label: str
) -> dict[str, str]:
    actual = set(raw)
    required = set(expected)
    if actual != required:
        raise ResearchStateError(
            f"{label} fields differ; missing={sorted(required - actual)}, "
            f"extra={sorted(actual - required)}"
        )
    values: dict[str, str] = {}
    for field in expected:
        value = raw[field]
        if not isinstance(value, str):
            raise ResearchStateError(f"{label}.{field} must be a string")
        if "\x00" in value or "\r" in value or "\n" in value:
            raise ResearchStateError(f"{label}.{field} must be a single safe CSV value")
        values[field] = value.strip()
    return values


def _required(values: Mapping[str, str], fields: Sequence[str], *, label: str) -> None:
    missing = [field for field in fields if not values[field]]
    if missing:
        raise ResearchStateError(f"{label} requires non-empty fields: {missing}")


def _identifier(value: str, *, label: str) -> None:
    if not SAFE_ID.fullmatch(value):
        raise ResearchStateError(f"{label} is not a safe immutable identifier: {value!r}")


def _canonical_timestamp(value: str, *, label: str, allow_empty: bool = False) -> str:
    if not value and allow_empty:
        return ""
    parsed = parse_timestamp(value)
    assert parsed is not None
    canonical = format_timestamp(parsed)
    if canonical != value:
        raise ResearchStateError(f"{label} must use canonical UTC form {canonical}")
    return canonical


def _wiki_page(repository_root: Path, value: str, domain: str) -> str:
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or len(relative.parts) < 4
        or relative.parts[:3] != ("data", "wiki", domain)
        or relative.suffix != ".md"
    ):
        raise ResearchStateError(f"research_page must be Markdown under data/wiki/{domain}/")
    path = repository_root.joinpath(*relative.parts)
    if path.is_symlink() or not path.is_file():
        raise ResearchStateError(f"research_page must exist before structured upsert: {value}")
    return relative.as_posix()


def _replace_row(
    repository_root: Path,
    table: str,
    row: Mapping[str, str],
    *,
    key: str,
) -> bool:
    existing = read_table(repository_root, table)
    previous = next((candidate for candidate in existing if candidate[key] == row[key]), None)
    if previous == row:
        return False
    output = [candidate for candidate in existing if candidate[key] != row[key]]
    output.append(dict(row))
    output.sort(key=lambda candidate: candidate[key])
    write_table(repository_root, table, output)
    return True


def _canonical_set(value: str, allowed: frozenset[str], *, label: str) -> tuple[str, ...]:
    values = tuple(part for part in value.split("|") if part)
    if values != tuple(sorted(set(values))):
        raise ResearchStateError(f"{label} must be sorted, unique, and pipe-delimited")
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ResearchStateError(f"{label} contains non-canonical values: {unknown}")
    return values


def _validate_evidence_refs(
    repository_root: Path,
    values: str,
    *,
    assessed_at: datetime,
    maximum_age: timedelta,
) -> tuple[str, ...]:
    references = tuple(part for part in values.split("|") if part)
    if not references or references != tuple(sorted(set(references))):
        raise ResearchStateError("assessment.evidence_refs must be sorted, unique source IDs")
    registry = {row["source_id"]: row for row in read_table(repository_root, "source_registry")}
    for reference in references:
        source = registry.get(reference)
        if source is None:
            raise ResearchStateError(f"assessment evidence source is not registered: {reference}")
        checked = parse_timestamp(source["last_checked_at"])
        if checked is None or checked > assessed_at or assessed_at - checked > maximum_age:
            raise ResearchStateError(f"assessment evidence source is not fresh: {reference}")
        if source["status"] not in {"available", "ok", "current"}:
            raise ResearchStateError(f"assessment evidence source is unavailable: {reference}")
    return references


def upsert_assessment(
    repository_root: Path,
    settings: Settings,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> bool:
    """Insert or replace one current comparable security assessment."""

    columns = contract_by_name(repository_root, "security_assessments").columns
    is_v2 = raw.get("assessment_schema_version") == "2"
    requested_source_operation_id = ""
    if is_v2:
        raw_source_operation_id = raw.get("source_operation_id", "")
        if not isinstance(raw_source_operation_id, str):
            raise ResearchStateError("assessment source_operation_id must be a string")
        requested_source_operation_id = raw_source_operation_id.strip()
        assessment_request = {
            key: value for key, value in raw.items() if key != "source_operation_id"
        }
        if (
            "valuation_template_rationale" not in raw
            and isinstance(raw.get("valuation_template"), str)
            and raw.get("valuation_template") != "other"
        ):
            # Named repository templates forbid a rationale, so its only canonical value is
            # the empty string. Accept omission at the JSON request boundary while preserving
            # the exact, explicit field in canonical CSV state.
            assessment_request = {**assessment_request, "valuation_template_rationale": ""}
        agent_values = _exact_strings(
            assessment_request, ASSESSMENT_V2_AGENT_FIELDS, label="assessment_v2"
        )
        try:
            normalized_v2 = normalize_v2_assessment(repository_root, settings, agent_values)
        except (CanonicalValueError, ValuationError, ValueError) as exc:
            raise ResearchStateError(f"assessment v2 is invalid: {exc}") from exc
        relationship_accepted = any(
            row["security_id"] == agent_values["security_id"] and row["status"] == "accepted"
            for row in read_table(repository_root, "relationships")
        )
        dimensions = derive_assessment_dimensions(
            {**agent_values, **normalized_v2},
            settings,
            relationship_accepted=relationship_accepted,
        )
        normalized_v2.update(dimensions)
        from papertrader.ratings import (
            canonical_rating,
            portfolio_action,
            research_conclusion,
        )

        rating_values = {**agent_values, **normalized_v2}
        rating = canonical_rating(rating_values, settings)
        portfolio_row = next(
            (
                row
                for row in read_table(repository_root, "portfolio")
                if row["security_id"] == agent_values["security_id"]
            ),
            None,
        )
        target = next(
            (
                row
                for row in read_table(repository_root, "allocation_targets")
                if row["security_id"] == agent_values["security_id"]
            ),
            None,
        )
        action = portfolio_action(
            rating,
            rating_values,
            current_quantity=(
                required_decimal(portfolio_row["quantity"], label="portfolio quantity")
                if portfolio_row
                else Decimal("0")
            ),
            current_weight_pct=(
                required_decimal(target["current_weight_pct"], label="current weight")
                if target
                else Decimal("0")
            ),
            target_weight_pct=(
                required_decimal(target["target_weight_pct"], label="target weight")
                if target
                else Decimal("0")
            ),
            strategies=[
                row
                for row in read_table(repository_root, "strategies")
                if row["security_id"] == agent_values["security_id"]
            ],
        )
        normalized_v2.update(
            {
                "canonical_rating": rating,
                "portfolio_action": action,
                "rating_change_conditions": agent_values["rating_change_conditions"],
                "research_conclusion": research_conclusion(
                    rating_values,
                    rating,
                    action,
                    agent_values["rating_change_conditions"],
                ),
            }
        )
        compatibility_eligibility = (
            dimensions["conviction_tier"]
            if dimensions["allocation_eligibility"] == "eligible"
            else "ineligible"
        )
        values = {
            "security_id": agent_values["security_id"],
            "assessed_at": agent_values["assessed_at"],
            "expires_at": agent_values["expires_at"],
            "eligibility": compatibility_eligibility,
            "confidence": agent_values["confidence"],
            **{field: agent_values[field] for field in ASSESSMENT_SCORE_FIELDS},
            "downside_pct": normalized_v2["bear_return_pct"],
            "base_upside_pct": normalized_v2["base_return_pct"],
            "valuation_horizon_months": agent_values["valuation_horizon_months"],
            "hard_blockers": agent_values["hard_blockers"],
            "soft_gaps": agent_values["soft_gaps"],
            "evidence_refs": agent_values["evidence_refs"],
            "run_id": agent_values["run_id"],
            **normalized_v2,
        }
    else:
        legacy = _exact_strings(raw, LEGACY_ASSESSMENT_FIELDS, label="assessment")
        values = {
            **legacy,
            **{field: "" for field in ASSESSMENT_V2_OUTPUT_FIELDS},
            "assessment_schema_version": "legacy_v1",
        }
    values = _exact_strings(values, columns, label="normalized_assessment")
    _required(
        values,
        tuple(
            field
            for field in LEGACY_ASSESSMENT_FIELDS
            if field not in {"hard_blockers", "soft_gaps", "downside_pct", "base_upside_pct"}
        ),
        label="assessment",
    )
    _identifier(values["security_id"], label="security_id")
    if not any(
        row["security_id"] == values["security_id"]
        for row in read_table(repository_root, "securities")
    ):
        raise ResearchStateError("assessment references an unknown security_id")
    if values["eligibility"] not in ASSESSMENT_ELIGIBILITY:
        raise ResearchStateError("assessment eligibility is not canonical")
    if values["confidence"] not in ASSESSMENT_CONFIDENCE:
        raise ResearchStateError("assessment confidence is not canonical")
    for field in ASSESSMENT_SCORE_FIELDS:
        score = required_decimal(values[field], label=field)
        if score != score.to_integral_value() or not Decimal("0") <= score <= Decimal("100"):
            raise ResearchStateError(f"assessment.{field} must be integer decimal text in 0-100")
        values[field] = decimal_text(score)
    for field in ("downside_pct", "base_upside_pct"):
        if values[field]:
            value = required_decimal(values[field], label=field)
            values[field] = decimal_text(value)
    try:
        horizon = int(values["valuation_horizon_months"])
    except ValueError as exc:
        raise ResearchStateError("valuation_horizon_months must be a positive integer") from exc
    if horizon <= 0 or values["valuation_horizon_months"] != str(horizon):
        raise ResearchStateError("valuation_horizon_months must be a positive integer")
    blockers = _canonical_set(values["hard_blockers"], HARD_BLOCKERS, label="hard_blockers")
    _canonical_set(values["soft_gaps"], SOFT_GAPS, label="soft_gaps")
    if blockers and values["eligibility"] != "ineligible":
        raise ResearchStateError("a hard blocker forces eligibility=ineligible")
    if not is_v2 and values["eligibility"] == "ineligible" and not blockers:
        raise ResearchStateError("an ineligible assessment requires an explicit hard blocker")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    values["assessed_at"] = _canonical_timestamp(values["assessed_at"], label="assessed_at")
    values["expires_at"] = _canonical_timestamp(values["expires_at"], label="expires_at")
    assessed = parse_timestamp(values["assessed_at"])
    expires = parse_timestamp(values["expires_at"])
    assert assessed is not None and expires is not None
    if assessed > instant:
        raise ResearchStateError("assessment must not be future-dated")
    if expires <= assessed:
        raise ResearchStateError("assessment expiration must follow assessment time")
    _validate_evidence_refs(
        repository_root,
        values["evidence_refs"],
        assessed_at=assessed,
        maximum_age=timedelta(days=settings.allocation.maximum_assessment_age_days),
    )
    _identifier(values["run_id"], label="run_id")
    rows = read_table(repository_root, "security_assessments")
    previous = next((row for row in rows if row["security_id"] == values["security_id"]), None)
    if previous is not None:
        previous_assessed = parse_timestamp(previous["assessed_at"])
        assert previous_assessed is not None
        if assessed < previous_assessed:
            raise ResearchStateError("assessment update is older than current assessment state")
        if assessed == previous_assessed and previous != values:
            raise ResearchStateError("assessment timestamp conflicts with existing assessment")
    security = next(
        row
        for row in read_table(repository_root, "securities")
        if row["security_id"] == values["security_id"]
    )
    page_relative = security["research_page"]
    page_hash = ""
    if page_relative:
        page = repository_root.joinpath(*PurePosixPath(page_relative).parts)
        if page.is_symlink() or not page.is_file():
            raise ResearchStateError("assessment security research_page is missing or a symlink")
        page_hash = content_hash(page.read_bytes())
    eligible_source_operations = [
        row
        for table in ("operations_todo", "operations_history")
        for row in read_table(repository_root, table)
        if row["operation_type"] in {"security_research", "quick_check_research"}
        and row["entity_id"] == values["security_id"]
        and row["claimed_by_run_id"] == values["run_id"]
    ]
    if requested_source_operation_id:
        if not SAFE_ID.fullmatch(requested_source_operation_id):
            raise ResearchStateError("assessment source_operation_id is invalid")
        source_operations = [
            row
            for row in eligible_source_operations
            if row["operation_id"] == requested_source_operation_id
        ]
        if len(source_operations) != 1:
            raise ResearchStateError(
                "assessment source_operation_id does not match this security research run"
            )
    else:
        source_operations = eligible_source_operations
        if len(source_operations) > 1:
            raise ResearchStateError("assessment source operation is ambiguous for this run")
    source_operation_id = source_operations[0]["operation_id"] if source_operations else ""
    source_result_path = (
        f"data/runs/{values['run_id']}/{source_operation_id}/agent_result.json"
        if source_operation_id
        else ""
    )
    history = read_table(repository_root, "security_assessment_history")
    current_history = next(
        (row for row in reversed(history) if row["security_id"] == values["security_id"]),
        None,
    )
    previous_assessment_id = current_history["assessment_id"] if current_history else ""
    assessment_identity = {
        **values,
        "source_operation_id": source_operation_id,
        "source_result_path": source_result_path,
        "research_page": page_relative,
        "research_page_hash": page_hash,
    }
    assessment_id = stable_id("assessment", content_hash(assessment_identity))
    if any(row["assessment_id"] == assessment_id for row in history):
        return False
    history_row = {
        "assessment_id": assessment_id,
        "previous_assessment_id": previous_assessment_id,
        **assessment_identity,
        "recorded_at": format_timestamp(instant),
    }
    # The immutable version is accepted and validated before the mutable current projection moves.
    appended = append_unique(
        repository_root,
        "security_assessment_history",
        [history_row],
        key_columns=("assessment_id",),
    )
    projected = _replace_row(
        repository_root,
        "security_assessments",
        values,
        key="security_id",
    )
    return bool(appended) or projected


def assessment_by_id(repository_root: Path, assessment_id: str) -> dict[str, str]:
    """Return one immutable historical assessment by its stable identity."""

    _identifier(assessment_id, label="assessment_id")
    matches = [
        row
        for row in read_table(repository_root, "security_assessment_history")
        if row["assessment_id"] == assessment_id
    ]
    if len(matches) != 1:
        raise ResearchStateError(f"unknown historical assessment_id: {assessment_id}")
    return matches[0]


def security_research_context(
    repository_root: Path, security_id: str, *, history_limit: int = 2
) -> dict[str, object]:
    """Build bounded, read-only prior-review context for one immutable security."""

    _identifier(security_id, label="security_id")
    if history_limit < 2 or history_limit > 10:
        raise ResearchStateError("history_limit must be between 2 and 10")
    security = next(
        (
            row
            for row in read_table(repository_root, "securities")
            if row["security_id"] == security_id
        ),
        None,
    )
    if security is None:
        raise ResearchStateError(f"unknown security_id: {security_id}")
    versions = [
        row
        for row in read_table(repository_root, "security_assessment_history")
        if row["security_id"] == security_id
    ][-history_limit:]
    current = next(
        (
            row
            for row in read_table(repository_root, "security_assessments")
            if row["security_id"] == security_id
        ),
        None,
    )
    successful = [
        row
        for row in read_table(repository_root, "operations_history")
        if row["operation_type"] in {"security_research", "quick_check_research"}
        and row["entity_id"] == security_id
        and row["terminal_status"] == "succeeded"
    ]
    latest_success = max(successful, key=lambda row: row["completed_at"], default=None)
    page_hash = ""
    if security["research_page"]:
        page = repository_root.joinpath(*PurePosixPath(security["research_page"]).parts)
        if page.is_file() and not page.is_symlink():
            page_hash = content_hash(page.read_bytes())
    relationships = [
        row
        for row in read_table(repository_root, "relationships")
        if row["security_id"] == security_id
    ]
    idea_ids = sorted({row["idea_id"] for row in relationships})
    evidence_ids = sorted(
        {
            reference
            for version in versions
            for reference in version["evidence_refs"].split("|")
            if reference
        }
    )
    sources = [
        row
        for row in read_table(repository_root, "source_registry")
        if row["source_id"] in evidence_ids
    ]
    return {
        "security": security,
        "current_assessment": current,
        "current_history_version": versions[-1] if versions else None,
        "previous_assessment": versions[-2] if len(versions) > 1 else None,
        "assessment_history": versions,
        "latest_successful_research": latest_success,
        "ideas": idea_ids,
        "relationships": relationships,
        "strategies": [
            row
            for row in read_table(repository_root, "strategies")
            if row["security_id"] == security_id
        ],
        "sources": sources,
        "previous_page_hash": versions[-1]["research_page_hash"] if versions else "",
        "current_page_hash": page_hash,
    }


def _legacy_source_operation(
    repository_root: Path, assessment: Mapping[str, str]
) -> Mapping[str, str] | None:
    matches = [
        row
        for row in read_table(repository_root, "operations_history")
        if row["operation_type"] in {"security_research", "quick_check_research"}
        and row["entity_id"] == assessment["security_id"]
        and row["claimed_by_run_id"] == assessment["run_id"]
        and row["terminal_status"] == "succeeded"
    ]
    return max(matches, key=lambda row: (row["completed_at"], row["operation_id"]), default=None)


def _migration_priority(
    security_id: str,
    assessment: Mapping[str, str] | None,
    *,
    holding_ids: set[str],
    pending_ids: set[str],
    target: Mapping[str, str] | None,
    now: datetime,
) -> tuple[int, Decimal]:
    edge = Decimal("0")
    if target and target.get("candidate_edge"):
        edge = required_decimal(target["candidate_edge"], label="candidate_edge")
    if security_id in holding_ids:
        return 96, edge
    if security_id in pending_ids:
        return 94, edge
    if target and required_decimal(target["target_weight_pct"], label="target_weight_pct") > 0:
        return 92, edge
    if target and target.get("rank"):
        return 88, edge
    expires = parse_timestamp(assessment["expires_at"]) if assessment else None
    if expires is None or expires <= now:
        return 84, edge
    if assessment and assessment.get("assessment_schema_version") != "2":
        return 80, edge
    return 70, edge


def migrate_legacy_assessments(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    enqueue_limit: int = 20,
    now: datetime | None = None,
) -> AssessmentMigrationResult:
    """Archive current v1 assessments without inventing values and queue bounded v2 refreshes."""

    from papertrader.queue import enqueue_operation

    _identifier(run_id, label="run_id")
    if enqueue_limit < 0 or enqueue_limit > 100:
        raise ResearchStateError("enqueue_limit must be between 0 and 100")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    migration_version = "assessment-v2-migration-v1"
    current = read_table(repository_root, "security_assessments")
    history = read_table(repository_root, "security_assessment_history")
    history_by_id = {row["assessment_id"]: row for row in history}
    latest_by_security = {
        row["security_id"]: row
        for row in sorted(history, key=lambda value: (value["recorded_at"], value["assessment_id"]))
    }
    additions: list[dict[str, str]] = []
    normalized_current: list[dict[str, str]] = []
    existing_count = 0
    for assessment in sorted(current, key=lambda row: row["security_id"]):
        if assessment.get("assessment_schema_version") == "2":
            normalized_current.append(dict(assessment))
            continue
        normalized = dict(assessment)
        normalized["assessment_schema_version"] = "legacy_v1"
        normalized_current.append(normalized)
        source_operation = _legacy_source_operation(repository_root, normalized)
        security = next(
            row
            for row in read_table(repository_root, "securities")
            if row["security_id"] == normalized["security_id"]
        )
        research_page = security["research_page"]
        research_page_hash = ""
        if research_page:
            page = repository_root.joinpath(*PurePosixPath(research_page).parts)
            if page.is_file() and not page.is_symlink():
                research_page_hash = content_hash(page.read_bytes())
        identity = {
            **normalized,
            "source_operation_id": source_operation["operation_id"] if source_operation else "",
            "source_result_path": source_operation["result_path"] if source_operation else "",
            "research_page": research_page,
            "research_page_hash": research_page_hash,
        }
        assessment_id = stable_id("assessment", content_hash(identity))
        if assessment_id in history_by_id:
            existing_count += 1
            latest_by_security[normalized["security_id"]] = history_by_id[assessment_id]
            continue
        previous = latest_by_security.get(normalized["security_id"])
        history_row = {
            "assessment_id": assessment_id,
            "previous_assessment_id": previous["assessment_id"] if previous else "",
            **identity,
            "recorded_at": format_timestamp(instant),
        }
        additions.append(history_row)
        history_by_id[assessment_id] = history_row
        latest_by_security[normalized["security_id"]] = history_row
    imported = append_unique(
        repository_root,
        "security_assessment_history",
        additions,
        key_columns=("assessment_id",),
    )
    # This replaces the transitional prefix header with the exact current contract. Values are
    # unchanged except for the explicit legacy schema marker and unavailable v2 fields remain blank.
    write_table(repository_root, "security_assessments", normalized_current)

    securities = {row["security_id"]: row for row in read_table(repository_root, "securities")}
    assessments = {
        row["security_id"]: row for row in read_table(repository_root, "security_assessments")
    }
    holding_ids = {
        row["security_id"]
        for row in read_table(repository_root, "portfolio")
        if required_decimal(row["quantity"], label="position quantity") != 0
    }
    active_orders = {
        row["order_id"]
        for row in read_table(repository_root, "orders")
        if row["status"] in {"pending", "open", "partially_filled"}
    }
    pending_ids = {
        row["security_id"]
        for row in read_table(repository_root, "order_legs")
        if row["order_id"] in active_orders
    }
    targets = {row["security_id"]: row for row in read_table(repository_root, "allocation_targets")}
    ranked: list[tuple[int, Decimal, str]] = []
    for security_id in sorted(securities):
        candidate_assessment = assessments.get(security_id)
        if candidate_assessment and candidate_assessment.get("assessment_schema_version") == "2":
            continue
        priority, edge = _migration_priority(
            security_id,
            candidate_assessment,
            holding_ids=holding_ids,
            pending_ids=pending_ids,
            target=targets.get(security_id),
            now=instant,
        )
        ranked.append((priority, edge, security_id))
    selected = sorted(ranked, key=lambda value: (-value[0], -value[1], value[2]))[:enqueue_limit]
    selected_ids: list[str] = []
    created_ids: list[str] = []
    for priority, _edge, security_id in selected:
        candidate_assessment = assessments.get(security_id)
        operation_id, created = enqueue_operation(
            repository_root,
            settings,
            operation_type="security_research",
            entity_type="security",
            entity_id=security_id,
            dedupe_key=f"security_research:{security_id}:{migration_version}",
            prompt=(
                f"Migrate {security_id} to one scenario-complete assessment v2 using current "
                "primary evidence and explicit prior-review comparison."
            ),
            inputs={
                "security_id": security_id,
                "maintenance_mode": "assessment_v2_migration",
                "assessment_state": (
                    candidate_assessment["assessed_at"] if candidate_assessment else "missing"
                ),
                "research_page": securities[security_id]["research_page"],
                "migration_version": migration_version,
            },
            source=f"assessment_v2_migration:{run_id}",
            priority=priority,
            freshness_days=0,
            source_refs=(
                tuple(part for part in candidate_assessment["evidence_refs"].split("|") if part)
                if candidate_assessment
                else ()
            ),
            now=instant,
        )
        selected_ids.append(operation_id)
        if created:
            created_ids.append(operation_id)

    migrated = read_table(repository_root, "security_assessments")
    report = {
        "report_version": 1,
        "migration_version": migration_version,
        "run_id": run_id,
        "as_of": format_timestamp(instant),
        "assessment_schema_distribution": dict(
            sorted(Counter(row["assessment_schema_version"] for row in migrated).items())
        ),
        "rating_distribution": dict(
            sorted(Counter(row["canonical_rating"] or "unavailable" for row in migrated).items())
        ),
        "allocation_eligibility_distribution": dict(
            sorted(
                Counter(row["allocation_eligibility"] or "unavailable" for row in migrated).items()
            )
        ),
        "legacy_score_ranges": {
            field: {
                "minimum": decimal_text(
                    min(
                        (required_decimal(row[field], label=field) for row in migrated),
                        default=Decimal("0"),
                    )
                ),
                "maximum": decimal_text(
                    max(
                        (required_decimal(row[field], label=field) for row in migrated),
                        default=Decimal("0"),
                    )
                ),
            }
            for field in ASSESSMENT_SCORE_FIELDS
        },
        "allocation_exclusion_reasons": dict(
            sorted(
                Counter(
                    reason
                    for target in targets.values()
                    for reason in target["reason"].split("|")
                    if reason
                ).items()
            )
        ),
        "refresh_security_ids": [security_id for _priority, _edge, security_id in selected],
        "refresh_operation_ids": selected_ids,
        "active_allocation_enabled": (
            settings.allocation.mode != "disabled"
            and sum(
                row["assessment_schema_version"] == "2" and row["research_status"] == "complete"
                for row in migrated
            )
            >= settings.allocation.minimum_diversified_candidates
        ),
    }
    report_path = repository_root / "data" / "runs" / run_id / "research_rollout.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(report_path, report, allowed_root=repository_root)
    return AssessmentMigrationResult(
        migration_version=migration_version,
        imported_history_rows=imported,
        existing_history_rows=existing_count,
        current_rows_rewritten=len(current),
        refreshes_selected=tuple(selected_ids),
        operations_created=tuple(created_ids),
        report_path=report_path.relative_to(repository_root).as_posix(),
    )


def enqueue_assessment_issue_recovery(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    now: datetime | None = None,
) -> Mapping[str, object]:
    """Enqueue one bounded review per security with an unresolved assessment failure."""

    from papertrader.queue import enqueue_operation

    _identifier(run_id, label="run_id")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    issues_by_security: dict[str, list[str]] = {}
    for issue in read_table(repository_root, "issues"):
        if (
            issue["status"] == "open"
            and issue["issue_code"] == "assessment_update_failed"
            and issue["entity_type"] == "security"
        ):
            issues_by_security.setdefault(issue["entity_id"], []).append(issue["issue_id"])
    securities = {row["security_id"]: row for row in read_table(repository_root, "securities")}
    operation_ids: list[str] = []
    created_ids: list[str] = []
    for security_id in sorted(issues_by_security):
        if security_id not in securities:
            raise ResearchStateError(
                f"assessment recovery issue references unknown security: {security_id}"
            )
        issue_ids = tuple(sorted(issues_by_security[security_id]))
        cause_hash = content_hash(issue_ids)[:16]
        operation_id, created = enqueue_operation(
            repository_root,
            settings,
            operation_type="security_research",
            entity_type="security",
            entity_id=security_id,
            dedupe_key=(f"security_research:{security_id}:assessment-issue-recovery:{cause_hash}"),
            prompt=(
                f"Repair the unresolved assessment for {security_id} with current primary "
                "evidence and explicit source-operation provenance."
            ),
            inputs={
                "security_id": security_id,
                "maintenance_mode": "assessment_issue_recovery",
                "issue_ids": list(issue_ids),
                "research_page": securities[security_id]["research_page"],
            },
            source=f"issue_reconciliation:{run_id}",
            priority=72,
            freshness_days=0,
            now=instant,
        )
        operation_ids.append(operation_id)
        if created:
            created_ids.append(operation_id)
    return {
        "security_count": len(issues_by_security),
        "operation_ids": tuple(operation_ids),
        "created_operation_ids": tuple(created_ids),
    }


def import_watchlist(
    repository_root: Path,
    settings: Settings,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> dict[str, object]:
    """Atomically add identity-only securities without inventing research state."""

    if set(raw) != {"watchlist_reason", "source", "securities"}:
        raise ResearchStateError(
            "watchlist import requires exactly watchlist_reason, source, and securities"
        )
    watchlist_reason = raw["watchlist_reason"]
    source = raw["source"]
    securities = raw["securities"]
    if not isinstance(watchlist_reason, str) or not watchlist_reason.strip():
        raise ResearchStateError("watchlist_reason must be a non-empty string")
    if not isinstance(source, str):
        raise ResearchStateError("watchlist source must be a string")
    parsed_source = urlsplit(source.strip())
    if parsed_source.scheme not in {"http", "https"} or not parsed_source.netloc:
        raise ResearchStateError("watchlist source must be an HTTP(S) URL")
    if not isinstance(securities, list) or not securities:
        raise ResearchStateError("watchlist securities must be a non-empty list")

    existing = read_table(repository_root, "securities")
    output = [dict(row) for row in existing]
    by_provider_identity = {
        (row["provider_symbol"], row["venue_mic"], row["currency"]): row for row in output
    }
    seen_provider_identities: set[tuple[str, str, str]] = set()
    created_ids: list[str] = []
    unchanged_ids: list[str] = []
    instant = format_timestamp(ensure_utc(now or utc_now()).replace(microsecond=0))

    for index, value in enumerate(securities, start=1):
        if not isinstance(value, Mapping):
            raise ResearchStateError(f"watchlist security {index} must be an object")
        fields = _exact_strings(
            value,
            WATCHLIST_SECURITY_FIELDS,
            label=f"watchlist security {index}",
        )
        _required(fields, WATCHLIST_SECURITY_FIELDS, label=f"watchlist security {index}")
        if fields["instrument_type"] not in settings.risk.allowed_instruments:
            raise ResearchStateError(f"watchlist security {index} instrument_type is not allowed")
        if fields["venue_mic"] not in settings.risk.allowed_exchanges:
            raise ResearchStateError(f"watchlist security {index} venue_mic is not allowed")
        if fields["currency"] not in settings.risk.allowed_currencies:
            raise ResearchStateError(f"watchlist security {index} currency is not allowed")
        if not re.fullmatch(r"[A-Z0-9]{4}", fields["venue_mic"]):
            raise ResearchStateError(f"watchlist security {index} venue_mic is invalid")
        if not re.fullmatch(r"[A-Z]{3}", fields["currency"]):
            raise ResearchStateError(f"watchlist security {index} currency is invalid")
        if not re.fullmatch(r"[A-Z]{2}", fields["country"]):
            raise ResearchStateError(f"watchlist security {index} country is invalid")

        provider_identity = (
            fields["provider_symbol"],
            fields["venue_mic"],
            fields["currency"],
        )
        if provider_identity in seen_provider_identities:
            raise ResearchStateError(
                f"watchlist contains duplicate provider identity: {provider_identity!r}"
            )
        seen_provider_identities.add(provider_identity)
        previous = by_provider_identity.get(provider_identity)
        if previous is not None:
            unchanged_ids.append(previous["security_id"])
            continue

        issuer_id = stable_id("issuer", fields["company_name"].casefold())
        security_id = stable_id(
            "security",
            fields["provider_symbol"],
            fields["venue_mic"],
            fields["currency"],
            fields["instrument_type"],
        )
        row = {
            "security_id": security_id,
            "issuer_id": issuer_id,
            **fields,
            "broker_symbol": "",
            "status": "watchlist",
            "watchlist_reason": " ".join(watchlist_reason.split()),
            "research_summary": "",
            "research_page": "",
            "last_research_at": "",
            "next_review_at": "",
            "created_at": instant,
            "updated_at": instant,
            "source": source.strip(),
        }
        output.append(row)
        by_provider_identity[provider_identity] = row
        created_ids.append(security_id)

    if created_ids:
        output.sort(key=lambda row: row["security_id"])
        write_table(repository_root, "securities", output)
    return {
        "created": len(created_ids),
        "created_security_ids": sorted(created_ids),
        "unchanged": len(unchanged_ids),
        "unchanged_security_ids": sorted(unchanged_ids),
    }


def upsert_security(
    repository_root: Path,
    settings: Settings,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> bool:
    """Insert or update one security while preserving its immutable provider identity."""

    columns = contract_by_name(repository_root, "securities").columns
    input_columns = tuple(
        column for column in columns if column not in {"created_at", "updated_at"}
    )
    values = _exact_strings(raw, input_columns, label="security")
    _required(
        values,
        (
            "security_id",
            "issuer_id",
            "company_name",
            "instrument_name",
            "instrument_type",
            "ticker",
            "exchange_code",
            "venue_mic",
            "provider_symbol",
            "currency",
            "country",
            "status",
            "research_summary",
            "research_page",
            "last_research_at",
            "next_review_at",
            "source",
        ),
        label="security",
    )
    _identifier(values["security_id"], label="security_id")
    _identifier(values["issuer_id"], label="issuer_id")
    if values["instrument_type"] not in settings.risk.allowed_instruments:
        raise ResearchStateError("security instrument_type is not allowed")
    if values["venue_mic"] not in settings.risk.allowed_exchanges:
        raise ResearchStateError("security venue_mic is not allowed")
    if values["currency"] not in settings.risk.allowed_currencies:
        raise ResearchStateError("security currency is not allowed")
    if len(values["research_summary"]) > 500:
        raise ResearchStateError("security research_summary exceeds 500 characters")
    values["research_page"] = _wiki_page(repository_root, values["research_page"], "securities")
    values["last_research_at"] = _canonical_timestamp(
        values["last_research_at"], label="last_research_at"
    )
    values["next_review_at"] = _canonical_timestamp(
        values["next_review_at"], label="next_review_at"
    )
    if values["next_review_at"] <= values["last_research_at"]:
        raise ResearchStateError("security next_review_at must follow last_research_at")
    rows = read_table(repository_root, "securities")
    previous = next((row for row in rows if row["security_id"] == values["security_id"]), None)
    if previous and any(previous[field] != values[field] for field in IMMUTABLE_SECURITY_FIELDS):
        raise ResearchStateError("security update conflicts with immutable identity")
    if (
        previous
        and previous["last_research_at"]
        and values["last_research_at"] < previous["last_research_at"]
    ):
        raise ResearchStateError("security update is older than current research state")
    identity = tuple(values[field] for field in IMMUTABLE_SECURITY_FIELDS)
    duplicate = next(
        (
            row
            for row in rows
            if row["security_id"] != values["security_id"]
            and tuple(row[field] for field in IMMUTABLE_SECURITY_FIELDS) == identity
        ),
        None,
    )
    if duplicate:
        raise ResearchStateError(f"security identity duplicates {duplicate['security_id']}")
    if previous and all(previous[field] == values[field] for field in input_columns):
        return False
    instant = format_timestamp(ensure_utc(now or utc_now()).replace(microsecond=0))
    row = {
        **values,
        "created_at": previous["created_at"] if previous else instant,
        "updated_at": instant,
    }
    return _replace_row(repository_root, "securities", row, key="security_id")


def upsert_relationship(
    repository_root: Path,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> bool:
    """Insert or update one explicit idea-security causal edge."""

    columns = contract_by_name(repository_root, "relationships").columns
    input_columns = tuple(
        column for column in columns if column not in {"created_at", "updated_at"}
    )
    values = _exact_strings(raw, input_columns, label="relationship")
    _required(values, input_columns, label="relationship")
    for field in ("relationship_id", "idea_id", "security_id"):
        _identifier(values[field], label=field)
    if not any(
        row["security_id"] == values["security_id"]
        for row in read_table(repository_root, "securities")
    ):
        raise ResearchStateError("relationship references an unknown security_id")
    idea_page = repository_root / "data" / "wiki" / "ideas" / f"{values['idea_id']}.md"
    if idea_page.is_symlink() or not idea_page.is_file():
        raise ResearchStateError("relationship references an idea without its canonical wiki page")
    values["research_page"] = _wiki_page(repository_root, values["research_page"], "relationships")
    values["last_reviewed_at"] = _canonical_timestamp(
        values["last_reviewed_at"], label="last_reviewed_at"
    )
    values["next_review_at"] = _canonical_timestamp(
        values["next_review_at"], label="next_review_at"
    )
    if values["next_review_at"] <= values["last_reviewed_at"]:
        raise ResearchStateError("relationship next_review_at must follow last_reviewed_at")
    rows = read_table(repository_root, "relationships")
    previous = next(
        (row for row in rows if row["relationship_id"] == values["relationship_id"]), None
    )
    if previous and any(previous[field] != values[field] for field in ("idea_id", "security_id")):
        raise ResearchStateError("relationship update conflicts with immutable endpoints")
    if (
        previous
        and previous["last_reviewed_at"]
        and values["last_reviewed_at"] < previous["last_reviewed_at"]
    ):
        raise ResearchStateError("relationship update is older than current research state")
    duplicate = next(
        (
            row
            for row in rows
            if row["relationship_id"] != values["relationship_id"]
            and row["idea_id"] == values["idea_id"]
            and row["security_id"] == values["security_id"]
            and row["relationship_type"] == values["relationship_type"]
        ),
        None,
    )
    if duplicate:
        raise ResearchStateError(f"relationship duplicates {duplicate['relationship_id']}")
    if previous and all(previous[field] == values[field] for field in input_columns):
        return False
    instant = format_timestamp(ensure_utc(now or utc_now()).replace(microsecond=0))
    row = {
        **values,
        "created_at": previous["created_at"] if previous else instant,
        "updated_at": instant,
    }
    return _replace_row(repository_root, "relationships", row, key="relationship_id")


def _strategy_leg(raw: Mapping[str, object]) -> tuple[OrderLegSpec, str]:
    expected = {
        "leg_id",
        "action",
        "side",
        "instrument_type",
        "security_id",
        "provider_contract_id",
        "option_type",
        "expiry",
        "strike",
        "quantity",
        "contract_multiplier",
        "order_type",
        "limit_price",
        "currency",
    }
    if set(raw) != expected:
        raise ResearchStateError("strategy leg fields differ from the canonical contract")
    order_type = raw["order_type"]
    if order_type not in {"market", "limit"}:
        raise ResearchStateError("strategy leg order_type must be market or limit")
    order_raw = {key: value for key, value in raw.items() if key != "order_type"}
    try:
        leg = leg_from_mapping(order_raw)
    except (CanonicalValueError, RuntimeError, ValueError) as exc:
        raise ResearchStateError(str(exc)) from exc
    if order_type == "limit" and leg.limit_price is None:
        raise ResearchStateError("limit strategy leg requires limit_price")
    return leg, str(order_type)


def _strategy_leg_row(strategy_id: str, leg: OrderLegSpec, order_type: str) -> dict[str, str]:
    return {
        "strategy_id": strategy_id,
        "leg_id": leg.leg_id,
        "action": leg.action,
        "side": leg.side,
        "instrument_type": leg.instrument_type,
        "security_id": leg.security_id,
        "provider_contract_id": leg.provider_contract_id,
        "option_type": leg.option_type,
        "expiry": leg.expiry.isoformat() if leg.expiry else "",
        "strike": decimal_text(leg.strike) if leg.strike is not None else "",
        "quantity": decimal_text(leg.quantity),
        "contract_multiplier": decimal_text(leg.contract_multiplier),
        "order_type": order_type,
        "limit_price": decimal_text(leg.limit_price) if leg.limit_price is not None else "",
        "currency": leg.currency,
    }


def upsert_strategy(
    repository_root: Path,
    settings: Settings,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> bool:
    """Upsert one evidence-linked strategy and its normalized deterministic legs."""

    if (
        set(raw) != {"strategy", "legs"}
        or not isinstance(raw["strategy"], dict)
        or not isinstance(raw["legs"], list)
    ):
        raise ResearchStateError("strategy request requires one strategy object and a legs array")
    columns = contract_by_name(repository_root, "strategies").columns
    input_columns = tuple(
        column for column in columns if column not in {"created_at", "updated_at"}
    )
    strategy_request = dict(raw["strategy"])
    instant_dt = ensure_utc(now or utc_now()).replace(microsecond=0)
    # Preserve the pre-Step-8 conviction request shape while storing explicit sleeve metadata.
    if "sleeve" not in strategy_request and "allocation_plan_id" not in strategy_request:
        strategy_request["sleeve"] = "conviction"
        strategy_request["allocation_plan_id"] = ""
    if "allocation_intent_id" not in strategy_request:
        strategy_request["allocation_intent_id"] = ""
    values = _exact_strings(strategy_request, input_columns, label="strategy")
    _required(
        values,
        tuple(
            column
            for column in input_columns
            if column
            not in {"allocation_plan_id", "allocation_intent_id", "not_before", "expires_at"}
        ),
        label="strategy",
    )
    for field in ("strategy_id", "idea_id", "security_id", "relationship_id"):
        _identifier(values[field], label=field)
    if values["status"] not in STRATEGY_STATUSES:
        raise ResearchStateError("strategy status is not canonical")
    if values["instrument_type"] not in settings.risk.allowed_instruments:
        raise ResearchStateError("strategy instrument_type is not allowed")
    risk_budget = required_decimal(values["risk_budget_pct"], label="risk_budget_pct")
    if not Decimal("0") < risk_budget <= Decimal("100"):
        raise ResearchStateError("strategy risk_budget_pct must be within (0, 100]")
    values["risk_budget_pct"] = decimal_text(risk_budget)
    if values["sleeve"] not in STRATEGY_SLEEVES:
        raise ResearchStateError("strategy sleeve must be conviction or baseline")
    if values["sleeve"] == "conviction" and (
        values["allocation_plan_id"] or values["allocation_intent_id"]
    ):
        raise ResearchStateError("conviction strategy must not reference an allocation intent")
    if values["sleeve"] == "baseline":
        _identifier(values["allocation_plan_id"], label="allocation_plan_id")
        if values["instrument_type"] != "equity" or values["direction"] != "long":
            raise ResearchStateError("baseline strategies must be long equity")
        from papertrader.allocation import baseline_strategy_id

        if values["strategy_id"] != baseline_strategy_id(values["security_id"]):
            raise ResearchStateError("baseline strategy_id is not the stable security identity")
        target = next(
            (
                row
                for row in read_table(repository_root, "allocation_targets")
                if row["strategy_id"] == values["strategy_id"]
            ),
            None,
        )
        if not values["allocation_intent_id"] and target is not None:
            values["allocation_intent_id"] = target["allocation_intent_id"]
        if values["allocation_intent_id"]:
            _identifier(values["allocation_intent_id"], label="allocation_intent_id")
        if values["status"] in {"ready", "active"}:
            if (
                target is None
                or target["allocation_plan_id"] != values["allocation_plan_id"]
                or target["allocation_intent_id"] != values["allocation_intent_id"]
                or target["security_id"] != values["security_id"]
            ):
                raise ResearchStateError("baseline strategy requires its current allocation target")
            target_time = parse_timestamp(target["as_of"])
            assert target_time is not None
            if (
                target_time > instant_dt
                or instant_dt - target_time > settings.market_data.stale_price_after
            ):
                raise ResearchStateError(
                    "baseline strategy allocation plan is stale or future-dated"
                )
            assessment = next(
                (
                    row
                    for row in read_table(repository_root, "security_assessments")
                    if row["security_id"] == values["security_id"]
                ),
                None,
            )
            if (
                assessment is None
                or assessment["assessed_at"] != target["assessment_as_of"]
                or target["disposition"] not in {"open", "increase", "reduce", "close"}
            ):
                raise ResearchStateError(
                    "baseline strategy requires the unchanged material plan assessment"
                )
            if target["disposition"] in {"open", "increase"} and target["tier"] not in {
                "full",
                "starter",
            }:
                raise ResearchStateError(
                    "non-investable live valuation tier cannot increase baseline exposure"
                )
        expected_risk_budget = (
            required_decimal(target["position_cap_pct"], label="target position cap")
            if target is not None and target["position_cap_pct"]
            else settings.allocation.maximum_baseline_position_pct
        )
        if risk_budget != expected_risk_budget:
            raise ResearchStateError(
                "baseline strategy risk budget must equal the configured position cap "
                "for its allocation tier"
            )
    values["not_before"] = _canonical_timestamp(
        values["not_before"], label="not_before", allow_empty=True
    )
    values["expires_at"] = _canonical_timestamp(
        values["expires_at"], label="expires_at", allow_empty=True
    )
    if (
        values["not_before"]
        and values["expires_at"]
        and values["not_before"] >= values["expires_at"]
    ):
        raise ResearchStateError("strategy not_before must precede expires_at")
    relationship = next(
        (
            row
            for row in read_table(repository_root, "relationships")
            if row["relationship_id"] == values["relationship_id"]
        ),
        None,
    )
    if (
        relationship is None
        or relationship["idea_id"] != values["idea_id"]
        or relationship["security_id"] != values["security_id"]
    ):
        raise ResearchStateError("strategy identity does not match its relationship endpoints")
    values["research_page"] = _wiki_page(repository_root, values["research_page"], "strategies")
    raw_legs = raw["legs"]
    if not all(isinstance(value, dict) for value in raw_legs):
        raise ResearchStateError("every strategy leg must be an object")
    parsed = [_strategy_leg(value) for value in raw_legs if isinstance(value, dict)]
    if values["sleeve"] == "baseline":
        if len(parsed) != 1:
            raise ResearchStateError("baseline strategy requires exactly one equity leg")
        baseline_leg = parsed[0][0]
        if (
            baseline_leg.instrument_type != "equity"
            or baseline_leg.side != "long"
            or baseline_leg.action != "buy"
            or baseline_leg.security_id != values["security_id"]
        ):
            raise ResearchStateError("baseline strategy leg must open its own long equity")
    if values["status"] in {"ready", "active"} and not parsed:
        raise ResearchStateError("ready or active strategy requires at least one normalized leg")
    leg_ids = [leg.leg_id for leg, _ in parsed]
    if len(leg_ids) != len(set(leg_ids)):
        raise ResearchStateError("strategy leg_id values must be unique")
    securities = {row["security_id"] for row in read_table(repository_root, "securities")}
    if any(leg.security_id not in securities for leg, _ in parsed):
        raise ResearchStateError("strategy leg references an unknown security")
    if any(
        leg.instrument_type not in settings.risk.allowed_instruments
        or leg.currency not in settings.risk.allowed_currencies
        for leg, _ in parsed
    ):
        raise ResearchStateError("strategy leg violates instrument or currency allowlists")
    rows = read_table(repository_root, "strategies")
    previous = next((row for row in rows if row["strategy_id"] == values["strategy_id"]), None)
    if previous and any(
        previous[field] != values[field] for field in ("idea_id", "security_id", "relationship_id")
    ):
        raise ResearchStateError("strategy update conflicts with immutable research identity")
    existing_legs = read_table(repository_root, "strategy_legs")
    leg_rows = [
        _strategy_leg_row(values["strategy_id"], leg, order_type) for leg, order_type in parsed
    ]
    leg_rows.sort(key=lambda candidate: (candidate["strategy_id"], candidate["leg_id"]))
    current_strategy_legs = [
        candidate
        for candidate in existing_legs
        if candidate["strategy_id"] == values["strategy_id"]
    ]
    if (
        previous
        and previous["status"] in {"active", "closed", "expired"}
        and values["status"] in {"draft", "researching", "ready"}
    ):
        unchanged_research = all(
            previous[field] == values[field] for field in input_columns if field != "status"
        )
        if unchanged_research and current_strategy_legs == leg_rows:
            return False
        raise ResearchStateError(
            f"strategy update would regress lifecycle status {previous['status']} to "
            f"{values['status']}"
        )
    if (
        previous
        and all(previous[field] == values[field] for field in input_columns)
        and current_strategy_legs == leg_rows
    ):
        return False
    instant = format_timestamp(instant_dt)
    row = {
        **values,
        "created_at": previous["created_at"] if previous else instant,
        "updated_at": instant,
    }
    strategy_changed = _replace_row(repository_root, "strategies", row, key="strategy_id")
    output_legs = [
        candidate
        for candidate in existing_legs
        if candidate["strategy_id"] != values["strategy_id"]
    ]
    output_legs.extend(leg_rows)
    output_legs.sort(key=lambda candidate: (candidate["strategy_id"], candidate["leg_id"]))
    legs_changed = output_legs != existing_legs
    if legs_changed:
        write_table(repository_root, "strategy_legs", output_legs)
    return strategy_changed or legs_changed


def record_source(
    repository_root: Path,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> tuple[str, bool]:
    """Record one source observation in the mutable registry and immutable history."""

    expected = (
        "source_id",
        "url",
        "canonical_url",
        "source_type",
        "title",
        "publisher",
        "license",
        "status",
        "content_hash",
        "related_entity_ids",
        "checked_at",
        "http_status",
        "changed",
        "excerpt",
        "summary",
        "run_id",
    )
    values = _exact_strings(raw, expected, label="source")
    _required(
        values,
        (
            "source_id",
            "url",
            "canonical_url",
            "source_type",
            "title",
            "publisher",
            "status",
            "content_hash",
            "checked_at",
            "changed",
            "summary",
            "run_id",
        ),
        label="source",
    )
    _identifier(values["source_id"], label="source_id")
    for field in ("url", "canonical_url"):
        parsed = urlsplit(values[field])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ResearchStateError(f"source {field} must be an HTTP(S) URL")
    if not re.fullmatch(r"[a-f0-9]{64}", values["content_hash"]):
        raise ResearchStateError("source content_hash must be lowercase SHA-256")
    if values["changed"] not in {"true", "false"}:
        raise ResearchStateError("source changed must be true or false")
    if len(values["excerpt"]) > 1000 or len(values["summary"]) > 2000:
        raise ResearchStateError("source excerpt or summary exceeds its bounded length")
    checked = _canonical_timestamp(values["checked_at"], label="checked_at")
    checked_at = parse_timestamp(checked)
    assert checked_at is not None
    registry = read_table(repository_root, "source_registry")
    previous = next((row for row in registry if row["source_id"] == values["source_id"]), None)
    if previous and previous["canonical_url"] != values["canonical_url"]:
        raise ResearchStateError("source update conflicts with immutable canonical_url")
    if previous and checked < previous["last_checked_at"]:
        raise ResearchStateError("source observation is older than the current registry state")
    previous_first_seen = parse_timestamp(previous["first_seen_at"]) if previous else None
    first_seen_at = format_timestamp(
        min(checked_at, previous_first_seen) if previous_first_seen else checked_at
    )
    previous_last_changed = previous["last_changed_at"] if previous else ""
    registry_row = {
        "source_id": values["source_id"],
        "url": values["url"],
        "canonical_url": values["canonical_url"],
        "source_type": values["source_type"],
        "title": values["title"],
        "publisher": values["publisher"],
        "license": values["license"],
        "status": values["status"],
        "content_hash": values["content_hash"],
        # The observation timestamp is authoritative when an immutable history row is
        # replayed after its original run. This keeps reconstructed registry state
        # consistent with assessments that were already completed against that evidence.
        "first_seen_at": first_seen_at,
        "last_checked_at": checked,
        "last_changed_at": (
            checked
            if values["changed"] == "true" or not previous_last_changed
            else previous_last_changed
        ),
        "related_entity_ids": values["related_entity_ids"],
    }
    history_id = stable_id("source_history", values["source_id"], checked, values["content_hash"])
    history_row = {
        "source_history_id": history_id,
        "source_id": values["source_id"],
        "checked_at": checked,
        "status": values["status"],
        "http_status": values["http_status"],
        "content_hash": values["content_hash"],
        "changed": values["changed"],
        "excerpt": values["excerpt"],
        "summary": values["summary"],
        "run_id": values["run_id"],
    }
    previous_history = next(
        (
            row
            for row in read_table(repository_root, "source_history")
            if row["source_history_id"] == history_id
        ),
        None,
    )
    if previous_history is not None and previous_history != history_row:
        raise ResearchStateError(f"source history identity collision: {history_id}")
    registry_changed = _replace_row(
        repository_root, "source_registry", registry_row, key="source_id"
    )
    appended = append_unique(
        repository_root,
        "source_history",
        [history_row],
        key_columns=("source_history_id",),
    )
    return history_id, registry_changed or bool(appended)


__all__ = [
    "ASSESSMENT_CONFIDENCE",
    "ASSESSMENT_ELIGIBILITY",
    "HARD_BLOCKERS",
    "SOFT_GAPS",
    "ResearchStateError",
    "enqueue_assessment_issue_recovery",
    "record_source",
    "upsert_assessment",
    "upsert_relationship",
    "upsert_security",
    "upsert_strategy",
]

"""Repository-local issue lifecycle and generated human-readable dashboard."""

from __future__ import annotations

import csv
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path

from papertrader.atomic_io import atomic_write_text
from papertrader.tables import contract_by_name, read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    format_timestamp,
    parse_timestamp,
    stable_id,
    utc_now,
)

ISSUE_STATUSES = frozenset({"open", "resolved"})
ISSUE_SEVERITIES = frozenset({"info", "warning", "error", "critical"})
ISSUE_IMPACTS = frozenset(
    {
        "blocks_portfolio",
        "blocks_action",
        "affects_candidate",
        "publication_only",
        "operational_only",
    }
)
ISSUE_CODE = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
ISSUE_ENTITY_TYPE = re.compile(r"^[a-z][a-z0-9_]{1,31}$")
SECURITY_ID = re.compile(r"security_[0-9a-f]{20}")
FX_PAIR = re.compile(r"\b([A-Z]{3})/([A-Z]{3})\b")
LEGACY_ISSUE_COLUMNS = (
    "issue_id",
    "status",
    "severity",
    "title",
    "description",
    "owner",
    "first_seen_at",
    "last_seen_at",
    "related_run_id",
    "related_operation_id",
    "resolution",
    "resolved_at",
)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _dashboard(rows: Sequence[Mapping[str, str]]) -> str:
    open_rows = sorted(
        (row for row in rows if row["status"] == "open"),
        key=lambda row: (
            {"critical": 0, "error": 1, "warning": 2, "info": 3}.get(row["severity"], 4),
            row["issue_id"],
        ),
    )
    lines = ["# PaperTrader issues", "", "Generated from `data/tables/issues.csv`.", ""]
    if not open_rows:
        lines.extend(["No open issues.", ""])
        return "\n".join(lines)
    lines.extend(
        [
            "| Impact | Severity | Issue | Last seen | Owner | Related operation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in open_rows:
        title = _cell(row["title"])
        lines.append(
            f"| {_cell(row['impact'])} | {_cell(row['severity'])} | "
            f"**{_cell(row['issue_id'])}** — {title} | "
            f"{_cell(row['last_seen_at'])} | {_cell(row['owner'])} | "
            f"{_cell(row['related_operation_id'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def regenerate_issue_dashboard(repository_root: Path) -> None:
    """Regenerate ``data/issues.md`` from canonical issue state."""

    content = _dashboard(read_table(repository_root, "issues"))
    atomic_write_text(
        repository_root / "data" / "issues.md",
        content,
        allowed_root=repository_root,
    )


def record_issue(
    repository_root: Path,
    *,
    issue_code: str,
    impact: str,
    severity: str,
    title: str,
    description: str,
    entity_type: str = "",
    entity_id: str = "",
    owner: str = "",
    related_run_id: str = "",
    related_operation_id: str = "",
    now: datetime | None = None,
) -> str:
    """Create or refresh one stable open issue and regenerate its dashboard."""

    if not ISSUE_CODE.fullmatch(issue_code):
        raise CanonicalValueError(f"invalid issue_code: {issue_code!r}")
    if impact not in ISSUE_IMPACTS:
        raise CanonicalValueError(f"unknown issue impact: {impact!r}")
    if severity not in ISSUE_SEVERITIES:
        raise CanonicalValueError(f"unknown issue severity: {severity!r}")
    entity_type = " ".join(entity_type.split())
    entity_id = " ".join(entity_id.split())
    if bool(entity_type) != bool(entity_id):
        raise CanonicalValueError("issue entity_type and entity_id must both be set or empty")
    if entity_type and not ISSUE_ENTITY_TYPE.fullmatch(entity_type):
        raise CanonicalValueError(f"invalid issue entity_type: {entity_type!r}")
    title = " ".join(title.split())
    description = " ".join(description.split())
    owner = " ".join(owner.split())
    related_run_id = " ".join(related_run_id.split())
    related_operation_id = " ".join(related_operation_id.split())
    if not title or not description:
        raise CanonicalValueError("issue title and description are required")
    timestamp = format_timestamp(now or utc_now())
    rows = read_table(repository_root, "issues")
    matches = [
        row
        for row in rows
        if row["issue_code"] == issue_code
        and row["entity_type"] == entity_type
        and row["entity_id"] == entity_id
    ]
    previous = max(matches, key=lambda row: (row["last_seen_at"], row["issue_id"]), default=None)
    issue_id = (
        previous["issue_id"]
        if previous is not None
        else stable_id("issue", issue_code, entity_type, entity_id)
    )
    row = {
        "issue_id": issue_id,
        "status": "open",
        "severity": severity,
        "issue_code": issue_code,
        "impact": impact,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "title": title,
        "description": description,
        "owner": owner,
        "first_seen_at": previous["first_seen_at"] if previous else timestamp,
        "last_seen_at": timestamp,
        "related_run_id": previous["related_run_id"] if previous else related_run_id,
        "related_operation_id": related_operation_id,
        "resolution": "",
        "resolved_at": "",
    }
    output = [candidate for candidate in rows if candidate["issue_id"] != issue_id]
    output.append(row)
    output.sort(key=lambda candidate: candidate["issue_id"])
    write_table(repository_root, "issues", output)
    regenerate_issue_dashboard(repository_root)
    return issue_id


def resolve_matching_issues(
    repository_root: Path,
    *,
    issue_code: str,
    entity_type: str,
    entity_id: str,
    resolution: str,
    now: datetime | None = None,
) -> tuple[str, ...]:
    """Resolve every open issue with one producer-owned stable identity."""

    rows = read_table(repository_root, "issues")
    issue_ids = tuple(
        row["issue_id"]
        for row in rows
        if row["status"] == "open"
        and row["issue_code"] == issue_code
        and row["entity_type"] == entity_type
        and row["entity_id"] == entity_id
    )
    for issue_id in issue_ids:
        resolve_issue(repository_root, issue_id, resolution, now=now)
    return issue_ids


def operation_validation_impact(operation_type: str) -> str:
    """Return the bounded health effect of one failed agent-result validation."""

    if operation_type == "daily_podcast":
        return "publication_only"
    if operation_type == "execute_strategy":
        return "blocks_action"
    if operation_type in {
        "opportunity_research",
        "quick_check_research",
        "idea_research",
        "security_research",
        "relationship_research",
        "strategy_research",
    }:
        return "affects_candidate"
    return "operational_only"


def resolve_issue(
    repository_root: Path,
    issue_id: str,
    resolution: str,
    *,
    now: datetime | None = None,
) -> None:
    """Resolve an existing issue without deleting its canonical history row."""

    resolution = " ".join(resolution.split())
    if not resolution:
        raise CanonicalValueError("issue resolution is required")
    rows = read_table(repository_root, "issues")
    timestamp = format_timestamp(now or utc_now())
    found = False
    for row in rows:
        if row["issue_id"] != issue_id:
            continue
        found = True
        if row["status"] == "resolved":
            if row["resolution"] != resolution:
                raise CanonicalValueError(f"issue {issue_id} is already resolved differently")
            return
        row["status"] = "resolved"
        row["resolution"] = resolution
        row["resolved_at"] = timestamp
    if not found:
        raise CanonicalValueError(f"unknown issue: {issue_id}")
    write_table(repository_root, "issues", rows)
    regenerate_issue_dashboard(repository_root)


def _operation_rows(repository_root: Path) -> dict[str, dict[str, str]]:
    return {
        row["operation_id"]: row
        for table in ("operations_todo", "operations_history")
        for row in read_table(repository_root, table)
    }


def _legacy_identity(
    row: Mapping[str, str], operations: Mapping[str, Mapping[str, str]]
) -> tuple[str, str, str, str]:
    """Map a legacy issue using producer provenance; text is used only for this migration."""

    title = row["title"]
    text = f"{title} {row['description']}".lower()
    owner = row["owner"]
    operation = operations.get(row["related_operation_id"], {})
    operation_type = operation.get("operation_type", "")
    operation_entity = operation.get("entity_id", "")
    security_match = SECURITY_ID.search(f"{title} {row['description']}")
    security_id = security_match.group(0) if security_match else ""

    if title.startswith("Telegram podcast audio"):
        return (
            "telegram_podcast_audio_delivery_failed",
            "publication_only",
            "delivery",
            "podcast_audio",
        )
    if title.startswith("Telegram podcast script"):
        return (
            "telegram_podcast_script_delivery_failed",
            "publication_only",
            "delivery",
            "podcast_script",
        )
    if title.startswith("Telegram delivery failed"):
        return "telegram_report_delivery_failed", "publication_only", "delivery", "daily_report"
    if title.startswith("Daily podcast"):
        entity_id = row["related_operation_id"] or row["related_run_id"]
        entity_type = "operation" if row["related_operation_id"] else "daily_run"
        return "daily_podcast_terminal", "publication_only", entity_type, entity_id
    if owner == "youtube-discovery" or title.startswith("YouTube discovery"):
        channel = title.rsplit(" ", maxsplit=1)[-1]
        return "youtube_discovery_failed", "operational_only", "channel", channel
    if title.startswith("Daily preparation degraded"):
        if security_id:
            return "daily_market_retrieval_failed", "affects_candidate", "security", security_id
        if "classifier" in text:
            packet = row["description"].split("classifier blocked for ", maxsplit=1)[-1]
            return (
                "daily_classifier_degraded",
                "affects_candidate",
                "candidate_packet",
                packet,
            )
        fx_pair = FX_PAIR.search(f"{title} {row['description']}")
        if fx_pair:
            return (
                "daily_fx_retrieval_failed",
                "affects_candidate",
                "fx_pair",
                f"{fx_pair.group(1)}_{fx_pair.group(2)}",
            )
        return "daily_preparation_degraded", "operational_only", "daily_run", row["related_run_id"]
    if "assessment" in text and (security_id or operation_entity.startswith("security_")):
        return (
            "assessment_update_failed",
            "affects_candidate",
            "security",
            security_id or operation_entity,
        )
    if title.startswith(
        ("Hermes operation validation failed", "Local harness operation validation failed")
    ):
        impact = (
            "publication_only"
            if operation_type == "daily_podcast"
            else "blocks_action"
            if operation_type == "execute_strategy"
            else "affects_candidate"
            if operation_type.endswith("_research")
            else "operational_only"
        )
        return (
            "agent_result_validation_failed",
            impact,
            "operation",
            row["related_operation_id"] or row["related_run_id"],
        )
    if any(token in text for token in ("reconciliation", "cash ledger", "accounting imbalance")):
        return "portfolio_reconciliation_failed", "blocks_portfolio", "system", "portfolio"
    if any(token in text for token in ("active order", "order validation", "execution control")):
        return "action_validation_failed", "blocks_action", "system", "paper_execution"
    if owner == "delivery" or any(token in text for token in ("pages", "publication", "deploy")):
        return "publication_delivery_failed", "publication_only", "daily_run", row["related_run_id"]
    if operation_entity:
        return "operation_failed", "operational_only", "operation", row["related_operation_id"]
    if security_id:
        return "security_data_issue", "affects_candidate", "security", security_id
    entity_id = row["related_run_id"] or row["issue_id"]
    return "legacy_unclassified", "operational_only", "legacy_issue", entity_id


def migrate_issues(repository_root: Path) -> Mapping[str, int]:
    """Upgrade the mutable issue table to explicit producer-owned health fields."""

    path = repository_root / "data" / "tables" / "issues.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        raw_rows = list(reader)
    current_columns = tuple(contract_by_name(repository_root, "issues").columns)
    if fieldnames not in {LEGACY_ISSUE_COLUMNS, current_columns}:
        raise CanonicalValueError(f"unsupported issues.csv header for migration: {fieldnames!r}")
    operations = _operation_rows(repository_root)
    migrated = 0
    rows: list[dict[str, str]] = []
    for raw_row in raw_rows:
        row = {column: raw_row.get(column, "") or "" for column in current_columns}
        if not row["issue_code"]:
            issue_code, impact, entity_type, entity_id = _legacy_identity(row, operations)
            row.update(
                {
                    "issue_code": issue_code,
                    "impact": impact,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                }
            )
            migrated += 1
        elif row["issue_code"] == "daily_fx_retrieval_failed":
            fx_pair = FX_PAIR.search(f"{row['title']} {row['description']}")
            if fx_pair and (row["entity_type"], row["entity_id"]) != (
                "fx_pair",
                f"{fx_pair.group(1)}_{fx_pair.group(2)}",
            ):
                row["entity_type"] = "fx_pair"
                row["entity_id"] = f"{fx_pair.group(1)}_{fx_pair.group(2)}"
                migrated += 1
            if row["resolution"].startswith("duplicate_legacy_issue:"):
                # The legacy run-level scope collapsed distinct currency pairs. Reopen those
                # rows once so each corrected pair must prove its own recovery.
                row["status"] = "open"
                row["resolution"] = ""
                row["resolved_at"] = ""
                migrated += 1
        rows.append(row)
    write_table(repository_root, "issues", rows)
    regenerate_issue_dashboard(repository_root)
    return {"row_count": len(rows), "migrated_count": migrated}


def _after(value: str, boundary: datetime | None) -> bool:
    parsed = parse_timestamp(value, allow_empty=True)
    return parsed is not None and boundary is not None and parsed > boundary


def reconcile_issues(
    repository_root: Path, *, as_of: datetime | None = None
) -> Mapping[str, object]:
    """Resolve open issues only when canonical state proves recovery after the last failure."""

    instant = as_of or utc_now()
    rows = read_table(repository_root, "issues")
    operations = _operation_rows(repository_root)
    history = read_table(repository_root, "operations_history")
    assessment_history = read_table(repository_root, "security_assessment_history")
    latest_market = {
        row["security_id"]: row for row in read_table(repository_root, "market_latest")
    }
    resolved: list[str] = []
    remediation_operation_ids: list[str] = []
    open_by_identity: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        if row["status"] == "open":
            open_by_identity.setdefault(
                (row["issue_code"], row["entity_type"], row["entity_id"]), []
            ).append(row)
    for duplicates in open_by_identity.values():
        if len(duplicates) < 2:
            continue
        keeper = max(duplicates, key=lambda value: (value["last_seen_at"], value["issue_id"]))
        for duplicate in duplicates:
            if duplicate is keeper:
                continue
            duplicate["status"] = "resolved"
            duplicate["resolution"] = f"duplicate_legacy_issue: {keeper['issue_id']}"
            duplicate["resolved_at"] = format_timestamp(instant)
            resolved.append(duplicate["issue_id"])
    for row in rows:
        if row["status"] != "open":
            continue
        last_seen = parse_timestamp(row["last_seen_at"], allow_empty=True)
        reason = ""
        code = row["issue_code"]
        if code == "daily_podcast_terminal" and "skipped" in row["title"].lower():
            reason = "valid_terminal_skip: podcast operation recorded its bounded no-content result"
        elif code == "daily_podcast_terminal":
            successes = [
                operation
                for operation in history
                if operation["operation_type"] == "daily_podcast"
                and operation["terminal_status"] == "succeeded"
                and _after(operation["completed_at"], last_seen)
            ]
            if successes:
                latest = max(
                    successes,
                    key=lambda value: (value["completed_at"], value["operation_id"]),
                )
                reason = f"superseded_by_successful_podcast_cycle: {latest['operation_id']}"
        elif code == "daily_market_retrieval_failed" and row["entity_type"] == "security":
            market = latest_market.get(row["entity_id"])
            if market and market["status"] == "ok" and _after(market["retrieved_at"], last_seen):
                reason = (
                    "current_state_recovered: market retrieval succeeded at "
                    f"{market['retrieved_at']}"
                )
        elif code == "daily_fx_retrieval_failed" and row["entity_type"] == "fx_pair":
            from papertrader.market_data import MarketDataError, read_fx_cache

            currencies = row["entity_id"].split("_")
            try:
                rates = (
                    read_fx_cache(repository_root, currencies[0], currencies[1])
                    if len(currencies) == 2
                    else ()
                )
            except MarketDataError:
                rates = ()
            if rates:
                newest = max(rates, key=lambda rate: (rate.retrieved_at, rate.date))
                if last_seen is not None and newest.retrieved_at > last_seen:
                    reason = (
                        "current_state_recovered: FX retrieval succeeded at "
                        f"{format_timestamp(newest.retrieved_at)}"
                    )
        elif code == "youtube_discovery_failed":
            from papertrader.queue import RETIRED_SOURCE_WATCH_PREFIXES

            active_watchers = [
                operation
                for operation in read_table(repository_root, "operations_todo")
                if operation["source"].startswith(RETIRED_SOURCE_WATCH_PREFIXES)
            ]
            retirements = [
                operation
                for operation in history
                if operation["terminal_status"] == "cancelled"
                and operation["terminal_reason"] == "source_watch_retired_manual_ideas"
                and operation["source"].startswith(RETIRED_SOURCE_WATCH_PREFIXES)
                and _after(operation["completed_at"], last_seen)
            ]
            if not active_watchers and retirements:
                latest = max(
                    retirements,
                    key=lambda value: (value["completed_at"], value["operation_id"]),
                )
                reason = f"source_watch_retired: {latest['operation_id']}"
        elif code in {"assessment_update_failed", "security_data_issue"}:
            versions = [
                version
                for version in assessment_history
                if version["security_id"] == row["entity_id"]
                and _after(version["recorded_at"], last_seen)
            ]
            if versions:
                latest = max(
                    versions,
                    key=lambda value: (value["recorded_at"], value["assessment_id"]),
                )
                reason = f"superseded_by_assessment: {latest['assessment_id']}"
        elif code == "security_assessment_duplicate_operation_versions":
            versions = [
                version
                for version in assessment_history
                if version["security_id"] == row["entity_id"]
                and _after(version["recorded_at"], last_seen)
            ]
            successes = [
                operation
                for operation in history
                if operation["operation_type"] == "security_research"
                and operation["entity_id"] == row["entity_id"]
                and operation["source"] == "issue-remediation:duplicate-assessment"
                and operation["terminal_status"] == "succeeded"
                and _after(operation["completed_at"], last_seen)
            ]
            if versions and successes:
                latest = max(
                    versions,
                    key=lambda value: (value["recorded_at"], value["assessment_id"]),
                )
                reason = f"clean_review_succeeded: {latest['assessment_id']}"
            else:
                active_review = next(
                    (
                        operation
                        for operation in read_table(repository_root, "operations_todo")
                        if operation["operation_type"] == "security_research"
                        and operation["entity_id"] == row["entity_id"]
                        and operation["source"] == "issue-remediation:duplicate-assessment"
                    ),
                    None,
                )
                if active_review is not None:
                    remediation_operation_ids.append(active_review["operation_id"])
                else:
                    from papertrader.config import load_settings
                    from papertrader.queue import enqueue_operation

                    settings = load_settings(repository_root, {})
                    operation_id, _ = enqueue_operation(
                        repository_root,
                        settings,
                        operation_type="security_research",
                        entity_type="security",
                        entity_id=row["entity_id"],
                        dedupe_key=(
                            "security_research:duplicate_assessment_remediation:"
                            f"{row['entity_id']}:{row['issue_id']}"
                        ),
                        prompt=(
                            "Perform one clean scenario-complete security review to supersede "
                            "the duplicate-assessment incident."
                        ),
                        inputs={
                            "security_id": row["entity_id"],
                            "research_reasons": [
                                {
                                    "reason": "duplicate_assessment_remediation",
                                    "issue_id": row["issue_id"],
                                }
                            ],
                        },
                        source="issue-remediation:duplicate-assessment",
                        priority=98,
                        freshness_days=0,
                        now=instant,
                    )
                    remediation_operation_ids.append(operation_id)
        elif code == "agent_result_validation_failed":
            failed_operation = operations.get(row["entity_id"], {})
            operation_type = failed_operation.get("operation_type", "")
            entity_id = failed_operation.get("entity_id", "")
            from papertrader.queue import RETIRED_SOURCE_WATCH_PREFIXES

            failed_source = failed_operation.get("source", "")
            retired_youtube_incident = failed_source.startswith(
                (*RETIRED_SOURCE_WATCH_PREFIXES, "youtube_backfill:")
            )
            if retired_youtube_incident:
                active_watchers = [
                    operation
                    for operation in read_table(repository_root, "operations_todo")
                    if operation["source"].startswith(RETIRED_SOURCE_WATCH_PREFIXES)
                ]
                retirements = [
                    operation
                    for operation in history
                    if operation["terminal_status"] == "cancelled"
                    and operation["terminal_reason"] == "source_watch_retired_manual_ideas"
                    and operation["source"].startswith(RETIRED_SOURCE_WATCH_PREFIXES)
                    and _after(operation["completed_at"], last_seen)
                ]
                if not active_watchers and retirements:
                    latest = max(
                        retirements,
                        key=lambda value: (value["completed_at"], value["operation_id"]),
                    )
                    reason = f"source_watch_retired: {latest['operation_id']}"
            if not reason:
                successes = [
                    operation
                    for operation in history
                    if operation["terminal_status"] == "succeeded"
                    and operation["operation_type"] == operation_type
                    and operation["entity_id"] == entity_id
                    and _after(operation["completed_at"], last_seen)
                ]
                if operation_type and entity_id and successes:
                    latest = max(
                        successes,
                        key=lambda value: (value["completed_at"], value["operation_id"]),
                    )
                    reason = f"superseded_by_success: {latest['operation_id']}"
        if not reason:
            continue
        row["status"] = "resolved"
        row["resolution"] = reason
        row["resolved_at"] = format_timestamp(instant)
        resolved.append(row["issue_id"])
    if resolved:
        write_table(repository_root, "issues", rows)
        regenerate_issue_dashboard(repository_root)
    return {
        "resolved_count": len(resolved),
        "resolved_issue_ids": tuple(sorted(resolved)),
        "remediation_operation_ids": tuple(sorted(set(remediation_operation_ids))),
    }


def validate_issue_state(repository_root: Path) -> list[str]:
    """Validate explicit issue identity, impact, and lifecycle invariants."""

    errors: list[str] = []
    open_identities: set[tuple[str, str, str]] = set()
    for row in read_table(repository_root, "issues"):
        prefix = f"issue {row['issue_id']}"
        if row["status"] not in ISSUE_STATUSES:
            errors.append(f"{prefix} has invalid status {row['status']!r}")
        if row["severity"] not in ISSUE_SEVERITIES:
            errors.append(f"{prefix} has invalid severity {row['severity']!r}")
        if not ISSUE_CODE.fullmatch(row["issue_code"]):
            errors.append(f"{prefix} has invalid issue_code {row['issue_code']!r}")
        if row["impact"] not in ISSUE_IMPACTS:
            errors.append(f"{prefix} has invalid impact {row['impact']!r}")
        if bool(row["entity_type"]) != bool(row["entity_id"]):
            errors.append(f"{prefix} has incomplete entity scope")
        elif row["entity_type"] and not ISSUE_ENTITY_TYPE.fullmatch(row["entity_type"]):
            errors.append(f"{prefix} has invalid entity_type {row['entity_type']!r}")
        first_seen = parse_timestamp(row["first_seen_at"], allow_empty=True)
        last_seen = parse_timestamp(row["last_seen_at"], allow_empty=True)
        resolved = parse_timestamp(row["resolved_at"], allow_empty=True)
        if first_seen is None or last_seen is None or first_seen > last_seen:
            errors.append(f"{prefix} has invalid first/last seen timestamps")
        if row["status"] == "resolved":
            if not row["resolution"] or resolved is None:
                errors.append(f"{prefix} resolved without resolution evidence")
            elif last_seen is not None and resolved < last_seen:
                errors.append(f"{prefix} resolves before it was last seen")
        elif row["resolution"] or resolved is not None:
            errors.append(f"{prefix} is open with stale resolution state")
        identity = (row["issue_code"], row["entity_type"], row["entity_id"])
        if row["status"] == "open" and identity in open_identities:
            errors.append(f"duplicate open issue identity: {identity!r}")
        if row["status"] == "open":
            open_identities.add(identity)
    return errors

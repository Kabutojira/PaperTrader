"""Bounded protected monitoring and rotating semantic audits within the normal queue budget."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.evidence import claims, validate_schema
from papertrader.governance import ROOT, GovernanceError, load_record, protected_entities, topics
from papertrader.tables import read_table
from papertrader.utils import content_hash, format_timestamp, parse_timestamp

if TYPE_CHECKING:
    from papertrader.queue import Operation


def schedule_monitoring(
    root: Path, settings: Settings, *, run_id: str, now: datetime
) -> tuple[str, ...]:
    from papertrader.hardening import policy
    from papertrader.queue import enqueue_operation

    if policy(root) is None:
        return ()
    securities = {row["security_id"]: row for row in read_table(root, "securities")}
    eligible = {entity for kind, entity in protected_entities(root) if kind == "security"}
    eligible.update(
        row["topic"]["entity_id"]
        for row in topics(root).values()
        if row["topic"]["scope_class"] == "user_directed"
        and row["topic"]["entity_type"] == "security"
        and row["topic"]["lifecycle"] == "active"
    )
    eligible &= securities.keys()
    last_checked: dict[str, str] = {}
    audit_weeks = set()
    for path in (root / ROOT / "monitoring").glob("*.json"):
        receipt = load_record(root, path)
        if receipt["complete_no_change"] or receipt["checked_count"]:
            last_checked[receipt["security_id"]] = max(
                last_checked.get(receipt["security_id"], ""), receipt["accepted_at"]
            )
        if receipt["kind"] == "semantic_audit":
            audit_weeks.add(receipt["window_key"])
    order = sorted(eligible, key=lambda key: (last_checked.get(key, ""), key))
    source_rows = read_table(root, "source_registry")
    week = now.strftime("%G-W%V")
    enqueued = []
    for index, security_id in enumerate(order[:2]):
        kind = (
            "semantic_audit"
            if index == min(1, len(order) - 1) and week not in audit_weeks
            else "source_monitor"
        )
        window_key = week if kind == "semantic_audit" else now.date().isoformat()
        investigation = f"{kind}:{security_id}:{window_key}"
        key = content_hash(investigation)[:24]
        context_path = root / ROOT / "monitoring-contexts" / f"{key}.json"
        if context_path.exists():
            context = load_record(root, context_path)
        else:
            registered = [
                row
                for row in source_rows
                if security_id in row["related_entity_ids"].split("|")
                and row["source_type"]
                in {
                    "filing",
                    "annual_report",
                    "earnings_release",
                    "issuer_release",
                    "regulatory",
                    "exchange",
                }
            ]
            targets = [
                {
                    "target_id": row["source_id"],
                    "kind": "primary_source",
                    "url": row["canonical_url"],
                    "previous_hash": row["content_hash"],
                }
                for row in registered[:5]
            ]
            if not targets:
                targets = [
                    {
                        "target_id": security_id,
                        "kind": "bounded_primary_search",
                        "url": "",
                        "previous_hash": "",
                    }
                ]
            related_claims = {
                row["version_id"]: row["claim"]
                for row in claims(root).values()
                if security_id in row["claim"]["security_ids"]
            }
            if kind == "semantic_audit":
                targets = [
                    {"target_id": key, "kind": "claim", "url": "", "previous_hash": ""}
                    for key in sorted(related_claims)[:20]
                ] or targets
            context = {
                "schema_version": 1,
                "kind": kind,
                "security_id": security_id,
                "window_key": window_key,
                "window_start": format_timestamp(
                    now - timedelta(days=7 if kind == "semantic_audit" else 1)
                ),
                "window_end": format_timestamp(now),
                "targets": targets,
                "claims": related_claims,
                "coverage_scope": "bounded subset; never complete-universe coverage",
            }
            context["context_hash"] = content_hash(context)
            if any(part.is_symlink() for part in (context_path, *context_path.parents)):
                raise GovernanceError("monitoring context destination traverses symlink")
            context_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(context_path, context, allowed_root=root)
        relative = context_path.relative_to(root).as_posix()
        operation_id, _ = enqueue_operation(
            root,
            settings,
            operation_type="research_triage",
            entity_type="security",
            entity_id=security_id,
            dedupe_key=investigation,
            prompt=(
                "Inspect only the frozen protected monitoring targets and report "
                "actual coverage and material changes."
            ),
            inputs={
                "security_id": security_id,
                "investigation_id": investigation,
                "cause": kind,
                "evidence_refs": [relative],
                "monitoring_context_path": relative,
            },
            source="controller:protected-monitoring",
            priority=94,
            freshness_days=0,
            now=now,
        )
        enqueued.append(operation_id)
    return tuple(enqueued)


def monitoring_context(root: Path, operation: Operation) -> dict[str, Any] | None:
    payload = load_record(root, root / operation.payload_path)
    relative = payload["inputs"].get("monitoring_context_path")
    if relative is None:
        return None
    path = root / relative
    if path.parent != root / ROOT / "monitoring-contexts":
        raise GovernanceError("monitoring context must be controller-owned")
    context = load_record(root, path)
    expected_investigation = f"{context['kind']}:{context['security_id']}:{context['window_key']}"
    if (
        payload["inputs"]["investigation_id"] != expected_investigation
        or operation.dedupe_key != expected_investigation
    ):
        raise GovernanceError("monitoring context belongs to a different investigation")
    if context["security_id"] != operation.entity_id or context["context_hash"] != content_hash(
        {key: value for key, value in context.items() if key != "context_hash"}
    ):
        raise GovernanceError("monitoring context identity/hash mismatch")
    return context


def validate_monitoring_result(
    root: Path, operation: Operation, result: Mapping[str, Any], *, now: datetime
) -> dict[str, Any] | None:
    context = monitoring_context(root, operation)
    if context is None:
        if result.get("monitoring_review") is not None:
            raise GovernanceError("unscheduled triage cannot invent monitoring coverage")
        return None
    review = result.get("monitoring_review")
    if not isinstance(review, dict):
        raise GovernanceError("monitored triage requires an explicit actual-coverage receipt")
    validate_schema(root, "research_monitoring", review)
    if review["context_hash"] != context["context_hash"]:
        raise GovernanceError("monitoring result conflicts with frozen context")
    targets = {row["target_id"] for row in context["targets"]}
    checked = set()
    checked_count = 0
    for check in review["checks"]:
        if check["target_id"] not in targets or check["target_id"] in checked:
            raise GovernanceError("monitoring receipt has an out-of-scope or repeated target")
        checked.add(check["target_id"])
        if check["state"] in {"checked_no_change", "changed"}:
            instant = parse_timestamp(check["checked_at"]) if check["checked_at"] else None
            start = parse_timestamp(context["window_start"])
            if (
                instant is None
                or start is None
                or not start <= instant <= now
                or not check["source_hash"]
                or not check["evidence_refs"]
            ):
                raise GovernanceError(
                    "successful monitoring requires actual timestamped source evidence"
                )
            checked_count += 1
    complete_no_change = checked == targets and all(
        row["state"] == "checked_no_change" for row in review["checks"]
    )
    disposition = result.get("triage_review", {}).get("disposition")
    if disposition in {"no_material_change", "duplicate"} and not complete_no_change:
        raise GovernanceError(
            "partial, failed, missing, or reserved checks cannot establish no change"
        )
    for conflict in review["conflicts"]:
        left = context["claims"].get(conflict["claim_a"])
        right = context["claims"].get(conflict["claim_b"])
        if left is None or right is None:
            raise GovernanceError("audit conflict must name inspected frozen claim versions")
        comparable = all(
            left[key] == right[key]
            for key in (
                "security_ids",
                "period_start",
                "period_end",
                "unit",
                "currency",
                "scope",
                "basis",
            )
        )
        if conflict["classification"] == "contradiction" and not comparable:
            raise GovernanceError(
                "different periods/units/scope are not a demonstrated contradiction"
            )
    return {
        "schema_version": 1,
        "operation_id": operation.operation_id,
        "security_id": operation.entity_id,
        "kind": context["kind"],
        "window_key": context["window_key"],
        "window_start": context["window_start"],
        "window_end": context["window_end"],
        "accepted_at": format_timestamp(now),
        "target_count": len(targets),
        "checked_count": checked_count,
        "complete_no_change": complete_no_change,
        "unexamined_target_ids": sorted(targets - checked),
        "review": review,
    }


def accept_monitoring(
    root: Path, operation: Operation, result: Mapping[str, Any], *, now: datetime
) -> bool:
    receipt = validate_monitoring_result(root, operation, result, now=now)
    if receipt is None:
        return False
    path = root / ROOT / "monitoring" / f"{operation.operation_id}.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(path, receipt, allowed_root=root)
    return bool(receipt["complete_no_change"])

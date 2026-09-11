"""Versioned research scope, conservative admission, and compact archival memory.

JSON revisions are canonical, append-only controller writes. The index and capsules are
derived views. Legacy unknown scope stays diagnostic; it never fabricates user authority.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from papertrader.atomic_io import atomic_write_json, atomic_write_text
from papertrader.config import Settings
from papertrader.tables import read_table
from papertrader.utils import content_hash, format_timestamp, utc_now

ROOT = "data/operations/research-governance"
AUTOMATIC_ACTIVE_TOPIC_CAP = 100  # Five days at the existing maximum 20 operations/day.


class GovernanceError(RuntimeError):
    """A scope transition would lose provenance or an operational obligation."""


def load_record(root: Path, path: Path) -> dict[str, Any]:
    if not path.is_relative_to(root) or any(part.is_symlink() for part in (path, *path.parents)):
        raise GovernanceError("governance path escapes repository or traverses symlink")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GovernanceError("governance record must be an object")
    return value


def topics(root: Path) -> dict[str, dict[str, Any]]:
    """Rebuild the latest projection from immutable revisions, rejecting chain forks."""
    revisions = [
        load_record(root, path) for path in sorted((root / ROOT / "topics").glob("*.json"))
    ]
    current: dict[str, dict[str, Any]] = {}
    unresolved = {row["version_id"]: row for row in revisions}
    while unresolved:
        progressed = False
        for version_id, row in list(unresolved.items()):
            previous = current.get(row["topic"]["topic_id"])
            if row["previous_version_id"] == (previous["version_id"] if previous else ""):
                if (
                    content_hash({key: value for key, value in row.items() if key != "version_id"})
                    != version_id
                ):
                    raise GovernanceError("research topic revision hash mismatch")
                current[row["topic"]["topic_id"]] = row
                del unresolved[version_id]
                progressed = True
        if not progressed:
            raise GovernanceError("research scope history has a missing predecessor or fork")
    return current


def protected_entities(root: Path) -> set[tuple[str, str]]:
    protected = {
        ("security", row["security_id"])
        for row in read_table(root, "portfolio")
        if row["quantity"] not in {"", "0"}
    }
    live_orders = {
        row["order_id"]
        for row in read_table(root, "orders")
        if row["status"] in {"pending", "partially_filled"}
    }
    protected.update(
        ("security", row["security_id"])
        for row in read_table(root, "order_legs")
        if row["order_id"] in live_orders
    )
    for row in read_table(root, "strategies"):
        if row["status"] == "active":
            protected.update(
                {
                    ("security", row["security_id"]),
                    ("idea", row["idea_id"]),
                    ("relationship", row["relationship_id"]),
                }
            )
    for row in read_table(root, "relationships"):
        if row["status"] == "accepted" and ("security", row["security_id"]) in protected:
            protected.update({("idea", row["idea_id"]), ("relationship", row["relationship_id"])})
    return protected


def record_topic(
    root: Path,
    topic: Mapping[str, Any],
    *,
    manual_tracking: bool = False,
    source_operation_id: str = "",
    now: datetime | None = None,
    apply: bool = True,
) -> str:
    schema = load_record(root, root / "schemas/research_topic.schema.json")
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(topic))
    if errors:
        raise GovernanceError("; ".join(error.message for error in errors))
    current = topics(root)
    previous = current.get(topic["topic_id"])
    if previous and previous["topic"] == topic:
        return str(previous["version_id"])
    if previous:
        for key in ("entity_type", "entity_id", "parent_ids"):
            if previous["topic"][key] != topic[key]:
                raise GovernanceError(f"topic lineage is immutable: {key}")
    if any(parent not in current or parent == topic["topic_id"] for parent in topic["parent_ids"]):
        raise GovernanceError("topic parents must be existing immutable topics")
    if any(
        row["topic"]["entity_type"] == topic["entity_type"]
        and row["topic"]["entity_id"] == topic["entity_id"]
        and key != topic["topic_id"]
        for key, row in current.items()
    ):
        raise GovernanceError("entity already has a canonical research topic")
    if topic["scope_class"] == "user_directed":
        if not manual_tracking and (
            previous is None or previous["topic"]["scope_class"] != "user_directed"
        ):
            raise GovernanceError("only explicit manual tracking can create a user anchor")
        if not topic["user_request_ref"] or topic["anchor_ids"]:
            raise GovernanceError(
                "user anchor requires an explicit request receipt, not inherited anchors"
            )
    elif topic["user_request_ref"]:
        raise GovernanceError("non-anchor cannot invent a tracking request")
    if topic["scope_class"] == "directly_adjacent":
        if not topic["anchor_ids"] or {item["anchor_id"] for item in topic["contributions"]} != set(
            topic["anchor_ids"]
        ):
            raise GovernanceError(
                "adjacent topic requires direct contributions to every original anchor"
            )
        for anchor in topic["anchor_ids"]:
            if anchor not in current or current[anchor]["topic"]["scope_class"] != "user_directed":
                raise GovernanceError(
                    "an adjacent topic cannot rebase scope through another adjacent topic"
                )
    if (
        previous
        and previous["topic"]["scope_class"] == "peripheral"
        and topic["scope_class"] == "directly_adjacent"
        and not set(topic["evidence_refs"]) - set(previous["topic"]["evidence_refs"])
    ):
        raise GovernanceError("peripheral promotion requires new direct-contribution evidence")
    if topic["lifecycle"] == "archived":
        if (topic["entity_type"], topic["entity_id"]) in protected_entities(root):
            raise GovernanceError(
                "protected exposure cannot lose research coverage through archival"
            )
        if not 100 <= len(topic["summary"].split()) <= 200:
            raise GovernanceError("archive capsule requires a 100-200 word original summary")
        if not topic["reactivation_conditions"]:
            raise GovernanceError("archive requires explicit reconsideration conditions")
    if (
        previous
        and previous["topic"]["lifecycle"] == "archived"
        and topic["lifecycle"] == "active"
        and not manual_tracking
        and not set(topic["evidence_refs"]) - set(previous["topic"]["evidence_refs"])
    ):
        raise GovernanceError("archive retrieval alone cannot reactivate a topic")
    automatic_active = sum(
        row["topic"]["lifecycle"] == "active"
        and row["topic"]["scope_class"] in {"directly_adjacent", "peripheral"}
        for key, row in current.items()
        if key != topic["topic_id"]
    )
    if (
        topic["lifecycle"] == "active"
        and topic["scope_class"] in {"directly_adjacent", "peripheral"}
        and automatic_active >= AUTOMATIC_ACTIVE_TOPIC_CAP
        and (topic["entity_type"], topic["entity_id"]) not in protected_entities(root)
    ):
        topic = {**topic, "lifecycle": "deferred", "reason": "deferred_for_capacity"}
    revision = {
        "schema_version": 1,
        "topic": dict(topic),
        "previous_version_id": previous["version_id"] if previous else "",
        "recorded_at": format_timestamp(now or utc_now()),
        "source_operation_id": source_operation_id,
    }
    version_id = content_hash(revision)
    if not apply:
        return version_id
    destination = root / ROOT / "topics" / f"{version_id}.json"
    if any(part.is_symlink() for part in (destination, *destination.parents)):
        raise GovernanceError("governance destination traverses a symlink")
    destination.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(destination, {**revision, "version_id": version_id}, allowed_root=root)
    render_scope(root)
    return version_id


def render_scope(root: Path) -> None:
    rows = topics(root)
    lines = [
        "---",
        "title: Research scope and dispositions",
        "type: query",
        "status: maintained",
        "tags: [research, query]",
        "created: " + min((row["recorded_at"][:10] for row in rows.values()), default="2026-09-11"),
        "updated: " + max((row["recorded_at"][:10] for row in rows.values()), default="2026-09-11"),
        "provenance: deterministic-research-scope",
        "---",
        "",
        "# Research scope and dispositions",
        "",
        "Generated from immutable scope revisions. Unknown legacy scope is not a user anchor.",
        "",
    ]
    for topic_id, row in sorted(rows.items()):
        topic = row["topic"]
        lines.append(
            f"- `{topic_id}`: {topic['scope_class']}; {topic['lifecycle']}; "
            f"{topic['reason']}; revision `{row['version_id']}`."
        )
        if topic["lifecycle"] == "archived":
            capsule = [
                "---",
                f"title: Archived research {topic_id}",
                "type: query",
                "status: archived",
                "tags: [research, query]",
                f"created: {row['recorded_at'][:10]}",
                f"updated: {row['recorded_at'][:10]}",
                "provenance: deterministic-research-scope",
                "---",
                "",
                topic["summary"],
                "",
                f"Disposition: {topic['reason']}",
                f"Original scope: {topic['scope_class']}",
                f"Revision: `{row['version_id']}`",
                "",
                "## Reconsideration",
                "",
                *[f"- {condition}" for condition in topic["reactivation_conditions"]],
                "",
                "## Evidence references",
                "",
                *[f"- `{ref}`" for ref in topic["evidence_refs"]],
                "",
                "Original evidence, notes, assessment history, and financial ledgers are retained.",
            ]
            atomic_write_text(
                root / "data/wiki/_archive" / f"research-topic-{topic_id}.md",
                "\n".join(capsule) + "\n",
                allowed_root=root,
            )
    destination = root / "data/wiki/_meta/research-scope.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(destination, "\n".join(lines) + "\n", allowed_root=root)


def admission_reason(
    root: Path,
    *,
    entity_type: str,
    entity_id: str,
    parent_ids: tuple[str, ...] = (),
    operation_type: str = "",
    inputs: Mapping[str, Any] | None = None,
    settings: Settings | None = None,
    now: datetime | None = None,
) -> str:
    """Known peripheral/archive boundaries are mandatory; legacy classification is diagnostic."""
    if (entity_type, entity_id) in protected_entities(root):
        return ""
    indexed = {
        (row["topic"]["entity_type"], row["topic"]["entity_id"]): row["topic"]
        for row in topics(root).values()
    }
    target = indexed.get((entity_type, entity_id))
    if target and target["lifecycle"] == "archived":
        return "scope_archived_requires_reactivation"
    if target and target["lifecycle"] == "deferred" and target["reason"] == "deferred_for_capacity":
        return "scope_deferred_for_capacity"
    operations = [*read_table(root, "operations_todo"), *read_table(root, "operations_history")]
    if (
        target
        and target["scope_class"] == "peripheral"
        and any(
            row["entity_type"] == entity_type
            and row["entity_id"] == entity_id
            and row.get("terminal_status") == "succeeded"
            for row in operations
        )
    ):
        return "scope_peripheral_terminal"
    for operation in operations:
        if operation["operation_id"] not in parent_ids:
            continue
        parent = indexed.get((operation["entity_type"], operation["entity_id"]))
        if parent and parent["scope_class"] == "peripheral":
            return "scope_peripheral_terminal"
    from papertrader.hardening import policy

    activation = policy(root)
    if activation is not None and operation_type in {
        "security_research",
        "idea_research",
        "relationship_research",
        "opportunity_research",
        "quick_check_research",
        "research_triage",
    }:
        from papertrader.scheduling import rsi_attention

        # Producer labels cannot grant authority. Protection comes from state,
        # original explicit topic anchors, or canonical current RSI evidence.
        exempt = bool(target and target["scope_class"] == "user_directed")
        if entity_type == "security" and settings is not None:
            exempt = (
                exempt or rsi_attention(root, settings, entity_id, now=now or utc_now()) is not None
            )
        outstanding = sum(
            row.get("status") in {"queued", "ready", "running", "waiting"}
            and row["operation_type"]
            in {
                "security_research",
                "idea_research",
                "relationship_research",
                "opportunity_research",
                "quick_check_research",
                "research_triage",
            }
            and (row["entity_type"], row["entity_id"]) not in protected_entities(root)
            for row in read_table(root, "operations_todo")
        )
        same_pending = any(
            row["entity_type"] == entity_type
            and row["entity_id"] == entity_id
            and row["status"] in {"queued", "ready", "waiting"}
            for row in read_table(root, "operations_todo")
        )
        if (
            not exempt
            and not same_pending
            and outstanding >= activation["automatic_obligation_cap"]
        ):
            return "scope_deferred_for_capacity"
    return ""


def validate_governance(root: Path) -> list[str]:
    try:
        current = topics(root)
        schema = load_record(root, root / "schemas/research_topic.schema.json")
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = [
            f"topic {key}: {error.message}"
            for key, row in current.items()
            for error in validator.iter_errors(row["topic"])
        ]
        return errors
    except (GovernanceError, KeyError, ValueError, OSError, TypeError) as exc:
        return [f"research_governance: {exc}"]


def security_change_class(root: Path, security_id: str, operation_id: str) -> str:
    rows = read_table(root, "security_assessment_history")
    current = next(
        (
            row
            for row in reversed(rows)
            if row["security_id"] == security_id and row["source_operation_id"] == operation_id
        ),
        None,
    )
    if current is None:
        return "unknown"
    previous = next(
        (row for row in rows if row["assessment_id"] == current["previous_assessment_id"]), None
    )
    if previous is None:
        return "new_facts"
    material = {
        "eligibility",
        "confidence",
        "thesis_score",
        "business_quality_score",
        "balance_sheet_score",
        "liquidity_score",
        "risk_penalty",
        "hard_blockers",
        "soft_gaps",
        "evidence_refs",
        "valuation_method",
        "valuation_template",
        "bear_fair_value",
        "bear_probability_pct",
        "bear_assumptions",
        "base_fair_value",
        "base_probability_pct",
        "base_assumptions",
        "bull_fair_value",
        "bull_probability_pct",
        "bull_assumptions",
        "research_conclusion",
    }
    if any(current.get(key) != previous.get(key) for key in material):
        return "new_facts"
    return (
        "price_only"
        if any(
            current.get(key) != previous.get(key) for key in ("reference_price", "fx_rate_to_base")
        )
        else "unchanged"
    )

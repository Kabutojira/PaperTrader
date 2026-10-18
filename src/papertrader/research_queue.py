"""Bounded company/idea work, without alerts, dependencies or operation history."""

from __future__ import annotations

import argparse
import configparser
import csv
import io
import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from papertrader.migration_inventory import _git
from papertrader.research_state import ResearchState, Row, decimal, timestamp

LEGACY_BLOCKED_REASONS = (
    "scope_deferred_for_capacity",
    "agent_result:blocked",
    "dependency_unavailable",
)


@dataclass(frozen=True)
class QueueLimits:
    max_pending: int = 30
    max_attempts: int = 2
    max_daily_operations: int = 3
    lease_seconds: int = 900

    def __post_init__(self) -> None:
        if not all(
            1 <= value <= 1000
            for value in (
                self.max_pending,
                self.max_attempts,
                self.max_daily_operations,
                self.lease_seconds,
            )
        ):
            raise ValueError("invalid queue limits")


DEFAULT_QUEUE_LIMITS = QueueLimits()


def queue_limits(root: Path) -> QueueLimits:
    config = configparser.ConfigParser()
    config.read(root / "research.ini")
    return QueueLimits(
        **{
            key: config.getint("research", key, fallback=default)
            for key, default in vars(DEFAULT_QUEUE_LIMITS).items()
        }
    )


def instant(now: datetime) -> str:
    if now.utcoffset() is None:
        raise ValueError("timezone-aware time required")
    return now.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def entity_key(state: ResearchState, entity_type: str, entity_id: str) -> tuple[str, str]:
    """One company task, while retaining every distinct instrument in the catalog."""
    if entity_type == "idea":
        if not any(row["idea_id"] == entity_id for row in state["ideas"]):
            raise ValueError("unknown idea")
        return entity_type, entity_id
    if entity_type != "security":
        raise ValueError("only company and idea research are supported")
    security = next((r for r in state["securities"] if r["security_id"] == entity_id), None)
    if security is None:
        raise ValueError("unknown security")
    issuer = security["issuer_id"]
    if not issuer:
        raise ValueError("company identity required")
    representative = min(r["security_id"] for r in state["securities"] if r["issuer_id"] == issuer)
    return "security", representative


def _key(row: Row) -> tuple[str, str]:
    return row["entity_type"], row["entity_id"]


def _order(row: Row) -> tuple[int, str, str, str]:
    return -int(row["priority"]), row["created_at"], *_key(row)


def _legacy_blocked_reason(error: str) -> str:
    for reason in LEGACY_BLOCKED_REASONS:
        if error == reason or error.startswith(f"{reason}:"):
            return reason
    return "unrecognized_blocked_reason"


def admit(
    state: ResearchState,
    entity_type: str,
    entity_id: str,
    *,
    reasons: set[str],
    priority: int,
    now: datetime,
    manual: bool = False,
    limits: QueueLimits = DEFAULT_QUEUE_LIMITS,
) -> str:
    """Merge, admit or leave an automatic candidate in its catalog. Never block rows."""
    key = entity_key(state, entity_type, entity_id)
    if (
        not 0 <= priority <= 100
        or not reasons
        or any(
            not reason or len(reason) > 160 or "|" in reason or "\n" in reason for reason in reasons
        )
    ):
        raise ValueError("invalid priority or compact reasons")
    queue = state["research_queue"]
    existing = next((row for row in queue if _key(row) == key), None)
    if existing is not None:
        merged = "|".join(sorted(set(existing["reasons"].split("|")) | reasons))
        new_priority = str(max(int(existing["priority"]), 100 if manual else priority))
        if (merged, new_priority, manual or existing["manual"] == "true") != (
            existing["reasons"],
            existing["priority"],
            existing["manual"] == "true",
        ):
            existing.update(
                reasons=merged,
                priority=new_priority,
                updated_at=instant(now),
                manual="true" if manual or existing["manual"] == "true" else "false",
            )
        return "merged"
    if len(queue) >= limits.max_pending:
        automatic = [
            row for row in queue if row["manual"] == "false" and row["status"] != "running"
        ]
        if manual and not automatic:
            raise ValueError("queue full of protected requests; manual request was not accepted")
        if not automatic:
            return "catalog_only"
        worst = max(automatic, key=_order)
        if not manual and priority <= int(worst["priority"]):
            return "catalog_only"
        queue.remove(worst)
    text = instant(now)
    queue.append(
        dict(
            entity_type=key[0],
            entity_id=key[1],
            priority=str(100 if manual else priority),
            reasons="|".join(sorted(reasons)),
            created_at=text,
            updated_at=text,
            status="pending",
            attempts="0",
            next_eligible_at=text,
            lease_until="",
            manual="true" if manual else "false",
            last_error="",
        )
    )
    return "admitted"


def _needs_attention(state: ResearchState, row: Row) -> None:
    kind, identity = _key(row)
    if kind == "security":
        issuer = next(r["issuer_id"] for r in state["securities"] if r["security_id"] == identity)
        for security in state["securities"]:
            if security["issuer_id"] == issuer:
                security["research_status"] = "needs_attention"
    else:
        next(r for r in state["ideas"] if r["idea_id"] == identity)["status"] = "needs_attention"
    state["research_queue"].remove(row)


def recover(
    state: ResearchState, *, now: datetime, limits: QueueLimits = DEFAULT_QUEUE_LIMITS
) -> None:
    for row in list(state["research_queue"]):
        if row["status"] == "running" and timestamp(row["lease_until"]) <= now:
            if int(row["attempts"]) >= limits.max_attempts:
                _needs_attention(state, row)
            else:
                row.update(
                    status="failed",
                    lease_until="",
                    next_eligible_at=instant(now),
                    updated_at=instant(now),
                    last_error="expired_research_lease",
                )


def claim(
    state: ResearchState,
    *,
    now: datetime,
    excluded: set[tuple[str, str]] | None = None,
    limits: QueueLimits = DEFAULT_QUEUE_LIMITS,
) -> Row | None:
    recover(state, now=now, limits=limits)
    # A live lease prevents a second operation; expired leases are recoverable above.
    if any(row["status"] == "running" for row in state["research_queue"]):
        return None
    eligible = [
        row
        for row in state["research_queue"]
        if _key(row) not in (excluded or set())
        and timestamp(row["next_eligible_at"]) <= now
        and int(row["attempts"]) < limits.max_attempts
    ]
    if not eligible:
        return None
    row = min(eligible, key=_order)
    row.update(
        status="running",
        attempts=str(int(row["attempts"]) + 1),
        updated_at=instant(now),
        lease_until=instant(now + timedelta(seconds=limits.lease_seconds)),
        last_error="",
    )
    return row.copy()


def finish(
    state: ResearchState,
    task: Row,
    *,
    now: datetime,
    error: str = "",
    limits: QueueLimits = DEFAULT_QUEUE_LIMITS,
) -> str:
    row = next((r for r in state["research_queue"] if _key(r) == _key(task)), None)
    if row is None or row["status"] != "running" or row["lease_until"] != task["lease_until"]:
        raise ValueError("task is not owned by this current operation")
    if not error:
        state["research_queue"].remove(row)
        return "completed"
    if int(row["attempts"]) >= limits.max_attempts:
        _needs_attention(state, row)
        return "needs_attention"
    row.update(
        status="failed",
        updated_at=instant(now),
        lease_until="",
        next_eligible_at=instant(now + timedelta(hours=6)),
        last_error=error[:300],
    )
    return "retry_scheduled"


def schedule_attention(
    state: ResearchState,
    features: list[Row],
    previous_features: list[Row],
    *,
    now: datetime,
    material_entities: set[tuple[str, str]] | None = None,
    limits: QueueLimits = DEFAULT_QUEUE_LIMITS,
) -> dict[str, int]:
    """Aggregate deterministic reasons; callers supply only verified material events.

    Comparing the pre-market feature snapshot avoids replaying an unchanged price
    observation. Ordinary overdue work is retained only as queue capacity permits.
    """
    old = {row["security_id"]: row for row in previous_features}
    current = {row["security_id"]: row for row in features}
    assessments = {row["security_id"]: row for row in state["security_assessments"]}
    counts: Counter[str] = Counter()
    candidates: dict[tuple[str, str], tuple[int, set[str]]] = {}
    for security in state["securities"]:
        sid = security["security_id"]
        if security["research_status"] == "needs_attention" or security["status"] not in {
            "active",
            "watching",
            "watchlist",
        }:
            continue
        reasons: set[str] = set()
        priority = 0
        assessment = assessments.get(sid)
        recently_reviewed = bool(
            security["last_research_at"]
            and now - timestamp(security["last_research_at"]) < timedelta(days=7)
        )
        if not recently_reviewed and (
            assessment is None or timestamp(assessment["valid_until"]) <= now
        ):
            priority = 60 if assessment else 20
            reasons.add("research_overdue" if assessment else "unresearched_candidate")
        feature = current.get(sid, {})
        if feature and feature != old.get(sid) and not recently_reviewed:
            change = max(
                (
                    abs(decimal(feature[key]))
                    for key in ("change_1d_pct", "change_5d_pct")
                    if feature.get(key)
                ),
                default=decimal("0"),
            )
            if change >= 15 or (
                feature.get("change_1d_pct") and abs(decimal(feature["change_1d_pct"])) >= 8
            ):
                priority = max(priority, 80)
                reasons.add("severe_price_movement")
            if (
                assessment
                and assessment["research_status"] == "supported"
                and assessment["confidence"] == "high"
                and change >= 5
            ):
                priority = max(priority, 70)
                reasons.add("high_confidence_valuation_review")
            if (
                feature.get("rsi_14")
                and feature.get("sma_200")
                and change >= 5
                and (decimal(feature["rsi_14"]) <= 25 or decimal(feature["rsi_14"]) >= 75)
            ):
                priority = max(priority, 65)
                reasons.add("material_technical_context")
        key = entity_key(state, "security", sid)
        if key in (material_entities or set()) or ("security", sid) in (material_entities or set()):
            priority = max(priority, 90)
            reasons.add("verified_material_evidence")
        if reasons:
            previous_priority, previous_reasons = candidates.get(key, (0, set()))
            candidates[key] = max(previous_priority, priority), previous_reasons | reasons
    for key in material_entities or set():
        if key[0] == "idea":
            entity_key(state, *key)
            candidates[key] = 90, {"verified_material_evidence"}
    for key, (priority, reasons) in sorted(
        candidates.items(), key=lambda item: (-item[1][0], item[0])
    ):
        counts[admit(state, *key, priority=priority, reasons=reasons, now=now, limits=limits)] += 1
    return dict(counts)


def rebuild_legacy_queue(
    state: ResearchState,
    legacy: list[Row],
    *,
    now: datetime,
    limits: QueueLimits = DEFAULT_QUEUE_LIMITS,
) -> dict[str, Any]:
    """Census every old row; rebuild entity demand, never old tasks/dependencies."""
    if state["research_queue"]:
        raise ValueError("legacy rebuild requires an empty target queue")
    dispositions: Counter[str] = Counter()
    manual: set[tuple[str, str]] = set()
    for row in legacy:
        if _legacy_blocked_reason(row["last_error"]) == "scope_deferred_for_capacity":
            disposition = "capacity_not_replayed"
        elif row["operation_type"] == "relationship_research":
            disposition = "optional_inline_relationship"
        elif row["source"] == "manual-user-request" and row["operation_type"] in {
            "security_research",
            "idea_research",
        }:
            try:
                key = entity_key(state, row["entity_type"], row["entity_id"])
                manual.add(key)
                disposition = "current_manual_entity_goal"
            except ValueError:
                disposition = "unknown_entity_not_migrated"
        elif row["operation_type"] == "wiki_ingest":
            # Search/transcript leads alone are not independently verified evidence.
            disposition = "unverified_source_lead_not_migrated"
        else:
            disposition = "retired_or_superseded_trigger"
        dispositions[disposition] += 1
    for key in sorted(manual):
        admit(
            state,
            *key,
            priority=100,
            reasons={"manual_primary_source_review"},
            now=now,
            manual=True,
            limits=limits,
        )
    schedule_attention(state, [], [], now=now, limits=limits)
    return {
        "legacy_rows": len(legacy),
        "dispositions": dict(sorted(dispositions.items())),
        "blocked_reasons": dict(
            sorted(
                Counter(
                    _legacy_blocked_reason(r["last_error"])
                    for r in legacy
                    if r["status"] == "blocked"
                ).items()
            )
        ),
        "waiting_relationships": sum(
            r["status"] == "waiting" and r["operation_type"] == "relationship_research"
            for r in legacy
        ),
        "manual_entities": len(manual),
        "new_pending": len(state["research_queue"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only legacy queue migration preview")
    parser.add_argument("--revision", required=True)
    parser.add_argument("--as-of", required=True, help="UTC timestamp, ending in Z")
    args = parser.parse_args()
    from papertrader.research_migration import prepare_migration

    root = Path.cwd()
    state, _, _ = prepare_migration(root, args.revision)
    legacy = list(
        csv.DictReader(
            io.StringIO(
                _git(root, "show", f"{args.revision}:data/operations/operations_TODO.csv").decode()
            )
        )
    )
    report = rebuild_legacy_queue(
        state, legacy, now=timestamp(args.as_of), limits=queue_limits(root)
    )
    print(
        json.dumps({"report": report, "queue": state["research_queue"]}, indent=2, sort_keys=True)
    )


if __name__ == "__main__":
    main()

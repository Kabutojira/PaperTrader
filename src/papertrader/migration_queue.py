"""One-time read-only queue census from a pinned Git revision; never a runtime queue."""

from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from papertrader.migration_inventory import _git
from papertrader.research_queue import (
    DEFAULT_QUEUE_LIMITS,
    QueueLimits,
    admit,
    entity_key,
    queue_limits,
    schedule_attention,
)
from papertrader.research_state import ResearchState, Row, timestamp

LEGACY_BLOCKED_REASONS = (
    "scope_deferred_for_capacity",
    "agent_result:blocked",
    "dependency_unavailable",
)


def _legacy_blocked_reason(error: str) -> str:
    for reason in LEGACY_BLOCKED_REASONS:
        if error == reason or error.startswith(f"{reason}:"):
            return reason
    return "unrecognized_blocked_reason"


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

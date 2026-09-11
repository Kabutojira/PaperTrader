"""Audited, restart-safe activation of research hardening without ledger rewrites."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.governance import ROOT, GovernanceError, load_record
from papertrader.tables import read_table
from papertrader.utils import content_hash, format_timestamp, parse_timestamp

POLICY_PATH = f"{ROOT}/policy.json"


def policy(root: Path) -> dict[str, Any] | None:
    path = root / POLICY_PATH
    if not path.exists():
        return None
    from papertrader.evidence import validate_schema

    value = load_record(root, path)
    validate_schema(root, "research_hardening", value)
    if value["migration_id"] != content_hash(
        {key: item for key, item in value.items() if key != "migration_id"}
    ):
        raise GovernanceError("hardening migration identity mismatch")
    return value


def migrate(
    root: Path, settings: Settings, *, now: datetime, apply: bool = False
) -> dict[str, Any]:
    """Preview by default. Preserve every existing queue row and accounting byte."""
    existing = policy(root)
    if existing is not None:
        return existing
    todo = read_table(root, "operations_todo")
    history = read_table(root, "operations_history")
    cutoff = now - timedelta(days=14)
    completed = [
        row
        for row in history
        if row.get("terminal_status") == "succeeded"
        and (
            parse_timestamp(row.get("completed_at", "")) or datetime.min.replace(tzinfo=now.tzinfo)
        )
        >= cutoff
    ]
    # A five-day service goal, measured over a fixed two-week window. Bootstrap
    # floor is one operation/day; this caps admission, never deletes legacy work.
    daily_throughput = max(1, (len(completed) + 13) // 14)
    capacity = min(100, daily_throughput * 5)
    value: dict[str, Any] = {
        "policy_version": 1,
        "effective_at": format_timestamp(now),
        "automatic_obligation_cap": capacity,
        "throughput_window_days": 14,
        "observed_completions": len(completed),
        "service_goal_days": 5,
        "legacy_queue": todo,
        "legacy_scope": [
            {"entity_type": kind, "entity_id": identity, "scope_class": "legacy_unclassified"}
            for kind, identity in sorted({(row["entity_type"], row["entity_id"]) for row in todo})
        ],
        "queue_census": dict(sorted(Counter(row["status"] for row in todo).items())),
        "pre_policy_execution_ids": [row["execution_id"] for row in read_table(root, "executions")],
        "legacy_pending_orders": [
            {
                "order_id": row["order_id"],
                "disposition": "hold_new_exposure_until_authenticated_review",
            }
            for row in read_table(root, "orders")
            if row["status"] in {"pending", "partially_filled"}
        ],
        "ledger_hashes": {
            name: content_hash((root / "data/tables" / f"{name}.csv").read_bytes())
            for name in ("executions", "cash_ledger", "portfolio")
        },
        "rollback": (
            "Revert source activation only after holding all new exposure; never remove "
            "accepted review proof or rewrite ledgers. Restore exact historical bytes "
            "from Git in a separate audit checkout."
        ),
    }
    value["migration_id"] = content_hash(value)
    from papertrader.evidence import validate_schema

    validate_schema(root, "research_hardening", value)
    if apply:
        path = root / POLICY_PATH
        if any(part.is_symlink() for part in (path, *path.parents)):
            raise GovernanceError("migration path traverses symlink")
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(path, value, allowed_root=root)
    return value


def validate_hardening(root: Path) -> list[str]:
    try:
        value = policy(root)
        if value is None:
            return validate_artifacts(root)
        current = {row["execution_id"] for row in read_table(root, "executions")}
        if not set(value["pre_policy_execution_ids"]) <= current:
            raise GovernanceError("migration lost a pre-policy execution")
        known = {
            row["operation_id"]
            for table in ("operations_todo", "operations_history")
            for row in read_table(root, table)
        }
        if not {row["operation_id"] for row in value["legacy_queue"]} <= known:
            raise GovernanceError("migration lost a legacy operation obligation")
        return validate_artifacts(root)
    except (GovernanceError, OSError, ValueError, KeyError, TypeError) as exc:
        return [f"research_hardening: {exc}"]


def validate_artifacts(root: Path) -> list[str]:
    """Validate every revision, not just the current research projections."""
    from papertrader.evidence import validate_claim, validate_schema
    from papertrader.research_calendar import catalyst_records, occurrence_window

    errors = []
    for path in sorted((root / ROOT).rglob("*.json")):
        try:
            row = load_record(root, path)
            kind = path.parent.name
            if kind in {"claims", "topics", "catalysts"}:
                if (
                    path.stem != row["version_id"]
                    or content_hash({key: item for key, item in row.items() if key != "version_id"})
                    != row["version_id"]
                ):
                    raise GovernanceError("revision filename or content hash mismatch")
                when = parse_timestamp(row["recorded_at"])
                if when is None:
                    raise GovernanceError("revision lacks canonical time")
                if kind == "claims":
                    validate_claim(root, row["claim"], now=when)
                elif kind == "topics":
                    validate_schema(root, "research_topic", row["topic"])
                else:
                    validate_schema(root, "research_catalyst", row["event"])
                    start, end = occurrence_window(row["event"])
                    if row["window_start"] != (format_timestamp(start) if start else None) or row[
                        "window_end"
                    ] != (format_timestamp(end) if end else None):
                        raise GovernanceError("catalyst precision/window mismatch")
            elif kind == "forecasts":
                validate_schema(root, "research_forecast", row["forecast"])
                registered = parse_timestamp(row["registered_at"])
                horizon = parse_timestamp(row["forecast"]["horizon_at"])
                if (
                    registered is None
                    or horizon is None
                    or registered >= horizon
                    or path.stem != row["forecast_id"]
                ):
                    raise GovernanceError("forecast identity or point-in-time boundary invalid")
                for key in row["forecast"]["claim_version_ids"]:
                    claim = load_record(root, root / ROOT / "claims" / f"{key}.json")
                    if (parse_timestamp(claim["recorded_at"]) or horizon) > registered:
                        raise GovernanceError("forecast uses future evidence")
            elif kind == "forecast-outcomes":
                from papertrader.research_calendar import resolve_forecast

                resolved = parse_timestamp(row["resolved_at"])
                if resolved is None:
                    raise GovernanceError("forecast outcome lacks timestamp")
                resolve_forecast(
                    root,
                    forecast_id=row["forecast_id"],
                    occurred=row["occurred"],
                    source_history_id=row["source_history_id"],
                    now=resolved,
                )
            elif kind == "monitoring-contexts":
                if (
                    content_hash({key: item for key, item in row.items() if key != "context_hash"})
                    != row["context_hash"]
                ):
                    raise GovernanceError("monitoring context hash mismatch")
            elif kind == "monitoring":
                validate_schema(root, "research_monitoring", row["review"])
                checked = sum(
                    check["state"] in {"checked_no_change", "changed"}
                    for check in row["review"]["checks"]
                )
                if checked != row["checked_count"] or checked > row["target_count"]:
                    raise GovernanceError("monitoring coverage count mismatch")
        except (GovernanceError, OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    try:
        catalyst_records(root)
    except (GovernanceError, OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"catalyst history: {exc}")
    for path in (root / "data/runs").glob("*/finding_coverage.json"):
        try:
            row = load_record(root, path)
            appendix = root / row["appendix_path"]
            if not appendix.is_relative_to(root / "data/wiki/queries") or any(
                part.is_symlink() for part in (appendix, *appendix.parents)
            ):
                raise GovernanceError("finding coverage path escapes query pages")
            text = appendix.read_text(encoding="utf-8")
            if content_hash(appendix.read_bytes()) != row["appendix_hash"] or not all(
                f"## {key}\n" in text for key in row["finding_ids"]
            ):
                raise GovernanceError("saved finding coverage differs from appendix")
            if row["saved"] is not True or row["user_observed"] is not False:
                raise GovernanceError("finding coverage fabricates delivery/user observation")
        except (GovernanceError, OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return errors

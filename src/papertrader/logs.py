"""Append-only structured event logging and reproducible 1,000-line tail view."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from papertrader.atomic_io import atomic_write_text
from papertrader.tables import append_unique
from papertrader.utils import (
    canonical_json,
    decimal_text,
    ensure_utc,
    format_timestamp,
    stable_id,
    utc_now,
)


def append_event(
    repository_root: Path,
    *,
    event_type: str,
    message: str,
    run_id: str = "",
    operation_id: str = "",
    data: Mapping[str, object] | None = None,
    occurred_at: datetime | None = None,
) -> str:
    """Append one canonical JSON event and rebuild the bounded text tail."""

    timestamp_value = ensure_utc(occurred_at or utc_now())
    timestamp = format_timestamp(timestamp_value)
    normalized_message = " ".join(message.split())
    normalized_event_type = " ".join(event_type.split())
    if not normalized_event_type or not normalized_message:
        raise ValueError("log event type and message are required")
    payload = dict(data or {})
    event_id = stable_id(
        "event",
        timestamp,
        normalized_event_type,
        run_id,
        operation_id,
        normalized_message,
        canonical_json(payload),
    )
    event = {
        "event_id": event_id,
        "occurred_at": timestamp,
        "event_type": normalized_event_type,
        "run_id": run_id,
        "operation_id": operation_id,
        "message": normalized_message,
        "data": payload,
    }
    log_path = repository_root / "data" / "logs" / f"operations-{timestamp_value.year}.ndjson"
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    existing_lines = [line for line in existing.splitlines() if line.strip()]
    serialized = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if serialized not in existing_lines:
        existing_lines.append(serialized)
        atomic_write_text(
            log_path,
            "\n".join(existing_lines) + "\n",
            allowed_root=repository_root,
        )
    regenerate_log_tail(repository_root)
    return event_id


def regenerate_log_tail(repository_root: Path, *, limit: int = 1000) -> None:
    """Generate the latest human-readable event lines without truncating NDJSON."""

    if limit < 0:
        raise ValueError("log tail limit must not be negative")
    events: list[dict[str, object]] = []
    for path in sorted((repository_root / "data" / "logs").glob("operations-*.ndjson")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid NDJSON in {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"event in {path}:{line_number} must be an object")
            events.append(value)
    events.sort(
        key=lambda event: (str(event.get("occurred_at", "")), str(event.get("event_id", "")))
    )
    lines = []
    for event in events[-limit:]:
        context = " ".join(
            part
            for part in (
                f"run={event.get('run_id')}" if event.get("run_id") else "",
                f"operation={event.get('operation_id')}" if event.get("operation_id") else "",
            )
            if part
        )
        suffix = f" {context}" if context else ""
        lines.append(
            f"{event.get('occurred_at', '')} [{event.get('event_type', '')}]{suffix} "
            f"{event.get('message', '')}"
        )
    content = "\n".join(lines) + ("\n" if lines else "")
    atomic_write_text(
        repository_root / "data" / "logs" / "log.txt",
        content,
        allowed_root=repository_root,
    )


def record_completed_run(
    repository_root: Path,
    *,
    run_id: str,
    started_at: datetime,
    completed_at: datetime,
    status: str,
    trigger: str,
    operation_count: int,
    model_budget_limit: Decimal,
    model_budget_used: Decimal,
    commit_sha: str = "",
    summary: str = "",
) -> None:
    """Append one immutable terminal run summary."""

    normalized_started = ensure_utc(started_at)
    normalized_completed = ensure_utc(completed_at)
    if not run_id or normalized_completed < normalized_started:
        raise ValueError("run identity and chronological timestamps are required")
    if (
        operation_count < 0
        or model_budget_limit < 0
        or model_budget_used < 0
        or model_budget_used > model_budget_limit
    ):
        raise ValueError("run counts and model budgets are inconsistent")
    row = {
        "run_id": run_id,
        "started_at": format_timestamp(normalized_started),
        "completed_at": format_timestamp(normalized_completed),
        "status": status,
        "trigger": trigger,
        "operation_count": str(operation_count),
        "model_budget_limit": decimal_text(model_budget_limit),
        "model_budget_used": decimal_text(model_budget_used),
        "commit_sha": commit_sha,
        "summary": " ".join(summary.split()),
    }
    append_unique(repository_root, "runs", [row], key_columns=("run_id",))

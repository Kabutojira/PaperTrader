"""Stable catalyst occurrences and frozen forecasts; never execution inputs."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from papertrader.atomic_io import atomic_write_json
from papertrader.evidence import validate_schema
from papertrader.governance import ROOT, GovernanceError, load_record
from papertrader.tables import read_table
from papertrader.utils import content_hash, format_timestamp, parse_timestamp


def schedule_catalysts(root: Path, settings: Any, *, now: datetime) -> tuple[str, ...]:
    from papertrader.hardening import policy
    from papertrader.queue import enqueue_operation

    if policy(root) is None:
        return ()
    due = [
        row
        for row in catalyst_records(root).values()
        if row["event"]["status"] in {"scheduled", "rescheduled"}
        and row["window_start"]
        and (parse_timestamp(row["window_start"]) or now) <= now
    ]
    active_and_history = [
        *read_table(root, "operations_todo"),
        *read_table(root, "operations_history"),
    ]
    known = {row["dedupe_key"] for row in active_and_history}
    for row in sorted(due, key=lambda value: (value["window_start"], value["occurrence_id"])):
        dedupe = f"catalyst:{row['occurrence_id']}:{row['version_id']}"
        if dedupe in known:
            continue
        security_id = row["event"]["security_id"]
        operation_id, _ = enqueue_operation(
            root,
            settings,
            operation_type="research_triage",
            entity_type="security",
            entity_id=security_id,
            dedupe_key=dedupe,
            prompt=(
                "Check the expected catalyst occurrence; do not infer that an event "
                "happened merely because its date passed."
            ),
            inputs={
                "security_id": security_id,
                "investigation_id": dedupe[:128],
                "cause": "catalyst_due",
                "evidence_refs": [row["event"]["source_history_id"]],
                "catalyst_occurrence_id": row["occurrence_id"],
                "catalyst_version_id": row["version_id"],
            },
            source="controller:catalyst-occurrence",
            depends_on=(row["source_operation_id"],) if row["source_operation_id"] else (),
            priority=94,
            freshness_days=0,
            now=now,
        )
        return (operation_id,)
    return ()


def _immutable_write(root: Path, path: Path, value: Mapping[str, Any]) -> None:
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise GovernanceError("calendar/forecast destination traverses symlink")
    if path.exists():
        if load_record(root, path) != value:
            raise GovernanceError("immutable research event conflicts with prior receipt")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, value, allowed_root=root)


def occurrence_window(value: Mapping[str, Any]) -> tuple[datetime | None, datetime | None]:
    zone = ZoneInfo(value["timezone"])
    precision = value["precision"]
    expected_field = {
        "datetime": "scheduled_at",
        "date": "expected_date",
        "month": "expected_month",
        "unknown": None,
    }[precision]
    for field in ("scheduled_at", "expected_date", "expected_month"):
        if (field == expected_field) != (value[field] is not None):
            raise GovernanceError("catalyst date precision conflicts with supplied timestamp/date")
    if precision == "unknown":
        return None, None
    if precision == "datetime":
        instant = parse_timestamp(value["scheduled_at"])
        return instant, instant
    day = date.fromisoformat(
        value["expected_date"] if precision == "date" else value["expected_month"] + "-01"
    )
    end_day = (
        day + timedelta(days=1)
        if precision == "date"
        else date(day.year + (day.month == 12), day.month % 12 + 1, 1)
    )
    return datetime.combine(day, time(), zone).astimezone(UTC), datetime.combine(
        end_day, time(), zone
    ).astimezone(UTC)


def catalyst_records(root: Path) -> dict[str, dict[str, Any]]:
    current: dict[str, dict[str, Any]] = {}
    records = [load_record(root, path) for path in (root / ROOT / "catalysts").glob("*.json")]
    pending = {row["version_id"]: row for row in records}
    while pending:
        progress = False
        for version_id, row in list(pending.items()):
            old = current.get(row["occurrence_id"])
            if row["previous_version_id"] != (old["version_id"] if old else ""):
                continue
            if version_id != content_hash(
                {key: value for key, value in row.items() if key != "version_id"}
            ):
                raise GovernanceError("catalyst history hash mismatch")
            current[row["occurrence_id"]] = row
            del pending[version_id]
            progress = True
        if not progress:
            raise GovernanceError("catalyst history has a missing predecessor or fork")
    return current


def record_catalyst(
    root: Path,
    value: Mapping[str, Any],
    *,
    operation_id: str = "",
    now: datetime,
    apply: bool = True,
) -> str:
    validate_schema(root, "research_catalyst", value)
    if value["security_id"] not in {row["security_id"] for row in read_table(root, "securities")}:
        raise GovernanceError("catalyst requires an immutable security")
    source = next(
        (
            row
            for row in read_table(root, "source_history")
            if row["source_history_id"] == value["source_history_id"]
        ),
        None,
    )
    if source is None or (parse_timestamp(source["checked_at"]) or now) > now:
        raise GovernanceError("catalyst requires available source-observation provenance")
    start, end = occurrence_window(value)
    occurrence_id = content_hash([value["event_id"], value["occurrence_key"]])[:24]
    previous = catalyst_records(root).get(occurrence_id)
    if previous and previous["event"] == value:
        return str(previous["version_id"])
    if previous and previous["event"]["security_id"] != value["security_id"]:
        raise GovernanceError("catalyst occurrence cannot change security identity")
    record = {
        "schema_version": 1,
        "occurrence_id": occurrence_id,
        "event": dict(value),
        "window_start": format_timestamp(start) if start else None,
        "window_end": format_timestamp(end) if end else None,
        "previous_version_id": previous["version_id"] if previous else "",
        "source_operation_id": operation_id,
        "recorded_at": format_timestamp(now),
    }
    version_id = content_hash(record)
    if apply:
        _immutable_write(
            root,
            root / ROOT / "catalysts" / f"{version_id}.json",
            {**record, "version_id": version_id},
        )
    return version_id


def register_forecast(
    root: Path,
    value: Mapping[str, Any],
    *,
    operation_id: str = "",
    now: datetime,
    apply: bool = True,
) -> str:
    validate_schema(root, "research_forecast", value)
    horizon = parse_timestamp(value["horizon_at"])
    path = root / ROOT / "forecasts" / f"{value['forecast_id']}.json"
    if path.exists():
        old = load_record(root, path)
        if old["forecast"] != value:
            raise GovernanceError("a forecast cannot be rewritten after registration")
        return str(old["forecast_id"])
    if horizon is None or horizon <= now:
        raise GovernanceError("forecast must be registered before its falsifiable horizon")
    for key in value["claim_version_ids"]:
        claim = load_record(root, root / ROOT / "claims" / f"{key}.json")
        recorded = parse_timestamp(claim["recorded_at"])
        if (
            recorded is None
            or recorded > now
            or value["security_id"] not in claim["claim"]["security_ids"]
        ):
            raise GovernanceError("forecast uses unavailable or unrelated evidence")
    record = {
        "schema_version": 1,
        "forecast_id": value["forecast_id"],
        "forecast": dict(value),
        "registered_at": format_timestamp(now),
        "source_operation_id": operation_id,
    }
    if apply:
        _immutable_write(root, path, record)
    return str(value["forecast_id"])


def resolve_forecast(
    root: Path, *, forecast_id: str, occurred: bool, source_history_id: str, now: datetime
) -> str:
    if not forecast_id.replace("_", "").replace("-", "").isalnum():
        raise GovernanceError("invalid forecast identity")
    forecast = load_record(root, root / ROOT / "forecasts" / f"{forecast_id}.json")
    horizon = parse_timestamp(forecast["forecast"]["horizon_at"])
    source = next(
        (
            row
            for row in read_table(root, "source_history")
            if row["source_history_id"] == source_history_id
        ),
        None,
    )
    observed = parse_timestamp(source["checked_at"]) if source else None
    if horizon is None or observed is None or not horizon <= observed <= now:
        raise GovernanceError("forecast resolution requires post-horizon observed evidence")
    score = (Decimal(forecast["forecast"]["probability"]) - Decimal(int(occurred))) ** 2
    result = {
        "schema_version": 1,
        "forecast_id": forecast_id,
        "occurred": occurred,
        "source_history_id": source_history_id,
        "resolved_at": format_timestamp(now),
        "brier_score": str(score),
    }
    path = root / ROOT / "forecast-outcomes" / f"{forecast_id}.json"
    if path.exists():
        original = load_record(root, path)
        if any(original[key] != result[key] for key in result if key != "resolved_at"):
            raise GovernanceError("forecast outcome conflicts with immutable resolution")
        return str(original["brier_score"])
    _immutable_write(root, path, result)
    return str(score)

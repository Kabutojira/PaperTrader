"""Validated, idempotent, strictly sequential operation queue state machine."""

from __future__ import annotations

import fcntl
import json
import os
import re
import stat
import tempfile
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path, PurePosixPath

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.dedupe import SemanticOverlapReviewer
from papertrader.tables import append_unique, read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    content_hash,
    deterministic_ulid,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    utc_now,
    validate_ulid,
)

ACTIVE_STATUSES = frozenset({"queued", "ready", "running", "waiting", "blocked"})
HISTORY_STATUSES = frozenset({"succeeded", "skipped", "failed", "cancelled", "expired"})
DEPENDENCY_SUCCESS = frozenset({"succeeded", "skipped"})
SUPPORTED_OPERATIONS = frozenset(
    {
        "wiki_ingest",
        "source_discovery",
        "opportunity_research",
        "quick_check_research",
        "idea_research",
        "security_research",
        "relationship_research",
        "strategy_research",
        "execute_strategy",
        "daily_podcast",
    }
)
OPERATION_SKILLS = {
    operation: f"papertrader-{operation.replace('_', '-')}" for operation in SUPPORTED_OPERATIONS
}
OPERATION_ENTITY_TYPES = {
    "wiki_ingest": "source",
    "source_discovery": "source",
    "opportunity_research": "opportunity",
    "quick_check_research": "security",
    "idea_research": "idea",
    "security_research": "security",
    "relationship_research": "relationship",
    "strategy_research": "strategy",
    "execute_strategy": "strategy",
    "daily_podcast": "run",
}
SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
MERGEABLE_RESEARCH_TYPES = frozenset({"security_research", "quick_check_research"})


class QueueError(RuntimeError):
    """Raised when queue state is malformed or a transition is not permitted."""


@dataclass(frozen=True, slots=True)
class Operation:
    """Parsed active queue row with canonical UTC and integer values."""

    operation_id: str
    created_at: datetime
    updated_at: datetime
    status: str
    priority: int
    operation_type: str
    entity_type: str
    entity_id: str
    not_before: datetime | None
    deadline: datetime | None
    depends_on: tuple[str, ...]
    dedupe_key: str
    freshness_days: int
    skill_names: tuple[str, ...]
    prompt: str
    payload_path: str
    source: str
    attempt_count: int
    max_attempts: int
    claimed_by_run_id: str
    lease_expires_at: datetime | None
    last_error: str

    @classmethod
    def from_row(cls, row: Mapping[str, str], *, archived: bool = False) -> Operation:
        """Parse and validate one complete active queue record."""

        operation_id = row["operation_id"]
        validate_ulid(operation_id)
        created = _canonical_time(row["created_at"], "created_at")
        updated = _canonical_time(row["updated_at"], "updated_at")
        assert created is not None and updated is not None
        not_before = _canonical_time(row["not_before"], "not_before", allow_empty=True)
        deadline = _canonical_time(row["deadline"], "deadline", allow_empty=True)
        lease = _canonical_time(row["lease_expires_at"], "lease_expires_at", allow_empty=True)
        try:
            priority = int(row["priority"])
            freshness_days = int(row["freshness_days"] or "0")
            attempt_count = int(row["attempt_count"])
            max_attempts = int(row["max_attempts"])
        except ValueError as exc:
            raise QueueError(f"operation {operation_id} contains a non-integer count") from exc
        status = row["status"]
        operation_type = row["operation_type"]
        if status not in ACTIVE_STATUSES:
            raise QueueError(f"operation {operation_id} has invalid active status {status!r}")
        if operation_type not in SUPPORTED_OPERATIONS:
            raise QueueError(f"operation {operation_id} has unsupported type {operation_type!r}")
        if not 0 <= priority <= 100:
            raise QueueError(f"operation {operation_id} priority must be between 0 and 100")
        if freshness_days < 0:
            raise QueueError(f"operation {operation_id} freshness_days must not be negative")
        if not 0 <= attempt_count <= max_attempts or max_attempts < 1:
            raise QueueError(f"operation {operation_id} has invalid attempt counts")
        if created > updated:
            raise QueueError(f"operation {operation_id} updated_at precedes created_at")
        if deadline is not None and deadline <= created:
            raise QueueError(f"operation {operation_id} deadline must follow created_at")
        if not_before is not None and deadline is not None and not_before >= deadline:
            raise QueueError(f"operation {operation_id} not_before must precede deadline")
        dependencies = tuple(filter(None, row["depends_on"].split("|")))
        if len(dependencies) != len(set(dependencies)) or operation_id in dependencies:
            raise QueueError(f"operation {operation_id} has invalid dependencies")
        for dependency in dependencies:
            validate_ulid(dependency)
        skills = tuple(filter(None, row["skill_names"].split("|")))
        if len(skills) != len(set(skills)):
            raise QueueError(f"operation {operation_id} has duplicate skill names")
        required_skills = {"llm-wiki", OPERATION_SKILLS[operation_type]}
        if set(skills) != required_skills:
            raise QueueError(
                f"operation {operation_id} must include exactly skills {sorted(required_skills)}"
            )
        if row["entity_type"] != OPERATION_ENTITY_TYPES[operation_type] or not row["entity_id"]:
            raise QueueError(f"operation {operation_id} requires entity_type and entity_id")
        if any(marker in row["entity_id"] for marker in "|\r\n"):
            raise QueueError(f"operation {operation_id} has an invalid entity_id")
        if not row["dedupe_key"] or any(marker in row["dedupe_key"] for marker in "\r\n"):
            raise QueueError(f"operation {operation_id} requires a one-line dedupe_key")
        if (
            not row["prompt"]
            or any(marker in row["prompt"] for marker in "\r\n")
            or len(row["prompt"]) > 2000
        ):
            raise QueueError(f"operation {operation_id} prompt must be one line up to 2,000 chars")
        _validate_payload_path(row["payload_path"])
        if status == "running":
            if not row["claimed_by_run_id"] or lease is None:
                raise QueueError(f"running operation {operation_id} requires a claim and lease")
            _validate_run_id(row["claimed_by_run_id"])
        elif row["claimed_by_run_id"] or lease is not None:
            if not (
                archived and status == "blocked" and row["claimed_by_run_id"] and lease is None
            ):
                raise QueueError(
                    f"non-running operation {operation_id} cannot retain a claim or lease"
                )
            _validate_run_id(row["claimed_by_run_id"])
        return cls(
            operation_id=operation_id,
            created_at=created,
            updated_at=updated,
            status=status,
            priority=priority,
            operation_type=operation_type,
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            not_before=not_before,
            deadline=deadline,
            depends_on=dependencies,
            dedupe_key=row["dedupe_key"],
            freshness_days=freshness_days,
            skill_names=skills,
            prompt=row["prompt"],
            payload_path=row["payload_path"],
            source=row["source"],
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            claimed_by_run_id=row["claimed_by_run_id"],
            lease_expires_at=lease,
            last_error=row["last_error"],
        )

    def to_row(self) -> dict[str, str]:
        """Serialize back to the exact active queue schema."""

        return {
            "operation_id": self.operation_id,
            "created_at": format_timestamp(self.created_at),
            "updated_at": format_timestamp(self.updated_at),
            "status": self.status,
            "priority": str(self.priority),
            "operation_type": self.operation_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "not_before": format_timestamp(self.not_before) if self.not_before else "",
            "deadline": format_timestamp(self.deadline) if self.deadline else "",
            "depends_on": "|".join(self.depends_on),
            "dedupe_key": self.dedupe_key,
            "freshness_days": str(self.freshness_days),
            "skill_names": "|".join(self.skill_names),
            "prompt": self.prompt,
            "payload_path": self.payload_path,
            "source": self.source,
            "attempt_count": str(self.attempt_count),
            "max_attempts": str(self.max_attempts),
            "claimed_by_run_id": self.claimed_by_run_id,
            "lease_expires_at": (
                format_timestamp(self.lease_expires_at) if self.lease_expires_at else ""
            ),
            "last_error": self.last_error,
        }


@dataclass(slots=True)
class RunBudget:
    """In-memory count/cost guard consumed by one sequential controller run."""

    maximum_operations: int
    maximum_cost: Decimal
    operation_count: int = 0
    cost_used: Decimal = Decimal("0")
    cost_reserved: Decimal = Decimal("0")

    @classmethod
    def from_settings(cls, settings: Settings) -> RunBudget:
        return cls(
            settings.operations.maximum_llm_operations_per_run,
            settings.operations.maximum_model_budget_usd_per_run,
        )

    def can_reserve(self, estimated_cost: Decimal = Decimal("0")) -> bool:
        return (
            self.operation_count < self.maximum_operations
            and self.cost_used + self.cost_reserved + estimated_cost <= self.maximum_cost
        )

    def reserve(self, estimated_cost: Decimal = Decimal("0")) -> None:
        if estimated_cost < 0 or not self.can_reserve(estimated_cost):
            raise QueueError("run operation or model-cost budget is exhausted")
        self.operation_count += 1
        self.cost_reserved += estimated_cost

    def charge(
        self,
        actual_cost: Decimal,
        *,
        reserved_cost: Decimal = Decimal("0"),
    ) -> None:
        if actual_cost < 0 or reserved_cost < 0 or reserved_cost > self.cost_reserved:
            raise QueueError("model cost or released reservation is invalid")
        self.cost_reserved -= reserved_cost
        self.cost_used += actual_cost


def _canonical_time(value: str, label: str, *, allow_empty: bool = False) -> datetime | None:
    try:
        parsed = parse_timestamp(value, allow_empty=allow_empty)
    except CanonicalValueError as exc:
        raise QueueError(f"{label}: {exc}") from exc
    if parsed is not None and value != format_timestamp(parsed):
        raise QueueError(f"{label} must use canonical UTC form {format_timestamp(parsed)}")
    return parsed


def _validate_run_id(value: str) -> None:
    if not SAFE_RUN_ID.fullmatch(value):
        raise QueueError(f"invalid run_id: {value!r}")


def _validate_payload_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or len(path.parts) != 4
        or path.parts[:3] != ("data", "operations", "payloads")
        or path.suffix != ".json"
    ):
        raise QueueError(f"invalid operation payload path: {value!r}")
    return path


def _payload_validator(repository_root: Path) -> Draft202012Validator:
    schema = json.loads(
        (repository_root / "schemas" / "operation_payload.schema.json").read_text(encoding="utf-8")
    )
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _validate_operation_payload_value(
    repository_root: Path,
    operation: Operation,
    payload: object,
    *,
    relative: PurePosixPath,
) -> None:
    """Validate one decoded payload before or after its durable write."""

    errors = sorted(
        _payload_validator(repository_root).iter_errors(payload), key=lambda error: list(error.path)
    )
    if errors:
        descriptions = "; ".join(error.message for error in errors)
        raise QueueError(f"payload {relative} fails schema: {descriptions}")
    assert isinstance(payload, dict)
    expected = {
        "operation_id": operation.operation_id,
        "operation_type": operation.operation_type,
        "entity_type": operation.entity_type,
        "entity_id": operation.entity_id,
    }
    mismatches = [key for key, value in expected.items() if payload.get(key) != value]
    if mismatches:
        raise QueueError(f"payload {relative} mismatches queue fields: {mismatches}")
    inputs = payload.get("inputs")
    if (
        operation.operation_type == "wiki_ingest"
        and isinstance(inputs, dict)
        and inputs.get("source_kind") == "youtube_video"
    ):
        video_id = inputs.get("video_id")
        channel_id = inputs.get("channel_id")
        source_id = inputs.get("source_id")
        if not all(isinstance(value, str) for value in (video_id, channel_id, source_id)):
            raise QueueError(f"payload {relative} has malformed YouTube identities")
        assert isinstance(video_id, str)
        assert isinstance(channel_id, str)
        assert isinstance(source_id, str)
        canonical_url = f"https://www.youtube.com/watch?v={video_id}"
        expected_dedupe = f"wiki_ingest:youtube:{channel_id}:{video_id}:v1"
        youtube_mismatches = []
        if source_id != f"youtube_{video_id}" or operation.entity_id != source_id:
            youtube_mismatches.append("source_id")
        if inputs.get("video_url") != canonical_url:
            youtube_mismatches.append("video_url")
        if inputs.get("channel_url") != (f"https://www.youtube.com/channel/{channel_id}/videos"):
            youtube_mismatches.append("channel_url")
        if operation.dedupe_key != expected_dedupe:
            youtube_mismatches.append("dedupe_key")
        if payload.get("source_refs") != [canonical_url]:
            youtube_mismatches.append("source_refs")
        if youtube_mismatches:
            raise QueueError(
                f"payload {relative} mismatches YouTube identities: {youtube_mismatches}"
            )


def validate_operation_payload(repository_root: Path, operation: Operation) -> None:
    """Validate a payload schema, queue identity match, and symlink-safe path."""

    relative = _validate_payload_path(operation.payload_path)
    path = repository_root.joinpath(*relative.parts)
    if path.is_symlink() or not path.is_file():
        raise QueueError(f"operation {operation.operation_id} payload does not exist: {relative}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QueueError(f"cannot read payload {relative}: {exc}") from exc
    _validate_operation_payload_value(
        repository_root,
        operation,
        payload,
        relative=relative,
    )


@contextmanager
def _queue_lock(repository_root: Path) -> Iterator[None]:
    digest = content_hash(str(repository_root.resolve()))[:16]
    path = Path(tempfile.gettempdir()) / f"papertrader-queue-{digest}.lock"
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o666)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise QueueError(f"queue lock must be a regular file: {path}")
        if stat.S_IMODE(metadata.st_mode) != 0o666:
            try:
                os.fchmod(descriptor, 0o666)
            except PermissionError as exc:
                raise QueueError(
                    f"queue lock is not writable across runtime users: {path}"
                ) from exc
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _read_active(repository_root: Path) -> list[Operation]:
    return [Operation.from_row(row) for row in read_table(repository_root, "operations_todo")]


def _write_active(repository_root: Path, operations: Sequence[Operation]) -> None:
    write_table(
        repository_root, "operations_todo", [operation.to_row() for operation in operations]
    )


def _history_row(
    operation: Operation,
    *,
    terminal_status: str,
    completed_at: datetime,
    result_path: str,
    result_summary: str,
    terminal_reason: str,
) -> dict[str, str]:
    if terminal_status not in HISTORY_STATUSES:
        raise QueueError(f"invalid history terminal status {terminal_status!r}")
    if not terminal_reason.strip():
        raise QueueError("every terminal operation requires a machine-readable reason")
    return {
        **operation.to_row(),
        "terminal_status": terminal_status,
        "completed_at": format_timestamp(completed_at),
        "result_path": result_path,
        "result_summary": " ".join(result_summary.split()),
        "terminal_reason": " ".join(terminal_reason.split()),
    }


def _terminalize(
    repository_root: Path,
    active: list[Operation],
    operation: Operation,
    *,
    terminal_status: str,
    completed_at: datetime,
    result_path: str = "",
    result_summary: str = "",
    terminal_reason: str,
) -> list[Operation]:
    row = _history_row(
        operation,
        terminal_status=terminal_status,
        completed_at=completed_at,
        result_path=result_path,
        result_summary=result_summary,
        terminal_reason=terminal_reason,
    )
    append_unique(
        repository_root,
        "operations_history",
        [row],
        key_columns=("operation_id",),
    )
    remaining = [
        candidate for candidate in active if candidate.operation_id != operation.operation_id
    ]
    _write_active(repository_root, remaining)
    return remaining


def _recover_archived(repository_root: Path, active: list[Operation]) -> list[Operation]:
    archived = {row["operation_id"] for row in read_table(repository_root, "operations_history")}
    remaining = [operation for operation in active if operation.operation_id not in archived]
    if len(remaining) != len(active):
        _write_active(repository_root, remaining)
    return remaining


def enqueue_operation(
    repository_root: Path,
    settings: Settings,
    *,
    operation_type: str,
    entity_type: str,
    entity_id: str,
    dedupe_key: str,
    prompt: str,
    inputs: Mapping[str, object],
    source: str,
    priority: int = 50,
    freshness_days: int = 0,
    depends_on: Sequence[str] = (),
    not_before: datetime | None = None,
    deadline: datetime | None = None,
    source_refs: Sequence[str] = (),
    max_attempts: int | None = None,
    now: datetime | None = None,
) -> tuple[str, bool]:
    """Idempotently write a validated payload and append one active request."""

    if operation_type not in SUPPORTED_OPERATIONS:
        raise QueueError(f"unsupported operation type: {operation_type}")
    if entity_type != OPERATION_ENTITY_TYPES[operation_type]:
        raise QueueError(
            f"operation {operation_type} requires entity_type "
            f"{OPERATION_ENTITY_TYPES[operation_type]!r}"
        )
    if any(marker in prompt for marker in "\r\n"):
        raise QueueError("operation prompt must not contain newlines")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        history = read_table(repository_root, "operations_history")
        for operation in active:
            if operation.dedupe_key == dedupe_key:
                return operation.operation_id, False
        for row in history:
            if row["dedupe_key"] == dedupe_key and row["terminal_status"] in DEPENDENCY_SUCCESS:
                return row["operation_id"], False
        if operation_type in MERGEABLE_RESEARCH_TYPES:
            merge_targets = [
                operation
                for operation in active
                if operation.entity_type == entity_type
                and operation.entity_id == entity_id
                and operation.operation_type in MERGEABLE_RESEARCH_TYPES
                and operation.status in {"queued", "ready", "waiting"}
            ]
            if merge_targets:
                merge_targets.sort(
                    key=lambda operation: (
                        operation.operation_type != "security_research",
                        -operation.priority,
                        operation.created_at,
                        operation.operation_id,
                    )
                )
                target = merge_targets[0]
                payload_path = repository_root.joinpath(
                    *_validate_payload_path(target.payload_path).parts
                )
                merged_payload = json.loads(payload_path.read_text(encoding="utf-8"))
                existing_inputs = merged_payload.get("inputs")
                if not isinstance(existing_inputs, dict):
                    raise QueueError(
                        f"operation {target.operation_id} payload inputs must be an object"
                    )
                reasons = existing_inputs.get("research_reasons")
                if not isinstance(reasons, list):
                    reasons = [
                        {
                            "dedupe_key": target.dedupe_key,
                            "prompt": target.prompt,
                            "source": target.source,
                            "source_refs": list(merged_payload.get("source_refs", [])),
                            "observed_at": format_timestamp(target.created_at),
                        }
                    ]
                if any(
                    isinstance(reason, dict) and reason.get("dedupe_key") == dedupe_key
                    for reason in reasons
                ):
                    return target.operation_id, False
                reason: dict[str, object] = {
                    "dedupe_key": dedupe_key,
                    "prompt": " ".join(prompt.split()),
                    "source": source,
                    "source_refs": sorted(set(source_refs)),
                    "observed_at": format_timestamp(instant),
                }
                trigger_types = inputs.get("trigger_types")
                if isinstance(trigger_types, list):
                    reason["trigger_types"] = sorted(
                        {str(value) for value in trigger_types if str(value)}
                    )
                market_date = inputs.get("market_data_date")
                if isinstance(market_date, str) and market_date:
                    reason["market_data_date"] = market_date
                reasons.append(reason)
                merged_inputs = _merge_research_inputs(existing_inputs, inputs)
                if (
                    target.operation_type == "quick_check_research"
                    and operation_type == "security_research"
                ):
                    merged_inputs["full_research_requested"] = True
                merged_inputs["research_reasons"] = reasons
                merged_payload["inputs"] = merged_inputs
                existing_refs = merged_payload.get("source_refs", [])
                if not isinstance(existing_refs, list):
                    existing_refs = []
                combined_refs = sorted(
                    {
                        str(value)
                        for value in (*existing_refs, *source_refs)
                        if isinstance(value, str) and value
                    }
                )
                if combined_refs:
                    merged_payload["source_refs"] = combined_refs
                combined_prompt = _merge_research_prompt(target.prompt, prompt)
                merged = replace(
                    target,
                    updated_at=instant,
                    priority=min(100, max(target.priority, priority) + 1),
                    prompt=combined_prompt,
                    depends_on=tuple(
                        sorted(
                            dependency
                            for dependency in set((*target.depends_on, *depends_on))
                            if dependency != target.operation_id
                        )
                    ),
                )
                merged_payload["objective"] = combined_prompt
                _validate_operation_payload_value(
                    repository_root,
                    merged,
                    merged_payload,
                    relative=PurePosixPath(merged.payload_path),
                )
                atomic_write_json(payload_path, merged_payload, allowed_root=repository_root)
                _write_active(
                    repository_root,
                    [
                        merged if operation.operation_id == merged.operation_id else operation
                        for operation in active
                    ],
                )
                return merged.operation_id, False
        operation_id = deterministic_ulid(instant, dedupe_key, entity_type, entity_id)
        payload_relative = f"data/operations/payloads/{operation_id}.json"
        skills = tuple(sorted({"llm-wiki", OPERATION_SKILLS[operation_type]}))
        operation = Operation(
            operation_id=operation_id,
            created_at=instant,
            updated_at=instant,
            status="queued",
            priority=priority,
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            not_before=ensure_utc(not_before).replace(microsecond=0) if not_before else None,
            deadline=ensure_utc(deadline).replace(microsecond=0) if deadline else None,
            depends_on=tuple(depends_on),
            dedupe_key=dedupe_key,
            freshness_days=freshness_days,
            skill_names=skills,
            prompt=" ".join(prompt.split()),
            payload_path=payload_relative,
            source=source,
            attempt_count=0,
            max_attempts=max_attempts or settings.operations.default_max_attempts,
            claimed_by_run_id="",
            lease_expires_at=None,
            last_error="",
        )
        # Re-parse the generated form so callers cannot bypass row-level invariants.
        operation = Operation.from_row(operation.to_row())
        payload: dict[str, object] = {
            "payload_version": 1,
            "operation_id": operation_id,
            "operation_type": operation_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "objective": operation.prompt,
            "inputs": dict(inputs),
        }
        if source_refs:
            payload["source_refs"] = sorted(set(source_refs))
        _validate_operation_payload_value(
            repository_root,
            operation,
            payload,
            relative=PurePosixPath(payload_relative),
        )
        payload_path = repository_root.joinpath(*PurePosixPath(payload_relative).parts)
        if payload_path.exists():
            try:
                existing_payload = json.loads(payload_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise QueueError(
                    f"cannot reuse operation payload {payload_relative}: {exc}"
                ) from exc
            if existing_payload != payload:
                raise QueueError(f"immutable operation payload conflicts: {payload_relative}")
        else:
            atomic_write_json(payload_path, payload, allowed_root=repository_root)
        validate_operation_payload(repository_root, operation)
        _write_active(repository_root, [*active, operation])
        return operation_id, True


def _merge_research_prompt(current: str, incoming: str) -> str:
    """Append a distinct queued research cause without exceeding the queue contract."""

    normalized = " ".join(incoming.split())
    if normalized == current or normalized in current.split(" | Additional cause: "):
        return current
    suffix = f" | Additional cause: {normalized}"
    if len(current) + len(suffix) <= 2000:
        return current + suffix
    return current


def _merge_research_inputs(
    current: Mapping[str, object], incoming: Mapping[str, object]
) -> dict[str, object]:
    """Combine pre-claim research inputs while preserving every conflicting cause."""

    merged = dict(current)
    conflicts = merged.get("merged_input_values")
    conflict_values: dict[str, list[object]] = (
        {str(key): list(value) for key, value in conflicts.items() if isinstance(value, list)}
        if isinstance(conflicts, dict)
        else {}
    )
    for key, value in incoming.items():
        if key == "research_reasons":
            continue
        if key not in merged:
            merged[key] = value
            continue
        previous = merged[key]
        if previous == value:
            continue
        if (
            key in {"trigger_types", "idea_ids"}
            and isinstance(previous, list)
            and isinstance(value, list)
        ):
            merged[key] = sorted({str(item) for item in (*previous, *value) if str(item)})
            continue
        if key == "idea_id" and isinstance(previous, str) and isinstance(value, str):
            raw_idea_ids = merged.get("idea_ids", [])
            idea_ids = raw_idea_ids if isinstance(raw_idea_ids, list) else []
            merged["idea_ids"] = sorted(
                {
                    previous,
                    value,
                    *(str(item) for item in idea_ids if isinstance(item, str)),
                }
            )
            continue
        if key == "period_start" and isinstance(previous, str) and isinstance(value, str):
            merged[key] = min(previous, value)
            continue
        if (
            key in {"period_end", "market_data_date", "market_data_as_of"}
            and isinstance(previous, str)
            and isinstance(value, str)
        ):
            merged[key] = max(previous, value)
            continue
        if key == "source_price_hash" and isinstance(previous, str) and isinstance(value, str):
            conflict_values.setdefault(key, []).extend(
                candidate
                for candidate in (previous, value)
                if candidate not in conflict_values.get(key, [])
            )
            merged[key] = value
            continue
        values = conflict_values.setdefault(key, [])
        for candidate in (previous, value):
            if candidate not in values:
                values.append(candidate)
    if conflict_values:
        merged["merged_input_values"] = conflict_values
    return merged


def _dependency_cycle(operations: Sequence[Operation]) -> set[str]:
    graph = {operation.operation_id: operation.depends_on for operation in operations}
    visiting: set[str] = set()
    visited: set[str] = set()
    cyclic: set[str] = set()

    def visit(node: str, stack: tuple[str, ...]) -> None:
        if node in visiting:
            start = stack.index(node) if node in stack else 0
            cyclic.update(stack[start:])
            return
        if node in visited or node not in graph:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency, (*stack, node))
        visiting.remove(node)
        visited.add(node)

    for operation_id in graph:
        visit(operation_id, ())
    return cyclic


def _recent_success(
    operation: Operation,
    history: Sequence[Mapping[str, str]],
    now: datetime,
) -> Mapping[str, str] | None:
    if operation.freshness_days <= 0:
        return None
    cutoff = now - timedelta(days=operation.freshness_days)
    for row in reversed(history):
        if (
            row["operation_type"] == operation.operation_type
            and row["entity_id"] == operation.entity_id
            and row["terminal_status"] == "succeeded"
        ):
            completed = parse_timestamp(row["completed_at"])
            if completed is not None and completed >= cutoff:
                return row
    return None


def _operation_inputs(repository_root: Path, operation: Operation) -> Mapping[str, object]:
    relative = _validate_payload_path(operation.payload_path)
    payload = json.loads(repository_root.joinpath(*relative.parts).read_text(encoding="utf-8"))
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict):
        raise QueueError(f"operation {operation.operation_id} payload inputs must be an object")
    return inputs


def _operation_allocation_plan_id(repository_root: Path, operation: Operation) -> str | None:
    if operation.operation_type not in {"strategy_research", "execute_strategy"}:
        return None
    inputs = _operation_inputs(repository_root, operation)
    plan_id = inputs.get("allocation_plan_id")
    if plan_id is None:
        return None
    if not isinstance(plan_id, str) or not plan_id:
        raise QueueError(
            f"operation {operation.operation_id} allocation_plan_id must be a nonempty string"
        )
    return plan_id


def _indicator_packet_cause(
    repository_root: Path,
    raw_path: object,
    *,
    security_id: str,
) -> str | None:
    """Resolve one canonical indicator packet to its trigger, or fail closed as ambiguous."""

    if not isinstance(raw_path, str):
        return None
    relative = PurePosixPath(raw_path)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.parts[:3] != ("data", "wiki", "inbox")
        or relative.suffix != ".md"
    ):
        return None
    path = repository_root.joinpath(*relative.parts)
    try:
        text = path.read_text(encoding="utf-8")
        raw, _ = text[4:].split("\n---\n", maxsplit=1)
        metadata = yaml.safe_load(raw)
        facts = metadata.get("candidate_facts") if isinstance(metadata, dict) else None
    except (OSError, UnicodeError, ValueError, yaml.YAMLError):
        return None
    if not isinstance(facts, dict) or facts.get("security_id") != security_id:
        return None
    trigger = facts.get("trigger")
    return trigger if isinstance(trigger, str) and trigger else None


def _exclusively_unheld_bearish_indicator_work(
    repository_root: Path,
    operation: Operation,
    *,
    held_ids: frozenset[str],
) -> bool:
    """Identify only complete, unambiguous bearish-indicator cause lineages."""

    if operation.status not in {"queued", "ready", "waiting"}:
        return False
    if operation.operation_type not in {
        "opportunity_research",
        "wiki_ingest",
        "quick_check_research",
        "security_research",
    }:
        return False
    inputs = _operation_inputs(repository_root, operation)
    security_id = inputs.get("security_id")
    packet_refs: list[object] = []
    triggers: list[object] = []
    if operation.operation_type == "wiki_ingest":
        packet_refs = [inputs.get("source_path")]
        if isinstance(packet_refs[0], str):
            packet_trigger = _indicator_packet_cause(
                repository_root, packet_refs[0], security_id=""
            )
            if packet_trigger is None:
                # The security identity is intentionally recovered from packet frontmatter here.
                relative = PurePosixPath(packet_refs[0])
                try:
                    text = repository_root.joinpath(*relative.parts).read_text(encoding="utf-8")
                    raw, _ = text[4:].split("\n---\n", maxsplit=1)
                    metadata = yaml.safe_load(raw)
                    facts = metadata.get("candidate_facts")
                    security_id = facts.get("security_id") if isinstance(facts, dict) else None
                except (OSError, UnicodeError, ValueError, yaml.YAMLError):
                    return False
            if isinstance(security_id, str):
                triggers = [
                    _indicator_packet_cause(
                        repository_root, packet_refs[0], security_id=security_id
                    )
                ]
    else:
        if not isinstance(security_id, str) or not security_id:
            return False
        reasons = inputs.get("research_reasons")
        if isinstance(reasons, list) and reasons:
            for reason in reasons:
                if (
                    not isinstance(reason, dict)
                    or reason.get("source") != "deterministic-price-alert"
                ):
                    return False
                raw_triggers = reason.get("trigger_types")
                raw_refs = reason.get("source_refs")
                if not isinstance(raw_triggers, list) or not isinstance(raw_refs, list):
                    return False
                triggers.extend(raw_triggers)
                packet_refs.extend(raw_refs)
        else:
            allowed_source = {
                "opportunity_research": "deterministic-indicator-transition",
                "quick_check_research": "deterministic-price-alert",
                "security_research": "deterministic-price-alert",
            }[operation.operation_type]
            if operation.source != allowed_source:
                return False
            raw_trigger = inputs.get("trigger_type")
            raw_triggers = inputs.get("trigger_types")
            triggers = (
                [raw_trigger]
                if isinstance(raw_trigger, str)
                else (list(raw_triggers) if isinstance(raw_triggers, list) else [])
            )
            payload_path = _validate_payload_path(operation.payload_path)
            payload = json.loads(
                repository_root.joinpath(*payload_path.parts).read_text(encoding="utf-8")
            )
            raw_refs = payload.get("source_refs")
            packet_refs = list(raw_refs) if isinstance(raw_refs, list) else []
    if not isinstance(security_id, str) or not security_id or security_id in held_ids:
        return False
    if not triggers or not packet_refs or not all(isinstance(value, str) for value in triggers):
        return False
    from papertrader.models import AlertDirection
    from papertrader.opportunity import alert_direction

    try:
        if any(alert_direction(str(value)) is not AlertDirection.BEARISH for value in triggers):
            return False
    except CanonicalValueError:
        return False
    packet_triggers = [
        _indicator_packet_cause(repository_root, ref, security_id=security_id)
        for ref in packet_refs
    ]
    return (
        bool(packet_triggers)
        and None not in packet_triggers
        and all(trigger in triggers for trigger in packet_triggers)
    )


def _triaged_operation(
    operation: Operation,
    *,
    status: str,
    last_error: str,
    updated_at: datetime,
) -> Operation:
    """Apply a triage transition without rewriting timestamps for an unchanged state."""

    if operation.status == status and operation.last_error == last_error:
        return operation
    return replace(
        operation,
        status=status,
        updated_at=updated_at,
        last_error=last_error,
    )


def prepare_queue(
    repository_root: Path,
    *,
    now: datetime | None = None,
    semantic_reviewer: SemanticOverlapReviewer | None = None,
) -> tuple[str, ...]:
    """Apply schema, deadline, dependency, exact-dedupe, freshness, and overlap triage."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    dispositions: list[str] = []
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        for operation in active:
            validate_operation_payload(repository_root, operation)
        running = [
            operation
            for operation in active
            if operation.status == "running"
            and operation.lease_expires_at is not None
            and operation.lease_expires_at > instant
        ]
        if len(running) > 1:
            raise QueueError("more than one operation has a live lease")
        cyclic = _dependency_cycle(active)
        history = read_table(repository_root, "operations_history")
        allocation_plan_ids = {
            row["allocation_plan_id"]
            for row in read_table(repository_root, "allocation_targets")
            if row["allocation_plan_id"]
        }
        if len(allocation_plan_ids) > 1:
            raise QueueError("current allocation targets contain multiple plan identities")
        current_allocation_plan_id = next(iter(allocation_plan_ids), None)
        signal_statuses = {
            row["signal_id"]: row["status"] for row in read_table(repository_root, "signals")
        }
        terminal_by_id = {row["operation_id"]: row["terminal_status"] for row in history}
        active_by_id = {operation.operation_id: operation for operation in active}
        from papertrader.opportunity import held_security_ids

        held_ids = held_security_ids(repository_root)
        seen_dedupe: dict[str, str] = {
            operation.dedupe_key: operation.operation_id
            for operation in active
            if operation.status == "running"
        }
        updated: list[Operation] = []
        terminal: list[tuple[Operation, str, str]] = []
        for operation in active:
            if operation.status == "running":
                updated.append(operation)
                continue
            if operation.status == "blocked" and not operation.last_error.startswith(
                ("dependency_cycle", "dependency_unavailable:")
            ):
                updated.append(operation)
                continue
            if _exclusively_unheld_bearish_indicator_work(
                repository_root, operation, held_ids=held_ids
            ):
                terminal.append((operation, "skipped", "bearish_alert_unowned"))
                continue
            if operation.deadline is not None and operation.deadline <= instant:
                terminal.append((operation, "expired", "deadline_elapsed"))
                continue
            duplicate_id = seen_dedupe.get(operation.dedupe_key)
            if duplicate_id is not None:
                terminal.append((operation, "skipped", f"exact_active_duplicate:{duplicate_id}"))
                continue
            seen_dedupe[operation.dedupe_key] = operation.operation_id
            prior_exact = next(
                (
                    row
                    for row in history
                    if row["dedupe_key"] == operation.dedupe_key
                    and row["terminal_status"] in DEPENDENCY_SUCCESS
                ),
                None,
            )
            if prior_exact is not None:
                terminal.append(
                    (
                        operation,
                        "skipped",
                        f"exact_history_duplicate:{prior_exact['operation_id']}",
                    )
                )
                continue
            operation_plan_id = _operation_allocation_plan_id(repository_root, operation)
            if (
                operation_plan_id is not None
                and current_allocation_plan_id is not None
                and operation_plan_id != current_allocation_plan_id
            ):
                terminal.append(
                    (
                        operation,
                        "skipped",
                        f"superseded_allocation_plan:{current_allocation_plan_id}",
                    )
                )
                continue
            if operation.operation_type == "execute_strategy":
                signal_id = _operation_inputs(repository_root, operation).get("signal_id")
                if not isinstance(signal_id, str) or not signal_id:
                    raise QueueError(
                        f"execute operation {operation.operation_id} lacks a signal identity"
                    )
                signal_status = signal_statuses.get(signal_id)
                if signal_status is None:
                    updated.append(
                        _triaged_operation(
                            operation,
                            status="blocked",
                            last_error=f"signal_missing:{signal_id}",
                            updated_at=instant,
                        )
                    )
                    dispositions.append(
                        f"{operation.operation_id}:blocked:signal_missing:{signal_id}"
                    )
                    continue
                if signal_status != "ready":
                    terminal.append(
                        (
                            operation,
                            "skipped",
                            f"signal_not_ready:{signal_status}",
                        )
                    )
                    continue
            if operation.operation_id in cyclic:
                updated.append(
                    _triaged_operation(
                        operation,
                        status="blocked",
                        last_error="dependency_cycle",
                        updated_at=instant,
                    )
                )
                dispositions.append(f"{operation.operation_id}:blocked:dependency_cycle")
                continue
            dependency_states = [
                terminal_by_id.get(dependency)
                or ("active" if dependency in active_by_id else "missing")
                for dependency in operation.depends_on
            ]
            failed_dependency = next(
                (
                    dependency
                    for dependency, state in zip(
                        operation.depends_on, dependency_states, strict=True
                    )
                    if state in {"failed", "cancelled", "expired", "missing"}
                ),
                None,
            )
            if failed_dependency is not None:
                updated.append(
                    _triaged_operation(
                        operation,
                        status="blocked",
                        last_error=f"dependency_unavailable:{failed_dependency}",
                        updated_at=instant,
                    )
                )
                dispositions.append(
                    f"{operation.operation_id}:blocked:dependency_unavailable:{failed_dependency}"
                )
                continue
            if any(state == "active" for state in dependency_states):
                updated.append(
                    _triaged_operation(
                        operation,
                        status="waiting",
                        last_error="dependencies_incomplete",
                        updated_at=instant,
                    )
                )
                continue
            if operation.not_before is not None and operation.not_before > instant:
                updated.append(
                    _triaged_operation(
                        operation,
                        status="waiting",
                        last_error="not_before_pending",
                        updated_at=instant,
                    )
                )
                continue
            recent = _recent_success(operation, history, instant)
            if recent is not None:
                terminal.append(
                    (
                        operation,
                        "skipped",
                        f"freshness_cooldown:{recent['operation_id']}",
                    )
                )
                continue
            overlaps = tuple(
                candidate.to_row()
                for candidate in updated
                if candidate.operation_type == operation.operation_type
                and candidate.entity_id == operation.entity_id
                and candidate.status in {"queued", "ready", "waiting"}
            )
            if semantic_reviewer is not None and overlaps:
                disposition = semantic_reviewer.review(operation.to_row(), overlaps)
                disposition.validate()
                overlap_ids = {candidate["operation_id"] for candidate in overlaps}
                if (
                    disposition.decision == "merge"
                    and disposition.target_operation_id not in overlap_ids
                ):
                    raise QueueError("semantic merge target is not an overlapping operation")
                reason = " ".join(disposition.reason.split())
                if disposition.decision in {"merge", "skip"}:
                    suffix = (
                        f":{disposition.target_operation_id}"
                        if disposition.target_operation_id
                        else ""
                    )
                    terminal.append(
                        (operation, "skipped", f"semantic_{disposition.decision}{suffix}:{reason}")
                    )
                    continue
                if disposition.decision == "defer":
                    updated.append(
                        _triaged_operation(
                            operation,
                            status="waiting",
                            last_error=f"semantic_defer:{reason}",
                            updated_at=instant,
                        )
                    )
                    continue
            updated.append(
                _triaged_operation(
                    operation,
                    status="ready",
                    last_error="",
                    updated_at=instant,
                )
            )
        if terminal:
            history_rows = [
                _history_row(
                    operation,
                    terminal_status=status,
                    completed_at=instant,
                    result_path="",
                    result_summary="Queue triage disposition",
                    terminal_reason=reason,
                )
                for operation, status, reason in terminal
            ]
            append_unique(
                repository_root,
                "operations_history",
                history_rows,
                key_columns=("operation_id",),
            )
            dispositions.extend(
                f"{operation.operation_id}:{status}:{reason}"
                for operation, status, reason in terminal
            )
        _write_active(repository_root, updated)
    return tuple(dispositions)


def release_expired_leases(
    repository_root: Path,
    *,
    now: datetime | None = None,
) -> tuple[str, ...]:
    """Requeue expired claims or fail them after the configured bounded attempts."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    outcomes: list[str] = []
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        updated: list[Operation] = []
        terminal: list[Operation] = []
        for operation in active:
            if (
                operation.status != "running"
                or operation.lease_expires_at is None
                or operation.lease_expires_at > instant
            ):
                updated.append(operation)
                continue
            if operation.attempt_count < operation.max_attempts:
                updated.append(
                    replace(
                        operation,
                        status="ready",
                        updated_at=instant,
                        claimed_by_run_id="",
                        lease_expires_at=None,
                        last_error="lease_expired",
                    )
                )
                outcomes.append(f"{operation.operation_id}:ready:lease_expired")
            else:
                terminal.append(operation)
                outcomes.append(f"{operation.operation_id}:failed:retry_exhausted")
        if terminal:
            append_unique(
                repository_root,
                "operations_history",
                [
                    _history_row(
                        operation,
                        terminal_status="failed",
                        completed_at=instant,
                        result_path="",
                        result_summary="Lease expired after final attempt",
                        terminal_reason="retry_exhausted",
                    )
                    for operation in terminal
                ],
                key_columns=("operation_id",),
            )
        _write_active(repository_root, updated)
    return tuple(outcomes)


def claim_next(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    budget: RunBudget,
    estimated_cost: Decimal = Decimal("0"),
    operation_id: str | None = None,
    operation_type: str | None = None,
    now: datetime | None = None,
) -> Operation | None:
    """Claim at most one ready operation and establish a single live lease."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    _validate_run_id(run_id)
    if not budget.can_reserve(estimated_cost):
        return None
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        live = [
            operation
            for operation in active
            if operation.status == "running"
            and operation.lease_expires_at is not None
            and operation.lease_expires_at > instant
        ]
        if live:
            return None
        candidates = [
            operation
            for operation in active
            if operation.status == "ready"
            and operation.attempt_count < operation.max_attempts
            and (operation.not_before is None or operation.not_before <= instant)
            and (operation.deadline is None or operation.deadline > instant)
            and (operation_id is None or operation.operation_id == operation_id)
            and (operation_type is None or operation.operation_type == operation_type)
        ]
        candidates.sort(
            key=lambda operation: (
                -operation.priority,
                operation.created_at,
                operation.operation_id,
            )
        )
        if not candidates:
            return None
        selected = candidates[0]
        claimed = replace(
            selected,
            status="running",
            updated_at=instant,
            attempt_count=selected.attempt_count + 1,
            claimed_by_run_id=run_id,
            lease_expires_at=instant + settings.operations.lease_duration,
            last_error="",
        )
        _write_active(
            repository_root,
            [
                claimed if operation.operation_id == claimed.operation_id else operation
                for operation in active
            ],
        )
        budget.reserve(estimated_cost)
        return claimed


def complete_operation(
    repository_root: Path,
    *,
    operation_id: str,
    run_id: str,
    terminal_status: str,
    result_path: str,
    result_summary: str,
    terminal_reason: str,
    now: datetime | None = None,
) -> None:
    """Append the complete terminal record before removing the active request."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    _validate_run_id(run_id)
    if terminal_status not in HISTORY_STATUSES:
        raise QueueError(f"invalid terminal status: {terminal_status}")
    result = PurePosixPath(result_path)
    expected_result = PurePosixPath("data", "runs", run_id, operation_id, "agent_result.json")
    if result != expected_result:
        raise QueueError(f"invalid result path: {result_path!r}")
    normalized_summary = " ".join(result_summary.split())
    normalized_reason = " ".join(terminal_reason.split())
    if not normalized_summary or not normalized_reason:
        raise QueueError("completed operation requires a result summary and terminal reason")
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        operation = next(
            (candidate for candidate in active if candidate.operation_id == operation_id), None
        )
        if operation is None:
            archived = next(
                (
                    row
                    for row in read_table(repository_root, "operations_history")
                    if row["operation_id"] == operation_id
                ),
                None,
            )
            if archived is not None:
                expected_retry = {
                    "terminal_status": terminal_status,
                    "result_path": result_path,
                    "result_summary": normalized_summary,
                    "terminal_reason": normalized_reason,
                    "claimed_by_run_id": run_id,
                }
                if all(archived[field] == value for field, value in expected_retry.items()):
                    return
                raise QueueError(f"terminal retry conflicts with archived operation {operation_id}")
            raise QueueError(f"unknown active operation: {operation_id}")
        if operation.status != "running" or operation.claimed_by_run_id != run_id:
            raise QueueError(f"operation {operation_id} is not claimed by run {run_id}")
        _terminalize(
            repository_root,
            active,
            operation,
            terminal_status=terminal_status,
            completed_at=instant,
            result_path=result_path,
            result_summary=result_summary,
            terminal_reason=terminal_reason,
        )


def fail_attempt(
    repository_root: Path,
    *,
    operation_id: str,
    run_id: str,
    error: str,
    result_path: str = "",
    result_summary: str = "",
    now: datetime | None = None,
) -> str:
    """Release one failed claim for retry or terminate after the final attempt."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    _validate_run_id(run_id)
    reason = " ".join(error.split())[:1000]
    if not reason:
        raise QueueError("failed attempt requires an error")
    if bool(result_path) != bool(result_summary):
        raise QueueError("failed result path and summary must be provided together")
    if result_path:
        expected_result = PurePosixPath("data", "runs", run_id, operation_id, "agent_result.json")
        if PurePosixPath(result_path) != expected_result:
            raise QueueError(f"invalid failed result path: {result_path!r}")
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        operation = next(
            (candidate for candidate in active if candidate.operation_id == operation_id), None
        )
        if operation is None or operation.status != "running":
            raise QueueError(f"operation {operation_id} is not running")
        if operation.claimed_by_run_id != run_id:
            raise QueueError(f"operation {operation_id} is not claimed by run {run_id}")
        if operation.attempt_count >= operation.max_attempts:
            _terminalize(
                repository_root,
                active,
                operation,
                terminal_status="failed",
                completed_at=instant,
                result_path=result_path,
                result_summary=result_summary,
                terminal_reason=f"retry_exhausted:{reason}",
            )
            return "failed"
        released = replace(
            operation,
            status="waiting",
            updated_at=instant,
            claimed_by_run_id="",
            lease_expires_at=None,
            last_error=reason,
        )
        _write_active(
            repository_root,
            [
                released if candidate.operation_id == operation_id else candidate
                for candidate in active
            ],
        )
        return "waiting"


def block_operation(
    repository_root: Path,
    *,
    operation_id: str,
    run_id: str,
    reason: str,
    now: datetime | None = None,
) -> None:
    """Retain an auditable blocked request as active with its machine-readable reason."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    _validate_run_id(run_id)
    normalized = " ".join(reason.split())[:1000]
    if not normalized:
        raise QueueError("blocked operation requires a reason")
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        operation = next(
            (candidate for candidate in active if candidate.operation_id == operation_id), None
        )
        if (
            operation is None
            or operation.status != "running"
            or operation.claimed_by_run_id != run_id
        ):
            raise QueueError(f"operation {operation_id} is not claimed by run {run_id}")
        blocked = replace(
            operation,
            status="blocked",
            updated_at=instant,
            claimed_by_run_id="",
            lease_expires_at=None,
            last_error=normalized,
        )
        _write_active(
            repository_root,
            [
                blocked if candidate.operation_id == operation_id else candidate
                for candidate in active
            ],
        )


def resolve_blocked_operation(
    repository_root: Path,
    *,
    operation_id: str,
    run_id: str,
    terminal_status: str,
    result_path: str,
    result_summary: str,
    terminal_reason: str,
    now: datetime | None = None,
) -> None:
    """Archive an adjudicated blocked result without rewriting queue CSV state by hand."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    _validate_run_id(run_id)
    if terminal_status not in {"skipped", "cancelled"}:
        raise QueueError("blocked operations may resolve only as skipped or cancelled")
    expected_result = PurePosixPath("data", "runs", run_id, operation_id, "agent_result.json")
    if PurePosixPath(result_path) != expected_result:
        raise QueueError(f"invalid blocked result path: {result_path!r}")
    resolved_result = repository_root / expected_result
    if resolved_result.is_symlink() or not resolved_result.is_file():
        raise QueueError(f"blocked result is missing or a symlink: {result_path}")
    normalized_summary = " ".join(result_summary.split())
    normalized_reason = " ".join(terminal_reason.split())
    if not normalized_summary or not normalized_reason:
        raise QueueError("resolved blocked operation requires a summary and terminal reason")
    with _queue_lock(repository_root):
        active = _recover_archived(repository_root, _read_active(repository_root))
        operation = next(
            (candidate for candidate in active if candidate.operation_id == operation_id), None
        )
        if operation is None:
            archived = next(
                (
                    row
                    for row in read_table(repository_root, "operations_history")
                    if row["operation_id"] == operation_id
                ),
                None,
            )
            expected_retry = {
                "terminal_status": terminal_status,
                "result_path": result_path,
                "result_summary": normalized_summary,
                "terminal_reason": normalized_reason,
                "claimed_by_run_id": run_id,
            }
            if archived is not None and all(
                archived[field] == value for field, value in expected_retry.items()
            ):
                return
            if archived is not None:
                raise QueueError(
                    f"blocked resolution conflicts with archived operation {operation_id}"
                )
            raise QueueError(f"unknown active operation: {operation_id}")
        if operation.status != "blocked":
            raise QueueError(f"operation {operation_id} is not blocked")
        resolved = replace(operation, claimed_by_run_id=run_id)
        _terminalize(
            repository_root,
            active,
            resolved,
            terminal_status=terminal_status,
            completed_at=instant,
            result_path=result_path,
            result_summary=normalized_summary,
            terminal_reason=normalized_reason,
        )


def validate_queue(repository_root: Path) -> list[str]:
    """Return complete active/history/payload/sequentiality validation errors."""

    errors: list[str] = []
    try:
        active = _read_active(repository_root)
    except (CanonicalValueError, QueueError, OSError) as exc:
        return [str(exc)]
    seen_ids: set[str] = set()
    seen_dedupe: set[str] = set()
    for operation in active:
        if operation.operation_id in seen_ids:
            errors.append(f"duplicate active operation_id: {operation.operation_id}")
        seen_ids.add(operation.operation_id)
        if operation.dedupe_key in seen_dedupe:
            errors.append(f"duplicate active dedupe_key: {operation.dedupe_key}")
        seen_dedupe.add(operation.dedupe_key)
        try:
            validate_operation_payload(repository_root, operation)
        except QueueError as exc:
            errors.append(str(exc))
    live_running = [operation for operation in active if operation.status == "running"]
    if len(live_running) > 1:
        errors.append("more than one operation is running")
    try:
        history = read_table(repository_root, "operations_history")
    except (CanonicalValueError, OSError) as exc:
        errors.append(str(exc))
        return errors
    history_ids: set[str] = set()
    for row in history:
        operation_id = row["operation_id"]
        try:
            operation = Operation.from_row(row, archived=True)
            completed_at = _canonical_time(row["completed_at"], "completed_at")
            assert completed_at is not None
            if completed_at < operation.updated_at:
                raise QueueError(f"history {operation_id} completed_at precedes updated_at")
            if row["result_path"]:
                expected_result = PurePosixPath(
                    "data",
                    "runs",
                    operation.claimed_by_run_id,
                    operation_id,
                    "agent_result.json",
                )
                if PurePosixPath(row["result_path"]) != expected_result:
                    raise QueueError(f"history {operation_id} has invalid result_path")
        except (CanonicalValueError, QueueError) as exc:
            errors.append(str(exc))
        if operation_id in history_ids:
            errors.append(f"duplicate history operation_id: {operation_id}")
        history_ids.add(operation_id)
        if row["terminal_status"] not in HISTORY_STATUSES:
            errors.append(f"history {operation_id} has invalid terminal_status")
        if not row["terminal_reason"] or any(marker in row["terminal_reason"] for marker in "\r\n"):
            errors.append(f"history {operation_id} lacks terminal_reason")
    overlap = seen_ids.intersection(history_ids)
    if overlap:
        errors.append(f"operations exist in active queue and history: {sorted(overlap)}")
    return errors

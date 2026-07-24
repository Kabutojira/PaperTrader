"""Tamper-evident-enough CLI receipts for structured agent state changes."""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

from papertrader.atomic_io import atomic_write_json
from papertrader.repository_state import RepositorySnapshot, compare_snapshots
from papertrader.utils import format_timestamp, validate_ulid

SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class CommandAuditError(ValueError):
    """Raised when an agent command-audit location or document is invalid."""


@dataclass(frozen=True, slots=True)
class CommandAuditContext:
    """Validated operation identity and canonical receipt path."""

    run_id: str
    operation_id: str
    path: Path


def audit_context(
    repository_root: Path, environment: Mapping[str, str]
) -> CommandAuditContext | None:
    """Resolve an opt-in audit context passed only to the Hermes child process."""

    run_id = environment.get("PAPERTRADER_AUDIT_RUN_ID", "")
    operation_id = environment.get("PAPERTRADER_AUDIT_OPERATION_ID", "")
    raw_path = environment.get("PAPERTRADER_AUDIT_PATH", "")
    if not any((run_id, operation_id, raw_path)):
        return None
    if not all((run_id, operation_id, raw_path)):
        raise CommandAuditError("incomplete PaperTrader command-audit environment")
    if not SAFE_RUN_ID.fullmatch(run_id):
        raise CommandAuditError(f"invalid audit run_id: {run_id!r}")
    validate_ulid(operation_id)
    relative = PurePosixPath(raw_path)
    expected = PurePosixPath("data", "runs", run_id, operation_id, "command_audit.json")
    if relative != expected:
        raise CommandAuditError(f"invalid command-audit path: {raw_path!r}")
    path = repository_root.joinpath(*relative.parts)
    if path.is_symlink():
        raise CommandAuditError("command-audit path must not be a symlink")
    return CommandAuditContext(run_id=run_id, operation_id=operation_id, path=path)


def canonical_command(arguments: Sequence[str]) -> str:
    """Render an installed-project CLI invocation without shell interpretation."""

    return shlex.join(("papertrader", *arguments))


def _request_receipt(
    repository_root: Path,
    arguments: Sequence[str],
    before: RepositorySnapshot,
) -> dict[str, object] | None:
    """Bind a request-bearing command to the exact JSON bytes it consumed."""

    raw_paths: list[str] = []
    for index, argument in enumerate(arguments):
        if argument == "--request" and index + 1 < len(arguments):
            raw_paths.append(arguments[index + 1])
        elif argument.startswith("--request="):
            raw_paths.append(argument.split("=", maxsplit=1)[1])
    if not raw_paths:
        return None
    if len(raw_paths) != 1:
        return {"path": "", "identity": None}
    candidate = Path(raw_paths[0])
    path = candidate if candidate.is_absolute() else repository_root / candidate
    try:
        relative = path.resolve(strict=True).relative_to(repository_root.resolve(strict=True))
    except (OSError, ValueError):
        return {"path": "", "identity": None}
    state = before.files.get(relative.as_posix())
    if state is None or state.kind != "file":
        return {"path": relative.as_posix(), "identity": None}
    return {"path": relative.as_posix(), "identity": list(state.content_identity)}


def record_command(
    repository_root: Path,
    context: CommandAuditContext,
    *,
    arguments: Sequence[str],
    exit_code: int,
    started_at: datetime,
    completed_at: datetime,
    before: RepositorySnapshot,
    after: RepositorySnapshot,
) -> None:
    """Append one canonical command receipt using an atomic JSON replacement."""

    document: dict[str, object]
    if context.path.exists():
        value = json.loads(context.path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise CommandAuditError("command-audit document must be an object")
        document = value
    else:
        document = {
            "audit_version": 1,
            "run_id": context.run_id,
            "operation_id": context.operation_id,
            "entries": [],
        }
    if (
        document.get("audit_version") != 1
        or document.get("run_id") != context.run_id
        or document.get("operation_id") != context.operation_id
    ):
        raise CommandAuditError("command-audit identity conflicts with the current operation")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise CommandAuditError("command-audit entries must be an array")
    delta = compare_snapshots(before, after)
    changes = []
    for path in delta.changed:
        before_state = before.files.get(path)
        after_state = after.files.get(path)
        changes.append(
            {
                "path": path,
                "before": list(before_state.content_identity) if before_state else None,
                "after": list(after_state.content_identity) if after_state else None,
            }
        )
    entries.append(
        {
            "command": canonical_command(arguments),
            "argv": ["papertrader", *arguments],
            "request": _request_receipt(repository_root, arguments, before),
            "started_at": format_timestamp(started_at),
            "completed_at": format_timestamp(completed_at),
            "exit_code": exit_code,
            "changed_paths": list(delta.changed),
            "changes": changes,
        }
    )
    context.path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(context.path, document, allowed_root=repository_root)

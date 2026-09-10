"""Bounded working-tree retention for run evidence that Git history already preserves.

Every daily cycle leaves immutable artifacts under ``data/runs/<cycle>/``.  Most of them are
replay evidence (prompts, Hermes transcripts, validation reports, command receipts) or bulky
snapshots that are only read while the cycle is live.  This module removes those files from
the working tree once a cycle is older than the configured retention window and records a
signed-by-hash manifest beside the cycle so integrity checks, operators, and the wiki keep an
exact pointer to the pruned content.  Nothing is rewritten in history: every pruned file is
recoverable with ``git show <commit>:<path>``.

Files that other subsystems read after a cycle completes are never pruned: ``agent_result.json``
(referenced by ``operations_history.csv`` and research pages), ``daily_run.json``,
``agent_batch.json``, allocation plans, source-discovery artifacts, podcast context, and request
receipts.  The published decision snapshot's owning cycle and every unfinished cycle are also
protected regardless of age.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.utils import (
    content_hash,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    utc_now,
)

RETENTION_MARKER = "retention.json"
RETENTION_VERSION = 1
PRUNABLE_CYCLE_FILES = frozenset({"decision_snapshot.json"})
PRUNABLE_OPERATION_FILES = frozenset(
    {
        "candidate_slate.json",
        "command_audit.json",
        "controller_prompt.md",
        "harness_preflight.json",
        "hermes_preflight.json",
        "hermes_run.json",
        "profile_route.json",
        "validation_report.json",
    }
)
MINIMUM_RETENTION_DAYS = 7


class RetentionError(RuntimeError):
    """Raised when run retention cannot be applied safely."""


@dataclass(frozen=True, slots=True)
class RetentionResult:
    """Deterministic summary of one pruning pass."""

    retention_days: int
    cutoff: str
    protected_run_ids: tuple[str, ...]
    pruned_run_ids: tuple[str, ...]
    pruned_paths: tuple[str, ...]
    bytes_pruned: int
    dry_run: bool


def _load_json_object(path: Path) -> dict[str, object] | None:
    if path.is_symlink() or not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _cycle_finished_at(manifest: Mapping[str, object]) -> datetime | None:
    """Return when a cycle stopped changing, or None while it may still be live."""

    version = manifest.get("daily_run_version")
    status = manifest.get("status")
    if version == 2:
        if not manifest.get("finalization_at"):
            return None
        if manifest.get("podcast_status") in {"pending", "running"}:
            return None
    elif status not in {"succeeded", "degraded", "failed"}:
        return None
    for field in ("completion_at", "podcast_text_at", "completed_at", "finalization_at"):
        raw = manifest.get(field)
        if isinstance(raw, str) and raw:
            parsed = parse_timestamp(raw)
            if parsed is not None:
                return parsed
    return None


def protected_run_ids(repository_root: Path) -> tuple[str, ...]:
    """Return cycles that must keep every artifact regardless of age."""

    protected: set[str] = set()
    published = _load_json_object(repository_root / "data" / "published" / "decision_snapshot.json")
    if published is not None and isinstance(published.get("run_id"), str):
        protected.add(str(published["run_id"]))
    latest: tuple[datetime, str] | None = None
    for manifest_path, manifest in _cycle_manifests(repository_root):
        run_id = manifest_path.parent.name
        finished_at = _cycle_finished_at(manifest)
        if finished_at is None:
            protected.add(run_id)
            continue
        if run_id.startswith("daily-") and (latest is None or (finished_at, run_id) > latest):
            latest = (finished_at, run_id)
    if latest is not None:
        protected.add(latest[1])
    return tuple(sorted(protected))


def _cycle_manifests(repository_root: Path) -> Iterator[tuple[Path, dict[str, object]]]:
    runs_root = repository_root / "data" / "runs"
    if runs_root.is_symlink() or not runs_root.is_dir():
        return
    for manifest_path in sorted(runs_root.glob("*/daily_run.json")):
        if manifest_path.parent.is_symlink():
            continue
        manifest = _load_json_object(manifest_path)
        if manifest is None or manifest.get("run_id") != manifest_path.parent.name:
            continue
        yield manifest_path, manifest


def prunable_paths(run_directory: Path) -> tuple[Path, ...]:
    """Return every prunable regular file currently present under one cycle directory."""

    candidates: list[Path] = []
    for name in sorted(PRUNABLE_CYCLE_FILES):
        candidates.append(run_directory / name)
    for child in sorted(run_directory.iterdir()):
        if child.is_symlink() or not child.is_dir():
            continue
        for name in sorted(PRUNABLE_OPERATION_FILES):
            candidates.append(child / name)
    return tuple(path for path in candidates if not path.is_symlink() and path.is_file())


def load_retention_marker(run_directory: Path) -> dict[str, object] | None:
    """Return the cycle's retention manifest when one exists."""

    return _load_json_object(run_directory / RETENTION_MARKER)


def prune_run_artifacts(
    repository_root: Path,
    settings: Settings,
    *,
    retention_days: int | None = None,
    now: datetime | None = None,
    dry_run: bool = False,
) -> RetentionResult:
    """Remove prunable evidence from cycles older than the retention window."""

    days = (
        settings.operations.run_artifact_retention_days
        if retention_days is None
        else retention_days
    )
    if days < MINIMUM_RETENTION_DAYS:
        raise RetentionError(
            f"run artifact retention must keep at least {MINIMUM_RETENTION_DAYS} days"
        )
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    cutoff = instant - timedelta(days=days)
    protected = protected_run_ids(repository_root)
    pruned_runs: list[str] = []
    pruned_paths: list[str] = []
    bytes_pruned = 0
    root = repository_root.resolve(strict=True)
    for manifest_path, manifest in _cycle_manifests(repository_root):
        run_directory = manifest_path.parent
        run_id = run_directory.name
        if run_id in protected:
            continue
        finished_at = _cycle_finished_at(manifest)
        if finished_at is None or finished_at >= cutoff:
            continue
        candidates = prunable_paths(run_directory)
        if not candidates:
            continue
        marker = load_retention_marker(run_directory) or {
            "run_retention_version": RETENTION_VERSION,
            "run_id": run_id,
            "artifacts": [],
        }
        raw_entries = marker.get("artifacts")
        entries: list[dict[str, object]] = (
            [dict(entry) for entry in raw_entries if isinstance(entry, dict)]
            if isinstance(raw_entries, list)
            else []
        )
        known = {str(entry.get("path")) for entry in entries}
        for path in candidates:
            relative = PurePosixPath(path.relative_to(root).as_posix()).as_posix()
            content = path.read_bytes()
            entry: dict[str, object] = {
                "path": relative,
                "sha256": content_hash(content),
                "size": len(content),
                "pruned_at": format_timestamp(instant),
            }
            if path.name == "decision_snapshot.json":
                snapshot = _load_json_object(path)
                snapshot_id = snapshot.get("snapshot_id") if snapshot is not None else None
                if not isinstance(snapshot_id, str) or not snapshot_id:
                    raise RetentionError(f"decision snapshot lacks an identity: {relative}")
                entry["snapshot_id"] = snapshot_id
            if relative not in known:
                entries.append(entry)
                known.add(relative)
            pruned_paths.append(relative)
            bytes_pruned += len(content)
        pruned_runs.append(run_id)
        if dry_run:
            continue
        marker.update(
            {
                "run_retention_version": RETENTION_VERSION,
                "run_id": run_id,
                "retention_days": days,
                "pruned_at": format_timestamp(instant),
                "artifacts": sorted(entries, key=lambda item: str(item["path"])),
            }
        )
        atomic_write_json(run_directory / RETENTION_MARKER, marker, allowed_root=repository_root)
        for path in candidates:
            path.unlink()
    return RetentionResult(
        retention_days=days,
        cutoff=format_timestamp(cutoff),
        protected_run_ids=protected,
        pruned_run_ids=tuple(pruned_runs),
        pruned_paths=tuple(pruned_paths),
        bytes_pruned=bytes_pruned,
        dry_run=dry_run,
    )


__all__ = [
    "MINIMUM_RETENTION_DAYS",
    "PRUNABLE_CYCLE_FILES",
    "PRUNABLE_OPERATION_FILES",
    "RETENTION_MARKER",
    "RETENTION_VERSION",
    "RetentionError",
    "RetentionResult",
    "load_retention_marker",
    "protected_run_ids",
    "prunable_paths",
    "prune_run_artifacts",
]

"""Deterministic context, assembly, and audit boundaries for the daily podcast."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.issues import record_issue
from papertrader.logs import append_event
from papertrader.queue import enqueue_operation
from papertrader.tables import read_table
from papertrader.utils import content_hash, ensure_utc, format_timestamp, parse_timestamp, utc_now

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
ULID = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")
PODCAST_PAGE = re.compile(r"^data/wiki/podcasts/daily-podcast_[0-9]{8}\.md$")
PODCAST_AUDIO = re.compile(r"^data/wiki/podcasts/daily-podcast_[0-9]{8}\.mp3$")
MINIMUM_SCRIPT_WORDS = 2400
MAXIMUM_SCRIPT_WORDS = 3600
MINIMUM_DURATION_SECONDS = 16 * 60
MAXIMUM_DURATION_SECONDS = 24 * 60


class PodcastError(RuntimeError):
    """Raised when podcast state or generated media fails closed."""


@dataclass(frozen=True, slots=True)
class PodcastEnqueueResult:
    run_id: str
    operation_id: str
    created: bool
    context_path: str


@dataclass(frozen=True, slots=True)
class PodcastAssembly:
    run_id: str
    operation_id: str
    output_path: str
    word_count: int
    duration_seconds: int
    sha256: str


def _manifest_path(repository_root: Path, run_id: str) -> Path:
    if not RUN_ID.fullmatch(run_id):
        raise PodcastError(f"invalid run_id: {run_id!r}")
    return repository_root / "data" / "runs" / run_id / "daily_run.json"


def _load_object(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise PodcastError(f"required podcast input is unavailable: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PodcastError(f"cannot read {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise PodcastError(f"{path.name} must contain an object")
    return value


def _source_items(repository_root: Path, run_id: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    histories = {
        row["operation_id"]: row
        for row in read_table(repository_root, "operations_history")
        if row["claimed_by_run_id"] == run_id
    }
    order = {
        "source_discovery": 10,
        "wiki_ingest": 20,
        "idea_research": 30,
        "opportunity_research": 40,
        "quick_check_research": 50,
        "security_research": 60,
        "relationship_research": 70,
        "strategy_research": 80,
        "execute_strategy": 90,
    }
    for operation_id, row in histories.items():
        result_path = row["result_path"]
        if not result_path:
            continue
        result = _load_object(repository_root / result_path)
        evidence = result.get("evidence", [])
        report_items = result.get("daily_report_items", [])
        changed = result.get("files_changed", [])
        items.append(
            {
                "sequence_group": order.get(row["operation_type"], 100),
                "operation_id": operation_id,
                "operation_type": row["operation_type"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "status": row["terminal_status"],
                "summary": row["result_summary"],
                "evidence": evidence if isinstance(evidence, list) else [],
                "daily_report_items": report_items if isinstance(report_items, list) else [],
                "files_changed": changed if isinstance(changed, list) else [],
                "result_path": result_path,
            }
        )
    items.sort(
        key=lambda item: (
            item["sequence_group"] if isinstance(item["sequence_group"], int) else 100,
            str(item["entity_type"]),
            str(item["entity_id"]),
            str(item["operation_id"]),
        )
    )
    return items


def enqueue_daily_podcast(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    now: datetime | None = None,
) -> PodcastEnqueueResult:
    """Collect one completed run's accepted changes and enqueue its final sequential podcast."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    manifest_path = _manifest_path(repository_root, run_id)
    manifest = _load_object(manifest_path)
    if manifest.get("run_id") != run_id or manifest.get("status") not in {
        "succeeded",
        "degraded",
    }:
        raise PodcastError("daily podcast requires a completed daily run")
    report_path = manifest.get("report_path")
    completed_at = manifest.get("completed_at")
    if not isinstance(report_path, str) or not isinstance(completed_at, str):
        raise PodcastError("completed daily run lacks report identity")
    report_date = parse_timestamp(completed_at)
    if report_date is None:
        raise PodcastError("completed daily run has an invalid completion time")
    stamp = report_date.strftime("%Y%m%d")
    page_path = f"data/wiki/podcasts/daily-podcast_{stamp}.md"
    audio_path = f"data/wiki/podcasts/daily-podcast_{stamp}.mp3"
    context_relative = f"data/runs/{run_id}/podcast_context.json"
    context_path = repository_root / context_relative
    context = {
        "podcast_context_version": 1,
        "run_id": run_id,
        "generated_at": format_timestamp(instant),
        "report_path": report_path,
        "decision_snapshot_path": f"data/runs/{run_id}/decision_snapshot.json",
        "wiki_orientation_paths": [
            "data/wiki/SCHEMA.md",
            "data/wiki/index.md",
            "data/wiki/research-catalog.md",
            "data/wiki/log.md",
        ],
        "source_items": _source_items(repository_root, run_id),
        "target_minutes": 20,
        "target_words": 3000,
        "page_path": page_path,
        "audio_path": audio_path,
    }
    if context_path.exists():
        existing = _load_object(context_path)
        stable_existing = {key: value for key, value in existing.items() if key != "generated_at"}
        stable_context = {key: value for key, value in context.items() if key != "generated_at"}
        if stable_existing != stable_context:
            raise PodcastError("immutable daily podcast context conflicts with completed run")
    else:
        atomic_write_json(context_path, context, allowed_root=repository_root)
    operation_id, created = enqueue_operation(
        repository_root,
        settings,
        operation_type="daily_podcast",
        entity_type="run",
        entity_id=run_id,
        dedupe_key=f"daily_podcast:{run_id}:v1",
        prompt=(
            f"Create the {stamp} PaperTrader daily podcast from this run's accepted changes and "
            "linked wiki, aiming for twenty minutes."
        ),
        inputs={
            "run_id": run_id,
            "context_path": context_relative,
            "report_path": report_path,
            "page_path": page_path,
            "audio_path": audio_path,
            "target_minutes": 20,
            "target_words": 3000,
        },
        source="deterministic-daily-podcast",
        source_refs=(context_relative, report_path),
        priority=100,
        max_attempts=1,
        now=instant,
    )
    updated_manifest = {
        **manifest,
        "podcast_status": "queued",
        "podcast_operation_id": operation_id,
        "podcast_page_path": page_path,
        "podcast_audio_path": audio_path,
    }
    atomic_write_json(manifest_path, updated_manifest, allowed_root=repository_root)
    return PodcastEnqueueResult(run_id, operation_id, created, context_relative)


def _repository_path(repository_root: Path, raw: str, pattern: re.Pattern[str]) -> Path:
    if not pattern.fullmatch(raw):
        raise PodcastError(f"invalid podcast path: {raw}")
    path = repository_root.joinpath(*PurePosixPath(raw).parts)
    if path.is_symlink():
        raise PodcastError(f"podcast path must not be a symlink: {raw}")
    return path


def assemble_podcast(
    repository_root: Path,
    request: Mapping[str, object],
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Validate a bounded script and atomically concatenate Hermes TTS chunks into MP3."""

    run_id = str(request.get("run_id", ""))
    operation_id = str(request.get("operation_id", ""))
    if not RUN_ID.fullmatch(run_id) or not ULID.fullmatch(operation_id):
        raise PodcastError("podcast assembly identity is invalid")
    script_raw = str(request.get("script_path", ""))
    output_raw = str(request.get("output_path", ""))
    script = _repository_path(repository_root, script_raw, PODCAST_PAGE)
    output = _repository_path(repository_root, output_raw, PODCAST_AUDIO)
    if not script.is_file():
        raise PodcastError("podcast script is unavailable")
    words = re.findall(r"\b[\w'-]+\b", script.read_text(encoding="utf-8"))
    word_count = len(words)
    if not MINIMUM_SCRIPT_WORDS <= word_count <= MAXIMUM_SCRIPT_WORDS:
        raise PodcastError(
            f"podcast script must contain {MINIMUM_SCRIPT_WORDS}-{MAXIMUM_SCRIPT_WORDS} words"
        )
    raw_chunks = request.get("chunk_paths")
    if not isinstance(raw_chunks, list) or not 2 <= len(raw_chunks) <= 12:
        raise PodcastError("podcast assembly requires 2-12 TTS chunks")
    operation_root = repository_root / "data" / "runs" / run_id / operation_id
    chunks: list[Path] = []
    for raw in raw_chunks:
        if not isinstance(raw, str):
            raise PodcastError("podcast chunk paths must be strings")
        relative = PurePosixPath(raw)
        chunk = repository_root.joinpath(*relative.parts)
        try:
            chunk.resolve(strict=True).relative_to(operation_root.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise PodcastError(f"podcast chunk escapes its operation directory: {raw}") from exc
        if chunk.is_symlink() or chunk.suffix != ".mp3" or not chunk.is_file():
            raise PodcastError(f"invalid podcast TTS chunk: {raw}")
        chunks.append(chunk)
    temporary_output = output.with_suffix(".mp3.tmp")
    try:
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if ffmpeg is None or ffprobe is None:
            raise PodcastError("ffmpeg and ffprobe are required for podcast assembly")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=operation_root) as temporary:
            temporary_root = Path(temporary)
            concat = temporary_root / "concat.txt"
            concat.write_text(
                "".join(f"file '{path.as_posix()}'\n" for path in chunks),
                encoding="utf-8",
            )
            assembled = temporary_root / "assembled.mp3"
            completed = runner(
                [
                    ffmpeg,
                    "-v",
                    "error",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(concat),
                    "-c",
                    "copy",
                    "-y",
                    str(assembled),
                ],
                check=False,
                capture_output=True,
            )
            if (
                completed.returncode != 0
                or not assembled.is_file()
                or assembled.stat().st_size == 0
            ):
                raise PodcastError("ffmpeg could not assemble the Hermes TTS chunks")
            probe = runner(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(assembled),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            try:
                duration = round(float(probe.stdout.strip()))
            except (AttributeError, ValueError) as exc:
                raise PodcastError("ffprobe returned no valid podcast duration") from exc
            if (
                probe.returncode != 0
                or not MINIMUM_DURATION_SECONDS <= duration <= MAXIMUM_DURATION_SECONDS
            ):
                raise PodcastError("assembled podcast duration must be between 16 and 24 minutes")
            with assembled.open("rb") as handle:
                audio = handle.read()
            with temporary_output.open("wb") as handle:
                handle.write(audio)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_output, output)
    finally:
        temporary_output.unlink(missing_ok=True)
        for chunk in chunks:
            chunk.unlink(missing_ok=True)
    return PodcastAssembly(
        run_id,
        operation_id,
        output_raw,
        word_count,
        duration,
        content_hash(output.read_bytes()),
    )


def finalize_daily_podcast(
    repository_root: Path,
    *,
    run_id: str,
    now: datetime | None = None,
) -> str:
    """Record the terminal podcast disposition on its completed daily manifest."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    path = _manifest_path(repository_root, run_id)
    manifest = _load_object(path)
    operation_id = manifest.get("podcast_operation_id")
    if not isinstance(operation_id, str) or not ULID.fullmatch(operation_id):
        raise PodcastError("daily run has no podcast operation identity")
    row = next(
        (
            value
            for value in read_table(repository_root, "operations_history")
            if value["operation_id"] == operation_id
            and value["operation_type"] == "daily_podcast"
            and value["entity_id"] == run_id
        ),
        None,
    )
    if row is None:
        active = next(
            (
                value
                for value in read_table(repository_root, "operations_todo")
                if value["operation_id"] == operation_id
                and value["operation_type"] == "daily_podcast"
                and value["entity_id"] == run_id
                and value["status"] == "blocked"
            ),
            None,
        )
        if active is not None:
            row = {
                **active,
                "terminal_status": "blocked",
                "result_summary": active["last_error"],
                "terminal_reason": active["last_error"],
            }
    if row is None:
        raise PodcastError("daily podcast operation has no final disposition")
    status = row["terminal_status"]
    if status == "succeeded":
        page = repository_root / str(manifest.get("podcast_page_path", ""))
        audio = repository_root / str(manifest.get("podcast_audio_path", ""))
        if page.is_symlink() or audio.is_symlink() or not page.is_file() or not audio.is_file():
            raise PodcastError("succeeded daily podcast lacks its page or audio")
    else:
        record_issue(
            repository_root,
            severity="warning",
            title=f"Daily podcast {status}: {run_id}",
            description=row["result_summary"] or row["terminal_reason"],
            owner="delivery",
            related_run_id=run_id,
            related_operation_id=operation_id,
            now=instant,
        )
    manifest["podcast_status"] = status
    atomic_write_json(path, manifest, allowed_root=repository_root)
    append_event(
        repository_root,
        event_type="daily_podcast_completed",
        message=f"Daily podcast finished with status {status}.",
        run_id=run_id,
        operation_id=operation_id,
        data={
            "audio_path": manifest.get("podcast_audio_path", "") if status == "succeeded" else ""
        },
        occurred_at=instant,
    )
    return status


__all__ = [
    "PodcastAssembly",
    "PodcastEnqueueResult",
    "PodcastError",
    "assemble_podcast",
    "enqueue_daily_podcast",
    "finalize_daily_podcast",
]

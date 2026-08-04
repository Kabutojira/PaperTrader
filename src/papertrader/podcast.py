"""Deterministic context, assembly, and audit boundaries for the daily podcast."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
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
PODCAST_PAGE = re.compile(r"^data/wiki/podcasts/daily-podcast_[0-9]{8}T[0-9]{6}Z\.md$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
TRANSCRIPT_START = "<!-- papertrader-spoken-transcript:start -->"
TRANSCRIPT_END = "<!-- papertrader-spoken-transcript:end -->"
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
    daily_cycle_id: str
    script_commit: str
    script_path: str
    audio_path: str
    manifest_path: str
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


def _source_items(
    repository_root: Path,
    run_id: str,
    *,
    started_at: datetime,
    cutoff: datetime,
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    manifest = _load_object(_manifest_path(repository_root, run_id))
    accepted_values = manifest.get("operations_accepted", [])
    if not isinstance(accepted_values, list):
        raise PodcastError("daily cycle accepted-operation accounting is invalid")
    accepted = {
        str(item.get("operation_id")): item
        for item in accepted_values
        if isinstance(item, dict) and isinstance(item.get("operation_id"), str)
    }
    histories = {
        row["operation_id"]: row
        for row in read_table(repository_root, "operations_history")
        if row["claimed_by_run_id"] == run_id
        and (completed := parse_timestamp(row["completed_at"])) is not None
        and started_at <= completed <= cutoff
    }
    active = {
        row["operation_id"]: row
        for row in read_table(repository_root, "operations_todo")
        if row["operation_id"] in accepted
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
    for operation_id in sorted(set(histories) | set(accepted)):
        row = histories.get(operation_id) or active.get(operation_id)
        if row is None:
            raise PodcastError(
                f"accepted cycle operation is missing from queue state: {operation_id}"
            )
        result_path = row.get("result_path", "") or (
            f"data/runs/{run_id}/{operation_id}/agent_result.json"
        )
        route_path = repository_root / result_path
        profile_file = route_path.with_name("profile_route.json")
        profile = _load_object(profile_file) if profile_file.is_file() else {}
        result_file = repository_root / result_path
        validation: dict[str, object] = {}
        if result_file.is_file() and not result_file.is_symlink():
            result = _load_object(result_file)
        else:
            validation_file = route_path.with_name("validation_report.json")
            validation = _load_object(validation_file)
            result_path = validation_file.relative_to(repository_root).as_posix()
            raw_errors = validation.get("errors", [])
            failure_errors = raw_errors if isinstance(raw_errors, list) else []
            result = {
                "summary": row.get("last_error", "")
                or row.get("terminal_reason", "")
                or "The controller rejected this operation's repository delta.",
                "evidence": [
                    {
                        "source": result_path,
                        "claim": str(error),
                    }
                    for error in failure_errors
                    if isinstance(error, str)
                ],
                "daily_report_items": [],
                "files_changed": [],
            }
        run_artifact = _load_object(route_path.with_name("hermes_run.json"))
        completed_at = row.get("completed_at", "") or str(run_artifact.get("completed_at", ""))
        completed = parse_timestamp(completed_at)
        if completed is None or not started_at <= completed <= cutoff:
            raise PodcastError(f"accepted operation falls outside the cycle cutoff: {operation_id}")
        accepted_item = accepted.get(operation_id, {})
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
                "status": row.get("terminal_status", "")
                or str(accepted_item.get("terminal_status", "")),
                "summary": row.get("result_summary", "") or str(result.get("summary", "")),
                "evidence": evidence if isinstance(evidence, list) else [],
                "daily_report_items": report_items if isinstance(report_items, list) else [],
                "files_changed": changed if isinstance(changed, list) else [],
                "result_path": result_path,
                "completed_at": completed_at,
                "profile": profile.get("profile", ""),
                "profile_policy_version": profile.get("profile_policy_version", ""),
                "route_reason": profile.get("route_reason", ""),
                "effective_model": profile.get("effective_model", ""),
                "weighted_cost": profile.get("weighted_cost", ""),
                "rejected_paths": validation.get("changed_paths", []),
                "failure_errors": validation.get("errors", []),
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
    version = manifest.get("daily_run_version")
    if manifest.get("run_id") != run_id:
        raise PodcastError("daily podcast run identity differs from its manifest")
    if version == 2:
        if not manifest.get("finalization_at") or manifest.get("status") not in {
            "running",
            "degraded",
        }:
            raise PodcastError("daily podcast requires a finalized daily cycle")
    elif manifest.get("status") not in {"succeeded", "degraded"}:
        raise PodcastError("daily podcast requires a completed daily run")
    report_path = manifest.get("report_path")
    completed_at = manifest.get("research_cutoff_at") or manifest.get("completed_at")
    if not isinstance(report_path, str) or not isinstance(completed_at, str):
        raise PodcastError("completed daily run lacks report identity")
    report_date = parse_timestamp(completed_at)
    if report_date is None:
        raise PodcastError("completed daily run has an invalid completion time")
    started_at = parse_timestamp(str(manifest.get("started_at", "")))
    if started_at is None or started_at > report_date:
        raise PodcastError("daily cycle has an invalid podcast evidence window")
    stamp = (
        run_id.removeprefix("daily-") if version == 2 else report_date.strftime("%Y%m%dT%H%M%SZ")
    )
    page_path = f"data/wiki/podcasts/daily-podcast_{stamp}.md"
    context_relative = f"data/runs/{run_id}/podcast_context.json"
    context_path = repository_root / context_relative
    context = {
        "podcast_context_version": 2,
        "run_id": run_id,
        "daily_cycle_id": run_id,
        "generated_at": format_timestamp(instant),
        "started_at": format_timestamp(started_at),
        "research_cutoff_at": format_timestamp(report_date),
        "report_path": report_path,
        "report_sha256": content_hash((repository_root / report_path).read_bytes()),
        "decision_snapshot_path": f"data/runs/{run_id}/decision_snapshot.json",
        "decision_snapshot_sha256": content_hash(
            (repository_root / "data" / "runs" / run_id / "decision_snapshot.json").read_bytes()
        ),
        "wiki_orientation_paths": [
            "data/wiki/SCHEMA.md",
            "data/wiki/index.md",
            "data/wiki/research-catalog.md",
            "data/wiki/log.md",
        ],
        "source_items": _source_items(
            repository_root, run_id, started_at=started_at, cutoff=report_date
        ),
        "fill_outcomes": manifest.get("fill_outcomes", []),
        "finalization_status": manifest.get("finalization_status", manifest.get("status")),
        "snapshot_id": manifest.get("snapshot_id", ""),
        "target_minutes": 20,
        "target_words": 3000,
        "page_path": page_path,
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
        dedupe_key=f"daily_podcast:{run_id}:text-v2",
        prompt=(
            f"Create the {stamp} PaperTrader daily podcast from this run's accepted changes and "
            "linked wiki, aiming for twenty minutes."
        ),
        inputs={
            "run_id": run_id,
            "context_path": context_relative,
            "report_path": report_path,
            "page_path": page_path,
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
        "podcast_audio_path": "",
    }
    atomic_write_json(manifest_path, updated_manifest, allowed_root=repository_root)
    return PodcastEnqueueResult(run_id, operation_id, created, context_relative)


def build_podcast_context(
    repository_root: Path,
    settings: Settings,
    *,
    daily_cycle_id: str,
    cutoff: datetime,
    now: datetime | None = None,
) -> str:
    """Freeze and validate the complete cycle context before text-only inference."""

    manifest = _load_object(_manifest_path(repository_root, daily_cycle_id))
    frozen = parse_timestamp(str(manifest.get("research_cutoff_at", "")))
    if frozen is None or ensure_utc(cutoff).replace(microsecond=0) != frozen:
        raise PodcastError("podcast context cutoff must equal the frozen research cutoff")
    result = enqueue_daily_podcast(repository_root, settings, run_id=daily_cycle_id, now=now)
    return result.context_path


def _repository_path(repository_root: Path, raw: str, pattern: re.Pattern[str]) -> Path:
    if not pattern.fullmatch(raw):
        raise PodcastError(f"invalid podcast path: {raw}")
    path = repository_root.joinpath(*PurePosixPath(raw).parts)
    if path.is_symlink():
        raise PodcastError(f"podcast path must not be a symlink: {raw}")
    return path


def _spoken_transcript(markdown: str) -> str:
    if markdown.count(TRANSCRIPT_START) != 1 or markdown.count(TRANSCRIPT_END) != 1:
        raise PodcastError("podcast page must contain one bounded spoken-transcript section")
    _, remainder = markdown.split(TRANSCRIPT_START, maxsplit=1)
    transcript, _ = remainder.split(TRANSCRIPT_END, maxsplit=1)
    transcript = transcript.strip()
    if not transcript:
        raise PodcastError("spoken podcast transcript is empty")
    return transcript


def assemble_podcast(
    repository_root: Path,
    request: Mapping[str, object],
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Reject the superseded repository-writing media assembly boundary."""

    del repository_root, request, runner
    raise PodcastError(
        "repository podcast assembly is disabled; render an exact committed transcript "
        "ephemerally with podcast render"
    )


def _transcript_chunks(transcript: str, limit: int) -> tuple[str, ...]:
    paragraphs = [" ".join(value.split()) for value in re.split(r"\n\s*\n", transcript)]
    paragraphs = [value for value in paragraphs if value]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > limit:
            raise PodcastError("one transcript paragraph exceeds the deterministic TTS limit")
        proposed = f"{current}\n\n{paragraph}" if current else paragraph
        if current and len(proposed) > limit:
            chunks.append(current)
            current = paragraph
        else:
            current = proposed
    if current:
        chunks.append(current)
    if not 2 <= len(chunks) <= 12:
        raise PodcastError("spoken transcript must split into 2-12 deterministic chunks")
    return tuple(chunks)


def _render_committed_podcast(
    repository_root: Path,
    settings: Settings,
    *,
    daily_cycle_id: str,
    script_commit: str,
    script_path: str,
    output_directory: Path,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Render exact committed transcript bytes only beneath a runner-owned temp directory."""

    if not RUN_ID.fullmatch(daily_cycle_id) or not COMMIT_SHA.fullmatch(script_commit):
        raise PodcastError("ephemeral podcast render identity is invalid")
    expected_stamp = daily_cycle_id.removeprefix("daily-")
    if script_path != f"data/wiki/podcasts/daily-podcast_{expected_stamp}.md":
        raise PodcastError("podcast page path is not bound to the timestamped cycle")
    output_root = output_directory.resolve()
    try:
        output_root.relative_to(repository_root.resolve())
    except ValueError:
        pass
    else:
        raise PodcastError("ephemeral podcast output must remain outside the checkout")
    shown = runner(
        ["git", "show", f"{script_commit}:{script_path}"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if shown.returncode != 0:
        raise PodcastError("cannot read the exact committed podcast transcript")
    raw_markdown = shown.stdout
    if isinstance(raw_markdown, str):
        markdown_bytes = raw_markdown.encode("utf-8")
    else:
        markdown_bytes = bytes(raw_markdown)
    try:
        markdown = markdown_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PodcastError("committed podcast transcript is not UTF-8") from exc
    if daily_cycle_id not in markdown:
        raise PodcastError("committed podcast transcript lacks its daily cycle ID")
    transcript = _spoken_transcript(markdown)
    words = re.findall(r"\b[\w'-]+\b", transcript)
    word_count = len(words)
    if not MINIMUM_SCRIPT_WORDS <= word_count <= MAXIMUM_SCRIPT_WORDS:
        raise PodcastError(
            f"spoken transcript must contain {MINIMUM_SCRIPT_WORDS}-{MAXIMUM_SCRIPT_WORDS} words"
        )
    chunks = _transcript_chunks(transcript, settings.podcast.chunk_character_limit)
    output_root.mkdir(parents=True, exist_ok=True)
    if output_root.is_symlink():
        raise PodcastError("ephemeral podcast directory must not be a symlink")
    if any(output_root.iterdir()):
        raise PodcastError("ephemeral podcast directory must start empty")
    chunk_paths: list[Path] = []
    for index, text in enumerate(chunks, start=1):
        path = output_root / f"chunk-{index:02d}.mp3"
        command = [
            *settings.podcast.tts_command,
            "--voice",
            settings.podcast.voice,
            "--text",
            text,
            "--write-media",
            str(path),
        ]
        rendered = runner(command, check=False, capture_output=True)
        if rendered.returncode != 0 or not path.is_file() or path.stat().st_size == 0:
            raise PodcastError(f"configured TTS backend failed for chunk {index}")
        chunk_paths.append(path)
    concat = output_root / "concat.txt"
    concat.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in chunk_paths), encoding="utf-8"
    )
    audio = output_root / f"{daily_cycle_id}.mp3"
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    ffprobe = shutil.which("ffprobe") or "ffprobe"
    assembled = runner(
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
            str(audio),
        ],
        check=False,
        capture_output=True,
    )
    if assembled.returncode != 0 or not audio.is_file() or audio.stat().st_size == 0:
        raise PodcastError("ffmpeg could not assemble the ephemeral podcast")
    probe = runner(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio),
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
        or not settings.podcast.minimum_duration_seconds
        <= duration
        <= settings.podcast.maximum_duration_seconds
    ):
        raise PodcastError("ephemeral podcast duration is outside configured bounds")
    if audio.stat().st_size > settings.telegram.audio_maximum_bytes:
        raise PodcastError("ephemeral podcast exceeds the Telegram audio size limit")
    manifest_path = output_root / f"{daily_cycle_id}.audio-manifest.json"
    audio_manifest = {
        "audio_manifest_version": 1,
        "daily_cycle_id": daily_cycle_id,
        "script_commit": script_commit,
        "script_path": script_path,
        "script_sha256": content_hash(markdown_bytes),
        "spoken_transcript_sha256": content_hash(transcript),
        "audio_filename": audio.name,
        "audio_size": audio.stat().st_size,
        "audio_sha256": content_hash(audio.read_bytes()),
        "duration_seconds": duration,
        "format": "mp3",
    }
    manifest_path.write_text(
        json.dumps(audio_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for path in (*chunk_paths, concat):
        path.unlink(missing_ok=True)
    return PodcastAssembly(
        daily_cycle_id=daily_cycle_id,
        script_commit=script_commit,
        script_path=script_path,
        audio_path=str(audio),
        manifest_path=str(manifest_path),
        word_count=word_count,
        duration_seconds=duration,
        sha256=str(audio_manifest["audio_sha256"]),
    )


def render_committed_podcast(
    repository_root: Path,
    settings: Settings,
    *,
    daily_cycle_id: str,
    script_commit: str,
    script_path: str,
    output_directory: Path,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Render ephemerally and remove every intermediate, including after failure."""

    completed = False
    initially_empty = not output_directory.exists() or (
        output_directory.is_dir()
        and not output_directory.is_symlink()
        and not any(output_directory.iterdir())
    )
    try:
        result = _render_committed_podcast(
            repository_root,
            settings,
            daily_cycle_id=daily_cycle_id,
            script_commit=script_commit,
            script_path=script_path,
            output_directory=output_directory,
            runner=runner,
        )
        completed = True
        return result
    finally:
        output_root = output_directory.resolve()
        try:
            output_root.relative_to(repository_root.resolve())
        except ValueError:
            outside_checkout = True
        else:
            outside_checkout = False
        if (
            initially_empty
            and outside_checkout
            and output_root.is_dir()
            and not output_root.is_symlink()
        ):
            for path in output_root.glob("chunk-*.mp3"):
                if path.is_file() and not path.is_symlink():
                    path.unlink(missing_ok=True)
            (output_root / "concat.txt").unlink(missing_ok=True)
            if not completed and RUN_ID.fullmatch(daily_cycle_id):
                (output_root / f"{daily_cycle_id}.mp3").unlink(missing_ok=True)
                (output_root / f"{daily_cycle_id}.audio-manifest.json").unlink(missing_ok=True)


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
        raw_page_path = str(manifest.get("podcast_page_path", ""))
        page = _repository_path(repository_root, raw_page_path, PODCAST_PAGE)
        if page.is_symlink() or not page.is_file():
            raise PodcastError("succeeded daily podcast lacks its committed text page")
        text = page.read_text(encoding="utf-8")
        spoken = _spoken_transcript(text)
        word_count = len(re.findall(r"\b[\w'-]+\b", spoken))
        if not MINIMUM_SCRIPT_WORDS <= word_count <= MAXIMUM_SCRIPT_WORDS:
            raise PodcastError("succeeded daily podcast has an invalid spoken word count")
        if run_id not in text or "paper trad" not in spoken.casefold():
            raise PodcastError("succeeded daily podcast lacks its cycle or paper-trading label")
        if re.search(r"(?i)\.(?:mp3|wav|m4a)(?:\b|[?#])", text):
            raise PodcastError("succeeded daily podcast contains a persistent audio link")
        report = repository_root / str(manifest.get("report_path", ""))
        if (
            report.is_symlink()
            or not report.is_file()
            or PurePosixPath(raw_page_path).stem not in report.read_text(encoding="utf-8")
        ):
            raise PodcastError("succeeded daily report lacks its transcript link")
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
    manifest["podcast_audio_path"] = ""
    if manifest.get("daily_run_version") == 2:
        manifest["podcast_text_at"] = format_timestamp(instant)
        manifest["completion_at"] = format_timestamp(instant)
        manifest["status"] = (
            "degraded"
            if status != "succeeded" or manifest.get("finalization_status") == "degraded"
            else "succeeded"
        )
    atomic_write_json(path, manifest, allowed_root=repository_root)
    append_event(
        repository_root,
        event_type="daily_podcast_completed",
        message=f"Daily podcast finished with status {status}.",
        run_id=run_id,
        operation_id=operation_id,
        data={"transcript_path": manifest.get("podcast_page_path", "")},
        occurred_at=instant,
    )
    return status


__all__ = [
    "PodcastAssembly",
    "PodcastEnqueueResult",
    "PodcastError",
    "assemble_podcast",
    "build_podcast_context",
    "enqueue_daily_podcast",
    "finalize_daily_podcast",
    "render_committed_podcast",
]

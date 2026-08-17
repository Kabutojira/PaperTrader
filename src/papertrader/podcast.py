"""Deterministic context, assembly, and audit boundaries for the daily podcast."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, cast

import yaml

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.issues import record_issue
from papertrader.logs import append_event
from papertrader.public_markdown import visible_machine_ids
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
PODCAST_OUTPUT_ENV = "PAPERTRADER_PODCAST_OUTPUT_DIRECTORY"
RESEARCH_OPERATION_TYPES = frozenset(
    {
        "wiki_ingest",
        "opportunity_research",
        "quick_check_research",
        "idea_research",
        "security_research",
        "relationship_research",
        "strategy_research",
    }
)
BACKGROUND_WIKI_DOMAINS = frozenset({"ideas", "securities", "concepts"})
RESEARCH_WIKI_DOMAINS = frozenset(
    {"ideas", "securities", "concepts", "relationships", "strategies", "comparisons"}
)
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\n]*?)?\]\]")


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


def _manifest_cutoff(manifest: Mapping[str, object]) -> datetime | None:
    raw = str(manifest.get("research_cutoff_at") or manifest.get("completed_at") or "").strip()
    return parse_timestamp(raw) if raw else None


def _regular_bytes(repository_root: Path, raw_path: str, *, label: str) -> bytes:
    relative = PurePosixPath(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise PodcastError(f"{label} has an invalid repository path")
    path = repository_root.joinpath(*relative.parts)
    current = repository_root.resolve()
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise PodcastError(f"{label} must not traverse a symlink: {raw_path}")
    try:
        path.resolve(strict=True).relative_to(repository_root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise PodcastError(f"{label} resolves outside the repository: {raw_path}") from exc
    if not path.is_file():
        raise PodcastError(f"{label} is not a committed regular file: {raw_path}")
    return path.read_bytes()


def _successful_prior_podcast(
    repository_root: Path,
    *,
    current_run_id: str,
    current_cutoff: datetime,
) -> dict[str, object] | None:
    """Select one unambiguous earlier successful transcript and its frozen cutoff."""

    candidates: list[dict[str, object]] = []
    claimed_pages: dict[str, str] = {}
    runs_root = repository_root / "data" / "runs"
    for manifest_path in sorted(runs_root.glob("*/daily_run.json")):
        if manifest_path.is_symlink() or not manifest_path.is_file():
            continue
        manifest = _load_object(manifest_path)
        run_id = manifest.get("daily_cycle_id") or manifest.get("run_id")
        if not isinstance(run_id, str) or run_id == current_run_id:
            continue
        if manifest.get("podcast_status") != "succeeded":
            continue
        cutoff = _manifest_cutoff(manifest)
        if cutoff is None or cutoff >= current_cutoff:
            continue
        page_path = manifest.get("podcast_page_path")
        if not isinstance(page_path, str) or not PODCAST_PAGE.fullmatch(page_path):
            raise PodcastError(f"successful prior podcast has an invalid page identity: {run_id}")
        other = claimed_pages.setdefault(page_path, run_id)
        if other != run_id:
            raise PodcastError("conflicting prior-podcast page identities")
        page_bytes = _regular_bytes(
            repository_root, page_path, label="successful prior podcast transcript"
        )
        try:
            page_text = page_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PodcastError("successful prior podcast transcript is not UTF-8") from exc
        if _podcast_cycle_id(page_text) != run_id:
            raise PodcastError("successful prior podcast transcript conflicts with its cycle")
        context_path = f"data/runs/{run_id}/podcast_context.json"
        prior_context = _load_object(repository_root / context_path)
        context_cutoff = parse_timestamp(str(prior_context.get("research_cutoff_at", "")))
        if (
            prior_context.get("daily_cycle_id", prior_context.get("run_id")) != run_id
            or context_cutoff != cutoff
            or prior_context.get("page_path") != page_path
        ):
            raise PodcastError("successful prior podcast context has conflicting identities")
        candidates.append(
            {
                "daily_cycle_id": run_id,
                "research_cutoff_at": format_timestamp(cutoff),
                "page_path": page_path,
                "page_sha256": content_hash(page_bytes),
                "context_path": context_path,
                "context_sha256": content_hash((repository_root / context_path).read_bytes()),
                "_cutoff": cutoff,
            }
        )
    if not candidates:
        return None
    latest_cutoff = max(cast(datetime, item["_cutoff"]) for item in candidates)
    latest = [item for item in candidates if cast(datetime, item["_cutoff"]) == latest_cutoff]
    if len(latest) != 1:
        raise PodcastError("conflicting prior-podcast cutoff identities")
    selected = dict(latest[0])
    selected.pop("_cutoff", None)
    return selected


def _operation_result_item(
    repository_root: Path,
    run_id: str,
    operation_id: str,
    accepted_item: Mapping[str, object],
    *,
    window_start: datetime,
    cutoff: datetime,
) -> dict[str, object] | None:
    queue_matches = [
        row
        for table in ("operations_history", "operations_todo")
        for row in read_table(repository_root, table)
        if row["operation_id"] == operation_id
    ]
    if not queue_matches:
        raise PodcastError(f"accepted research is missing from queue state: {operation_id}")
    if len(queue_matches) > 1:
        raise PodcastError(f"accepted research has conflicting queue identities: {operation_id}")
    row = queue_matches[0]
    if row["operation_type"] not in RESEARCH_OPERATION_TYPES:
        return None

    artifact_root = repository_root / "data" / "runs" / run_id / operation_id
    attempt_history_path = artifact_root / "operation_history.json"
    row_belongs_to_attempt = row["claimed_by_run_id"] == run_id
    if attempt_history_path.is_file() and not attempt_history_path.is_symlink():
        attempt_history = _load_object(attempt_history_path)
        if (
            attempt_history.get("operation_history_version") != 1
            or attempt_history.get("daily_cycle_id") != run_id
            or attempt_history.get("operation_id") != operation_id
            or attempt_history.get("operation_type") != row["operation_type"]
            or attempt_history.get("cycle_disposition") != accepted_item.get("terminal_status")
        ):
            raise PodcastError(
                f"accepted research attempt has conflicting provenance: {operation_id}"
            )
    elif not row_belongs_to_attempt:
        raise PodcastError(f"accepted research is missing run provenance: {operation_id}")

    result_path = f"data/runs/{run_id}/{operation_id}/agent_result.json"
    result_file = repository_root / result_path
    validation: dict[str, object] = {}
    if result_file.is_file() and not result_file.is_symlink():
        result = _load_object(result_file)
    else:
        validation_file = result_file.with_name("validation_report.json")
        validation = _load_object(validation_file)
        result_path = validation_file.relative_to(repository_root).as_posix()
        raw_errors = validation.get("errors", [])
        failure_errors = raw_errors if isinstance(raw_errors, list) else []
        result = {
            "summary": (row.get("last_error", "") if row_belongs_to_attempt else "")
            or (row.get("terminal_reason", "") if row_belongs_to_attempt else "")
            or "The accepted research did not produce a valid result.",
            "evidence": [
                {"source": result_path, "claim": str(error)}
                for error in failure_errors
                if isinstance(error, str)
            ],
            "daily_report_items": [],
            "files_changed": [],
        }
    run_artifact = _load_object(result_file.with_name("hermes_run.json"))
    completed_at = (row.get("completed_at", "") if row_belongs_to_attempt else "") or str(
        run_artifact.get("completed_at", "")
    )
    completed = parse_timestamp(completed_at)
    if completed is None or not window_start < completed <= cutoff:
        raise PodcastError(
            f"accepted research result falls outside the frozen window: {operation_id}"
        )
    status = str(accepted_item.get("terminal_status", "")) or row.get("terminal_status", "")
    if status == "skipped":
        return None
    evidence = result.get("evidence", [])
    report_items = result.get("daily_report_items", [])
    changed = result.get("files_changed", [])
    return {
        "daily_cycle_id": run_id,
        "operation_id": operation_id,
        "operation_type": row["operation_type"],
        "entity_type": row["entity_type"],
        "entity_id": row["entity_id"],
        "status": status,
        "summary": (
            (row.get("result_summary", "") if row_belongs_to_attempt else "")
            or str(result.get("summary", ""))
        ),
        "evidence": evidence if isinstance(evidence, list) else [],
        "daily_report_items": report_items if isinstance(report_items, list) else [],
        "files_changed": changed if isinstance(changed, list) else [],
        "result_path": result_path,
        "completed_at": completed_at,
        "failure_errors": validation.get("errors", []),
    }


def _window_research(
    repository_root: Path,
    *,
    current_run_id: str,
    window_start: datetime,
    cutoff: datetime,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str]]:
    developments: list[dict[str, object]] = []
    gaps: list[dict[str, object]] = []
    cycle_ids: list[str] = []
    history_by_run: dict[str, list[Mapping[str, str]]] = {}
    for row in read_table(repository_root, "operations_history"):
        history_by_run.setdefault(row["claimed_by_run_id"], []).append(row)
    for manifest_path in sorted((repository_root / "data" / "runs").glob("*/daily_run.json")):
        if manifest_path.is_symlink() or not manifest_path.is_file():
            continue
        manifest = _load_object(manifest_path)
        run_id = manifest.get("daily_cycle_id") or manifest.get("run_id")
        cycle_cutoff = _manifest_cutoff(manifest)
        if (
            not isinstance(run_id, str)
            or cycle_cutoff is None
            or not window_start < cycle_cutoff <= cutoff
        ):
            continue
        if run_id == current_run_id and cycle_cutoff != cutoff:
            raise PodcastError("current podcast cycle cutoff conflicts with its manifest")
        raw_accepted = manifest.get("operations_accepted")
        if raw_accepted is None:
            accepted_values: list[Mapping[str, object]] = [
                {"operation_id": row["operation_id"], "terminal_status": row["terminal_status"]}
                for row in history_by_run.get(run_id, [])
            ]
        elif isinstance(raw_accepted, list) and all(
            isinstance(item, dict) for item in raw_accepted
        ):
            accepted_values = [item for item in raw_accepted if isinstance(item, dict)]
        else:
            raise PodcastError(f"daily cycle accepted-operation accounting is invalid: {run_id}")
        cycle_ids.append(run_id)
        for accepted in accepted_values:
            operation_id = accepted.get("operation_id")
            if not isinstance(operation_id, str) or not ULID.fullmatch(operation_id):
                raise PodcastError(f"daily cycle contains an invalid accepted operation: {run_id}")
            item = _operation_result_item(
                repository_root,
                run_id,
                operation_id,
                accepted,
                window_start=window_start,
                cutoff=cycle_cutoff,
            )
            if item is None:
                continue
            if item["status"] == "succeeded":
                developments.append(item)
            elif item["status"] in {"failed", "blocked"}:
                gaps.append(item)

    def order(item: Mapping[str, object]) -> tuple[str, str]:
        return str(item["completed_at"]), str(item["operation_id"])

    developments.sort(key=order)
    gaps.sort(key=order)
    return developments, gaps, cycle_ids


def _wiki_context_pages(
    repository_root: Path,
    developments: list[dict[str, object]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    changed_paths: set[str] = set()
    evidence_paths: set[str] = set()
    for item in developments:
        raw_changed = item.get("files_changed", [])
        for raw in raw_changed if isinstance(raw_changed, list) else []:
            if isinstance(raw, str) and raw.startswith("data/wiki/") and raw.endswith(".md"):
                _regular_bytes(repository_root, raw, label="accepted changed wiki page")
                parts = PurePosixPath(raw).parts
                if len(parts) >= 4 and parts[2] in RESEARCH_WIKI_DOMAINS:
                    changed_paths.add(raw)
        raw_evidence = item.get("evidence", [])
        for evidence in raw_evidence if isinstance(raw_evidence, list) else []:
            if not isinstance(evidence, dict):
                continue
            raw = evidence.get("source")
            if isinstance(raw, str) and raw.startswith("data/wiki/") and raw.endswith(".md"):
                parts = PurePosixPath(raw).parts
                if len(parts) >= 4 and parts[2] in BACKGROUND_WIKI_DOMAINS:
                    evidence_paths.add(raw)
    linked_paths: set[str] = set(evidence_paths)
    for raw in sorted(changed_paths):
        text = _regular_bytes(repository_root, raw, label="accepted changed wiki page").decode(
            "utf-8"
        )
        for match in WIKI_LINK.finditer(text):
            target = match.group(1).strip().removesuffix(".md")
            relative = PurePosixPath(target)
            if relative.is_absolute() or ".." in relative.parts:
                continue
            if relative.parts and relative.parts[0] in BACKGROUND_WIKI_DOMAINS:
                linked_paths.add(f"data/wiki/{target}.md")
    linked_paths.difference_update(changed_paths)

    def identities(paths: set[str], label: str) -> list[dict[str, str]]:
        return [
            {"path": raw, "sha256": content_hash(_regular_bytes(repository_root, raw, label=label))}
            for raw in sorted(paths)
        ]

    return identities(changed_paths, "changed wiki page"), identities(
        linked_paths, "linked background wiki page"
    )


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
    prior_podcast = _successful_prior_podcast(
        repository_root,
        current_run_id=run_id,
        current_cutoff=report_date,
    )
    if prior_podcast is None:
        window_start = report_date - timedelta(days=7)
        window_mode = "seven_day_bootstrap"
    else:
        prior_cutoff = parse_timestamp(str(prior_podcast["research_cutoff_at"]))
        if prior_cutoff is None:
            raise PodcastError("prior podcast lacks a canonical research cutoff")
        window_start = prior_cutoff
        window_mode = "since_previous_successful_podcast"
    developments, gaps, intervening_cycles = _window_research(
        repository_root,
        current_run_id=run_id,
        window_start=window_start,
        cutoff=report_date,
    )
    changed_pages, background_pages = _wiki_context_pages(repository_root, developments)
    context = {
        "podcast_context_version": 3,
        "run_id": run_id,
        "daily_cycle_id": run_id,
        "generated_at": format_timestamp(instant),
        "window_mode": window_mode,
        "window_start_exclusive": format_timestamp(window_start),
        "research_cutoff_at": format_timestamp(report_date),
        "previous_successful_podcast": prior_podcast,
        "intervening_daily_cycles": intervening_cycles,
        "report_path": report_path,
        "report_sha256": content_hash(
            _regular_bytes(repository_root, report_path, label="current daily report")
        ),
        "decision_snapshot_path": f"data/runs/{run_id}/decision_snapshot.json",
        "decision_snapshot_sha256": content_hash(
            _regular_bytes(
                repository_root,
                f"data/runs/{run_id}/decision_snapshot.json",
                label="current decision snapshot",
            )
        ),
        "wiki_orientation_paths": [
            "data/wiki/SCHEMA.md",
            "data/wiki/index.md",
            "data/wiki/research-catalog.md",
            "data/wiki/log.md",
        ],
        "research_developments": developments,
        "unresolved_research_gaps": gaps,
        "changed_wiki_pages": changed_pages,
        "background_wiki_pages": background_pages,
        "portfolio_implication_paths": [
            f"data/runs/{run_id}/decision_snapshot.json",
            report_path,
        ],
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
        dedupe_key=f"daily_podcast:{run_id}:research-v3",
        prompt=(
            f"Create the {stamp} research-first PaperTrader podcast from all accepted research "
            "since the previous successful episode, using linked maintained wiki knowledge to "
            "tell one accessible twenty-minute story, then render its ephemeral audio draft once."
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


def spoken_transcript(markdown: str) -> str:
    """Extract only the bounded spoken prose for deterministic delivery."""

    return _spoken_transcript(markdown)


def _podcast_metadata(markdown: str) -> Mapping[str, object]:
    if not markdown.startswith("---\n") or "\n---\n" not in markdown[4:]:
        raise PodcastError("podcast page lacks frontmatter identity")
    raw, _ = markdown[4:].split("\n---\n", maxsplit=1)
    try:
        metadata = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise PodcastError("podcast page has invalid frontmatter") from exc
    if not isinstance(metadata, dict):
        raise PodcastError("podcast page frontmatter must be an object")
    return metadata


def _podcast_cycle_id(markdown: str) -> str:
    """Read immutable podcast cycle identity from YAML frontmatter only."""

    metadata = _podcast_metadata(markdown)
    cycle_id = metadata.get("daily_cycle_id")
    if not isinstance(cycle_id, str) or not RUN_ID.fullmatch(cycle_id):
        raise PodcastError("podcast page lacks a valid frontmatter cycle identity")
    return cycle_id


def validate_podcast_script(markdown: str, *, daily_cycle_id: str) -> tuple[str, int]:
    """Validate accessible prose and metadata without rewriting generated narration."""

    metadata = _podcast_metadata(markdown)
    if metadata.get("daily_cycle_id") != daily_cycle_id:
        raise PodcastError("podcast transcript frontmatter has the wrong cycle ID")
    if metadata.get("paper_trading") is not True:
        raise PodcastError("podcast transcript must retain paper_trading: true in frontmatter")
    transcript = _spoken_transcript(markdown)
    words = re.findall(r"\b[\w'-]+\b", transcript)
    if not MINIMUM_SCRIPT_WORDS <= len(words) <= MAXIMUM_SCRIPT_WORDS:
        raise PodcastError(
            f"spoken transcript must contain {MINIMUM_SCRIPT_WORDS}-{MAXIMUM_SCRIPT_WORDS} words"
        )
    if any(character.isdigit() for character in transcript):
        raise PodcastError("spoken transcript must spell out quantities without numeric glyphs")
    if re.search(r"(?m)^\s*(?:[-+*]\s+|#{1,6}\s+|>\s+|```|~~~)", transcript):
        raise PodcastError("spoken transcript must be narrative prose without Markdown lists")
    if "|" in transcript or re.search(r"(?m)^\s*:?-{3,}:?\s*$", transcript):
        raise PodcastError("spoken transcript must not contain Markdown table formatting")
    if re.search(r"(?i)\b(?:https?://|www\.)", transcript):
        raise PodcastError("spoken transcript must not contain raw URLs")
    if "[[" in transcript or re.search(r"\[[^\]\n]+\]\([^\n)]+\)", transcript):
        raise PodcastError("spoken transcript must not contain visible link markup")
    disclosure = re.compile(
        r"(?i)(?:paper[ -]trad|live trad|not (?:investment|financial) advice|"
        r"does not constitute (?:investment|financial) advice|brokerage service|"
        r"instruction to buy or sell)"
    )
    if disclosure.search(transcript):
        raise PodcastError("spoken transcript must not contain advice or trading disclaimers")
    _, visible_body = markdown[4:].split("\n---\n", maxsplit=1)
    visible_without_spoken = re.sub(
        re.escape(TRANSCRIPT_START) + r".*?" + re.escape(TRANSCRIPT_END),
        "",
        visible_body,
        flags=re.DOTALL,
    )
    if disclosure.search(visible_without_spoken):
        raise PodcastError("podcast page must keep paper-trading identity in metadata only")
    paragraphs = [value.strip() for value in re.split(r"\n\s*\n", transcript) if value.strip()]
    if len(paragraphs) < 8:
        raise PodcastError("spoken transcript must contain at least eight narrative paragraphs")
    if visible_machine_ids(markdown):
        raise PodcastError("podcast transcript exposes a machine identity")
    return transcript, len(words)


def assemble_podcast(
    repository_root: Path,
    request: Mapping[str, object],
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Reject the superseded repository-writing media assembly boundary."""

    del repository_root, request, runner
    raise PodcastError(
        "repository podcast assembly is disabled; daily_podcast must render one ephemeral draft"
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


def _output_root(repository_root: Path, output_directory: Path, daily_cycle_id: str) -> Path:
    if not RUN_ID.fullmatch(daily_cycle_id):
        raise PodcastError("ephemeral podcast cycle identity is invalid")
    if not output_directory.is_absolute():
        raise PodcastError("ephemeral podcast output directory must be absolute")
    if output_directory.is_symlink():
        raise PodcastError("ephemeral podcast output directory must not be a symlink")
    output_root = output_directory.resolve()
    try:
        output_root.relative_to(repository_root.resolve())
    except ValueError:
        pass
    else:
        raise PodcastError("ephemeral podcast output must remain outside the checkout")
    if output_root.name != daily_cycle_id or output_root.parent.name != "papertrader-podcast":
        raise PodcastError("ephemeral podcast output is not the controller-approved cycle path")
    return output_root


def _probe_audio(
    audio: Path,
    settings: Settings,
    *,
    runner: Callable[..., Any],
) -> int:
    ffprobe = shutil.which("ffprobe") or "ffprobe"
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
    return duration


def _render_draft_podcast(
    repository_root: Path,
    settings: Settings,
    *,
    daily_cycle_id: str,
    script_path: str,
    output_directory: Path,
    audit_run_id: str,
    audit_operation_id: str,
    audit_operation_type: str,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Render the workspace draft once inside an audited daily_podcast operation."""

    if (
        audit_operation_type != "daily_podcast"
        or audit_run_id != daily_cycle_id
        or not ULID.fullmatch(audit_operation_id)
    ):
        raise PodcastError("podcast draft rendering requires an audited daily_podcast operation")
    expected_stamp = daily_cycle_id.removeprefix("daily-")
    if script_path != f"data/wiki/podcasts/daily-podcast_{expected_stamp}.md":
        raise PodcastError("podcast page path is not bound to the timestamped cycle")
    output_root = _output_root(repository_root, output_directory, daily_cycle_id)
    markdown_bytes = _regular_bytes(repository_root, script_path, label="podcast draft transcript")
    try:
        markdown = markdown_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PodcastError("podcast draft transcript is not UTF-8") from exc
    transcript, word_count = validate_podcast_script(markdown, daily_cycle_id=daily_cycle_id)
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
    duration = _probe_audio(audio, settings, runner=runner)
    manifest_path = output_root / f"{daily_cycle_id}.draft-manifest.json"
    audio_manifest = {
        "podcast_draft_manifest_version": 1,
        "daily_cycle_id": daily_cycle_id,
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
        script_commit="",
        script_path=script_path,
        audio_path=str(audio),
        manifest_path=str(manifest_path),
        word_count=word_count,
        duration_seconds=duration,
        sha256=str(audio_manifest["audio_sha256"]),
    )


def render_draft_podcast(
    repository_root: Path,
    settings: Settings,
    *,
    daily_cycle_id: str,
    script_path: str,
    output_directory: Path,
    audit_run_id: str,
    audit_operation_id: str,
    audit_operation_type: str,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Render one audited draft and remove every partial media file after failure."""

    completed = False
    initially_empty = not output_directory.exists() or (
        output_directory.is_dir()
        and not output_directory.is_symlink()
        and not any(output_directory.iterdir())
    )
    try:
        result = _render_draft_podcast(
            repository_root,
            settings,
            daily_cycle_id=daily_cycle_id,
            script_path=script_path,
            output_directory=output_directory,
            audit_run_id=audit_run_id,
            audit_operation_id=audit_operation_id,
            audit_operation_type=audit_operation_type,
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
                (output_root / f"{daily_cycle_id}.draft-manifest.json").unlink(missing_ok=True)


def seal_podcast_render(
    repository_root: Path,
    settings: Settings,
    *,
    daily_cycle_id: str,
    script_commit: str,
    script_path: str,
    output_directory: Path,
    runner: Callable[..., Any] = subprocess.run,
) -> PodcastAssembly:
    """Bind existing draft media to exact committed script bytes without synthesizing again."""

    if not COMMIT_SHA.fullmatch(script_commit):
        raise PodcastError("podcast render seal requires a canonical script commit")
    expected_stamp = daily_cycle_id.removeprefix("daily-")
    if script_path != f"data/wiki/podcasts/daily-podcast_{expected_stamp}.md":
        raise PodcastError("podcast page path is not bound to the timestamped cycle")
    output_root = _output_root(repository_root, output_directory, daily_cycle_id)
    draft_path = output_root / f"{daily_cycle_id}.draft-manifest.json"
    draft = _load_object(draft_path)
    audio = output_root / f"{daily_cycle_id}.mp3"
    if (
        draft.get("podcast_draft_manifest_version") != 1
        or draft.get("daily_cycle_id") != daily_cycle_id
        or draft.get("script_path") != script_path
        or draft.get("audio_filename") != audio.name
    ):
        raise PodcastError("podcast draft manifest identity is invalid")
    shown = runner(
        ["git", "show", f"{script_commit}:{script_path}"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if shown.returncode != 0:
        raise PodcastError("cannot read the exact committed podcast transcript")
    markdown_bytes = (
        shown.stdout.encode("utf-8") if isinstance(shown.stdout, str) else bytes(shown.stdout)
    )
    try:
        markdown = markdown_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PodcastError("committed podcast transcript is not UTF-8") from exc
    transcript, word_count = validate_podcast_script(markdown, daily_cycle_id=daily_cycle_id)
    if draft.get("script_sha256") != content_hash(markdown_bytes) or draft.get(
        "spoken_transcript_sha256"
    ) != content_hash(transcript):
        raise PodcastError("podcast draft is not bound to the exact committed transcript")
    if audio.is_symlink() or not audio.is_file() or audio.stat().st_size == 0:
        raise PodcastError("ephemeral podcast audio is missing or invalid")
    audio_sha = content_hash(audio.read_bytes())
    if draft.get("audio_size") != audio.stat().st_size or draft.get("audio_sha256") != audio_sha:
        raise PodcastError("ephemeral podcast audio differs from its draft manifest")
    duration = _probe_audio(audio, settings, runner=runner)
    if draft.get("duration_seconds") != duration:
        raise PodcastError("ephemeral podcast duration differs from its draft manifest")
    manifest_path = output_root / f"{daily_cycle_id}.sealed-manifest.json"
    sealed = {
        "audio_manifest_version": 2,
        "daily_cycle_id": daily_cycle_id,
        "script_commit": script_commit,
        "script_path": script_path,
        "script_sha256": content_hash(markdown_bytes),
        "spoken_transcript_sha256": content_hash(transcript),
        "audio_filename": audio.name,
        "audio_size": audio.stat().st_size,
        "audio_sha256": audio_sha,
        "duration_seconds": duration,
        "format": "mp3",
    }
    manifest_path.write_text(json.dumps(sealed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    draft_path.unlink()
    return PodcastAssembly(
        daily_cycle_id=daily_cycle_id,
        script_commit=script_commit,
        script_path=script_path,
        audio_path=str(audio),
        manifest_path=str(manifest_path),
        word_count=word_count,
        duration_seconds=duration,
        sha256=audio_sha,
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
        raw_page_path = str(manifest.get("podcast_page_path", ""))
        page = _repository_path(repository_root, raw_page_path, PODCAST_PAGE)
        if page.is_symlink() or not page.is_file():
            raise PodcastError("succeeded daily podcast lacks its committed text page")
        text = page.read_text(encoding="utf-8")
        validate_podcast_script(text, daily_cycle_id=run_id)
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
    "render_draft_podcast",
    "seal_podcast_render",
    "spoken_transcript",
    "validate_podcast_script",
]

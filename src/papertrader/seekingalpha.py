"""Search-index-only Seeking Alpha lead scheduling and exact-once queueing."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import UTC, datetime, time, timedelta
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.queue import Operation, enqueue_operation
from papertrader.tables import read_table
from papertrader.utils import (
    CanonicalValueError,
    content_hash,
    ensure_utc,
    format_timestamp,
    parse_iso_date,
    utc_now,
)

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
ARTICLE_ID = re.compile(r"^[1-9][0-9]*$")
ARTICLE_PATH = re.compile(
    r"^/(?P<section>article|news)/(?P<article_id>[1-9][0-9]*)"
    r"(?P<slug>-[a-z0-9]+(?:-[a-z0-9]+)*)?/?$"
)
CONTENT_SECTIONS = {"analysis": "article", "news": "news"}
ANALYSIS_PAGE_URL = "https://seekingalpha.com/trending-analysis"
NEWS_PAGE_URL = "https://seekingalpha.com/market-news/trending"


class SeekingAlphaError(CanonicalValueError):
    """Raised when a search-index discovery contract is unsafe or inconsistent."""


def canonical_article_url(raw_url: str) -> tuple[str, str, str]:
    """Validate and normalize one canonical analysis/news URL without fetching it."""

    parsed = urlsplit(raw_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in {"seekingalpha.com", "www.seekingalpha.com"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port is not None
        or parsed.query
        or parsed.fragment
    ):
        raise SeekingAlphaError(f"invalid Seeking Alpha canonical URL: {raw_url!r}")
    match = ARTICLE_PATH.fullmatch(parsed.path)
    if match is None:
        raise SeekingAlphaError(f"invalid Seeking Alpha article path: {parsed.path!r}")
    section = match.group("section")
    content_kind = "analysis" if section == "article" else "news"
    article_id = match.group("article_id")
    slug = match.group("slug") or ""
    return content_kind, article_id, f"https://seekingalpha.com/{section}/{article_id}{slug}"


def seekingalpha_source_id(content_kind: str, article_id: str) -> str:
    """Return the immutable source identity for one indexed article URL."""

    if content_kind not in CONTENT_SECTIONS or ARTICLE_ID.fullmatch(article_id) is None:
        raise SeekingAlphaError("invalid Seeking Alpha source identity")
    return f"seekingalpha_{content_kind}_{article_id}"


def seekingalpha_dedupe_key(content_kind: str, article_id: str) -> str:
    """Return the once-ever article-review queue key."""

    seekingalpha_source_id(content_kind, article_id)
    return f"wiki_ingest:seekingalpha:{content_kind}:{article_id}:v1"


def seekingalpha_discovery_dedupe_key(discovery_date: str) -> str:
    """Return the once-per-UTC-day discovery-operation key."""

    parse_iso_date(discovery_date)
    return f"source_discovery:seekingalpha:{discovery_date}:v1"


def _known_operation(repository_root: Path, dedupe_key: str) -> str:
    for table in ("operations_todo", "operations_history"):
        for row in read_table(repository_root, table):
            if row["dedupe_key"] == dedupe_key:
                return row["operation_id"]
    return ""


def _schedule_document(
    *,
    run_id: str,
    instant: datetime,
    status: str,
    reason: str,
    operation_id: str = "",
    operation_created: bool = False,
    deadline: datetime | None = None,
) -> dict[str, object]:
    return {
        "seekingalpha_schedule_version": 1,
        "run_id": run_id,
        "scheduled_at": format_timestamp(instant),
        "discovery_date": instant.date().isoformat(),
        "status": status,
        "reason": reason,
        "operation_id": operation_id,
        "operation_created": operation_created,
        "deadline": format_timestamp(deadline) if deadline else "",
    }


def _load_seekingalpha_schedule(repository_root: Path, run_id: str) -> Mapping[str, object]:
    """Load and validate one immutable Seeking Alpha schedule artifact."""

    artifact = repository_root / "data" / "runs" / run_id / "seekingalpha_schedule.json"
    if artifact.parent.is_symlink() or artifact.is_symlink() or not artifact.is_file():
        raise SeekingAlphaError("Seeking Alpha schedule artifact must be a regular file")
    try:
        value = json.loads(artifact.read_text(encoding="utf-8"))
        schema = json.loads(
            (repository_root / "schemas" / "seekingalpha_schedule.schema.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise SeekingAlphaError(f"cannot read Seeking Alpha schedule artifact: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        raise SeekingAlphaError(f"invalid Seeking Alpha schedule artifact: {errors[0].message}")
    if not isinstance(value, Mapping) or value.get("run_id") != run_id:
        raise SeekingAlphaError("Seeking Alpha schedule artifact identity mismatch")
    return value


def _skip_existing_seekingalpha_schedule(
    repository_root: Path, run_id: str
) -> Mapping[str, object] | None:
    """Return an idempotent skip result without replacing an existing schedule."""

    artifact = repository_root / "data" / "runs" / run_id / "seekingalpha_schedule.json"
    if not artifact.exists():
        return None
    schedule = _load_seekingalpha_schedule(repository_root, run_id)
    return {
        "seekingalpha_schedule_version": schedule["seekingalpha_schedule_version"],
        "run_id": run_id,
        "status": "skipped",
        "reason": "manifest_already_exists",
        "existing_manifest_status": schedule["status"],
        "manifest_path": artifact.relative_to(repository_root).as_posix(),
        "operation_id": schedule["operation_id"],
        "operation_created": False,
    }


def schedule_seekingalpha_discovery(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    dry_run: bool = False,
    now: datetime | None = None,
) -> Mapping[str, object]:
    """Schedule one expiring search-index discovery operation without network access."""

    if RUN_ID.fullmatch(run_id) is None:
        raise SeekingAlphaError(f"invalid Seeking Alpha schedule run_id: {run_id!r}")
    existing = _skip_existing_seekingalpha_schedule(repository_root, run_id)
    if existing is not None:
        return existing
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    artifact = repository_root / "data" / "runs" / run_id / "seekingalpha_schedule.json"
    if artifact.parent.is_symlink():
        raise SeekingAlphaError("Seeking Alpha schedule directory must not be a symlink")
    artifact.parent.mkdir(parents=True, exist_ok=True)

    if not settings.seekingalpha.enabled or dry_run:
        status = "disabled" if not settings.seekingalpha.enabled else "dry_run"
        document = _schedule_document(
            run_id=run_id,
            instant=instant,
            status=status,
            reason=status,
        )
        atomic_write_json(artifact, document, allowed_root=repository_root)
        return document

    discovery_date = instant.date().isoformat()
    dedupe_key = seekingalpha_discovery_dedupe_key(discovery_date)
    known_operation_id = _known_operation(repository_root, dedupe_key)
    deadline = datetime.combine(instant.date() + timedelta(days=1), time(), tzinfo=UTC)
    if known_operation_id:
        document = _schedule_document(
            run_id=run_id,
            instant=instant,
            status="duplicate",
            reason="daily_discovery_already_known",
            operation_id=known_operation_id,
            deadline=deadline,
        )
        atomic_write_json(artifact, document, allowed_root=repository_root)
        return document

    operation_id, created = enqueue_operation(
        repository_root,
        settings,
        operation_type="source_discovery",
        entity_type="source",
        entity_id="seekingalpha_trending_daily",
        dedupe_key=dedupe_key,
        prompt=(
            "Discover material Seeking Alpha analysis and entity-relevant news through "
            "search-index metadata only."
        ),
        inputs={
            "source_kind": "seekingalpha_search_index",
            "source_id": "seekingalpha_trending_daily",
            "discovery_date": discovery_date,
            "analysis_page_url": ANALYSIS_PAGE_URL,
            "news_page_url": NEWS_PAGE_URL,
            "analysis_candidate_limit": settings.seekingalpha.analysis_candidate_limit,
            "news_candidate_limit": settings.seekingalpha.news_candidate_limit,
            "lookback_days": settings.seekingalpha.lookback_days,
            "search_attempts": settings.seekingalpha.search_attempts,
            "maximum_leads": settings.seekingalpha.maximum_leads_per_day,
            "discovery_mode": "search_index",
            "direct_site_access_allowed": False,
        },
        source=f"seekingalpha_schedule:{run_id}",
        priority=settings.seekingalpha.discovery_priority,
        deadline=deadline,
        source_refs=(ANALYSIS_PAGE_URL, NEWS_PAGE_URL),
        now=instant,
    )
    document = _schedule_document(
        run_id=run_id,
        instant=instant,
        status="queued" if created else "duplicate",
        reason="" if created else "daily_discovery_already_known",
        operation_id=operation_id,
        operation_created=created,
        deadline=deadline,
    )
    atomic_write_json(artifact, document, allowed_root=repository_root)
    return document


def _validate_discovery_document(repository_root: Path, document: Mapping[str, object]) -> None:
    try:
        schema = json.loads(
            (repository_root / "schemas" / "seekingalpha_discovery.schema.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise SeekingAlphaError(f"cannot load Seeking Alpha discovery schema: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors[:5])
        raise SeekingAlphaError(f"invalid Seeking Alpha discovery manifest: {details}")


def _active_discovery_operation(
    repository_root: Path, *, run_id: str, operation_id: str
) -> tuple[Operation, Mapping[str, object]]:
    matches = [
        Operation.from_row(row)
        for row in read_table(repository_root, "operations_todo")
        if row["operation_id"] == operation_id
    ]
    if len(matches) != 1:
        raise SeekingAlphaError("discovery manifest operation is not active")
    operation = matches[0]
    if (
        operation.operation_type != "source_discovery"
        or operation.status != "running"
        or operation.claimed_by_run_id != run_id
    ):
        raise SeekingAlphaError("discovery manifest operation is not the running source discovery")
    payload_path = repository_root.joinpath(*PurePosixPath(operation.payload_path).parts)
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SeekingAlphaError(f"cannot read discovery operation payload: {exc}") from exc
    inputs = payload.get("inputs") if isinstance(payload, dict) else None
    if not isinstance(inputs, dict) or inputs.get("source_kind") != "seekingalpha_search_index":
        raise SeekingAlphaError("operation is not Seeking Alpha search-index discovery")
    return operation, inputs


def _known_article_keys(repository_root: Path) -> set[str]:
    return {
        row["dedupe_key"]
        for table in ("operations_todo", "operations_history")
        for row in read_table(repository_root, table)
    }


def _registered_sources(repository_root: Path) -> dict[str, Mapping[str, str]]:
    return {row["source_id"]: row for row in read_table(repository_root, "source_registry")}


def _known_entity_ids(repository_root: Path) -> set[str]:
    security_ids = {row["security_id"] for row in read_table(repository_root, "securities")}
    ideas_directory = repository_root / "data" / "wiki" / "ideas"
    idea_ids = {
        path.stem
        for path in ideas_directory.glob("*.md")
        if path.is_file() and not path.is_symlink()
    }
    return security_ids | idea_ids


def _normalized_line(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise SeekingAlphaError(f"{label} must be a string")
    normalized = " ".join(value.split())
    if not normalized or normalized != value:
        raise SeekingAlphaError(f"{label} must be a non-empty normalized single line")
    return normalized


def _integer_value(values: Mapping[str, object], key: str) -> int:
    value = values.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise SeekingAlphaError(f"{key} must be an integer")
    return value


def enqueue_seekingalpha_leads(
    repository_root: Path,
    settings: Settings,
    document: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> Mapping[str, object]:
    """Validate an agent discovery artifact and queue each selected article at most once."""

    _validate_discovery_document(repository_root, document)
    if document["status"] != "succeeded":
        raise SeekingAlphaError("unavailable discovery manifests cannot enqueue leads")
    run_id = str(document["run_id"])
    discovery_operation_id = str(document["operation_id"])
    _, source_inputs = _active_discovery_operation(
        repository_root,
        run_id=run_id,
        operation_id=discovery_operation_id,
    )
    if document["discovery_date"] != source_inputs.get("discovery_date"):
        raise SeekingAlphaError("discovery manifest date does not match its operation payload")
    selected = document["selected"]
    candidate_counts = document["candidate_counts"]
    assert isinstance(selected, list) and isinstance(candidate_counts, dict)
    if len(selected) > _integer_value(source_inputs, "maximum_leads"):
        raise SeekingAlphaError("discovery selected more leads than its operation allows")
    if _integer_value(candidate_counts, "analysis") > _integer_value(
        source_inputs, "analysis_candidate_limit"
    ):
        raise SeekingAlphaError("analysis candidate count exceeds its operation bound")
    if _integer_value(candidate_counts, "news") > _integer_value(
        source_inputs, "news_candidate_limit"
    ):
        raise SeekingAlphaError("news candidate count exceeds its operation bound")

    known_entities = _known_entity_ids(repository_root)
    known_keys = _known_article_keys(repository_root)
    registered = _registered_sources(repository_root)
    seen_source_ids: set[str] = set()
    duplicate_source_ids: list[str] = []
    operation_ids: list[str] = []
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)

    ordered = sorted(
        selected,
        key=lambda value: (
            int(value["rank"]),
            str(value["content_kind"]),
            str(value["article_id"]),
        ),
    )
    for raw in ordered:
        assert isinstance(raw, dict)
        content_kind = str(raw["content_kind"])
        article_id = str(raw["article_id"])
        parsed_kind, parsed_id, canonical_url = canonical_article_url(str(raw["canonical_url"]))
        if parsed_kind != content_kind or parsed_id != article_id:
            raise SeekingAlphaError("selected lead URL, kind, and article ID do not match")
        source_id = seekingalpha_source_id(content_kind, article_id)
        if source_id in seen_source_ids:
            raise SeekingAlphaError(f"discovery selected duplicate source: {source_id}")
        seen_source_ids.add(source_id)
        title = _normalized_line(raw["title"], f"{source_id}.title")
        lead_reason = _normalized_line(raw["lead_reason"], f"{source_id}.lead_reason")
        related = raw["related_entity_ids"]
        assert isinstance(related, list)
        related_ids = tuple(str(value) for value in related)
        unknown_entities = sorted(set(related_ids) - known_entities)
        if unknown_entities:
            raise SeekingAlphaError(
                f"selected lead references unknown entities: {unknown_entities}"
            )
        if content_kind == "news" and not related_ids:
            raise SeekingAlphaError("Seeking Alpha news leads require an existing related entity")
        rank = int(raw["rank"])
        candidate_limit = _integer_value(source_inputs, f"{content_kind}_candidate_limit")
        if rank > candidate_limit:
            raise SeekingAlphaError(f"{source_id} rank exceeds its candidate bound")
        dedupe_key = seekingalpha_dedupe_key(content_kind, article_id)
        existing_source = registered.get(source_id)
        if existing_source is not None:
            try:
                registered_kind, registered_id, _ = canonical_article_url(
                    existing_source["canonical_url"]
                )
            except SeekingAlphaError as exc:
                raise SeekingAlphaError(f"registered source URL conflicts for {source_id}") from exc
            if registered_kind != content_kind or registered_id != article_id:
                raise SeekingAlphaError(f"registered source identity conflicts for {source_id}")
        if dedupe_key in known_keys or existing_source is not None:
            duplicate_source_ids.append(source_id)
            continue
        author = " ".join(str(raw["author"]).split())
        published_at = str(raw["published_at"])
        summary_hash = str(raw["summary_hash"])
        metadata_hash = content_hash(
            {
                "article_id": article_id,
                "author": author,
                "canonical_url": canonical_url,
                "content_kind": content_kind,
                "published_at": published_at,
                "summary_hash": summary_hash,
                "title": title,
            }
        )
        operation_id, created = enqueue_operation(
            repository_root,
            settings,
            operation_type="wiki_ingest",
            entity_type="source",
            entity_id=source_id,
            dedupe_key=dedupe_key,
            prompt=("Research one Seeking Alpha search-index lead without fetching Seeking Alpha."),
            inputs={
                "source_kind": "seekingalpha_search_lead",
                "source_id": source_id,
                "content_kind": content_kind,
                "article_id": article_id,
                "title": title,
                "canonical_url": canonical_url,
                "author": author,
                "published_at": published_at,
                "discovered_at": str(document["discovered_at"]),
                "discovery_operation_id": discovery_operation_id,
                "discovery_date": str(document["discovery_date"]),
                "rank": rank,
                "summary_hash": summary_hash,
                "metadata_hash": metadata_hash,
                "related_entity_ids": list(related_ids),
                "lead_reason": lead_reason,
                "discovery_mode": "search_index",
                "direct_site_access_allowed": False,
            },
            source=f"seekingalpha_discovery:{discovery_operation_id}",
            priority=(
                settings.seekingalpha.analysis_priority
                if content_kind == "analysis"
                else settings.seekingalpha.news_priority
            ),
            depends_on=(discovery_operation_id,),
            source_refs=(canonical_url,),
            now=instant,
        )
        known_keys.add(dedupe_key)
        if created:
            operation_ids.append(operation_id)
        else:
            duplicate_source_ids.append(source_id)
    return {
        "discovery_operation_id": discovery_operation_id,
        "selected_count": len(selected),
        "operation_count": len(operation_ids),
        "operation_ids": operation_ids,
        "duplicate_source_ids": sorted(duplicate_source_ids),
    }


__all__ = [
    "ANALYSIS_PAGE_URL",
    "NEWS_PAGE_URL",
    "SeekingAlphaError",
    "canonical_article_url",
    "enqueue_seekingalpha_leads",
    "schedule_seekingalpha_discovery",
    "seekingalpha_dedupe_key",
    "seekingalpha_discovery_dedupe_key",
    "seekingalpha_source_id",
]

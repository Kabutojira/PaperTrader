"""Secret-free discovery of regular videos from the curated YouTube source table."""

from __future__ import annotations

import itertools
import json
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

from jsonschema import Draft202012Validator, FormatChecker

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.issues import record_issue, resolve_matching_issues
from papertrader.queue import enqueue_operation
from papertrader.tables import read_table, write_table
from papertrader.utils import ensure_utc, format_timestamp, utc_now

CHANNEL_ID = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
HANDLE = re.compile(r"^@[A-Za-z0-9._-]{3,64}$")
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
ISO_DURATION = re.compile(
    r"^P(?:(?P<days>\d+)D)?T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?"
    r"(?:(?P<seconds>\d+)S)?$"
)
YOUTUBE_DATA_API_ROOT = "https://www.googleapis.com/youtube/v3"
YOUTUBE_DATA_API_ENV = "YOUTUBE_DATA_API"
YOUTUBE_SHORT_MAX_SECONDS = 180

CURATED_CHANNELS = {
    "@allin": "UCESLZhusAkFfsNsApnjF_Cg",
    "@Value-Investing": "UCrTTBSUr0zhPU56UQljag5A",
    "@thelimitingfactor": "UCIFn7ONIJHyC-lMnb7Fm_jw",
    "@ConnectingODots": "UCOOSDCjFzHfnGoV8iNLC65A",
    "@CouchInvestor": "UCrGLm-Drgv0vbbemwwHeXJw",
    "@DumbMoneyLive": "UCS01CiRDAiyhR_mTHXDW23A",
}


class YouTubeScanError(RuntimeError):
    """Raised when curated discovery configuration or run state is unsafe."""


@dataclass(frozen=True, slots=True)
class YouTubeChannel:
    """One validated human-curated source subscription."""

    channel_id: str
    handle: str
    status: str
    transcript_languages: tuple[str, ...]
    prefer_human: bool
    last_seen_video_id: str


@dataclass(frozen=True, slots=True)
class YouTubeVideo:
    """Bounded metadata needed to create one immutable transcript-review request."""

    video_id: str
    title: str
    kind: str = "regular"


@dataclass(frozen=True, slots=True)
class YouTubeFeed:
    """Newest-first entries plus the resolved immutable channel identity."""

    channel_id: str
    entries: tuple[YouTubeVideo, ...]


class YouTubeDiscoveryClient(Protocol):
    """Narrow injectable boundary around the network-facing channel implementation."""

    provider_name: str

    def channel_feed(
        self,
        handle: str,
        *,
        channel_id: str,
        limit: int,
        minimum_regular: int = 0,
        stop_at_video_id: str = "",
        anchor_video_id: str = "",
        minimum_regular_after_anchor: int = 0,
    ) -> YouTubeFeed:
        """Return bounded newest entries, stopping once the scan objective is satisfied."""


def canonical_video_url(video_id: str) -> str:
    """Return the only canonical video URL accepted by payload and source contracts."""

    if not VIDEO_ID.fullmatch(video_id):
        raise YouTubeScanError(f"invalid YouTube video ID: {video_id!r}")
    return f"https://www.youtube.com/watch?v={video_id}"


def canonical_channel_url(channel_id: str) -> str:
    """Return the immutable channel Videos-tab URL."""

    if not CHANNEL_ID.fullmatch(channel_id):
        raise YouTubeScanError(f"invalid YouTube channel ID: {channel_id!r}")
    return f"https://www.youtube.com/channel/{channel_id}/videos"


def youtube_source_id(video_id: str) -> str:
    """Return a readable stable source identity derived only from the video ID."""

    canonical_video_url(video_id)
    return f"youtube_{video_id}"


def youtube_dedupe_key(channel_id: str, video_id: str) -> str:
    """Return the versioned once-ever queue identity for a curated video."""

    canonical_channel_url(channel_id)
    canonical_video_url(video_id)
    return f"wiki_ingest:youtube:{channel_id}:{video_id}:v1"


def load_youtube_channels(repository_root: Path, settings: Settings) -> tuple[YouTubeChannel, ...]:
    """Validate the complete curated table before any network access or mutation."""

    rows = read_table(repository_root, "youtube_channels")
    identities = {(row["handle"], row["channel_id"]) for row in rows}
    if identities != set(CURATED_CHANNELS.items()) or len(rows) != len(CURATED_CHANNELS):
        raise YouTubeScanError(
            "youtube channel table must contain exactly the six curated identities"
        )
    channels: list[YouTubeChannel] = []
    for row in rows:
        channel_id = row["channel_id"]
        handle = row["handle"]
        if not CHANNEL_ID.fullmatch(channel_id) or not HANDLE.fullmatch(handle):
            raise YouTubeScanError(f"invalid curated YouTube identity: {handle}/{channel_id}")
        if CURATED_CHANNELS.get(handle) != channel_id:
            raise YouTubeScanError(f"curated YouTube handle/channel mismatch: {handle}")
        if row["status"] not in {"active", "inactive"}:
            raise YouTubeScanError(f"invalid YouTube channel status for {handle}")
        if row["video_scope"] != "regular":
            raise YouTubeScanError(f"YouTube channel {handle} must use regular-video scope")
        languages = tuple(part for part in row["transcript_languages"].split("|") if part)
        if (
            not languages
            or len(languages) != len(set(languages))
            or any(language not in settings.youtube.transcript_languages for language in languages)
        ):
            raise YouTubeScanError(f"invalid transcript language preferences for {handle}")
        if row["prefer_human"] not in {"true", "false"}:
            raise YouTubeScanError(f"invalid human-caption preference for {handle}")
        cursor = row["last_seen_video_id"]
        if cursor and not VIDEO_ID.fullmatch(cursor):
            raise YouTubeScanError(f"invalid last-seen video cursor for {handle}")
        channels.append(
            YouTubeChannel(
                channel_id=channel_id,
                handle=handle,
                status=row["status"],
                transcript_languages=languages,
                prefer_human=row["prefer_human"] == "true",
                last_seen_video_id=cursor,
            )
        )
    return tuple(sorted(channels, key=lambda channel: channel.channel_id))


def _video_kind(video: object) -> str:
    """Classify a pytubefix object without treating Shorts or live replays as videos."""

    watch_url = str(getattr(video, "watch_url", ""))
    if "/shorts/" in watch_url:
        return "short"
    details = getattr(video, "vid_info", {})
    if isinstance(details, Mapping):
        video_details = details.get("videoDetails")
        if isinstance(video_details, Mapping) and video_details.get("isLiveContent") is True:
            return "livestream"
        microformat = details.get("microformat")
        if isinstance(microformat, Mapping):
            renderer = microformat.get("playerMicroformatRenderer")
            if isinstance(renderer, Mapping) and "liveBroadcastDetails" in renderer:
                return "livestream"
    return "regular"


class PytubefixDiscoveryClient:
    """Production adapter that reads only each channel's Videos tab without credentials."""

    provider_name = "pytubefix"

    def channel_feed(
        self,
        handle: str,
        *,
        channel_id: str,
        limit: int,
        minimum_regular: int = 0,
        stop_at_video_id: str = "",
        anchor_video_id: str = "",
        minimum_regular_after_anchor: int = 0,
    ) -> YouTubeFeed:
        from pytubefix import Channel  # type: ignore[import-untyped]

        channel = Channel(
            f"https://www.youtube.com/{handle}/videos",
            client="WEB",
            use_oauth=False,
            allow_oauth_cache=False,
        )
        resolved_channel_id = str(channel.channel_id)
        entries: list[YouTubeVideo] = []
        regular_count = 0
        anchor_seen = False
        regular_after_anchor = 0
        for video in itertools.islice(channel.videos, limit):
            video_id = str(video.video_id)
            if not VIDEO_ID.fullmatch(video_id):
                raise YouTubeScanError(f"channel {handle} returned an invalid video ID")
            entry = YouTubeVideo(
                video_id=video_id,
                title=" ".join(str(video.title).split())[:500],
                kind=_video_kind(video),
            )
            entries.append(entry)
            regular_count += entry.kind == "regular"
            if video_id == anchor_video_id:
                anchor_seen = True
            elif anchor_seen and entry.kind == "regular":
                regular_after_anchor += 1
            if stop_at_video_id and video_id == stop_at_video_id:
                break
            if (
                minimum_regular_after_anchor
                and regular_after_anchor >= minimum_regular_after_anchor
            ):
                break
            if minimum_regular and regular_count >= minimum_regular:
                break
        return YouTubeFeed(channel_id=resolved_channel_id, entries=tuple(entries))


def _duration_seconds(value: object) -> int:
    """Parse the bounded ISO-8601 duration form returned by the YouTube Data API."""

    if not isinstance(value, str):
        raise YouTubeScanError("YouTube Data API video duration is missing")
    match = ISO_DURATION.fullmatch(value)
    if match is None:
        raise YouTubeScanError("YouTube Data API video duration is malformed")
    parts = {name: int(raw or "0") for name, raw in match.groupdict().items()}
    return parts["days"] * 86400 + parts["hours"] * 3600 + parts["minutes"] * 60 + parts["seconds"]


def _mapping_items(
    payload: Mapping[str, object], *, endpoint: str
) -> tuple[Mapping[str, object], ...]:
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or any(not isinstance(item, Mapping) for item in raw_items):
        raise YouTubeScanError(f"YouTube Data API {endpoint} response has invalid items")
    return tuple(raw_items)


def _apply_feed_objective(
    entries: Sequence[YouTubeVideo],
    *,
    minimum_regular: int,
    stop_at_video_id: str,
    anchor_video_id: str,
    minimum_regular_after_anchor: int,
) -> tuple[YouTubeVideo, ...]:
    selected: list[YouTubeVideo] = []
    regular_count = 0
    anchor_seen = False
    regular_after_anchor = 0
    for entry in entries:
        selected.append(entry)
        regular_count += entry.kind == "regular"
        if entry.video_id == anchor_video_id:
            anchor_seen = True
        elif anchor_seen and entry.kind == "regular":
            regular_after_anchor += 1
        if stop_at_video_id and entry.video_id == stop_at_video_id:
            break
        if minimum_regular_after_anchor and regular_after_anchor >= minimum_regular_after_anchor:
            break
        if minimum_regular and regular_count >= minimum_regular:
            break
    return tuple(selected)


class YouTubeDataAPIClient:
    """Bounded key-based discovery through channels, uploads playlists, and video metadata."""

    provider_name = "youtube_data_api"

    def __init__(self, api_key: str, *, timeout_seconds: int = 30) -> None:
        normalized = api_key.strip()
        if not normalized:
            raise YouTubeScanError("YouTube Data API key must not be empty")
        self._api_key = normalized
        self._timeout_seconds = timeout_seconds

    def _request_json(self, endpoint: str, parameters: Mapping[str, str]) -> Mapping[str, object]:
        query = urlencode({**parameters, "key": self._api_key})
        request = Request(
            f"{YOUTUBE_DATA_API_ROOT}/{endpoint}?{query}",
            headers={"Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            raise YouTubeScanError(
                f"YouTube Data API {endpoint} request failed with HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise YouTubeScanError(f"YouTube Data API {endpoint} request failed") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise YouTubeScanError(f"YouTube Data API {endpoint} returned invalid JSON") from exc
        if not isinstance(payload, Mapping):
            raise YouTubeScanError(f"YouTube Data API {endpoint} returned a non-object")
        return payload

    def channel_feed(
        self,
        handle: str,
        *,
        channel_id: str,
        limit: int,
        minimum_regular: int = 0,
        stop_at_video_id: str = "",
        anchor_video_id: str = "",
        minimum_regular_after_anchor: int = 0,
    ) -> YouTubeFeed:
        if not CHANNEL_ID.fullmatch(channel_id):
            raise YouTubeScanError(f"invalid curated YouTube channel ID: {channel_id!r}")
        if limit < 1 or limit > 50:
            raise YouTubeScanError("YouTube Data API discovery limit must be between 1 and 50")
        channel_items = _mapping_items(
            self._request_json(
                "channels",
                {"part": "contentDetails", "id": channel_id, "maxResults": "1"},
            ),
            endpoint="channels",
        )
        if len(channel_items) != 1 or channel_items[0].get("id") != channel_id:
            raise YouTubeScanError(f"YouTube Data API could not resolve curated channel {handle}")
        content_details = channel_items[0].get("contentDetails")
        related_playlists = (
            content_details.get("relatedPlaylists")
            if isinstance(content_details, Mapping)
            else None
        )
        uploads_id = (
            related_playlists.get("uploads") if isinstance(related_playlists, Mapping) else None
        )
        if not isinstance(uploads_id, str) or not uploads_id:
            raise YouTubeScanError("YouTube Data API channel has no uploads playlist")

        playlist_items = _mapping_items(
            self._request_json(
                "playlistItems",
                {
                    "part": "contentDetails",
                    "playlistId": uploads_id,
                    "maxResults": str(limit),
                },
            ),
            endpoint="playlistItems",
        )
        video_ids: list[str] = []
        for item in playlist_items:
            details = item.get("contentDetails")
            video_id = details.get("videoId") if isinstance(details, Mapping) else None
            if not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id):
                raise YouTubeScanError("YouTube Data API uploads playlist has an invalid video ID")
            video_ids.append(video_id)
        if len(video_ids) != len(set(video_ids)):
            raise YouTubeScanError("YouTube Data API uploads playlist returned duplicate videos")
        if not video_ids:
            return YouTubeFeed(channel_id=channel_id, entries=())

        video_items = _mapping_items(
            self._request_json(
                "videos",
                {
                    "part": "contentDetails,liveStreamingDetails,snippet",
                    "id": ",".join(video_ids),
                    "maxResults": str(len(video_ids)),
                },
            ),
            endpoint="videos",
        )
        metadata: dict[str, Mapping[str, object]] = {}
        for item in video_items:
            video_id = item.get("id")
            if not isinstance(video_id, str) or video_id in metadata:
                raise YouTubeScanError("YouTube Data API video metadata has invalid identities")
            metadata[video_id] = item
        if set(metadata) != set(video_ids):
            raise YouTubeScanError("YouTube Data API omitted requested video metadata")

        entries: list[YouTubeVideo] = []
        for video_id in video_ids:
            item = metadata[video_id]
            snippet = item.get("snippet")
            details = item.get("contentDetails")
            if not isinstance(snippet, Mapping) or not isinstance(details, Mapping):
                raise YouTubeScanError("YouTube Data API video metadata is incomplete")
            title = snippet.get("title")
            live_state = snippet.get("liveBroadcastContent")
            if not isinstance(title, str) or live_state not in {"none", "live", "upcoming"}:
                raise YouTubeScanError("YouTube Data API video snippet is malformed")
            duration = _duration_seconds(details.get("duration"))
            if live_state != "none" or "liveStreamingDetails" in item:
                kind = "livestream"
            elif duration <= YOUTUBE_SHORT_MAX_SECONDS:
                kind = "short"
            else:
                kind = "regular"
            entries.append(
                YouTubeVideo(
                    video_id=video_id,
                    title=" ".join(title.split())[:500],
                    kind=kind,
                )
            )
        return YouTubeFeed(
            channel_id=channel_id,
            entries=_apply_feed_objective(
                entries,
                minimum_regular=minimum_regular,
                stop_at_video_id=stop_at_video_id,
                anchor_video_id=anchor_video_id,
                minimum_regular_after_anchor=minimum_regular_after_anchor,
            ),
        )


def youtube_discovery_client(environment: Mapping[str, str]) -> YouTubeDiscoveryClient:
    """Select Data API discovery only when its purpose-bound credential is nonempty."""

    api_key = environment.get(YOUTUBE_DATA_API_ENV, "").strip()
    return YouTubeDataAPIClient(api_key) if api_key else PytubefixDiscoveryClient()


def _manifest_provider(discovery: YouTubeDiscoveryClient | None) -> tuple[str, str]:
    provider = getattr(discovery, "provider_name", "pytubefix") if discovery else "none"
    if provider == "youtube_data_api":
        return provider, "non_live_duration_over_180_seconds"
    if provider == "pytubefix":
        return provider, "videos_tab_non_short_non_live"
    raise YouTubeScanError(f"unsupported YouTube discovery provider: {provider}")


def _failure_reason(exc: Exception, environment: Mapping[str, str]) -> str:
    reason = " ".join(str(exc).split())[:1000] or exc.__class__.__name__
    secret = environment.get(YOUTUBE_DATA_API_ENV, "").strip()
    return reason.replace(secret, "[REDACTED]") if secret else reason


def _registered_video_ids(repository_root: Path) -> set[str]:
    video_ids: set[str] = set()
    for row in read_table(repository_root, "source_registry"):
        if row["source_type"] != "youtube_video":
            continue
        parsed = urlsplit(row["canonical_url"])
        candidate = parse_qs(parsed.query).get("v", [""])[0]
        if VIDEO_ID.fullmatch(candidate):
            video_ids.add(candidate)
        elif row["source_id"].startswith("youtube_"):
            candidate = row["source_id"].removeprefix("youtube_")
            if VIDEO_ID.fullmatch(candidate):
                video_ids.add(candidate)
    return video_ids


def _known_dedupe_keys(repository_root: Path) -> set[str]:
    return {
        row["dedupe_key"]
        for table in ("operations_todo", "operations_history")
        for row in read_table(repository_root, table)
    }


def _failure_issue(
    repository_root: Path,
    *,
    channel: YouTubeChannel,
    run_id: str,
    reason: str,
    now: datetime,
) -> str:
    return record_issue(
        repository_root,
        issue_code="youtube_discovery_failed",
        impact="operational_only",
        severity="warning",
        title=f"YouTube discovery failed for {channel.channel_id}",
        description=f"{channel.handle}: {reason}",
        entity_type="channel",
        entity_id=channel.channel_id,
        owner="youtube-discovery",
        related_run_id=run_id,
        now=now,
    )


def _channel_row(channel: YouTubeChannel, cursor: str) -> dict[str, str]:
    return {
        "channel_id": channel.channel_id,
        "handle": channel.handle,
        "status": channel.status,
        "video_scope": "regular",
        "transcript_languages": "|".join(channel.transcript_languages),
        "prefer_human": str(channel.prefer_human).lower(),
        "last_seen_video_id": cursor,
    }


def _load_youtube_scan_manifest(repository_root: Path, run_id: str) -> Mapping[str, object]:
    """Load and validate one immutable YouTube discovery artifact."""

    path = repository_root / "data" / "runs" / run_id / "youtube_scan.json"
    if path.is_symlink() or not path.is_file():
        raise YouTubeScanError("YouTube scan artifact must be a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads(
            (repository_root / "schemas" / "youtube_scan.schema.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise YouTubeScanError(f"cannot read YouTube scan artifact: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        raise YouTubeScanError(f"invalid YouTube scan artifact: {errors[0].message}")
    if not isinstance(value, Mapping) or value.get("run_id") != run_id:
        raise YouTubeScanError("YouTube scan artifact identity mismatch")
    return value


def _skip_existing_youtube_scan(repository_root: Path, run_id: str) -> Mapping[str, object] | None:
    """Return an idempotent skip result without replacing an existing manifest."""

    manifest_path = repository_root / "data" / "runs" / run_id / "youtube_scan.json"
    if not manifest_path.exists():
        return None
    manifest = _load_youtube_scan_manifest(repository_root, run_id)
    return {
        "youtube_scan_version": manifest["youtube_scan_version"],
        "run_id": run_id,
        "status": "skipped",
        "reason": "manifest_already_exists",
        "existing_manifest_status": manifest["status"],
        "manifest_path": manifest_path.relative_to(repository_root).as_posix(),
        "operation_count": 0,
        "failure_count": 0,
    }


def scan_youtube(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    dry_run: bool = False,
    client: YouTubeDiscoveryClient | None = None,
    environment: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> Mapping[str, object]:
    """Scan curated channels sequentially and enqueue one bounded operation per unseen video."""

    if not RUN_ID.fullmatch(run_id):
        raise YouTubeScanError(f"invalid YouTube scan run_id: {run_id!r}")
    existing = _skip_existing_youtube_scan(repository_root, run_id)
    if existing is not None:
        return existing
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    source_environment = os.environ if environment is None else environment
    channels = load_youtube_channels(repository_root, settings)
    manifest_path = repository_root / "data" / "runs" / run_id / "youtube_scan.json"
    if manifest_path.parent.is_symlink():
        raise YouTubeScanError("YouTube scan run directory must not be a symlink")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    selected_discovery = client or youtube_discovery_client(source_environment)
    discovery_provider, regular_video_policy = _manifest_provider(selected_discovery)
    if not settings.youtube.enabled or dry_run:
        status = "disabled" if not settings.youtube.enabled else "dry_run"
        if not settings.youtube.enabled:
            discovery_provider, regular_video_policy = "none", "none"
        dry_outcomes = [
            {
                "channel_id": channel.channel_id,
                "handle": channel.handle,
                "status": "skipped",
                "reason": status,
                "previous_cursor": channel.last_seen_video_id,
                "next_cursor": channel.last_seen_video_id,
                "inspected_count": 0,
                "discovered_video_ids": [],
                "duplicate_video_ids": [],
                "operation_ids": [],
                "issue_id": "",
            }
            for channel in channels
        ]
        manifest: Mapping[str, object] = {
            "youtube_scan_version": 2,
            "run_id": run_id,
            "discovered_at": format_timestamp(instant),
            "status": status,
            "discovery_provider": discovery_provider,
            "regular_video_policy": regular_video_policy,
            "scan_bound": settings.youtube.scan_bound,
            "seed_count": settings.youtube.seed_count,
            "channels": dry_outcomes,
            "operation_count": 0,
            "failure_count": 0,
        }
        atomic_write_json(manifest_path, manifest, allowed_root=repository_root)
        return manifest

    discovery = selected_discovery
    known_dedupe = _known_dedupe_keys(repository_root)
    registered_video_ids = _registered_video_ids(repository_root)
    cursors = {channel.channel_id: channel.last_seen_video_id for channel in channels}
    outcomes: list[dict[str, object]] = []
    all_video_ids: set[str] = set()
    operation_count = 0
    failure_count = 0

    for channel in channels:
        if channel.status == "inactive":
            outcomes.append(
                {
                    "channel_id": channel.channel_id,
                    "handle": channel.handle,
                    "status": "skipped",
                    "reason": "inactive",
                    "previous_cursor": channel.last_seen_video_id,
                    "next_cursor": channel.last_seen_video_id,
                    "inspected_count": 0,
                    "discovered_video_ids": [],
                    "duplicate_video_ids": [],
                    "operation_ids": [],
                    "issue_id": "",
                }
            )
            continue
        inspected_count = 0
        discovered: tuple[YouTubeVideo, ...] = ()
        duplicate_ids: list[str] = []
        operation_ids: list[str] = []
        try:
            fetch_limit = settings.youtube.scan_bound
            feed = discovery.channel_feed(
                channel.handle,
                channel_id=channel.channel_id,
                limit=fetch_limit,
                minimum_regular=(
                    settings.youtube.seed_count if not channel.last_seen_video_id else 0
                ),
                stop_at_video_id=channel.last_seen_video_id,
            )
            if feed.channel_id != channel.channel_id:
                raise YouTubeScanError(
                    f"resolved channel ID {feed.channel_id!r} does not match configuration"
                )
            entries = feed.entries[:fetch_limit]
            inspected_count = len(entries)
            if len({entry.video_id for entry in entries}) != len(entries):
                raise YouTubeScanError("Videos tab returned duplicate video identities")
            regular = tuple(entry for entry in entries if entry.kind == "regular")
            if any(not VIDEO_ID.fullmatch(entry.video_id) for entry in regular):
                raise YouTubeScanError("Videos tab returned a malformed video identity")
            if channel.last_seen_video_id:
                cursor_index = next(
                    (
                        index
                        for index, entry in enumerate(entries)
                        if entry.video_id == channel.last_seen_video_id
                    ),
                    None,
                )
                if cursor_index is None:
                    raise YouTubeScanError(
                        f"cursor_not_found_within_scan_bound:{settings.youtube.scan_bound}"
                    )
                discovered = tuple(
                    entry for entry in entries[:cursor_index] if entry.kind == "regular"
                )
                mode = "incremental"
            else:
                if len(regular) < settings.youtube.seed_count:
                    raise YouTubeScanError(
                        "insufficient_regular_videos_for_bootstrap:"
                        f"{len(regular)}/{settings.youtube.seed_count}"
                    )
                discovered = regular[: settings.youtube.seed_count]
                mode = "bootstrap"
            duplicate_cross_channel = sorted(
                entry.video_id for entry in discovered if entry.video_id in all_video_ids
            )
            if duplicate_cross_channel:
                raise YouTubeScanError(
                    f"video identity returned by multiple channels: {duplicate_cross_channel}"
                )
            all_video_ids.update(entry.video_id for entry in discovered)

            for video in discovered:
                dedupe_key = youtube_dedupe_key(channel.channel_id, video.video_id)
                if video.video_id in registered_video_ids or dedupe_key in known_dedupe:
                    duplicate_ids.append(video.video_id)
                    continue
                source_id = youtube_source_id(video.video_id)
                operation_id, created = enqueue_operation(
                    repository_root,
                    settings,
                    operation_type="wiki_ingest",
                    entity_type="source",
                    entity_id=source_id,
                    dedupe_key=dedupe_key,
                    prompt="Analyze one curated YouTube transcript as an untrusted lead source.",
                    inputs={
                        "source_kind": "youtube_video",
                        "source_id": source_id,
                        "video_id": video.video_id,
                        "video_title": video.title,
                        "video_url": canonical_video_url(video.video_id),
                        "channel_id": channel.channel_id,
                        "channel_handle": channel.handle,
                        "channel_url": canonical_channel_url(channel.channel_id),
                        "discovered_at": format_timestamp(instant),
                        "transcript_languages": list(channel.transcript_languages),
                        "prefer_human": channel.prefer_human,
                        "discovery_mode": mode,
                    },
                    source=f"youtube_scan:{run_id}",
                    priority=(
                        settings.youtube.bootstrap_priority
                        if mode == "bootstrap"
                        else settings.youtube.discovery_priority
                    ),
                    source_refs=(canonical_video_url(video.video_id),),
                    now=instant,
                )
                known_dedupe.add(dedupe_key)
                if created:
                    operation_ids.append(operation_id)
                    operation_count += 1
                else:
                    duplicate_ids.append(video.video_id)
            next_cursor = regular[0].video_id if regular else channel.last_seen_video_id
            cursors[channel.channel_id] = next_cursor
            resolve_matching_issues(
                repository_root,
                issue_code="youtube_discovery_failed",
                entity_type="channel",
                entity_id=channel.channel_id,
                resolution=f"youtube_discovery_recovered: {run_id}",
                now=instant,
            )
            outcomes.append(
                {
                    "channel_id": channel.channel_id,
                    "handle": channel.handle,
                    "status": "succeeded",
                    "reason": "",
                    "previous_cursor": channel.last_seen_video_id,
                    "next_cursor": next_cursor,
                    "inspected_count": inspected_count,
                    "discovered_video_ids": [entry.video_id for entry in discovered],
                    "duplicate_video_ids": sorted(duplicate_ids),
                    "operation_ids": operation_ids,
                    "issue_id": "",
                }
            )
        except Exception as exc:
            reason = _failure_reason(exc, source_environment)
            issue_id = _failure_issue(
                repository_root,
                channel=channel,
                run_id=run_id,
                reason=reason,
                now=instant,
            )
            failure_count += 1
            outcomes.append(
                {
                    "channel_id": channel.channel_id,
                    "handle": channel.handle,
                    "status": "failed",
                    "reason": reason,
                    "previous_cursor": channel.last_seen_video_id,
                    "next_cursor": channel.last_seen_video_id,
                    "inspected_count": inspected_count,
                    "discovered_video_ids": [entry.video_id for entry in discovered],
                    "duplicate_video_ids": sorted(duplicate_ids),
                    "operation_ids": operation_ids,
                    "issue_id": issue_id,
                }
            )

    updated_rows = [_channel_row(channel, cursors[channel.channel_id]) for channel in channels]
    if updated_rows != read_table(repository_root, "youtube_channels"):
        write_table(repository_root, "youtube_channels", updated_rows)
    manifest = {
        "youtube_scan_version": 2,
        "run_id": run_id,
        "discovered_at": format_timestamp(instant),
        "status": "degraded" if failure_count else "succeeded",
        "discovery_provider": discovery_provider,
        "regular_video_policy": regular_video_policy,
        "scan_bound": settings.youtube.scan_bound,
        "seed_count": settings.youtube.seed_count,
        "channels": outcomes,
        "operation_count": operation_count,
        "failure_count": failure_count,
    }
    atomic_write_json(manifest_path, manifest, allowed_root=repository_root)
    return manifest


def backfill_youtube(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    channel_id: str,
    count: int,
    client: YouTubeDiscoveryClient | None = None,
    environment: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> Mapping[str, object]:
    """Queue exactly ``count`` unseen regular videos older than one channel's cursor."""

    if not RUN_ID.fullmatch(run_id):
        raise YouTubeScanError(f"invalid YouTube backfill run_id: {run_id!r}")
    if not CHANNEL_ID.fullmatch(channel_id):
        raise YouTubeScanError(f"invalid YouTube backfill channel ID: {channel_id!r}")
    if count < 1 or count >= settings.youtube.scan_bound:
        raise YouTubeScanError(
            f"YouTube backfill count must be between 1 and {settings.youtube.scan_bound - 1}"
        )
    existing = _skip_existing_youtube_scan(repository_root, run_id)
    if existing is not None:
        return existing
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    source_environment = os.environ if environment is None else environment
    channels = load_youtube_channels(repository_root, settings)
    targets = [channel for channel in channels if channel.channel_id == channel_id]
    if len(targets) != 1:
        raise YouTubeScanError(f"YouTube backfill channel is not curated: {channel_id}")
    target = targets[0]
    if target.status != "active" or not target.last_seen_video_id:
        raise YouTubeScanError("YouTube backfill requires an active channel with a cursor")
    manifest_path = repository_root / "data" / "runs" / run_id / "youtube_scan.json"
    if manifest_path.parent.is_symlink():
        raise YouTubeScanError("YouTube backfill run directory must not be a symlink")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not settings.youtube.enabled:
        raise YouTubeScanError("YouTube discovery is disabled")

    known_dedupe = _known_dedupe_keys(repository_root)
    registered_video_ids = _registered_video_ids(repository_root)
    prefix = f"wiki_ingest:youtube:{channel_id}:"
    known_channel_video_ids = {
        key.removeprefix(prefix).removesuffix(":v1")
        for key in known_dedupe
        if key.startswith(prefix) and key.endswith(":v1")
    }
    minimum_after_cursor = min(
        settings.youtube.scan_bound - 1,
        count + len(known_channel_video_ids - {target.last_seen_video_id}),
    )
    discovery = client or youtube_discovery_client(source_environment)
    discovery_provider, regular_video_policy = _manifest_provider(discovery)
    outcomes: list[dict[str, object]] = []
    operation_ids: list[str] = []
    discovered_video_ids: list[str] = []
    duplicate_video_ids: list[str] = []
    inspected_count = 0
    failure_count = 0
    failure_reason = ""
    issue_id = ""
    try:
        feed = discovery.channel_feed(
            target.handle,
            channel_id=target.channel_id,
            limit=settings.youtube.scan_bound,
            anchor_video_id=target.last_seen_video_id,
            minimum_regular_after_anchor=minimum_after_cursor,
        )
        if feed.channel_id != target.channel_id:
            raise YouTubeScanError(
                f"resolved channel ID {feed.channel_id!r} does not match configuration"
            )
        entries = feed.entries[: settings.youtube.scan_bound]
        inspected_count = len(entries)
        if len({entry.video_id for entry in entries}) != len(entries):
            raise YouTubeScanError("Videos tab returned duplicate video identities")
        cursor_index = next(
            (
                index
                for index, entry in enumerate(entries)
                if entry.video_id == target.last_seen_video_id
            ),
            None,
        )
        if cursor_index is None:
            raise YouTubeScanError(
                f"cursor_not_found_within_scan_bound:{settings.youtube.scan_bound}"
            )
        candidates: list[YouTubeVideo] = []
        for video in entries[cursor_index + 1 :]:
            if video.kind != "regular":
                continue
            dedupe_key = youtube_dedupe_key(target.channel_id, video.video_id)
            if video.video_id in registered_video_ids or dedupe_key in known_dedupe:
                duplicate_video_ids.append(video.video_id)
                continue
            candidates.append(video)
            if len(candidates) == count:
                break
        if len(candidates) != count:
            raise YouTubeScanError(
                f"insufficient_unseen_regular_videos_for_backfill:{len(candidates)}/{count}"
            )
        discovered_video_ids = [video.video_id for video in candidates]
        for video in candidates:
            operation_id, created = enqueue_operation(
                repository_root,
                settings,
                operation_type="wiki_ingest",
                entity_type="source",
                entity_id=youtube_source_id(video.video_id),
                dedupe_key=youtube_dedupe_key(target.channel_id, video.video_id),
                prompt="Analyze one curated YouTube transcript as an untrusted lead source.",
                inputs={
                    "source_kind": "youtube_video",
                    "source_id": youtube_source_id(video.video_id),
                    "video_id": video.video_id,
                    "video_title": video.title,
                    "video_url": canonical_video_url(video.video_id),
                    "channel_id": target.channel_id,
                    "channel_handle": target.handle,
                    "channel_url": canonical_channel_url(target.channel_id),
                    "discovered_at": format_timestamp(instant),
                    "transcript_languages": list(target.transcript_languages),
                    "prefer_human": target.prefer_human,
                    "discovery_mode": "backfill",
                },
                source=f"youtube_backfill:{run_id}",
                priority=settings.youtube.bootstrap_priority,
                source_refs=(canonical_video_url(video.video_id),),
                now=instant,
            )
            if not created:
                raise YouTubeScanError(f"backfill operation became duplicate: {video.video_id}")
            known_dedupe.add(youtube_dedupe_key(target.channel_id, video.video_id))
            operation_ids.append(operation_id)
    except Exception as exc:
        failure_count = 1
        failure_reason = _failure_reason(exc, source_environment)
        issue_id = _failure_issue(
            repository_root,
            channel=target,
            run_id=run_id,
            reason=failure_reason,
            now=instant,
        )
    if not failure_count:
        resolve_matching_issues(
            repository_root,
            issue_code="youtube_discovery_failed",
            entity_type="channel",
            entity_id=target.channel_id,
            resolution=f"youtube_discovery_recovered: {run_id}",
            now=instant,
        )

    for channel in channels:
        selected = channel.channel_id == target.channel_id
        outcomes.append(
            {
                "channel_id": channel.channel_id,
                "handle": channel.handle,
                "status": "failed"
                if selected and failure_count
                else ("succeeded" if selected else "skipped"),
                "reason": failure_reason if selected else "not_selected_for_backfill",
                "previous_cursor": channel.last_seen_video_id,
                "next_cursor": channel.last_seen_video_id,
                "inspected_count": inspected_count if selected else 0,
                "discovered_video_ids": discovered_video_ids if selected else [],
                "duplicate_video_ids": sorted(duplicate_video_ids) if selected else [],
                "operation_ids": operation_ids if selected else [],
                "issue_id": issue_id if selected else "",
            }
        )
    manifest = {
        "youtube_scan_version": 2,
        "run_id": run_id,
        "discovered_at": format_timestamp(instant),
        "status": "degraded" if failure_count else "succeeded",
        "discovery_provider": discovery_provider,
        "regular_video_policy": regular_video_policy,
        "scan_bound": settings.youtube.scan_bound,
        "seed_count": settings.youtube.seed_count,
        "scan_mode": "backfill",
        "requested_count": count,
        "channels": outcomes,
        "operation_count": len(operation_ids),
        "failure_count": failure_count,
    }
    atomic_write_json(manifest_path, manifest, allowed_root=repository_root)
    return manifest


def youtube_scan_failures(repository_root: Path, run_id: str) -> tuple[str, ...]:
    """Return validated channel failures for daily degradation and reporting."""

    path = repository_root / "data" / "runs" / run_id / "youtube_scan.json"
    if not path.exists():
        return ()
    value = _load_youtube_scan_manifest(repository_root, run_id)
    channels = value.get("channels")
    assert isinstance(channels, Sequence)
    return tuple(
        f"youtube scan failed for {channel['channel_id']}: {channel['reason']}"
        for channel in channels
        if isinstance(channel, Mapping) and channel.get("status") == "failed"
    )


__all__ = [
    "CURATED_CHANNELS",
    "PytubefixDiscoveryClient",
    "YouTubeChannel",
    "YouTubeDataAPIClient",
    "YouTubeDiscoveryClient",
    "YouTubeFeed",
    "YouTubeScanError",
    "YouTubeVideo",
    "backfill_youtube",
    "canonical_channel_url",
    "canonical_video_url",
    "load_youtube_channels",
    "scan_youtube",
    "youtube_dedupe_key",
    "youtube_discovery_client",
    "youtube_scan_failures",
    "youtube_source_id",
]

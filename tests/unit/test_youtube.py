from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request

import pytest

import papertrader.youtube as youtube_module
from papertrader.config import Settings
from papertrader.daily import prepare_daily_run
from papertrader.tables import read_table, write_table
from papertrader.youtube import (
    CURATED_CHANNELS,
    PytubefixDiscoveryClient,
    YouTubeDataAPIClient,
    YouTubeFeed,
    YouTubeScanError,
    YouTubeVideo,
    backfill_youtube,
    canonical_channel_url,
    canonical_video_url,
    deactivate_youtube_channels,
    load_youtube_channels,
    scan_youtube,
    youtube_dedupe_key,
    youtube_discovery_client,
    youtube_source_id,
)

NOW = datetime(2026, 7, 29, 8, tzinfo=UTC)


class FakeDiscovery:
    provider_name = "pytubefix"

    def __init__(self, feeds: dict[str, YouTubeFeed | Exception]) -> None:
        self.feeds = feeds
        self.calls: list[tuple[str, int]] = []

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
        assert channel_id == CURATED_CHANNELS[handle]
        self.calls.append((handle, limit))
        value = self.feeds[handle]
        if isinstance(value, Exception):
            raise value
        entries: list[YouTubeVideo] = []
        regular_count = 0
        anchor_seen = False
        regular_after_anchor = 0
        for entry in value.entries[:limit]:
            entries.append(entry)
            regular_count += entry.kind == "regular"
            if entry.video_id == anchor_video_id:
                anchor_seen = True
            elif anchor_seen and entry.kind == "regular":
                regular_after_anchor += 1
            if stop_at_video_id and entry.video_id == stop_at_video_id:
                break
            if (
                minimum_regular_after_anchor
                and regular_after_anchor >= minimum_regular_after_anchor
            ):
                break
            if minimum_regular and regular_count >= minimum_regular:
                break
        return YouTubeFeed(value.channel_id, tuple(entries))


def _video(index: int, *, kind: str = "regular") -> YouTubeVideo:
    return YouTubeVideo(f"{index:011d}", f"Video {index}", kind)


def _seed_channels(repository: Path, *, cursor: str = "") -> None:
    write_table(
        repository,
        "youtube_channels",
        [
            {
                "channel_id": channel_id,
                "handle": handle,
                "status": "active",
                "video_scope": "regular",
                "transcript_languages": "en|en-US|en-GB",
                "prefer_human": "true",
                "last_seen_video_id": cursor,
            }
            for handle, channel_id in sorted(CURATED_CHANNELS.items(), key=lambda item: item[1])
        ],
    )


def _feeds(*, videos_per_channel: int = 7) -> dict[str, YouTubeFeed]:
    feeds: dict[str, YouTubeFeed] = {}
    for channel_index, (handle, channel_id) in enumerate(sorted(CURATED_CHANNELS.items()), start=1):
        start = channel_index * 100
        feeds[handle] = YouTubeFeed(
            channel_id,
            tuple(_video(start + index) for index in range(videos_per_channel)),
        )
    return feeds


def test_canonical_youtube_identities_and_channel_table_validation(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)

    channels = load_youtube_channels(sandbox_repository, sandbox_settings)

    assert len(channels) == 6
    assert canonical_video_url("abcdefghijk") == ("https://www.youtube.com/watch?v=abcdefghijk")
    assert youtube_source_id("abcdefghijk") == "youtube_abcdefghijk"
    assert canonical_channel_url(channels[0].channel_id).endswith("/videos")
    assert youtube_dedupe_key(channels[0].channel_id, "abcdefghijk").endswith(":abcdefghijk:v1")

    rows = read_table(sandbox_repository, "youtube_channels")
    rows[0]["video_scope"] = "all"
    write_table(sandbox_repository, "youtube_channels", rows)
    with pytest.raises(YouTubeScanError, match="regular-video scope"):
        load_youtube_channels(sandbox_repository, sandbox_settings)


def test_deactivate_youtube_channels_is_validated_and_idempotent(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)

    changed = deactivate_youtube_channels(sandbox_repository, sandbox_settings)

    assert set(changed) == set(CURATED_CHANNELS.values())
    assert {row["status"] for row in read_table(sandbox_repository, "youtube_channels")} == {
        "inactive"
    }
    assert deactivate_youtube_channels(sandbox_repository, sandbox_settings) == ()


def test_bootstrap_queues_exactly_five_regular_videos_per_channel_and_is_idempotent(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds()

    first = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-bootstrap",
        client=FakeDiscovery(feeds),
        now=NOW,
    )

    assert first["status"] == "succeeded"
    assert first["youtube_scan_version"] == 2
    assert first["discovery_provider"] == "pytubefix"
    assert first["regular_video_policy"] == "videos_tab_non_short_non_live"
    assert first["operation_count"] == 30
    operations = read_table(sandbox_repository, "operations_todo")
    assert len(operations) == 30
    assert {row["priority"] for row in operations} == {"60"}
    assert len({row["dedupe_key"] for row in operations}) == 30
    assert all(row["dedupe_key"].endswith(":v1") for row in operations)
    payloads = [
        json.loads((sandbox_repository / row["payload_path"]).read_text(encoding="utf-8"))
        for row in operations
    ]
    assert {payload["inputs"]["discovery_mode"] for payload in payloads} == {"bootstrap"}
    assert all(payload["inputs"]["source_kind"] == "youtube_video" for payload in payloads)
    assert all(len(outcome["discovered_video_ids"]) == 5 for outcome in first["channels"])

    table_before = read_table(sandbox_repository, "youtube_channels")
    second = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-identical",
        client=FakeDiscovery(feeds),
        now=NOW + timedelta(days=1),
    )

    assert second["operation_count"] == 0
    assert read_table(sandbox_repository, "operations_todo") == operations
    assert read_table(sandbox_repository, "youtube_channels") == table_before


def test_existing_scan_manifest_returns_successful_skip_without_mutation(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds()
    discovery = FakeDiscovery(feeds)
    run_id = "youtube-repeat-run"
    first = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        client=discovery,
        now=NOW,
    )
    manifest_path = sandbox_repository / "data" / "runs" / run_id / "youtube_scan.json"
    manifest_before = manifest_path.read_bytes()
    channels_before = read_table(sandbox_repository, "youtube_channels")
    operations_before = read_table(sandbox_repository, "operations_todo")
    discovery.calls.clear()

    repeated = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        client=discovery,
        now=NOW + timedelta(hours=1),
    )

    assert repeated == {
        "youtube_scan_version": 2,
        "run_id": run_id,
        "status": "skipped",
        "reason": "manifest_already_exists",
        "existing_manifest_status": first["status"],
        "manifest_path": f"data/runs/{run_id}/youtube_scan.json",
        "operation_count": 0,
        "failure_count": 0,
    }
    assert discovery.calls == []
    assert manifest_path.read_bytes() == manifest_before
    assert read_table(sandbox_repository, "youtube_channels") == channels_before
    assert read_table(sandbox_repository, "operations_todo") == operations_before


def test_scan_excludes_shorts_and_livestream_replays(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds(videos_per_channel=0)
    for index, (handle, channel_id) in enumerate(sorted(CURATED_CHANNELS.items()), start=1):
        feeds[handle] = YouTubeFeed(
            channel_id,
            (
                _video(index * 100 + 1, kind="short"),
                _video(index * 100 + 2, kind="livestream"),
                *tuple(_video(index * 100 + value) for value in range(3, 8)),
            ),
        )

    result = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-regular-only",
        client=FakeDiscovery(feeds),
        now=NOW,
    )

    assert result["operation_count"] == 30
    discovered = {
        video_id for outcome in result["channels"] for video_id in outcome["discovered_video_ids"]
    }
    assert not any(video_id.endswith("01") or video_id.endswith("02") for video_id in discovered)


def test_bootstrap_fails_one_channel_instead_of_silently_seeding_fewer_than_five(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds(videos_per_channel=5)
    failed_handle = sorted(CURATED_CHANNELS)[0]
    failed_feed = feeds[failed_handle]
    feeds[failed_handle] = YouTubeFeed(failed_feed.channel_id, failed_feed.entries[:4])

    result = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-short-bootstrap",
        client=FakeDiscovery(feeds),
        now=NOW,
    )

    assert result["status"] == "degraded"
    assert result["operation_count"] == 25
    failed = next(row for row in result["channels"] if row["handle"] == failed_handle)
    assert failed["reason"] == "insufficient_regular_videos_for_bootstrap:4/5"
    assert failed["next_cursor"] == ""


def test_incremental_scan_uses_cursor_and_discovery_priority(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds()
    scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-seed",
        client=FakeDiscovery(feeds),
        now=NOW,
    )
    target_handle = sorted(CURATED_CHANNELS)[0]
    old_feed = feeds[target_handle]
    feeds[target_handle] = YouTubeFeed(
        old_feed.channel_id,
        (_video(999_999), _video(999_998), *old_feed.entries),
    )

    result = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-incremental",
        client=FakeDiscovery(feeds),
        now=NOW + timedelta(days=1),
    )

    assert result["operation_count"] == 2
    incremental = [
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["source"] == "youtube_scan:youtube-incremental"
    ]
    assert len(incremental) == 2
    assert {row["priority"] for row in incremental} == {"65"}


def test_cursor_not_found_fails_one_channel_without_advancing_or_stopping_others(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository, cursor="99999999999")
    feeds = _feeds(videos_per_channel=50)
    failing_handle = sorted(CURATED_CHANNELS)[0]
    # The other channels include their cursor after one new regular video.
    for offset, (handle, feed) in enumerate(tuple(feeds.items()), start=1):
        if handle != failing_handle:
            feeds[handle] = YouTubeFeed(
                feed.channel_id,
                (_video(888_000 + offset), _video(99_999_999_999)),
            )

    result = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-cursor-missing",
        client=FakeDiscovery(feeds),
        now=NOW,
    )

    assert result["status"] == "degraded"
    assert result["failure_count"] == 1
    assert result["operation_count"] == 5
    failed = next(row for row in result["channels"] if row["status"] == "failed")
    assert failed["handle"] == failing_handle
    assert "cursor_not_found_within_scan_bound:50" in failed["reason"]
    assert failed["previous_cursor"] == failed["next_cursor"] == "99999999999"
    assert (
        len([row for row in read_table(sandbox_repository, "issues") if row["status"] == "open"])
        == 1
    )


def test_channel_failure_degrades_the_daily_run_without_duplicate_issue(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds: dict[str, YouTubeFeed | Exception] = _feeds(videos_per_channel=5)
    failed_handle = sorted(CURATED_CHANNELS)[0]
    feeds[failed_handle] = RuntimeError("remote channel unavailable")
    scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-daily-degraded",
        client=FakeDiscovery(feeds),
        now=NOW,
    )

    preparation = prepare_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-daily-degraded",
        trigger="unit",
        source_sha="a" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )

    assert len(preparation.errors) == 1
    assert preparation.errors[0].startswith("youtube scan failed for ")
    assert len(read_table(sandbox_repository, "issues")) == 1


def test_dry_run_validates_configuration_without_network_or_state_changes(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    client = FakeDiscovery({})
    before = read_table(sandbox_repository, "youtube_channels")

    result = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-dry-run",
        dry_run=True,
        client=client,
        now=NOW,
    )

    assert result["status"] == "dry_run"
    assert client.calls == []
    assert read_table(sandbox_repository, "youtube_channels") == before
    assert read_table(sandbox_repository, "operations_todo") == []


def test_discovery_client_prefers_nonempty_data_api_key() -> None:
    assert isinstance(youtube_discovery_client({}), PytubefixDiscoveryClient)
    assert isinstance(
        youtube_discovery_client({"YOUTUBE_DATA_API": "   "}), PytubefixDiscoveryClient
    )
    assert isinstance(
        youtube_discovery_client({"YOUTUBE_DATA_API": "api-key"}),
        YouTubeDataAPIClient,
    )


def test_data_api_preserves_upload_order_and_filters_short_and_live_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    channel_id = CURATED_CHANNELS["@allin"]
    video_ids = ["regular0001", "short000001", "live0000001", "replay00001"]
    responses: dict[str, object] = {
        "channels": {
            "items": [
                {
                    "id": channel_id,
                    "contentDetails": {"relatedPlaylists": {"uploads": "uploads-id"}},
                }
            ]
        },
        "playlistItems": {
            "items": [{"contentDetails": {"videoId": video_id}} for video_id in video_ids]
        },
        "videos": {
            "items": [
                {
                    "id": "replay00001",
                    "snippet": {"title": "Replay", "liveBroadcastContent": "none"},
                    "contentDetails": {"duration": "PT2H"},
                    "liveStreamingDetails": {"actualStartTime": "2026-07-01T10:00:00Z"},
                },
                {
                    "id": "live0000001",
                    "snippet": {"title": "Live", "liveBroadcastContent": "live"},
                    "contentDetails": {"duration": "PT20M"},
                },
                {
                    "id": "short000001",
                    "snippet": {"title": "Three minutes", "liveBroadcastContent": "none"},
                    "contentDetails": {"duration": "PT3M"},
                },
                {
                    "id": "regular0001",
                    "snippet": {
                        "title": "Three minutes one second",
                        "liveBroadcastContent": "none",
                    },
                    "contentDetails": {"duration": "PT3M1S"},
                },
            ]
        },
    }
    requested_endpoints: list[str] = []

    class Response:
        def __init__(self, payload: object) -> None:
            self.payload = payload

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(self.payload).encode()

    def fake_urlopen(request: Request, *, timeout: int) -> Response:
        assert timeout == 30
        parsed = urlsplit(request.full_url)
        endpoint = parsed.path.rsplit("/", 1)[-1]
        parameters = parse_qs(parsed.query)
        assert parameters["key"] == ["api-key"]
        requested_endpoints.append(endpoint)
        return Response(responses[endpoint])

    monkeypatch.setattr(youtube_module, "urlopen", fake_urlopen)
    feed = YouTubeDataAPIClient("api-key").channel_feed(
        "@allin",
        channel_id=channel_id,
        limit=4,
    )

    assert requested_endpoints == ["channels", "playlistItems", "videos"]
    assert [entry.video_id for entry in feed.entries] == video_ids
    assert [entry.kind for entry in feed.entries] == [
        "regular",
        "short",
        "livestream",
        "livestream",
    ]


def test_data_api_failure_is_redacted_and_does_not_fall_back(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_channels(sandbox_repository)
    secret = "youtube-secret-value"

    def fail_request(request: Request, *, timeout: int) -> object:
        del timeout
        raise HTTPError(request.full_url, 403, "forbidden", {}, None)

    monkeypatch.setattr(youtube_module, "urlopen", fail_request)
    result = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-api-failure",
        environment={"YOUTUBE_DATA_API": secret},
        now=NOW,
    )

    assert result["status"] == "degraded"
    assert result["failure_count"] == 6
    assert result["discovery_provider"] == "youtube_data_api"
    assert result["regular_video_policy"] == "non_live_duration_over_180_seconds"
    assert secret not in json.dumps(result)
    assert all(secret not in row["description"] for row in read_table(sandbox_repository, "issues"))


def test_registered_source_deduplicates_by_immutable_video_id(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds(videos_per_channel=5)
    first_handle = sorted(CURATED_CHANNELS)[0]
    video_id = feeds[first_handle].entries[0].video_id
    video_url = canonical_video_url(video_id)
    write_table(
        sandbox_repository,
        "source_registry",
        [
            {
                "source_id": youtube_source_id(video_id),
                "url": video_url,
                "canonical_url": video_url,
                "source_type": "youtube_video",
                "title": "Already reviewed",
                "publisher": first_handle,
                "license": "copyrighted-transcript-not-stored",
                "status": "available",
                "content_hash": "a" * 64,
                "first_seen_at": "2026-07-28T08:00:00Z",
                "last_checked_at": "2026-07-28T08:00:00Z",
                "last_changed_at": "2026-07-28T08:00:00Z",
                "related_entity_ids": "",
            }
        ],
    )

    result = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-source-dedupe",
        client=FakeDiscovery(feeds),
        now=NOW,
    )

    assert result["operation_count"] == 29
    outcome = next(row for row in result["channels"] if row["handle"] == first_handle)
    assert outcome["duplicate_video_ids"] == [video_id]


def test_backfill_queues_exactly_twenty_older_allin_videos_without_advancing_cursor(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds(videos_per_channel=30)
    scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-seed-before-backfill",
        client=FakeDiscovery(feeds),
        now=NOW,
    )
    allin_id = CURATED_CHANNELS["@allin"]
    cursor_before = next(
        row["last_seen_video_id"]
        for row in read_table(sandbox_repository, "youtube_channels")
        if row["channel_id"] == allin_id
    )

    result = backfill_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id="youtube-allin-backfill",
        channel_id=allin_id,
        count=20,
        client=FakeDiscovery(feeds),
        now=NOW + timedelta(hours=1),
    )

    rows = [
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["source"] == "youtube_backfill:youtube-allin-backfill"
    ]
    assert result["status"] == "succeeded"
    assert result["operation_count"] == 20
    assert len(rows) == 20
    assert {row["priority"] for row in rows} == {"60"}
    assert all(
        json.loads((sandbox_repository / row["payload_path"]).read_text(encoding="utf-8"))[
            "inputs"
        ]["discovery_mode"]
        == "backfill"
        for row in rows
    )
    cursor_after = next(
        row["last_seen_video_id"]
        for row in read_table(sandbox_repository, "youtube_channels")
        if row["channel_id"] == allin_id
    )
    assert cursor_after == cursor_before
    target = next(row for row in result["channels"] if row["channel_id"] == allin_id)
    assert len(target["duplicate_video_ids"]) == 4
    assert all(
        row["reason"] == "not_selected_for_backfill"
        for row in result["channels"]
        if row["channel_id"] != allin_id
    )


def test_existing_scan_manifest_skips_backfill_without_discovery(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _seed_channels(sandbox_repository)
    feeds = _feeds(videos_per_channel=30)
    discovery = FakeDiscovery(feeds)
    run_id = "youtube-repeat-backfill"
    scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        client=discovery,
        now=NOW,
    )
    manifest_path = sandbox_repository / "data" / "runs" / run_id / "youtube_scan.json"
    manifest_before = manifest_path.read_bytes()
    operations_before = read_table(sandbox_repository, "operations_todo")
    discovery.calls.clear()

    repeated = backfill_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        channel_id=CURATED_CHANNELS["@allin"],
        count=20,
        client=discovery,
        now=NOW + timedelta(hours=1),
    )

    assert repeated["status"] == "skipped"
    assert repeated["reason"] == "manifest_already_exists"
    assert discovery.calls == []
    assert manifest_path.read_bytes() == manifest_before
    assert read_table(sandbox_repository, "operations_todo") == operations_before

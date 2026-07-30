from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from papertrader.atomic_io import atomic_write_text
from papertrader.config import Settings
from papertrader.daily import execute_agent_batch, finalize_daily_run, prepare_daily_run
from papertrader.integrity import is_runtime_path_allowed, validate_integrity
from papertrader.market_data import write_price_cache
from papertrader.models import PriceBar
from papertrader.queue import Operation, enqueue_operation
from papertrader.research import import_watchlist, record_source
from papertrader.result_validator import _youtube_wiki_ingest_errors
from papertrader.tables import read_table, write_table
from papertrader.wiki import lint_wiki
from papertrader.youtube import CURATED_CHANNELS, YouTubeFeed, YouTubeVideo, scan_youtube

NOW = datetime(2026, 7, 29, 22, tzinfo=UTC)
RUN_ID = "youtube-integration-cycle"


class _Discovery:
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
        del (
            minimum_regular,
            stop_at_video_id,
            anchor_video_id,
            minimum_regular_after_anchor,
        )
        assert channel_id == CURATED_CHANNELS[handle]
        channel_number = sorted(CURATED_CHANNELS).index(handle) + 1
        entries = tuple(
            YouTubeVideo(f"{channel_number * 100 + index:011d}", f"Video {index}")
            for index in range(1, 6)
        )
        return YouTubeFeed(channel_id, entries[:limit])


def _seed_channels(repository: Path) -> None:
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
                "last_seen_video_id": "",
            }
            for handle, channel_id in sorted(CURATED_CHANNELS.items(), key=lambda item: item[1])
        ],
    )


def test_curated_youtube_ingest_cycle_stays_research_only_and_reproducible(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    _seed_channels(sandbox_repository)
    scan = scan_youtube(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        client=_Discovery(),
        now=NOW,
    )
    assert scan["operation_count"] == 30

    ingest_row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["source"] == f"youtube_scan:{RUN_ID}"
    )
    ingest = Operation.from_row(ingest_row)
    payload = json.loads((sandbox_repository / ingest.payload_path).read_text(encoding="utf-8"))
    inputs = payload["inputs"]
    video_url = inputs["video_url"]
    transcript_hash = "b" * 64
    operation_ids_before = {
        row["operation_id"] for row in read_table(sandbox_repository, "operations_todo")
    }

    history_id, source_changed = record_source(
        sandbox_repository,
        {
            "source_id": inputs["source_id"],
            "url": video_url,
            "canonical_url": video_url,
            "source_type": "youtube_video",
            "title": inputs["video_title"],
            "publisher": inputs["channel_handle"],
            "license": "copyrighted-transcript-not-stored",
            "status": "available",
            "content_hash": transcript_hash,
            "related_entity_ids": "",
            "checked_at": "2026-07-29T22:00:00Z",
            "http_status": "200",
            "changed": "true",
            "excerpt": "",
            "summary": "One transcript was reviewed as an untrusted source of leads.",
            "run_id": RUN_ID,
        },
        now=NOW,
    )
    assert source_changed
    assert history_id

    imported = import_watchlist(
        sandbox_repository,
        sandbox_settings,
        {
            "watchlist_reason": (
                "A material causal hypothesis survived independent issuer-identity checks."
            ),
            "source": video_url,
            "securities": [
                {
                    "company_name": "Verified Lead Corporation",
                    "instrument_name": "Verified Lead common stock",
                    "instrument_type": "equity",
                    "ticker": "VLDC",
                    "exchange_code": "XNAS",
                    "venue_mic": "XNAS",
                    "provider_symbol": "VLDC",
                    "currency": "USD",
                    "country": "US",
                    "sector": "Industrials",
                    "industry": "Research fixture",
                }
            ],
        },
        now=NOW,
    )
    security_id = imported["created_security_ids"][0]
    write_price_cache(
        sandbox_repository,
        security_id,
        (
            PriceBar(
                date=NOW.date(),
                open=Decimal("10"),
                high=Decimal("11"),
                low=Decimal("9"),
                close=Decimal("10"),
                adjusted_close=Decimal("10"),
                volume=1000,
                dividends=Decimal("0"),
                stock_splits=Decimal("0"),
                currency="USD",
                provider_symbol="VLDC",
                retrieved_at=NOW,
                source="integration-fixture",
            ),
        ),
    )
    followup_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id=security_id,
        dedupe_key=f"security_research:{security_id}:youtube:{inputs['video_id']}",
        prompt="Verify and value one identity-resolved security lead.",
        inputs={"security_id": security_id},
        source=f"youtube_ingest:{ingest.operation_id}",
        priority=66,
        depends_on=(ingest.operation_id,),
        source_refs=(video_url, "https://www.sec.gov/edgar/search/"),
        now=NOW,
    )
    assert created

    analysis_relative = f"data/runs/{RUN_ID}/{ingest.operation_id}/youtube_analysis.md"
    (sandbox_repository / analysis_relative).parent.mkdir()
    atomic_write_text(
        sandbox_repository / analysis_relative,
        (
            "# Curated YouTube analysis\n\n"
            f"Video ID: `{inputs['video_id']}`\n\n"
            f"Canonical URL: {video_url}\n\n"
            f"Canonical transcript SHA-256: `{transcript_hash}`\n\n"
            "The transcript supplied a hypothesis only. The retained issuer identity was "
            "checked independently; no assessment, strategy, signal, allocation, or order was "
            "changed.\n"
        ),
        allowed_root=sandbox_repository,
    )
    rows_after = {
        row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")
    }
    created_operation_ids = set(rows_after) - operation_ids_before
    changed_paths = (
        analysis_relative,
        "data/market/prices/" + security_id + ".csv",
        "data/operations/payloads/" + followup_id + ".json",
        "data/operations/operations_TODO.csv",
        "data/tables/securities.csv",
        "data/tables/source_history.csv",
        "data/tables/source_registry.csv",
    )
    assert created_operation_ids == {followup_id}
    assert (
        _youtube_wiki_ingest_errors(
            sandbox_repository,
            run_id=RUN_ID,
            operation=ingest,
            status="succeeded",
            result={"status": "succeeded"},
            changed_paths=changed_paths,
            created_operation_ids=created_operation_ids,
            operation_rows_after=rows_after,
            followup_priority=66,
        )
        == []
    )
    assert all(is_runtime_path_allowed(path) for path in changed_paths)
    assert read_table(sandbox_repository, "strategies") == []
    assert read_table(sandbox_repository, "signals") == []
    assert read_table(sandbox_repository, "orders") == []
    assert not any(
        inputs["video_id"] in path.name
        for path in (sandbox_repository / "data" / "wiki").rglob("*.md")
    )

    preparation = prepare_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        trigger="integration",
        source_sha="a" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )
    execute_agent_batch(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        hermes_home=tmp_path / "unused-hermes",
        environment={"PATH": "/usr/bin"},
        maximum_operations=0,
        now=NOW,
    )
    finalization = finalize_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        github_report_url=(
            "https://github.com/example/PaperTrader/blob/main/"
            "data/wiki/daily-reports/daily-report_20260729.md"
        ),
        now=NOW,
    )
    report = (sandbox_repository / finalization.report_path).read_text(encoding="utf-8")
    assert preparation.errors == ()
    assert "### Curated YouTube discovery" in report
    assert "Operations queued: `30`" in report
    assert lint_wiki(sandbox_repository / "data" / "wiki") == []
    assert (
        validate_integrity(
            sandbox_repository,
            {
                "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
            },
        )
        == []
    )

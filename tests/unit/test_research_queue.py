from __future__ import annotations

import copy
import csv
import io
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from papertrader.research_migration import prepare_migration
from papertrader.research_queue import (
    QueueLimits,
    admit,
    claim,
    finish,
    rebuild_legacy_queue,
    recover,
    schedule_attention,
)
from papertrader.research_state import ResearchState, validate_state

NOW = datetime(2026, 10, 18, 17, tzinfo=UTC)
BASELINE = "9056d3dff03740a6c3310e086a240186bca4527a"


@pytest.fixture
def state() -> ResearchState:
    return {
        "securities": [
            dict(
                security_id=f"s{i:02}",
                issuer_id=f"issuer{i:02}",
                status="active",
                research_status="unresearched",
                last_research_at="",
            )
            for i in range(40)
        ],
        "ideas": [dict(idea_id="idea1", status="unresearched")],
        "security_assessments": [],
        "source_registry": [],
        "relationships": [],
        "research_queue": [],
    }


def add(state: ResearchState, sid: str = "s00", **kwargs: object) -> str:
    return admit(
        state, "security", sid, reasons={"research_overdue"}, priority=60, now=NOW, **kwargs
    )  # type: ignore[arg-type]


def test_company_dedupe_reason_merge_and_identical_observation_no_write(
    state: ResearchState,
) -> None:
    state["securities"][1]["issuer_id"] = "issuer00"
    assert add(state) == "admitted"
    assert admit(state, "security", "s01", reasons={"price_move"}, priority=80, now=NOW) == "merged"
    row = state["research_queue"][0]
    assert row["entity_id"] == "s00"
    assert row["reasons"] == "price_move|research_overdue"
    assert row["priority"] == "80"
    before = copy.deepcopy(state)
    admit(
        state, "security", "s01", reasons={"price_move"}, priority=80, now=NOW + timedelta(days=1)
    )
    assert state == before
    assert len(state["securities"]) == 40


def test_capacity_and_manual_requests_never_silently_disappear(state: ResearchState) -> None:
    for i in range(30):
        add(state, f"s{i:02}")
    assert add(state, "s30") == "catalog_only"
    assert len(state["research_queue"]) == 30
    assert add(state, "s30", manual=True) == "admitted"
    assert len(state["research_queue"]) == 30
    assert any(
        row["entity_id"] == "s30" and row["manual"] == "true" for row in state["research_queue"]
    )
    assert not any(row["status"] == "blocked" for row in state["research_queue"])
    assert len(state["securities"]) == 40
    state["research_queue"].clear()
    for i in range(30):
        add(state, f"s{i:02}", manual=True)
    with pytest.raises(ValueError, match="not accepted"):
        add(state, "s30", manual=True)


def test_material_new_work_displaces_ordinary_backlog(state: ResearchState) -> None:
    for i in range(30):
        add(state, f"s{i:02}")
    assert (
        admit(state, "security", "s31", reasons={"material_evidence"}, priority=90, now=NOW)
        == "admitted"
    )
    assert any(row["entity_id"] == "s31" for row in state["research_queue"])


def test_bounded_retries_do_not_starve_other_companies(state: ResearchState) -> None:
    add(state, manual=True)
    add(state, "s01")
    original = copy.deepcopy(state["security_assessments"])
    task = claim(state, now=NOW)
    assert task and task["entity_id"] == "s00"
    assert claim(state, now=NOW) is None
    assert finish(state, task, now=NOW, error="invalid_citation") == "retry_scheduled"
    unrelated = claim(state, now=NOW)
    assert unrelated and unrelated["entity_id"] == "s01"
    finish(state, unrelated, now=NOW)
    assert claim(state, now=NOW) is None
    retry = claim(state, now=NOW + timedelta(hours=6))
    assert retry and retry["entity_id"] == "s00"
    assert (
        finish(state, retry, now=NOW + timedelta(hours=6), error="invalid_citation")
        == "needs_attention"
    )
    assert state["research_queue"] == []
    assert state["securities"][0]["research_status"] == "needs_attention"
    assert state["security_assessments"] == original
    schedule_attention(state, [], [], now=NOW + timedelta(days=1))
    assert all(row["entity_id"] != "s00" for row in state["research_queue"])


def test_explicit_manual_retry_bypasses_backoff_without_resetting_attempts(
    state: ResearchState,
) -> None:
    add(state, manual=True)
    task = claim(state, now=NOW)
    assert task
    assert finish(state, task, now=NOW, error="validation:ValueError:papertrader.module.fn:1") == (
        "retry_scheduled"
    )
    failed = state["research_queue"][0]
    assert failed["attempts"] == "1"
    delayed_until = failed["next_eligible_at"]

    admit(state, "security", "s00", reasons={"automatic"}, priority=90, now=NOW)
    assert failed["status"] == "failed"
    assert failed["next_eligible_at"] == delayed_until

    assert add(state, manual=True) == "merged"
    assert failed["status"] == "pending"
    assert failed["next_eligible_at"] == "2026-10-18T17:00:00Z"
    assert failed["attempts"] == "1"
    retry = claim(state, now=NOW)
    assert retry and retry["attempts"] == "2"


def test_expired_lease_recovers_and_old_owner_cannot_finish(state: ResearchState) -> None:
    add(state)
    first = claim(state, now=NOW)
    assert first
    recover(state, now=NOW + timedelta(minutes=16))
    second = claim(state, now=NOW + timedelta(minutes=16))
    assert second and second["attempts"] == "2"
    with pytest.raises(ValueError, match="owned"):
        finish(state, first, now=NOW + timedelta(minutes=16))
    recover(state, now=NOW + timedelta(minutes=32))
    assert not state["research_queue"]
    assert state["securities"][0]["research_status"] == "needs_attention"


def test_daily_selection_has_three_attempt_budget(state: ResearchState) -> None:
    schedule_attention(state, [], [], now=NOW)
    excluded: set[tuple[str, str]] = set()
    for _ in range(QueueLimits().max_daily_operations):
        task = claim(state, now=NOW, excluded=excluded)
        assert task
        excluded.add((task["entity_type"], task["entity_id"]))
        finish(state, task, now=NOW, error="offline")
    assert len(excluded) == 3
    assert sum(row["attempts"] == "1" for row in state["research_queue"]) == 3


def test_many_indicators_and_classes_produce_one_company_task(state: ResearchState) -> None:
    state["securities"] = state["securities"][:2]
    state["securities"][1]["issuer_id"] = "issuer00"
    observations = [
        dict(
            security_id=sid,
            price_date="2026-10-16",
            change_1d_pct="-10",
            change_5d_pct="-20",
            rsi_14="20",
            sma_200="100",
        )
        for sid in ("s00", "s01")
    ]
    schedule_attention(state, observations, [], now=NOW, material_entities={("security", "s01")})
    assert len(state["research_queue"]) == 1
    row = state["research_queue"][0]
    assert row["priority"] == "90"
    assert set(row["reasons"].split("|")) == {
        "unresearched_candidate",
        "severe_price_movement",
        "material_technical_context",
        "verified_material_evidence",
    }
    assert "alert" not in str(state)
    # Same current features after completion cannot replay their technical/price cause.
    task = claim(state, now=NOW)
    assert task
    finish(state, task, now=NOW)
    schedule_attention(state, observations, observations, now=NOW)
    assert state["research_queue"][0]["reasons"] == "unresearched_candidate"


def test_recent_review_avoids_daily_unsupported_research_loop(state: ResearchState) -> None:
    state["securities"] = state["securities"][:1]
    state["securities"][0]["last_research_at"] = "2026-10-18T16:00:00Z"
    schedule_attention(state, [], [], now=NOW)
    assert not state["research_queue"]


def test_real_census_accounts_for_all_old_rows_without_replaying_blocks(
    repository_root: Path,
) -> None:
    state, pages, _ = prepare_migration(repository_root, BASELINE)
    raw = subprocess.check_output(
        ["git", "show", f"{BASELINE}:data/operations/operations_TODO.csv"], cwd=repository_root
    )
    legacy = list(csv.DictReader(io.StringIO(raw.decode())))
    report = rebuild_legacy_queue(state, legacy, now=NOW)
    assert report["legacy_rows"] == sum(report["dispositions"].values()) == 648
    assert report["dispositions"]["capacity_not_replayed"] == 320
    assert report["blocked_reasons"] == {
        "scope_deferred_for_capacity": 320,
        "agent_result:blocked": 15,
        "dependency_unavailable": 5,
    }
    assert report["waiting_relationships"] == 13
    assert report["manual_entities"] == 3
    assert report["new_pending"] == 30
    assert sum(row["manual"] == "true" for row in state["research_queue"]) == 3
    assert all(
        row["status"] == "pending" and row["attempts"] == "0" for row in state["research_queue"]
    )
    assert all(
        "operation_id" not in row and "depends_on" not in row for row in state["research_queue"]
    )
    assert validate_state(repository_root, state, pages=pages) == []
    # The selected queue is deterministic for identical evidence and as-of time.
    again, _, _ = prepare_migration(repository_root, BASELINE)
    assert rebuild_legacy_queue(again, legacy, now=NOW) == report
    assert again["research_queue"] == state["research_queue"]


def test_legacy_blocked_census_discards_detailed_suffixes(state: ResearchState) -> None:
    legacy = [
        {
            "status": "blocked",
            "last_error": error,
            "operation_type": "opportunity_research",
            "source": "daily",
        }
        for error in (
            "scope_deferred_for_capacity:detail",
            "agent_result:blocked:detailed prose must not enter the compact census",
            "dependency_unavailable:01LEGACYOPERATION",
        )
    ]
    report = rebuild_legacy_queue(state, legacy, now=NOW)
    assert report["blocked_reasons"] == {
        "scope_deferred_for_capacity": 1,
        "agent_result:blocked": 1,
        "dependency_unavailable": 1,
    }
    assert "detailed prose" not in str(report)
    assert "01LEGACYOPERATION" not in str(report)


def test_queue_validation_rejects_corrupt_and_duplicate_company_tasks(
    repository_root: Path,
) -> None:
    state, pages, _ = prepare_migration(repository_root, BASELINE)
    sid = state["securities"][0]["security_id"]
    admit(state, "security", sid, reasons={"manual_review"}, priority=100, now=NOW)
    state["research_queue"][0]["attempts"] = "-1"
    assert validate_state(repository_root, state, pages=pages)

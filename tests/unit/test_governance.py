from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from papertrader.governance import (
    GovernanceError,
    admission_reason,
    record_topic,
    topics,
    validate_governance,
)
from papertrader.queue import enqueue_operation
from papertrader.tables import read_table, write_table

NOW = datetime(2026, 7, 24, 10, tzinfo=UTC)


def topic(topic_id="anchor", scope="user_directed", **changes):
    return {
        "topic_id": topic_id,
        "entity_type": "idea",
        "entity_id": topic_id,
        "scope_class": scope,
        "anchor_ids": [],
        "parent_ids": [],
        "contributions": [],
        "lifecycle": "active",
        "reason": "explicit_tracking" if scope == "user_directed" else "bounded_exploration",
        "summary": "A bounded topic with retained uncertainty.",
        "evidence_refs": [],
        "reactivation_conditions": [],
        "user_request_ref": "manual:track:fixture" if scope == "user_directed" else "",
        "review_at": None,
        **changes,
    }


def test_only_explicit_tracking_creates_anchor(sandbox_repository):
    with pytest.raises(GovernanceError, match="explicit manual tracking"):
        record_topic(sandbox_repository, topic())
    version = record_topic(sandbox_repository, topic(), manual_tracking=True, now=NOW)
    assert record_topic(sandbox_repository, topic(), manual_tracking=True, now=NOW) == version
    assert (
        len(
            list((sandbox_repository / "data/operations/research-governance/topics").glob("*.json"))
        )
        == 1
    )
    assert validate_governance(sandbox_repository) == []


def test_adjacent_cannot_rebase_through_adjacent(sandbox_repository):
    record_topic(sandbox_repository, topic(), manual_tracking=True, now=NOW)
    direct = topic(
        "supplier",
        "directly_adjacent",
        anchor_ids=["anchor"],
        parent_ids=["anchor"],
        contributions=[
            {
                "anchor_id": "anchor",
                "mechanism": "Material production bottleneck constrains demand capture",
                "evidence_refs": ["fixture:primary"],
            }
        ],
    )
    record_topic(sandbox_repository, direct, now=NOW)
    indirect = {
        **direct,
        "topic_id": "subsupplier",
        "entity_id": "subsupplier",
        "anchor_ids": ["supplier"],
        "parent_ids": ["supplier"],
        "contributions": [{**direct["contributions"][0], "anchor_id": "supplier"}],
    }
    with pytest.raises(GovernanceError, match="rebase"):
        record_topic(sandbox_repository, indirect, now=NOW)


def test_peripheral_cannot_spawn_but_protected_child_survives(sandbox_repository, sandbox_settings):
    record_topic(sandbox_repository, topic("edge", "peripheral"), now=NOW)
    parent, _ = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="idea_research",
        entity_type="idea",
        entity_id="edge",
        dedupe_key="edge",
        prompt="Bounded edge",
        inputs={"idea_id": "edge", "seed_claim": "fixture"},
        source="fixture",
        now=NOW,
    )
    child, _ = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec_child",
        dedupe_key="child",
        prompt="Child",
        inputs={"security_id": "sec_child"},
        depends_on=(parent,),
        source="calendar",
        now=NOW,
    )
    row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == child
    )
    assert row["status"] == "blocked" and row["last_error"] == "scope_peripheral_terminal"
    # Protection is derived from canonical live strategy state, not a payload label.
    from test_execution_accounting import _strategy_row

    strategy = _strategy_row("active")
    strategy.update(status="active", security_id="sec_child")
    write_table(sandbox_repository, "strategies", [strategy])
    assert (
        admission_reason(
            sandbox_repository, entity_type="security", entity_id="sec_child", parent_ids=(parent,)
        )
        == ""
    )


def test_archive_retains_history_and_reading_does_not_reactivate(sandbox_repository):
    original = topic("old", "peripheral")
    first = record_topic(sandbox_repository, original, now=NOW)
    archived = {
        **original,
        "lifecycle": "archived",
        "reason": "unattractive_valuation",
        "summary": " ".join(
            ["Evidence and uncertainty remain preserved for a future bounded reconsideration."] * 11
        ),
        "reactivation_conditions": ["New evidence or a sufficient price change"],
    }
    record_topic(sandbox_repository, archived, now=NOW)
    assert (
        sandbox_repository / f"data/operations/research-governance/topics/{first}.json"
    ).exists()
    assert topics(sandbox_repository)["old"]["topic"]["lifecycle"] == "archived"
    assert (
        admission_reason(sandbox_repository, entity_type="idea", entity_id="old")
        == "scope_archived_requires_reactivation"
    )
    with pytest.raises(GovernanceError, match="retrieval alone"):
        record_topic(sandbox_repository, original, now=NOW)


def test_security_deltas_coalesce_without_losing_results(sandbox_repository, sandbox_settings):
    results = []
    for index, source_id in enumerate(["01K0AAAAAA0000000000000001", "01K0AAAAAA0000000000000002"]):
        operation_id, _ = enqueue_operation(
            sandbox_repository,
            sandbox_settings,
            operation_type="idea_research",
            entity_type="idea",
            entity_id="idea_delta",
            dedupe_key=f"delta:{source_id}",
            prompt="Apply security delta",
            inputs={
                "idea_id": "idea_delta",
                "seed_claim": "Maintained thesis",
                "security_id": f"sec_{index}",
                "security_research_operation_id": source_id,
                "security_research_result_path": f"data/runs/fixture/{source_id}/agent_result.json",
            },
            depends_on=(source_id,),
            source="research",
            now=NOW,
        )
        results.append(operation_id)
    assert results[0] == results[1]
    row = read_table(sandbox_repository, "operations_todo")[0]
    payload = json.loads((sandbox_repository / row["payload_path"]).read_text())
    assert payload["inputs"]["review_mode"] == "delta"
    assert len(payload["inputs"]["security_deltas"]) == 2
    assert len(row["depends_on"].split("|")) == 2

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.config import Settings
from papertrader.profiles import select_profile
from papertrader.queue import Operation, QueueError, enqueue_operation
from papertrader.tables import read_table
from papertrader.triage import apply_triage_result

NOW = datetime(2026, 9, 11, 12, tzinfo=UTC)


def test_triage_rejects_a_different_payload_security(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    with pytest.raises(QueueError, match="security identity"):
        enqueue_operation(
            sandbox_repository,
            sandbox_settings,
            operation_type="research_triage",
            entity_type="security",
            entity_id="security_a",
            dedupe_key="triage:mismatch",
            prompt="Inspect the named security.",
            inputs={
                "security_id": "security_b",
                "investigation_id": "mismatch",
                "cause": "Test mismatch",
                "evidence_refs": ["https://example.com/filing"],
            },
            source="manual",
            now=NOW,
        )
    assert read_table(sandbox_repository, "operations_todo") == []


def _triage(root: Path, settings: Settings) -> Operation:
    operation_id, _ = enqueue_operation(
        root,
        settings,
        operation_type="research_triage",
        entity_type="security",
        entity_id="security_example",
        dedupe_key="triage:example:filing-v2",
        prompt="Check a filing amendment.",
        inputs={
            "security_id": "security_example",
            "investigation_id": "filing-v2",
            "cause": "A material amendment was published.",
            "evidence_refs": ["https://example.com/filing"],
        },
        source="manual",
        priority=70,
        now=NOW,
    )
    return Operation.from_row(
        next(
            row
            for row in read_table(root, "operations_todo")
            if row["operation_id"] == operation_id
        )
    )


def test_triage_routes_luna_and_escalates_uncertainty_once(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation = _triage(sandbox_repository, sandbox_settings)
    profile, _ = select_profile(sandbox_repository, sandbox_settings, operation)
    assert profile.model == "gpt-5.6-luna"
    result: dict[str, object] = {
        "triage_review": {
            "disposition": "uncertain",
            "reason": "Cannot inspect the amended segment note.",
            "examined_evidence": [],
        }
    }
    path = f"data/runs/triage/{operation.operation_id}/agent_result.json"
    first = apply_triage_result(
        sandbox_repository, sandbox_settings, operation, result, result_path=path, now=NOW
    )
    second = apply_triage_result(
        sandbox_repository, sandbox_settings, operation, result, result_path=path, now=NOW
    )
    assert first == second
    rows = read_table(sandbox_repository, "operations_todo")
    followups = [row for row in rows if row["operation_type"] == "security_research"]
    assert len(followups) == 1
    assert followups[0]["depends_on"] == operation.operation_id
    assert followups[0]["priority"] == "70"
    assert read_table(sandbox_repository, "security_assessments") == []
    assert read_table(sandbox_repository, "orders") == []


def test_no_change_check_does_not_publish_an_assessment(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation = _triage(sandbox_repository, sandbox_settings)
    result: dict[str, object] = {
        "triage_review": {
            "disposition": "no_material_change",
            "reason": "Only filing typography changed.",
            "examined_evidence": ["https://example.com/filing"],
        }
    }
    assert (
        apply_triage_result(
            sandbox_repository, sandbox_settings, operation, result, result_path="unused", now=NOW
        )
        is None
    )
    assert len(read_table(sandbox_repository, "operations_todo")) == 1
    assert read_table(sandbox_repository, "security_assessment_history") == []

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from test_execution_accounting import _security_row, _strategy_row

from papertrader.atomic_io import atomic_write_json, atomic_write_text
from papertrader.findings import pending_findings, prepare_finding_appendix, record_finding_coverage
from papertrader.governance import GovernanceError
from papertrader.monitoring import (
    monitoring_context,
    schedule_monitoring,
    validate_monitoring_result,
)
from papertrader.queue import Operation
from papertrader.tables import append_unique, contract_by_name, read_table, write_table
from papertrader.triage import apply_triage_result

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def monitored(root, settings):
    from papertrader.hardening import migrate

    migrate(root, settings, now=NOW, apply=True)
    write_table(root, "securities", [_security_row()])
    strategy = _strategy_row("active")
    strategy["status"] = "active"
    write_table(root, "strategies", [strategy])
    ids = schedule_monitoring(root, settings, run_id="monitor", now=NOW)
    assert len(ids) == 1
    operation = Operation.from_row(read_table(root, "operations_todo")[0])
    context = monitoring_context(root, operation)
    assert context is not None
    result = {
        "status": "succeeded",
        "triage_review": {
            "disposition": "no_material_change",
            "reason": "Bounded sources checked",
            "examined_evidence": ["https://example.test/primary"],
        },
        "monitoring_review": {
            "context_hash": context["context_hash"],
            "checks": [
                {
                    "target_id": row["target_id"],
                    "state": "checked_no_change",
                    "checked_at": "2026-07-24T12:00:00Z",
                    "source_hash": "a" * 64,
                    "evidence_refs": ["https://example.test/primary"],
                    "reason": "Inspected the bounded primary source",
                }
                for row in context["targets"]
            ],
            "conflicts": [],
            "limitations": ["Not complete universe coverage"],
        },
    }
    return operation, result


def test_monitoring_is_bounded_and_idempotent(sandbox_repository, sandbox_settings):
    operation, result = monitored(sandbox_repository, sandbox_settings)
    ids = schedule_monitoring(sandbox_repository, sandbox_settings, run_id="monitor", now=NOW)
    assert ids == (operation.operation_id,)
    receipt = validate_monitoring_result(sandbox_repository, operation, result, now=NOW)
    assert receipt["checked_count"] == receipt["target_count"] == 1
    assert len(read_table(sandbox_repository, "operations_todo")) == 1


@pytest.mark.parametrize("state", ["reserved", "failed", "partial"])
def test_failed_or_reserved_search_never_counts_as_no_update(
    sandbox_repository, sandbox_settings, state
):
    operation, result = monitored(sandbox_repository, sandbox_settings)
    result["monitoring_review"]["checks"][0]["state"] = state
    with pytest.raises(GovernanceError, match="cannot establish no change"):
        validate_monitoring_result(sandbox_repository, operation, result, now=NOW)
    result["triage_review"]["disposition"] = "uncertain"
    receipt = validate_monitoring_result(sandbox_repository, operation, result, now=NOW)
    assert receipt["checked_count"] == 0 and not receipt["complete_no_change"]


def test_successful_protected_nochange_monitor_does_not_refresh_assessment(
    sandbox_repository, sandbox_settings
):
    operation, result = monitored(sandbox_repository, sandbox_settings)
    before = read_table(sandbox_repository, "security_assessments")
    assert (
        apply_triage_result(
            sandbox_repository,
            sandbox_settings,
            operation,
            result,
            result_path=f"data/runs/monitor/{operation.operation_id}/agent_result.json",
            now=NOW,
        )
        is None
    )
    assert read_table(sandbox_repository, "security_assessments") == before
    assert len(read_table(sandbox_repository, "operations_todo")) == 1


def test_omitted_finding_remains_reportable_and_saved_is_not_delivery(sandbox_repository):
    operation_id = "01K0AAAAAA0000000000000001"
    result_path = f"data/runs/original/{operation_id}/agent_result.json"
    destination = sandbox_repository / result_path
    destination.parent.mkdir(parents=True)
    atomic_write_json(
        destination,
        {
            "summary": "Research",
            "daily_report_items": ["First original finding", "Second original finding"],
        },
        allowed_root=sandbox_repository,
    )
    row = {key: "" for key in contract_by_name(sandbox_repository, "operations_history").columns}
    row.update(
        operation_id=operation_id,
        operation_type="idea_research",
        entity_type="idea",
        entity_id="idea_test",
        terminal_status="succeeded",
        completed_at="2026-07-24T11:00:00Z",
        result_path=result_path,
    )
    assert (
        append_unique(
            sandbox_repository,
            "operations_history",
            [row],
            key_columns=("operation_id",),
        )
        == 1
    )
    section, ids, appendix = prepare_finding_appendix(
        sandbox_repository, run_id="report", report_date=NOW.date(), as_of=NOW, maximum_findings=1
    )
    assert (
        len(ids) == 1
        and len(pending_findings(sandbox_repository, report_date=NOW.date(), as_of=NOW)) == 2
    )
    report = sandbox_repository / "data/wiki/daily-reports/fixture.md"
    atomic_write_text(report, "\n".join(section), allowed_root=sandbox_repository)
    record_finding_coverage(
        sandbox_repository,
        run_id="report",
        report_date=NOW.date(),
        report_path=report,
        finding_ids=ids,
        appendix_path=appendix,
    )
    tomorrow = NOW + timedelta(days=1)
    assert (
        len(pending_findings(sandbox_repository, report_date=tomorrow.date(), as_of=tomorrow)) == 1
    )
    from papertrader.governance import load_record

    receipt = load_record(
        sandbox_repository, sandbox_repository / "data/runs/report/finding_coverage.json"
    )
    assert (
        receipt["saved"]
        and receipt["delivery"] == "not_attested_here"
        and receipt["user_observed"] is False
    )

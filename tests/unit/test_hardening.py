from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from papertrader.atomic_io import atomic_write_json
from papertrader.governance import GovernanceError
from papertrader.hardening import POLICY_PATH, migrate, policy, validate_hardening
from papertrader.queue import enqueue_operation
from papertrader.tables import read_table

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def test_migration_preview_apply_replay_preserves_all_state(sandbox_repository, sandbox_settings):
    root = sandbox_repository
    before = {path: path.read_bytes() for path in (root / "data").rglob("*.csv")}
    preview = migrate(root, sandbox_settings, now=NOW)
    assert not (root / POLICY_PATH).exists()
    assert preview["automatic_obligation_cap"] == 5
    assert migrate(root, sandbox_settings, now=NOW, apply=True) == preview
    assert migrate(root, sandbox_settings, now=NOW + timedelta(days=1), apply=True) == preview
    assert {path: path.read_bytes() for path in before} == before
    assert validate_hardening(root) == []


def test_policy_cannot_be_activated_by_arbitrary_marker(sandbox_repository):
    root = sandbox_repository
    path = root / POLICY_PATH
    path.parent.mkdir(parents=True)
    atomic_write_json(path, {"policy_version": 1}, allowed_root=root)
    with pytest.raises(GovernanceError):
        policy(root)


def test_capacity_preserves_deferred_request_and_legacy_obligations(
    sandbox_repository, sandbox_settings
):
    root = sandbox_repository
    migrate(root, sandbox_settings, now=NOW, apply=True)
    for number in range(6):
        enqueue_operation(
            root,
            sandbox_settings,
            operation_type="research_triage",
            entity_type="security",
            entity_id=f"sec_{number}",
            dedupe_key=f"test:{number}",
            prompt="Bounded check",
            inputs={
                "security_id": f"sec_{number}",
                "investigation_id": f"test:{number}",
                "cause": "ordinary",
                "evidence_refs": [f"fixture:capacity:{number}"],
            },
            source="controller:test",
            now=NOW,
        )
    rows = read_table(root, "operations_todo")
    assert len(rows) == 6
    assert rows[-1]["status"] == "blocked"
    assert rows[-1]["last_error"] == "scope_deferred_for_capacity"
    assert validate_hardening(root) == []

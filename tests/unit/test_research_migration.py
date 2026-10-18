from __future__ import annotations

import copy
import csv
import io
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.research_migration import prepare_migration, stage_migration
from papertrader.research_state import read_state, validate_state

BASELINE = "9056d3dff03740a6c3310e086a240186bca4527a"


def _legacy(root: Path, name: str) -> list[dict[str, str]]:
    content = subprocess.check_output(
        ["git", "-C", str(root), "show", f"{BASELINE}:data/tables/{name}.csv"]
    )
    return list(csv.DictReader(io.StringIO(content.decode(), newline="")))


def test_real_migration_preserves_identity_scenarios_expiry_and_sources(
    repository_root: Path,
) -> None:
    before = subprocess.check_output(
        ["git", "status", "--porcelain", "--", "data"], cwd=repository_root
    )
    state, pages, report = prepare_migration(repository_root, BASELINE)
    assert report["rows"] == {
        "securities": 92,
        "ideas": 29,
        "relationships": 47,
        "security_assessments": 83,
        "source_registry": 366,
        "research_queue": 0,
    }
    assert validate_state(repository_root, state, pages=pages) == []
    old_securities = {row["security_id"]: row for row in _legacy(repository_root, "securities")}
    for row in state["securities"]:
        for column in ("security_id", "issuer_id", "venue_mic", "provider_symbol", "currency"):
            assert row[column] == old_securities[row["security_id"]][column]
        assert "broker_symbol" not in row
    old_assessments = {
        row["security_id"]: row for row in _legacy(repository_root, "security_assessments")
    }
    for row in state["security_assessments"]:
        old = old_assessments[row["security_id"]]
        assert row["assessed_at"] == old["assessed_at"]
        assert row["valid_until"] == old["expires_at"]
        if old["valuation_supported"] == "true":
            for case in ("bear", "base", "bull"):
                for column in ("fair_value", "probability_pct", "assumptions"):
                    assert row[f"{case}_{column}"] == old[f"{case}_{column}"]
        else:
            assert row["research_status"] == "valuation_unsupported"
            assert all(not row[f"{case}_fair_value"] for case in ("bear", "base", "bull"))
        assert (
            not {"portfolio_action", "eligibility", "allocation_eligibility", "run_id"} & row.keys()
        )
    now = datetime(2026, 10, 18, tzinfo=UTC)
    assert (
        sum(
            datetime.fromisoformat(row["valid_until"].replace("Z", "+00:00")) < now
            for row in state["security_assessments"]
        )
        == 82
    )
    assert not any(
        row["research_status"] == "supported"
        and datetime.fromisoformat(row["valid_until"].replace("Z", "+00:00")) > now
        for row in state["security_assessments"]
    )
    assert {row["source_id"] for row in state["source_registry"]} == {
        row["source_id"] for row in _legacy(repository_root, "source_registry")
    }
    assert report["history_references_rewritten"] == [
        "data/wiki/securities/security_96ba305ee7cd586bc348.md"
    ]
    assert (
        subprocess.check_output(["git", "status", "--porcelain", "--", "data"], cwd=repository_root)
        == before
    )


def test_staging_is_explicit_validated_and_idempotent(
    repository_root: Path, tmp_path: Path
) -> None:
    destination = tmp_path / "current-research"
    first = stage_migration(repository_root, BASELINE, destination)
    times = {path: path.stat().st_mtime_ns for path in destination.rglob("*") if path.is_file()}
    assert validate_state(destination, read_state(destination)) == []
    assert stage_migration(repository_root, BASELINE, destination) == first
    assert {path: path.stat().st_mtime_ns for path in times} == times
    assert not (destination / "data/tables/security_assessment_history.csv").exists()
    assert not (destination / "data/operations").exists()
    with pytest.raises(ValueError, match="outside active data"):
        stage_migration(repository_root, BASELINE, repository_root / "data/migrated")


@pytest.mark.parametrize("mutation", ["duplicate", "source", "probabilities", "path", "missing"])
def test_research_schema_rejects_corrupt_migrations(repository_root: Path, mutation: str) -> None:
    state, pages, _ = prepare_migration(repository_root, BASELINE)
    invalid = copy.deepcopy(state)
    if mutation == "duplicate":
        invalid["security_assessments"].append(invalid["security_assessments"][0].copy())
    elif mutation == "source":
        invalid["security_assessments"][0]["source_ids"] = "source_invented"
    elif mutation == "probabilities":
        supported = next(
            row for row in invalid["security_assessments"] if row["research_status"] == "supported"
        )
        supported["base_probability_pct"] = "99"
    elif mutation == "path":
        invalid["securities"][0]["research_page"] = "data/wiki/securities/../../secret.md"
    else:
        del invalid["security_assessments"][0]["assessed_at"]
    assert validate_state(repository_root, invalid, pages=pages)


def test_share_classes_keep_distinct_security_ids(repository_root: Path) -> None:
    state, pages, _ = prepare_migration(repository_root, BASELINE)
    share_class = state["securities"][0].copy()
    share_class.update(
        {
            "security_id": "security_fixture_share_class",
            "ticker": "FIX.B",
            "provider_symbol": "FIX-B",
            "research_page": "",
            "research_status": "unresearched",
        }
    )
    state["securities"].append(share_class)
    assert validate_state(repository_root, state, pages=pages) == []


def test_security_mic_accepts_iso_alphanumeric_code(repository_root: Path) -> None:
    state, pages, _ = prepare_migration(repository_root, BASELINE)
    state["securities"][0]["venue_mic"] = "X1A2"
    assert validate_state(repository_root, state, pages=pages) == []

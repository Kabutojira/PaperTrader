from __future__ import annotations

import copy
import csv
import io
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.research_migration import prepare_migration, stage_migration
from papertrader.research_state import (
    FUNDAMENTAL_SCORES,
    contracts,
    csv_bytes,
    read_state,
    unscored_fields,
    validate_state,
)

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
        assert all(not row[field] for field in FUNDAMENTAL_SCORES)
        assert row["scoring_rubric_version"] == "1"
        assert (
            row["score_details"]
            == unscored_fields("Historical research was not assessed under scoring rubric 1.")[
                "score_details"
            ]
        )
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


def test_clean_checkout_crlf_inside_quoted_prose_is_logically_idempotent(
    repository_root: Path, tmp_path: Path
) -> None:
    state, _, _ = prepare_migration(repository_root, BASELINE)
    destination = tmp_path / "crlf-checkout"
    stage_migration(repository_root, BASELINE, destination)
    contract = contracts(destination)["security_assessments"]
    path = destination / contract.path
    staged = path.read_bytes()
    # Git stores text-normalized CSV and .gitattributes checks every LF out as
    # CRLF, including newlines embedded inside RFC 4180 quoted prose cells.
    checkout = staged.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    assert checkout != staged
    path.write_bytes(checkout)

    checked_out = read_state(destination)["security_assessments"]

    assert any("\n" in value for row in checked_out for value in row.values())
    assert not any("\r" in value for row in checked_out for value in row.values())
    assert csv_bytes(contract, checked_out) == csv_bytes(contract, state["security_assessments"])


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


def test_explicit_narratives_exclude_relationships_charts_and_trade_gates() -> None:
    from papertrader.research_migration import existing_narratives

    text = """## Thesis, catalysts and risks

Contrary evidence is delayed customer orders and supplier concentration.

Catalysts are funded backlog conversion. Invalidate the thesis if orders fail to convert.

```echart
{"description":"Risks are a fake chart narrative."}
```

## Idea exposure map

Invalidate the thesis if the unrelated idea fails.

## Changes since prior review

Risks are an obsolete prior conclusion.
"""
    found = existing_narratives(text)
    assert found == {
        "downside": "Contrary evidence is delayed customer orders and supplier concentration.",
        "catalysts": "Catalysts are funded backlog conversion.",
        "invalidation_conditions": "Invalidate the thesis if orders fail to convert.",
    }
    ambiguous = text + "\n## Business risks\n\nRisks are another distinct conclusion.\n"
    assert "downside" not in existing_narratives(ambiguous)
    assert (
        existing_narratives(
            "## Risks\n\nRisks are a pending canonical relationship and blocked paper orders.\n"
        )
        == {}
    )


def test_recovery_is_dry_by_default_and_preserves_values_sources_and_original_age(
    repository_root: Path, tmp_path: Path
) -> None:
    import shutil

    from papertrader.research_migration import recover_narratives
    from papertrader.research_ratings import reprice, valuation_coverage
    from papertrader.research_state import write_state

    root = tmp_path / "recovery"
    root.mkdir()
    shutil.copytree(repository_root / "schemas", root / "schemas")
    shutil.copy2(repository_root / "research.ini", root / "research.ini")
    schema = contracts(root)
    state = {name: [] for name in schema}
    now = datetime(2026, 10, 18, tzinfo=UTC)
    for sid in ("expired", "fresh", "mismatch", "unsupported"):
        security = dict.fromkeys(schema["securities"].columns, "")
        security.update(
            security_id=sid,
            issuer_id="issuer_" + sid,
            venue_mic="XNYS",
            currency="USD",
            research_status="researched",
            research_page=f"data/wiki/securities/{sid}.md",
        )
        state["securities"].append(security)
        date = "2026-10-18" if sid == "fresh" else "2026-08-01"
        assessment = dict.fromkeys(schema["security_assessments"].columns, "")
        assessment.update(unscored_fields("Historical fixture has no component scoring evidence."))
        assessment.update(
            security_id=sid,
            assessed_at=date + "T00:00:00Z",
            valid_until=("2026-11-17" if sid == "fresh" else "2026-08-31") + "T00:00:00Z",
            research_status="valuation_unsupported" if sid == "unsupported" else "supported",
            method="normalized_earnings",
            method_rationale="Verified per-share earning power and assumed multiples.",
            currency="USD",
            horizon_months="12",
            confidence="medium",
            source_ids="source1",
            thesis="Recurring demand supports earning power.",
            key_assumptions="Margins remain stable.",
        )
        if sid != "unsupported":
            for case, value, probability in (
                ("bear", "50", "25"),
                ("base", "100", "50"),
                ("bull", "150", "25"),
            ):
                assessment.update(
                    {
                        case + "_fair_value": value,
                        case + "_probability_pct": probability,
                        case + "_assumptions": "Original case-specific earning power and multiple.",
                    }
                )
        state["security_assessments"].append(assessment)
        page = root / security["research_page"]
        page.parent.mkdir(parents=True, exist_ok=True)
        page_date = "2026-08-02" if sid == "mismatch" else date
        page.write_text(
            f'---\nsecurity_id: {sid}\nissuer_id: issuer_{sid}\nupdated: "{page_date}"\n---\n'
            "\n## Thesis, catalysts and invalidation\n\n"
            "Contrary evidence is customer concentration.\n\n"
            "Catalysts are retained-customer growth. "
            "Invalidate on persistent margin compression.\n\n"
            "[Current primary source](https://issuer.example/results) (source1).\n"
        )
    source = dict.fromkeys(schema["source_registry"].columns, "")
    source.update(source_id="source1", url="https://issuer.example/results", status="valid")
    state["source_registry"].append(source)
    write_state(root, state)
    original = {path: path.read_bytes() for path in (root / "data").rglob("*") if path.is_file()}

    preview = recover_narratives(root, now=now)
    assert preview == recover_narratives(root, now=now)
    assert preview["mode"] == "dry_run" and preview["changed"] == []
    assert [row["security_id"] for row in preview["changes"]] == ["expired"]
    assert all(path.read_bytes() == content for path, content in original.items())
    applied = recover_narratives(root, apply=True, now=now)
    assert applied["changed"] == ["data/tables/security_assessments.csv"]
    after = read_state(root)
    before_rows = {row["security_id"]: row for row in state["security_assessments"]}
    after_rows = {row["security_id"]: row for row in after["security_assessments"]}
    for sid, before in before_rows.items():
        if sid != "expired":
            assert after_rows[sid] == before
            continue
        assert valuation_coverage(after_rows[sid]) == "complete"
        for column, value in before.items():
            if column not in {"downside", "catalysts", "invalidation_conditions"}:
                assert after_rows[sid][column] == value
        assert (
            reprice(after_rows[sid], {"security_id": sid}, now=now)["reason"]
            == "research_expired_or_future"
        )
    for name in state.keys() - {"security_assessments"}:
        assert after[name] == state[name]
    assert all(
        path.read_bytes() == content for path, content in original.items() if path.suffix == ".md"
    )
    times = {path: path.stat().st_mtime_ns for path in original}
    assert recover_narratives(root, apply=True, now=now)["changed"] == []
    assert {path: path.stat().st_mtime_ns for path in times} == times

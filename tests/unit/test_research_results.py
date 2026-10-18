from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

import pytest

from papertrader import research_transaction
from papertrader.research_agent import (
    MAX_AUTH_BYTES,
    ResearchLimits,
    _source_identity_index,
    agent_environment,
    run_cycle,
    run_model,
)
from papertrader.research_cli import main
from papertrader.research_publication import snapshot
from papertrader.research_queue import admit
from papertrader.research_results import (
    ResearchResultValidationError,
    commit_result,
    prepare_result,
)
from papertrader.research_state import contracts, read_state, validate_state, write_state
from papertrader.research_transaction import apply_files, research_lock
from papertrader.research_web import SOURCE_RESPONSE_MAX_BYTES, ResearchWeb, public_url
from papertrader.research_worker import POLICY

NOW = datetime(2026, 10, 18, 17, tzinfo=UTC)
STAMP = "2026-10-18T17:00:00Z"
URL = "https://issuer.example/earnings"


@pytest.fixture
def current(repository_root: Path, tmp_path: Path) -> Path:
    root = tmp_path / "current"
    root.mkdir()
    shutil.copytree(repository_root / "schemas", root / "schemas")
    shutil.copytree(repository_root / "skills", root / "skills")
    shutil.copy2(repository_root / "research.ini", root / "research.ini")
    schema = contracts(root)
    state = {name: [] for name in schema}
    for sid in ("security1", "security2"):
        row = dict.fromkeys(schema["securities"].columns, "")
        row.update(
            security_id=sid,
            issuer_id="issuer" + sid[-1],
            company_name="Example",
            instrument_name="Ordinary",
            instrument_type="equity",
            ticker="EX",
            venue_mic="XNYS",
            provider_symbol="EX",
            currency="USD",
            status="watching",
            research_status="researched",
            research_page=f"data/wiki/securities/{sid}.md",
        )
        state["securities"].append(row)
        path = root / row["research_page"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nsecurity_id: {sid}\nissuer_id: {row['issuer_id']}\n"
            "title: Example\n---\nCurrent thesis.\n"
        )
    idea = dict.fromkeys(schema["ideas"].columns, "")
    idea.update(
        idea_id="idea1",
        title="Mechanism",
        status="unresearched",
        research_page="data/wiki/ideas/idea1.md",
    )
    state["ideas"].append(idea)
    path = root / idea["research_page"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\nidea_id: idea1\ntitle: Mechanism\n---\nMechanism.\n")
    write_state(root, state)
    assert validate_state(root, read_state(root)) == []
    return root


def result(root: Path, *, supported: bool = True) -> dict[str, Any]:
    schema = contracts(root)
    assessment = dict.fromkeys(schema["security_assessments"].columns, "")
    assessment.update(
        security_id="security1",
        assessed_at=STAMP,
        valid_until="2026-11-17T17:00:00Z",
        research_status="supported" if supported else "valuation_unsupported",
        method="normalized_earnings",
        method_rationale="Per-share earning power and a justified multiple.",
        currency="USD",
        horizon_months="12",
        thesis="Durable demand.",
        key_assumptions="Earnings remain stable.",
        downside="Demand contracts.",
        catalysts="Next annual results.",
        invalidation_conditions="Sustained negative cash flow.",
        confidence="medium",
        limitations="Estimation uncertainty."
        if supported
        else "Reliable normalized earnings unavailable.",
        source_ids="source1",
    )
    if supported:
        for case, fair, prob in [
            ("bear", "50", "25"),
            ("base", "100", "50"),
            ("bull", "150", "25"),
        ]:
            assessment.update(
                {
                    f"{case}_fair_value": fair,
                    f"{case}_probability_pct": prob,
                    f"{case}_assumptions": "Cited earning power, justified case multiple.",
                }
            )
    source = dict.fromkeys(schema["source_registry"].columns, "")
    source.update(
        source_id="source1",
        url=URL,
        title="Issuer earnings",
        publisher="Issuer",
        source_type="earnings_release",
        license="link_only",
        status="valid",
        related_entity_ids="security1",
    )
    markdown = (
        "---\nsecurity_id: security1\nissuer_id: issuer1\ntitle: Example\n---\n# Research\n"
        f"Original synthesis. [Earnings]({URL})\n"
    )
    return dict(
        operation="research_security",
        entity_id="security1",
        outcome="updated" if supported else "not_supportable",
        summary="Current primary review.",
        assessment=assessment,
        idea=None,
        sources=[source],
        relationships=[],
        pages={"data/wiki/securities/security1.md": markdown},
    )


def observations() -> dict[str, dict[str, str]]:
    return {
        URL: dict(
            url=URL,
            final_url=URL,
            checked_at=STAMP,
            content_hash="a" * 64,
            source_text="Issuer earnings release with primary financial evidence.",
        )
    }


def idea_result(root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    state = read_state(root)
    document = result(root)
    idea = state["ideas"][0].copy()
    idea.update(
        status="researched",
        thesis="Verified causal mechanism.",
        source_ids="source1",
        last_reviewed_on="2026-10-18",
    )
    document.update(
        operation="research_idea",
        entity_id="idea1",
        idea=idea,
        assessment=None,
        pages={
            "data/wiki/ideas/idea1.md": (
                f"---\nidea_id: idea1\ntitle: Mechanism\n---\n"
                f"Original causal analysis. [Source]({URL})\n"
            )
        },
    )
    document["sources"][0]["related_entity_ids"] = "idea1"
    relationship = dict.fromkeys(contracts(root)["relationships"].columns, "")
    relationship.update(
        relationship_id="link1",
        idea_id="idea1",
        security_id="security1",
        relationship_type="beneficiary",
        direction="positive",
        mechanism="Verified demand transmission.",
        confidence="medium",
        status="current",
        source_ids="source1",
        research_page="data/wiki/ideas/idea1.md",
        last_reviewed_at=STAMP,
    )
    document["relationships"] = [relationship]
    return document, relationship


def data_bytes(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in (root / "data").rglob("*")
        if p.is_file()
    }


def test_final_frontmatter_and_current_rows_applied_together_idempotently(current: Path) -> None:
    before_other = (current / "data/wiki/securities/security2.md").read_bytes()
    document = result(current)
    # October15 regression: final frontmatter is staged before matching current rows;
    # no immutable page hash or assessment revision is written before this correction.
    document["pages"]["data/wiki/securities/security1.md"] += "\nReviewed frontmatter is final.\n"
    state, pages = prepare_result(
        current,
        read_state(current),
        document,
        operation="research_security",
        entity_id="security1",
        now=NOW,
        observations=observations(),
    )
    with research_lock(current):
        changed = commit_result(current, state, pages)
    assert "data/wiki/securities/security1.md" in changed
    assert "data/tables/security_assessments.csv" in changed
    assert read_state(current)["security_assessments"][0]["base_fair_value"] == "100"
    times = {p: p.stat().st_mtime_ns for p in (current / "data").rglob("*") if p.is_file()}
    state, pages = prepare_result(
        current,
        read_state(current),
        document,
        operation="research_security",
        entity_id="security1",
        now=NOW,
        observations=observations(),
    )
    with research_lock(current):
        assert commit_result(current, state, pages) == []
    assert {p: p.stat().st_mtime_ns for p in times} == times
    assert (current / "data/wiki/securities/security2.md").read_bytes() == before_other
    assert not list((current / "data").rglob("*history*"))


@pytest.mark.parametrize(
    "corruption",
    [
        "probability",
        "unknown_source",
        "unopened",
        "identity",
        "issuer",
        "future",
        "expiry",
        "unsafe_path",
        "script",
        "retired_chart",
        "partial",
        "missing_risk",
    ],
)
def test_invalid_result_changes_no_source_csv_or_page(current: Path, corruption: str) -> None:
    document = result(current)
    observed = observations()
    page = "data/wiki/securities/security1.md"
    if corruption == "probability":
        document["assessment"]["bull_probability_pct"] = "50"
    elif corruption == "unknown_source":
        document["assessment"]["source_ids"] = "invented"
    elif corruption == "unopened":
        observed = {}
    elif corruption == "identity":
        document["assessment"]["security_id"] = "security2"
    elif corruption == "issuer":
        document["pages"][page] = document["pages"][page].replace("issuer1", "issuer2")
    elif corruption == "future":
        document["assessment"]["assessed_at"] = "2026-10-19T17:00:00Z"
    elif corruption == "expiry":
        document["assessment"]["valid_until"] = "2027-01-01T00:00:00Z"
    elif corruption == "unsafe_path":
        document["pages"]["data/wiki/securities/../../.env"] = document["pages"].pop(page)
    elif corruption == "script":
        document["pages"][page] += "<script>alert(1)</script>"
    elif corruption == "retired_chart":
        document["pages"][page] += '\n```echart\n{"chart_id":"market-technicals"}\n```\n'
    elif corruption == "partial":
        del document["assessment"]["thesis"]
    else:
        document["assessment"]["downside"] = ""
    before = data_bytes(current)
    with pytest.raises(ValueError):
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observed,
        )
    assert data_bytes(current) == before


def test_unassessed_needs_attention_may_lack_page_but_assessed_security_may_not(
    current: Path,
) -> None:
    state = read_state(current)
    security = state["securities"][0]
    security.update(research_status="needs_attention", research_page="")

    assert validate_state(current, state) == []

    document = result(current)
    state["source_registry"] = document["sources"]
    state["security_assessments"] = [document["assessment"]]
    errors = validate_state(current, state)

    assert any(error.startswith("missing research page:") for error in errors)


def test_global_state_failure_uses_redacted_static_diagnostic(current: Path) -> None:
    state = read_state(current)
    state["securities"][1].update(research_status="researched", research_page="")

    with pytest.raises(ResearchResultValidationError) as failure:
        prepare_result(
            current,
            state,
            result(current),
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observations(),
        )

    assert failure.value.diagnostic_code == "state.research_page.invalid"
    assert str(failure.value) == "invalid research result field"
    assert "security2" not in str(failure.value)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("source.published_at", "2026-10-18", "source.published_at.invalid"),
        (
            "source.published_at",
            "2026-10-18T19:00:00+02:00",
            "source.published_at.invalid",
        ),
        ("source.published_at", "2026-10-19T17:00:00Z", "source.published_at.future"),
        ("assessment.assessed_at", "2026-10-18", "assessment.assessed_at.invalid"),
        (
            "assessment.assessed_at",
            "2026-10-18T19:00:00+02:00",
            "assessment.assessed_at.invalid",
        ),
        (
            "assessment.assessed_at",
            "2026-10-18T17:06:00Z",
            "assessment.assessed_at.future",
        ),
        (
            "assessment.assessed_at",
            "2026-10-18T15:59:00Z",
            "assessment.assessed_at.stale",
        ),
        ("assessment.valid_until", "2026-11-17", "assessment.valid_until.invalid"),
        (
            "assessment.valid_until",
            "2026-11-17T19:00:00+02:00",
            "assessment.valid_until.invalid",
        ),
        (
            "assessment.valid_until",
            "2026-11-18T17:00:00Z",
            "assessment.valid_until.exceeds_freshness",
        ),
    ],
)
def test_model_timestamps_have_strict_field_specific_codes(
    current: Path, field: str, value: str, code: str
) -> None:
    document = result(current)
    section, column = field.split(".")
    target = document["sources"][0] if section == "source" else document["assessment"]
    target[column] = value

    with pytest.raises(ResearchResultValidationError) as failure:
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observations(),
        )

    assert failure.value.diagnostic_code == code


def test_unsupported_valuation_is_honest_and_valid(current: Path) -> None:
    state, pages = prepare_result(
        current,
        read_state(current),
        result(current, supported=False),
        operation="research_security",
        entity_id="security1",
        now=NOW,
        observations=observations(),
    )
    with research_lock(current):
        commit_result(current, state, pages)
    assessment = read_state(current)["security_assessments"][0]
    assert assessment["research_status"] == "valuation_unsupported"
    assert not assessment["base_fair_value"]


@pytest.mark.parametrize(
    "field",
    [
        "thesis",
        "method_rationale",
        "key_assumptions",
        "downside",
        "catalysts",
        "invalidation_conditions",
        "limitations",
        "source_ids",
    ],
)
def test_unsupported_valuation_requires_each_narrative_with_static_code(
    current: Path, field: str
) -> None:
    document = result(current, supported=False)
    document["assessment"][field] = ""

    with pytest.raises(ResearchResultValidationError) as failure:
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observations(),
        )

    assert failure.value.diagnostic_code == f"assessment.{field}.missing"
    assert str(failure.value) == "invalid research result field"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("status", "unverified", "source.status.invalid"),
        ("title", "", "source.title.missing"),
        (
            "related_entity_ids",
            "security2",
            "source.related_entity_ids.target_missing",
        ),
    ],
)
def test_source_row_failures_have_static_field_diagnostics(
    current: Path, field: str, value: str, code: str
) -> None:
    document = result(current)
    document["sources"][0][field] = value

    with pytest.raises(ResearchResultValidationError) as failure:
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observations(),
        )

    assert failure.value.diagnostic_code == code
    assert str(failure.value) == "invalid research result field"


def test_exception_mid_transaction_restores_all_originals(
    current: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = data_bytes(current)
    write = research_transaction.atomic_write_bytes
    count = 0

    def failing(*args: Any, **kwargs: Any) -> None:
        nonlocal count
        count += 1
        if count == 2:
            raise OSError("simulated disk failure")
        write(*args, **kwargs)

    monkeypatch.setattr(research_transaction, "atomic_write_bytes", failing)
    with research_lock(current), pytest.raises(OSError):
        apply_files(
            current,
            {
                "data/wiki/securities/security1.md": b"replaced",
                "data/wiki/securities/security2.md": b"replaced",
            },
        )
    assert data_bytes(current) == before
    assert not (current / ".cache/research-transaction.json").exists()


def test_copyrighted_source_prose_over_25_words_is_rejected(current: Path) -> None:
    copied = " ".join(f"evidence{index}" for index in range(40))
    document = result(current)
    page = "data/wiki/securities/security1.md"
    document["pages"][page] += f"\n{copied}\n"
    observed = observations()
    observed[URL]["source_text"] = f"Introduction {copied} conclusion"
    before = data_bytes(current)

    with pytest.raises(ValueError, match="copies more than 25"):
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observed,
        )

    assert data_bytes(current) == before


def test_new_source_cannot_self_assert_a_copy_exempt_license(current: Path) -> None:
    copied = " ".join(f"filingword{index}" for index in range(30))
    document = result(current)
    document["sources"][0]["license"] = "public-domain-us-government"
    document["pages"]["data/wiki/securities/security1.md"] += f"\n{copied}\n"
    observed = observations()
    observed[URL]["source_text"] = copied

    with pytest.raises(ValueError, match="copies more than 25"):
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observed,
        )


def test_existing_cited_source_is_refreshed_even_when_omitted_from_result_sources(
    current: Path,
) -> None:
    state = read_state(current)
    source = result(current)["sources"][0]
    source.update(checked_at="2026-10-01T00:00:00Z", content_hash="b" * 64)
    state["source_registry"] = [source]
    write_state(current, state)
    document = result(current)
    document["sources"] = []

    candidate, _ = prepare_result(
        current,
        read_state(current),
        document,
        operation="research_security",
        entity_id="security1",
        now=NOW,
        observations=observations(),
    )

    refreshed = candidate["source_registry"][0]
    assert refreshed["checked_at"] == STAMP
    assert refreshed["content_hash"] == "a" * 64


def test_new_source_id_cannot_reuse_an_existing_registry_url(current: Path) -> None:
    state = read_state(current)
    existing = result(current)["sources"][0]
    existing.update(checked_at=STAMP, content_hash="a" * 64)
    state["source_registry"] = [existing]
    write_state(current, state)
    document = result(current)
    document["sources"][0]["source_id"] = "source2"
    document["assessment"]["source_ids"] = "source2"

    with pytest.raises(ValueError, match="stable source identity"):
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_security",
            entity_id="security1",
            now=NOW,
            observations=observations(),
        )


def test_existing_source_alias_can_refresh_its_own_stable_identity(current: Path) -> None:
    state = read_state(current)
    source = result(current)["sources"][0]
    source.update(checked_at="2026-10-01T00:00:00Z", content_hash="b" * 64)
    alias = source.copy()
    alias.update(
        source_id="source_alias",
        title="Legacy citation for the same page",
        related_entity_ids="security2",
    )
    state["source_registry"] = [source, alias]
    write_state(current, state)

    candidate, _ = prepare_result(
        current,
        read_state(current),
        result(current),
        operation="research_security",
        entity_id="security1",
        now=NOW,
        observations=observations(),
    )

    accepted = {row["source_id"]: row for row in candidate["source_registry"]}
    assert set(accepted) == {"source1", "source_alias"}
    assert accepted["source1"]["checked_at"] == STAMP
    assert accepted["source1"]["content_hash"] == "a" * 64
    assert accepted["source_alias"] == alias
    assert candidate["security_assessments"][0]["source_ids"] == "source1"


def test_source_identity_index_prefers_target_alias_and_contains_no_metadata(current: Path) -> None:
    state = read_state(current)
    target = result(current)["sources"][0]
    target.update(title="private title", publisher="private publisher")
    other = target.copy()
    other.update(source_id="aaa_other_alias", related_entity_ids="security2")
    state["source_registry"] = [other, target]

    index = _source_identity_index(state, "security1")

    assert index == [{"source_id": "source1", "url": URL, "license": "link_only"}]
    assert set(index[0]) == {"source_id", "url", "license"}
    assert "private title" not in json.dumps(index)
    assert "private publisher" not in json.dumps(index)


def test_plain_prose_may_explain_retired_technical_chart(current: Path) -> None:
    document = result(current)
    document["pages"]["data/wiki/securities/security1.md"] += (
        "\nThe former market-technicals chart was removed and is not required.\n"
    )
    prepare_result(
        current,
        read_state(current),
        document,
        operation="research_security",
        entity_id="security1",
        now=NOW,
        observations=observations(),
    )


def test_invalid_result_does_not_starve_later_entities_and_cycle_is_bounded(current: Path) -> None:
    state = read_state(current)
    admit(state, "security", "security1", reasons={"manual"}, priority=100, manual=True, now=NOW)
    admit(state, "security", "security2", reasons={"manual"}, priority=100, manual=True, now=NOW)
    admit(state, "idea", "idea1", reasons={"manual"}, priority=100, manual=True, now=NOW)
    with research_lock(current):
        commit_result(current, state, {})
    calls = []

    def execute(root: Path, packet: dict[str, Any], limits: ResearchLimits) -> dict[str, Any]:
        calls.append(packet["identity"].get("security_id") or packet["identity"]["idea_id"])
        if packet["identity"].get("security_id") == "security1":
            raise ValueError("secret must not enter public error")
        return dict(
            result=dict(
                operation=packet["operation"],
                entity_id=calls[-1],
                outcome="no_change",
                summary="Reviewed, no change.",
                assessment=None,
                idea=None,
                sources=[],
                relationships=[],
                pages={},
            ),
            observations={},
            usage={"web_requests": limits.max_web_calls},
        )

    before_page = (current / "data/wiki/securities/security1.md").read_bytes()
    response = run_cycle(current, dry_run=False, executor=execute, clock=lambda: NOW)
    assert len(calls) == 3
    assert response["exit_code"] == 3
    assert response["web_requests"] == ResearchLimits().max_web_calls * 2
    assert "secret" not in json.dumps(response)
    failed = next(outcome for outcome in response["outcomes"] if "error" in outcome)
    assert failed["stage"] == "model"
    assert failed["error"] == "ValueError"
    assert failed["location"].startswith("papertrader.research_agent.run_cycle:")
    assert "/" not in failed["location"]
    state = read_state(current)
    assert len(state["research_queue"]) == 1
    assert state["research_queue"][0]["entity_id"] == "security1"
    assert state["research_queue"][0]["status"] == "failed"
    assert state["research_queue"][0]["last_error"].startswith(
        "model:ValueError:papertrader.research_agent.run_cycle:"
    )
    assert (current / "data/wiki/securities/security1.md").read_bytes() == before_page


def test_exhausted_first_review_persists_and_unrelated_research_and_publication_continue(
    current: Path,
) -> None:
    accepted, pages = prepare_result(
        current,
        read_state(current),
        result(current),
        operation="research_security",
        entity_id="security1",
        now=NOW,
        observations=observations(),
    )
    with research_lock(current):
        commit_result(current, accepted, pages)
    prior_assessment = [row.copy() for row in read_state(current)["security_assessments"]]
    prior_page = (current / "data/wiki/securities/security1.md").read_bytes()

    state = read_state(current)
    second = state["securities"][1]
    old_second_page = current / second["research_page"]
    second.update(research_status="unresearched", research_page="")
    admit(
        state,
        "security",
        "security2",
        reasons={"valuation_coverage_gap"},
        priority=100,
        manual=True,
        now=NOW,
    )
    admit(
        state,
        "security",
        "security1",
        reasons={"research_overdue"},
        priority=90,
        now=NOW,
    )
    write_state(current, state)
    old_second_page.unlink()
    calls: list[str] = []

    def execute(_root: Path, packet: dict[str, Any], _limits: ResearchLimits) -> dict[str, Any]:
        identity = packet["identity"]["security_id"]
        calls.append(identity)
        if identity == "security2":
            raise RuntimeError("provider body must remain private")
        return {
            "result": {
                "operation": "research_security",
                "entity_id": identity,
                "outcome": "no_change",
                "summary": "Current assessment reviewed without changes.",
                "assessment": None,
                "idea": None,
                "sources": [],
                "relationships": [],
                "pages": {},
            },
            "observations": {},
            "usage": {},
        }

    first = run_cycle(current, dry_run=False, executor=execute, clock=lambda: NOW)

    assert first["exit_code"] == 3
    assert calls == ["security2", "security1"]
    assert read_state(current)["research_queue"][0]["status"] == "failed"

    exhausted_at = NOW + timedelta(hours=6)
    second_run = run_cycle(current, dry_run=False, executor=execute, clock=lambda: exhausted_at)
    final = read_state(current)

    assert second_run["exit_code"] == 3
    assert second_run["outcomes"][0]["status"] == "needs_attention"
    assert calls == ["security2", "security1", "security2"]
    assert final["research_queue"] == []
    failed_security = next(row for row in final["securities"] if row["security_id"] == "security2")
    assert failed_security["research_status"] == "needs_attention"
    assert failed_security["research_page"] == ""
    assert final["security_assessments"] == prior_assessment
    assert (current / "data/wiki/securities/security1.md").read_bytes() == prior_page
    assert validate_state(current, final) == []
    publication = snapshot(current, now=exhausted_at)
    assert publication["coverage"]["watchlist_needs_attention"] == 1
    assert publication["coverage"]["watchlist_missing_research"] == 1


def test_invalid_worker_result_reports_validation_location_and_bounded_usage(current: Path) -> None:
    state = read_state(current)
    admit(state, "security", "security1", reasons={"manual"}, priority=100, manual=True, now=NOW)
    with research_lock(current):
        commit_result(current, state, {})

    def execute(_root: Path, _packet: dict[str, Any], limits: ResearchLimits) -> dict[str, Any]:
        document = result(current)
        document["assessment"]["bear_probability_pct"] = "30"
        return dict(
            result=document,
            observations=observations(),
            usage={
                "web_requests": limits.max_web_calls,
                "provider_body": "secret source prose",
            },
        )

    response = run_cycle(current, dry_run=False, executor=execute, clock=lambda: NOW)

    assert response["exit_code"] == 3
    assert response["web_requests"] == ResearchLimits().max_web_calls
    assert "secret source prose" not in json.dumps(response)
    [outcome] = response["outcomes"]
    assert outcome | {"location": "redacted"} == {
        "entity_id": "security1",
        "status": "retry_scheduled",
        "stage": "validation",
        "error": "ResearchResultValidationError",
        "code": "state.assessment.invalid",
        "location": "redacted",
        "web_requests": str(ResearchLimits().max_web_calls),
    }
    assert outcome["location"].startswith("papertrader.research_results.prepare_result:")
    assert "/" not in outcome["location"]


def test_model_timestamp_diagnostic_never_exposes_rejected_value(current: Path) -> None:
    state = read_state(current)
    admit(state, "security", "security1", reasons={"manual"}, priority=100, manual=True, now=NOW)
    with research_lock(current):
        commit_result(current, state, {})
    rejected = "secret-provider-date"

    def execute(_root: Path, _packet: dict[str, Any], _limits: ResearchLimits) -> dict[str, Any]:
        document = result(current)
        document["sources"][0]["published_at"] = rejected
        return dict(result=document, observations=observations(), usage={"web_requests": 1})

    response = run_cycle(current, dry_run=False, executor=execute, clock=lambda: NOW)

    assert rejected not in json.dumps(response)
    [outcome] = response["outcomes"]
    assert outcome["stage"] == "validation"
    assert outcome["error"] == "ResearchResultValidationError"
    assert outcome["code"] == "source.published_at.invalid"
    assert outcome["location"].startswith("papertrader.research_results._model_timestamp:")
    queue = read_state(current)["research_queue"]
    assert len(queue) == 1
    assert "source.published_at.invalid" in queue[0]["last_error"]
    assert rejected not in queue[0]["last_error"]


def test_worker_prompt_states_exact_current_research_contract() -> None:
    for requirement in (
        "exactly every column in context.contracts",
        "Every source row has status\nvalid",
        "source_id, source_url and source_license",
        "Copy that exact tuple into the source row",
        "Never guess or replace a source identity",
        "related_entity_ids includes the target entity",
        "target security_id and its immutable issuer_id exactly",
        "Copy context.as_of exactly",
        "Leave source.published_at empty",
        "Every source ID in an assessment, idea row or relationship row must exist",
        "have its exact URL linked\nin the final primary Markdown page",
        "Clearly attributed trustworthy secondary financial reporting",
        "A generic corporate\nhomepage is not financial evidence",
        "All eight assessment narratives/evidence fields",
        "including for an\nunsupported valuation",
        "confidence to exactly low, medium or high",
        "research_status to exactly supported, unrated or valuation_unsupported",
        "Never carry unverified prior numbers forward",
    ):
        assert requirement in POLICY


def test_model_context_receives_configured_nonsecret_research_limits(current: Path) -> None:
    configuration = current / "research.ini"
    configuration.write_text(
        configuration.read_text().replace(
            "assessment_freshness_days = 30", "assessment_freshness_days = 7"
        )
    )
    seen: dict[str, Any] = {}

    def execute(_root: Path, packet: dict[str, Any], limits: ResearchLimits) -> dict[str, Any]:
        seen.update(packet)
        return dict(
            result=dict(
                operation="research_security",
                entity_id="security1",
                outcome="no_change",
                summary="Reviewed, no change.",
                assessment=None,
                idea=None,
                sources=[],
                relationships=[],
                pages={},
            ),
            observations={},
            usage={"web_requests": 0},
        )

    response = run_cycle(
        current,
        dry_run=False,
        entity_type="security",
        entity_id="security1",
        executor=execute,
        clock=lambda: NOW,
    )

    assert response["exit_code"] == 0
    assert seen["limits"] == vars(ResearchLimits(assessment_freshness_days=7))


def test_explicit_cycle_claims_only_the_requested_entity(current: Path) -> None:
    state = read_state(current)
    older = NOW.replace(day=17)
    admit(state, "security", "security1", reasons={"manual"}, priority=100, manual=True, now=older)
    with research_lock(current):
        commit_result(current, state, {})
    unrelated_before = read_state(current)["research_queue"][0].copy()
    calls: list[str] = []

    def execute(_root: Path, packet: dict[str, Any], _limits: ResearchLimits) -> dict[str, Any]:
        calls.append(packet["identity"]["security_id"])
        return dict(
            result=dict(
                operation="research_security",
                entity_id="security2",
                outcome="no_change",
                summary="Reviewed, no change.",
                assessment=None,
                idea=None,
                sources=[],
                relationships=[],
                pages={},
            ),
            observations={},
            usage={},
        )

    response = run_cycle(
        current,
        dry_run=False,
        entity_type="security",
        entity_id="security2",
        executor=execute,
        clock=lambda: NOW,
    )

    assert response["exit_code"] == 0
    assert calls == ["security2"]
    assert read_state(current)["research_queue"] == [unrelated_before]


def test_dry_run_never_invokes_model_and_environment_excludes_secrets(
    current: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "private-write")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "private-delivery")
    monkeypatch.setenv("OPENAI_OAUTH_SECRET", "private-encryption-key")
    environment = agent_environment(current, [])
    assert not {"GITHUB_TOKEN", "TELEGRAM_BOT_TOKEN", "OPENAI_OAUTH_SECRET"} & environment.keys()
    before = data_bytes(current)
    response = run_cycle(
        current,
        entity_type="security",
        entity_id="security1",
        executor=lambda *args: pytest.fail("dry-run model invocation"),
        clock=lambda: NOW,
    )
    assert response["status"] == "dry_run"
    assert data_bytes(current) == before
    assert main(["--repository", str(current), "validate"]) == 0


def test_corrupt_current_state_fails_before_claim_or_model(current: Path) -> None:
    state = read_state(current)
    state["securities"][0]["currency"] = "US"
    write_state(current, state)
    before = data_bytes(current)

    with pytest.raises(ValueError, match="invalid security currency"):
        run_cycle(
            current,
            dry_run=False,
            executor=lambda *_: pytest.fail("model invoked for corrupt state"),
            clock=lambda: NOW,
        )

    assert data_bytes(current) == before
    assert main(["--repository", str(current), "research", "--apply"]) == 4
    assert data_bytes(current) == before


def test_model_process_drops_root_privileges_and_sees_only_staged_worker(
    repository_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "hermes-home"
    home.mkdir()
    (home / "auth.json").write_text('{"token":"inference-only"}')
    python = tmp_path / "hermes-python"
    python.write_text("")
    hermes_code = tmp_path / "hermes-code"
    hermes_code.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("PAPERTRADER_HERMES_PYTHON", str(python))
    monkeypatch.setenv("PAPERTRADER_HERMES_CODE", str(hermes_code))
    monkeypatch.setenv("GITHUB_TOKEN", "repository-write-secret")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "delivery-secret")
    monkeypatch.setattr("papertrader.research_agent.os.geteuid", lambda: 0)
    ownership: list[tuple[Path, int, int]] = []
    monkeypatch.setattr(
        "papertrader.research_agent.os.chown",
        lambda path, uid, gid: ownership.append((Path(path), uid, gid)),
    )
    captured: dict[str, Any] = {}

    class Process:
        returncode = 0
        pid = 123

        def communicate(self, timeout: int | None = None) -> tuple[str, str]:
            del timeout
            return json.dumps({"result": {}, "observations": {}, "usage": {}}), ""

    def popen(command: list[str], **kwargs: Any) -> Process:
        captured.update(command=command, **kwargs)
        request = Path(command[-1])
        captured["request"] = json.loads(request.read_text())
        captured["request_mode"] = request.stat().st_mode & 0o777
        return Process()

    monkeypatch.setattr("papertrader.research_agent.subprocess.Popen", popen)
    source_identities = [{"source_id": "source1", "url": URL, "license": "link_only"}]
    response = run_model(
        repository_root,
        {"operation": "research_security", "_source_identity_index": source_identities},
        ResearchLimits(),
    )

    assert response["usage"] == {}
    assert captured["user"] == 10_000
    assert captured["group"] == 10_000
    assert captured["extra_groups"] == ()
    assert captured["request_mode"] == 0o600
    assert captured["request"]["source_identities"] == source_identities
    assert "_source_identity_index" not in captured["request"]["context"]
    environment = captured["env"]
    assert "GITHUB_TOKEN" not in environment
    assert "TELEGRAM_BOT_TOKEN" not in environment
    assert str(repository_root / "src") not in environment["PYTHONPATH"].split(os.pathsep)
    assert str(repository_root / ".git") not in environment["PYTHONPATH"]
    assert "worker-code" in environment["PYTHONPATH"]
    assert environment["HERMES_HOME"] != str(home)
    assert captured["cwd"] != repository_root
    assert any(path.name == "auth.json" and uid == gid == 10_000 for path, uid, gid in ownership)
    assert {path.name for path in home.iterdir()} == {"auth.json"}


@pytest.mark.parametrize("unmanaged", ["plugins", "hooks", "memories"])
def test_shared_unmanaged_research_profile_is_rejected_before_model_start(
    repository_root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    unmanaged: str,
) -> None:
    home = tmp_path / "shared-auth"
    home.mkdir()
    (home / "auth.json").write_text('{"token":"initial"}')
    (home / unmanaged).mkdir()
    python = tmp_path / "hermes-python"
    python.write_text("")
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("PAPERTRADER_HERMES_PYTHON", str(python))
    monkeypatch.setattr(
        "papertrader.research_agent.subprocess.Popen",
        lambda *_args, **_kwargs: pytest.fail("model started with unmanaged shared profile"),
    )

    with pytest.raises(RuntimeError, match="unmanaged_research_profile"):
        run_model(repository_root, {"operation": "research_security"}, ResearchLimits())


def test_sequential_model_operations_use_fresh_profiles_and_sync_oauth(
    repository_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "shared-auth"
    home.mkdir()
    (home / "auth.json").write_text('{"token":"initial"}')
    python = tmp_path / "hermes-python"
    python.write_text("")
    hermes_code = tmp_path / "hermes-code"
    hermes_code.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("PAPERTRADER_HERMES_PYTHON", str(python))
    monkeypatch.setenv("PAPERTRADER_HERMES_CODE", str(hermes_code))
    profiles: list[Path] = []
    starting_tokens: list[str] = []

    class Process:
        returncode = 0
        pid = 123

        def __init__(self, environment: dict[str, str]) -> None:
            self.environment = environment

        def communicate(self, timeout: int | None = None) -> tuple[str, str]:
            del timeout
            profile = Path(self.environment["HERMES_HOME"])
            profiles.append(profile)
            assert {path.name for path in profile.iterdir()} == {"auth.json", "config.yaml"}
            starting_tokens.append(json.loads((profile / "auth.json").read_text())["token"])
            for name in ("plugins", "hooks", "memories"):
                (profile / name).mkdir()
            (profile / "operation.log").write_text("ephemeral private trace")
            (profile / "auth.json").write_text(json.dumps({"token": f"refreshed-{len(profiles)}"}))
            return json.dumps({"result": {}, "observations": {}, "usage": {}}), ""

    monkeypatch.setattr(
        "papertrader.research_agent.subprocess.Popen",
        lambda _command, **kwargs: Process(kwargs["env"]),
    )

    for _ in range(2):
        run_model(repository_root, {"operation": "research_security"}, ResearchLimits())

    assert starting_tokens == ["initial", "refreshed-1"]
    assert json.loads((home / "auth.json").read_text()) == {"token": "refreshed-2"}
    assert len(set(profiles)) == 2
    assert all(not profile.exists() for profile in profiles)
    assert {path.name for path in home.iterdir()} == {"auth.json"}


def test_failed_model_discards_profile_but_keeps_valid_oauth_refresh(
    repository_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "shared-auth"
    home.mkdir()
    (home / "auth.json").write_text('{"token":"initial"}')
    python = tmp_path / "hermes-python"
    python.write_text("")
    hermes_code = tmp_path / "hermes-code"
    hermes_code.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("PAPERTRADER_HERMES_PYTHON", str(python))
    monkeypatch.setenv("PAPERTRADER_HERMES_CODE", str(hermes_code))
    profiles: list[Path] = []

    class Process:
        returncode = 1
        pid = 123

        def __init__(self, environment: dict[str, str]) -> None:
            self.environment = environment

        def communicate(self, timeout: int | None = None) -> tuple[str, str]:
            del timeout
            profile = Path(self.environment["HERMES_HOME"])
            profiles.append(profile)
            (profile / "operation.log").write_text("must be discarded")
            (profile / "auth.json").write_text('{"token":"legitimate-refresh"}')
            return "", ""

    monkeypatch.setattr(
        "papertrader.research_agent.subprocess.Popen",
        lambda _command, **kwargs: Process(kwargs["env"]),
    )

    with pytest.raises(RuntimeError, match="research_model_failed"):
        run_model(repository_root, {"operation": "research_security"}, ResearchLimits())

    assert json.loads((home / "auth.json").read_text()) == {"token": "legitimate-refresh"}
    assert all(not profile.exists() for profile in profiles)
    assert {path.name for path in home.iterdir()} == {"auth.json"}


@pytest.mark.parametrize("mutation", ["symlink", "malformed", "oversized"])
def test_unsafe_refreshed_oauth_never_reaches_shared_home(
    repository_root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    home = tmp_path / "shared-auth"
    home.mkdir()
    (home / "auth.json").write_text('{"token":"initial"}')
    python = tmp_path / "hermes-python"
    python.write_text("")
    hermes_code = tmp_path / "hermes-code"
    hermes_code.mkdir()
    outside = tmp_path / "outside-auth.json"
    outside.write_text('{"token":"outside"}')
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("PAPERTRADER_HERMES_PYTHON", str(python))
    monkeypatch.setenv("PAPERTRADER_HERMES_CODE", str(hermes_code))
    profiles: list[Path] = []

    class Process:
        returncode = 0
        pid = 123

        def __init__(self, environment: dict[str, str]) -> None:
            self.environment = environment

        def communicate(self, timeout: int | None = None) -> tuple[str, str]:
            del timeout
            profile = Path(self.environment["HERMES_HOME"])
            profiles.append(profile)
            auth = profile / "auth.json"
            if mutation == "symlink":
                auth.unlink()
                auth.symlink_to(outside)
            elif mutation == "malformed":
                auth.write_text("not-json")
            else:
                auth.write_bytes(b"x" * (MAX_AUTH_BYTES + 1))
            (profile / "operation.log").write_text("must be discarded")
            return json.dumps({"result": {}, "observations": {}, "usage": {}}), ""

    monkeypatch.setattr(
        "papertrader.research_agent.subprocess.Popen",
        lambda _command, **kwargs: Process(kwargs["env"]),
    )

    with pytest.raises(RuntimeError, match="invalid_refreshed_inference_auth"):
        run_model(repository_root, {"operation": "research_security"}, ResearchLimits())

    assert json.loads((home / "auth.json").read_text()) == {"token": "initial"}
    assert outside.read_text() == '{"token":"outside"}'
    assert all(not profile.exists() for profile in profiles)
    assert {path.name for path in home.iterdir()} == {"auth.json"}


def test_network_budget_is_hard_and_private_sources_are_forbidden(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    broker = ResearchWeb(max_calls=1)
    monkeypatch.setattr("papertrader.research_web.public_url", lambda _: None)
    broker.take(URL)
    with pytest.raises(ValueError, match="budget"):
        broker.take(URL)
    monkeypatch.undo()
    with pytest.raises(ValueError):
        public_url("http://127.0.0.1/private")
    with pytest.raises(ValueError):
        public_url("file:///etc/passwd")


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("pdf", "pdf_unsupported"),
        ("too_large", "source_too_large"),
        ("empty", "empty_content"),
    ],
)
def test_broker_returns_static_content_error_categories_without_source_data(
    monkeypatch: pytest.MonkeyPatch, mode: str, expected: str
) -> None:
    read_limits: list[int] = []

    class Response:
        def __init__(self) -> None:
            self.headers = {"Content-Type": "application/pdf" if mode == "pdf" else "text/html"}

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self, limit: int) -> bytes:
            read_limits.append(limit)
            if mode == "too_large":
                return b"x" * limit
            if mode == "empty":
                return b"<script>provider secret</script>"
            return b"provider secret PDF body"

        def geturl(self) -> str:
            return URL

    class Opener:
        def open(self, *_: object, **__: object) -> Response:
            return Response()

    monkeypatch.setattr("papertrader.research_web.public_url", lambda _: None)
    monkeypatch.setattr("papertrader.research_web.build_opener", lambda *_: Opener())

    outcome = json.loads(ResearchWeb().tool({"action": "open", "url": URL}))

    assert outcome == {"error": expected, "requests_used": 1}
    assert read_limits == [SOURCE_RESPONSE_MAX_BYTES + 1]
    assert "provider secret" not in json.dumps(outcome)


@pytest.mark.parametrize("status", [403, 404])
def test_broker_returns_only_numeric_http_status(
    monkeypatch: pytest.MonkeyPatch, status: int
) -> None:
    class Opener:
        def open(self, *_: object, **__: object) -> None:
            raise HTTPError(URL, status, "provider secret reason", {}, None)

    monkeypatch.setattr("papertrader.research_web.public_url", lambda _: None)
    monkeypatch.setattr("papertrader.research_web.build_opener", lambda *_: Opener())

    outcome = json.loads(ResearchWeb().tool({"action": "open", "url": URL}))

    assert outcome == {"error": "http_error", "requests_used": 1, "http_status": status}
    assert "provider secret" not in json.dumps(outcome)


def test_broker_budget_error_is_static_and_does_not_spend_a_request() -> None:
    outcome = json.loads(ResearchWeb(max_calls=0).tool({"action": "open", "url": URL}))

    assert outcome == {"error": "budget_exhausted", "requests_used": 0}


def test_opened_sources_receive_existing_or_deterministic_new_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requested = "https://issuer.example/redirect"
    new_url = "https://issuer.example/new-primary-source"
    destinations = iter([URL, new_url])

    class Response:
        def __init__(self, final_url: str) -> None:
            self.final_url = final_url
            self.headers = {"Content-Type": "text/html"}

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self, _: int) -> bytes:
            return b"<html><body>Primary evidence.</body></html>"

        def geturl(self) -> str:
            return self.final_url

    class Opener:
        def open(self, *_: object, **__: object) -> Response:
            return Response(next(destinations))

    monkeypatch.setattr("papertrader.research_web.public_url", lambda _: None)
    monkeypatch.setattr("papertrader.research_web.build_opener", lambda *_: Opener())
    broker = ResearchWeb(
        source_identities=[{"source_id": "source1", "url": URL, "license": "link_only"}]
    )

    existing = broker.open(requested)
    discovered = broker.open(new_url)

    assert (existing["source_id"], existing["source_url"], existing["source_license"]) == (
        "source1",
        URL,
        "link_only",
    )
    assert discovered["source_url"] == new_url
    assert discovered["source_license"] == "link_only"
    assert discovered["source_id"] == (
        "source_web_" + hashlib.sha256(new_url.encode()).hexdigest()[:24]
    )
    assert broker.observations[requested]["source_id"] == "source1"
    assert broker.observations[new_url]["source_id"] == discovered["source_id"]


def test_idea_and_inline_relationship_update_do_not_create_company_tasks(current: Path) -> None:
    state = read_state(current)
    document, relationship = idea_result(current)
    candidate, pages = prepare_result(
        current,
        state,
        document,
        operation="research_idea",
        entity_id="idea1",
        now=NOW,
        observations=observations(),
    )
    with research_lock(current):
        commit_result(current, candidate, pages)
    accepted = read_state(current)
    assert accepted["ideas"][0]["thesis"] == "Verified causal mechanism."
    assert accepted["relationships"] == [relationship]
    assert accepted["securities"] == state["securities"]
    assert accepted["research_queue"] == []


def test_relationship_source_url_must_appear_on_final_idea_page(current: Path) -> None:
    document, relationship = idea_result(current)
    relationship_url = "https://issuer.example/relationship-evidence"
    relationship["source_ids"] = "relationship-source-secret"
    source = document["sources"][0].copy()
    source.update(
        source_id="relationship-source-secret",
        url=relationship_url,
        title="Relationship evidence",
    )
    document["sources"].append(source)
    observed = observations()
    observed[relationship_url] = {
        "url": relationship_url,
        "final_url": relationship_url,
        "checked_at": STAMP,
        "content_hash": "b" * 64,
        "source_text": "Primary relationship evidence.",
    }
    before = data_bytes(current)

    with pytest.raises(ResearchResultValidationError) as failure:
        prepare_result(
            current,
            read_state(current),
            document,
            operation="research_idea",
            entity_id="idea1",
            now=NOW,
            observations=observed,
        )

    assert failure.value.diagnostic_code == "relationship.source_ids.url_missing_from_page"
    assert str(failure.value) == "invalid research result field"
    assert relationship_url not in str(failure.value)
    assert relationship["source_ids"] not in str(failure.value)
    assert data_bytes(current) == before


def test_interrupted_transaction_recovers_before_reader(current: Path) -> None:
    import base64

    page = current / "data/wiki/securities/security1.md"
    original = page.read_bytes()
    cache = current / ".cache"
    cache.mkdir()
    (cache / "research-transaction.json").write_text(
        json.dumps(
            {
                "data/wiki/securities/security1.md": base64.b64encode(original).decode(),
                "data/wiki/securities/partial.md": None,
            }
        )
    )
    page.write_bytes(b"partial update")
    (page.parent / "partial.md").write_bytes(b"partial new file")
    with research_lock(current):
        assert page.read_bytes() == original
        assert not (page.parent / "partial.md").exists()
    assert not (cache / "research-transaction.json").exists()


def test_initial_coverage_context_includes_target_path_gaps_and_recent_issuer_leads(
    current: Path,
) -> None:
    from papertrader.research_results import context_packet

    state = read_state(current)
    state["securities"][0]["research_page"] = ""
    state["securities"][0]["research_status"] = "unresearched"
    schema = contracts(current)
    for i in range(13):
        row = dict.fromkeys(schema["source_registry"].columns, "")
        row.update(
            source_id=f"old{i}",
            url=f"https://issuer.example/old{i}",
            related_entity_ids="security1",
            checked_at="2026-08-01T00:00:00Z",
        )
        state["source_registry"].append(row)
    lead = dict.fromkeys(schema["source_registry"].columns, "")
    lead.update(
        source_id="source_z_latest",
        url=URL,
        title="Issuer earnings release",
        license="link_only",
        status="available",
        checked_at=STAMP,
        related_entity_ids="security1",
    )
    state["source_registry"].append(lead)
    write_state(current, state)
    before = data_bytes(current)
    packet = context_packet(current, state, operation="research_security", entity_id="security1")
    assert packet["target_page"] == "data/wiki/securities/security1.md"
    assert packet["identity"]["research_page"] == ""
    assert packet["valuation_coverage"]["status"] == "missing_research"
    assert "base_fair_value" in packet["valuation_coverage"]["missing_fields"]
    assert "invalidation_conditions" in packet["valuation_coverage"]["missing_fields"]
    assert packet["sources"][0]["source_id"] == "source_z_latest"
    assert len(packet["sources"]) == 12
    assert data_bytes(current) == before


def test_skipped_coverage_review_has_cooldown_without_inventing_assessment(current: Path) -> None:
    from papertrader.research_queue import schedule_attention

    state = read_state(current)
    admit(state, "security", "security1", reasons={"valuation_coverage_gap"}, priority=75, now=NOW)
    write_state(current, state)
    original_assessments = state["security_assessments"]

    def executor(_root: Path, packet: dict[str, Any], _limits: ResearchLimits) -> dict[str, Any]:
        assert "valuation_coverage_gap" in packet["request"]["reasons"]
        return dict(
            result=dict(
                operation="research_security",
                entity_id="security1",
                outcome="skip_as_stale",
                summary="Reviewed current context; no supported update.",
                assessment=None,
                idea=None,
                sources=[],
                relationships=[],
                pages={},
            ),
            observations={},
            usage={},
        )

    response = run_cycle(
        current,
        dry_run=False,
        entity_type="security",
        entity_id="security1",
        executor=executor,
        clock=lambda: NOW,
    )
    assert response["outcomes"][0]["status"] == "skip_as_stale"
    reviewed = read_state(current)
    assert reviewed["security_assessments"] == original_assessments
    assert reviewed["securities"][0]["last_research_at"] == STAMP
    schedule_attention(reviewed, [], [], now=NOW)
    assert all(row["entity_id"] != "security1" for row in reviewed["research_queue"])


def test_source_reader_keeps_financial_body_after_large_navigation() -> None:
    from papertrader.research_web import SOURCE_TEXT_LIMIT, _Text

    parser = _Text()
    navigation = "<a href='/menu'>Menu entry </a>" * 2000
    navigation += "<a href='/investor/financial-results'>Investor results</a>"
    parser.feed(
        f"<html><head><title>Issuer results</title></head><body><header>{navigation}</header>"
        "<nav>Navigation outside header</nav><main><h1>Results</h1>"
        "Revenue 120 million. Diluted earnings per share 2.50."
        "<a href='/filing'>Financial filing</a></main><footer>Repeated navigation</footer>"
        "<script>untrusted executable content</script></body></html>"
    )
    text = " ".join(parser.parts)[:SOURCE_TEXT_LIMIT]
    assert "Revenue 120 million" in text
    assert "Diluted earnings per share 2.50" in text
    assert "[link: /filing]" in text
    assert "Menu entry" not in text
    assert "[link: /menu]" not in text
    assert "untrusted executable" not in text
    assert parser.source_links == ["/investor/financial-results"]

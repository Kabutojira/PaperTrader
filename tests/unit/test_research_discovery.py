from __future__ import annotations

import json
import shutil
from collections.abc import Iterator, Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from papertrader.research_discovery import (
    IdentityVerifier,
    company_key,
    prepare_candidates,
    run_discovery,
)
from papertrader.research_queue import admit, claim, schedule_attention
from papertrader.research_results import commit_result
from papertrader.research_state import (
    contracts,
    read_state,
    unscored_fields,
    validate_state,
    write_state,
)
from papertrader.research_transaction import research_lock

NOW = datetime(2026, 10, 18, 17, tzinfo=UTC)
STAMP = "2026-10-18T17:00:00Z"


@pytest.fixture
def catalog(repository_root: Path, tmp_path: Path) -> Path:
    root = tmp_path / "catalog"
    root.mkdir()
    (root / "schemas").mkdir()
    shutil.copy2(
        repository_root / "schemas/research_contracts.yaml",
        root / "schemas/research_contracts.yaml",
    )
    shutil.copy2(repository_root / "research.ini", root / "research.ini")
    for operation in ("research_security", "research_idea"):
        shutil.copytree(repository_root / "skills" / operation, root / "skills" / operation)
    write_state(root, {name: [] for name in contracts(root)})
    return root


def company(name: str = "Alpha Industrial Ltd.", symbol: str = "ALP") -> dict[str, Any]:
    return dict(
        company_name=name,
        instrument_name="Ordinary shares",
        ticker=symbol,
        venue_mic="XNAS",
        provider_symbol=symbol,
        currency="USD",
        country="US",
        thesis="Demand creates operating leverage; working capital remains uncertain.",
        source_urls=["https://issuer.example/filing"],
        idea_id="",
        idea_title="",
        mechanism="",
    )


def proposal(companies: list[dict[str, Any]] | None = None, *, idea: bool = True) -> dict[str, Any]:
    return dict(
        operation="research_idea",
        mode="discovery",
        summary="Primary-evidence candidates, not completed research.",
        ideas=[
            dict(
                title="Industrial bottlenecks",
                thesis="Supply constraints may change industry economics.",
                source_urls=["https://issuer.example/filing"],
            )
        ]
        if idea
        else [],
        companies=companies if companies is not None else [company()],
    )


def observations(now: datetime = NOW) -> dict[str, dict[str, str]]:
    return {
        "https://issuer.example/filing": dict(
            url="https://issuer.example/filing",
            checked_at=now.isoformat().replace("+00:00", "Z"),
            content_hash="a" * 64,
            source_text=(
                "Alpha Industrial Ltd. publishes primary operating evidence "
                "and verified public listing identity."
            ),
        )
    }


def metadata(value: dict[str, Any]) -> dict[str, str]:
    return dict(
        symbol=value["provider_symbol"],
        longName=value["company_name"],
        currency="USD",
        instrumentType="EQUITY",
        exchangeName="NMS",
    )


class LazyMetadata(Mapping[str, str]):
    def __init__(self, values: dict[str, str]) -> None:
        self.values = values

    def __getitem__(self, key: str) -> str:
        if key not in self.values:
            raise KeyError(key)
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("identity verification must not iterate lazy metadata")

    def __len__(self) -> int:
        raise AssertionError("identity verification must not inspect unrelated metadata")


def test_identity_verifier_reads_only_required_mapping_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = metadata(company()) | {"shortName": "Alpha"}
    provider = SimpleNamespace(session=object())
    verifier = IdentityVerifier.__new__(IdentityVerifier)
    verifier.provider = provider

    class Ticker:
        def __init__(self, symbol: str, *, session: object) -> None:
            assert symbol == "ALP" and session is provider.session

        def get_history_metadata(self, *, repair: bool) -> Mapping[str, str]:
            assert repair is False
            return LazyMetadata(expected)

    monkeypatch.setattr("papertrader.research_discovery.yf.Ticker", Ticker)

    assert verifier(company()) == expected


def test_identity_verifier_rejects_incomplete_mapping_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = IdentityVerifier.__new__(IdentityVerifier)
    verifier.provider = SimpleNamespace(session=object())

    class Ticker:
        def __init__(self, symbol: str, *, session: object) -> None:
            pass

        def get_history_metadata(self, *, repair: bool) -> Mapping[str, str]:
            return LazyMetadata({"symbol": "ALP"})

    monkeypatch.setattr("papertrader.research_discovery.yf.Ticker", Ticker)

    with pytest.raises(ValueError, match="provider identity metadata unavailable"):
        verifier(company())


def accept(root: Path, document: dict[str, Any], *, manual: bool = False) -> dict[str, Any]:
    state, pages, report = prepare_candidates(
        root,
        read_state(root),
        document,
        now=NOW,
        observations=observations(),
        verify_identity=metadata,
        manual=manual,
    )
    with research_lock(root):
        commit_result(root, state, pages)
    return report


def test_candidates_create_sources_pages_links_without_queue_or_valuations(catalog: Path) -> None:
    value = company()
    value.update(
        idea_title="Industrial bottlenecks",
        mechanism="Supply constraints transmit to component pricing.",
    )
    report = accept(catalog, proposal([value]))
    state = read_state(catalog)
    assert len(report["ideas"]) == len(report["companies"]) == 1
    assert len(state["relationships"]) == 1
    assert state["relationships"][0]["mechanism"] == value["mechanism"]
    assert len(state["source_registry"]) == 1
    assert (
        state["securities"][0]["research_status"] == state["ideas"][0]["status"] == "unresearched"
    )
    assert state["securities"][0]["last_research_at"] == state["ideas"][0]["last_reviewed_on"] == ""
    assert not state["research_queue"] and not state["security_assessments"]
    assert validate_state(catalog, state) == []
    for row in [*state["securities"], *state["ideas"]]:
        text = (catalog / row["research_page"]).read_text()
        assert "Unresearched candidate" in text and "https://issuer.example/filing" in text


def test_share_class_discovery_dedupes_issuer_but_manual_import_preserves_instruments(
    catalog: Path,
) -> None:
    first = company("Alphabet Inc.", "GOOG")
    second = company("Alphabet Inc. Class A", "GOOGL")
    report = accept(catalog, proposal([first, second], idea=False))
    state = read_state(catalog)
    assert len(report["companies"]) == len(report["known_issuers"]) == 1
    assert len(state["securities"]) == 1
    original = state["securities"][0].copy()
    accept(catalog, proposal([second], idea=False), manual=True)
    state = read_state(catalog)
    assert len(state["securities"]) == 2
    assert {row["issuer_id"] for row in state["securities"]} == {original["issuer_id"]}
    assert len({row["security_id"] for row in state["securities"]}) == 2
    assert original in state["securities"]
    assert {row["provider_symbol"] for row in state["securities"]} == {"GOOG", "GOOGL"}


def test_company_key_normalizes_equivalent_legal_spellings_and_share_class() -> None:
    assert company_key("Atlas, Incorporated") == company_key("Atlas Inc.")
    assert company_key("Atlas Corporation") == company_key("Atlas Corp.")
    assert company_key("Atlas Limited") == company_key("Atlas Ltd.")
    assert company_key("Atlas Company") == company_key("Atlas Co.")
    assert company_key("Alphabet Inc. Class A") == company_key("Alphabet Inc.")
    assert company_key("Atlas Inc.") != company_key("Atlas Corporation")


def test_equal_basename_with_distinct_legal_issuers_keeps_both_identities(
    catalog: Path,
) -> None:
    verified: list[tuple[str, str]] = []

    def verify(value: dict[str, Any]) -> dict[str, str]:
        verified.append((value["company_name"], value["provider_symbol"]))
        return metadata(value)

    document = proposal(
        [company("Atlas Inc.", "ATLI"), company("Atlas Corporation", "ATLC")],
        idea=False,
    )
    state, pages, report = prepare_candidates(
        catalog,
        read_state(catalog),
        document,
        now=NOW,
        observations=observations(),
        verify_identity=verify,
        manual=True,
    )
    with research_lock(catalog):
        commit_result(catalog, state, pages)
    accepted = read_state(catalog)

    assert verified == [("Atlas Inc.", "ATLI"), ("Atlas Corporation", "ATLC")]
    assert len(report["companies"]) == 2
    assert report["known_issuers"] == []
    assert len({row["issuer_id"] for row in accepted["securities"]}) == 2
    assert len({row["security_id"] for row in accepted["securities"]}) == 2
    assert {row["provider_symbol"] for row in accepted["securities"]} == {"ATLI", "ATLC"}


def test_repeated_candidate_import_is_idempotent(catalog: Path) -> None:
    document = proposal()
    accept(catalog, document)
    before = {
        path: path.stat().st_mtime_ns for path in (catalog / "data").rglob("*") if path.is_file()
    }
    accept(catalog, document)
    assert {path: path.stat().st_mtime_ns for path in before} == before
    state = read_state(catalog)
    assert len(state["ideas"]) == len(state["securities"]) == len(state["source_registry"]) == 1


@pytest.mark.parametrize(
    "bad",
    ["company_limit", "idea_limit", "currency", "name", "venue", "unopened", "ticker", "cascade"],
)
def test_invalid_candidate_batch_changes_nothing(catalog: Path, bad: str) -> None:
    document = proposal()
    observed = observations()
    verify = metadata
    if bad == "company_limit":
        document["companies"] *= 3
    elif bad == "idea_limit":
        document["ideas"] *= 2
    elif bad == "currency":
        document["companies"][0]["currency"] = "EUR"
    elif bad == "name":

        def unrelated(value: dict[str, Any]) -> dict[str, str]:
            return {**metadata(value), "longName": "Unrelated Corp."}

        verify = unrelated
    elif bad == "venue":
        document["companies"][0]["venue_mic"] = "XNYS"
    elif bad == "ticker":
        document["companies"][0]["ticker"] = "INVENTED"
    elif bad == "unopened":
        observed = {}
    else:
        document["companies"][0]["follow_up_tasks"] = ["unlimited"]
    before = read_state(catalog)
    with pytest.raises(ValueError):
        prepare_candidates(
            catalog, before, document, now=NOW, observations=observed, verify_identity=verify
        )
    assert read_state(catalog) == before
    assert not list((catalog / "data/wiki").rglob("*.md"))


def test_weekly_discovery_is_once_in_seven_days_and_dry_run_is_read_only(catalog: Path) -> None:
    calls = []

    def execute(*_: Any) -> dict[str, Any]:
        calls.append(1)
        return dict(result=proposal(), observations=observations(), usage={})

    assert (
        run_discovery(catalog, executor=execute, verify_identity=metadata, clock=lambda: NOW)[
            "status"
        ]
        == "dry_run"
    )
    assert not calls and not (catalog / "data/status.json").exists()
    assert (
        run_discovery(
            catalog, dry_run=False, executor=execute, verify_identity=metadata, clock=lambda: NOW
        )["status"]
        == "succeeded"
    )
    assert (
        run_discovery(
            catalog,
            dry_run=False,
            executor=execute,
            verify_identity=metadata,
            clock=lambda: NOW + timedelta(days=6),
        )["status"]
        == "not_due"
    )
    assert len(calls) == 1
    state = read_state(catalog)
    assert not state["research_queue"]
    status = json.loads((catalog / "data/status.json").read_text())["research"]
    assert status["last_discovery_attempt_at"] == status["last_discovery_success_at"] == STAMP


def test_failed_discovery_is_bounded_and_leaves_catalogs_unchanged(catalog: Path) -> None:
    before = read_state(catalog)

    def failing(*_: Any) -> dict[str, Any]:
        raise RuntimeError("private provider content")

    response = run_discovery(
        catalog, dry_run=False, executor=failing, verify_identity=metadata, clock=lambda: NOW
    )
    assert response["exit_code"] == 3
    assert read_state(catalog) == before
    assert "private" not in (catalog / "data/status.json").read_text()
    assert (
        run_discovery(catalog, dry_run=False, executor=failing, clock=lambda: NOW)["status"]
        == "not_due"
    )


def test_manual_share_class_selection_is_exact_without_duplicate_company_work(
    catalog: Path,
) -> None:
    accept(
        catalog,
        proposal(
            [company("Alphabet Inc.", "GOOG"), company("Alphabet Inc. Class A", "GOOGL")],
            idea=False,
        ),
        manual=True,
    )
    state = read_state(catalog)
    ids = [row["security_id"] for row in state["securities"]]
    other = max(ids)
    admit(state, "security", min(ids), reasons={"overdue"}, priority=60, now=NOW)
    admit(
        state,
        "security",
        other,
        reasons={"explicit_manual_request"},
        priority=100,
        manual=True,
        now=NOW,
    )
    assert len(state["research_queue"]) == 1
    assert state["research_queue"][0]["entity_id"] == other
    task = claim(state, now=NOW)
    assert task and task["entity_id"] == other
    # A second distinct manual instrument goal is explicitly rejected, not lost.
    with pytest.raises(ValueError, match="share-class"):
        admit(state, "security", min(ids), reasons={"manual"}, priority=100, manual=True, now=NOW)


def test_reviewed_share_class_queues_one_uncovered_sibling_valuation(catalog: Path) -> None:
    accept(
        catalog,
        proposal(
            [company("Alphabet Inc.", "GOOG"), company("Alphabet Inc. Class A", "GOOGL")],
            idea=False,
        ),
        manual=True,
    )
    state = read_state(catalog)
    reviewed, uncovered = state["securities"]
    reviewed["last_research_at"] = STAMP
    assessment = dict.fromkeys(contracts(catalog)["security_assessments"].columns, "")
    assessment.update(unscored_fields("Historical fixture has no component scoring evidence."))
    assessment.update(
        security_id=reviewed["security_id"],
        assessed_at=STAMP,
        valid_until="2026-11-17T17:00:00Z",
        research_status="supported",
        method="normalized_earnings",
        method_rationale="Cited per-share earning power.",
        currency="USD",
        horizon_months="12",
        thesis="Durable search demand.",
        key_assumptions="Demand remains stable.",
        downside="Competition reduces margins.",
        catalysts="Annual results.",
        invalidation_conditions="Sustained cash-flow decline.",
        confidence="medium",
        limitations="Forecast uncertainty.",
        source_ids=state["source_registry"][0]["source_id"],
    )
    for case, fair, probability in (
        ("bear", "80", "25"),
        ("base", "100", "50"),
        ("bull", "120", "25"),
    ):
        assessment.update(
            {
                f"{case}_fair_value": fair,
                f"{case}_probability_pct": probability,
                f"{case}_assumptions": "Cited demand and multiple.",
            }
        )
    state["security_assessments"].append(assessment)
    reviewed_assessment = assessment.copy()

    schedule_attention(state, [], [], now=NOW)
    assert len(state["research_queue"]) == 1
    task = state["research_queue"][0]
    assert task["entity_id"] == uncovered["security_id"]
    assert task["priority"] == "75"
    assert task["reasons"] == "missing_research|valuation_coverage_gap"
    assert state["security_assessments"] == [reviewed_assessment]
    assert not any(
        row["security_id"] == uncovered["security_id"] for row in state["security_assessments"]
    )

    queue = [task.copy()]
    schedule_attention(state, [], [], now=NOW)
    assert state["research_queue"] == queue


def test_manual_roles_are_explicit_and_import_preserves_existing_research(catalog: Path) -> None:
    value = company()
    accept(catalog, proposal([value], idea=False), manual=True)
    before = read_state(catalog)
    original = before["securities"][0].copy()
    assert original["research_role"] == "long"
    value.update(research_role="short_candidate", sector="Industrial automation")
    accept(catalog, proposal([value], idea=False), manual=True)
    after = read_state(catalog)
    updated = after["securities"][0]
    assert updated["research_role"] == "short_candidate"
    assert updated["sector"] == "Industrial automation"
    assert {k: v for k, v in updated.items() if k not in {"research_role", "sector"}} == {
        k: v for k, v in original.items() if k not in {"research_role", "sector"}
    }
    assert before["security_assessments"] == after["security_assessments"]
    assert before["research_queue"] == after["research_queue"]
    value.pop("research_role")
    value.pop("sector")
    accept(catalog, proposal([value], idea=False), manual=True)
    assert read_state(catalog)["securities"][0] == updated


@pytest.mark.parametrize("role,manual", [("short", True), ("", True), ("short_candidate", False)])
def test_invalid_or_automatic_bearish_roles_are_rejected(
    catalog: Path, role: str, manual: bool
) -> None:
    value = company()
    value["research_role"] = role
    before = read_state(catalog)
    with pytest.raises(ValueError, match="research role"):
        accept(catalog, proposal([value]), manual=manual)
    assert read_state(catalog) == before


def test_import_preserves_all_existing_identities_and_assessments(repository_root: Path) -> None:
    import copy

    before = read_state(repository_root)
    unchanged = copy.deepcopy(before)
    candidate, _, report = prepare_candidates(
        repository_root,
        before,
        proposal([company()], idea=False),
        now=NOW,
        observations=observations(),
        verify_identity=metadata,
        manual=True,
    )
    existing = {row["security_id"]: row for row in candidate["securities"]}
    assert all(existing[row["security_id"]] == row for row in before["securities"])
    assert candidate["security_assessments"] == before["security_assessments"]
    assert before == unchanged
    assert len(report["companies"]) == 1


def test_requested_bearish_universe_has_unique_verified_identities(repository_root: Path) -> None:
    active = set(["FCEL", "AI", "SPCE", "CIFR", "WULF", "BBAI", "APLD", "ONDS", "AEVA", "PDYN"])
    research_only = set(["KSCP", "MVIS", "PSNY", "PLUG", "ARQQ", "SPIR"])
    state = read_state(repository_root)
    selected = [row for row in state["securities"] if row["ticker"] in active | research_only]
    assert len(selected) == len({row["security_id"] for row in selected}) == 16
    assert len({row["issuer_id"] for row in selected}) == 16
    assert {row["ticker"] for row in selected} == active | research_only
    for row in selected:
        assert row["research_role"] == (
            "short_candidate" if row["ticker"] in active else "short_research_only"
        )
        assert row["currency"] == "USD" and row["venue_mic"] in {"XNAS", "XNYS"}
        assert row["discovery_provenance"].startswith("manual_import:source_")
        assert (repository_root / row["research_page"]).is_file()
    for request in (repository_root / "docs/short-research/imports").glob("batch-*.json"):
        assert len(json.loads(request.read_text())["companies"]) <= 2

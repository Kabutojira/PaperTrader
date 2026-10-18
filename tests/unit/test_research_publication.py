from __future__ import annotations

import copy
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.research_market import LATEST_COLUMNS, PRICE_COLUMNS, _write
from papertrader.research_publication import prepare_site, publish_views, snapshot
from papertrader.research_state import contracts, read_state, write_state

NOW = datetime(2026, 10, 18, 20, tzinfo=UTC)
STAMP = "2026-10-18T17:00:00Z"


@pytest.fixture
def publication(repository_root: Path, tmp_path: Path) -> Path:
    root = tmp_path / "publication"
    root.mkdir()
    shutil.copytree(repository_root / "schemas", root / "schemas")
    shutil.copy2(repository_root / "research.ini", root / "research.ini")
    schema = contracts(root)
    state = {name: [] for name in schema}
    source = dict.fromkeys(schema["source_registry"].columns, "")
    source.update(
        source_id="source1",
        url="https://issuer.example/filing",
        title="Annual filing",
        status="valid",
        checked_at=STAMP,
        content_hash="a" * 64,
    )
    state["source_registry"].append(source)
    for index in range(30):
        sid = f"security{index:02}"
        security = dict.fromkeys(schema["securities"].columns, "")
        security.update(
            security_id=sid,
            issuer_id=f"issuer{index:02}",
            company_name=f"Company {index}",
            instrument_name="Ordinary",
            instrument_type="equity",
            ticker=f"EX{index}",
            provider_symbol=f"EX{index}",
            venue_mic="XNYS",
            currency="USD",
            status="watching",
            research_status="researched",
            research_page=f"data/wiki/securities/{sid}.md",
        )
        state["securities"].append(security)
        page = root / security["research_page"]
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            f"---\nsecurity_id: {sid}\nissuer_id: issuer{index:02}\n---\n"
            "Original research. [Source](https://issuer.example/filing)\n"
        )
        assessment = dict.fromkeys(schema["security_assessments"].columns, "")
        assessment.update(
            security_id=sid,
            assessed_at=STAMP,
            valid_until="2026-11-17T17:00:00Z",
            research_status="supported",
            method="earnings",
            method_rationale="Cited multiple",
            currency="USD",
            horizon_months="12",
            thesis="Earning power",
            source_ids="source1",
            confidence="high",
            key_assumptions="Demand stable",
            downside="Demand falls",
            catalysts="Results",
            invalidation_conditions="Cash flow disappears",
        )
        fair = 160 + index if index < 15 else 10 + index
        for case, adjustment, probability in (("bear", -10, 25), ("base", 0, 50), ("bull", 10, 25)):
            assessment.update(
                {
                    f"{case}_fair_value": str(fair + adjustment),
                    f"{case}_probability_pct": str(probability),
                    f"{case}_assumptions": "Cited demand and multiple",
                }
            )
        state["security_assessments"].append(assessment)
    write_state(root, state)
    _write(
        root,
        "data/market/latest.csv",
        LATEST_COLUMNS,
        [
            dict.fromkeys(LATEST_COLUMNS, "")
            | {
                "security_id": row["security_id"],
                "provider_symbol": row["provider_symbol"],
                "venue_mic": "XNYS",
                "currency": "USD",
                "close": "100",
                "price_date": "2026-10-16",
                "status": "current",
            }
            for row in state["securities"]
        ],
    )
    return root


def test_rankings_are_bounded_ordered_native_currency_and_issuer_deduped(publication: Path) -> None:
    state = read_state(publication)
    state["securities"][14]["issuer_id"] = state["securities"][13]["issuer_id"]
    page = publication / state["securities"][14]["research_page"]
    page.write_text(page.read_text().replace("issuer14", "issuer13"))
    write_state(publication, state)
    before = copy.deepcopy(state)
    view = snapshot(publication, now=NOW)
    assert len(view["buys"]) == len(view["sells"]) == 10
    assert len({row["issuer_id"] for row in view["buys"]}) == 10
    assert view["buys"][0]["security_id"] == "security14"
    assert view["sells"][0]["security_id"] == "security15"
    assert all(
        row["currency"] == "USD" and row["price_date"] == "2026-10-16" for row in view["buys"]
    )
    assert read_state(publication) == before
    assert snapshot(publication, now=NOW) == view
    assert not (publication / ".cache").exists()
    assert publish_views(publication, now=NOW)
    assert (publication / ".cache").is_dir()
    assert publish_views(publication, now=NOW) == []
    home = (publication / "data/wiki/index.md").read_text()
    assert "Top 10 Buy" in home and "Top 10 Sell" in home
    assert "securities/security14" in home and "source" in home


def test_publication_rejects_symlink_transaction_directory(
    publication: Path, tmp_path: Path
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (publication / ".cache").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="unsafe research transaction directory"):
        publish_views(publication, now=NOW)

    assert not (outside / "research-transaction.json").exists()


@pytest.mark.parametrize(
    "failure",
    [
        "expired",
        "unsupported",
        "incomplete",
        "blocker",
        "source",
        "split",
        "stale_quote",
        "identity",
    ],
)
def test_ineligible_research_never_pads_rankings(publication: Path, failure: str) -> None:
    state = read_state(publication)
    for row in state["security_assessments"]:
        if failure == "expired":
            row["valid_until"] = "2026-10-18T18:00:00Z"
        elif failure == "unsupported":
            row["research_status"] = "valuation_unsupported"
            for case in ("bear", "base", "bull"):
                row[f"{case}_fair_value"] = row[f"{case}_probability_pct"] = ""
        elif failure == "incomplete":
            row["invalidation_conditions"] = ""
        elif failure == "blocker":
            row["limitations"] = "BLOCKER: earnings cannot be reconciled"
        elif failure == "split":
            _write(
                publication,
                f"data/market/prices/{row['security_id']}.csv",
                PRICE_COLUMNS,
                [dict.fromkeys(PRICE_COLUMNS, "") | {"date": "2026-10-19", "stock_splits": "2"}],
            )
    if failure == "source":
        state["source_registry"][0]["checked_at"] = "2026-10-01T00:00:00Z"
    write_state(publication, state)
    if failure in {"stale_quote", "identity"}:
        import csv

        rows = list(csv.DictReader((publication / "data/market/latest.csv").open()))
        for row in rows:
            row["price_date" if failure == "stale_quote" else "provider_symbol"] = (
                "2026-10-15" if failure == "stale_quote" else "WRONG"
            )
        _write(publication, "data/market/latest.csv", LATEST_COLUMNS, rows)
    view = snapshot(publication, now=NOW)
    assert view["buys"] == view["sells"] == []


def test_current_page_closure_excludes_retired_features_and_keeps_sources(
    publication: Path, tmp_path: Path
) -> None:
    wiki = publication / "data/wiki"
    source = wiki / "raw/filing.md"
    source.parent.mkdir()
    source.write_text("Primary facts.\n")
    retired = wiki / "strategies/old.md"
    retired.parent.mkdir()
    retired.write_text("Retired trading strategy")
    page = wiki / "securities/security00.md"
    page.write_text(
        page.read_text() + "\n[Relative source](../raw/filing.md) "
        "[Peer research](../securities/security01.md) "
        "[Company catalog](../security-catalog.md) "
        "[Escaped source](../../outside/filing.md) "
        "[[strategies/old|Old thesis]] [[missing|Missing lead]]\n"
    )
    output = tmp_path / "site-input"
    report = prepare_site(publication, output, now=NOW)
    assert report["pages"] >= 35
    assert (output / "raw/filing.md").read_bytes() == source.read_bytes()
    assert not (output / "strategies").exists()
    assert not (output / "model-portfolio.md").exists()
    assert (output / "data/top_buys.csv").is_file()
    rendered = (output / "securities/security00.md").read_text()
    assert "pre-research-only-20261018" in rendered and "[[missing" not in rendered
    assert "[Relative source](../raw/filing.md)" in rendered
    assert "[Peer research](../securities/security01.md)" in rendered
    assert "[Company catalog](../security-catalog.md)" in rendered
    assert "../../outside" not in rendered and "Escaped source" in rendered
    assert "https://issuer.example/filing" in rendered
    assert source.read_text() == "Primary facts.\n"
    with pytest.raises(ValueError, match="outside"):
        prepare_site(publication, publication / "stage", now=NOW)


def test_fresh_generated_views_override_stale_committed_link_targets(
    publication: Path, tmp_path: Path
) -> None:
    wiki = publication / "data/wiki"
    stale = "STALE GENERATED VIEW MUST NOT BE PUBLISHED"
    (wiki / "index.md").write_text(f"---\ntitle: Old home\n---\n{stale}\n")
    (wiki / "security-catalog.md").write_text(f"---\ntitle: Old catalog\n---\n{stale}\n")
    company = wiki / "securities/security00.md"
    company.write_text(
        company.read_text() + "\n[Current rankings](../index.md) "
        "[Company catalog](../security-catalog.md)\n"
    )

    output = tmp_path / "fresh-site-input"
    prepare_site(publication, output, now=NOW)

    home = (output / "index.md").read_text()
    catalog = (output / "security-catalog.md").read_text()
    rendered_company = (output / "securities/security00.md").read_text()
    assert stale not in home + catalog
    assert "# Company research and valuation" in home
    assert "# Companies" in catalog
    assert "[Current rankings](../index.md)" in rendered_company
    assert "[Company catalog](../security-catalog.md)" in rendered_company


def test_deployed_artifact_has_exact_revision_metadata_and_freshness_banner(
    publication: Path, tmp_path: Path
) -> None:
    import json

    output = tmp_path / "published"
    metadata = {
        "commit_sha": "a" * 40,
        "built_at": "2026-10-18T20:00:00Z",
        "run_url": "https://github.com/example/research/actions/runs/123",
    }
    prepare_site(publication, output, now=NOW, publication=metadata)
    home = (output / "index.md").read_text()
    assert "Published snapshot" in home and metadata["commit_sha"] in home
    assert metadata["built_at"] in home and metadata["run_url"] in home
    assert json.loads((output / "data/publication.json").read_text()) == metadata
    page = (output / "securities/security00.md").read_text()
    assert "Current research opinion:" in page and "strong_buy" in page
    assert "2026-11-17T17:00:00Z" in page
    assert (
        "Current research opinion:"
        not in (publication / "data/wiki/securities/security00.md").read_text()
    )
    state = read_state(publication)
    for row in state["security_assessments"]:
        row["valid_until"] = "2026-10-18T18:00:00Z"
    write_state(publication, state)
    stale = tmp_path / "stale"
    prepare_site(publication, stale, now=NOW)
    page = (stale / "securities/security00.md").read_text()
    assert "**unrated**" in page and "research_expired_or_future" in page

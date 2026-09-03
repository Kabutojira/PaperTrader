from __future__ import annotations

import json
import shutil
from pathlib import Path

from papertrader.tables import write_table
from papertrader.wiki import (
    TECHNICAL_CHART_END,
    TECHNICAL_CHART_START,
    lint_wiki,
    parse_research_charts,
    security_technical_chart_errors,
    sync_security_technical_charts,
    technical_chart_spec,
)


def _series_chart() -> dict[str, object]:
    return {
        "schema_version": 1,
        "chart_id": "revenue-and-income",
        "kind": "series",
        "title": "Revenue and GAAP net income",
        "description": "Comparable annual issuer results.",
        "as_of": "2026-06-30",
        "sources": [{"label": "Issuer annual report", "url": "https://example.com/filing"}],
        "x_axis": {"type": "category", "label": "Fiscal year", "values": ["2023", "2024", "2025"]},
        "y_axes": [{"label": "USD", "unit": "USD", "format": "currency", "currency": "USD"}],
        "series": [
            {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["100", "110", "125"]},
            {"name": "GAAP net income", "render": "line", "y_axis": 0, "values": ["8", "9", "12"]},
        ],
    }


def test_initial_wiki_is_clean(repository_root: Path) -> None:
    assert lint_wiki(repository_root / "data" / "wiki") == []


def test_research_chart_parser_accepts_declarative_decimal_series(
    repository_root: Path, tmp_path: Path
) -> None:
    page = tmp_path / "research.md"
    page.write_text(
        "## Visual evidence\n\n```echart\n" + json.dumps(_series_chart()) + "\n```\n",
        encoding="utf-8",
    )

    charts, errors = parse_research_charts(
        page, repository_root / "schemas" / "research_chart.schema.json"
    )

    assert errors == []
    assert [chart["chart_id"] for chart in charts] == ["revenue-and-income"]


def test_research_chart_parser_rejects_json_numbers_and_duplicate_ids(
    repository_root: Path, tmp_path: Path
) -> None:
    chart = _series_chart()
    chart["series"] = [{"name": "Revenue", "render": "bar", "y_axis": 0, "values": [100, 110, 125]}]
    block = "```echart\n" + json.dumps(chart) + "\n```\n"
    page = tmp_path / "research.md"
    page.write_text(block + block, encoding="utf-8")

    _, errors = parse_research_charts(
        page, repository_root / "schemas" / "research_chart.schema.json"
    )

    assert any("decimal strings" in error or "not valid" in error for error in errors)
    assert any("chart_id must be unique" in error for error in errors)


def test_research_chart_parser_accepts_stable_technical_reference(
    repository_root: Path, tmp_path: Path
) -> None:
    chart = technical_chart_spec("sec-fixture", "USD")
    page = tmp_path / "security.md"
    page.write_text(
        f"{TECHNICAL_CHART_START}\n```echart\n{json.dumps(chart)}\n```\n{TECHNICAL_CHART_END}\n",
        encoding="utf-8",
    )

    parsed, errors = parse_research_charts(
        page, repository_root / "schemas" / "research_chart.schema.json"
    )

    assert errors == []
    assert parsed == [chart]


def test_research_chart_parser_rejects_technical_path_identity_mismatch(
    repository_root: Path, tmp_path: Path
) -> None:
    chart = technical_chart_spec("sec-fixture", "USD")
    chart["data_path"] = "data/market/technical/sec-other.csv"
    page = tmp_path / "security.md"
    page.write_text(f"```echart\n{json.dumps(chart)}\n```\n", encoding="utf-8")

    _, errors = parse_research_charts(
        page, repository_root / "schemas" / "research_chart.schema.json"
    )

    assert any("data_path must match" in error for error in errors)


def test_security_technical_chart_sync_is_idempotent(
    sandbox_repository: Path,
) -> None:
    security_id = "sec-fixture"
    research_page = f"data/wiki/securities/{security_id}.md"
    write_table(
        sandbox_repository,
        "securities",
        [
            {
                "security_id": security_id,
                "issuer_id": "issuer-fixture",
                "company_name": "Fixture Corp",
                "instrument_name": "Fixture common stock",
                "instrument_type": "equity",
                "ticker": "FIX",
                "exchange_code": "XNYS",
                "venue_mic": "XNYS",
                "provider_symbol": "FIX",
                "broker_symbol": "",
                "currency": "USD",
                "country": "US",
                "sector": "Industrials",
                "industry": "Testing",
                "status": "watchlist",
                "watchlist_reason": "fixture",
                "research_summary": "fixture",
                "research_page": research_page,
                "last_research_at": "",
                "next_review_at": "",
                "created_at": "2026-09-02T00:00:00Z",
                "updated_at": "2026-09-02T00:00:00Z",
                "source": "test",
            }
        ],
    )
    page = sandbox_repository / research_page
    page.write_text(
        """---
title: Fixture security
type: security
status: maintained
tags: [security]
created: "2026-09-01"
updated: "2026-09-01"
provenance: test
---

# Fixture security

Research content stays unchanged.

## Sources

- Fixture source.
""",
        encoding="utf-8",
    )

    first = sync_security_technical_charts(sandbox_repository)
    first_text = page.read_text(encoding="utf-8")
    second = sync_security_technical_charts(sandbox_repository)

    assert first == (page,)
    assert second == ()
    assert page.read_text(encoding="utf-8") == first_text
    assert 'updated: "2026-09-01"' in first_text
    assert "Research content stays unchanged." in first_text
    assert first_text.index("# Fixture security") < first_text.index("## Visual evidence")
    assert first_text.index("## Visual evidence") < first_text.index(
        "Research content stays unchanged."
    )
    assert first_text.index("## Visual evidence") < first_text.index("## Sources")
    assert (
        security_technical_chart_errors(
            page,
            sandbox_repository / "schemas" / "research_chart.schema.json",
            security_id=security_id,
            currency="USD",
        )
        == []
    )


def test_security_technical_chart_sync_moves_existing_visual_section_after_title(
    sandbox_repository: Path,
) -> None:
    security_id = "sec-fixture"
    research_page = f"data/wiki/securities/{security_id}.md"
    write_table(
        sandbox_repository,
        "securities",
        [
            {
                "security_id": security_id,
                "issuer_id": "issuer-fixture",
                "company_name": "Fixture Corp",
                "instrument_name": "Fixture common stock",
                "instrument_type": "equity",
                "ticker": "FIX",
                "exchange_code": "XNYS",
                "venue_mic": "XNYS",
                "provider_symbol": "FIX",
                "broker_symbol": "",
                "currency": "USD",
                "country": "US",
                "sector": "Industrials",
                "industry": "Testing",
                "status": "watchlist",
                "watchlist_reason": "fixture",
                "research_summary": "fixture",
                "research_page": research_page,
                "last_research_at": "",
                "next_review_at": "",
                "created_at": "2026-09-02T00:00:00Z",
                "updated_at": "2026-09-02T00:00:00Z",
                "source": "test",
            }
        ],
    )
    chart = json.dumps(technical_chart_spec(security_id, "USD"), indent=2)
    page = sandbox_repository / research_page
    page.write_text(
        """---
title: Fixture security
type: security
status: maintained
tags: [security]
created: "2026-09-01"
updated: "2026-09-01"
provenance: test
---

# Fixture security

## Identity

Research content stays unchanged.

## Visual evidence

"""
        + f"{TECHNICAL_CHART_START}\n```echart\n{chart}\n```\n{TECHNICAL_CHART_END}\n\n"
        + "Analytical visual evidence stays in this section.\n",
        encoding="utf-8",
    )

    changed = sync_security_technical_charts(sandbox_repository)
    updated = page.read_text(encoding="utf-8")

    assert changed == (page,)
    assert updated.index("# Fixture security") < updated.index("## Visual evidence")
    assert updated.index("## Visual evidence") < updated.index("## Identity")
    assert updated.index(TECHNICAL_CHART_END) < updated.index(
        "Analytical visual evidence stays in this section."
    )
    assert sync_security_technical_charts(sandbox_repository) == ()
    assert (
        security_technical_chart_errors(
            page,
            sandbox_repository / "schemas" / "research_chart.schema.json",
            security_id=security_id,
            currency="USD",
        )
        == []
    )


def test_research_chart_schema_accepts_each_supported_family(
    repository_root: Path, tmp_path: Path
) -> None:
    common = {
        "schema_version": 1,
        "title": "Fixture chart",
        "description": "A bounded chart-family fixture.",
        "as_of": "2026-07-24",
        "sources": [{"label": "Fixture source"}],
    }
    axis = {"label": "Value", "unit": "units", "format": "decimal"}
    charts = [
        {
            **common,
            "chart_id": "scatter-fixture",
            "kind": "scatter",
            "x_axis": axis,
            "y_axis": axis,
            "points": [
                {"label": "A", "x": "1", "y": "2"},
                {"label": "B", "x": "2", "y": "3"},
                {"label": "C", "x": "3", "y": "5"},
            ],
        },
        {
            **common,
            "chart_id": "composition-fixture",
            "kind": "composition",
            "display": "donut",
            "axis": {"label": "Share", "unit": "%", "format": "percent"},
            "items": [
                {"label": "A", "value": "50"},
                {"label": "B", "value": "30"},
                {"label": "C", "value": "20"},
            ],
        },
        {
            **common,
            "chart_id": "candlestick-fixture",
            "kind": "candlestick",
            "currency": "USD",
            "rows": [
                {"at": "2026-07-21", "open": "10", "close": "11", "low": "9", "high": "12"},
                {"at": "2026-07-22", "open": "11", "close": "10", "low": "9", "high": "12"},
                {"at": "2026-07-23", "open": "10", "close": "12", "low": "10", "high": "13"},
            ],
        },
        {
            **common,
            "chart_id": "heatmap-fixture",
            "kind": "heatmap",
            "x_labels": ["A", "B"],
            "y_labels": ["Low", "High"],
            "axis": axis,
            "cells": [
                {"x": 0, "y": 0, "value": "1"},
                {"x": 1, "y": 0, "value": "2"},
                {"x": 0, "y": 1, "value": "3"},
                {"x": 1, "y": 1, "value": "4"},
            ],
        },
        {
            **common,
            "chart_id": "network-fixture",
            "kind": "network",
            "display": "sankey",
            "nodes": [{"id": "idea-a", "label": "Idea"}, {"id": "security-a", "label": "Security"}],
            "links": [{"source": "idea-a", "target": "security-a", "value": "1"}],
        },
    ]
    page = tmp_path / "families.md"
    page.write_text(
        "\n".join("```echart\n" + json.dumps(chart) + "\n```" for chart in charts),
        encoding="utf-8",
    )

    parsed, errors = parse_research_charts(
        page, repository_root / "schemas" / "research_chart.schema.json"
    )

    assert errors == []
    assert {chart["kind"] for chart in parsed} == {
        "scatter",
        "composition",
        "candlestick",
        "heatmap",
        "network",
    }


def test_wiki_log_uses_rotation_threshold_instead_of_page_size(
    repository_root: Path,
    tmp_path: Path,
) -> None:
    wiki = tmp_path / "wiki"
    shutil.copytree(repository_root / "data" / "wiki", wiki)
    log = wiki / "log.md"
    log.write_text(
        log.read_text(encoding="utf-8") + "\n" + ("bounded-log-entry " * 7000),
        encoding="utf-8",
    )

    assert log.stat().st_size > 100000
    assert lint_wiki(wiki) == []


def test_wiki_log_must_rotate_after_its_line_threshold(
    repository_root: Path,
    tmp_path: Path,
) -> None:
    wiki = tmp_path / "wiki"
    shutil.copytree(repository_root / "data" / "wiki", wiki)
    schema = wiki / "SCHEMA.md"
    schema.write_text(
        schema.read_text(encoding="utf-8").replace(
            "log_rotation_lines: 5000", "log_rotation_lines: 1"
        ),
        encoding="utf-8",
    )

    assert "log.md: log exceeds the 1-line rotation threshold" in lint_wiki(wiki)


def test_wiki_lint_reports_orphan_and_broken_link(repository_root: Path, tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    shutil.copytree(repository_root / "data" / "wiki", wiki)
    page = wiki / "ideas" / "idea-example.md"
    page.write_text(
        """---
title: Example idea
type: idea
status: maintained
tags: [idea]
created: "2026-07-24"
updated: "2026-07-24"
provenance: test
---

This links to [[missing-page]].
""",
        encoding="utf-8",
    )

    errors = lint_wiki(wiki)

    assert "ideas/idea-example.md: broken or ambiguous wikilink [[missing-page]]" in errors
    assert "ideas/idea-example.md: page is missing from index.md" in errors


def test_wiki_lint_does_not_require_retired_archive_pages_in_public_index(
    repository_root: Path, tmp_path: Path
) -> None:
    wiki = tmp_path / "wiki"
    shutil.copytree(repository_root / "data" / "wiki", wiki)
    page = wiki / "_archive" / "retired-example.md"
    page.write_text(
        """---
title: Retired example
type: meta
status: maintained
tags: [meta]
created: "2026-07-24"
updated: "2026-07-24"
provenance: test
---

This retired page is intentionally absent from the public index.
""",
        encoding="utf-8",
    )

    assert lint_wiki(wiki) == []

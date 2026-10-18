from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from papertrader.research_migration import remove_retired_technicals


def test_retired_chart_cleanup_preserves_frontmatter_research_and_analytical_chart() -> None:
    analysis = '```echart\n{"kind":"series","chart_id":"earnings"}\n```'
    text = (
        "---\nsecurity_id: sec1\nupdated: 2026-10-15\n---\n# Research\nCited thesis.\n"
        "<!-- papertrader:technical-chart:start -->\nold price graph\n"
        "<!-- papertrader:technical-chart:end -->\n" + analysis
    )
    result = remove_retired_technicals(text)
    assert result.startswith("---\nsecurity_id: sec1\nupdated: 2026-10-15\n---")
    assert "Cited thesis." in result and analysis in result and "old price graph" not in result
    assert remove_retired_technicals(result) == result
    with pytest.raises(ValueError, match="incomplete"):
        remove_retired_technicals(text.replace("<!-- papertrader:technical-chart:end -->", ""))


def test_original_pre_migration_technical_failure_remains_reproducible(
    repository_root: Path,
) -> None:
    path = "data/wiki/securities/security_33d9c44facc75c726c7d.md"
    text = subprocess.check_output(
        ["git", "show", f"pre-research-only-20261018:{path}"], cwd=repository_root
    ).decode()
    assert "market-technicals" in text
    assert "market-technicals" not in remove_retired_technicals(text)
    fixture = json.loads(
        (repository_root / "tests/fixtures/migration/assessment_page_ordering.json").read_text()
    )
    assert fixture["recorded_page_sha256"] != fixture["final_page_sha256"]

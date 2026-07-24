from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from papertrader.reports import NarrativeItem, generate_daily_report
from papertrader.telegram import escape_markdown_v2, split_message
from papertrader.wiki import lint_wiki


def test_daily_report_matches_reference_and_registers_one_canonical_page(
    sandbox_repository: Path,
    repository_root: Path,
) -> None:
    generated_at = datetime(2026, 7, 24, 22, tzinfo=UTC)
    arguments = {
        "run_id": "run-report",
        "run_status": "succeeded",
        "report_date": date(2026, 7, 24),
        "narrative_items": (
            NarrativeItem(
                "No material market move required a research follow-up.",
                ("data/market/latest.csv",),
            ),
        ),
        "github_report_url": (
            "https://github.com/example/PaperTrader/blob/main/"
            "data/wiki/daily-reports/daily-report_20260724.md"
        ),
        "generated_at": generated_at,
    }

    path = generate_daily_report(sandbox_repository, **arguments)
    generate_daily_report(sandbox_repository, **arguments)

    expected = (
        repository_root / "tests" / "reference_outputs" / "daily_report_empty.md"
    ).read_text(encoding="utf-8")
    assert path.read_text(encoding="utf-8") == expected
    index = (sandbox_repository / "data" / "wiki" / "index.md").read_text(encoding="utf-8")
    log = (sandbox_repository / "data" / "wiki" / "log.md").read_text(encoding="utf-8")
    assert index.count("[[daily-reports/daily-report_20260724") == 1
    assert log.count("Generated canonical [[daily-reports/daily-report_20260724]]") == 1
    assert lint_wiki(sandbox_repository / "data" / "wiki") == []


def test_telegram_markdown_escaping_and_bounded_lossless_splitting() -> None:
    raw = r"P/L +1.2% [paper] (only)! #safe \\"
    escaped = escape_markdown_v2(raw)

    assert escaped == r"P/L \+1\.2% \[paper\] \(only\)\! \#safe \\\\"
    message = "first line\n" + "word " * 20 + "tail"
    chunks = split_message(message, limit=25)
    assert "".join(chunks) == message
    assert all(len(chunk) <= 25 for chunk in chunks)

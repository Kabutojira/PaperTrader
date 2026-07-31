from __future__ import annotations

import shutil
from pathlib import Path

from papertrader.wiki import lint_wiki


def test_initial_wiki_is_clean(repository_root: Path) -> None:
    assert lint_wiki(repository_root / "data" / "wiki") == []


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

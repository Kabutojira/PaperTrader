from __future__ import annotations

from pathlib import Path

from papertrader.integrity import validate_integrity, validate_skills


def test_clean_scaffold_passes_integrity(
    repository_root: Path, paper_environment: dict[str, str]
) -> None:
    assert validate_integrity(repository_root, paper_environment) == []


def test_all_project_skills_are_discoverable(repository_root: Path) -> None:
    assert validate_skills(repository_root) == []

from __future__ import annotations

from pathlib import Path

from papertrader.integrity import load_csv_contracts, validate_integrity, validate_skills
from papertrader.tables import read_csv


def test_clean_scaffold_passes_integrity(
    repository_root: Path, paper_environment: dict[str, str]
) -> None:
    assert validate_integrity(repository_root, paper_environment) == []


def test_all_project_skills_are_discoverable(repository_root: Path) -> None:
    assert validate_skills(repository_root) == []


def test_sandbox_repository_excludes_mutable_runtime_state(sandbox_repository: Path) -> None:
    for contract in load_csv_contracts(sandbox_repository):
        path = sandbox_repository.joinpath(*contract.path.parts)
        assert read_csv(path, contract.columns) == []

    data = sandbox_repository / "data"
    assert list((data / "market" / "prices").glob("*.csv")) == []
    assert list((data / "logs").glob("operations-*.ndjson")) == []
    assert list((data / "runs").iterdir()) == []
    assert list((data / "wiki" / "daily-reports").iterdir()) == []

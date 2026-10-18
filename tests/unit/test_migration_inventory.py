from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import pytest

from papertrader.migration_inventory import baseline_inventory, export_inventory


def test_inventory_reads_only_pinned_git_data_and_exports_outside_checkout(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    tables = root / "data/tables"
    tables.mkdir(parents=True)
    securities = tables / "securities.csv"
    securities.write_text("security_id,issuer_id,ticker,venue_mic,currency\ns1,i1,FIX,XNAS,USD\n")
    page = root / "data/wiki/securities/s1.md"
    page.parent.mkdir(parents=True)
    page.write_text("[[ideas/i1]] [Issuer](https://example.test) source_fixture\n")
    for arguments in (
        ["init", "--quiet"],
        ["add", "data"],
        [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "-qm",
            "Seed",
        ],
    ):
        subprocess.run(["git", "-C", str(root), *arguments], check=True, capture_output=True)
    securities.unlink()
    page.write_text("Uncommitted page must remain untouched.\n")
    before = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"])
    first = baseline_inventory(root, "HEAD", as_of=date(2026, 10, 18))
    second = export_inventory(
        root, "HEAD", as_of=date(2026, 10, 18), output=tmp_path / "census.json"
    )
    assert first == second
    assert first["identities"][0]["security_id"] == "s1"
    assert first["wiki"]["data/wiki/securities/s1.md"]["source_ids"] == ["source_fixture"]
    assert not securities.exists()
    assert page.read_text() == "Uncommitted page must remain untouched.\n"
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]) == before
    with pytest.raises(ValueError, match="outside the repository"):
        export_inventory(root, "HEAD", as_of=date(2026, 10, 18), output=root / "census.json")

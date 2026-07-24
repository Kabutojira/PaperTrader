from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from papertrader.atomic_io import (
    UnsafeWriteError,
    atomic_write_csv,
    atomic_write_json,
    atomic_write_text,
)


def test_atomic_write_text_replaces_destination_without_temp_files(tmp_path: Path) -> None:
    destination = tmp_path / "state.txt"
    destination.write_text("old", encoding="utf-8")

    atomic_write_text(destination, "new\n", allowed_root=tmp_path)

    assert destination.read_text(encoding="utf-8") == "new\n"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["state.txt"]


def test_atomic_write_rejects_destination_outside_allowed_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()

    with pytest.raises(UnsafeWriteError, match="escapes allowed root"):
        atomic_write_text(tmp_path / "outside.txt", "no", allowed_root=allowed)


def test_atomic_write_rejects_symlink_component(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    (allowed / "linked").symlink_to(outside, target_is_directory=True)

    with pytest.raises(UnsafeWriteError, match="symlink destinations are forbidden"):
        atomic_write_text(allowed / "linked" / "state.txt", "no", allowed_root=allowed)


def test_atomic_json_is_stable_and_utf8(tmp_path: Path) -> None:
    destination = tmp_path / "result.json"

    atomic_write_json(destination, {"z": "caffè", "a": 1}, allowed_root=tmp_path)

    assert destination.read_text(encoding="utf-8") == '{\n  "a": 1,\n  "z": "caffè"\n}\n'
    assert json.loads(destination.read_text(encoding="utf-8")) == {"a": 1, "z": "caffè"}


def test_atomic_csv_uses_explicit_header_order(tmp_path: Path) -> None:
    destination = tmp_path / "table.csv"

    atomic_write_csv(
        destination,
        ("immutable_id", "value"),
        ({"value": "a,b", "immutable_id": "id-1"},),
        allowed_root=tmp_path,
    )

    with destination.open("r", encoding="utf-8", newline="") as handle:
        assert list(csv.reader(handle)) == [["immutable_id", "value"], ["id-1", "a,b"]]

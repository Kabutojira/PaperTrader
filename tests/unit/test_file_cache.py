from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from papertrader.file_cache import DISABLE_ENVIRONMENT_NAME, SignatureCache, file_signature


def _age(path: Path, seconds: int) -> None:
    stamp = time.time() - seconds
    os.utime(path, (stamp, stamp))


def test_cache_serves_settled_files_and_never_trusts_recent_writes(tmp_path: Path) -> None:
    path = tmp_path / "table.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    loads: list[int] = []
    cache: SignatureCache[str] = SignatureCache(capacity=4)

    def loader() -> str:
        loads.append(1)
        return path.read_text(encoding="utf-8")

    # A file written moments ago is racy: every read goes to disk.
    assert cache.get_or_load(path, "x", loader) == "a,b\n1,2\n"
    assert cache.get_or_load(path, "x", loader) == "a,b\n1,2\n"
    assert len(loads) == 2

    # Once the write has settled, the parsed value is memoised per file signature.
    _age(path, 10)
    assert cache.get_or_load(path, "x", loader) == "a,b\n1,2\n"
    assert cache.get_or_load(path, "x", loader) == "a,b\n1,2\n"
    assert len(loads) == 3
    assert cache.get_or_load(path, "other-columns", loader) == "a,b\n1,2\n"
    assert len(loads) == 4

    # An in-place rewrite of identical size is detected through mtime/ctime.
    path.write_text("a,b\n3,4\n", encoding="utf-8")
    assert cache.get_or_load(path, "x", loader) == "a,b\n3,4\n"
    _age(path, 10)
    assert cache.get_or_load(path, "x", loader) == "a,b\n3,4\n"
    assert cache.get_or_load(path, "x", loader) == "a,b\n3,4\n"
    assert len(loads) == 6

    # Missing files and the debug switch bypass the cache entirely.
    assert file_signature(tmp_path / "absent.csv") is None
    cache.clear()
    assert cache.get_or_load(path, "x", loader) == "a,b\n3,4\n"
    assert len(loads) == 7


def test_cache_can_be_disabled_by_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "table.csv"
    path.write_text("a\n1\n", encoding="utf-8")
    _age(path, 10)
    cache: SignatureCache[int] = SignatureCache()
    counter = iter(range(100))
    assert cache.get_or_load(path, "k", lambda: next(counter)) == 0
    assert cache.get_or_load(path, "k", lambda: next(counter)) == 0
    monkeypatch.setenv(DISABLE_ENVIRONMENT_NAME, "1")
    assert cache.get_or_load(path, "k", lambda: next(counter)) == 1
    assert cache.enabled() is False


def test_cache_evicts_least_recently_used_entries(tmp_path: Path) -> None:
    cache: SignatureCache[str] = SignatureCache(capacity=2)
    paths = []
    for index in range(3):
        path = tmp_path / f"{index}.csv"
        path.write_text(f"{index}\n", encoding="utf-8")
        _age(path, 10)
        paths.append(path)
    loads: list[str] = []

    def loader_for(path: Path):
        def loader() -> str:
            loads.append(path.name)
            return path.read_text(encoding="utf-8")

        return loader

    for path in paths:
        cache.get_or_load(path, "k", loader_for(path))
    assert loads == ["0.csv", "1.csv", "2.csv"]
    cache.get_or_load(paths[2], "k", loader_for(paths[2]))
    cache.get_or_load(paths[0], "k", loader_for(paths[0]))
    assert loads == ["0.csv", "1.csv", "2.csv", "0.csv"]

"""Recoverable logical transactions for current research, without revision chains."""

from __future__ import annotations

import base64
import contextlib
import fcntl
import json
from collections.abc import Iterator, Mapping
from pathlib import Path, PurePosixPath

from papertrader.atomic_io import atomic_write_bytes, atomic_write_json


def safe_path(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "data":
        raise ValueError("unsafe research destination")
    target = root / relative
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("symlink research destination")
    return target


@contextlib.contextmanager
def research_lock(root: Path) -> Iterator[None]:
    directory = root / ".cache"
    if directory.is_symlink():
        raise ValueError("unsafe research lock directory")
    directory.mkdir(exist_ok=True)
    lock = directory / "research.lock"
    if lock.is_symlink():
        raise ValueError("unsafe research lock")
    with lock.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            recover_transaction(root)
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def recover_transaction(root: Path) -> None:
    """An interrupted uncommitted write is rolled back before the next reader."""
    journal = root / ".cache/research-transaction.json"
    if journal.is_symlink():
        raise ValueError("unsafe transaction journal")
    if not journal.exists():
        return
    original = json.loads(journal.read_text())
    for relative, encoded in original.items():
        target = safe_path(root, relative)
        if encoded is None:
            target.unlink(missing_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_bytes(target, base64.b64decode(encoded, validate=True), allowed_root=root)
    journal.unlink()


def apply_files(root: Path, files: Mapping[str, bytes]) -> list[str]:
    """Caller holds research_lock. Stage final Markdown before matching tables.

    Readers use the same lock. The one temporary rollback journal is removed on
    success; accepted history exists only in the controller's subsequent Git commit.
    """
    changed = {
        name: body
        for name, body in files.items()
        if not safe_path(root, name).exists() or safe_path(root, name).read_bytes() != body
    }
    if not changed:
        return []
    originals = {
        name: base64.b64encode(safe_path(root, name).read_bytes()).decode()
        if safe_path(root, name).exists()
        else None
        for name in changed
    }
    journal = root / ".cache/research-transaction.json"
    if journal.exists() or journal.is_symlink():
        raise ValueError("unfinished research transaction")
    atomic_write_json(journal, originals, allowed_root=root)
    try:
        for name in sorted(changed, key=lambda name: (not name.endswith(".md"), name)):
            target = safe_path(root, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_bytes(target, changed[name], allowed_root=root)
    except BaseException:
        recover_transaction(root)
        raise
    journal.unlink()
    return sorted(changed)

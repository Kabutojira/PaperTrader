"""Content-addressed repository snapshots for post-agent change validation."""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "site/node_modules",
        "site/public",
        "site/quartz",
    }
)


@dataclass(frozen=True, slots=True)
class FileState:
    """One repository entry captured without following symlinks."""

    kind: str
    sha256: str
    size: int
    mode: int
    modified_ns: int

    @property
    def content_identity(self) -> tuple[str, str, int, int]:
        """Return the fields that constitute a persistent content change."""

        return (self.kind, self.sha256, self.size, self.mode)


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    """Immutable map of repository-relative paths to content identities."""

    files: dict[str, FileState]


@dataclass(frozen=True, slots=True)
class RepositoryDelta:
    """Created, modified, deleted, and type-changed paths between snapshots."""

    created: tuple[str, ...]
    modified: tuple[str, ...]
    deleted: tuple[str, ...]

    @property
    def changed(self) -> tuple[str, ...]:
        """Return every changed path in deterministic order."""

        return tuple(sorted((*self.created, *self.modified, *self.deleted)))


def _ignored(relative: Path) -> bool:
    value = relative.as_posix()
    return any(value == prefix or value.startswith(f"{prefix}/") for prefix in IGNORED_DIRECTORIES)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _state(path: Path) -> FileState:
    metadata = path.lstat()
    mode = stat.S_IMODE(metadata.st_mode)
    if stat.S_ISLNK(metadata.st_mode):
        target = os.readlink(path).encode("utf-8", errors="surrogateescape")
        return FileState(
            "symlink", hashlib.sha256(target).hexdigest(), len(target), mode, metadata.st_mtime_ns
        )
    if not stat.S_ISREG(metadata.st_mode):
        return FileState("special", "", metadata.st_size, mode, metadata.st_mtime_ns)
    return FileState("file", _hash_file(path), metadata.st_size, mode, metadata.st_mtime_ns)


def snapshot_repository(repository_root: Path) -> RepositorySnapshot:
    """Capture all persistent checkout files while excluding generated local caches."""

    root = repository_root.resolve(strict=True)
    files: dict[str, FileState] = {}
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_directories: list[str] = []
        for name in sorted(directory_names):
            path = current_path / name
            relative = path.relative_to(root)
            if _ignored(relative):
                continue
            if path.is_symlink():
                files[relative.as_posix()] = _state(path)
            else:
                kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            path = current_path / name
            relative = path.relative_to(root)
            if _ignored(relative) or path.suffix == ".pyc":
                continue
            files[relative.as_posix()] = _state(path)
    return RepositorySnapshot(files)


def compare_snapshots(before: RepositorySnapshot, after: RepositorySnapshot) -> RepositoryDelta:
    """Return content changes without treating timestamp-only touches as mutations."""

    before_paths = set(before.files)
    after_paths = set(after.files)
    created = tuple(sorted(after_paths - before_paths))
    deleted = tuple(sorted(before_paths - after_paths))
    modified = tuple(
        sorted(
            path
            for path in before_paths & after_paths
            if before.files[path].content_identity != after.files[path].content_identity
        )
    )
    return RepositoryDelta(created=created, modified=modified, deleted=deleted)

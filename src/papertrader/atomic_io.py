"""Git-safe, validated atomic file writes for deterministic state owners."""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path


class UnsafeWriteError(ValueError):
    """Raised when a destination escapes its allowed root or traverses a symlink."""


def _validate_destination(destination: Path, allowed_root: Path) -> tuple[Path, Path]:
    root = allowed_root.resolve(strict=True)
    target = destination if destination.is_absolute() else root / destination
    target = target.absolute()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise UnsafeWriteError(f"destination escapes allowed root: {target}") from exc

    relative = target.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise UnsafeWriteError(f"symlink destinations are forbidden: {current}")
    if not target.parent.is_dir():
        raise UnsafeWriteError(f"destination parent does not exist: {target.parent}")
    return target, root


def atomic_write_bytes(destination: Path, content: bytes, *, allowed_root: Path) -> None:
    """Write bytes beside the destination, fsync, and atomically replace it."""

    target, _ = _validate_destination(destination, allowed_root)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        directory_descriptor = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_text(
    destination: Path, content: str, *, allowed_root: Path, encoding: str = "utf-8"
) -> None:
    """Atomically write normalized text without silently changing caller content."""

    atomic_write_bytes(destination, content.encode(encoding), allowed_root=allowed_root)


def atomic_write_json(
    destination: Path, value: object, *, allowed_root: Path, indent: int = 2
) -> None:
    """Serialize canonical UTF-8 JSON and replace the destination atomically."""

    content = json.dumps(value, ensure_ascii=False, indent=indent, sort_keys=True) + "\n"
    atomic_write_text(destination, content, allowed_root=allowed_root)


def atomic_write_csv(
    destination: Path,
    columns: Sequence[str],
    rows: Iterable[Mapping[str, object]],
    *,
    allowed_root: Path,
) -> None:
    """Write an RFC 4180-compatible CSV using an explicit, stable column order."""

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(columns), extrasaction="raise")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    atomic_write_text(destination, buffer.getvalue(), allowed_root=allowed_root)

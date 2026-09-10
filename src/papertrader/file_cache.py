"""Process-local memoisation keyed by file identity for repeatedly parsed repository files.

The CLI re-reads the same CSV contracts and canonical tables dozens of times per invocation.
Every canonical writer replaces files atomically, so a file's ``(inode, size, mtime, ctime)``
signature changes on every durable write; caching parsed results under that signature is
therefore safe for the deterministic core while still invalidating on in-place edits made by
tests or humans.  Set ``PAPERTRADER_DISABLE_FILE_CACHE=1`` to bypass the cache when debugging.
"""

from __future__ import annotations

import os
import time
from collections import OrderedDict
from collections.abc import Callable, Hashable
from pathlib import Path

DISABLE_ENVIRONMENT_NAME = "PAPERTRADER_DISABLE_FILE_CACHE"
RACY_WINDOW_NS = 2_000_000_000


def file_signature(path: Path) -> tuple[str, int, int, int, int] | None:
    """Return an identity that changes whenever the file's bytes may have changed."""

    try:
        status = path.stat()
    except OSError:
        return None
    return (str(path), status.st_ino, status.st_size, status.st_mtime_ns, status.st_ctime_ns)


class SignatureCache[T]:
    """Bounded LRU cache whose keys embed a file signature."""

    def __init__(self, capacity: int = 256) -> None:
        self._capacity = capacity
        self._entries: OrderedDict[Hashable, T] = OrderedDict()

    def enabled(self) -> bool:
        return os.environ.get(DISABLE_ENVIRONMENT_NAME, "") not in {"1", "true", "yes"}

    def get_or_load(self, path: Path, extra: Hashable, loader: Callable[[], T]) -> T:
        """Return the cached value for ``path`` plus ``extra`` or load and remember it."""

        signature = file_signature(path)
        if signature is None or not self.enabled():
            return loader()
        if time.time_ns() - signature[3] < RACY_WINDOW_NS:
            # Kernel file timestamps are tick-granular, so two in-place writes of equal size
            # inside one tick share a signature. Like Git's racy-index rule, never trust a
            # cache entry for a file modified within the last two seconds.
            return loader()
        key = (signature, extra)
        cached = self._entries.get(key)
        if cached is not None:
            self._entries.move_to_end(key)
            return cached
        value = loader()
        self._entries[key] = value
        while len(self._entries) > self._capacity:
            self._entries.popitem(last=False)
        return value

    def clear(self) -> None:
        self._entries.clear()


__all__ = ["DISABLE_ENVIRONMENT_NAME", "SignatureCache", "file_signature"]

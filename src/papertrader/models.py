"""Small shared models for repository contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True, slots=True)
class CsvContract:
    """The canonical path and ordered columns for one CSV file."""

    name: str
    path: PurePosixPath
    columns: tuple[str, ...]
    append_only: bool = False
    generated: bool = False


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """A named validation result with deterministic error messages."""

    name: str
    errors: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors

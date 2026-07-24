#!/usr/bin/env python3
"""Build the Quartz site from the canonical repository-local wiki."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    wiki_path = (repository_root / "data" / "wiki").resolve()
    environment = os.environ.copy()
    environment["WIKI_PATH"] = str(wiki_path)
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=repository_root / "site",
        env=environment,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

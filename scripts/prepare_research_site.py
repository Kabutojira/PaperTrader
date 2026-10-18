#!/usr/bin/env python3
"""Stage only current research content for the pinned Quartz build."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from papertrader.research_publication import prepare_site

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repository", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
now = datetime.now(UTC)
publication = None
sha = os.environ.get("PAPERTRADER_PUBLICATION_SHA", "")
if sha:
    publication = dict(
        commit_sha=sha,
        built_at=now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        run_url=f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
    )
print(
    json.dumps(
        prepare_site(args.repository.resolve(), args.output, now=now, publication=publication)
    )
)

#!/usr/bin/env python3
"""Stage only current research content for the pinned Quartz build."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from papertrader.research_publication import prepare_site

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repository", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
print(json.dumps(prepare_site(args.repository.resolve(), args.output, now=datetime.now(UTC))))

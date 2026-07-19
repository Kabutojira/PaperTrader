#!/usr/bin/env python3
"""Repository-level entrypoint for the PaperTrader signal validator."""

from pathlib import Path
import runpy

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "Skills"
    / "papertrader"
    / "scripts"
    / "validate_signal.py"
)
runpy.run_path(str(SCRIPT), run_name="__main__")

#!/usr/bin/env python3
"""Validate the PaperTrader repository and Hermes skill scaffold."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    ROOT / "Skills",
    ROOT / "scripts",
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "INSTALL.md",
    ROOT / "Skills" / "papertrader" / "SKILL.md",
    ROOT / "Skills" / "papertrader" / "references" / "google-sheets-contract.md",
    ROOT / "Skills" / "papertrader" / "references" / "operating-rules.md",
    ROOT / "Skills" / "papertrader" / "templates" / "signal.schema.json",
    ROOT / "Skills" / "papertrader" / "templates" / "signal.example.json",
    ROOT / "Skills" / "papertrader" / "scripts" / "validate_signal.py",
    ROOT / "scripts" / "install-local.sh",
    ROOT / "scripts" / "check.sh",
    ROOT / "scripts" / "validate_signal.py",
]
REQUIRED_SKILL_SECTIONS = [
    "# PaperTrader Skill",
    "## When to Use",
    "## Prerequisites",
    "## How to Run",
    "## Quick Reference",
    "## Procedure",
    "## Pitfalls",
    "## Verification",
]


def parse_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return text[4:end]


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f"missing required path: {path.relative_to(ROOT)}")

    skill_path = ROOT / "Skills" / "papertrader" / "SKILL.md"
    if skill_path.exists():
        skill_text = skill_path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(skill_text)
        if frontmatter is None:
            errors.append("Skills/papertrader/SKILL.md has invalid or missing frontmatter")
        else:
            for key in ("name", "description", "version"):
                if not re.search(rf"(?m)^{re.escape(key)}:\s*\S+", frontmatter):
                    errors.append(f"SKILL.md frontmatter is missing {key}")
            if not re.search(r"(?m)^name:\s*papertrader\s*$", frontmatter):
                errors.append("SKILL.md name must be papertrader")
        for section in REQUIRED_SKILL_SECTIONS:
            if section not in skill_text:
                errors.append(f"SKILL.md is missing section: {section}")

    for relative in (
        "Skills/papertrader/templates/signal.schema.json",
        "Skills/papertrader/templates/signal.example.json",
    ):
        path = ROOT / relative
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{relative} is invalid JSON: {exc}")

    for relative in ("scripts/install-local.sh", "scripts/check.sh"):
        path = ROOT / relative
        if path.exists() and not path.stat().st_mode & 0o111:
            errors.append(f"{relative} is not executable")

    example = ROOT / "Skills" / "papertrader" / "templates" / "signal.example.json"
    validator = ROOT / "Skills" / "papertrader" / "scripts" / "validate_signal.py"
    if example.exists() and validator.exists():
        result = subprocess.run(
            [sys.executable, str(validator), str(example)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stdout + result.stderr).strip()
            errors.append(f"example signal did not validate: {details}")

    if errors:
        print("REPOSITORY INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("REPOSITORY VALID")
    print("- required files and directories are present")
    print("- Hermes SKILL.md frontmatter and sections are present")
    print("- JSON templates parse")
    print("- example signal passes deterministic validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

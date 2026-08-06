"""Strict checks for machine identities leaking into visible generated Markdown."""

from __future__ import annotations

import re
from pathlib import Path

MACHINE_ID = re.compile(
    r"(?:\b(?:security|relationship|strategy|opportunity|signal|position|operation|order|"
    r"execution|allocation_plan|snapshot|issue|decision)_[0-9a-f]{20}\b|"
    r"\bidea_(?!research\b)[a-z0-9][a-z0-9_]{5,}\b|"
    r"\bsource_(?!discovery\b)[A-Za-z0-9][A-Za-z0-9_-]{5,}\b|"
    r"\bdaily-[0-9]{8}T[0-9]{6}Z\b|"
    r"\b(?=[0-9A-HJKMNP-TV-Z]{0,25}[A-HJKMNP-TV-Z])[0-9A-HJKMNP-TV-Z]{26}\b|"
    r"\b[0-9a-f]{40,64}\b)"
)


def visible_markdown(markdown: str) -> str:
    """Remove frontmatter and link destinations while preserving user-visible labels."""

    body = markdown
    if body.startswith("---\n") and "\n---\n" in body[4:]:
        _, body = body[4:].split("\n---\n", maxsplit=1)
    body = body.replace("\\_", "_")
    body = re.sub(r"\]\([^\n)]*\)", "]()", body)
    body = re.sub(r"\[\[([^\]|\n]+)\|([^\]\n]+)\]\]", r"[[|\2]]", body)
    body = re.sub(r"\[\[([^\]\n]+)\]\]", r"[[\1]]", body)
    body = re.sub(r'(?i)\b(?:id|href)="[^"]*"', "", body)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    return body


def visible_machine_ids(markdown: str) -> tuple[str, ...]:
    """Return sorted unique forbidden identities from visible Markdown text."""

    return tuple(sorted(set(MACHINE_ID.findall(visible_markdown(markdown)))))


def validate_generated_public_markdown(repository_root: Path) -> list[str]:
    """Validate currently published/generated pages without rewriting historical reports."""

    wiki = repository_root / "data" / "wiki"
    paths = [
        wiki / name
        for name in (
            "index.md",
            "model-portfolio.md",
            "signals.md",
            "performance.md",
            "system-status.md",
            "security-catalog.md",
        )
    ]
    paths.extend(sorted((wiki / "inbox").glob("*.md")))
    paths.extend(sorted((wiki / "podcasts").glob("daily-podcast_*.md")))
    published = repository_root / "data" / "published" / "decision_snapshot.json"
    try:
        import json

        snapshot = json.loads(published.read_text(encoding="utf-8"))
        report_date = snapshot.get("report_date") if isinstance(snapshot, dict) else None
    except (OSError, ValueError):
        report_date = None
    if isinstance(report_date, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", report_date):
        paths.append(wiki / "daily-reports" / f"daily-report_{report_date.replace('-', '')}.md")
    errors: list[str] = []
    for path in sorted(set(paths)):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            leaked = visible_machine_ids(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            relative = path.relative_to(repository_root)
            errors.append(f"cannot validate generated public page {relative}: {exc}")
            continue
        if leaked:
            errors.append(
                f"generated public page exposes machine identities: "
                f"{path.relative_to(repository_root)}: {', '.join(leaked[:5])}"
            )
    return errors

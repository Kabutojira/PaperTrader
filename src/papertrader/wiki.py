"""Deterministic linting for the Hermes-native Markdown wiki."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from pathlib import Path, PurePosixPath

import yaml

from papertrader.atomic_io import atomic_write_text

WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\n]*?)?\]\]")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\n]*?\]\(([^)\s]+)\)")
FENCED_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)


class WikiFormatError(ValueError):
    """Raised when a maintained wiki page cannot be parsed."""


def _frontmatter(path: Path) -> tuple[Mapping[object, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise WikiFormatError("missing YAML frontmatter")
    raw_metadata, body = text[4:].split("\n---\n", maxsplit=1)
    metadata = yaml.safe_load(raw_metadata)
    if not isinstance(metadata, Mapping):
        raise WikiFormatError("frontmatter must be a mapping")
    return metadata, body


def _maintained_pages(wiki_root: Path) -> list[Path]:
    return [
        path
        for path in sorted(wiki_root.rglob("*.md"))
        if "raw" not in path.relative_to(wiki_root).parts
    ]


def _page_key(wiki_root: Path, path: Path) -> str:
    return PurePosixPath(path.relative_to(wiki_root)).with_suffix("").as_posix()


def _resolve_link(
    target: str,
    source_key: str,
    page_keys: set[str],
    keys_by_stem: Mapping[str, set[str]],
) -> str | None:
    normalized = target.removesuffix(".md").strip().lstrip("/")
    if not normalized or ".." in PurePosixPath(normalized).parts:
        return None
    if normalized in page_keys:
        return normalized
    source_parent = PurePosixPath(source_key).parent
    relative = (source_parent / normalized).as_posix()
    if relative in page_keys:
        return relative
    matches = keys_by_stem.get(PurePosixPath(normalized).name, set())
    if len(matches) == 1:
        return next(iter(matches))
    return None


def lint_wiki(wiki_root: Path) -> list[str]:
    """Check frontmatter, catalog coverage, wikilinks, tags, and bounded page size."""

    if not wiki_root.is_dir():
        return [f"wiki root does not exist: {wiki_root}"]
    pages = _maintained_pages(wiki_root)
    schema_path = wiki_root / "SCHEMA.md"
    index_path = wiki_root / "index.md"
    if schema_path not in pages or index_path not in pages:
        return ["wiki must contain SCHEMA.md and index.md"]

    try:
        schema_metadata, _ = _frontmatter(schema_path)
    except (OSError, UnicodeError, yaml.YAMLError, WikiFormatError) as exc:
        return [f"SCHEMA.md: {exc}"]

    required_raw = schema_metadata.get("required_frontmatter", [])
    known_tags_raw = schema_metadata.get("known_tags", [])
    max_page_bytes_raw = schema_metadata.get("max_page_bytes", 100000)
    if not isinstance(required_raw, list) or not all(
        isinstance(value, str) for value in required_raw
    ):
        return ["SCHEMA.md: required_frontmatter must be a list of strings"]
    if not isinstance(known_tags_raw, list) or not all(
        isinstance(value, str) for value in known_tags_raw
    ):
        return ["SCHEMA.md: known_tags must be a list of strings"]
    if not isinstance(max_page_bytes_raw, int) or max_page_bytes_raw <= 0:
        return ["SCHEMA.md: max_page_bytes must be a positive integer"]
    required = set(required_raw)
    known_tags = set(known_tags_raw)

    page_keys = {_page_key(wiki_root, path) for path in pages}
    keys_by_stem: dict[str, set[str]] = {}
    for key in page_keys:
        keys_by_stem.setdefault(PurePosixPath(key).name, set()).add(key)

    errors: list[str] = []
    resolved_links: dict[str, set[str]] = {}
    for path in pages:
        relative = path.relative_to(wiki_root).as_posix()
        key = _page_key(wiki_root, path)
        try:
            metadata, body = _frontmatter(path)
        except (OSError, UnicodeError, yaml.YAMLError, WikiFormatError) as exc:
            errors.append(f"{relative}: {exc}")
            continue
        missing = sorted(required.difference(str(item) for item in metadata))
        if missing:
            errors.append(f"{relative}: missing frontmatter fields: {', '.join(missing)}")
        tags = metadata.get("tags")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            errors.append(f"{relative}: tags must be a list of strings")
        else:
            unknown = sorted(set(tags).difference(known_tags))
            if unknown:
                errors.append(f"{relative}: unknown tags: {', '.join(unknown)}")
        if path.stat().st_size > max_page_bytes_raw:
            errors.append(f"{relative}: page exceeds {max_page_bytes_raw} bytes")

        body_without_code = FENCED_BLOCK_PATTERN.sub("", body)
        for target in WIKILINK_PATTERN.findall(body_without_code):
            resolved = _resolve_link(target, key, page_keys, keys_by_stem)
            if resolved is None:
                errors.append(f"{relative}: broken or ambiguous wikilink [[{target}]]")
            else:
                resolved_links.setdefault(key, set()).add(resolved)
        if key in {"index", "research-catalog"}:
            for target in MARKDOWN_LINK_PATTERN.findall(body_without_code):
                if target.startswith(("#", "http://", "https://", "mailto:", "tel:")):
                    continue
                resolved = _resolve_link(target, key, page_keys, keys_by_stem)
                if resolved is None:
                    errors.append(f"{relative}: broken or ambiguous Markdown link ({target})")
                else:
                    resolved_links.setdefault(key, set()).add(resolved)

    reachable = {"index"}
    pending = ["index"]
    while pending:
        source = pending.pop()
        for target in resolved_links.get(source, set()):
            if target not in reachable:
                reachable.add(target)
                pending.append(target)
    for key in sorted(page_keys.difference({"index"})):
        if key not in reachable:
            errors.append(f"{key}.md: page is missing from index.md")
    return errors


def _replace_frontmatter_date(text: str, value: date) -> str:
    """Update the required frontmatter date without reformatting the page body."""

    replacement = f'updated: "{value.isoformat()}"'
    updated, count = re.subn(
        r'^updated: "\d{4}-\d{2}-\d{2}"$', replacement, text, count=1, flags=re.M
    )
    if count != 1:
        raise WikiFormatError("page must contain one quoted updated frontmatter date")
    return updated


def register_wiki_page(
    wiki_root: Path,
    *,
    page_key: str,
    label: str,
    section: str,
    event: str,
    event_date: date,
) -> None:
    """Idempotently catalog a generated page and append a dated wiki-log entry."""

    if not page_key or ".." in PurePosixPath(page_key).parts or page_key.startswith("/"):
        raise WikiFormatError(f"invalid wiki page key: {page_key!r}")
    research_catalog_path = wiki_root / "research-catalog.md"
    index_path = (
        research_catalog_path if research_catalog_path.is_file() else wiki_root / "index.md"
    )
    index_text = index_path.read_text(encoding="utf-8")
    if label.startswith("["):
        escaped_label = label.replace("[", r"\[").replace("]", r"\]")
        link = f"- [{escaped_label}]({page_key})"
    else:
        link = f"- [[{page_key}|{label}]]"
    existing_wikilink = rf"^- \[\[{re.escape(page_key)}(?:\|[^\n]*?)?\]\]\n?"
    existing_markdown = rf"^- \[[^\n]*?\]\({re.escape(page_key)}\)\n?"
    existing_pattern = re.compile(
        f"(?:{existing_wikilink}|{existing_markdown})",
        flags=re.MULTILINE,
    )
    matches = tuple(existing_pattern.finditer(index_text))
    if matches and any(match.group(0).rstrip() != link for match in matches):
        index_text = existing_pattern.sub("", index_text)
    if link not in index_text:
        heading = f"## {section}\n"
        if heading not in index_text:
            index_text = index_text.rstrip() + f"\n\n{heading}\n{link}\n"
        else:
            start = index_text.index(heading) + len(heading)
            end = index_text.find("\n## ", start)
            end = len(index_text) if end == -1 else end
            body = index_text[start:end]
            body = re.sub(r"\n?No [^.]+\.\n?", "\n", body).strip("\n")
            links = sorted({*body.splitlines(), link})
            replacement = heading + "\n" + "\n".join(links) + "\n"
            index_text = index_text[: start - len(heading)] + replacement + index_text[end:]
        index_text = _replace_frontmatter_date(index_text, event_date)
        atomic_write_text(index_path, index_text, allowed_root=wiki_root)

    log_path = wiki_root / "log.md"
    log_text = log_path.read_text(encoding="utf-8")
    entry = f"- {event}"
    if entry not in log_text:
        heading = f"## {event_date.isoformat()}"
        if heading in log_text:
            insert_at = log_text.find("\n## ", log_text.index(heading) + len(heading))
            insert_at = len(log_text) if insert_at == -1 else insert_at
            block = log_text[log_text.index(heading) : insert_at].rstrip()
            updated_block = block + "\n\n" + entry + "\n"
            log_text = log_text[: log_text.index(heading)] + updated_block + log_text[insert_at:]
        else:
            log_text = log_text.rstrip() + f"\n\n{heading}\n\n{entry}\n"
        log_text = _replace_frontmatter_date(log_text, event_date)
        atomic_write_text(log_path, log_text, allowed_root=wiki_root)

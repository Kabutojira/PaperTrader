"""Deterministic linting for the Hermes-native Markdown wiki."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

import yaml

WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
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

    index_links = resolved_links.get("index", set())
    for key in sorted(page_keys.difference({"index"})):
        if key not in index_links:
            errors.append(f"{key}.md: page is missing from index.md")
    return errors

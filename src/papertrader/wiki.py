"""Deterministic linting for the Hermes-native Markdown wiki."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from papertrader.atomic_io import atomic_write_text
from papertrader.tables import read_table

WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\n]*?)?\]\]")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\n]*?\]\(([^)\s]+)\)")
FENCED_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
ECHART_BLOCK_PATTERN = re.compile(
    r"^```echart[ \t]*\r?\n(?P<payload>.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL
)
ECHART_OPEN_PATTERN = re.compile(r"^```(?P<info>echart[^\r\n]*)$", re.MULTILINE)
MAX_RESEARCH_CHARTS_PER_PAGE = 12
MAX_RESEARCH_CHART_BYTES = 24 * 1024
MAX_RESEARCH_CHART_NUMERIC_CELLS = 500
TECHNICAL_CHART_ID = "market-technicals"
TECHNICAL_CHART_START = "<!-- papertrader:technical-chart:start -->"
TECHNICAL_CHART_END = "<!-- papertrader:technical-chart:end -->"


class WikiFormatError(ValueError):
    """Raised when a maintained wiki page cannot be parsed."""


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON number {value!r} is forbidden")


def _research_chart_semantic_errors(chart: Mapping[str, object]) -> list[str]:
    errors: list[str] = []
    kind = chart.get("kind")
    decimal_pattern = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
    numeric_cells = 0

    def count_decimals(value: object) -> None:
        nonlocal numeric_cells
        if isinstance(value, str) and decimal_pattern.fullmatch(value):
            numeric_cells += 1
        elif isinstance(value, Mapping):
            for child in value.values():
                count_decimals(child)
        elif isinstance(value, list):
            for child in value:
                count_decimals(child)

    count_decimals(chart)
    if numeric_cells > MAX_RESEARCH_CHART_NUMERIC_CELLS:
        errors.append(
            f"contains {numeric_cells} numeric cells; maximum is {MAX_RESEARCH_CHART_NUMERIC_CELLS}"
        )

    if kind == "series":
        x_axis = chart.get("x_axis")
        x_values = x_axis.get("values", []) if isinstance(x_axis, Mapping) else []
        y_axes = chart.get("y_axes")
        series = chart.get("series")
        if isinstance(series, list):
            for index, item in enumerate(series):
                if not isinstance(item, Mapping):
                    continue
                values = item.get("values")
                if isinstance(values, list) and len(values) != len(x_values):
                    errors.append(f"series[{index}] values must align one-for-one with x_axis")
                y_axis = item.get("y_axis")
                if isinstance(y_axes, list) and isinstance(y_axis, int) and y_axis >= len(y_axes):
                    errors.append(f"series[{index}] references missing y_axis {y_axis}")
    elif kind == "composition":
        display = chart.get("display")
        axis = chart.get("axis")
        items = chart.get("items")
        if display == "donut" and isinstance(items, list) and len(items) > 5:
            errors.append("donut charts may contain at most five slices")
        if (
            display == "donut"
            and isinstance(axis, Mapping)
            and axis.get("format") == "percent"
            and isinstance(items, list)
        ):
            try:
                total = sum(
                    (Decimal(str(item["value"])) for item in items if isinstance(item, Mapping)),
                    Decimal("0"),
                )
            except (InvalidOperation, KeyError):
                total = Decimal("NaN")
            if total != Decimal("100"):
                errors.append("percent donut values must total exactly 100")
    elif kind == "candlestick":
        rows = chart.get("rows")
        if isinstance(rows, list):
            for index, row in enumerate(rows):
                if not isinstance(row, Mapping):
                    continue
                try:
                    opening = Decimal(str(row["open"]))
                    close = Decimal(str(row["close"]))
                    low = Decimal(str(row["low"]))
                    high = Decimal(str(row["high"]))
                except (InvalidOperation, KeyError):
                    continue
                if low > min(opening, close) or high < max(opening, close) or low > high:
                    errors.append(f"rows[{index}] has inconsistent OHLC bounds")
    elif kind == "technical":
        security_id = chart.get("security_id")
        data_path = chart.get("data_path")
        expected = (
            f"data/market/technical/{security_id}.csv" if isinstance(security_id, str) else ""
        )
        if data_path != expected:
            errors.append("technical data_path must match its immutable security_id")
    elif kind == "heatmap":
        x_labels = chart.get("x_labels")
        y_labels = chart.get("y_labels")
        cells = chart.get("cells")
        seen_cells: set[tuple[int, int]] = set()
        if isinstance(cells, list):
            for index, cell in enumerate(cells):
                if not isinstance(cell, Mapping):
                    continue
                x = cell.get("x")
                y = cell.get("y")
                if not isinstance(x, int) or not isinstance(y, int):
                    continue
                coordinate = (x, y)
                if coordinate in seen_cells:
                    errors.append(f"cells[{index}] duplicates coordinate {coordinate}")
                seen_cells.add(coordinate)
                if isinstance(x_labels, list) and x >= len(x_labels):
                    errors.append(f"cells[{index}] x index is outside x_labels")
                if isinstance(y_labels, list) and y >= len(y_labels):
                    errors.append(f"cells[{index}] y index is outside y_labels")
    elif kind == "network":
        nodes = chart.get("nodes")
        links = chart.get("links")
        node_ids = (
            {str(node["id"]) for node in nodes if isinstance(node, Mapping) and "id" in node}
            if isinstance(nodes, list)
            else set()
        )
        if isinstance(nodes, list) and len(node_ids) != len(nodes):
            errors.append("network node ids must be unique")
        if isinstance(links, list):
            for index, link in enumerate(links):
                if not isinstance(link, Mapping):
                    continue
                if link.get("source") not in node_ids or link.get("target") not in node_ids:
                    errors.append(f"links[{index}] must reference existing node ids")
    return errors


def parse_research_charts(
    path: Path, schema_path: Path
) -> tuple[list[dict[str, object]], list[str]]:
    """Parse and validate non-executable ECharts JSON fences in one Markdown page."""

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [], [f"cannot read chart blocks: {exc}"]
    matches = list(ECHART_BLOCK_PATTERN.finditer(text))
    errors: list[str] = []
    for opening in ECHART_OPEN_PATTERN.finditer(text):
        if opening.group("info").strip() != "echart":
            line = text.count("\n", 0, opening.start()) + 1
            errors.append(f"line {line}: ECharts fence language must be exactly 'echart'")
    if len(matches) > MAX_RESEARCH_CHARTS_PER_PAGE + 1:
        errors.append(
            f"contains {len(matches)} ECharts blocks; maximum is "
            f"{MAX_RESEARCH_CHARTS_PER_PAGE} analytical charts plus one technical chart"
        )
    if not matches:
        return [], errors
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return [], [*errors, f"cannot load research chart schema: {exc}"]

    charts: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for match in matches:
        payload = match.group("payload")
        line = text.count("\n", 0, match.start()) + 1
        if len(payload.encode("utf-8")) > MAX_RESEARCH_CHART_BYTES:
            errors.append(f"line {line}: ECharts block exceeds {MAX_RESEARCH_CHART_BYTES} bytes")
            continue
        try:
            value = json.loads(payload, parse_constant=_reject_json_constant)
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"line {line}: invalid ECharts JSON: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"line {line}: ECharts JSON must be an object")
            continue
        chart_id = value.get("chart_id")
        label = str(chart_id) if isinstance(chart_id, str) else f"line {line}"
        schema_errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
        for error in schema_errors:
            location = ".".join(str(part) for part in error.absolute_path) or "root"
            errors.append(f"chart {label}: {location}: {error.message}")
        if isinstance(chart_id, str):
            if chart_id in seen_ids:
                errors.append(f"chart {chart_id}: chart_id must be unique within the page")
            seen_ids.add(chart_id)
        for error in _research_chart_semantic_errors(value):
            errors.append(f"chart {label}: {error}")
        charts.append(value)
    technical_count = sum(chart.get("kind") == "technical" for chart in charts)
    analytical_count = len(charts) - technical_count
    if technical_count > 1:
        errors.append("a page may contain at most one technical chart")
    if analytical_count > MAX_RESEARCH_CHARTS_PER_PAGE:
        errors.append(
            f"contains {analytical_count} analytical charts; maximum is "
            f"{MAX_RESEARCH_CHARTS_PER_PAGE}"
        )
    return charts, errors


def technical_chart_spec(security_id: str, currency: str) -> dict[str, object]:
    """Return the stable reference-only technical chart specification."""

    return {
        "schema_version": 2,
        "chart_id": TECHNICAL_CHART_ID,
        "kind": "technical",
        "title": "One-year price, volume, and technical indicators",
        "description": (
            "Adjusted daily OHLC with Bollinger bands and moving averages, followed by "
            "volume, RSI, and MACD panels from the deterministic PaperTrader market cache."
        ),
        "security_id": security_id,
        "currency": currency,
        "price_basis": "adjusted",
        "window_days": 365,
        "data_path": f"data/market/technical/{security_id}.csv",
        "sources": [
            {"label": "Canonical PaperTrader price cache and deterministic TA-Lib projection"}
        ],
        "notes": [
            "Adjusted OHLC aligns price history with indicators calculated from adjusted close.",
            "Technical indicators are research alerts, not trade signals.",
        ],
    }


def _technical_chart_block(security_id: str, currency: str) -> str:
    payload = json.dumps(
        technical_chart_spec(security_id, currency),
        ensure_ascii=False,
        indent=2,
    )
    return (
        f"{TECHNICAL_CHART_START}\n"
        "This deterministic monitoring chart is derived from the repository-local market cache. "
        "Its source CSV remains downloadable and does not feed research scoring or trading "
        "state.\n\n"
        f"```echart\n{payload}\n```\n"
        f"{TECHNICAL_CHART_END}"
    )


def _visual_evidence_section_bounds(page_text: str) -> tuple[int, int] | None:
    heading = re.search(r"^## Visual evidence\s*$", page_text, flags=re.MULTILINE)
    if heading is None:
        return None
    following_heading = re.search(
        r"^##(?!#)\s+.+$",
        page_text[heading.end() :],
        flags=re.MULTILINE,
    )
    end = (
        heading.end() + following_heading.start()
        if following_heading is not None
        else len(page_text)
    )
    return heading.start(), end


def _move_visual_evidence_after_title(page_text: str) -> str:
    """Place the complete Visual evidence section immediately after the page H1."""

    bounds = _visual_evidence_section_bounds(page_text)
    if bounds is None:
        raise WikiFormatError("security page lacks a Visual evidence section")
    start, end = bounds
    section = page_text[start:end].strip("\n")
    before = page_text[:start].rstrip()
    after = page_text[end:].lstrip("\n")
    without_section = before + ("\n\n" + after if after else "\n")
    title = re.search(r"^#(?!#)\s+.+$", without_section, flags=re.MULTILINE)
    if title is None:
        raise WikiFormatError("security page lacks a level-one title")
    remainder = without_section[title.end() :].lstrip("\n")
    return (without_section[: title.end()] + f"\n\n{section}\n\n" + remainder).rstrip() + "\n"


def security_technical_chart_errors(
    path: Path,
    schema_path: Path,
    *,
    security_id: str,
    currency: str,
) -> list[str]:
    """Validate the one mandatory deterministic technical chart on a security page."""

    try:
        page_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read security technical chart: {exc}"]
    errors: list[str] = []
    if page_text.count(TECHNICAL_CHART_START) != 1 or page_text.count(TECHNICAL_CHART_END) != 1:
        errors.append("security page requires one marker-bounded technical chart")
    visual_bounds = _visual_evidence_section_bounds(page_text)
    if visual_bounds is None:
        errors.append("security page requires a Visual evidence section")
    else:
        title = re.search(r"^#(?!#)\s+.+$", page_text, flags=re.MULTILINE)
        if title is None or page_text[title.end() : visual_bounds[0]].strip():
            errors.append("security page requires Visual evidence immediately after its title")
    charts, chart_errors = parse_research_charts(path, schema_path)
    errors.extend(chart_errors)
    technical = [chart for chart in charts if chart.get("kind") == "technical"]
    if len(technical) != 1:
        errors.append("security page requires exactly one technical chart")
        return errors
    expected = technical_chart_spec(security_id, currency)
    if technical[0] != expected:
        errors.append("security technical chart does not match its canonical identity")
    return errors


def validate_security_technical_charts(repository_root: Path) -> list[str]:
    """Validate every security research page's stable technical chart reference."""

    schema_path = repository_root / "schemas" / "research_chart.schema.json"
    errors: list[str] = []
    for security in read_table(repository_root, "securities"):
        relative = security["research_page"]
        if not relative:
            continue
        pure = PurePosixPath(relative)
        if (
            pure.is_absolute()
            or ".." in pure.parts
            or pure.parts[:3] != ("data", "wiki", "securities")
            or pure.suffix != ".md"
        ):
            errors.append(f"invalid security research page path: {security['security_id']}")
            continue
        path = repository_root.joinpath(*pure.parts)
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing security research page: {security['security_id']}")
            continue
        errors.extend(
            f"{relative}: {error}"
            for error in security_technical_chart_errors(
                path,
                schema_path,
                security_id=security["security_id"],
                currency=security["currency"],
            )
        )
    return errors


def sync_security_technical_charts(repository_root: Path) -> tuple[Path, ...]:
    """Insert or repair stable technical chart references without changing research dates."""

    changed: list[Path] = []
    schema_path = repository_root / "schemas" / "research_chart.schema.json"
    marker_pattern = re.compile(
        rf"{re.escape(TECHNICAL_CHART_START)}.*?{re.escape(TECHNICAL_CHART_END)}",
        flags=re.DOTALL,
    )
    for security in read_table(repository_root, "securities"):
        relative = security["research_page"]
        if not relative:
            continue
        pure = PurePosixPath(relative)
        if (
            pure.is_absolute()
            or ".." in pure.parts
            or pure.parts[:3] != ("data", "wiki", "securities")
            or pure.suffix != ".md"
        ):
            raise WikiFormatError(f"invalid security research page path: {relative}")
        path = repository_root.joinpath(*pure.parts)
        if not path.is_file() or path.is_symlink():
            raise WikiFormatError(f"security research page is missing or unsafe: {relative}")
        page_text = path.read_text(encoding="utf-8")
        charts, chart_errors = parse_research_charts(path, schema_path)
        if chart_errors:
            raise WikiFormatError(f"cannot sync invalid chart page {relative}: {chart_errors[0]}")
        if any(chart.get("kind") == "technical" for chart in charts) and not (
            TECHNICAL_CHART_START in page_text and TECHNICAL_CHART_END in page_text
        ):
            raise WikiFormatError(f"unmarked technical chart cannot be replaced safely: {relative}")
        if page_text.count(TECHNICAL_CHART_START) > 1 or page_text.count(TECHNICAL_CHART_END) > 1:
            raise WikiFormatError(f"duplicate technical chart markers: {relative}")

        block = _technical_chart_block(security["security_id"], security["currency"])
        if TECHNICAL_CHART_START in page_text or TECHNICAL_CHART_END in page_text:
            if TECHNICAL_CHART_START not in page_text or TECHNICAL_CHART_END not in page_text:
                raise WikiFormatError(f"incomplete technical chart markers: {relative}")
            updated = marker_pattern.sub(block, page_text, count=1)
        else:
            heading = re.search(r"^## Visual evidence\s*$", page_text, flags=re.MULTILINE)
            if heading is not None:
                insertion = heading.end()
                updated = page_text[:insertion] + f"\n\n{block}" + page_text[insertion:]
            else:
                sources = re.search(r"^## Sources\s*$", page_text, flags=re.MULTILINE)
                section = f"## Visual evidence\n\n{block}\n\n"
                if sources is not None:
                    updated = page_text[: sources.start()] + section + page_text[sources.start() :]
                else:
                    updated = page_text.rstrip() + f"\n\n{section.rstrip()}\n"
        updated = _move_visual_evidence_after_title(updated)
        if updated != page_text:
            atomic_write_text(path, updated, allowed_root=repository_root)
            changed.append(path)
    return tuple(changed)


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


def _research_chart_schema_path(wiki_root: Path) -> Path:
    """Resolve the repository-owned chart schema for canonical or copied wiki trees."""

    canonical = wiki_root.parent.parent / "schemas" / "research_chart.schema.json"
    if canonical.is_file() and not canonical.is_symlink():
        return canonical
    return Path(__file__).resolve().parents[2] / "schemas" / "research_chart.schema.json"


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
    chart_schema = _research_chart_schema_path(wiki_root)
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
    log_rotation_lines_raw = schema_metadata.get("log_rotation_lines", 5000)
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
    if not isinstance(log_rotation_lines_raw, int) or log_rotation_lines_raw <= 0:
        return ["SCHEMA.md: log_rotation_lines must be a positive integer"]
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
        if relative == "log.md":
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            if line_count > log_rotation_lines_raw:
                errors.append(
                    f"{relative}: log exceeds the {log_rotation_lines_raw}-line rotation threshold"
                )
        elif path.stat().st_size > max_page_bytes_raw:
            errors.append(f"{relative}: page exceeds {max_page_bytes_raw} bytes")

        charts, chart_errors = parse_research_charts(path, chart_schema)
        del charts
        errors.extend(f"{relative}: {error}" for error in chart_errors)

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
        if key.startswith("_archive/"):
            continue
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

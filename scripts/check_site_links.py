#!/usr/bin/env python3
"""Fail when generated Quartz pages reference missing internal artifacts."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


@dataclass(frozen=True, order=True)
class BrokenSiteLink:
    source: str
    target: str
    resolved_path: str


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        self.links.extend(
            value for name, value in attrs if name in {"href", "src"} and value is not None
        )


def _canonical_base_url(base_url: str) -> str:
    value = base_url.strip().rstrip("/")
    if not value:
        raise ValueError("PAPERTRADER_BASE_URL must not be empty")
    if "://" not in value:
        value = f"https://{value}"
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"invalid PAPERTRADER_BASE_URL: {base_url}")
    return value


def _page_url(output_root: Path, page: Path, base_url: str) -> str:
    relative = page.relative_to(output_root)
    if relative.name == "index.html":
        route = relative.parent.as_posix()
        return urljoin(f"{base_url}/", f"{route}/" if route != "." else "")
    return urljoin(f"{base_url}/", relative.with_suffix("").as_posix())


def _target_exists(output_root: Path, target: str, *, directory_route: bool) -> bool:
    if not target:
        return (output_root / "index.html").is_file()
    path = output_root / target
    candidates = [path / "index.html"] if directory_route else [path]
    if not directory_route and not path.suffix:
        candidates.extend((path.with_suffix(".html"), path / "index.html"))
    return any(candidate.is_file() for candidate in candidates)


def find_broken_site_links(output_root: Path, base_url: str) -> list[BrokenSiteLink]:
    root = output_root.resolve()
    canonical_base = _canonical_base_url(base_url)
    parsed_base = urlsplit(canonical_base)
    base_path = unquote(parsed_base.path).rstrip("/")
    broken: set[BrokenSiteLink] = set()

    for page in sorted(root.rglob("*.html")):
        collector = _LinkCollector()
        collector.feed(page.read_text(encoding="utf-8"))
        source = page.relative_to(root).as_posix()
        page_url = _page_url(root, page, canonical_base)

        for target in collector.links:
            if target.startswith("#"):
                continue
            resolved = urlsplit(urljoin(page_url, target))
            if resolved.scheme not in {"http", "https"}:
                continue
            if resolved.netloc.lower() != parsed_base.netloc.lower():
                continue
            resolved_path = unquote(resolved.path)
            if resolved_path == base_path:
                relative_target = ""
            elif resolved_path.startswith(f"{base_path}/"):
                relative_target = resolved_path[len(base_path) :].lstrip("/")
            else:
                broken.add(BrokenSiteLink(source, target, resolved_path))
                continue
            if not _target_exists(
                root,
                relative_target,
                directory_route=resolved_path.endswith("/"),
            ):
                broken.add(BrokenSiteLink(source, target, resolved_path))

    return sorted(broken)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.environ.get("PAPERTRADER_SITE_OUTPUT", "public")),
    )
    parser.add_argument("--base-url", default=os.environ.get("PAPERTRADER_BASE_URL", ""))
    arguments = parser.parse_args(argv)
    if not arguments.output.is_dir():
        parser.error(f"Quartz output directory does not exist: {arguments.output}")
    try:
        broken = find_broken_site_links(arguments.output, arguments.base_url)
    except ValueError as exc:
        parser.error(str(exc))
    if broken:
        for link in broken:
            print(f"{link.source}: {link.target} -> {link.resolved_path}")
        print(f"ERROR: {len(broken)} broken internal site link(s)")
        return 1
    print("OK [site-links]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

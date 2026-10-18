"""Small read-only research web broker with one hard request/time budget."""

from __future__ import annotations

import hashlib
import io
import ipaddress
import json
import re
import socket
import time
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from pypdf import PdfReader, apply_configuration
from pypdf.errors import LimitReachedError

from papertrader.research_state import source_url

SOURCE_TEXT_LIMIT = 12_000
SOURCE_IDENTITY_MAX_ROWS = 5_000
SOURCE_IDENTITY_MAX_BYTES = 1_000_000
SOURCE_RESPONSE_MAX_BYTES = 2_000_000
PDF_MAX_PAGES = 250
PDF_WINDOW_PAGES = 3
PDF_STREAM_MAX_BYTES = 1_000_000
WEB_ERROR_CATEGORIES = {
    "budget_exhausted",
    "empty_content",
    "invalid_request",
    "pdf_invalid",
    "pdf_encrypted",
    "pdf_page_invalid",
    "pdf_too_complex",
    "source_too_large",
}


class ResearchWebError(ValueError):
    """A controller-owned category safe to return without provider content."""

    def __init__(self, category: str) -> None:
        if category not in WEB_ERROR_CATEGORIES:
            raise ValueError("unknown research web error category")
        self.category = category
        super().__init__(category)


def pdf_text(raw: bytes, page: int) -> tuple[str, dict[str, str]]:
    """Read a small text-only page window; never render, decrypt or execute assets."""
    try:
        with apply_configuration(
            maximum_declared_stream_length=PDF_STREAM_MAX_BYTES,
            array_based_stream_maximum_output_length=PDF_STREAM_MAX_BYTES,
            zlib_maximum_output_length=PDF_STREAM_MAX_BYTES,
            lzw_maximum_output_length=PDF_STREAM_MAX_BYTES,
            run_length_maximum_output_length=PDF_STREAM_MAX_BYTES,
            brotli_maximum_output_length=PDF_STREAM_MAX_BYTES,
            stream_decoding_work_maximum_length=4 * PDF_STREAM_MAX_BYTES,
            stream_parsing_work_maximum_count=100_000,
            page_tree_maximum_entries=PDF_MAX_PAGES,
            page_tree_maximum_depth=30,
            xform_maximum_invocations_per_extraction=1_000,
            jbig2dec_binary=None,
        ):
            reader = PdfReader(io.BytesIO(raw), root_object_recovery_limit=2_000)
            if reader.is_encrypted:
                raise ResearchWebError("pdf_encrypted")
            count = len(reader.pages)
            if count > PDF_MAX_PAGES:
                raise ResearchWebError("pdf_too_complex")
            if page > count:
                raise ResearchWebError("pdf_page_invalid")
            parts: list[str] = []
            read_pages: list[str] = []
            for index in range(page - 1, min(page - 1 + PDF_WINDOW_PAGES, count)):
                text = (
                    reader.pages[index].extract_text(
                        extraction_mode="layout", layout_mode_space_vertically=False
                    )
                    or ""
                )
                # Preserve rows and column separation without allowing page
                # positioning whitespace to consume the evidence window.
                text = "\n".join(
                    re.sub(r"[^\S\n]{2,}", "  ", line).strip() for line in text.splitlines()
                )
                parts.append(f"[PDF page {index + 1} of {count}]\n{text}")
                read_pages.append(str(index + 1))
                if sum(map(len, parts)) >= SOURCE_TEXT_LIMIT:
                    break
            if not any(part.split("\n", 1)[1].strip() for part in parts):
                raise ResearchWebError("empty_content")
            return "\n\n".join(parts)[:SOURCE_TEXT_LIMIT], {
                "pdf_page_count": str(count),
                "pdf_pages_read": ",".join(read_pages),
            }
    except ResearchWebError:
        raise
    except LimitReachedError:
        raise ResearchWebError("pdf_too_complex") from None
    except Exception:
        raise ResearchWebError("pdf_invalid") from None


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.source_links: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav", "header", "footer"}:
            self.hidden += 1
        if tag == "a":
            for key, value in attrs:
                if key != "href" or not value:
                    continue
                if (
                    len(self.source_links) < 20
                    and len(value) <= 2048
                    and any(
                        term in value.lower()
                        for term in (
                            "investor",
                            "financial",
                            "earnings",
                            "report",
                            "://ir.",
                            "/ir/",
                        )
                    )
                    and value not in self.source_links
                ):
                    self.source_links.append(value)
                if not self.hidden:
                    self.parts.append(" [link: " + value + "] ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "header", "footer"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def public_url(url: str) -> None:
    parsed = urlsplit(url)
    if not source_url(url) or parsed.port not in {None, 80, 443}:
        raise ResearchWebError("invalid_request")
    addresses = socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    if not addresses or any(
        not ipaddress.ip_address(address[4][0]).is_global for address in addresses
    ):
        raise ResearchWebError("invalid_request")


class ResearchWeb:
    def __init__(
        self,
        *,
        max_calls: int = 12,
        timeout: int = 15,
        runtime: int = 600,
        source_identities: list[dict[str, str]] | None = None,
    ) -> None:
        self.max_calls, self.timeout = max_calls, timeout
        self.deadline = time.monotonic() + runtime
        self.calls = 0
        self.observations: dict[str, dict[str, str]] = {}
        identities = [] if source_identities is None else source_identities
        if (
            not isinstance(identities, list)
            or len(identities) > SOURCE_IDENTITY_MAX_ROWS
            or len(json.dumps(identities, separators=(",", ":")).encode())
            > SOURCE_IDENTITY_MAX_BYTES
            or any(
                not isinstance(row, dict)
                or set(row) != {"source_id", "url", "license"}
                or any(not isinstance(value, str) for value in row.values())
                or not row["source_id"]
                or not source_url(row["url"])
                for row in identities
            )
        ):
            raise ValueError("invalid bounded source identity index")
        self.source_identities = {row["url"]: row.copy() for row in reversed(identities)}

    def source_identity(self, requested_url: str, final_url: str) -> dict[str, str]:
        existing = self.source_identities.get(requested_url) or self.source_identities.get(
            final_url
        )
        if existing:
            return existing.copy()
        return {
            "source_id": "source_web_" + hashlib.sha256(final_url.encode()).hexdigest()[:24],
            "url": final_url,
            "license": "link_only",
        }

    def take(self, url: str) -> None:
        if self.calls >= self.max_calls or time.monotonic() >= self.deadline:
            raise ResearchWebError("budget_exhausted")
        public_url(url)
        self.calls += 1

    def open(self, url: str, *, search: bool = False, page: int = 1) -> dict[str, str]:
        if type(page) is not int or not 1 <= page <= PDF_MAX_PAGES:
            raise ResearchWebError("pdf_page_invalid")
        self.take(url)
        broker = self

        class Redirects(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
                broker.take(newurl)
                return super().redirect_request(req, fp, code, msg, headers, newurl)

        request = Request(
            url,
            headers={
                "User-Agent": "PaperTrader research contact github.com/Kabutojira/PaperTrader"
            },
        )
        timeout = max(0.1, min(self.timeout, self.deadline - time.monotonic()))
        with build_opener(Redirects()).open(request, timeout=timeout) as response:
            raw = response.read(SOURCE_RESPONSE_MAX_BYTES + 1)
            if len(raw) > SOURCE_RESPONSE_MAX_BYTES:
                raise ResearchWebError("source_too_large")
            is_pdf = "pdf" in response.headers.get(
                "Content-Type", ""
            ).lower() or raw.lstrip().startswith(b"%PDF-")
            final_url = response.geturl()
        details: dict[str, str] = {}
        links: list[str] = []
        if is_pdf:
            text, details = pdf_text(raw, page)
        else:
            if page != 1:
                raise ResearchWebError("pdf_page_invalid")
            parser = _Text()
            parser.feed(raw.decode("utf-8", errors="replace"))
            text = " ".join(" ".join(parser.parts).split())[:SOURCE_TEXT_LIMIT]
            links = parser.source_links
        if not text:
            raise ResearchWebError("empty_content")
        checked = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
        observation = dict(
            url=url,
            final_url=final_url,
            content_hash=hashlib.sha256(raw).hexdigest(),
            checked_at=checked,
            # This bounded excerpt exists only in the controller/worker response so
            # the deterministic validator can detect copied source prose. It is
            # never written to the source registry or a public artifact.
            source_text=text[:SOURCE_TEXT_LIMIT],
            **details,
        )
        if not search:
            previous = self.observations.get(url) or self.observations.get(final_url)
            if previous:
                # Compare against every excerpt seen in this operation, including
                # earlier PDF windows. At most max_calls bounded windows exist.
                observation["source_text"] = previous["source_text"]
                if text not in previous["source_text"]:
                    observation["source_text"] += "\n\n" + text
            identity = self.source_identity(url, final_url)
            observation.update(
                source_id=identity["source_id"],
                source_url=identity["url"],
                source_license=identity["license"],
            )
            self.observations[url] = observation
            self.observations[final_url] = {**observation, "url": final_url}
        return {
            **{key: value for key, value in observation.items() if key != "source_text"},
            "source_links": "\n".join(
                link for value in links if source_url(link := urljoin(final_url, value))
            ),
            "untrusted_source_text": text[:SOURCE_TEXT_LIMIT],
        }

    def tool(self, args: dict[str, object], **_: object) -> str:
        try:
            if args.get("action") == "search":
                query = args.get("query", "")
                if not isinstance(query, str) or not 1 <= len(query) <= 500:
                    raise ResearchWebError("invalid_request")
                return json.dumps(
                    self.open(
                        "https://www.bing.com/search?" + urlencode({"format": "rss", "q": query}),
                        search=True,
                    )
                )
            if args.get("action") != "open":
                raise ResearchWebError("invalid_request")
            url, page = args.get("url", ""), args.get("page", 1)
            if not isinstance(url, str) or type(page) is not int:
                raise ResearchWebError("invalid_request")
            return json.dumps(self.open(urljoin("", url), page=page))
        except HTTPError as exc:
            # Numeric HTTP status is trustworthy; response bodies and reasons are not.
            status = exc.code if isinstance(exc.code, int) and 100 <= exc.code <= 599 else None
            result: dict[str, int | str] = {
                "error": "http_error",
                "requests_used": self.calls,
            }
            if status is not None:
                result["http_status"] = status
            return json.dumps(result)
        except ResearchWebError as exc:
            return json.dumps({"error": exc.category, "requests_used": self.calls})
        except Exception:
            # No exception text, source content, provider body or secret enters the model response.
            return json.dumps({"error": "request_failed", "requests_used": self.calls})

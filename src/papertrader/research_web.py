"""Small read-only research web broker with one hard request/time budget."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import socket
import time
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from papertrader.research_state import source_url

SOURCE_TEXT_LIMIT = 12_000
SOURCE_IDENTITY_MAX_ROWS = 5_000
SOURCE_IDENTITY_MAX_BYTES = 1_000_000
SOURCE_RESPONSE_MAX_BYTES = 2_000_000
WEB_ERROR_CATEGORIES = {
    "budget_exhausted",
    "empty_content",
    "invalid_request",
    "pdf_unsupported",
    "source_too_large",
}


class ResearchWebError(ValueError):
    """A controller-owned category safe to return without provider content."""

    def __init__(self, category: str) -> None:
        if category not in WEB_ERROR_CATEGORIES:
            raise ValueError("unknown research web error category")
        self.category = category
        super().__init__(category)


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

    def open(self, url: str, *, search: bool = False) -> dict[str, str]:
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
            if "pdf" in response.headers.get("Content-Type", "").lower():
                raise ResearchWebError("pdf_unsupported")
            content = raw.decode("utf-8", errors="replace")
            final_url = response.geturl()
        parser = _Text()
        parser.feed(content)
        text = " ".join(" ".join(parser.parts).split())
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
        )
        if not search:
            identity = self.source_identity(url, final_url)
            observation.update(
                source_id=identity["source_id"],
                source_url=identity["url"],
                source_license=identity["license"],
            )
            self.observations[url] = observation
            self.observations[final_url] = {**observation, "url": final_url}
        return {
            **observation,
            "source_links": "\n".join(
                link
                for value in parser.source_links
                if source_url(link := urljoin(final_url, value))
            ),
            "untrusted_source_text": text[:SOURCE_TEXT_LIMIT],
        }

    def tool(self, args: dict[str, str], **_: object) -> str:
        try:
            if args.get("action") == "search":
                query = args.get("query", "")
                if not 1 <= len(query) <= 500:
                    raise ResearchWebError("invalid_request")
                return json.dumps(
                    self.open(
                        "https://www.bing.com/search?" + urlencode({"format": "rss", "q": query}),
                        search=True,
                    )
                )
            if args.get("action") != "open":
                raise ResearchWebError("invalid_request")
            return json.dumps(self.open(urljoin("", args.get("url", ""))))
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

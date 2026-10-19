"""Bounded windows for long public HTML financial sources."""

from __future__ import annotations

import hashlib
import json

import pytest

from papertrader.research_results import _reject_copied_source_text
from papertrader.research_web import SOURCE_TEXT_LIMIT, ResearchWeb

URL = "https://issuer.example/quarterly-results"
EARLY_WORDS = " ".join(f"introductory{i}" for i in range(30))
LATE_FINANCIALS = "Quarter-end cash was 168 million and diluted shares were 72 million."


def long_financial_html() -> bytes:
    filler = "Operating narrative and customer program discussion continued. " * 300
    return (
        "<html><body><header>Issuer navigation</header><main>"
        f"<p>{EARLY_WORDS}</p><p>{filler}</p>"
        f"<table><tr><td>{LATE_FINANCIALS}</td></tr></table>"
        "</main><footer>Legal navigation</footer></body></html>"
    ).encode()


def broker(monkeypatch: pytest.MonkeyPatch, raw: bytes, *, max_calls: int = 12) -> ResearchWeb:
    class Response:
        def __init__(self) -> None:
            self.headers = {"Content-Type": "text/html; charset=utf-8"}

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self, limit: int) -> bytes:
            return raw[:limit]

        def geturl(self) -> str:
            return URL

    class Opener:
        def open(self, *_: object, **__: object) -> Response:
            return Response()

    monkeypatch.setattr("papertrader.research_web.public_url", lambda _: None)
    monkeypatch.setattr("papertrader.research_web.build_opener", lambda *_: Opener())
    return ResearchWeb(
        max_calls=max_calls,
        source_identities=[{"source_id": "source1", "url": URL, "license": "link_only"}],
    )


def test_long_html_windows_reach_late_financials_and_retain_early_copy_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = long_financial_html()
    web = broker(monkeypatch, raw)

    first = json.loads(web.tool({"action": "open", "url": URL}))
    later = json.loads(web.tool({"action": "open", "url": URL, "page": 2}))

    assert first["html_window_index"] == "1"
    assert first["html_window_count"] == later["html_window_count"] == "2"
    assert first["html_text_truncated"] == later["html_text_truncated"] == "true"
    assert LATE_FINANCIALS not in first["untrusted_source_text"]
    assert LATE_FINANCIALS in later["untrusted_source_text"]
    assert len(first["untrusted_source_text"]) <= SOURCE_TEXT_LIMIT
    assert len(later["untrusted_source_text"]) <= SOURCE_TEXT_LIMIT
    assert first["source_id"] == later["source_id"] == "source1"
    assert first["content_hash"] == later["content_hash"] == hashlib.sha256(raw).hexdigest()
    assert "source_text" not in first and "source_text" not in later
    assert EARLY_WORDS in web.observations[URL]["source_text"]
    assert LATE_FINANCIALS in web.observations[URL]["source_text"]
    with pytest.raises(ValueError, match="copies more than 25"):
        _reject_copied_source_text(
            EARLY_WORDS,
            {"license": "link_only"},
            web.observations[URL],
            trusted_prior=None,
        )


def test_html_window_page_validation_and_request_budget_are_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = long_financial_html()
    invalid = broker(monkeypatch, raw)
    assert json.loads(invalid.tool({"action": "open", "url": URL, "page": 3})) == {
        "error": "pdf_page_invalid",
        "requests_used": 1,
    }
    assert invalid.observations == {}

    limited = broker(monkeypatch, raw, max_calls=1)
    assert "untrusted_source_text" in json.loads(limited.tool({"action": "open", "url": URL}))
    assert json.loads(limited.tool({"action": "open", "url": URL, "page": 2})) == {
        "error": "budget_exhausted",
        "requests_used": 1,
    }

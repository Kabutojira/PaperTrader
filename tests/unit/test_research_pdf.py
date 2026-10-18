"""Bounded primary-PDF reading without rendering or public raw-content storage."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from papertrader.research_agent import _stage_worker
from papertrader.research_results import _reject_copied_source_text
from papertrader.research_web import PDF_MAX_PAGES, PDF_STREAM_MAX_BYTES, ResearchWeb

URL = "https://issuer.example/shareholder-letter.pdf"
WORDS = " ".join(f"evidence{i}" for i in range(30))


def document(*, pages: int = 5, encrypt: bool = False, huge: bool = False) -> bytes:
    writer = PdfWriter()
    for number in range(1, pages + 1):
        page = writer.add_blank_page(width=612, height=792)
        font = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
        )
        content = DecodedStreamObject()
        text = WORDS if number == 1 else f"Financial statements page {number}"
        content.set_data(
            f"BT /F1 10 Tf 20 700 Td ({text}) Tj ET\n".encode()
            + (b" " * (PDF_STREAM_MAX_BYTES + 1) if huge else b"")
        )
        page[NameObject("/Contents")] = content.flate_encode() if huge else content
    if encrypt:
        writer.encrypt("not-an-authorized-password")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def broker(monkeypatch: pytest.MonkeyPatch, raw: bytes, *, calls: int = 4) -> ResearchWeb:
    class Response:
        def __init__(self) -> None:
            self.headers = {"Content-Type": "application/pdf"}

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_: object) -> None:
            pass

        def read(self, limit: int) -> bytes:
            return raw[:limit]

        def geturl(self) -> str:
            return URL

    class Opener:
        def open(self, *_: object, **__: object) -> Response:
            return Response()

    monkeypatch.setattr("papertrader.research_web.public_url", lambda _: None)
    monkeypatch.setattr("papertrader.research_web.build_opener", lambda *_: Opener())
    return ResearchWeb(max_calls=calls)


def test_pdf_windows_retain_source_identity_and_all_seen_copyright_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = document()
    web = broker(monkeypatch, raw, calls=3)
    first = json.loads(web.tool({"action": "open", "url": URL}))
    later = json.loads(web.tool({"action": "open", "url": URL, "page": 4}))
    repeated = json.loads(web.tool({"action": "open", "url": URL}))

    assert first["pdf_page_count"] == "5"
    assert first["pdf_pages_read"] == "1,2,3"
    assert "Financial statements page 4" not in first["untrusted_source_text"]
    assert later["pdf_pages_read"] == "4,5"
    assert "Financial statements page 5" in later["untrusted_source_text"]
    assert first["source_id"] == later["source_id"] == repeated["source_id"]
    assert first["content_hash"] == hashlib.sha256(raw).hexdigest()
    assert "source_text" not in first  # The model receives one bounded excerpt.
    assert WORDS in web.observations[URL]["source_text"]
    assert "Financial statements page 5" in web.observations[URL]["source_text"]
    with pytest.raises(ValueError, match="copies more than 25"):
        _reject_copied_source_text(
            WORDS,
            {"license": "link_only"},
            web.observations[URL],
            trusted_prior=None,
        )
    assert json.loads(web.tool({"action": "open", "url": URL, "page": 4})) == {
        "error": "budget_exhausted",
        "requests_used": 3,
    }


@pytest.mark.parametrize(
    ("raw", "page", "expected", "requests"),
    [
        (b"malformed provider secret", 1, "pdf_invalid", 1),
        (document(encrypt=True), 1, "pdf_encrypted", 1),
        (document(pages=1, huge=True), 1, "pdf_too_complex", 1),
        (document(pages=PDF_MAX_PAGES + 1), 1, "pdf_too_complex", 1),
        (document(), 6, "pdf_page_invalid", 1),
        (document(), 0, "pdf_page_invalid", 0),
    ],
)
def test_bad_pdf_is_bounded_redacted_and_never_accepted_as_evidence(
    monkeypatch: pytest.MonkeyPatch, raw: bytes, page: int, expected: str, requests: int
) -> None:
    web = broker(monkeypatch, raw)
    assert json.loads(web.tool({"action": "open", "url": URL, "page": page})) == {
        "error": expected,
        "requests_used": requests,
    }
    assert web.observations == {}


def test_staged_worker_can_import_pinned_pdf_reader_without_controller_environment(
    repository_root: Path, tmp_path: Path
) -> None:
    directory = tmp_path / "isolated"
    directory.mkdir()
    code = _stage_worker(repository_root, directory)
    assert (code / "pypdf/__init__.py").is_file()
    assert not (code / "papertrader/research_runtime.py").exists()
    assert not (code / ".git").exists()
    pdf = directory / "test.pdf"
    pdf.write_bytes(document(pages=1))
    program = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from papertrader.research_web import pdf_text;"
        "from pathlib import Path;"
        "text,meta=pdf_text(Path(sys.argv[2]).read_bytes(),1);"
        "assert 'evidence0' in text and meta['pdf_page_count']=='1'"
    )
    # yaml is an existing Hermes dependency, not a new reader dependency. Supply
    # it explicitly because -S excludes every installed site-packages directory.
    shutil.copytree(Path(yaml.__file__).parent, code / "yaml")
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", program, str(code), str(pdf)],
        cwd=directory,
        env={},
        capture_output=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()

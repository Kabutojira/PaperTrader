from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE_URL = "example.github.io/PaperTrader"
SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_site_links.py"


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _check(output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(output), "--base-url", BASE_URL],
        check=False,
        capture_output=True,
        text=True,
    )


def test_generated_site_links_resolve_within_project_pages_subpath(tmp_path: Path) -> None:
    _write(
        tmp_path / "index.html",
        """
        <a href="./published">Published</a>
        <a href="https://example.github.io/PaperTrader/reports/">Reports</a>
        <a href="https://github.com/example/PaperTrader">Source</a>
        <a href="#section">Section</a>
        <script src="./static/app.js"></script>
        """,
    )
    _write(tmp_path / "published.html")
    _write(tmp_path / "reports" / "index.html")
    _write(tmp_path / "static" / "app.js")

    result = _check(tmp_path)

    assert result.returncode == 0
    assert result.stdout == "OK [site-links]\n"


def test_generated_site_links_report_missing_and_outside_base_targets(tmp_path: Path) -> None:
    _write(
        tmp_path / "daily-reports" / "report.html",
        """
        <a href="../inbox/missing-packet">Missing packet</a>
        <a href="/outside-project">Wrong root</a>
        <script src="../static/missing.js"></script>
        """,
    )
    _write(tmp_path / "static" / "missing.html")

    result = _check(tmp_path)

    assert result.returncode == 1
    assert result.stdout.splitlines() == [
        "daily-reports/report.html: ../inbox/missing-packet -> /PaperTrader/inbox/missing-packet",
        "daily-reports/report.html: ../static/missing.js -> /PaperTrader/static/missing.js",
        "daily-reports/report.html: /outside-project -> /outside-project",
        "ERROR: 3 broken internal site link(s)",
    ]

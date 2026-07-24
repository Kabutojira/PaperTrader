from __future__ import annotations

import pytest

from papertrader.integrity import is_runtime_path_allowed, validate_runtime_paths


@pytest.mark.parametrize(
    "path",
    [
        "data/wiki/index.md",
        "data/wiki/daily-reports/daily-report_20260724.md",
        "data/wiki/raw/filing.pdf",
        "data/wiki/raw/chart.webp",
        "data/tables/securities.csv",
        "data/market/prices/sec-1.csv",
        "data/operations/payloads/op.json",
        "data/operations/prompts/op.md",
        "data/runs/run-1/op-1/agent_result.json",
        "data/logs/operations-2026.ndjson",
        "data/logs/log.txt",
        "data/issues.md",
    ],
)
def test_allowed_runtime_paths(path: str) -> None:
    assert is_runtime_path_allowed(path)


@pytest.mark.parametrize(
    "path",
    [
        "src/papertrader/cli.py",
        ".env",
        "data/wiki/raw/article.html",
        "data/wiki/image.png",
        "data/runs/run-1/result.txt",
        "data/logs/debug.log",
        "data/../pyproject.toml",
        "data//tables/securities.csv",
        "/data/tables/securities.csv",
        "data\\tables\\securities.csv",
        "site/public/index.html",
    ],
)
def test_disallowed_runtime_paths(path: str) -> None:
    assert not is_runtime_path_allowed(path)


def test_validator_reports_every_disallowed_path() -> None:
    assert validate_runtime_paths(
        ["data/wiki/index.md", "pyproject.toml", ".env", "data/tables/runs.csv"]
    ) == [
        "runtime path is not allowed: pyproject.toml",
        "runtime path is not allowed: .env",
    ]

from __future__ import annotations

import json
import tarfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

import papertrader.research_runtime as runtime
from papertrader.research_agent import run_cycle
from papertrader.research_market import PRICE_COLUMNS, _write
from papertrader.research_queue import admit
from papertrader.research_state import contracts, read_state, write_state

NOW = datetime(2026, 10, 18, 20, tzinfo=UTC)
STAMP = "2026-10-18T20:00:00Z"


@pytest.fixture
def runtime_root(repository_root: Path, tmp_path: Path) -> Path:
    import shutil

    root = tmp_path / "runtime"
    root.mkdir()
    shutil.copytree(repository_root / "schemas", root / "schemas")
    shutil.copytree(repository_root / "skills", root / "skills")
    shutil.copy2(repository_root / "research.ini", root / "research.ini")
    schema = contracts(root)
    state = {name: [] for name in schema}
    for sid in ("sec1", "sec2"):
        row = dict.fromkeys(schema["securities"].columns, "")
        row.update(
            security_id=sid,
            issuer_id="issuer" + sid,
            company_name=sid,
            instrument_name="Ordinary",
            instrument_type="equity",
            ticker=sid.upper(),
            provider_symbol=sid.upper(),
            venue_mic="XNYS",
            currency="USD",
            status="watching",
            research_status="unresearched",
        )
        state["securities"].append(row)
    write_state(root, state)
    return root


class Provider:
    def __init__(self, bad: bool = False) -> None:
        self.calls: list[list[str]] = []
        self.bad = bad

    def fetch(self, symbols: list[str], start: Any, end: Any) -> dict[str, list[dict[str, str]]]:
        self.calls.append(symbols)
        return {
            symbol: (
                []
                if self.bad and symbol == "SEC2"
                else [
                    {
                        "date": "2026-10-16",
                        "open": "100",
                        "high": "101",
                        "low": "99",
                        "close": "100",
                        "adjusted_close": "100",
                        "volume": "1000",
                        "dividends": "0",
                        "stock_splits": "0",
                        "currency": "USD",
                        "provider_symbol": symbol,
                        "retrieved_at": STAMP,
                        "source": "yfinance",
                    }
                ]
            )
            for symbol in symbols
        }


def test_closed_repeat_is_no_network_and_no_state_commit(runtime_root: Path) -> None:
    provider = Provider()
    assert (
        runtime.market_cycle(runtime_root, dry_run=True, now=NOW, provider=provider)[
            "provider_calls"
        ]
        == 0
    )
    assert provider.calls == []
    first = runtime.market_cycle(runtime_root, dry_run=False, now=NOW, provider=provider)
    assert first["exit_code"] == 0 and first["provider_calls"] > 0
    before = {
        p.relative_to(runtime_root): p.read_bytes()
        for p in (runtime_root / "data").rglob("*")
        if p.is_file()
    }
    provider.calls.clear()
    repeat = runtime.market_cycle(runtime_root, dry_run=False, now=NOW, provider=provider)
    assert provider.calls == [] and repeat["provider_calls"] == 0 and repeat["changed"] == []
    assert before == {
        p.relative_to(runtime_root): p.read_bytes()
        for p in (runtime_root / "data").rglob("*")
        if p.is_file()
    }


def test_market_outage_preserves_other_quotes_and_old_good_bar(runtime_root: Path) -> None:
    old = Provider().fetch(["SEC2"], None, None)["SEC2"][0]
    old["date"] = "2026-10-15"
    _write(runtime_root, "data/market/prices/sec2.csv", PRICE_COLUMNS, [old])
    result = runtime.market_cycle(runtime_root, dry_run=False, now=NOW, provider=Provider(bad=True))
    assert result["exit_code"] == 2 and set(result["failed_tickers"]) == {"sec2"}
    latest = {
        row["security_id"]: row for row in runtime._read(runtime_root / "data/market/latest.csv")
    }
    assert latest["sec1"]["status"] == "current"
    assert latest["sec2"]["status"] == "stale" and latest["sec2"]["close"] == "100"
    assert latest["sec2"]["price_date"] == "2026-10-15"


def test_pages_failure_does_not_undo_market_or_research(
    runtime_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        runtime,
        "publish_views",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("pages unavailable")),
    )
    result = runtime.market_cycle(runtime_root, dry_run=False, now=NOW, provider=Provider())
    assert result["exit_code"] == 0 and result["publication_input_error"] == "derived_views_failed"
    monkeypatch.setattr(
        runtime,
        "run_cycle",
        lambda *a, **k: dict(
            status="succeeded", exit_code=0, outcomes=[{"status": "no_change"}], changed=[]
        ),
    )
    result = runtime.research_cycle(runtime_root, dry_run=False)
    assert result["exit_code"] == 0 and result["publication_input_error"] == "derived_views_failed"
    status = json.loads((runtime_root / "data/status.json").read_text())
    assert status["market"]["status"] == status["research"]["status"] == "succeeded"


def test_failed_discovery_uses_one_of_three_operations_and_other_research_continues(
    runtime_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        runtime, "run_discovery", lambda *a, **k: dict(status="failed", exit_code=3, model_calls=1)
    )
    reserved: list[int] = []

    def cycle(*args: Any, **kwargs: Any) -> dict[str, Any]:
        reserved.append(kwargs["reserved_operations"])
        return dict(
            status="succeeded", exit_code=0, outcomes=[{"status": "no_change"}] * 2, changed=[]
        )

    monkeypatch.setattr(runtime, "run_cycle", cycle)
    result = runtime.research_cycle(runtime_root, dry_run=False, discovery=True)
    assert reserved == [1] and result["model_operations"] == 3 and result["exit_code"] == 3


def test_reserved_operation_budget_reduces_actual_claims(runtime_root: Path) -> None:
    state = read_state(runtime_root)
    for row in state["securities"]:
        admit(
            state,
            "security",
            row["security_id"],
            reasons={"manual"},
            priority=100,
            manual=True,
            now=NOW,
        )
    write_state(runtime_root, state)
    calls: list[int] = []

    def failing(*args: Any) -> dict[str, Any]:
        calls.append(1)
        raise RuntimeError("mock outage")

    result = run_cycle(
        runtime_root, dry_run=False, reserved_operations=2, executor=failing, clock=lambda: NOW
    )
    assert len(calls) == len(result["outcomes"]) == 1
    assert result["exit_code"] == 3
    assert len(read_state(runtime_root)["research_queue"]) == 2


@pytest.mark.parametrize(
    "path",
    [
        ".env",
        "src/papertrader/foo.py",
        ".git/config",
        "data/tables/portfolio.csv",
        "data/market/../secrets.csv",
        "data/wiki/evil.json",
        ".papertrader/credentials/auth.json",
    ],
)
def test_runtime_commit_allowlist_rejects_non_product_and_secret_paths(path: str) -> None:
    assert not runtime.allowed_runtime_path(path, "market")
    assert not runtime.allowed_runtime_path(path, "research")


def test_git_divergence_preserves_new_accepted_page_without_pushing(
    runtime_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    page = runtime_root / "data/wiki/securities/new.md"
    page.parent.mkdir(parents=True)
    page.write_text("Accepted original source-linked research")
    commands: list[tuple[str, ...]] = []

    def git(root: Path, *args: str, **kwargs: Any) -> str:
        commands.append(args)
        if args == ("rev-parse", "HEAD"):
            return "a" * 40
        if args == ("rev-parse", "origin/main"):
            return "b" * 40
        if args[:2] == ("ls-files", "--others"):
            return "data/wiki/securities/new.md\0"
        return ""

    monkeypatch.setattr(runtime, "_git", git)
    with pytest.raises(RuntimeError, match="git_conflict"):
        runtime.finalize_commit(runtime_root, phase="research", token="mock-test-token")
    assert not any(args[0] in {"push", "commit", "add"} for args in commands)
    with tarfile.open(runtime_root / ".cache/recovery.tar.gz") as archive:
        assert "data/wiki/securities/new.md" in archive.getnames()
        assert archive.extractfile("data/wiki/securities/new.md").read() == page.read_bytes()  # type: ignore[union-attr]


def test_market_cannot_commit_judgment_owned_research_pages() -> None:
    assert not runtime.allowed_runtime_path("data/wiki/securities/sec1.md", "market")
    assert runtime.allowed_runtime_path("data/wiki/securities/sec1.md", "research")
    assert runtime.allowed_runtime_path("data/wiki/index.md", "market")

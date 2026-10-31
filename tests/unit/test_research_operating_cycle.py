"""Mocked full operating cycle, with the real controller/validator/transactions."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from papertrader.research_agent import run_cycle
from papertrader.research_publication import publish_views, snapshot
from papertrader.research_runtime import market_cycle
from papertrader.research_state import contracts, read_state, unscored_fields, write_state

NOW = datetime(2026, 10, 18, 20, tzinfo=UTC)
STAMP = "2026-10-18T20:00:00Z"


def test_mocked_market_research_publication_and_rejected_update_are_independent(
    repository_root: Path, tmp_path: Path
) -> None:
    root = tmp_path / "cycle"
    root.mkdir()
    shutil.copytree(repository_root / "schemas", root / "schemas")
    shutil.copytree(repository_root / "skills", root / "skills")
    shutil.copy2(repository_root / "research.ini", root / "research.ini")
    schema = contracts(root)
    state = {name: [] for name in schema}
    security = dict.fromkeys(schema["securities"].columns, "")
    security.update(
        research_role="long",
        security_id="sec1",
        issuer_id="issuer1",
        company_name="Example",
        instrument_name="Ordinary",
        instrument_type="equity",
        ticker="EX",
        provider_symbol="EX",
        venue_mic="XNYS",
        currency="USD",
        status="watching",
        research_status="unresearched",
    )
    state["securities"].append(security)
    write_state(root, state)

    class Provider:
        calls = 0

        def fetch(
            self, symbols: list[str], start: Any, end: Any
        ) -> dict[str, list[dict[str, str]]]:
            self.calls += 1
            return {
                "EX": [
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
                        "provider_symbol": "EX",
                        "retrieved_at": STAMP,
                        "source": "yfinance",
                    }
                ]
            }

    provider = Provider()
    assert market_cycle(root, dry_run=False, now=NOW, provider=provider)["exit_code"] == 0
    assert len(read_state(root)["research_queue"]) == 1

    def completed(*args: Any) -> dict[str, Any]:
        assessment = dict.fromkeys(schema["security_assessments"].columns, "")
        assessment.update(unscored_fields("Component scoring evidence has not been verified."))
        assessment.update(
            security_id="sec1",
            assessed_at=STAMP,
            valid_until="2026-11-17T20:00:00Z",
            research_status="supported",
            method="earnings",
            method_rationale="Cited earning power at scenario multiples",
            currency="USD",
            horizon_months="12",
            thesis="Recurring demand supports earnings",
            key_assumptions="Demand and margins stabilize",
            downside="Demand declines",
            catalysts="Next results",
            invalidation_conditions="Persistent negative cash flow",
            confidence="high",
            limitations="Estimation uncertainty",
            source_ids="source1",
        )
        for case, value, probability in (
            ("bear", "50", "30"),
            ("base", "150", "50"),
            ("bull", "200", "20"),
        ):
            assessment.update(
                {
                    f"{case}_fair_value": value,
                    f"{case}_probability_pct": probability,
                    f"{case}_assumptions": "Explicit demand and margin assumptions",
                }
            )
        source = dict.fromkeys(schema["source_registry"].columns, "")
        source.update(
            source_id="source1",
            url="https://issuer.example/filing",
            title="Annual filing",
            publisher="Issuer",
            source_type="annual_filing",
            license="link_only",
            status="valid",
            related_entity_ids="sec1",
        )
        page = (
            "---\nsecurity_id: sec1\nissuer_id: issuer1\ntitle: Example\n---\n# Research\n"
            "Original earning-power analysis. [Filing](https://issuer.example/filing)\n"
        )
        return {
            "result": dict(
                operation="research_security",
                entity_id="sec1",
                outcome="updated",
                summary="Primary evidence reviewed",
                assessment=assessment,
                idea=None,
                sources=[source],
                relationships=[],
                pages={"data/wiki/securities/sec1.md": page},
            ),
            "observations": {
                "https://issuer.example/filing": dict(
                    content_hash="a" * 64,
                    checked_at=STAMP,
                    source_text="Original primary filing observations.",
                )
            },
            "usage": {"web_requests": 1},
        }

    result = run_cycle(root, dry_run=False, executor=completed, clock=lambda: NOW)
    assert result["exit_code"] == 0 and result["web_requests"] == 1
    assert read_state(root)["research_queue"] == []
    assert len(read_state(root)["security_assessments"]) == 1
    assert publish_views(root, now=NOW)
    view = snapshot(root, now=NOW)
    assert len(view["buys"]) == 1 and view["sells"] == []
    assert view["buys"][0]["weighted_fair_value"] == "130"
    assert publish_views(root, now=NOW) == []
    before = read_state(root)["security_assessments"]
    page_before = (root / "data/wiki/securities/sec1.md").read_bytes()

    def invalid(*args: Any) -> dict[str, Any]:
        response = completed()
        response["result"]["entity_id"] = "different_entity"
        return response

    rejected = run_cycle(
        root,
        dry_run=False,
        entity_type="security",
        entity_id="sec1",
        executor=invalid,
        clock=lambda: NOW,
    )
    assert rejected["exit_code"] == 3
    assert read_state(root)["security_assessments"] == before
    assert (root / "data/wiki/securities/sec1.md").read_bytes() == page_before
    provider.calls = 0
    assert market_cycle(root, dry_run=False, now=NOW, provider=provider)["exit_code"] == 0
    assert provider.calls == 0
    assert snapshot(root, now=NOW)["buys"] == view["buys"]
    assert json.loads((root / "data/status.json").read_text())["market"]["status"] == "succeeded"

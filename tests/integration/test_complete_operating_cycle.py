from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import exchange_calendars as xcals
import pandas as pd

from papertrader.agent_runner import configure_hermes_home
from papertrader.atomic_io import atomic_write_json, atomic_write_text
from papertrader.config import Settings
from papertrader.daily import execute_agent_batch, finalize_daily_run, prepare_daily_run
from papertrader.execution import process_order_fill
from papertrader.indicators import update_indicators
from papertrader.integrity import validate_integrity
from papertrader.market_data import (
    MarketDataError,
    latest_completed_session,
    read_price_cache,
    session_close,
    session_open,
    update_market_data,
)
from papertrader.models import ClassifierDecision, ReferencePrice, SecurityIdentity
from papertrader.opportunity import process_opportunity_transitions
from papertrader.portfolio import build_risk_state, reconcile_portfolio
from papertrader.publication import apply_runtime_bundle, create_runtime_bundle
from papertrader.repository_state import compare_snapshots, snapshot_repository
from papertrader.tables import read_table, write_table
from papertrader.telegram import deliver_committed_report
from papertrader.utils import format_timestamp, parse_timestamp, utc_now
from papertrader.wiki import lint_wiki, register_wiki_page

SECURITY_ID = "sec_operating_cycle"
IDEA_ID = "idea_operating_cycle"
RELATIONSHIP_ID = "relationship_operating_cycle"
STRATEGY_ID = "strategy_operating_cycle"
SOURCE_ID = "source_operating_cycle"
RUN_ID = "operating-cycle-1"


class _RecordedProvider:
    name = "yfinance"

    def __init__(self, frame: pd.DataFrame) -> None:
        self.frame = frame
        self.calls = 0

    def history(
        self,
        identity: SecurityIdentity,
        *,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        del identity, start, end
        self.calls += 1
        return self.frame.copy()


class _IngestClassifier:
    def __init__(self) -> None:
        self.calls = 0

    def classify(self, candidate: Mapping[str, object]) -> ClassifierDecision:
        self.calls += 1
        return ClassifierDecision(
            decision="ingest",
            reason="The synthetic transition materially updates the maintained cycle thesis.",
            related_entity_ids=(str(candidate["security_id"]),),
        )


class _SuccessfulTelegram:
    def __init__(self) -> None:
        self.calls: list[Mapping[str, str]] = []

    def send(
        self,
        token: str,
        payload: Mapping[str, str],
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        assert token == "fixture-token"
        assert timeout_seconds > 0
        self.calls.append(payload)
        return {"ok": True}


def _git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _wiki_page(
    repository: Path,
    *,
    domain: str,
    page_id: str,
    title: str,
    page_type: str,
    tag: str,
    provenance: str,
    body: str,
    event_date: date,
) -> str:
    relative = f"data/wiki/{domain}/{page_id}.md"
    content = (
        "---\n"
        f"title: {title}\n"
        f"type: {page_type}\n"
        "status: maintained\n"
        f"tags: [{tag}, research]\n"
        f'created: "{event_date.isoformat()}"\n'
        f'updated: "{event_date.isoformat()}"\n'
        f"provenance: {provenance}\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{body.strip()}\n"
    )
    atomic_write_text(repository / relative, content, allowed_root=repository)
    register_wiki_page(
        repository / "data" / "wiki",
        page_key=f"{domain}/{page_id}",
        label=title,
        section=domain.replace("-", " ").title(),
        event=f"Maintained [[{domain}/{page_id}]] for the operating-cycle validation.",
        event_date=event_date,
    )
    return relative


def _seed_security(repository: Path, instant: datetime) -> None:
    page = _wiki_page(
        repository,
        domain="securities",
        page_id=SECURITY_ID,
        title="Operating Cycle SE",
        page_type="security",
        tag="security",
        provenance="manual-validation-seed",
        body=(
            "A synthetic EUR-denominated XETR equity used only to validate the paper-trading "
            "operating cycle. It is not an investment recommendation."
        ),
        event_date=instant.date(),
    )
    timestamp = format_timestamp(instant - timedelta(days=1))
    write_table(
        repository,
        "securities",
        [
            {
                "security_id": SECURITY_ID,
                "issuer_id": "issuer_operating_cycle",
                "company_name": "Operating Cycle SE",
                "instrument_name": "Operating Cycle ordinary share",
                "instrument_type": "equity",
                "ticker": "OCY",
                "exchange_code": "XETR",
                "venue_mic": "XETR",
                "provider_symbol": "OCY.DE",
                "broker_symbol": "",
                "currency": "EUR",
                "country": "DE",
                "sector": "Industrials",
                "industry": "Validation fixtures",
                "status": "active",
                "watchlist_reason": "Validate one complete synthetic paper lifecycle.",
                "research_summary": "Synthetic security for operating-cycle validation.",
                "research_page": page,
                "last_research_at": timestamp,
                "next_review_at": format_timestamp(instant + timedelta(days=30)),
                "created_at": timestamp,
                "updated_at": timestamp,
                "source": "manual-validation-seed",
            }
        ],
    )


def _market_frame(session_dates: Sequence[date]) -> pd.DataFrame:
    closes = [Decimal("40") + Decimal(index) / Decimal("4") for index in range(len(session_dates))]
    return pd.DataFrame(
        {
            "Open": [value - Decimal("0.10") for value in closes],
            "High": [value + Decimal("0.75") for value in closes],
            "Low": [value - Decimal("0.75") for value in closes],
            "Close": closes,
            "Adj Close": closes,
            "Volume": [100_000 + index * 100 for index in range(len(session_dates))],
            "Dividends": [Decimal("0")] * len(session_dates),
            "Stock Splits": [Decimal("0")] * len(session_dates),
        },
        index=pd.DatetimeIndex(session_dates),
    )


def _sessions_through(session_date: date) -> tuple[date, ...]:
    calendar = xcals.get_calendar("XETR")
    sessions = calendar.sessions_in_range(
        (session_date - timedelta(days=370)).isoformat(),
        session_date.isoformat(),
    )
    return tuple(timestamp.date() for timestamp in sessions[-240:])


def _next_session_after(instant: datetime) -> date:
    for offset in range(11):
        candidate = instant.date() + timedelta(days=offset)
        try:
            opening = session_open("XETR", candidate)
        except MarketDataError:
            continue
        if opening > instant:
            return candidate
    raise AssertionError("XETR has no next session within the bounded fixture window")


class _CycleHermes:
    def __init__(self, *, reference_price: Decimal, reference_time: datetime) -> None:
        self.reference_price = reference_price
        self.reference_time = reference_time
        self.expiry = reference_time + timedelta(days=10)
        self.operation_types: list[str] = []
        self.replay_requests: dict[str, Path] = {}
        self.queue_requests: list[Path] = []

    def _run_request(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
        filename: str,
        payload: Mapping[str, object],
        arguments: Sequence[str],
    ) -> Mapping[str, object]:
        request = artifact / filename
        atomic_write_json(request, payload, allowed_root=repository)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "papertrader",
                "--repository",
                str(repository),
                *arguments,
                "--request",
                str(request),
            ],
            cwd=repository,
            env=dict(environment),
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        self.replay_requests[filename] = request
        output = result.stdout.strip()
        return json.loads(output) if output.startswith("{") else {"value": output}

    def _enqueue(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
        filename: str,
        *,
        operation_type: str,
        entity_type: str,
        entity_id: str,
        dedupe_key: str,
        prompt: str,
        inputs: Mapping[str, object],
        source_refs: Sequence[str],
        priority: int,
    ) -> str:
        response = self._run_request(
            repository,
            environment,
            artifact,
            filename,
            {
                "operation_type": operation_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "dedupe_key": dedupe_key,
                "prompt": prompt,
                "inputs": dict(inputs),
                "source": "operating-cycle-validation",
                "priority": priority,
                "freshness_days": 30,
                "depends_on": [],
                "not_before": "",
                "deadline": "",
                "source_refs": list(source_refs),
                "max_attempts": 3,
            },
            ("queue", "enqueue"),
        )
        assert response["created"] is True
        self.queue_requests.append(artifact / filename)
        return str(response["operation_id"])

    def _opportunity(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
        payload: Mapping[str, object],
    ) -> tuple[list[str], str]:
        idea_page = _wiki_page(
            repository,
            domain="ideas",
            page_id=IDEA_ID,
            title="Synthetic operating-cycle momentum",
            page_type="idea",
            tag="idea",
            provenance="operating-cycle-opportunity",
            body=(
                f"The synthetic transition may benefit [[securities/{SECURITY_ID}]]. The "
                "mechanism is a validation fixture with bounded downside and an explicit "
                "invalidation if the deterministic cycle fails."
            ),
            event_date=self.reference_time.date(),
        )
        followup = self._enqueue(
            repository,
            environment,
            artifact,
            "enqueue-relationship.json",
            operation_type="relationship_research",
            entity_type="relationship",
            entity_id=RELATIONSHIP_ID,
            dedupe_key=f"relationship_research:{RELATIONSHIP_ID}:synthetic-cycle:v1",
            prompt="Validate one synthetic idea-security relationship.",
            inputs={
                "relationship_id": RELATIONSHIP_ID,
                "idea_id": IDEA_ID,
                "security_id": SECURITY_ID,
            },
            source_refs=(idea_page, str(payload["source_refs"][0])),
            priority=55,
        )
        return [followup], "The material synthetic transition justified one relationship review."

    def _security(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
        run_id: str,
    ) -> tuple[list[str], str]:
        page = _wiki_page(
            repository,
            domain="securities",
            page_id=SECURITY_ID,
            title="Operating Cycle SE",
            page_type="security",
            tag="security",
            provenance=SOURCE_ID,
            body=(
                "The alert-driven review found a sound synthetic business with a positive "
                "valuation range and sufficient liquidity. The deterministic price alert "
                "justifies continued research, but it does not by itself decide a trade."
            ),
            event_date=self.reference_time.date(),
        )
        self._run_request(
            repository,
            environment,
            artifact,
            "record-security-source.json",
            {
                "source_id": SOURCE_ID,
                "url": "https://example.test/papertrader/operating-cycle",
                "canonical_url": "https://example.test/papertrader/operating-cycle",
                "source_type": "synthetic-fixture",
                "title": "PaperTrader operating-cycle security fixture",
                "publisher": "PaperTrader tests",
                "license": "user-owned",
                "status": "available",
                "content_hash": "a" * 64,
                "related_entity_ids": SECURITY_ID,
                "checked_at": format_timestamp(self.reference_time),
                "http_status": "200",
                "changed": "true",
                "excerpt": "Synthetic security validation evidence.",
                "summary": "The alert-driven security review supports a comparable assessment.",
                "run_id": run_id,
            },
            ("research", "source", "record"),
        )
        security = dict(read_table(repository, "securities")[0])
        security.update(
            {
                "research_summary": (
                    "Alert-driven review supports baseline eligibility with bounded downside."
                ),
                "research_page": page,
                "last_research_at": format_timestamp(self.reference_time),
                "next_review_at": format_timestamp(self.reference_time + timedelta(days=30)),
                "updated_at": format_timestamp(self.reference_time),
                "source": "https://example.test/papertrader/operating-cycle",
            }
        )
        security.pop("created_at")
        security.pop("updated_at")
        self._run_request(
            repository,
            environment,
            artifact,
            "upsert-security.json",
            security,
            ("research", "security", "upsert"),
        )
        self._run_request(
            repository,
            environment,
            artifact,
            "upsert-assessment.json",
            {
                "security_id": SECURITY_ID,
                "assessed_at": format_timestamp(self.reference_time),
                "expires_at": format_timestamp(self.reference_time + timedelta(days=30)),
                "eligibility": "baseline",
                "confidence": "high",
                "thesis_score": "80",
                "business_quality_score": "80",
                "balance_sheet_score": "80",
                "valuation_score": "80",
                "timing_score": "80",
                "liquidity_score": "80",
                "risk_penalty": "0",
                "downside_pct": "-20",
                "base_upside_pct": "25",
                "valuation_horizon_months": "12",
                "hard_blockers": "",
                "soft_gaps": "",
                "evidence_refs": SOURCE_ID,
                "run_id": run_id,
            },
            ("research", "assessment", "upsert"),
        )
        return [], "The alert-driven security review kept the security baseline-eligible."

    def _wiki_ingest(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
        payload: Mapping[str, object],
        run_id: str,
    ) -> tuple[list[str], str]:
        inputs = payload["inputs"]
        assert isinstance(inputs, dict)
        source_hash = str(inputs["source_hash"])
        _wiki_page(
            repository,
            domain="concepts",
            page_id=SOURCE_ID,
            title="Synthetic operating-cycle evidence",
            page_type="concept",
            tag="source",
            provenance=SOURCE_ID,
            body=(
                f"This original summary records a synthetic indicator transition for "
                f"[[securities/{SECURITY_ID}]] and [[ideas/{IDEA_ID}]]. No copyrighted source "
                "content is retained."
            ),
            event_date=self.reference_time.date(),
        )
        self._run_request(
            repository,
            environment,
            artifact,
            "record-source.json",
            {
                "source_id": SOURCE_ID,
                "url": "https://example.test/papertrader/operating-cycle",
                "canonical_url": "https://example.test/papertrader/operating-cycle",
                "source_type": "synthetic-fixture",
                "title": "PaperTrader operating-cycle fixture",
                "publisher": "PaperTrader tests",
                "license": "user-owned",
                "status": "available",
                "content_hash": source_hash,
                "related_entity_ids": f"{IDEA_ID}|{SECURITY_ID}",
                "checked_at": format_timestamp(self.reference_time),
                "http_status": "200",
                "changed": "true",
                "excerpt": "Synthetic validation evidence.",
                "summary": "A synthetic market transition entered the research queue.",
                "run_id": run_id,
            },
            ("research", "source", "record"),
        )
        return [], "The classified packet was ingested once with provenance and a source hash."

    def _relationship(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
    ) -> tuple[list[str], str]:
        page = _wiki_page(
            repository,
            domain="relationships",
            page_id=RELATIONSHIP_ID,
            title="Synthetic momentum to Operating Cycle SE",
            page_type="relationship",
            tag="relationship",
            provenance=SOURCE_ID,
            body=(
                f"[[ideas/{IDEA_ID}]] has a positive, medium-sensitivity fixture relationship "
                f"to [[securities/{SECURITY_ID}]]. It is invalidated if the seeded evidence or "
                "paper accounting fails validation."
            ),
            event_date=self.reference_time.date(),
        )
        self._run_request(
            repository,
            environment,
            artifact,
            "upsert-relationship.json",
            {
                "relationship_id": RELATIONSHIP_ID,
                "idea_id": IDEA_ID,
                "security_id": SECURITY_ID,
                "relationship_type": "beneficiary",
                "direction": "positive",
                "mechanism": "The synthetic momentum fixture raises the modeled value signal.",
                "sensitivity": "medium",
                "confidence": "high",
                "catalyst": "A deterministic overbought transition enters the queue.",
                "invalidation": "Any operating-cycle validation check fails.",
                "status": "accepted",
                "research_page": page,
                "last_reviewed_at": format_timestamp(self.reference_time),
                "next_review_at": format_timestamp(self.reference_time + timedelta(days=30)),
            },
            ("research", "relationship", "upsert"),
        )
        followup = self._enqueue(
            repository,
            environment,
            artifact,
            "enqueue-strategy.json",
            operation_type="strategy_research",
            entity_type="strategy",
            entity_id=STRATEGY_ID,
            dedupe_key=f"strategy_research:{STRATEGY_ID}:synthetic-cycle:v1",
            prompt="Create one bounded synthetic paper strategy.",
            inputs={"strategy_id": STRATEGY_ID, "relationship_id": RELATIONSHIP_ID},
            source_refs=(page,),
            priority=50,
        )
        return [followup], "The causal relationship was accepted and linked to one strategy review."

    def _strategy(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
        run_id: str,
    ) -> tuple[list[str], str]:
        page = _wiki_page(
            repository,
            domain="strategies",
            page_id=STRATEGY_ID,
            title="Synthetic next-open long equity",
            page_type="strategy",
            tag="strategy",
            provenance=SOURCE_ID,
            body=(
                f"Open ten synthetic shares of [[securities/{SECURITY_ID}]] at the next eligible "
                f"session for [[relationships/{RELATIONSHIP_ID}]]. Exit if any fixture invariant "
                "fails."
            ),
            event_date=self.reference_time.date(),
        )
        self._run_request(
            repository,
            environment,
            artifact,
            "upsert-strategy.json",
            {
                "strategy": {
                    "strategy_id": STRATEGY_ID,
                    "idea_id": IDEA_ID,
                    "security_id": SECURITY_ID,
                    "relationship_id": RELATIONSHIP_ID,
                    "name": "Synthetic next-open long equity",
                    "status": "ready",
                    "direction": "long",
                    "instrument_type": "equity",
                    "thesis": "The evidence-linked synthetic transition supports a bounded test.",
                    "entry_rule": "Enter at the next eligible XETR session open.",
                    "exit_rule": "Close after validation or at the review deadline.",
                    "invalidation": "Any deterministic validation invariant fails.",
                    "risk_budget_pct": "1",
                    "not_before": "",
                    "expires_at": "",
                    "research_page": page,
                },
                "legs": [
                    {
                        "leg_id": "leg_operating_cycle",
                        "action": "buy",
                        "side": "long",
                        "instrument_type": "equity",
                        "security_id": SECURITY_ID,
                        "provider_contract_id": "",
                        "option_type": "",
                        "expiry": "",
                        "strike": "",
                        "quantity": "10",
                        "contract_multiplier": "1",
                        "order_type": "market",
                        "limit_price": "",
                        "currency": "EUR",
                    }
                ],
            },
            ("research", "strategy", "upsert"),
        )
        signal = self._run_request(
            repository,
            environment,
            artifact,
            "create-signal.json",
            {
                "strategy_id": STRATEGY_ID,
                "signal_type": "open",
                "rationale": "Open the evidence-linked synthetic next-session paper position.",
                "market_data_as_of": format_timestamp(self.reference_time),
                "run_id": run_id,
                "order_request_path": "",
                "expires_at": format_timestamp(self.expiry),
            },
            ("signal", "create"),
        )
        signal_id = str(signal["signal_id"])
        followup = self._enqueue(
            repository,
            environment,
            artifact,
            "enqueue-execution.json",
            operation_type="execute_strategy",
            entity_type="strategy",
            entity_id=STRATEGY_ID,
            dedupe_key=f"execute_strategy:{STRATEGY_ID}:{signal_id}:open",
            prompt="Validate and create one pending synthetic paper order.",
            inputs={"strategy_id": STRATEGY_ID, "signal_id": signal_id, "action": "open"},
            source_refs=(page,),
            priority=50,
        )
        return [followup], "The bounded strategy and one time-limited signal were created."

    def _execute(
        self,
        repository: Path,
        environment: Mapping[str, str],
        artifact: Path,
        payload: Mapping[str, object],
        run_id: str,
    ) -> tuple[list[str], str]:
        inputs = payload["inputs"]
        assert isinstance(inputs, dict)
        order_time = utc_now().replace(microsecond=0)
        response = self._run_request(
            repository,
            environment,
            artifact,
            "create-order.json",
            {
                "signal_id": str(inputs["signal_id"]),
                "strategy_id": STRATEGY_ID,
                "legs": [
                    {
                        "leg_id": "leg_operating_cycle",
                        "action": "buy",
                        "side": "long",
                        "instrument_type": "equity",
                        "security_id": SECURITY_ID,
                        "provider_contract_id": "",
                        "option_type": "",
                        "expiry": "",
                        "strike": "",
                        "quantity": "10",
                        "contract_multiplier": "1",
                        "limit_price": "",
                        "currency": "EUR",
                    }
                ],
                "references": [
                    {
                        "security_id": SECURITY_ID,
                        "provider_contract_id": "",
                        "price": str(self.reference_price),
                        "currency": "EUR",
                        "fx_rate_to_base": "1",
                        "as_of": format_timestamp(order_time),
                        "bid": "",
                        "ask": "",
                        "open_interest": None,
                        "volume": None,
                    }
                ],
                "run_id": run_id,
                "fill_policy": "next_open",
                "order_type": "market",
                "limit_price": "",
                "not_before": format_timestamp(order_time),
                "expires_at": format_timestamp(self.expiry),
                "now": format_timestamp(order_time),
            },
            ("order", "create"),
        )
        assert response["created"] is True
        return [], "The validated paper order remains pending until the next eligible open."

    def __call__(
        self,
        command: Sequence[str],
        cwd: Path,
        environment: Mapping[str, str],
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del timeout
        assert "--yolo" in command
        assert "GITHUB_TOKEN" not in environment
        assert "TELEGRAM_BOT_TOKEN" not in environment
        operation_id = environment["PAPERTRADER_AUDIT_OPERATION_ID"]
        run_id = environment["PAPERTRADER_AUDIT_RUN_ID"]
        operation = next(
            row for row in read_table(cwd, "operations_todo") if row["operation_id"] == operation_id
        )
        operation_type = operation["operation_type"]
        self.operation_types.append(operation_type)
        payload = json.loads((cwd / operation["payload_path"]).read_text(encoding="utf-8"))
        artifact = cwd / "data" / "runs" / run_id / operation_id
        before = snapshot_repository(cwd)

        if operation_type == "security_research":
            created, summary = self._security(cwd, environment, artifact, run_id)
        elif operation_type == "opportunity_research":
            created, summary = self._opportunity(cwd, environment, artifact, payload)
        elif operation_type == "wiki_ingest":
            created, summary = self._wiki_ingest(cwd, environment, artifact, payload, run_id)
        elif operation_type == "relationship_research":
            created, summary = self._relationship(cwd, environment, artifact)
        elif operation_type == "strategy_research":
            created, summary = self._strategy(cwd, environment, artifact, run_id)
        elif operation_type == "execute_strategy":
            created, summary = self._execute(cwd, environment, artifact, payload, run_id)
        else:
            raise AssertionError(f"unexpected operating-cycle operation: {operation_type}")

        after = snapshot_repository(cwd)
        audit_path = f"data/runs/{run_id}/{operation_id}/command_audit.json"
        changed = tuple(
            path for path in compare_snapshots(before, after).changed if path != audit_path
        )
        audit = json.loads((cwd / audit_path).read_text(encoding="utf-8"))
        commands = [entry["command"] for entry in audit["entries"]]
        atomic_write_json(
            artifact / "agent_result.json",
            {
                "operation_id": operation_id,
                "status": "succeeded",
                "summary": summary,
                "evidence": [
                    {
                        "source": "synthetic operating-cycle fixture",
                        "claim": summary,
                        "url": "https://example.test/papertrader/operating-cycle",
                        "observed_at": format_timestamp(self.reference_time),
                    }
                ],
                "files_changed": list(changed),
                "operations_created": sorted(created),
                "issues_recorded": [],
                "daily_report_items": [summary],
                "commands_run": commands,
                "validation": {
                    "passed": True,
                    "checks": ["bounded synthetic operating-cycle operation completed"],
                },
            },
            allowed_root=cwd,
        )
        return subprocess.CompletedProcess(command, 0, "completed", "")

    def rewrite_wiki_pages(self, repository: Path) -> None:
        _wiki_page(
            repository,
            domain="ideas",
            page_id=IDEA_ID,
            title="Synthetic operating-cycle momentum",
            page_type="idea",
            tag="idea",
            provenance="operating-cycle-opportunity",
            body=(
                f"The synthetic transition may benefit [[securities/{SECURITY_ID}]]. The "
                "mechanism is a validation fixture with bounded downside and an explicit "
                "invalidation if the deterministic cycle fails."
            ),
            event_date=self.reference_time.date(),
        )


def _plain_request(
    repository: Path, request: Path, arguments: Sequence[str]
) -> Mapping[str, object]:
    environment = os.environ | {
        "WIKI_PATH": str(repository / "data" / "wiki"),
    }
    for name in tuple(environment):
        if name.startswith("PAPERTRADER_AUDIT_"):
            environment.pop(name)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "papertrader",
            "--repository",
            str(repository),
            *arguments,
            "--request",
            str(request),
        ],
        cwd=repository,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    output = result.stdout.strip()
    return json.loads(output) if output.startswith("{") else {"value": output}


def _initialize_seed_commit(repository: Path) -> str:
    _git(repository, "init", "-b", "main")
    _git(repository, "config", "user.name", "PaperTrader cycle test")
    _git(repository, "config", "user.email", "cycle@example.test")
    _git(repository, "add", "--all")
    _git(repository, "commit", "-m", "test: seed operating cycle")
    return _git(repository, "rev-parse", "HEAD")


def test_clean_checkout_research_to_publication_cycle_is_replay_safe(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    repository_root: Path,
    tmp_path: Path,
) -> None:
    sandbox_settings = replace(
        sandbox_settings,
        operations=replace(
            sandbox_settings.operations,
            maximum_llm_operations_per_run=6,
            maximum_model_budget_usd_per_run=Decimal("6"),
        ),
    )
    started_at = utc_now().replace(microsecond=0) - timedelta(minutes=1)
    completed_session = latest_completed_session("XETR", started_at)
    session_dates = _sessions_through(completed_session)
    assert len(session_dates) >= 200
    _seed_security(sandbox_repository, started_at)
    base_sha = _initialize_seed_commit(sandbox_repository)
    assert _git(sandbox_repository, "status", "--porcelain") == ""

    classifier = _IngestClassifier()
    initial_provider = _RecordedProvider(_market_frame(session_dates))
    preparation = prepare_daily_run(
        sandbox_repository,
        replace(
            sandbox_settings,
            allocation=replace(sandbox_settings.allocation, mode="disabled"),
        ),
        run_id=RUN_ID,
        trigger="integration",
        source_sha=base_sha,
        now=started_at,
        provider=initial_provider,
        classifier=classifier,
    )
    assert preparation.errors == ()
    assert classifier.calls >= 1
    assert len(read_table(sandbox_repository, "operations_todo")) >= 2

    home = tmp_path / "hermes"
    configure_hermes_home(sandbox_repository, sandbox_settings, home)
    native = home / "skills" / "research" / "llm-wiki" / "SKILL.md"
    native.parent.mkdir(parents=True)
    native.write_text(
        "---\nname: llm-wiki\ndescription: Native fixture.\nversion: 2.1.0\n---\n# Wiki\n",
        encoding="utf-8",
    )
    latest = read_price_cache(sandbox_repository, SECURITY_ID)[-1]
    executor = _CycleHermes(reference_price=latest.close, reference_time=started_at)
    batch = execute_agent_batch(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        hermes_home=home,
        environment={
            "PATH": os.environ.get("PATH", "/usr/bin"),
            "OPENROUTER_API_KEY": "test-auxiliary-key",
        },
        maximum_operations=6,
        executor=executor,
    )
    assert batch.operation_count == 6
    assert executor.operation_types == [
        "security_research",
        "opportunity_research",
        "wiki_ingest",
        "relationship_research",
        "strategy_research",
        "execute_strategy",
    ]
    assert read_table(sandbox_repository, "operations_todo") == []

    order = read_table(sandbox_repository, "orders")[0]
    order_created = parse_timestamp(order["created_at"])
    assert order_created is not None
    fill_session = _next_session_after(order_created)
    final_at = session_close("XETR", fill_session) + timedelta(hours=1)
    final_dates = (*session_dates, fill_session)
    final_provider = _RecordedProvider(_market_frame(final_dates))
    assert (
        update_market_data(
            sandbox_repository,
            sandbox_settings,
            provider=final_provider,
            now=final_at,
            sleeper=lambda _: None,
        )
        == ()
    )
    _, _, final_indicator_errors = update_indicators(
        sandbox_repository,
        sandbox_settings,
        now=final_at,
    )
    assert final_indicator_errors == ()
    report_name = f"daily-report_{fill_session.strftime('%Y%m%d')}.md"
    finalization = finalize_daily_run(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        github_report_url=(
            "https://github.com/example/PaperTrader/blob/main/"
            f"data/wiki/daily-reports/{report_name}"
        ),
        now=final_at,
    )
    assert finalization.status == "succeeded"
    assert len(read_table(sandbox_repository, "executions")) == 1
    assert read_table(sandbox_repository, "orders")[0]["status"] == "filled"
    assert read_table(sandbox_repository, "signals")[0]["status"] == "filled"
    assert read_table(sandbox_repository, "portfolio")[0]["security_id"] == SECURITY_ID
    assert reconcile_portfolio(sandbox_repository) == []
    assert lint_wiki(sandbox_repository / "data" / "wiki") == []
    report = sandbox_repository / finalization.report_path
    report_text = report.read_text(encoding="utf-8")
    assert all(
        row["operation_id"] in report_text
        for row in read_table(sandbox_repository, "operations_history")
    )
    assert f"[[ideas/{IDEA_ID}]]" in report_text
    assert f"[[relationships/{RELATIONSHIP_ID}]]" in report_text
    assert f"[[strategies/{STRATEGY_ID}]]" in report_text
    homepage_text = (sandbox_repository / "data" / "wiki" / "index.md").read_text(encoding="utf-8")
    assert homepage_text.index("Maintain the current model portfolio") < homepage_text.index(
        "## Explore"
    )
    assert "## Current and approved target portfolio" in homepage_text
    assert "OCY — Operating Cycle SE" in homepage_text
    assert f"strategies/{STRATEGY_ID}" in homepage_text
    assert "**No actionable trade signals.**" in homepage_text
    assert finalization.snapshot_id in homepage_text
    assert finalization.snapshot_id in report_text

    counts_before_replay = {
        name: len(read_table(sandbox_repository, name))
        for name in (
            "source_registry",
            "source_history",
            "operations_todo",
            "operations_history",
            "signals",
            "orders",
            "order_legs",
            "executions",
            "cash_ledger",
        )
    }
    pages_before_replay = tuple(
        path.relative_to(sandbox_repository).as_posix()
        for path in sorted((sandbox_repository / "data" / "wiki").rglob("*.md"))
    )
    old, current, indicator_errors = update_indicators(
        sandbox_repository,
        sandbox_settings,
        now=final_at,
    )
    assert indicator_errors == ()
    classifier_calls = classifier.calls
    assert (
        process_opportunity_transitions(
            sandbox_repository,
            sandbox_settings,
            old,
            current,
            {SECURITY_ID: read_price_cache(sandbox_repository, SECURITY_ID)},
            classifier=classifier,
            now=final_at,
        )
        == ()
    )
    assert classifier.calls == classifier_calls
    for request in executor.queue_requests:
        assert _plain_request(sandbox_repository, request, ("queue", "enqueue"))["created"] is False
    assert (
        _plain_request(
            sandbox_repository,
            executor.replay_requests["record-source.json"],
            ("research", "source", "record"),
        )["changed"]
        is False
    )
    assert (
        _plain_request(
            sandbox_repository,
            executor.replay_requests["upsert-relationship.json"],
            ("research", "relationship", "upsert"),
        )["changed"]
        is False
    )
    assert (
        _plain_request(
            sandbox_repository,
            executor.replay_requests["upsert-strategy.json"],
            ("research", "strategy", "upsert"),
        )["changed"]
        is False
    )
    assert (
        _plain_request(
            sandbox_repository,
            executor.replay_requests["create-signal.json"],
            ("signal", "create"),
        )["created"]
        is False
    )
    assert (
        _plain_request(
            sandbox_repository,
            executor.replay_requests["create-order.json"],
            ("order", "create"),
        )["created"]
        is False
    )
    executor.rewrite_wiki_pages(sandbox_repository)
    latest_mark = read_price_cache(sandbox_repository, SECURITY_ID)[-1]
    reference = ReferencePrice(
        security_id=SECURITY_ID,
        provider_contract_id="",
        price=latest_mark.close,
        currency="EUR",
        fx_rate_to_base=Decimal("1"),
        as_of=session_close("XETR", latest_mark.date),
    )
    replay_status, replayed_executions = process_order_fill(
        sandbox_repository,
        sandbox_settings,
        order_id=order["order_id"],
        bars=(),
        quotes=(),
        risk_state=build_risk_state(sandbox_repository, (reference,), as_of=final_at),
        risk_references=(reference,),
        run_id=RUN_ID,
        now=final_at,
    )
    assert replay_status == "filled"
    assert len(replayed_executions) == 1
    assert {
        name: len(read_table(sandbox_repository, name)) for name in counts_before_replay
    } == counts_before_replay
    assert (
        tuple(
            path.relative_to(sandbox_repository).as_posix()
            for path in sorted((sandbox_repository / "data" / "wiki").rglob("*.md"))
        )
        == pages_before_replay
    )

    bundle_directory = tmp_path / "runtime-bundle"
    bundle = create_runtime_bundle(
        sandbox_repository,
        bundle_directory,
        run_id=RUN_ID,
        base_sha=base_sha,
    )
    publication = tmp_path / "publication-checkout"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", str(sandbox_repository), str(publication)],
        check=True,
        capture_output=True,
        text=True,
    )
    applied = apply_runtime_bundle(publication, bundle_directory)
    assert applied == bundle
    _git(publication, "config", "user.name", "PaperTrader cycle test")
    _git(publication, "config", "user.email", "cycle@example.test")
    _git(publication, "commit", "-m", "chore(runtime): publish operating cycle")
    commit_sha = _git(publication, "rev-parse", "HEAD")
    environment = {
        "WIKI_PATH": str(publication / "data" / "wiki"),
    }
    assert validate_integrity(publication, environment) == []
    assert lint_wiki(publication / "data" / "wiki") == []
    assert reconcile_portfolio(publication) == []

    telegram = _SuccessfulTelegram()
    delivery = deliver_committed_report(
        publication,
        sandbox_settings,
        commit_sha=commit_sha,
        report_path=finalization.report_path,
        repository_url="https://github.com/example/PaperTrader",
        run_id=RUN_ID,
        token="fixture-token",
        chat_id="-123",
        transport=telegram,
        sleeper=lambda _: None,
        now=final_at,
    )
    assert delivery.status == "sent"
    delivered_markdown = "".join(
        json.loads(call["rich_message"])["markdown"] for call in telegram.calls
    )
    assert "# Maintain the current model portfolio" in delivered_markdown
    assert "## Approved target changes" in delivered_markdown
    assert "## Complete active queue" not in delivered_markdown
    assert finalization.snapshot_id in delivered_markdown
    assert "title:" not in delivered_markdown
    assert "https://example.github.io/PaperTrader/daily-reports/" in delivered_markdown
    assert "github.com/example/PaperTrader/blob" not in delivered_markdown
    assert all(set(call) == {"chat_id", "rich_message"} for call in telegram.calls)

    if os.environ.get("PAPERTRADER_VALIDATE_QUARTZ") == "true":
        site_output = tmp_path / "published-site"
        site_environment = os.environ | {
            "WIKI_PATH": str(publication / "data" / "wiki"),
            "PAPERTRADER_SITE_OUTPUT": str(site_output),
            "PAPERTRADER_BASE_URL": "example.github.io/PaperTrader",
        }
        site = subprocess.run(
            ["npm", "run", "build", "--prefix", str(repository_root / "site")],
            cwd=repository_root,
            env=site_environment,
            check=False,
            capture_output=True,
            text=True,
        )
        assert site.returncode == 0, site.stderr
        html = site_output / "daily-reports" / report.with_suffix(".html").name
        assert html.is_file()
        assert RUN_ID in html.read_text(encoding="utf-8")
        homepage_html = (site_output / "index.html").read_text(encoding="utf-8")
        assert (
            "No trade" in homepage_html or "Maintain the current model portfolio" in homepage_html
        )
        assert 'class="papertrader-nav"' in homepage_html
        for publication_name in (
            "decision_snapshot.json",
            "model_portfolio.csv",
            "actionable_signals.csv",
        ):
            assert (site_output / "data" / publication_name).read_bytes() == (
                publication / "data" / "published" / publication_name
            ).read_bytes()

    assert _git(publication, "status", "--porcelain") == ""

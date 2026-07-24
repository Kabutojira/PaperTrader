from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from papertrader.config import Settings
from papertrader.research import (
    ResearchStateError,
    import_watchlist,
    record_source,
    upsert_relationship,
    upsert_security,
    upsert_strategy,
)
from papertrader.tables import read_table, write_table

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def _watchlist_security() -> dict[str, object]:
    return {
        "company_name": "Watchlist Example S.p.A.",
        "instrument_name": "Watchlist Example ordinary shares",
        "instrument_type": "equity",
        "ticker": "WCH",
        "exchange_code": "MIL",
        "venue_mic": "XMIL",
        "provider_symbol": "WCH.MI",
        "currency": "EUR",
        "country": "IT",
        "sector": "Industrials",
        "industry": "Components",
    }


def _watchlist_request() -> dict[str, object]:
    return {
        "watchlist_reason": "User-requested monitoring; research pending.",
        "source": "https://finance.yahoo.com/",
        "securities": [_watchlist_security()],
    }


def test_watchlist_import_is_atomic_idempotent_and_does_not_invent_research(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    first = import_watchlist(
        sandbox_repository,
        sandbox_settings,
        _watchlist_request(),
        now=NOW,
    )
    assert first["created"] == 1
    assert first["unchanged"] == 0

    row = read_table(sandbox_repository, "securities")[0]
    assert row["ticker"] == "WCH"
    assert row["status"] == "watchlist"
    assert row["research_summary"] == ""
    assert row["research_page"] == ""
    assert row["last_research_at"] == ""
    assert row["next_review_at"] == ""

    second = import_watchlist(
        sandbox_repository,
        sandbox_settings,
        _watchlist_request(),
        now=NOW + timedelta(days=1),
    )
    assert second["created"] == 0
    assert second["unchanged"] == 1
    assert read_table(sandbox_repository, "securities") == [row]

    duplicate = _watchlist_request()
    duplicate["securities"] = [_watchlist_security(), _watchlist_security()]
    with pytest.raises(ResearchStateError, match="duplicate provider identity"):
        import_watchlist(
            sandbox_repository,
            sandbox_settings,
            duplicate,
            now=NOW + timedelta(days=2),
        )
    assert read_table(sandbox_repository, "securities") == [row]


def _security_request() -> dict[str, object]:
    return {
        "security_id": "sec_example",
        "issuer_id": "issuer_example",
        "company_name": "Example S.p.A.",
        "instrument_name": "Example ordinary share",
        "instrument_type": "equity",
        "ticker": "EXM",
        "exchange_code": "MIL",
        "venue_mic": "XMIL",
        "provider_symbol": "EXM.MI",
        "broker_symbol": "",
        "currency": "EUR",
        "country": "IT",
        "sector": "Industrials",
        "industry": "Components",
        "status": "watchlist",
        "watchlist_reason": "Evidence-linked valuation review.",
        "research_summary": "Primary evidence supports continued monitoring.",
        "research_page": "data/wiki/securities/sec_example.md",
        "last_research_at": "2026-07-24T12:00:00Z",
        "next_review_at": "2026-08-24T12:00:00Z",
        "source": "source_example",
    }


def _wiki_page(repository: Path) -> None:
    path = repository / "data" / "wiki" / "securities" / "sec_example.md"
    path.write_text(
        "---\n"
        "title: Example security\n"
        "type: security\n"
        "status: maintained\n"
        "tags: [security]\n"
        "created: '2026-07-24'\n"
        "updated: '2026-07-24'\n"
        "provenance: source_example\n"
        "---\n\n"
        "# Example security\n",
        encoding="utf-8",
    )


def test_security_upsert_is_idempotent_and_preserves_immutable_identity(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _wiki_page(sandbox_repository)
    request = _security_request()

    assert upsert_security(sandbox_repository, sandbox_settings, request, now=NOW)
    assert not upsert_security(
        sandbox_repository,
        sandbox_settings,
        request,
        now=NOW + timedelta(days=1),
    )
    row = read_table(sandbox_repository, "securities")[0]
    assert row["security_id"] == "sec_example"
    assert row["provider_symbol"] == "EXM.MI"
    assert row["created_at"] == "2026-07-24T12:00:00Z"

    conflicting = request | {"provider_symbol": "OTHER.MI"}
    with pytest.raises(ResearchStateError, match="immutable identity"):
        upsert_security(
            sandbox_repository,
            sandbox_settings,
            conflicting,
            now=datetime(2026, 7, 25, 12, tzinfo=UTC),
        )

    stale = request | {
        "last_research_at": "2026-07-23T12:00:00Z",
        "next_review_at": "2026-08-23T12:00:00Z",
    }
    with pytest.raises(ResearchStateError, match="older than current research"):
        upsert_security(
            sandbox_repository,
            sandbox_settings,
            stale,
            now=NOW + timedelta(days=2),
        )


def test_security_upsert_requires_wiki_change_before_structured_state(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    with pytest.raises(ResearchStateError, match="must exist before structured upsert"):
        upsert_security(
            sandbox_repository,
            sandbox_settings,
            _security_request(),
            now=NOW,
        )

    assert read_table(sandbox_repository, "securities") == []


def _entity_page(repository: Path, domain: str, entity_id: str, page_type: str) -> None:
    path = repository / "data" / "wiki" / domain / f"{entity_id}.md"
    path.write_text(f"# {page_type}: {entity_id}\n", encoding="utf-8")


def test_relationship_and_strategy_upserts_are_idempotent_across_run_times(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    _wiki_page(sandbox_repository)
    _entity_page(sandbox_repository, "ideas", "idea_example", "Idea")
    _entity_page(
        sandbox_repository,
        "relationships",
        "relationship_example",
        "Relationship",
    )
    _entity_page(sandbox_repository, "strategies", "strategy_example", "Strategy")
    assert upsert_security(
        sandbox_repository,
        sandbox_settings,
        _security_request(),
        now=NOW,
    )
    relationship = {
        "relationship_id": "relationship_example",
        "idea_id": "idea_example",
        "security_id": "sec_example",
        "relationship_type": "beneficiary",
        "direction": "positive",
        "mechanism": "Demand expansion raises addressable revenue.",
        "sensitivity": "medium",
        "confidence": "medium",
        "catalyst": "Verified customer adoption.",
        "invalidation": "Demand does not translate into orders.",
        "status": "accepted",
        "research_page": "data/wiki/relationships/relationship_example.md",
        "last_reviewed_at": "2026-07-24T12:00:00Z",
        "next_review_at": "2026-08-24T12:00:00Z",
    }
    assert upsert_relationship(sandbox_repository, relationship, now=NOW)
    assert not upsert_relationship(
        sandbox_repository,
        relationship,
        now=NOW + timedelta(days=1),
    )

    strategy = {
        "strategy": {
            "strategy_id": "strategy_example",
            "idea_id": "idea_example",
            "security_id": "sec_example",
            "relationship_id": "relationship_example",
            "name": "Example long equity",
            "status": "ready",
            "direction": "long",
            "instrument_type": "equity",
            "thesis": "Evidence supports a bounded long candidate.",
            "entry_rule": "Enter after the next eligible session opens.",
            "exit_rule": "Exit at fair value or review deadline.",
            "invalidation": "Orders fail to confirm demand.",
            "risk_budget_pct": "1",
            "not_before": "2026-07-25T08:00:00Z",
            "expires_at": "2026-08-24T08:00:00Z",
            "research_page": "data/wiki/strategies/strategy_example.md",
        },
        "legs": [
            {
                "leg_id": "leg_1",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": "sec_example",
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
    }
    assert upsert_strategy(sandbox_repository, sandbox_settings, strategy, now=NOW)
    assert not upsert_strategy(
        sandbox_repository,
        sandbox_settings,
        strategy,
        now=NOW + timedelta(days=1),
    )
    updated = {
        **strategy,
        "legs": [{**strategy["legs"][0], "quantity": "12"}],  # type: ignore[index]
    }
    assert upsert_strategy(
        sandbox_repository,
        sandbox_settings,
        updated,
        now=NOW + timedelta(days=2),
    )
    assert read_table(sandbox_repository, "strategy_legs")[0]["quantity"] == "12"
    assert read_table(sandbox_repository, "strategies")[0]["updated_at"] == "2026-07-26T12:00:00Z"


def test_strategy_replay_does_not_regress_execution_owned_active_status(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _wiki_page(sandbox_repository)
    _entity_page(sandbox_repository, "ideas", "idea_example", "Idea")
    _entity_page(sandbox_repository, "relationships", "relationship_example", "Relationship")
    _entity_page(sandbox_repository, "strategies", "strategy_example", "Strategy")
    assert upsert_security(
        sandbox_repository,
        sandbox_settings,
        _security_request(),
        now=NOW,
    )
    relationship = {
        "relationship_id": "relationship_example",
        "idea_id": "idea_example",
        "security_id": "sec_example",
        "relationship_type": "beneficiary",
        "direction": "positive",
        "mechanism": "Demand expansion raises addressable revenue.",
        "sensitivity": "medium",
        "confidence": "medium",
        "catalyst": "Verified customer adoption.",
        "invalidation": "Demand does not translate into orders.",
        "status": "accepted",
        "research_page": "data/wiki/relationships/relationship_example.md",
        "last_reviewed_at": "2026-07-24T12:00:00Z",
        "next_review_at": "2026-08-24T12:00:00Z",
    }
    assert upsert_relationship(sandbox_repository, relationship, now=NOW)
    strategy = {
        "strategy": {
            "strategy_id": "strategy_example",
            "idea_id": "idea_example",
            "security_id": "sec_example",
            "relationship_id": "relationship_example",
            "name": "Example long equity",
            "status": "ready",
            "direction": "long",
            "instrument_type": "equity",
            "thesis": "Evidence supports a bounded long candidate.",
            "entry_rule": "Enter after the next eligible session opens.",
            "exit_rule": "Exit at fair value or review deadline.",
            "invalidation": "Orders fail to confirm demand.",
            "risk_budget_pct": "1",
            "not_before": "",
            "expires_at": "",
            "research_page": "data/wiki/strategies/strategy_example.md",
        },
        "legs": [
            {
                "leg_id": "leg_1",
                "action": "buy",
                "side": "long",
                "instrument_type": "equity",
                "security_id": "sec_example",
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
    }
    assert upsert_strategy(sandbox_repository, sandbox_settings, strategy, now=NOW)
    rows = read_table(sandbox_repository, "strategies")
    rows[0]["status"] = "active"
    write_table(sandbox_repository, "strategies", rows)

    assert not upsert_strategy(
        sandbox_repository,
        sandbox_settings,
        strategy,
        now=NOW + timedelta(days=1),
    )
    assert read_table(sandbox_repository, "strategies")[0]["status"] == "active"


def test_source_registry_rejects_stale_observations_and_replays_exactly(
    sandbox_repository: Path,
) -> None:
    request = {
        "source_id": "source_example",
        "url": "https://example.test/filing",
        "canonical_url": "https://example.test/filing",
        "source_type": "filing",
        "title": "Example filing",
        "publisher": "Example issuer",
        "license": "public-record",
        "status": "available",
        "content_hash": "a" * 64,
        "related_entity_ids": "sec_example",
        "checked_at": "2026-07-24T12:00:00Z",
        "http_status": "200",
        "changed": "true",
        "excerpt": "A short lawful excerpt.",
        "summary": "The filing updates one evidence claim.",
        "run_id": "research-1",
    }
    history_id, changed = record_source(sandbox_repository, request, now=NOW)
    assert changed
    assert record_source(
        sandbox_repository,
        request,
        now=NOW + timedelta(days=1),
    ) == (history_id, False)
    stale = request | {"checked_at": "2026-07-23T12:00:00Z"}
    with pytest.raises(ResearchStateError, match="older than the current registry"):
        record_source(
            sandbox_repository,
            stale,
            now=NOW + timedelta(days=2),
        )

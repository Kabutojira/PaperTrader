"""Weekly research_idea discovery mode: bounded catalogs, no queue fan-out."""

from __future__ import annotations

import configparser
import copy
import hashlib
import html
import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml
import yfinance as yf  # type: ignore[import-untyped]

from papertrader.research_agent import ResearchLimits, research_limits, run_model
from papertrader.research_market import CALENDARS, YFinanceResearchProvider, market_limits
from papertrader.research_queue import instant
from papertrader.research_results import (
    _fresh_observation,
    _reject_copied_source_text,
)
from papertrader.research_state import (
    RESEARCH_ROLES,
    ResearchState,
    contracts,
    csv_bytes,
    read_state,
    timestamp,
    validate_state,
)
from papertrader.research_transaction import apply_files, research_lock

EXCHANGES = {
    "NMS": "XNAS",
    "NGM": "XNAS",
    "NCM": "XNAS",
    "NYQ": "XNYS",
    "ASE": "XASE",
    "PCX": "ARCX",
    "BTS": "BATS",
    "LSE": "XLON",
    "GER": "XETR",
    "FRA": "XFRA",
    "VIE": "XWBO",
    "HKG": "XHKG",
    "KSC": "XKRX",
    "KOE": "XKOS",
    "JPX": "XTKS",
    "TOR": "XTSE",
    "ASX": "XASX",
    "PAR": "XPAR",
    "AMS": "XAMS",
    "MIL": "XMIL",
    "PNK": "XOTC",
}
COMPANY_FIELDS = {
    "company_name",
    "instrument_name",
    "ticker",
    "venue_mic",
    "provider_symbol",
    "currency",
    "country",
    "thesis",
    "source_urls",
    "idea_id",
    "idea_title",
    "mechanism",
}
OPTIONAL_COMPANY_FIELDS = {"research_role", "sector"}
IDEA_FIELDS = {"title", "thesis", "source_urls"}


@dataclass(frozen=True)
class DiscoveryLimits:
    weekly_max_ideas: int = 1
    weekly_max_companies: int = 2
    max_identity_http_requests: int = 8


def discovery_limits(root: Path) -> DiscoveryLimits:
    config = configparser.ConfigParser()
    config.read(root / "research.ini")
    values = {
        key: config.getint("discovery", key, fallback=value)
        for key, value in vars(DiscoveryLimits()).items()
    }
    if (
        not all(0 <= value <= 12 for value in values.values())
        or values["max_identity_http_requests"] < 1
    ):
        raise ValueError("invalid discovery limits")
    return DiscoveryLimits(**values)


def identifier(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256(
        json.dumps(list(parts), ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()[:20]
    return f"{prefix}_{digest}"


def company_key(name: str) -> str:
    name = re.sub(
        r"\bclass\s+[a-z0-9]+\b(?:\s+(?:common|ordinary)\s+(?:stock|shares?))?\s*$",
        "",
        name.casefold(),
    )
    tokens = re.findall(r"[a-z0-9]+", name)
    legal_aliases = {
        "incorporated": "inc",
        "corporation": "corp",
        "company": "co",
        "limited": "ltd",
    }
    return " ".join(legal_aliases.get(token, token) for token in tokens)


def _text(value: Any, *, required: bool = True) -> str:
    if not isinstance(value, str) or len(value) > 2000 or (required and not value.strip()):
        raise ValueError("bounded discovery text required")
    if re.search(r"<\s*\w|javascript\s*:|\[\[|\]\s*\(", value, re.I):
        raise ValueError("candidate text must be original plain prose")
    return " ".join(value.split())


def _urls(value: Any) -> list[str]:
    if (
        not isinstance(value, list)
        or not 1 <= len(value) <= 3
        or any(not isinstance(url, str) or len(url) > 2000 for url in value)
    ):
        raise ValueError("one to three primary source URLs required")
    return sorted(set(value))


class IdentityVerifier:
    """Same yfinance provider, separate small metadata budget; no inference."""

    def __init__(self, root: Path, limits: DiscoveryLimits) -> None:
        market = replace(
            market_limits(root),
            max_http_requests=limits.max_identity_http_requests,
            max_runtime_seconds=60,
        )
        self.provider = YFinanceResearchProvider(market)

    def __call__(self, candidate: dict[str, Any]) -> Mapping[str, Any]:
        metadata = yf.Ticker(
            candidate["provider_symbol"], session=self.provider.session
        ).get_history_metadata(repair=False)
        if not isinstance(metadata, Mapping):
            raise ValueError("provider identity metadata unavailable")
        identity = {
            key: metadata.get(key)
            for key in (
                "symbol",
                "longName",
                "shortName",
                "currency",
                "instrumentType",
                "exchangeName",
            )
        }
        if not (identity["longName"] or identity["shortName"]) or any(
            not identity[key] for key in ("symbol", "currency", "instrumentType", "exchangeName")
        ):
            raise ValueError("provider identity metadata unavailable")
        return identity


def _source(
    state: ResearchState,
    url: str,
    entity: str,
    title: str,
    observations: Mapping[str, Mapping[str, str]],
    now: datetime,
    synthesis: str,
) -> str:
    observed = _fresh_observation(observations, url, now)
    prior = next((row for row in state["source_registry"] if row["url"] == url), None)
    row = (
        prior.copy()
        if prior
        else dict(
            source_id=identifier("source", url),
            url=url,
            title=f"Primary discovery evidence: {title}",
            publisher=urlsplit(url).hostname or "",
            source_type="primary_evidence",
            license="link_only",
            status="valid",
            content_hash="",
            published_at="",
            checked_at="",
            related_entity_ids="",
        )
    )
    _reject_copied_source_text(synthesis, row, observed, trusted_prior=prior)
    row.update(
        checked_at=observed["checked_at"],
        content_hash=observed["content_hash"],
        status="valid",
        related_entity_ids="|".join(
            sorted(set(filter(None, row["related_entity_ids"].split("|"))) | {entity})
        ),
    )
    if prior:
        state["source_registry"][state["source_registry"].index(prior)] = row
    else:
        state["source_registry"].append(row)
    return row["source_id"]


def _page(
    key: str, identity: str, title: str, thesis: str, urls: list[str], *, issuer: str = ""
) -> bytes:
    metadata = {key: identity, "title": title, "status": "unresearched"}
    if issuer:
        metadata["issuer_id"] = issuer
    text = "---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=True) + "---\n"
    text += f"# {html.escape(title)}\n\n"
    text += "**Unresearched candidate — no current valuation or rating.**\n\n"
    text += f"{html.escape(thesis)}\n\n## Sources\n\n"
    text += "\n".join(f"- [Primary evidence](<{url}>)" for url in urls) + "\n"
    return text.encode()


def prepare_candidates(
    root: Path,
    state: ResearchState,
    document: Any,
    *,
    now: datetime,
    observations: Mapping[str, Mapping[str, str]],
    verify_identity: Callable[[dict[str, Any]], Mapping[str, Any]],
    limits: DiscoveryLimits | None = None,
    manual: bool = False,
) -> tuple[ResearchState, dict[str, bytes], dict[str, Any]]:
    limits = limits or discovery_limits(root)
    if (
        not isinstance(document, dict)
        or set(document) != {"operation", "mode", "summary", "ideas", "companies"}
        or document["operation"] != "research_idea"
        or document["mode"] != "discovery"
    ):
        raise ValueError("bounded research_idea discovery result required")
    _text(document["summary"])
    if (
        not isinstance(document["ideas"], list)
        or len(document["ideas"]) > limits.weekly_max_ideas
        or not isinstance(document["companies"], list)
        or len(document["companies"]) > limits.weekly_max_companies
    ):
        raise ValueError("candidate proposal limit exceeded")
    candidate = copy.deepcopy(state)
    pages: dict[str, bytes] = {}
    created: dict[str, list[str]] = {"ideas": [], "companies": [], "known_issuers": []}
    idea_titles = {row["title"].casefold(): row["idea_id"] for row in candidate["ideas"]}
    provenance = "manual_import" if manual else "weekly_discovery"
    schema = contracts(root)
    for value in document["ideas"]:
        if not isinstance(value, dict) or set(value) != IDEA_FIELDS:
            raise ValueError("invalid idea candidate fields")
        title, thesis = _text(value["title"]), _text(value["thesis"])
        urls = _urls(value["source_urls"])
        if title.casefold() in idea_titles:
            continue
        identity = identifier("idea", title.casefold())
        source_ids = [
            _source(candidate, url, identity, title, observations, now, thesis) for url in urls
        ]
        page = f"data/wiki/ideas/{identity}.md"
        row = dict.fromkeys(schema["ideas"].columns, "")
        row.update(
            idea_id=identity,
            title=title,
            thesis=thesis,
            status="unresearched",
            source_ids="|".join(source_ids),
            research_page=page,
            created_on=now.date().isoformat(),
            discovery_provenance=provenance,
        )
        candidate["ideas"].append(row)
        pages[page] = _page("idea_id", identity, title, thesis, urls)
        idea_titles[title.casefold()] = identity
        created["ideas"].append(identity)
    for value in document["companies"]:
        if (
            not isinstance(value, dict)
            or not set(value) >= COMPANY_FIELDS
            or set(value) - COMPANY_FIELDS - OPTIONAL_COMPANY_FIELDS
        ):
            raise ValueError("invalid company candidate fields")
        fields = {
            key: _text(value[key], required=key not in {"idea_id", "idea_title", "mechanism"})
            for key in COMPANY_FIELDS - {"source_urls"}
        }
        role = value.get("research_role", "long")
        if role not in RESEARCH_ROLES or (not manual and role != "long"):
            raise ValueError("invalid manual research role")
        sector = _text(value.get("sector", ""), required=False)
        urls = _urls(value["source_urls"])
        # Verify every proposed citation before catalog creation, including duplicates.
        for url in urls:
            _fresh_observation(observations, url, now)
        if (
            fields["venue_mic"] not in CALENDARS
            or not re.fullmatch(r"[A-Z]{3}", fields["currency"])
            or not re.fullmatch(r"[A-Z]{2}", fields["country"])
        ):
            raise ValueError("invalid company listing identity")
        ticker_key = fields["ticker"].replace(".", "-")
        provider_ticker = fields["provider_symbol"].split(".")[0]
        if ticker_key != provider_ticker:
            raise ValueError("ticker does not match verified provider instrument")
        metadata = verify_identity(fields)
        provider_currency = "GBP" if metadata.get("currency") == "GBp" else metadata.get("currency")
        verified_name = metadata.get("longName") or metadata.get("shortName")
        if (
            not isinstance(verified_name, str)
            or not company_key(verified_name)
            or company_key(verified_name) != company_key(fields["company_name"])
            or metadata.get("symbol") != fields["provider_symbol"]
            or provider_currency != fields["currency"]
            or metadata.get("instrumentType") != "EQUITY"
            or EXCHANGES.get(str(metadata.get("exchangeName"))) != fields["venue_mic"]
        ):
            raise ValueError("public company identity could not be independently reconciled")
        known = next(
            (
                row
                for row in candidate["securities"]
                if company_key(row["company_name"]) == company_key(verified_name)
            ),
            None,
        )
        same_instrument = next(
            (
                row
                for row in candidate["securities"]
                if (row["provider_symbol"], row["venue_mic"], row["currency"])
                == (fields["provider_symbol"], fields["venue_mic"], fields["currency"])
            ),
            None,
        )
        if same_instrument and (not known or same_instrument["issuer_id"] != known["issuer_id"]):
            raise ValueError("provider instrument conflicts with issuer identity")
        # Weekly discovery dedupes companies; an explicit import can retain a distinct
        # verified share class while reusing the issuer's immutable identity.
        if same_instrument or (known and not manual):
            security = same_instrument or known
            assert security is not None
            created["known_issuers"].append(security["issuer_id"])
            if manual:
                for url in urls:
                    _source(
                        candidate,
                        url,
                        security["security_id"],
                        verified_name,
                        observations,
                        now,
                        fields["thesis"],
                    )
                if "research_role" in value:
                    security["research_role"] = role
                if "sector" in value:
                    security["sector"] = sector
        else:
            issuer = (
                known["issuer_id"] if known else identifier("issuer", company_key(verified_name))
            )
            identity = identifier(
                "security",
                fields["provider_symbol"],
                fields["venue_mic"],
                fields["currency"],
                "equity",
            )
            source_ids = [
                _source(
                    candidate, url, identity, verified_name, observations, now, fields["thesis"]
                )
                for url in urls
            ]
            page = f"data/wiki/securities/{identity}.md"
            security = dict.fromkeys(schema["securities"].columns, "")
            security.update(
                security_id=identity,
                issuer_id=issuer,
                company_name=verified_name,
                instrument_name=fields["instrument_name"],
                instrument_type="equity",
                ticker=fields["ticker"],
                venue_mic=fields["venue_mic"],
                provider_symbol=fields["provider_symbol"],
                currency=fields["currency"],
                country=fields["country"],
                sector=sector,
                research_role=role,
                status="watchlist",
                research_status="unresearched",
                discovery_provenance=provenance + ":" + "|".join(source_ids),
                research_page=page,
                created_at=instant(now),
                updated_at=instant(now),
            )
            candidate["securities"].append(security)
            pages[page] = _page(
                "security_id", identity, verified_name, fields["thesis"], urls, issuer=issuer
            )
            created["companies"].append(identity)
        idea = fields["idea_id"] or idea_titles.get(fields["idea_title"].casefold(), "")
        if fields["idea_title"] and not idea:
            raise ValueError("unknown related idea title")
        if idea:
            if (
                not any(row["idea_id"] == idea for row in candidate["ideas"])
                or not fields["mechanism"]
            ):
                raise ValueError("known idea and evidenced causal mechanism required")
            source_ids = [
                _source(
                    candidate,
                    url,
                    security["security_id"],
                    verified_name,
                    observations,
                    now,
                    fields["mechanism"],
                )
                for url in urls
            ]
            relation_id = identifier("relationship", idea, security["security_id"])
            if not any(
                row["idea_id"] == idea and row["security_id"] == security["security_id"]
                for row in candidate["relationships"]
            ):
                row = dict.fromkeys(schema["relationships"].columns, "")
                row.update(
                    relationship_id=relation_id,
                    idea_id=idea,
                    security_id=security["security_id"],
                    relationship_type="candidate",
                    direction="uncertain",
                    mechanism=fields["mechanism"],
                    confidence="low",
                    status="candidate",
                    source_ids="|".join(source_ids),
                    research_page=security["research_page"],
                    last_reviewed_at=instant(now),
                )
                candidate["relationships"].append(row)
    all_pages = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for directory in ("securities", "ideas")
        for path in (root / "data/wiki" / directory).glob("*.md")
    }
    all_pages.update(pages)
    errors = validate_state(root, candidate, pages=all_pages)
    if errors:
        raise ValueError("; ".join(errors[:8]))
    if candidate["research_queue"] != state["research_queue"]:
        raise ValueError("discovery cannot create research obligations")
    return candidate, pages, created


def run_discovery(
    root: Path,
    *,
    dry_run: bool = True,
    force: bool = False,
    executor: Callable[[Path, dict[str, Any], ResearchLimits], dict[str, Any]] = run_model,
    verify_identity: Callable[[dict[str, Any]], Mapping[str, Any]] | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    with research_lock(root):
        state = read_state(root)
        errors = validate_state(root, state)
        if errors:
            raise ValueError("corrupt research data before discovery")
        path = root / "data/status.json"
        status = json.loads(path.read_text()) if path.exists() else {}
        research = status.setdefault("research", {})
        previous = research.get("last_discovery_attempt_at", "")
        due = not previous or clock() - timestamp(previous) >= timedelta(days=7)
        limits = discovery_limits(root)
        if dry_run or (not due and not force):
            return dict(
                status="dry_run" if dry_run else "not_due",
                exit_code=0,
                due=due,
                limits=vars(limits),
                model_calls=0,
            )
        research.pop("discovery_error", None)
        research["last_discovery_attempt_at"] = instant(clock())
        research["discovery_status"] = "running"
        apply_files(
            root,
            {"data/status.json": (json.dumps(status, sort_keys=True, indent=2) + "\n").encode()},
        )
        packet = dict(
            operation="research_idea",
            mode="discovery",
            identity={"idea_id": "discovery", "title": "Bounded weekly company and idea discovery"},
            as_of=instant(clock()),
            limits=vars(limits),
            existing_ideas=[{"idea_id": r["idea_id"], "title": r["title"]} for r in state["ideas"]],
            existing_companies=[
                {"issuer_id": r["issuer_id"], "company_name": r["company_name"]}
                for r in state["securities"]
            ],
            skill=(root / "skills/research_idea/SKILL.md").read_text(),
        )
        try:
            response = executor(root, packet, research_limits(root))
            candidate, pages, created = prepare_candidates(
                root,
                state,
                response["result"],
                now=clock(),
                observations=response["observations"],
                verify_identity=verify_identity or IdentityVerifier(root, limits),
                limits=limits,
            )
            research["discovery_status"] = "succeeded"
            research["last_discovery_success_at"] = instant(clock())
            files = {
                **pages,
                **{
                    contract.path: csv_bytes(contract, candidate[name])
                    for name, contract in contracts(root).items()
                },
                "data/status.json": (json.dumps(status, sort_keys=True, indent=2) + "\n").encode(),
            }
            changed = apply_files(root, files)
            return dict(
                status="succeeded", exit_code=0, created=created, changed=changed, model_calls=1
            )
        except Exception as exc:
            research["discovery_status"] = "failed"
            research["discovery_error"] = type(exc).__name__
            apply_files(
                root,
                {
                    "data/status.json": (
                        json.dumps(status, sort_keys=True, indent=2) + "\n"
                    ).encode()
                },
            )
            return dict(status="failed", exit_code=3, error=type(exc).__name__, model_calls=1)

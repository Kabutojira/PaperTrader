"""Deterministic current research rankings and a source-linked Quartz input tree."""

from __future__ import annotations

import csv
import io
import json
import posixpath
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from papertrader.research_market import _read
from papertrader.research_ratings import rating_thresholds, reprice, valuation_coverage
from papertrader.research_state import (
    ResearchState,
    Row,
    decimal,
    read_state,
    timestamp,
    validate_state,
)
from papertrader.research_transaction import apply_files, safe_path

RANK_COLUMNS = (
    "security_id",
    "issuer_id",
    "company_name",
    "ticker",
    "currency",
    "price",
    "price_date",
    "weighted_fair_value",
    "base_fair_value",
    "expected_return_pct",
    "adjusted_return_pct",
    "rating",
    "confidence",
    "assessed_at",
    "valid_until",
    "research_page",
)
PUBLIC_FOLDERS = {
    "securities",
    "ideas",
    "raw",
    "concepts",
    "relationships",
    "comparisons",
    "queries",
}
CURRENT_ROOT_PAGES = {
    "index.md",
    "security-catalog.md",
    "idea-catalog.md",
    "research-catalog.md",
    "rating-methodology.md",
}
BACKUP = "https://github.com/Kabutojira/PaperTrader/blob/pre-research-only-20261018/data/wiki/"
WIKILINK = re.compile(r"\[\[([^\]|#]+)(#[^\]|]+)?(?:\|([^\]]+))?\]\]")
MDLINK = re.compile(r"(!?\[[^\]]*\]\()([^\s)]+)(\))")


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", " ").replace("<", "&lt;")


def _link(row: Row, title: str) -> str:
    path = row.get("research_page", "").removeprefix("data/wiki/").removesuffix(".md")
    return f"[{_cell(title)}]({path})" if path else _cell(title)


def _number(value: str) -> str:
    return f"{decimal(value):,.2f}" if value else "—"


def _money(value: str) -> str:
    if not value:
        return "—"
    amount = decimal(value)
    if amount == 0:
        return "0.00"
    places = 2 if abs(amount) >= 1 else max(4, -abs(amount).adjusted() + 2)
    return f"{amount:,.{places}f}"


def snapshot(root: Path, *, now: datetime, state: ResearchState | None = None) -> dict[str, Any]:
    state = read_state(root) if state is None else state
    errors = validate_state(root, state)
    if errors:
        raise ValueError("; ".join(errors[:8]))
    quotes = {row["security_id"]: row for row in _read(root / "data/market/latest.csv")}
    assessments = {row["security_id"]: row for row in state["security_assessments"]}
    sources = {row["source_id"]: row for row in state["source_registry"]}
    thresholds = rating_thresholds(root)
    coverage = dict(
        instruments=len(state["securities"]),
        issuers=0,
        researched=len(assessments),
        current=0,
        stale=0,
        unrated=0,
        failed_tickers=0,
        watchlist_instruments=0,
        watchlist_complete=0,
        watchlist_missing_research=0,
        watchlist_valuation_unsupported=0,
        watchlist_incomplete_research=0,
        watchlist_needs_attention=0,
    )
    rows: list[Row] = []
    for security in state["securities"]:
        sid = security["security_id"]
        assessment = assessments.get(sid)
        coverage_status = valuation_coverage(assessment)
        if security["status"] in {"active", "watching", "watchlist"}:
            coverage["watchlist_instruments"] += 1
            coverage[f"watchlist_{coverage_status}"] += 1
            if security["research_status"] == "needs_attention":
                coverage["watchlist_needs_attention"] += 1
        quote = dict(quotes.get(sid, {}))
        # Validate the quote against canonical listing identity, not ticker text.
        if any(
            quote.get(key) != security[key] for key in ("provider_symbol", "currency", "venue_mic")
        ):
            quote["status"] = "identity_mismatch"
        price_rows = _read(root / f"data/market/prices/{sid}.csv")
        splits = [
            row["date"]
            for row in price_rows
            if decimal(row.get("stock_splits") or "0") not in (0, 1)
        ]
        opinion = (
            reprice(
                assessment,
                quote,
                now=now,
                thresholds=thresholds,
                latest_split_date=max(splits, default=""),
            )
            if assessment
            else {"rating": "unrated", "reason": "unresearched"}
        )
        if assessment:
            fresh = (
                timestamp(assessment["valid_until"]) > now
                and timestamp(assessment["assessed_at"]) <= now
            )
            coverage["current" if fresh else "stale"] += 1
            # A source must still be valid and have been checked during this assessment.
            if any(
                source_id not in sources
                or sources[source_id]["status"] not in {"available", "valid"}
                or not sources[source_id]["checked_at"]
                or timestamp(sources[source_id]["checked_at"])
                < timestamp(assessment["assessed_at"]) - timedelta(hours=1)
                or timestamp(sources[source_id]["checked_at"]) > now
                for source_id in assessment["source_ids"].split("|")
                if source_id
            ):
                opinion.update(rating="unrated", reason="source_evidence_unavailable")
        if opinion["rating"] == "unrated":
            coverage["unrated"] += 1
        if quote.get("status") != "current":
            coverage["failed_tickers"] += 1
        row = {key: security.get(key, "") for key in RANK_COLUMNS}
        row["entity_status"] = security["research_status"]
        row["valuation_coverage"] = coverage_status
        row["bear_fair_value"] = (assessment or {}).get("bear_fair_value", "")
        row["bull_fair_value"] = (assessment or {}).get("bull_fair_value", "")
        row.update(price=quote.get("close", ""), price_date=quote.get("price_date", ""), **opinion)
        if assessment:
            row.update(
                {
                    key: assessment[key]
                    for key in ("base_fair_value", "confidence", "assessed_at", "valid_until")
                }
            )
        rows.append(row)
    coverage["issuers"] = len({row["issuer_id"] for row in rows})

    def rank(categories: set[str], *, sell: bool) -> list[Row]:
        eligible = [row for row in rows if row["rating"] in categories]
        eligible.sort(
            key=lambda row: (
                decimal(row["adjusted_return_pct"]) * (1 if sell else -1),
                row["issuer_id"],
                row["security_id"],
            )
        )
        selected: list[Row] = []
        seen: set[str] = set()
        for row in eligible:
            if row["issuer_id"] not in seen:
                selected.append({key: row.get(key, "") for key in RANK_COLUMNS})
                seen.add(row["issuer_id"])
            if len(selected) == 10:
                break
        return selected

    status_file = root / "data/status.json"
    status = json.loads(status_file.read_text()) if status_file.exists() else {}
    return dict(
        version=1,
        coverage=coverage,
        buys=rank({"buy", "strong_buy"}, sell=False),
        sells=rank({"sell", "strong_sell"}, sell=True),
        last_market_session=max((row.get("price_date", "") for row in quotes.values()), default=""),
        last_research_at=max(
            (row.get("last_research_at", "") for row in state["securities"]), default=""
        ),
        last_successful_research=status.get("research", {}).get("last_success_at", ""),
        phase_health={
            phase: status.get(phase, {}).get("status", "not_recorded")
            for phase in ("market", "research")
        },
        companies=rows,
        ideas=state["ideas"],
    )


def _table(rows: list[Row]) -> str:
    if not rows:
        return (
            "No current, supportable ratings qualify. Expired and unsupported "
            "research is excluded.\n"
        )
    header = (
        "| Company / thesis & sources | Ticker | Currency | Price | Price "
        "as of | Weighted / base fair value | Implied / adjusted return | "
        "Rating | Confidence | Researched / expiry |\n"
    )
    result = header + "| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- | --- |\n"
    for row in rows:
        values = [
            _link(row, row["company_name"]),
            row["ticker"],
            row["currency"],
            _money(row["price"]),
            row["price_date"],
            f"{_money(row['weighted_fair_value'])} / {_money(row['base_fair_value'])}",
            f"{_number(row['expected_return_pct'])}% / {_number(row['adjusted_return_pct'])}%",
            row["rating"],
            row["confidence"],
            f"{row['assessed_at']} / {row['valid_until']}",
        ]
        result += (
            "| "
            + " | ".join(_cell(value) if index else value for index, value in enumerate(values))
            + " |\n"
        )
    return result


def render_views(view: dict[str, Any]) -> dict[str, bytes]:
    coverage = view["coverage"]
    home = (
        "---\ntitle: Investment research\ntype: research-home\n---\n\n# "
        "Company research and valuation\n\n"
    )
    home += (
        "Current research opinions in each instrument's native currency. "
        "Fair values change only after research.\n\n"
    )
    home += f"## Top 10 Buy\n\n{_table(view['buys'])}\n## Top 10 Sell\n\n{_table(view['sells'])}\n"
    home += (
        "Sell denotes researched overvaluation or downside, regardless of "
        "ownership. It is not a short-trade recommendation.\n\n"
    )
    home += (
        "Confidence scales prospective return toward zero: high x1, "
        "medium x0.7, low x0.4. Ratings require at least medium "
        "confidence, complete scenarios and current evidence. Lists "
        "contain up to ten issuers and are never padded. [Rating "
        "methodology](rating-methodology).\n\n"
    )
    home += "## Coverage and health\n\n"
    home += (
        f"{coverage['issuers']} companies / {coverage['instruments']} instruments; "
        f"{coverage['researched']} assessed, {coverage['current']} in date, "
        f"{coverage['stale']} stale; "
        f"{coverage['unrated']} currently unrated. "
        f"{coverage['failed_tickers']} quotes require attention.\n\n"
        f"Last observed market session: {view['last_market_session'] or 'unavailable'}. "
        "Last successful research: "
        f"{view['last_successful_research'] or 'not recorded since cutover'}. "
        f"Market: {view['phase_health']['market']}; "
        f"research: {view['phase_health']['research']}. "
        "Publication has an independent deployment outcome; its revision and build date "
        "appear in the deployed snapshot metadata.\n\n"
    )
    home += (
        f"Watchlist valuation coverage: **{coverage['watchlist_complete']} / "
        f"{coverage['watchlist_instruments']} instruments** have complete sourced "
        "bear/base/bull research, including historical assessments. "
        f"Missing research: {coverage['watchlist_missing_research']}; unsupported "
        f"valuation: {coverage['watchlist_valuation_unsupported']}; incomplete "
        f"research: {coverage['watchlist_incomplete_research']}. "
        f"Needs attention: {coverage['watchlist_needs_attention']}. "
        "Baseline coverage and current freshness are separate: expired research "
        "never enters current rankings. Missing or incomplete coverage is scheduled "
        "ahead of ordinary expiry refreshes within the daily budget. "
        "Unsupported cases remain visible until evidence supports a valuation.\n\n"
    )
    recent = [
        (row.get("assessed_at", ""), row, row["company_name"])
        for row in view["companies"]
        if row.get("assessed_at")
    ]
    recent += [
        (row.get("last_reviewed_on", ""), row, row["title"])
        for row in view["ideas"]
        if row.get("last_reviewed_on")
    ]
    recent.sort(key=lambda item: (item[0], item[2]), reverse=True)
    home += "## Recently updated research\n\n"
    home += (
        "\n".join(
            f"- {_link(row, title)} — {date}; "
            f"{row.get('reason') or row.get('status') or row.get('rating', '')}"
            for date, row, title in recent[:10]
        )
        or "No research updates yet."
    )
    home += (
        "\n\n## Ideas and interesting companies\n\n[Company "
        "catalog](security-catalog) · [Idea catalog](idea-catalog) · "
        "[Research sources and navigation](research-catalog)\n\n"
    )
    home += (
        "[Buy CSV](data/top_buys.csv) · [Sell CSV](data/top_sells.csv) · "
        "[Current rankings JSON](data/research_rankings.json)\n"
    )
    catalog = (
        "---\ntitle: Company catalog\n---\n\n# Companies\n\nHistorical "
        "and stale research remains readable; only current validated "
        "opinions enter rankings.\n\n| Company | Instrument | Status / "
        "limitation | Valuation coverage | Bear / base / bull fair value | Researched | Expiry |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    for row in sorted(view["companies"], key=lambda row: (row["company_name"], row["security_id"])):
        catalog += (
            f"| {_link(row, row['company_name'])} | "
            f"{_cell(row['ticker'])} ({row['currency']}) | "
            f"{_cell(row.get('entity_status', ''))}: "
            f"{_cell(row.get('reason') or row['rating'])} | "
            f"{row['valuation_coverage']} | "
            f"{_money(row['bear_fair_value'])} / {_money(row['base_fair_value'])} / "
            f"{_money(row['bull_fair_value'])} {row['currency']} | "
            f"{row.get('assessed_at') or 'unresearched'} | "
            f"{row.get('valid_until') or '—'} |\n"
        )
    ideas = "---\ntitle: Idea catalog\n---\n\n# Investment ideas\n\n"
    ideas += "\n".join(
        f"- {_link(row, row['title'])} — {_cell(row['status'])}; "
        f"reviewed {row['last_reviewed_on'] or 'not yet'}"
        for row in sorted(view["ideas"], key=lambda row: row["idea_id"])
    )
    navigation = (
        "---\ntitle: Research catalog\n---\n\n# Research\n\n[Company "
        "catalog](security-catalog) · [Idea catalog](idea-catalog) · "
        "[Current rankings](index)\n\nEach company and idea page retains "
        "its current source citations. Older conclusions are marked stale "
        "in the company catalog.\n"
    )
    files = {
        f"data/wiki/{name}.md": content.encode()
        for name, content in (
            ("index", home),
            ("security-catalog", catalog),
            ("idea-catalog", ideas),
            ("research-catalog", navigation),
        )
    }
    files["data/published/research_rankings.json"] = (
        json.dumps(
            {key: value for key, value in view.items() if key not in {"companies", "ideas"}},
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode()
    for name, key in (("top_buys", "buys"), ("top_sells", "sells")):
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=RANK_COLUMNS)
        writer.writeheader()
        writer.writerows(view[key])
        files[f"data/published/{name}.csv"] = buffer.getvalue().encode()
    return files


def publish_views(root: Path, *, now: datetime) -> list[str]:
    # The CLI normally creates this through research_lock. Keep the public
    # deterministic publisher usable in a clean checkout while preserving the
    # transaction journal's no-symlink boundary.
    transaction_directory = root / ".cache"
    if transaction_directory.is_symlink():
        raise ValueError("unsafe research transaction directory")
    transaction_directory.mkdir(exist_ok=True)
    return apply_files(root, render_views(snapshot(root, now=now)))


def prepare_site(
    root: Path, output: Path, *, now: datetime, publication: dict[str, str] | None = None
) -> dict[str, int]:
    """Build an isolated current-page closure, without mutating the checkout."""
    if output.exists() and any(output.iterdir()):
        raise ValueError("site staging output must be empty")
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("site staging must be outside the repository")
    state = read_state(root)
    view = snapshot(root, now=now, state=state)
    files = render_views(view)
    opinions = {
        row["research_page"].removeprefix("data/wiki/"): row
        for row in view["companies"]
        if row["research_page"]
    }
    if publication is not None:
        if (
            set(publication) != {"commit_sha", "built_at", "run_url"}
            or not re.fullmatch(r"[0-9a-f]{40}", publication["commit_sha"])
            or not re.fullmatch(
                r"https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/actions/runs/[0-9]+",
                publication["run_url"],
            )
        ):
            raise ValueError("invalid publication metadata")
        timestamp(publication["built_at"])
        files["data/published/publication.json"] = (
            json.dumps(publication, sort_keys=True, indent=2) + "\n"
        ).encode()
        files["data/wiki/index.md"] += (
            "\n## Published snapshot\n\n"
            f"Built {publication['built_at']} from committed revision "
            f"`{publication['commit_sha']}`. "
            f"[Independent deployment outcome]({publication['run_url']}). "
            "This metadata describes the artifact served here; a failed newer deployment "
            "leaves this snapshot available.\n"
        ).encode()
    wiki = root / "data/wiki"
    available = {
        path.relative_to(wiki).as_posix(): path
        for path in wiki.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    basenames = {Path(name).stem: name for name in sorted(available)}
    generated_pages = {
        name.removeprefix("data/wiki/") for name in files if name.startswith("data/wiki/")
    }
    pending = {
        row["research_page"].removeprefix("data/wiki/")
        for row in state["securities"] + state["ideas"]
        if row["research_page"]
    }
    pending.add("rating-methodology.md")
    retained: dict[str, bytes] = {}

    def resolve_link(target: str, origin: str) -> str | None:
        clean = unquote(target).split("#", 1)[0].removeprefix("data/wiki/")
        if not clean or "\\" in clean or clean.startswith("/"):
            return None

        def normalize(candidate: str) -> str | None:
            normalized = posixpath.normpath(candidate)
            if normalized in {"", ".", ".."} or normalized.startswith("../"):
                return None
            return normalized

        candidates: list[str] = []
        for value in (posixpath.join(posixpath.dirname(origin), clean), clean):
            normalized = normalize(value)
            if normalized:
                candidates.extend(
                    [normalized, normalized if normalized.endswith(".md") else normalized + ".md"]
                )
        # Unique-stem fallback supports old bare wikilinks, but must never turn
        # a lexical escape into an unrelated in-tree page with the same name.
        if ".." not in Path(clean).parts:
            stem_match = basenames.get(Path(clean).stem, "")
            if stem_match:
                candidates.append(stem_match)
        for candidate in candidates:
            if candidate in available or candidate in generated_pages:
                return candidate
        return None

    while pending:
        name = min(pending)
        pending.remove(name)
        # Root views are freshly rendered above. They remain valid link targets,
        # but committed copies must never re-enter the closure and overwrite the
        # current rankings/catalogs in the final merge.
        if name in generated_pages or name in retained or name not in available:
            continue
        safe_path(root, f"data/wiki/{name}")
        path = available[name]
        if path.suffix != ".md":
            retained[name] = path.read_bytes()
            continue
        text = path.read_text()
        if name in opinions:
            row = opinions[name]
            frontmatter, body = text.split("\n---\n", 1)
            text = (
                frontmatter
                + "\n---\n\n"
                + (
                    f"> Current research opinion: **{row['rating']}**; "
                    f"entity status: {row['entity_status']}. "
                    f"{row.get('reason') or 'Current supported valuation'}. "
                    f"Assessed: {row.get('assessed_at') or 'not yet'}; "
                    f"expiry: {row.get('valid_until') or 'not applicable'}. "
                    "Older conclusions below remain historical when research is "
                    "stale or unsupported.\n\n"
                )
                + body
            )

        def rewrite(target: str, label: str, original: str, origin: str = name) -> str:
            resolved = resolve_link(target, origin)
            if resolved and (
                Path(resolved).parts[0] in PUBLIC_FOLDERS or resolved in CURRENT_ROOT_PAGES
            ):
                pending.add(resolved)
                return original
            if resolved:
                return f"[{label}]({BACKUP}{resolved})"
            # Existing wiki references without a current target retain readable text.
            return label

        text = WIKILINK.sub(lambda match: rewrite(match[1], match[3] or match[1], match[0]), text)

        def markdown(match: re.Match[str]) -> str:
            target = match[2]
            if ":" in target or target.startswith("#"):
                return match[0]
            return rewrite(target, match[1].removeprefix("!")[1:-2], match[0])

        text = MDLINK.sub(markdown, text)
        retained[name] = text.encode()
    for name, content in retained.items():
        files[f"data/wiki/{name}"] = content
    for name, content in files.items():
        relative = (
            name.removeprefix("data/wiki/")
            if name.startswith("data/wiki/")
            else "data/" + Path(name).name
        )
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return dict(pages=sum(name.endswith(".md") for name in retained) + 4, files=len(files))

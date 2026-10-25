"""Complete current research results validated before any canonical write."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from papertrader.research_queue import instant
from papertrader.research_ratings import VALUATION_RESEARCH_FIELDS, valuation_coverage
from papertrader.research_state import (
    ResearchState,
    Row,
    contracts,
    csv_bytes,
    timestamp,
    validate_state,
)
from papertrader.research_transaction import apply_files

RESULT_KEYS = {
    "operation",
    "entity_id",
    "outcome",
    "summary",
    "assessment",
    "idea",
    "sources",
    "relationships",
    "pages",
}
OUTCOMES = {"updated", "no_change", "not_supportable", "skip_as_stale"}
MAX_SOURCE_QUOTE_WORDS = 25
COPY_EXEMPT_LICENSE_PREFIXES = ("public-domain", "permissive", "user-owned")
RESULT_VALIDATION_CODES = frozenset(
    {
        "assessment.assessed_at.future",
        "assessment.assessed_at.invalid",
        "assessment.assessed_at.stale",
        "assessment.valid_until.exceeds_freshness",
        "assessment.valid_until.invalid",
        "assessment.valid_until.not_after_assessed",
        "assessment.thesis.missing",
        "assessment.method_rationale.missing",
        "assessment.key_assumptions.missing",
        "assessment.downside.missing",
        "assessment.catalysts.missing",
        "assessment.invalidation_conditions.missing",
        "assessment.limitations.missing",
        "assessment.source_ids.missing",
        "assessment.source_ids.not_currently_opened",
        "assessment.source_ids.status_invalid",
        "assessment.source_ids.target_entity_missing",
        "assessment.source_ids.url_missing_from_page",
        "idea.last_reviewed_on.invalid",
        "idea.source_ids.missing",
        "idea.source_ids.not_currently_opened",
        "idea.source_ids.status_invalid",
        "idea.source_ids.target_entity_missing",
        "idea.source_ids.url_missing_from_page",
        "relationship.source_ids.missing",
        "relationship.source_ids.not_currently_opened",
        "relationship.source_ids.status_invalid",
        "relationship.source_ids.target_entity_missing",
        "relationship.source_ids.url_missing_from_page",
        "source.status.invalid",
        "source.title.missing",
        "source.related_entity_ids.target_missing",
        "source.published_at.future",
        "source.published_at.invalid",
        "state.assessment.invalid",
        "state.assessment.scoring.invalid",
        "state.integrity.invalid",
        "state.research_page.invalid",
    }
)


class ResearchResultValidationError(ValueError):
    """A controller-owned diagnostic code without a model-controlled value."""

    def __init__(self, diagnostic_code: str) -> None:
        if diagnostic_code not in RESULT_VALIDATION_CODES:
            raise ValueError("unknown research result validation code")
        self.diagnostic_code = diagnostic_code
        super().__init__("invalid research result field")


def _model_timestamp(value: str, field: str) -> datetime:
    try:
        return timestamp(value)
    except ValueError:
        raise ResearchResultValidationError(f"{field}.invalid") from None


def _state_validation_code(errors: list[str]) -> str:
    page_prefixes = (
        "broken entity wikilink:",
        "missing or invalid research page:",
        "missing research page:",
        "unsafe research page:",
    )
    if any(error.startswith(page_prefixes) for error in errors):
        return "state.research_page.invalid"
    scoring_markers = (
        "score",
        "scoring rubric",
        "valuation reference",
        "unscored valuation",
    )
    if any(
        error.startswith("invalid assessment ")
        and any(marker in error for marker in scoring_markers)
        for error in errors
    ):
        return "state.assessment.scoring.invalid"
    if any(
        error.startswith(("assessment identity/currency mismatch:", "invalid assessment "))
        for error in errors
    ):
        return "state.assessment.invalid"
    return "state.integrity.invalid"


def _row(value: Any, columns: tuple[str, ...]) -> Row:
    if (
        not isinstance(value, dict)
        or set(value) != set(columns)
        or any(not isinstance(v, str) or len(v) > 12000 for v in value.values())
    ):
        raise ValueError("complete string-valued research row required")
    return value


def _upsert(rows: list[Row], row: Row, key: str) -> None:
    for index, current in enumerate(rows):
        if current[key] == row[key]:
            rows[index] = row.copy()
            return
    rows.append(row.copy())


def _fresh_observation(
    observations: Mapping[str, Mapping[str, str]], url: str, now: datetime
) -> Mapping[str, str]:
    observed = observations.get(url)
    if observed is None:
        raise ValueError("source URL was not verified during this operation")
    try:
        checked = timestamp(observed["checked_at"])
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid source verification evidence") from exc
    if checked > now + timedelta(minutes=5) or now - checked > timedelta(hours=1):
        raise ValueError("source URL was not verified during this operation")
    if not re.fullmatch(r"[a-f0-9]{64}", observed.get("content_hash", "")):
        raise ValueError("invalid source verification evidence")
    return observed


def _words(text: str) -> list[str]:
    return re.findall(r"[\w']+", text.casefold(), flags=re.UNICODE)


def _reject_copied_source_text(
    markdown: str,
    source: Row,
    observed: Mapping[str, str],
    *,
    trusted_prior: Row | None,
) -> None:
    if (
        trusted_prior is not None
        and trusted_prior["url"] == source["url"]
        and trusted_prior["license"].casefold().startswith(COPY_EXEMPT_LICENSE_PREFIXES)
    ):
        return
    source_text = observed.get("source_text", "")
    if not source_text:
        raise ValueError("copyright comparison needs bounded opened source text")
    width = MAX_SOURCE_QUOTE_WORDS + 1
    source_words = _words(source_text)
    page_words = _words(markdown)
    if len(source_words) < width or len(page_words) < width:
        return
    source_shingles = {
        tuple(source_words[index : index + width]) for index in range(len(source_words) - width + 1)
    }
    if any(
        tuple(page_words[index : index + width]) in source_shingles
        for index in range(len(page_words) - width + 1)
    ):
        raise ValueError("research page copies more than 25 source words")


def prepare_result(
    root: Path,
    state: ResearchState,
    result: Any,
    *,
    operation: str,
    entity_id: str,
    now: datetime,
    observations: Mapping[str, Mapping[str, str]],
    freshness_days: int = 30,
) -> tuple[ResearchState, dict[str, bytes]]:
    """Observations come from the trusted read-only web broker, never model JSON."""
    if not isinstance(result, dict) or set(result) != RESULT_KEYS:
        raise ValueError("invalid completed research result schema")
    if (
        result["operation"] != operation
        or result["entity_id"] != entity_id
        or operation not in {"research_security", "research_idea"}
    ):
        raise ValueError("research result identity mismatch")
    if (
        result["outcome"] not in OUTCOMES
        or not isinstance(result["summary"], str)
        or not 1 <= len(result["summary"]) <= 2000
    ):
        raise ValueError("research outcome/summary required")
    for key in ("sources", "relationships"):
        if not isinstance(result[key], list) or len(result[key]) > 12:
            raise ValueError("bounded source/relationship list required")
    if (
        not isinstance(result["pages"], dict)
        or len(result["pages"]) > 1
        or any(
            not isinstance(k, str) or not isinstance(v, str) or len(v.encode()) > 80000
            for k, v in result["pages"].items()
        )
    ):
        raise ValueError("one bounded staged Markdown page required")
    candidate = copy.deepcopy(state)
    schema = contracts(root)
    kind = "securities" if operation == "research_security" else "ideas"
    key = "security_id" if kind == "securities" else "idea_id"
    entity = next((r for r in candidate[kind] if r[key] == entity_id), None)
    if entity is None:
        raise ValueError("unknown research entity")
    for value in result["sources"]:
        row = _row(value, schema["source_registry"].columns).copy()
        if row["status"] != "valid":
            raise ResearchResultValidationError("source.status.invalid")
        if not row["title"]:
            raise ResearchResultValidationError("source.title.missing")
        if entity_id not in row["related_entity_ids"].split("|"):
            raise ResearchResultValidationError("source.related_entity_ids.target_missing")
        observed = _fresh_observation(observations, row["url"], now)
        row.update(checked_at=observed["checked_at"], content_hash=observed["content_hash"])
        prior = next(
            (r for r in state["source_registry"] if r["source_id"] == row["source_id"]), None
        )
        if prior and prior["url"] != row["url"]:
            raise ValueError("source identity cannot change URL")
        if prior and prior["license"] != row["license"]:
            raise ValueError("source license cannot change without independent verification")
        duplicate = next(
            (
                r
                for r in candidate["source_registry"]
                if r["url"] == row["url"] and r["source_id"] != row["source_id"]
            ),
            None,
        )
        if duplicate and prior is None:
            raise ValueError("verified source URL already has a stable source identity")
        if row["published_at"]:
            published = _model_timestamp(row["published_at"], "source.published_at")
            if published > now:
                raise ResearchResultValidationError("source.published_at.future")
        if prior:
            row["related_entity_ids"] = "|".join(
                sorted(
                    set(prior["related_entity_ids"].split("|"))
                    | set(row["related_entity_ids"].split("|"))
                )
            )
        _upsert(candidate["source_registry"], row, "source_id")
    for value in result["relationships"]:
        row = _row(value, schema["relationships"].columns)
        if row[key] != entity_id or not row["source_ids"]:
            raise ValueError("relationship outside the current entity or missing evidence")
        prior = next(
            (r for r in state["relationships"] if r["relationship_id"] == row["relationship_id"]),
            None,
        )
        if prior and prior[key] != entity_id:
            raise ValueError("relationship identity belongs to another entity")
        _upsert(candidate["relationships"], row, "relationship_id")
    unchanged = result["outcome"] in {"no_change", "skip_as_stale"}
    if unchanged:
        if (
            result["assessment"] is not None
            or result["idea"] is not None
            or result["pages"]
            or result["sources"]
            or result["relationships"]
        ):
            raise ValueError("unchanged outcome cannot partially write research")
        if kind == "securities":
            # Record the actual review for the existing cooldown, without
            # changing assessment dates, fair values, sources or freshness.
            entity.update(last_research_at=instant(now), updated_at=instant(now))
        elif result["outcome"] == "no_change":
            entity["last_reviewed_on"] = now.date().isoformat()
        return candidate, {}
    page = entity["research_page"] or f"data/wiki/{kind}/{entity_id}.md"
    if set(result["pages"]) != {page}:
        raise ValueError("only the target entity page may be staged")
    markdown = result["pages"][page]
    if not markdown.startswith("---\n") or "\n---\n" not in markdown[4:]:
        raise ValueError("frontmatter required")
    metadata = yaml.safe_load(markdown[4:].split("\n---\n", 1)[0])
    if not isinstance(metadata, dict) or metadata.get(key) != entity_id:
        raise ValueError("frontmatter identity mismatch")
    if operation == "research_security" and metadata.get("issuer_id") != entity["issuer_id"]:
        raise ValueError("frontmatter issuer mismatch")
    if re.search(
        r"<\s*(script|iframe|object)\b|javascript\s*:|\bon[a-z]+\s*=",
        markdown,
        re.I,
    ):
        raise ValueError("unsafe Markdown or retired technical chart")
    if re.search(
        r"papertrader:technical-chart:(?:start|end)|"
        r'"chart_id"\s*:\s*"market-technicals"',
        markdown,
        re.I,
    ):
        raise ValueError("unsafe Markdown or retired technical chart")
    chart_validator = Draft202012Validator(
        json.loads((root / "schemas/research_chart.schema.json").read_text())
    )
    for fence in re.findall(r"```echart\s*\n(.*?)\n```", markdown, re.S):
        chart = json.loads(fence)
        if list(chart_validator.iter_errors(chart)):
            raise ValueError("invalid optional analytical chart")
    if operation == "research_security":
        if result["idea"] is not None:
            raise ValueError("security operation cannot replace an idea")
        assessment = _row(result["assessment"], schema["security_assessments"].columns)
        if assessment["security_id"] != entity_id:
            raise ValueError("assessment identity mismatch")
        assessed = _model_timestamp(assessment["assessed_at"], "assessment.assessed_at")
        expires = _model_timestamp(assessment["valid_until"], "assessment.valid_until")
        if assessed < now - timedelta(hours=1):
            raise ResearchResultValidationError("assessment.assessed_at.stale")
        if assessed > now + timedelta(minutes=5):
            raise ResearchResultValidationError("assessment.assessed_at.future")
        if expires <= assessed:
            raise ResearchResultValidationError("assessment.valid_until.not_after_assessed")
        if expires > assessed + timedelta(days=freshness_days):
            raise ResearchResultValidationError("assessment.valid_until.exceeds_freshness")
        required = (
            "thesis",
            "method_rationale",
            "key_assumptions",
            "downside",
            "catalysts",
            "invalidation_conditions",
            "limitations",
            "source_ids",
        )
        for field in required:
            if not assessment[field]:
                raise ResearchResultValidationError(f"assessment.{field}.missing")
        if (
            result["outcome"] == "not_supportable"
            and assessment["research_status"] != "valuation_unsupported"
        ):
            raise ValueError("unsupported outcome cannot invent a valuation")
        _upsert(candidate["security_assessments"], assessment, "security_id")
        entity.update(
            research_page=page,
            research_status="researched",
            last_research_at=assessment["assessed_at"],
            updated_at=assessment["assessed_at"],
        )
        evidence = assessment["source_ids"]
    else:
        if result["assessment"] is not None:
            raise ValueError("idea operation cannot replace company valuation")
        idea = _row(result["idea"], schema["ideas"].columns)
        if idea["idea_id"] != entity_id or idea["research_page"] != page or not idea["thesis"]:
            raise ValueError("invalid current idea result")
        if idea["last_reviewed_on"] != now.date().isoformat():
            raise ResearchResultValidationError("idea.last_reviewed_on.invalid")
        _upsert(candidate["ideas"], idea, "idea_id")
        evidence = idea["source_ids"]
    sources = {r["source_id"]: r for r in candidate["source_registry"]}
    primary_source_field = (
        "assessment.source_ids" if operation == "research_security" else "idea.source_ids"
    )
    reference_fields: dict[str, set[str]] = {}
    for source_id in filter(None, evidence.split("|")):
        reference_fields.setdefault(source_id, set()).add(primary_source_field)
    for relationship in result["relationships"]:
        for source_id in filter(None, relationship["source_ids"].split("|")):
            reference_fields.setdefault(source_id, set()).add("relationship.source_ids")
    if not reference_fields:
        raise ValueError("current research needs sources")
    for source_id in sorted(reference_fields):
        fields = reference_fields[source_id]
        field = (
            primary_source_field if primary_source_field in fields else "relationship.source_ids"
        )
        source = sources.get(source_id)
        if source is None:
            raise ResearchResultValidationError(f"{field}.missing")
        if source["status"] != "valid":
            raise ResearchResultValidationError(f"{field}.status_invalid")
        if entity_id not in source["related_entity_ids"].split("|"):
            raise ResearchResultValidationError(f"{field}.target_entity_missing")
        if source["url"] not in markdown:
            raise ResearchResultValidationError(f"{field}.url_missing_from_page")
        try:
            observed = _fresh_observation(observations, source["url"], now)
        except ValueError:
            raise ResearchResultValidationError(f"{field}.not_currently_opened") from None
        source.update(checked_at=observed["checked_at"], content_hash=observed["content_hash"])
        trusted_prior = next(
            (row for row in state["source_registry"] if row["source_id"] == source_id), None
        )
        _reject_copied_source_text(markdown, source, observed, trusted_prior=trusted_prior)
    pages = {page: markdown.encode()}
    # Validate final frontmatter and Markdown before matching current rows are written.
    all_pages = {
        p.relative_to(root).as_posix(): p.read_bytes()
        for directory in ("securities", "ideas")
        for p in (root / "data/wiki" / directory).glob("*.md")
    }
    all_pages.update(pages)
    errors = validate_state(root, candidate, pages=all_pages)
    if errors:
        raise ResearchResultValidationError(_state_validation_code(errors))
    return candidate, pages


def commit_result(root: Path, state: ResearchState, pages: dict[str, bytes]) -> list[str]:
    files = {
        **pages,
        **{
            contract.path: csv_bytes(contract, state[name])
            for name, contract in contracts(root).items()
        },
    }
    return apply_files(root, files)


def context_packet(
    root: Path, state: ResearchState, *, operation: str, entity_id: str
) -> dict[str, Any]:
    kind, key = (
        ("securities", "security_id") if operation == "research_security" else ("ideas", "idea_id")
    )
    entity = next(row for row in state[kind] if row[key] == entity_id)
    links = [row for row in state["relationships"] if row[key] == entity_id][:20]
    assessment = next(
        (row for row in state["security_assessments"] if row["security_id"] == entity_id), None
    )
    refs = set((assessment or entity).get("source_ids", "").split("|"))
    sources = sorted(
        (
            row
            for row in state["source_registry"]
            if row["source_id"] in refs or entity_id in row["related_entity_ids"].split("|")
        ),
        key=lambda row: (
            timestamp(row["checked_at"]).timestamp() if row["checked_at"] else 0,
            row["source_id"],
        ),
        reverse=True,
    )[:12]
    page = entity["research_page"]
    content = (root / page).read_text()[:40000] if page else ""
    packet: dict[str, Any] = dict(
        operation=operation,
        identity=entity,
        target_page=page or f"data/wiki/{kind}/{entity_id}.md",
        assessment=assessment,
        relationships=links,
        sources=sources,
        current_markdown=content,
    )
    if kind == "securities":
        fields = (
            *VALUATION_RESEARCH_FIELDS,
            *(
                f"{case}_{field}"
                for case in ("bear", "base", "bull")
                for field in ("fair_value", "probability_pct")
            ),
        )
        packet["valuation_coverage"] = dict(
            status=valuation_coverage(assessment),
            missing_fields=[field for field in fields if not (assessment or {}).get(field)],
        )
    packet["related_entities"] = [
        row
        for row in state["ideas" if kind == "securities" else "securities"]
        if row["idea_id" if kind == "securities" else "security_id"]
        in {link["idea_id" if kind == "securities" else "security_id"] for link in links}
    ][:20]
    latest = root / "data/market/latest.csv"
    if latest.exists() and kind == "securities":
        import csv

        with latest.open(newline="") as stream:
            packet["market"] = next(
                (r for r in csv.DictReader(stream) if r["security_id"] == entity_id), None
            )
    if len(json.dumps(packet).encode()) > 120000:
        raise ValueError("research context exceeds bounded packet")
    return packet

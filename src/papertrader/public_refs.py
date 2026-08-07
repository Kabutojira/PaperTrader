"""Human-readable, linked references for generated public Markdown."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import yaml

from papertrader.tables import read_table
from papertrader.utils import CanonicalValueError, parse_timestamp

PUBLIC_DAILY_RUN_ID = re.compile(
    r"(?<![A-Za-z0-9_-])(?:[A-Za-z0-9]+-)*daily-[0-9]{8}T[0-9]{6}Z"
    r"(?![A-Za-z0-9_-])"
)


@dataclass(frozen=True, slots=True)
class HumanReference:
    """One public label and its canonical destination."""

    label: str
    target: str

    def markdown(self) -> str:
        label = self.label.replace("|", "\\|")
        if self.target.startswith(("https://", "http://")):
            return f"[{label}]({self.target})"
        target = self.target.removeprefix("data/wiki/")
        page, separator, anchor = target.partition("#")
        target = page.removesuffix(".md") + (f"#{anchor}" if separator else "")
        return f"[[{target}|{label}]]"


def _frontmatter_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
        raw, _ = text[4:].split("\n---\n", maxsplit=1)
        metadata = yaml.safe_load(raw)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        raise CanonicalValueError(f"cannot resolve public page title: {path}") from exc
    title = metadata.get("title") if isinstance(metadata, dict) else None
    if not isinstance(title, str) or not title.strip():
        raise CanonicalValueError(f"public page has no human title: {path}")
    return " ".join(title.split())


class PublicEntityResolver:
    """Resolve canonical identities without exposing them in visible Markdown."""

    def __init__(self, repository_root: Path) -> None:
        self.root = repository_root
        contracts = {
            "securities": ("securities", "security_id"),
            "relationships": ("relationships", "relationship_id"),
            "strategies": ("strategies", "strategy_id"),
            "sources": ("source_registry", "source_id"),
            "orders": ("orders", "order_id"),
            "issues": ("issues", "issue_id"),
        }
        self.tables = {
            name: {row[key]: row for row in read_table(repository_root, contract)}
            for name, (contract, key) in contracts.items()
        }
        self.executions = {
            row["execution_id"]: row for row in read_table(repository_root, "executions")
        }
        self.operations = {
            row["operation_id"]: row
            for table in ("operations_history", "operations_todo")
            for row in read_table(repository_root, table)
        }
        self.runs = {row["run_id"]: row for row in read_table(repository_root, "runs")}
        self.signals = {row["signal_id"]: row for row in read_table(repository_root, "signals")}
        self.positions = {
            row["position_id"]: row for row in read_table(repository_root, "portfolio")
        }

    def _page(self, raw: str, *, fallback: str = "") -> str:
        value = raw or fallback
        path = PurePosixPath(value.partition("#")[0])
        if (
            not value
            or path.is_absolute()
            or ".." in path.parts
            or path.parts[:2] != ("data", "wiki")
            or path.suffix != ".md"
        ):
            raise CanonicalValueError("public entity lacks a canonical wiki target")
        return value

    def _opportunity(self, entity_id: str) -> HumanReference:
        row = next(
            (
                candidate
                for candidate in self.operations.values()
                if candidate["entity_id"] == entity_id
            ),
            None,
        )
        if row is None:
            raise CanonicalValueError("cannot resolve required public opportunity reference")
        payload = self.root / row["payload_path"]
        try:
            value = json.loads(payload.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CanonicalValueError("cannot read required public opportunity reference") from exc
        inputs = value.get("inputs") if isinstance(value, dict) else None
        security_id = inputs.get("security_id") if isinstance(inputs, dict) else None
        if not isinstance(security_id, str):
            raise CanonicalValueError("public opportunity lacks a security reference")
        security = self._security(security_id)
        return HumanReference(f"Market alert for {security.label}", security.target)

    def resolve(self, entity_type: str, entity_id: str) -> HumanReference:
        method = getattr(self, f"_{entity_type}", None)
        if method is None:
            raise CanonicalValueError(f"unsupported public entity type: {entity_type}")
        result = method(entity_id)
        if not isinstance(result, HumanReference):
            raise CanonicalValueError("public entity resolver returned an invalid reference")
        return result

    def markdown(self, entity_type: str, entity_id: str) -> str:
        return self.resolve(entity_type, entity_id).markdown()

    def _security(self, entity_id: str) -> HumanReference:
        row = self.tables["securities"].get(entity_id)
        if row is None or not row["ticker"]:
            raise CanonicalValueError("cannot resolve required public security reference")
        target = row["research_page"] or f"data/wiki/security-catalog.md#security-{entity_id}"
        return HumanReference(row["ticker"], self._page(target))

    def _idea(self, entity_id: str) -> HumanReference:
        target = f"data/wiki/ideas/{entity_id}.md"
        path = self.root / target
        return HumanReference(_frontmatter_title(path), self._page(target))

    def _relationship(self, entity_id: str) -> HumanReference:
        row = self.tables["relationships"].get(entity_id)
        if row is None:
            raise CanonicalValueError("cannot resolve required public relationship reference")
        target = self._page(row["research_page"])
        return HumanReference(_frontmatter_title(self.root / target), target)

    def _strategy(self, entity_id: str) -> HumanReference:
        row = self.tables["strategies"].get(entity_id)
        if row is None or not row["name"]:
            raise CanonicalValueError("cannot resolve required public strategy reference")
        fallback = self._security(row["security_id"]).target
        return HumanReference(row["name"], self._page(row["research_page"], fallback=fallback))

    def _source(self, entity_id: str) -> HumanReference:
        row = self.tables["sources"].get(entity_id)
        if row is not None:
            target = row["canonical_url"] or row["url"]
            label = row["title"] or row["publisher"] or urlparse(target).hostname or "Source"
        else:
            operation = next(
                (
                    candidate
                    for candidate in self.operations.values()
                    if candidate["entity_type"] == "source" and candidate["entity_id"] == entity_id
                ),
                None,
            )
            if operation is None:
                raise CanonicalValueError("cannot resolve required public source reference")
            try:
                payload = json.loads((self.root / operation["payload_path"]).read_text())
            except (OSError, json.JSONDecodeError) as exc:
                raise CanonicalValueError("cannot read required public source reference") from exc
            inputs = payload.get("inputs") if isinstance(payload, dict) else None
            if not isinstance(inputs, dict):
                raise CanonicalValueError("public source operation lacks source context")
            source_path = inputs.get("source_path")
            if isinstance(source_path, str) and source_path.endswith(".md"):
                target = self._page(source_path)
                label = _frontmatter_title(self.root / target)
                return HumanReference(label, target)
            target = next(
                (
                    value
                    for key in (
                        "canonical_url",
                        "source_url",
                        "url",
                        "video_url",
                        "analysis_page_url",
                        "news_page_url",
                    )
                    if isinstance((value := inputs.get(key)), str)
                    and value.startswith(("https://", "http://"))
                ),
                "",
            )
            label = str(inputs.get("title") or urlparse(target).hostname or "Source")
        if not target.startswith(("https://", "http://")):
            raise CanonicalValueError("public source lacks a canonical URL")
        return HumanReference(label, target)

    def _signal(self, entity_id: str) -> HumanReference:
        row = self.signals.get(entity_id)
        if row is None:
            raise CanonicalValueError("cannot resolve required public signal reference")
        strategy = self._strategy(row["strategy_id"])
        timestamp = parse_timestamp(row["created_at"])
        day = timestamp.date().isoformat() if timestamp else "unknown date"
        return HumanReference(f"Paper signal for {strategy.label} on {day}", strategy.target)

    def _position(self, entity_id: str) -> HumanReference:
        row = self.positions.get(entity_id)
        if row is None:
            raise CanonicalValueError("cannot resolve required public position reference")
        security = self._security(row["security_id"])
        return HumanReference(f"Paper position in {security.label}", security.target)

    def _operation(self, entity_id: str) -> HumanReference:
        row = self.operations.get(entity_id)
        if row is None:
            raise CanonicalValueError("cannot resolve required public operation reference")
        try:
            entity = self.resolve(row["entity_type"], row["entity_id"])
        except CanonicalValueError:
            if row["entity_type"] != "relationship":
                raise
            try:
                payload = json.loads((self.root / row["payload_path"]).read_text())
            except (OSError, json.JSONDecodeError) as exc:
                raise CanonicalValueError(
                    "cannot resolve pending public relationship reference"
                ) from exc
            inputs = payload.get("inputs") if isinstance(payload, dict) else None
            idea_id = inputs.get("idea_id") if isinstance(inputs, dict) else None
            security_id = inputs.get("security_id") if isinstance(inputs, dict) else None
            if not isinstance(idea_id, str) or not isinstance(security_id, str):
                raise CanonicalValueError(
                    "pending relationship lacks human-readable entity context"
                ) from None
            idea = self._idea(idea_id)
            security = self._security(security_id)
            entity = HumanReference(
                f"relationship between {idea.label} and {security.label}", idea.target
            )
        timestamp = parse_timestamp(row.get("completed_at") or row["created_at"])
        label = f"{row['operation_type'].replace('_', ' ').capitalize()} for {entity.label}"
        if timestamp is not None:
            label += f" on {timestamp.date().isoformat()}"
        return HumanReference(label, entity.target)

    def _order(self, entity_id: str) -> HumanReference:
        row = self.tables["orders"].get(entity_id)
        if row is None:
            raise CanonicalValueError("cannot resolve required public order reference")
        strategy = self._strategy(row["strategy_id"])
        timestamp = parse_timestamp(row["created_at"])
        day = timestamp.date().isoformat() if timestamp else "unknown date"
        return HumanReference(f"Order for {strategy.label} on {day}", strategy.target)

    def _execution(self, entity_id: str) -> HumanReference:
        row = self.executions.get(entity_id)
        if row is None:
            raise CanonicalValueError("cannot resolve required public execution reference")
        security = self._security(row["security_id"])
        timestamp = parse_timestamp(row["executed_at"])
        day = timestamp.date().isoformat() if timestamp else "unknown date"
        return HumanReference(f"Fill for {security.label} on {day}", security.target)

    def _run(self, entity_id: str) -> HumanReference:
        manifest_path = self.root / "data" / "runs" / entity_id / "daily_run.json"
        if manifest_path.is_file():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise CanonicalValueError("cannot read required public run reference") from exc
            report = manifest.get("report_path")
            stamp = manifest.get("completed_at") or manifest.get("research_cutoff_at")
            parsed = parse_timestamp(stamp) if isinstance(stamp, str) else None
            if isinstance(report, str) and report and parsed is not None:
                label = f"Daily report for {parsed.date().isoformat()}"
                return HumanReference(label, self._page(report))
        row = self.runs.get(entity_id)
        parsed = parse_timestamp(row["completed_at"]) if row is not None else None
        if parsed is None:
            raise CanonicalValueError("cannot resolve required public run reference")
        target = f"data/wiki/daily-reports/daily-report_{parsed.strftime('%Y%m%d')}.md"
        return HumanReference(f"Daily report for {parsed.date().isoformat()}", self._page(target))

    def _issue(self, entity_id: str) -> HumanReference:
        row = self.tables["issues"].get(entity_id)
        if row is None or not row["title"]:
            raise CanonicalValueError("cannot resolve required public issue reference")
        return HumanReference(self.human_label(row["title"]), "data/wiki/system-status.md")

    def human_label(self, text: str) -> str:
        """Humanize embedded identities for contexts that cannot contain nested links."""

        linked = self.humanize(text)
        return re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", linked)

    def humanize(self, text: str) -> str:
        """Replace embedded canonical identities with linked public context."""

        text = text.replace("\\_", "_")
        token = re.compile(
            r"\b(?:security|relationship|strategy|opportunity|signal|position|operation|order|"
            r"execution|issue)_[0-9a-f]{20}\b|"
            r"\bidea_(?!research\b)[a-z0-9][a-z0-9_]{5,}\b|"
            r"\bsource_(?!discovery\b)[A-Za-z0-9][A-Za-z0-9_-]{5,}\b|"
            rf"{PUBLIC_DAILY_RUN_ID.pattern}|"
            r"\b(?=[0-9A-HJKMNP-TV-Z]{0,25}[A-HJKMNP-TV-Z])[0-9A-HJKMNP-TV-Z]{26}\b|"
            r"\b(?:allocation_plan|snapshot|decision)_[A-Za-z0-9_-]{6,}\b|"
            r"\b[0-9a-f]{40,64}\b"
        )

        def replace(match: re.Match[str]) -> str:
            value = match.group(0)
            if value in {
                "security_research",
                "idea_research",
                "relationship_research",
                "strategy_research",
                "opportunity_research",
                "source_discovery",
            }:
                return value.replace("_", " ")
            if re.fullmatch(r"[0-9a-f]{40,64}", value):
                return "recorded source state"
            if value.startswith("allocation_plan_"):
                return "current allocation plan"
            if value.startswith(("snapshot_", "decision_")):
                return "decision snapshot"
            if PUBLIC_DAILY_RUN_ID.fullmatch(value):
                return self.markdown("run", value)
            if re.fullmatch(
                r"(?=[0-9A-HJKMNP-TV-Z]{0,25}[A-HJKMNP-TV-Z])[0-9A-HJKMNP-TV-Z]{26}",
                value,
            ):
                return self.markdown("operation", value)
            prefix = value.split("_", maxsplit=1)[0]
            try:
                return self.markdown(prefix, value)
            except CanonicalValueError:
                if prefix == "source":
                    return "recorded source"
                raise

        return token.sub(replace, text)


def report_date_reference(day: date, target: str) -> HumanReference:
    """Create a run/report reference when the immutable cycle ID is intentionally hidden."""

    return HumanReference(f"Daily report for {day.isoformat()}", target)

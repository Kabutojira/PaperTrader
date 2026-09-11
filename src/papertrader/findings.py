"""Point-in-time finding inventory and honest saved-report coverage receipts."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from html import escape
from pathlib import Path
from typing import Any

from papertrader.atomic_io import atomic_write_json, atomic_write_text
from papertrader.evidence import claim_diagnostics
from papertrader.governance import ROOT, load_record, security_change_class
from papertrader.tables import read_table
from papertrader.utils import content_hash, format_timestamp, parse_timestamp

RESEARCH_TYPES = {
    "opportunity_research",
    "quick_check_research",
    "idea_research",
    "security_research",
    "relationship_research",
    "strategy_research",
    "research_triage",
    "final_buy_review",
}


def finding_inventory(root: Path, *, as_of: datetime) -> list[dict[str, Any]]:
    findings = []
    for operation in read_table(root, "operations_history"):
        completed = parse_timestamp(operation["completed_at"])
        if (
            operation["operation_type"] not in RESEARCH_TYPES
            or operation["terminal_status"] != "succeeded"
            or completed is None
            or completed > as_of
            or not operation["result_path"]
        ):
            continue
        result = load_record(root, root / operation["result_path"])
        narratives = result.get("daily_report_items") or [result["summary"]]
        for index, text in enumerate(narratives):
            identity = {
                "operation_id": operation["operation_id"],
                "result_hash": content_hash(result),
                "index": index,
                "text": text,
            }
            findings.append(
                {
                    "finding_id": "finding_" + content_hash(identity)[:24],
                    **identity,
                    "completed_at": operation["completed_at"],
                    "entity_type": operation["entity_type"],
                    "entity_id": operation["entity_id"],
                    "result_path": operation["result_path"],
                    "change_class": security_change_class(
                        root, operation["entity_id"], operation["operation_id"]
                    )
                    if operation["operation_type"] == "security_research"
                    else operation["operation_type"],
                    "challenge_status": result.get("adversarial_review", {}).get(
                        "status", "not_recorded"
                    ),
                    "review_decision": result.get("final_buy_review", {}).get("decision", ""),
                }
            )
    return sorted(findings, key=lambda row: (row["completed_at"], row["finding_id"]))


def pending_findings(root: Path, *, report_date: date, as_of: datetime) -> list[dict[str, Any]]:
    represented = set()
    for path in (root / "data/runs").glob("*/finding_coverage.json"):
        receipt = load_record(root, path)
        if receipt["report_date"] < report_date.isoformat():
            represented.update(receipt["finding_ids"])
    # Same-date reports can be replaced by a later completed cycle. Include their findings
    # again so that replacing the canonical report never hides previously represented work.
    return [
        row for row in finding_inventory(root, as_of=as_of) if row["finding_id"] not in represented
    ]


def prepare_finding_appendix(
    root: Path, *, run_id: str, report_date: date, as_of: datetime, maximum_findings: int = 100
) -> tuple[list[str], list[str], str]:
    pending = pending_findings(root, report_date=report_date, as_of=as_of)
    selected = pending[:maximum_findings]
    if not selected:
        return [], [], ""
    public_identity = content_hash({"artifact": "research_finding_appendix", "run_id": run_id})[:24]
    page_key = f"queries/research-findings-{public_identity}"
    destination = root / "data/wiki" / f"{page_key}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"title: Research findings {public_identity}",
        "type: query",
        "status: maintained",
        "tags:",
        "  - query",
        "  - research",
        f'created: "{report_date.isoformat()}"',
        f'updated: "{report_date.isoformat()}"',
        "provenance: deterministic-research-finding-coverage",
        "---",
        "",
        "# Research findings represented in this report",
        "",
        f"Point-in-time cutoff: {format_timestamp(as_of)}. Saved is not proof of "
        "publication, delivery, or user observation.",
        "",
    ]
    for finding in selected:
        lines.extend(
            [
                f"## {finding['finding_id']}",
                "",
                escape(str(finding["text"])),
                "",
                f"- Change class: {finding['change_class']}",
                f"- Challenge coverage: {finding['challenge_status']}",
                f"- Source result: `{finding['result_path']}`",
                f"- Result hash: `{finding['result_hash']}`",
                "",
            ]
        )
    atomic_write_text(destination, "\n".join(lines), allowed_root=root)
    from papertrader.wiki import register_wiki_page

    register_wiki_page(
        root / "data/wiki",
        page_key=page_key,
        label=f"Research findings {public_identity}",
        section="Queries",
        event=f"Saved bounded research finding coverage in [[{page_key}]].",
        event_date=report_date,
    )
    section = [
        "",
        "### Research finding coverage",
        "",
        f"[[{page_key}|{len(selected)} completed findings, including "
        "prior-cycle/manual work]] are represented in the linked appendix.",
        f"{len(pending) - len(selected)} additional findings remain unrepresented "
        "and eligible for a later report.",
        "",
    ]
    return (
        section,
        [row["finding_id"] for row in selected],
        destination.relative_to(root).as_posix(),
    )


def record_finding_coverage(
    root: Path,
    *,
    run_id: str,
    report_date: date,
    report_path: Path,
    finding_ids: list[str],
    appendix_path: str,
) -> None:
    if not finding_ids:
        return
    appendix = root / appendix_path
    text = appendix.read_text(encoding="utf-8")
    if not all(f"## {key}\n" in text for key in finding_ids):
        raise ValueError("cannot mark an omitted finding as represented")
    key = appendix.relative_to(root / "data/wiki").with_suffix("").as_posix()
    if f"[[{key}|" not in report_path.read_text(encoding="utf-8"):
        raise ValueError("finding appendix is not linked by the saved report")
    receipt = {
        "schema_version": 1,
        "run_id": run_id,
        "report_date": report_date.isoformat(),
        "finding_ids": finding_ids,
        "appendix_path": appendix_path,
        "appendix_hash": content_hash(appendix.read_bytes()),
        "report_path": report_path.relative_to(root).as_posix(),
        "saved": True,
        "publication": "not_attested_here",
        "delivery": "not_attested_here",
        "user_observed": False,
    }
    path = root / "data/runs" / run_id / "finding_coverage.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and load_record(root, path) != receipt:
        raise ValueError("immutable finding coverage differs on replay")
    atomic_write_json(path, receipt, allowed_root=root)


def research_metrics(root: Path, *, as_of: datetime) -> dict[str, Any]:
    active = [
        row
        for row in read_table(root, "operations_todo")
        if (parse_timestamp(row["created_at"]) or as_of) <= as_of
    ]
    history = [
        row
        for row in read_table(root, "operations_history")
        if (parse_timestamp(row["completed_at"]) or as_of) <= as_of
    ]
    latency = []
    for row in history:
        completed = parse_timestamp(row["completed_at"])
        created = parse_timestamp(row["created_at"])
        if completed is not None and created is not None:
            latency.append((completed - created).total_seconds())
    findings = finding_inventory(root, as_of=as_of)
    reviews = Counter(row["review_decision"] for row in findings if row["review_decision"])
    coverage = [load_record(root, path) for path in (root / ROOT / "monitoring").glob("*.json")]
    coverage = [row for row in coverage if (parse_timestamp(row["accepted_at"]) or as_of) <= as_of]
    invocations = []
    for path in (root / "data/runs").glob("*/*/hermes_run.json"):
        value = load_record(root, path)
        completed = parse_timestamp(value.get("completed_at", ""))
        if completed is not None and completed <= as_of:
            invocations.append(value)
    from papertrader.buy_review import PACKETS, REVIEWS

    accepted = [load_record(root, path) for path in (root / REVIEWS).glob("*.json")]
    accepted = [row for row in accepted if (parse_timestamp(row["accepted_at"]) or as_of) <= as_of]
    decision_counts = Counter(row["decision"] for row in accepted)
    intent_counts = Counter(row["order_id"] for row in accepted)
    submission_latencies = []
    for review in accepted:
        order = next(
            (row for row in read_table(root, "orders") if row["order_id"] == review["order_id"]),
            None,
        )
        if order and (parse_timestamp(order["created_at"]) or as_of) <= as_of:
            packet = load_record(root, root / PACKETS / f"{review['review_request_id']}.json")
            created = parse_timestamp(packet["created_at"])
            submitted = parse_timestamp(order["created_at"])
            if created is not None and submitted is not None:
                submission_latencies.append(max(0, (submitted - created).total_seconds()))
    rsi_results = []
    for row in history:
        path = root / row["payload_path"]
        if path.is_file() and load_record(root, path).get("inputs", {}).get("rsi_attention"):
            created, completed = (
                parse_timestamp(row["created_at"]),
                parse_timestamp(row["completed_at"]),
            )
            rsi_results.append(
                {
                    "operation_id": row["operation_id"],
                    "status": row["terminal_status"],
                    "latency_seconds": (completed - created).total_seconds()
                    if completed and created
                    else None,
                }
            )
    forecasts = [load_record(root, path) for path in (root / ROOT / "forecasts").glob("*.json")]
    forecasts = [
        row for row in forecasts if (parse_timestamp(row["registered_at"]) or as_of) <= as_of
    ]
    outcomes = [
        load_record(root, path) for path in (root / ROOT / "forecast-outcomes").glob("*.json")
    ]
    outcomes = [row for row in outcomes if (parse_timestamp(row["resolved_at"]) or as_of) <= as_of]
    useful = {
        row["operation_id"]
        for row in findings
        if row["change_class"] not in {"price_only", "no_material_change", "unknown"}
    }
    expensive = [row for row in invocations if row.get("profile") != "scout"]
    return {
        "schema_version": 1,
        "as_of": format_timestamp(as_of),
        "active_status_counts": dict(Counter(row["status"] for row in active)),
        "terminal_status_counts": dict(Counter(row["terminal_status"] for row in history)),
        "mean_completion_latency_seconds": sum(latency) / len(latency) if latency else None,
        "finding_change_classes": dict(Counter(row["change_class"] for row in findings)),
        "final_review_decisions": dict(reviews),
        "authenticated_final_decisions": dict(decision_counts),
        "final_review_reasons": dict(Counter(row["reason"] for row in accepted)),
        "repeat_review_count": sum(max(0, count - 1) for count in intent_counts.values()),
        "eligibility_to_submission_seconds": submission_latencies,
        "observed_model_calls": len(invocations),
        "expensive_calls_per_material_conclusion": len(expensive) / len(useful) if useful else None,
        "model_cost_coverage": (
            "Retained invocation receipts only; pruned historical calls and token "
            "billing are not inferred."
        ),
        "challenge_coverage": dict(Counter(row["challenge_status"] for row in findings)),
        "rsi_investigations": rsi_results,
        "forecast_candidate_dispositions": dict(
            Counter(row["forecast"]["candidate_disposition"] for row in forecasts)
        ),
        "forecast_outcomes": outcomes,
        "evaluation_limitations": [
            "Coverage and completion are not investment correctness or causal challenge "
            "effectiveness.",
            "Current queue statuses are not reconstructed historical statuses; future "
            "admissions are excluded.",
            "RSI outcomes retain original investigation IDs for later point-in-time "
            "economic evaluation.",
        ],
        "monitoring_checked_targets": sum(row["checked_count"] for row in coverage),
        "monitoring_scheduled_targets": sum(row["target_count"] for row in coverage),
        "performance_claim": (
            "Research correctness is not inferred from profitable fills or intrinsic fair values."
        ),
        "evidence": claim_diagnostics(root, as_of=as_of),
    }

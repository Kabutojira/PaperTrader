"""Controller-owned application of read-only research check outcomes."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

from papertrader.config import Settings
from papertrader.profiles import routing_context
from papertrader.queue import Operation, enqueue_operation


def apply_triage_result(
    repository_root: Path,
    settings: Settings,
    operation: Operation,
    result: Mapping[str, object],
    *,
    result_path: str,
    now: datetime | None = None,
) -> str | None:
    """Escalate material/uncertain checks once, preserving the investigation and cause.

    This is invoked by the trusted parent only after full result validation. A current
    exposure obligation cannot be discarded by a cheap model's no-change conclusion.
    """

    if operation.operation_type != "research_triage":
        raise ValueError("triage acceptance requires a research_triage operation")
    review = result.get("triage_review")
    if not isinstance(review, dict):
        raise ValueError("triage acceptance requires a structured review")
    from papertrader.monitoring import accept_monitoring
    from papertrader.utils import utc_now

    completed_monitor = accept_monitoring(repository_root, operation, result, now=now or utc_now())
    if review.get("disposition") in {"no_material_change", "duplicate"} and (
        completed_monitor or not routing_context(repository_root, operation).portfolio_sensitive
    ):
        return None
    payload = json.loads((repository_root / operation.payload_path).read_text(encoding="utf-8"))
    inputs = payload["inputs"]
    operation_id, _ = enqueue_operation(
        repository_root,
        settings,
        operation_type="security_research",
        entity_type="security",
        entity_id=operation.entity_id,
        dedupe_key=f"security_research:triage:{operation.entity_id}:{inputs['investigation_id']}",
        prompt=f"Investigate the unresolved cause from triage {operation.operation_id}.",
        inputs={
            "security_id": operation.entity_id,
            "investigation_id": inputs["investigation_id"],
            "original_cause": inputs["cause"],
            "original_created_at": operation.to_row()["created_at"],
            "triage_operation_id": operation.operation_id,
            "triage_result_path": result_path,
            "triage_reason": review["reason"],
            "evidence_refs": inputs["evidence_refs"],
        },
        source="controller:research_triage",
        priority=operation.priority,
        freshness_days=0,
        depends_on=(operation.operation_id,),
        source_refs=(*inputs["evidence_refs"], result_path),
        now=now,
    )
    return operation_id

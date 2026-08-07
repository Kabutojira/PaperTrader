from __future__ import annotations

import json
from pathlib import Path

from papertrader import daily


def _write_result(path: Path, item: str) -> None:
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "evidence": [{"source": f"evidence for {item}"}],
                "daily_report_items": [item],
            }
        ),
        encoding="utf-8",
    )


def test_research_narratives_exclude_unaccepted_agent_artifacts(
    sandbox_repository: Path,
    monkeypatch,
) -> None:
    run_id = "local-daily-20260807T161139Z"
    accepted_id = "01KZEHGE70QV9HKC2T38858SKT"
    orphan_id = "01KZ9ZJVER177B5ASW4ZMQHEG3"
    accepted_path = (
        sandbox_repository / "data" / "runs" / run_id / accepted_id / "agent_result.json"
    )
    orphan_path = sandbox_repository / "data" / "runs" / run_id / orphan_id / "agent_result.json"
    _write_result(accepted_path, "Accepted failed-closed result.")
    _write_result(orphan_path, "Rejected attempt must not be published.")

    monkeypatch.setattr(
        daily,
        "read_table",
        lambda _root, name: (
            [
                {
                    "claimed_by_run_id": run_id,
                    "operation_id": accepted_id,
                    "result_path": accepted_path.relative_to(sandbox_repository).as_posix(),
                },
                {
                    "claimed_by_run_id": run_id,
                    "operation_id": orphan_id,
                    "result_path": "",
                },
            ]
            if name == "operations_history"
            else []
        ),
    )

    narratives = daily._research_narratives(sandbox_repository, run_id)

    assert [item.text for item in narratives] == ["Accepted failed-closed result."]

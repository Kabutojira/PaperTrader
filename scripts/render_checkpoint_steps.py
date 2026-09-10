#!/usr/bin/env python3
"""Render the sequential checkpoint steps of ``reusable-llm.yml`` from one template.

GitHub Actions cannot loop over composite actions, so the runtime workflow unrolls the
"run one operation without credentials, then push its validated checkpoint" step once per
allowed operation.  Keeping twenty hand-copied blocks in sync is the maintenance hazard this
script removes: the region between the BEGIN/END markers is generated from ``STEP_TEMPLATE`` and
``tests/unit/test_workflow_contracts.py`` fails when the committed file drifts from the render.

Usage:
    python scripts/render_checkpoint_steps.py          # rewrite the region in place
    python scripts/render_checkpoint_steps.py --check  # exit 1 when the file would change
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "reusable-llm.yml"
BEGIN = (
    "      # BEGIN generated checkpoint steps "
    "(scripts/render_checkpoint_steps.py; do not edit by hand)\n"
)
END = "      # END generated checkpoint steps\n"
MAXIMUM_OPERATIONS = 20
STEP_TEMPLATE = """      - name: Routed research checkpoint {index:02d}
        id: operation_{index:02d}
        if: ${{{{ {condition} }}}}
        uses: ./.github/actions/checkpoint-operation
        with:
          daily_cycle_id: ${{{{ steps.cycle.outputs.cycle_id }}}}
          hermes_home: ${{{{ env.HERMES_HOME }}}}
          operation_id: ${{{{ inputs.operation_id }}}}
          operation_type: ${{{{ inputs.operation_type }}}}
          target_branch: ${{{{ inputs.target_branch || github.event.repository.default_branch }}}}
          dry_run: ${{{{ inputs.dry_run }}}}
          github_token: ${{{{ !inputs.dry_run && github.token || '' }}}}
          openai_oauth_secret: ${{{{ secrets.OPENAI_OAUTH_SECRET }}}}
"""


def render_steps(maximum_operations: int = MAXIMUM_OPERATIONS) -> str:
    """Return the generated step block for ``maximum_operations`` sequential checkpoints."""

    blocks: list[str] = []
    for index in range(1, maximum_operations + 1):
        condition = (
            "steps.cycle.outputs.needs_finalization == 'true' "
            f"&& fromJSON(inputs.max_operations) >= {index}"
        )
        if index > 1:
            condition += f" && steps.operation_{index - 1:02d}.outputs.continue == 'true'"
        blocks.append(STEP_TEMPLATE.format(index=index, condition=condition))
    return "".join(blocks)


def render_workflow(text: str, maximum_operations: int = MAXIMUM_OPERATIONS) -> str:
    """Return ``text`` with the marked region replaced by a fresh render."""

    start = text.index(BEGIN) + len(BEGIN)
    stop = text.index(END)
    return text[:start] + render_steps(maximum_operations) + text[stop:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail when the file would change")
    parser.add_argument("--workflow", type=Path, default=WORKFLOW)
    arguments = parser.parse_args(argv)
    current = arguments.workflow.read_text(encoding="utf-8")
    rendered = render_workflow(current)
    if rendered == current:
        return 0
    if arguments.check:
        print(f"{arguments.workflow} differs from scripts/render_checkpoint_steps.py output")
        return 1
    arguments.workflow.write_text(rendered, encoding="utf-8")
    print(f"rewrote {arguments.workflow}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

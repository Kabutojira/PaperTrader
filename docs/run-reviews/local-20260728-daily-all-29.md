# Hermes run review

## Run summary

This review covers completed local Hermes daily run `local-20260728-daily-all-29`, the newest
completed `local-*` daily run that contains a Hermes execution artifact. The requested
`MAX_OPERATIONS=10` was treated as the review ceiling; this historical run's immutable
`agent_batch.json` records `maximum_operations: 1`, and the run contains one operation.

The run started at `2026-07-28T08:38:20Z`, completed at `2026-07-28T08:45:56Z`, and finished
`succeeded`. Its source revision was `5d4e05f42c569d7450596b2ca964a84364beee44`. The final
snapshot was `decision_55f99cf865416f0c19b8`.

| Operation type | succeeded | skipped | failed | blocked | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| `execute_strategy` | 1 | 0 | 0 | 0 | 1 |
| **Total** | **1** | **0** | **0** | **0** | **1** |

Operation `01KYKX54MRDBWHGFKQERB0YG2Q` reviewed strategy
`strategy_bd005fc3733b1475b6f9` for immutable security
`security_1f9cce545ede94cd6349` (Intuitive Surgical, `ISRG`). It created pending paper order
`order_745a7a020ecf89d5734d` with one deterministic seven-share long-equity leg and no fill or
accounting transition.

The operation-level behavior was otherwise sound:

- `hermes_preflight.json` selected `papertrader-execute-strategy` and `llm-wiki`; the exact
  historical operation skill and controller skill were recovered from commit
  `6e713bfe0d5b939fdc579afb13da90bef5cd3163`, and their hashes match the preflight artifact.
- The payload bound the decision to immutable security, strategy, signal, assessment, and
  allocation-plan identities. It used fresh canonical market and FX timestamps and did not rely
  on ticker text as identity.
- Hermes used the audited `papertrader order create-baseline` command, followed by strict
  portfolio reconciliation. The command audit and result agree that only `orders.csv`,
  `order_legs.csv`, and `signals.csv` changed.
- No wiki page, ledger, portfolio, performance row, allocation row, or follow-up operation was
  changed. `agent_result.json` accurately reports the command, evidence, files, and pending status.
- `validation_report.json` correctly verified the operation-local exact delta. The terminal
  `succeeded` status is correct for the operation boundary, although Finding H-01 shows that the
  later daily finalization missed a cross-phase semantic conflict.
- No related unresolved issue was present in `data/tables/issues.csv` or `data/issues.md`.
  `data/wiki/log.md` records the preceding strategy handoff, the risk-ceiling repair, and the
  completed daily report without claiming a fill.

All artifacts below `data/runs/local-20260728-daily-all-29/`, the terminal history row, and all
append-only histories were treated as immutable and were not changed.

## Findings

### H-01 — A pending baseline order superseded its own allocation-plan identity and was still published as copy-ready

- **Severity:** high
- **Operation ID and type:** `01KYKX54MRDBWHGFKQERB0YG2Q`, `execute_strategy`
- **Observed behavior:** The operation correctly created incremental order
  `order_745a7a020ecf89d5734d` under allocation plan
  `allocation_plan_8859abf5cf5708b35855`. During the same run, deterministic finalization
  regenerated allocation state as plan `allocation_plan_16a2809e7228b32b5bb7`, whose ISRG row
  had `disposition: hold`, `delta_value_base: 0`, and the two pending orders already providing the
  4.39% target. Despite the plan mismatch, the decision snapshot published both pending ISRG
  orders as `copy_ready: true`. Current pre-fill safety code rejects a baseline order when the
  strategy plan differs from the latest allocation target, so publication represented orders as
  actionable even though the execution path would classify them as superseded.
- **Concrete artifact or changed-file evidence:** The immutable payload
  `data/operations/payloads/01KYKX54MRDBWHGFKQERB0YG2Q.json`, request
  `data/runs/local-20260728-daily-all-29/01KYKX54MRDBWHGFKQERB0YG2Q/order_create_baseline_01.json`,
  and agent result bind the new order to plan `allocation_plan_8859abf5cf5708b35855`.
  `data/runs/local-20260728-daily-all-29/allocation_plan.json` records plan
  `allocation_plan_16a2809e7228b32b5bb7`. The final immutable
  `decision_snapshot.json` publishes orders `order_3b1467697b731e2bf689` and
  `order_745a7a020ecf89d5734d` as copy-ready, while the ISRG strategy text still says the earlier
  plan must remain current. The historical daily report's allocation audit shows the new plan and
  a hold disposition. In current code, `plan_allocation` includes non-terminal orders, pending
  exposure, pending cash, deployment budgets, and incremental candidate allocation in the plan
  hash, while `cancel_unauthorized_baseline_orders` rejects a strategy/latest-target plan mismatch.
- **Expected behavior:** Creating a pending order that fulfills an already approved total target
  must not, by itself, change that target's economic plan identity. A final snapshot must never
  mark a baseline order copy-ready if its structured plan binding is inconsistent with the latest
  target used by deterministic pre-fill validation.
- **Root-cause classification:** deterministic Python implementation, plus schema/validator
  coverage at the publication boundary. This is not an operation-skill failure or expected model
  variability; Hermes followed the selected skill and the inconsistent identity arose after the
  agent finished.
- **Proposed remediation:** Derive allocation-plan identity from stable economic inputs and the
  approved target outputs, excluding transient pending-order mechanics that merely implement the
  same target. Retain market, assessment, relationship, policy, and target changes in the identity.
  Also make decision-snapshot projection fail closed for a baseline pending order whose strategy
  plan does not match the latest canonical target. Do not weaken pre-fill validation.
- **Regression fixture required:** yes. Add one allocation regression that creates a deterministic
  baseline order and replans with unchanged evidence, proving that plan identity remains stable
  while disposition moves to `hold`. Add one advice regression proving that an actually mismatched
  baseline plan produces no projected/copy-ready order and blocks the snapshot.

### L-01 — The successful operation required a retry after a baseline risk ceiling was encoded as a rounded target

- **Severity:** low
- **Operation ID and type:** `01KYKX54MRDBWHGFKQERB0YG2Q`, `execute_strategy`
- **Observed behavior:** The terminal history records `attempt_count: 2`. The preceding immutable
  attempt in `local-20260728-daily-all-28` failed because the strategy's `risk_budget_pct` was the
  rounded current target rather than the configured maximum-position ceiling. The wiki log records
  the repair to 5% before the successful retry.
- **Concrete artifact or changed-file evidence:** The prior attempt's command audit records the
  risk-budget rejection; `data/wiki/log.md` records that the 4.39% display target was corrected to
  the configured 5% ceiling without enlarging the allocation target. The final run's command then
  succeeded with the same deterministic quantity.
- **Expected behavior:** A baseline strategy's risk budget is a ceiling; its quantity and rounded
  current target remain allocation-owned values. A strategy producer should encode the ceiling
  correctly on the first attempt.
- **Root-cause classification:** operation skill and structured strategy producer behavior in the
  preceding attempt, detected correctly by deterministic Python validation. It was not caused by
  the reviewed execute skill or external availability.
- **Proposed remediation:** no new change. The repository already states the ceiling rule in
  `AGENTS.md` and the strategy/execute workflow, enforces it deterministically, and has focused
  allocation tests that reject a baseline strategy whose risk budget differs from the configured
  cap. Adding another prompt instruction would be redundant.
- **Regression fixture required:** no new fixture; the current deterministic regression already
  covers this repaired behavior.

## Skill coverage

Meaningful coverage present in this run:

- `execute_strategy` for one baseline long-equity `increase` disposition normalized to the `open`
  signal lifecycle;
- immutable security, strategy, relationship, signal, assessment, and allocation-plan identity;
- deterministic whole-share incremental sizing with no quantity supplied by the agent;
- USD security with a separate USD/EUR conversion reference;
- `next_open` pending-order behavior with no backfilled fill;
- audited CLI-only structured writes and strict reconciliation;
- exact-delta validation and accurate agent-result reporting;
- one retry after deterministic risk-ceiling rejection;
- two concurrent pending orders for one cumulative baseline target;
- same-run allocation finalization and investor publication after order creation.

Important operation types not exercised:

- `source_discovery`, `wiki_ingest`, `opportunity_research`, `quick_check_research`,
  `idea_research`, `security_research`, `relationship_research`, `strategy_research`, and
  `daily_podcast` as Hermes operations in this run.

Important edge cases not exercised:

- execute `reduce`, `close`, `roll`, or `cancel`;
- short, option, or multi-leg strategies;
- `limit_touch` or `quote_mid` policies;
- partial or completed fills, fees, cash entries, portfolio rebuilds, and performance effects;
- stale or missing price/FX data, risk rejection in the successful attempt, expired orders, or
  option-quote unavailability;
- blocked/skipped/failed terminal agent results, dependencies, deduplication/merge decisions, or
  bounded follow-up creation;
- Markdown edits, source hierarchy, contradictory evidence handling, assessment updates, and
  security/relationship identity resolution;
- external source or network availability;
- Telegram delivery and podcast generation.

## Proposed changes

### Skill changes

No skill change. The exact historical execute skill required the behavior Hermes performed, and
the defect occurred in deterministic finalization after the operation. The already-repaired
baseline risk-ceiling rule does not need another duplicated instruction.

### Controller changes

No controller change. The controller selected the correct operation skill, captured the command
audit, enforced the file delta, and terminalized the operation consistently with its local result.

### Deterministic implementation changes

- Refactor allocation-plan hashing so a pending order that implements an unchanged approved total
  target cannot self-supersede that target. Hash stable decision inputs and normalized economic
  target outputs, not pending-order rows, pending accounting, or incremental allocation mechanics.
- Reject baseline pending-order projection in investor advice when the current strategy plan and
  latest allocation target disagree, matching pre-fill safety semantics.

### Schema or validator changes

- No JSON Schema shape change is required. Extend deterministic advice validation through the
  canonical snapshot builder so a plan-mismatched baseline pending order produces the existing
  `pending_order_state_unsafe` blocked state rather than a copy-ready row.

### Test and fixture changes

- Extend the existing active baseline allocation fixture to assert stable plan identity after its
  deterministic order becomes pending and the unchanged target moves to `hold`.
- Add a focused baseline advice fixture with a deliberately mismatched latest allocation plan and
  assert that no pending projection or actionable signal is published.

### No-change observations

- Preserve every immutable run artifact, terminal queue-history row, assessment history, allocation
  history, order/execution/cash history, and wiki log entry.
- Keep the operation's terminal `succeeded` status: the order creation itself was correct and the
  semantic defect was introduced by later deterministic finalization.
- Keep strict pre-fill plan, assessment, payoff, freshness, and risk gates unchanged.
- Treat the absence of network access in this operation as expected; it used retained canonical
  evidence and current deterministic market/FX records.
- Treat narrative phrasing and the model's concise result as acceptable variability; all material
  claims were supported by the payload, audited command output, and canonical state.

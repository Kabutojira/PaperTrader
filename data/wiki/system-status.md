---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-09-10"
updated: "2026-09-10"
provenance: deterministic-decision-projection
snapshot_id: "decision_3f0087c0f474f071d325"
as_of: "2026-09-10T19:03:58Z"
---

# System status and audit

**As of:** `2026-09-10T19:03:58Z`
**Investment data:** Portfolio state safe — research gaps remain
**Operations:** Attention required
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

Publication validation confirms that this generated artifact is internally consistent. Investment and operations health below describe the current canonical inputs.

## Current investment health

- Assessments: 52/83
- Fresh-evidence assessments: 48/83
- Relationship reviews: 20/83
- Accepted relationships: 19
- Market success/failure: 91/0
- Candidate FX gaps: 0
- Last successful daily run: 2026-09-10

## Queue and execution health

- Ready or active strategies: 4
- Active signals: 2
- Pending orders: 2
- Queued remediation operations: 0
- Operations are claimed and executed strictly sequentially.

## Sequential research backlog

- Research backlog: 345

## Publication health

- Snapshot schema and derived CSV equality: validated
- Portfolio accounting reconciliation: validated

## Current issues by investment impact

Current unresolved issues: **22**.
Resolved and superseded issues remain in the canonical audit but are not current health.

### Affects Candidate (16)

- Error **ETN — Eaton Corporation plc: Hermes operation validation failed: Quick check research for ETN on 2026-08-11** — agent result schema: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment; post-run integrity: agent result data/runs/Daily report for 2026-08-11/Quick check research for ETN on 2026-08-11/agent\_result.json: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'
- Error **FUC.F — Fanuc Corporation: FANUC assessment source operation is ambiguous within one run** — The schema-v2 FANUC full-review assessment could not be accepted because the deterministic research applier found both the completed quick\_check\_research operation and this running security\_research operation for the same security and run\_id, then rejected the immutable assessment request with no assessment-state changes. The mandatory security context succeeded; both issuer PDFs were rechecked with unchanged hashes, source history and the security summary were updated through validated commands
- Error **KTOS — Kratos Defense &amp; Security Solutions, Inc.: Hermes operation validation failed: Quick check research for KTOS on 2026-08-12** — Hermes timed out after 600s; agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for KTOS on 2026-08-12/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment
- Error **Hermes operation validation failed: Quick check research for HOOD on 2026-08-15** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-15/Quick check research for HOOD on 2026-08-15
- Error **RKLB — Rocket Lab Corporation: Hermes operation validation failed: Quick check research for RKLB on 2026-08-18** — commands\_run claims commands without deterministic CLI audit receipts: \['scripts/papertrader research assessment upsert --request data/runs/Daily report for 2026-08-18/Quick check research for RKLB on 2026-08-18/assessment\_upsert\_request.json', 'scripts/papertrader research security-context --security-id RKLB'\]
- Error **Hermes operation validation failed: Quick check research for SPOT on 2026-08-16** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Security research for WTI on 2026-08-18** — Hermes exited with status 1; agent result is missing or a symlink: data/runs/Daily report for 2026-09-06/Security research for WTI on 2026-08-18/agent\_result.json
- Error **XMTR — Xometry, Inc.: Xometry security review blocked by issuer identity conflict** — The validated operation payload identifies XMTR with issuer\_id issuer\_0b3fe347955c2ce31e63, while canonical data/tables/securities.csv binds the same immutable security\_id to issuer\_dbdde9b294689a9af3d5. The validated security upsert correctly failed closed with an immutable-identity conflict. Four current primary sources were retained, but no security row, research page, assessment, strategy, signal, order, allocation or accounting state was changed. Resolve the canonic
- Error **Hermes operation validation failed: Security research for SGML on 2026-08-17** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-17/Security research for SGML on 2026-08-17
- Error **Hermes operation validation failed: Security research for YEC.F on 2026-08-22** — Hermes timed out after 1800s; agent result is missing or a symlink: data/runs/Daily report for 2026-09-07/Security research for YEC.F on 2026-08-22/agent\_result.json
- Error **Hermes operation validation failed: Security research for ANIC.L on 2026-07-29** — agent result schema: 'insufficient\_observations' is not one of \['single\_value', 'insufficient\_comparability', 'insufficient\_history', 'recorded source', 'not\_decision\_relevant', 'no\_page\_change'\]; post-run integrity: agent result data/runs/Daily report for 2026-09-09/Security research for ANIC.L on 2026-07-29/agent\_result.json: 'insufficient\_observations' is not one of \['single\_value', 'insufficient\_comparability', 'insufficient\_history', 'recorded source', 'not\_decision\_relevant', 'no\_page\_change'\]
- Error **ABBNY — ABB Ltd: ABB assessment provenance does not match corrected final research page** — Operation Security research for ABBNY on 2026-09-03 accepted immutable assessment assessment\_a3946a163695f1a9f51f while the security page still carried the prior prose disposition. Deterministic derivation changed the current disposition from Sell / Avoid to Hold / Watch at the lower mark, so the page and structured security summary were corrected after the immutable assessment was written. The current assessment and final page now agree economically, and exactly one assessment version names this operation, bu
- Error **Hermes operation validation failed: Security research for ABBNY on 2026-09-03** — files\_changed claims paths absent from the actual delta: \['data/operations/operations\_TODO.csv'\]
- Error **Hermes operation validation failed: Quick check research for TWST on 2026-08-05** — agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for TWST on 2026-08-05/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **ASML — ASML Holding N.V.: ASML assessment rejected after security row update** — The retry operation refreshed the ASML page and security row to the 2026-08-19 USD 1,751.73 mark, but the schema-v2 assessment request was rejected before assessment state changed because valuation\_template\_rationale is a required field and was omitted. The routed-operation no-retry rule forbids correcting and invoking a second assessment request after this rejection. The canonical assessment therefore remains the prior unsupported version, the prepared relationship and idea follow-up requests w
- Error **WTI — W&amp;T Offshore, Inc.: Hermes operation validation failed: Quick check research for WTI on 2026-08-18** — completed security research requires this run's comparable assessment

### Publication Only (6)

- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — Hermes timed out after 1200s; agent result was written before completed change: data/runs/Daily report for 2026-08-17/Daily podcast for Daily report for 2026-08-17 on 2026-08-17/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-05 on 2026-08-05** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/Daily report for 2026-08-05/Daily podcast for Daily report for 2026-08-05 on 2026-08-05/agent\_result.json
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — cannot restore rejected path data/wiki/daily-reports/daily-report\_20260806.md: pre-run path cannot be restored because Git metadata is unavailable; daily podcast spoken transcript must label paper trading
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — non-successful daily podcast must not retain a transcript page
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-09-06 on 2026-09-06** — Hermes exited with status 1; agent result is missing or a symlink: data/runs/Daily report for 2026-09-06/Daily podcast for Daily report for 2026-09-06 on 2026-09-06/agent\_result.json

## Historical audit health

- Resolved and superseded incidents remain visible in canonical issue and operation history.
- No unresolved issue is hidden or aged out.

## Audit links

- [[research-catalog|Complete research catalog]]
- [[security-catalog|Tracked securities]]
- [[SCHEMA|Wiki schema]]
- [[log|Append-only research log]]
- [Decision snapshot JSON](data/decision_snapshot.json)
- [Model portfolio CSV](data/model_portfolio.csv)
- [Actionable signals CSV](data/actionable_signals.csv)

[[index|Back to today's decision]]

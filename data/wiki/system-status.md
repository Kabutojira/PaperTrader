---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-09-25"
updated: "2026-09-25"
provenance: deterministic-decision-projection
snapshot_id: "decision_a6f0800e760ee3140acb"
as_of: "2026-09-25T19:12:04Z"
---

# System status and audit

**As of:** `2026-09-25T19:12:04Z`
**Investment data:** Portfolio state safe — research gaps remain
**Operations:** Attention required
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

Publication validation confirms that this generated artifact is internally consistent. Investment and operations health below describe the current canonical inputs.

## Current investment health

- Assessments: 32/83
- Fresh-evidence assessments: 31/83
- Relationship reviews: 20/83
- Accepted relationships: 19
- Market success/failure: 92/0
- Candidate FX gaps: 0
- Last successful daily run: 2026-09-11

## Queue and execution health

- Ready or active strategies: 3
- Active signals: 0
- Pending orders: 0
- Queued remediation operations: 0
- Operations are claimed and executed strictly sequentially.

## Sequential research backlog

- Research backlog: 532

## Publication health

- Snapshot schema and derived CSV equality: validated
- Portfolio accounting reconciliation: validated

## Current issues by investment impact

Current unresolved issues: **44**.
Resolved and superseded issues remain in the canonical audit but are not current health.

### Affects Candidate (37)

- Error **ETN — Eaton Corporation plc: Hermes operation validation failed: Quick check research for ETN on 2026-08-11** — agent result schema: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment; post-run integrity: agent result data/runs/Daily report for 2026-08-11/Quick check research for ETN on 2026-08-11/agent\_result.json: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'
- Error **FUC.F — Fanuc Corporation: FANUC assessment source operation is ambiguous within one run** — The schema-v2 FANUC full-review assessment could not be accepted because the deterministic research applier found both the completed quick\_check\_research operation and this running security\_research operation for the same security and run\_id, then rejected the immutable assessment request with no assessment-state changes. The mandatory security context succeeded; both issuer PDFs were rechecked with unchanged hashes, source history and the security summary were updated through validated commands
- Error **KTOS — Kratos Defense &amp; Security Solutions, Inc.: Hermes operation validation failed: Quick check research for KTOS on 2026-08-12** — Hermes timed out after 600s; agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for KTOS on 2026-08-12/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment
- Error **Hermes operation validation failed: Security research for PLS.AX on 2026-09-24** — Hermes exited with status 1; agent result is missing or a symlink: data/runs/Daily report for 2026-09-25/Security research for PLS.AX on 2026-09-24/agent\_result.json
- Error **Hermes operation validation failed: Quick check research for HOOD on 2026-08-15** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-15/Quick check research for HOOD on 2026-08-15
- Error **Hermes operation validation failed: Security research for ANIC.L on 2026-09-21** — searched challenge requires retained immutable inspection references
- Error **RKLB — Rocket Lab Corporation: Hermes operation validation failed: Quick check research for RKLB on 2026-08-18** — commands\_run claims commands without deterministic CLI audit receipts: \['scripts/papertrader research assessment upsert --request data/runs/Daily report for 2026-08-18/Quick check research for RKLB on 2026-08-18/assessment\_upsert\_request.json', 'scripts/papertrader research security-context --security-id RKLB'\]
- Error **Hermes operation validation failed: Quick check research for SPOT on 2026-08-16** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Security research for WTI on 2026-08-18** — Hermes exited with status 1; agent result is missing or a symlink: data/runs/Daily report for 2026-09-06/Security research for WTI on 2026-08-18/agent\_result.json
- Error **XMTR — Xometry, Inc.: Xometry security review blocked by issuer identity conflict** — The validated operation payload identifies XMTR with issuer\_id issuer\_0b3fe347955c2ce31e63, while canonical data/tables/securities.csv binds the same immutable security\_id to issuer\_dbdde9b294689a9af3d5. The validated security upsert correctly failed closed with an immutable-identity conflict. Four current primary sources were retained, but no security row, research page, assessment, strategy, signal, order, allocation or accounting state was changed. Resolve the canonic
- Error **Hermes operation validation failed: Security research for SGML on 2026-08-17** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-17/Security research for SGML on 2026-08-17
- Error **Hermes operation validation failed: Security research for YEC.F on 2026-08-22** — Hermes timed out after 1800s; agent result is missing or a symlink: data/runs/Daily report for 2026-09-07/Security research for YEC.F on 2026-08-22/agent\_result.json
- Error **Hermes operation validation failed: Security research for ANIC.L on 2026-09-11** — files\_changed claims paths absent from the actual delta: \['data/operations/operations\_TODO.csv'\]
- Error **ABBNY — ABB Ltd: ABB assessment provenance does not match corrected final research page** — Operation Security research for ABBNY on 2026-09-03 accepted immutable assessment assessment\_a3946a163695f1a9f51f while the security page still carried the prior prose disposition. Deterministic derivation changed the current disposition from Sell / Avoid to Hold / Watch at the lower mark, so the page and structured security summary were corrected after the immutable assessment was written. The current assessment and final page now agree economically, and exactly one assessment version names this operation, bu
- Error **Hermes operation validation failed: Security research for LMND on 2026-09-11** — claim excerpt exceeds the bounded public-source quote allowance
- Error **Hermes operation validation failed: Opportunity research for Market alert for CROX on 2026-09-11** — agent result is missing or a symlink: data/runs/Daily report for 2026-09-11/Opportunity research for Market alert for CROX on 2026-09-11/agent\_result.json
- Error **Hermes operation validation failed: Security research for ABBNY on 2026-09-03** — files\_changed claims paths absent from the actual delta: \['data/operations/operations\_TODO.csv'\]
- Error **Hermes operation validation failed: Quick check research for TWST on 2026-08-05** — agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for TWST on 2026-08-05/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Security research for ALB on 2026-09-17** — observed claim support must match the retained inspected source excerpt
- Error **Hermes operation validation failed: Security research for FLNC on 2026-09-22** — Hermes timed out after 1800s; agent result is missing or a symlink: data/runs/Daily report for 2026-09-22/Security research for FLNC on 2026-09-22/agent\_result.json
- Error **Hermes operation validation failed: Security research for FLNC on 2026-09-23** — observed claim support must match the retained inspected source excerpt
- Error **ASML — ASML Holding N.V.: ASML assessment rejected after security row update** — The retry operation refreshed the ASML page and security row to the 2026-08-19 USD 1,751.73 mark, but the schema-v2 assessment request was rejected before assessment state changed because valuation\_template\_rationale is a required field and was omitted. The routed-operation no-retry rule forbids correcting and invoking a second assessment request after this rejection. The canonical assessment therefore remains the prior unsupported version, the prepared relationship and idea follow-up requests w
- Error **WTI — W&amp;T Offshore, Inc.: Hermes operation validation failed: Quick check research for WTI on 2026-08-18** — completed security research requires this run's comparable assessment
- Warning **PLS.AX — PLS Group Limited: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-PLS.AX-rsi\_oversold-7072b69ac454.md** — classifier blocked for data/wiki/inbox/market-PLS.AX-rsi\_oversold-7072b69ac454.md
- Warning **TWST — Twist Bioscience Corporation: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-TWST-volume\_anomaly-eca44104d625.md** — classifier blocked for data/wiki/inbox/market-TWST-volume\_anomaly-eca44104d625.md
- Warning **RBLX — Roblox Corporation: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-RBLX-volume\_anomaly-da215c897da5.md** — classifier blocked for data/wiki/inbox/market-RBLX-volume\_anomaly-da215c897da5.md
- Warning **FUC.F — Fanuc Corporation: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-FUC.F-volume\_anomaly-55ab37e01463.md** — classifier blocked for data/wiki/inbox/market-FUC.F-volume\_anomaly-55ab37e01463.md
- Warning **VALE — Vale S.A.: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-VALE-bollinger\_below\_lower-4e9f92c3ade3.md** — classifier blocked for data/wiki/inbox/market-VALE-bollinger\_below\_lower-4e9f92c3ade3.md
- Warning **DNA — Ginkgo Bioworks Holdings, Inc.: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-DNA-volume\_anomaly-baf6fd98f3b4.md** — classifier blocked for data/wiki/inbox/market-DNA-volume\_anomaly-baf6fd98f3b4.md
- Warning **EVK — Evonik Industries AG: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-EVK-volume\_anomaly-9c18f8d9013d.md** — classifier blocked for data/wiki/inbox/market-EVK-volume\_anomaly-9c18f8d9013d.md
- Warning **ANIC.L — Agronomics Limited: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-ANIC.L-volume\_anomaly-cff91c2ffc03.md** — classifier blocked for data/wiki/inbox/market-ANIC.L-volume\_anomaly-cff91c2ffc03.md
- Warning **PARRO.PA — Parrot S.A.: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-PARRO.PA-bollinger\_below\_lower-1e5a0379c26f.md** — classifier blocked for data/wiki/inbox/market-PARRO.PA-bollinger\_below\_lower-1e5a0379c26f.md
- Warning **RTX — RTX Corporation: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-RTX-rsi\_oversold-35152eacefc5.md** — classifier blocked for data/wiki/inbox/market-RTX-rsi\_oversold-35152eacefc5.md
- Warning **SCCO — Southern Copper Corporation: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-SCCO-macd\_cross\_above\_signal-fc616bc5927d.md** — classifier blocked for data/wiki/inbox/market-SCCO-macd\_cross\_above\_signal-fc616bc5927d.md
- Warning **PRLB — Proto Labs, Inc.: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-PRLB-volume\_anomaly-18a17447098d.md** — classifier blocked for data/wiki/inbox/market-PRLB-volume\_anomaly-18a17447098d.md
- Warning **BAS — BASF SE: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-BAS-volume\_anomaly-9d5076893945.md** — classifier blocked for data/wiki/inbox/market-BAS-volume\_anomaly-9d5076893945.md
- Warning **FLNC — Fluence Energy, Inc.: Daily preparation degraded: classifier blocked for data/wiki/inbox/market-FLNC-rsi\_oversold-87f176686042.md** — classifier blocked for data/wiki/inbox/market-FLNC-rsi\_oversold-87f176686042.md

### Publication Only (6)

- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — Hermes timed out after 1200s; agent result was written before completed change: data/runs/Daily report for 2026-08-17/Daily podcast for Daily report for 2026-08-17 on 2026-08-17/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-05 on 2026-08-05** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/Daily report for 2026-08-05/Daily podcast for Daily report for 2026-08-05 on 2026-08-05/agent\_result.json
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — cannot restore rejected path data/wiki/daily-reports/daily-report\_20260806.md: pre-run path cannot be restored because Git metadata is unavailable; daily podcast spoken transcript must label paper trading
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — non-successful daily podcast must not retain a transcript page
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-09-06 on 2026-09-06** — Hermes exited with status 1; agent result is missing or a symlink: data/runs/Daily report for 2026-09-06/Daily podcast for Daily report for 2026-09-06 on 2026-09-06/agent\_result.json

### Operational Only (1)

- Error **PRX — Prosus N.V.: Hermes operation validation failed: Research triage for PRX on 2026-09-17** — commands\_run claims commands without deterministic CLI audit receipts: \['scripts/papertrader research security-context --security-id PRX'\]

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

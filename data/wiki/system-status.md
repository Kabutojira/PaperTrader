---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-07-28"
updated: "2026-07-28"
provenance: deterministic-decision-projection
snapshot_id: "decision_f7970c846929cff52159"
as_of: "2026-07-28T10:15:46Z"
---

# System status and audit

**Publication snapshot:** `decision_f7970c846929cff52159`
**As of:** `2026-07-28T10:15:46Z`
**Data status:** Degraded — review coverage and data gaps
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

## Coverage

- Assessments: 24/24
- Fresh-evidence assessments: 24/24
- Current accepted relationships: 22/24
- Ready or active strategies: 1
- Active signals: 2
- Pending orders: 2
- Market success/failure: 24/0
- Candidate FX gaps: 0
- Research backlog: 3
- Last successful daily run: `2026-07-28T10:15:46Z`

## Current issues by investment impact

### Publication Only

- `warning` **Telegram delivery failed: a1340c7457be74bc0d53dcf03b78647077a1ae75** — Committed Telegram delivery is awaiting a bounded retry.
- `warning` **Telegram delivery failed: a8393d13b8e650e0d813cc9346c3d11dd063264f** — Committed Telegram delivery is awaiting a bounded retry.

## Bounded active operation queue

Showing 3 of 3 active operations.

<details><summary>Technical queue identifiers</summary>

- `waiting` `01KYEXAGNREGCP02XCC9VBV80V` — `security_research` for `security_c5a9e460d3350284d157`
- `waiting` `01KYEWGWBRV9EV6YN1WQA6G3WF` — `security_research` for `security_cb88f9154cfeaa15e878`
- `waiting` `01KYFXFKB04HSHKYVSPNGXVJX0` — `security_research` for `security_66cdcf90aac0d83e76f3`

</details>

## Audit links

- [[research-catalog|Complete research catalog]]
- [[SCHEMA|Wiki schema]]
- [[log|Append-only research log]]
- [Decision snapshot JSON](data/decision_snapshot.json)
- [Model portfolio CSV](data/model_portfolio.csv)
- [Actionable signals CSV](data/actionable_signals.csv)

[[index|Back to today's decision]]

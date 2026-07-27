---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-07-27"
updated: "2026-07-27"
provenance: deterministic-decision-projection
snapshot_id: "decision_7eae4d9fa5380e578266"
as_of: "2026-07-27T15:39:59Z"
---

# System status and audit

**Publication snapshot:** `decision_7eae4d9fa5380e578266`
**As of:** `2026-07-27T15:39:59Z`
**Data status:** Degraded — review coverage and data gaps
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

## Coverage

- Assessments: 2/24
- Fresh-evidence assessments: 2/24
- Current accepted relationships: 3/24
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market success/failure: 22/2
- Candidate FX gaps: 0
- Research backlog: 57
- Last successful daily run: `2026-07-27T13:35:47Z`

## Current issues by investment impact

### Affects Candidate

- `warning` **FCX — Freeport-McMoRan Inc.: Daily preparation degraded: security\_2dbe878dfc899d7ee867** — security\_2dbe878dfc899d7ee867: MarketDataError: invalid OHLC range on 2026-07-27 for security\_2dbe878dfc899d7ee867
- `warning` **SQM — Sociedad Quimica y Minera de Chile S.A.: Daily preparation degraded: security\_9d4049ed6669a52815d6** — security\_9d4049ed6669a52815d6: MarketDataError: invalid OHLC range on 2026-07-27 for security\_9d4049ed6669a52815d6

### Publication Only

- `warning` **Telegram delivery failed: 798017b585f7de9127a798eb52aac52052f72786** — Committed Telegram delivery is awaiting a bounded retry.
- `warning` **Telegram delivery failed: d3c816d22ba7ec5bb52ac8278b8f231f68dace74** — Committed Telegram delivery is awaiting a bounded retry.

## Bounded active operation queue

Showing 20 of 57 active operations.

<details><summary>Technical queue identifiers</summary>

- `waiting` `01KYHW57102CCNPR5A5GNX8WVG` — `relationship_research` for `relationship_def43e5b4e13577e2b99`
- `waiting` `01KYHW57102ZB98NS7QHW3JSD9` — `relationship_research` for `relationship_297f9e36fb4e93a808e8`
- `ready` `01KYHW57104SC0RP9HX81QSW7K` — `relationship_research` for `relationship_d9c8f578040386a487be`
- `waiting` `01KYHW57105JV3P74FXN3P4HZ6` — `relationship_research` for `relationship_871e21ff73620ab8eb14`
- `waiting` `01KYHW5710BWYZSZ0Z4ASMB8EM` — `relationship_research` for `relationship_ad2f37b49980dbc73a08`
- `waiting` `01KYHW5710C90D1S5BAXB10915` — `relationship_research` for `relationship_510158d3d515d91d5c14`
- `waiting` `01KYHW5710DS9JV64CJDQBVCMV` — `relationship_research` for `relationship_392da6d90e7c969945a2`
- `ready` `01KYHW5710GZWDV54QMTWS2159` — `relationship_research` for `relationship_3570e003fd90cd83d26f`
- `waiting` `01KYHW5710HN9JVFYSCM4C3KKT` — `relationship_research` for `relationship_9e7b4700174908755cbc`
- `waiting` `01KYHW5710J70PNSC8E3ET3904` — `relationship_research` for `relationship_7e9fd9486e494dd05bb5`
- `waiting` `01KYHW5710K4BSCNVNKX25GXD9` — `relationship_research` for `relationship_e5f55616b9beaf661080`
- `waiting` `01KYHW5710KX0AQTGA5359Y5WF` — `relationship_research` for `relationship_1655ac715c33506ec7da`
- `waiting` `01KYHW5710MA7RMCX7VSSRBN3W` — `relationship_research` for `relationship_f2efab6050df0edcb762`
- `waiting` `01KYHW5710NPPFPFY0HTDAME01` — `relationship_research` for `relationship_87b95f713a902d531f2f`
- `waiting` `01KYHW5710QM7X1WMPT8PR0MTQ` — `relationship_research` for `relationship_228f56aa5d91f3688b67`
- `waiting` `01KYHW5710RH631A9AKFJ8KRGG` — `relationship_research` for `relationship_c829dae21648bb133cc7`
- `waiting` `01KYHW5710S59C4PZQJD9311NB` — `relationship_research` for `relationship_9773364a04293a4febaf`
- `waiting` `01KYHW5710VH8HSMT8N209A500` — `relationship_research` for `relationship_250194f6a9e3a1817632`
- `waiting` `01KYHW5710X7RTKPR6BKG7S9YA` — `relationship_research` for `relationship_afac7205cd7e09800edf`
- `waiting` `01KYHW5710Y3GNPD64A26Y4GF4` — `relationship_research` for `relationship_670ed88c8e4616316a19`

</details>

## Audit links

- [[research-catalog|Complete research catalog]]
- [[SCHEMA|Wiki schema]]
- [[log|Append-only research log]]
- [Decision snapshot JSON](data/decision_snapshot.json)
- [Model portfolio CSV](data/model_portfolio.csv)
- [Actionable signals CSV](data/actionable_signals.csv)

[[index|Back to today's decision]]

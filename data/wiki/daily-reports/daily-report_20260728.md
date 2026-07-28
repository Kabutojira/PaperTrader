---
title: "PaperTrader daily report — 2026-07-28"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-28"
updated: "2026-07-28"
provenance: deterministic-report-generator
run_id: "local-20260728-daily-all-29"
snapshot_id: "decision_55f99cf865416f0c19b8"
---

# PaperTrader daily report — 2026-07-28

## 1. Investor decision summary

<!-- papertrader-investor-brief:start -->
# Deploy approved paper capital

- **Data status:** Degraded — review coverage and data gaps
- **As of:** `2026-07-28T08:45:56Z`
- **Snapshot:** `decision_55f99cf865416f0c19b8`
- **Cash:** 100000 EUR (100%)
- **Gross exposure:** 0 EUR
- **Approved target cash:** 95604.41 EUR (95.606745%)
- **Actionable signals:** 2

## Approved target changes

- **ISRG:** Buy to 4.393255% (paper estimate)

## Actionable signals

- **ISRG:** Buy — Pending validated paper order
- **ISRG:** Buy — Pending validated paper order

## Top blocker or near miss

- **ISRG — Intuitive Surgical, Inc.:** The eligible set is not sufficiently diversified.
<!-- papertrader-investor-brief:end -->

### Deterministic reasons

- Validated opening paper actions are pending.

## 2. Model portfolio and approved changes

- Current equity: 100000 EUR
- Current cash: 100000 EUR (100%)
- Current gross exposure: 0 EUR
- Approved target cash: 95604.41 EUR (95.606745%)
- Pending-order targets are estimates at the snapshot mark; only fills change accounting.

| Holding | Sleeve | Current weight | Approved target | Current value | Target value | Action | State |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Cash | cash | 100% | 95.606745% | 100000  | 95604.41  | Trim | Pending validated paper order |
| [ISRG — Intuitive Surgical, Inc.](strategies/strategy_bd005fc3733b1475b6f9) | baseline | 0% | 4.393255% | 0  | 4393.15  | Buy | Pending validated paper order |

## 3. Actionable signals and pending orders

### [ISRG — Intuitive Surgical, Inc.](strategies/strategy_bd005fc3733b1475b6f9)

- Action: **Buy**
- State: Pending validated paper order (copy ready)
- Strategy: Intuitive Surgical bounded baseline allocation
- Signal window: `2026-07-28T07:47:48Z` to `2026-07-29T07:45:53Z`
- Market data: `2026-07-27T20:55:09Z`
- Rationale: Replace the cancelled under-sized order signal while allocation plan allocation\_plan\_02b52e8899b55922bf4e and assessment 2026-07-27T21:28:56Z remain current. The approved target remains a bounded 2.2% Intuitive Surgical baseline allocation, and deterministic create-baseline sizing now owns the exact whole-share delta.

### [ISRG — Intuitive Surgical, Inc.](strategies/strategy_bd005fc3733b1475b6f9)

- Action: **Buy**
- State: Pending validated paper order (copy ready)
- Strategy: Intuitive Surgical bounded baseline allocation
- Signal window: `2026-07-28T08:22:44Z` to `2026-07-29T08:21:25Z`
- Market data: `2026-07-27T20:55:09Z`
- Rationale: Review the incremental allocator-directed Intuitive Surgical baseline exposure only while allocation plan allocation\_plan\_8859abf5cf5708b35855 and assessment 2026-07-27T21:28:56Z remain current. The plan's increase disposition maps to the open signal lifecycle, but this signal authorizes no quantity. The effective score of 63 clears the cash hurdle, while limited 2.5% base upside, 23.2% downside, weak timing, and insufficient diversification keep exposure lower-conviction and capped at the deterministic 4.39% target after pending exposure.

## 4. Candidates and near misses

| Candidate | State | Score | Base upside | Main reason |
| --- | --- | ---: | ---: | --- |
| [ISRG — Intuitive Surgical, Inc.](securities/security_1f9cce545ede94cd6349) | Risk blocked | 63 | 2.5% | The eligible set is not sufficiently diversified. |
| [GEV — GE Vernova Inc.](securities/security_4b61970aa8f574446819) | Valuation unattractive | 42.8 | 1.9% | The effective score does not beat the configured cash hurdle. |
| [ANET — Arista Networks, Inc.](securities/security_6f9a1450edceb9307c9a) | Valuation unattractive | 34 | -15.7% | The assessed base case has no positive upside. |
| [RBLX — Roblox Corporation](securities/security_c9a37d277445869a8809) | Valuation unattractive | 30.6 | -19.9% | The assessed base case has no positive upside. |
| [PLTR — Palantir Technologies Inc.](securities/security_bdc2f87dadf134760c3a) | Valuation unattractive | 28.6 | -40.4% | The assessed base case has no positive upside. |

## 5. Performance and risk

- Daily return: 0%
- Cumulative return: 0%
- Running drawdown: 0%
- Realized P/L: 0 EUR
- Unrealized P/L: 0 EUR
- Largest position weight: 0%
- Largest sector weight: 0%


## 6. Research changes

### Evidence-linked narrative

- Created pending next-open paper order \`order\_745a7a020ecf89d5734d\` for seven incremental Intuitive Surgical shares under the current 4.39% baseline target after 2.2% pending exposure; no fill or accounting transition occurred. Evidence: `data/market/latest.csv and data/market/fx/USD_EUR.csv`, `data/runs/local-20260728-daily-all-29/01KYKX54MRDBWHGFKQERB0YG2Q/command_audit.json`, `data/tables/allocation_targets.csv`, `data/tables/orders.csv and data/tables/order_legs.csv`, `data/tables/strategies.csv, data/tables/strategy_legs.csv, and data/tables/signals.csv`.

- [[model-portfolio]]
- [[performance]]
- [[relationships/relationship_1655ac715c33506ec7da]]
- [[relationships/relationship_228f56aa5d91f3688b67]]
- [[relationships/relationship_250194f6a9e3a1817632]]
- [[relationships/relationship_297f9e36fb4e93a808e8]]
- [[relationships/relationship_392da6d90e7c969945a2]]
- [[relationships/relationship_510158d3d515d91d5c14]]
- [[relationships/relationship_670ed88c8e4616316a19]]
- [[relationships/relationship_7e9fd9486e494dd05bb5]]
- [[relationships/relationship_871e21ff73620ab8eb14]]
- [[relationships/relationship_87b95f713a902d531f2f]]
- [[relationships/relationship_9773364a04293a4febaf]]
- [[relationships/relationship_9befaccc50d8cd94372b]]
- [[relationships/relationship_9e7b4700174908755cbc]]
- [[relationships/relationship_ad2f37b49980dbc73a08]]
- [[relationships/relationship_afac7205cd7e09800edf]]
- [[relationships/relationship_c829dae21648bb133cc7]]
- [[relationships/relationship_cbdd07edda84994325d6]]
- [[relationships/relationship_d9c8f578040386a487be]]
- [[relationships/relationship_def43e5b4e13577e2b99]]
- [[relationships/relationship_e5f55616b9beaf661080]]
- [[relationships/relationship_f2efab6050df0edcb762]]
- [[research-catalog]]
- [[securities/security_22c2b9d782a62d7a9b86]]
- [[securities/security_2c779e81c27b78c556bb]]
- [[securities/security_4627aea1bf7d8943d3d8]]
- [[securities/security_59304f90c440def31dc5]]
- [[securities/security_66cdcf90aac0d83e76f3]]
- [[securities/security_8472507d7d320aa388a7]]
- [[securities/security_9d4049ed6669a52815d6]]
- [[securities/security_c120e9f26ebb6159adf9]]
- [[securities/security_cc4dcb8f002b61dffe00]]
- [[securities/security_f2b9760d847b2ba59324]]
- [[securities/security_fb87fac302a5446a1ced]]
- [[signals]]
- [[strategies/strategy_bd005fc3733b1475b6f9]]
- [[system-status]]

## 7. Data-quality and coverage impact

- Data status: **degraded**
- Assessments: 24/24
- Fresh-evidence assessments: 24/24
- Current accepted relationships: 22/24
- Ready or active strategies: 1
- Active signals: 2
- Pending orders: 2
- Market-data success/failure: 24/0
- Research alerts (not trade signals): 14

No current system impacts.

## 8. Audit appendix

### Run diagnostics

- Run ID: `local-20260728-daily-all-29`
- Run status: `succeeded`
- Generated (UTC): `2026-07-28T08:45:56Z`
- Decision snapshot: `decision_55f99cf865416f0c19b8`

### Complete market freshness

| Security ID | Price date | Retrieved at | Status | Error |
| --- | --- | --- | --- | --- |
| security_18a3ab0ee6086ee85d0f | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_1c055eb9b2bb1f5a8ff2 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_1f9cce545ede94cd6349 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_22c2b9d782a62d7a9b86 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_2c779e81c27b78c556bb | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_2dbe878dfc899d7ee867 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_37ddcbdaad296ad831f2 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_4627aea1bf7d8943d3d8 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_4b61970aa8f574446819 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_59304f90c440def31dc5 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_66cdcf90aac0d83e76f3 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_6ad1af8d10d6276a0221 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_6f9a1450edceb9307c9a | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_7ca095d63423c55a90e3 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_8472507d7d320aa388a7 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_9d4049ed6669a52815d6 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_a9eb9838940ef5ceaa0c | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_bdc2f87dadf134760c3a | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_c120e9f26ebb6159adf9 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_c9a37d277445869a8809 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_cc4dcb8f002b61dffe00 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_ed7d5b616a196969c815 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_f2b9760d847b2ba59324 | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |
| security_fb87fac302a5446a1ced | 2026-07-27 | 2026-07-27T20:55:09Z | ok | — |

### Orders and executions

| Order ID | Strategy ID | Fill policy | Status | Created |
| --- | --- | --- | --- | --- |
| order_371f356c9fa026750350 | strategy_bd005fc3733b1475b6f9 | next_open | cancelled | 2026-07-28T07:36:01Z |
| order_3b1467697b731e2bf689 | strategy_bd005fc3733b1475b6f9 | next_open | pending | 2026-07-28T07:52:26Z |
| order_745a7a020ecf89d5734d | strategy_bd005fc3733b1475b6f9 | next_open | pending | 2026-07-28T08:42:27Z |

| Execution ID | Order ID | Security ID | Side | Quantity | Fill | Fees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| — | — | — | — | 0 | no executions | 0 |

### Allocation audit

- Plan ID: `allocation_plan_16a2809e7228b32b5bb7`
- Mode: `active`
- Deployment budget: 15000 EUR
- Capital allocated: 0 EUR
- Capital unallocated: 55606.85186299546379433569002 EUR

| Rank | Security ID | Target weight | Disposition | Machine reasons |
| ---: | --- | ---: | --- | --- |
| 1 | security_1f9cce545ede94cd6349 | 4.39% | hold | above_cash_hurdle\|insufficient_diversification |
| — | security_18a3ab0ee6086ee85d0f | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_1c055eb9b2bb1f5a8ff2 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_22c2b9d782a62d7a9b86 | 0% | excluded | score_below_cash_hurdle |
| — | security_2c779e81c27b78c556bb | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_2dbe878dfc899d7ee867 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_37ddcbdaad296ad831f2 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_4627aea1bf7d8943d3d8 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:accounting_uncertain,solvency_risk,valuation_unsupported\|score_below_cash_hurdle |
| — | security_4b61970aa8f574446819 | 0% | excluded | score_below_cash_hurdle |
| — | security_59304f90c440def31dc5 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_66cdcf90aac0d83e76f3 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_6ad1af8d10d6276a0221 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_6f9a1450edceb9307c9a | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_7ca095d63423c55a90e3 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_8472507d7d320aa388a7 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_9d4049ed6669a52815d6 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_a9eb9838940ef5ceaa0c | 0% | excluded | score_below_cash_hurdle |
| — | security_bdc2f87dadf134760c3a | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_c120e9f26ebb6159adf9 | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_c9a37d277445869a8809 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle |
| — | security_cc4dcb8f002b61dffe00 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_ed7d5b616a196969c815 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_f2b9760d847b2ba59324 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_fb87fac302a5446a1ced | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |

### Research-operation audit

| Operation ID | Type | Entity ID | Disposition | Machine reason |
| --- | --- | --- | --- | --- |
| 01KYHW5710HN1HFEQB9TRTX6S2 | security_research | security_2dbe878dfc899d7ee867 | succeeded | agent_result:succeeded |
| 01KYHW5710M89EMQMNDY940EKH | security_research | security_59304f90c440def31dc5 | succeeded | agent_result:succeeded |
| 01KYHW5710QD07N3J66DEV37C1 | security_research | security_9d4049ed6669a52815d6 | succeeded | agent_result:succeeded |
| 01KYHW5710QRVPBXMBAY8GAWDM | security_research | security_22c2b9d782a62d7a9b86 | succeeded | agent_result:succeeded |
| 01KYHW5710RKVS0S8HF233BBTR | security_research | security_c120e9f26ebb6159adf9 | succeeded | agent_result:succeeded |
| 01KYHW5710RZHZ6RPTYKEGH9JB | security_research | security_2c779e81c27b78c556bb | succeeded | agent_result:succeeded |
| 01KYHW5710WGW08Q1BA7KTM2W5 | security_research | security_66cdcf90aac0d83e76f3 | succeeded | agent_result:succeeded |
| 01KYHW5710WP98V55QRM5RBXSQ | security_research | security_cc4dcb8f002b61dffe00 | succeeded | agent_result:succeeded |
| 01KYHW5710YVB0Z61AF9G5XS4X | security_research | security_8472507d7d320aa388a7 | succeeded | agent_result:succeeded |
| 01KYHW57102CCNPR5A5GNX8WVG | relationship_research | relationship_def43e5b4e13577e2b99 | succeeded | agent_result:succeeded |
| 01KYHW57102ZB98NS7QHW3JSD9 | relationship_research | relationship_297f9e36fb4e93a808e8 | succeeded | agent_result:succeeded |
| 01KYHW57104SC0RP9HX81QSW7K | relationship_research | relationship_d9c8f578040386a487be | succeeded | agent_result:succeeded |
| 01KYHW57105JV3P74FXN3P4HZ6 | relationship_research | relationship_871e21ff73620ab8eb14 | succeeded | agent_result:succeeded |
| 01KYHW5710BWYZSZ0Z4ASMB8EM | relationship_research | relationship_ad2f37b49980dbc73a08 | succeeded | agent_result:succeeded |
| 01KYHW5710C90D1S5BAXB10915 | relationship_research | relationship_510158d3d515d91d5c14 | succeeded | agent_result:succeeded |
| 01KYHW5710DS9JV64CJDQBVCMV | relationship_research | relationship_392da6d90e7c969945a2 | succeeded | agent_result:succeeded |
| 01KYHW5710GZWDV54QMTWS2159 | relationship_research | relationship_3570e003fd90cd83d26f | skipped | agent_result:skipped |
| 01KYHW5710HN9JVFYSCM4C3KKT | relationship_research | relationship_9e7b4700174908755cbc | succeeded | agent_result:succeeded |
| 01KYHW5710J70PNSC8E3ET3904 | relationship_research | relationship_7e9fd9486e494dd05bb5 | succeeded | agent_result:succeeded |
| 01KYHW5710K4BSCNVNKX25GXD9 | relationship_research | relationship_e5f55616b9beaf661080 | succeeded | agent_result:succeeded |
| 01KYHW5710KX0AQTGA5359Y5WF | relationship_research | relationship_1655ac715c33506ec7da | succeeded | agent_result:succeeded |
| 01KYHW5710MA7RMCX7VSSRBN3W | relationship_research | relationship_f2efab6050df0edcb762 | succeeded | agent_result:succeeded |
| 01KYHW5710NPPFPFY0HTDAME01 | relationship_research | relationship_87b95f713a902d531f2f | succeeded | agent_result:succeeded |
| 01KYHW5710QM7X1WMPT8PR0MTQ | relationship_research | relationship_228f56aa5d91f3688b67 | succeeded | agent_result:succeeded |
| 01KYHW5710RH631A9AKFJ8KRGG | relationship_research | relationship_c829dae21648bb133cc7 | succeeded | agent_result:succeeded |
| 01KYHW5710S59C4PZQJD9311NB | relationship_research | relationship_9773364a04293a4febaf | succeeded | agent_result:succeeded |
| 01KYHW5710VH8HSMT8N209A500 | relationship_research | relationship_250194f6a9e3a1817632 | succeeded | agent_result:succeeded |
| 01KYHW5710X7RTKPR6BKG7S9YA | relationship_research | relationship_afac7205cd7e09800edf | succeeded | agent_result:succeeded |
| 01KYHW5710Y3GNPD64A26Y4GF4 | relationship_research | relationship_670ed88c8e4616316a19 | succeeded | agent_result:succeeded |
| 01KYHW5710YS6ZF4HJTWXCZ0X8 | relationship_research | relationship_cbdd07edda84994325d6 | succeeded | agent_result:succeeded |
| 01KYHW5710ZHRS9ZVRME3SGQC5 | relationship_research | relationship_9befaccc50d8cd94372b | succeeded | agent_result:succeeded |
| 01KYJ375G06AA8K2J4SVCQZED7 | wiki_ingest | source_960b91fa563fb8a926b9 | succeeded | agent_result:succeeded |
| 01KYJ375G07WRVDAAGCMTAMJAX | wiki_ingest | source_5392f8ab153edf73d1e7 | succeeded | agent_result:succeeded |
| 01KYJ375G0AV63H4YP5TXQN6QM | wiki_ingest | source_1272c9af68af3c39b32e | succeeded | agent_result:succeeded |
| 01KYJ375G0CK6TQJZ3Y927QK2P | wiki_ingest | source_88641b43d89ee178051e | succeeded | agent_result:succeeded |
| 01KYJ375G0GN464TRX7KH9748R | wiki_ingest | source_e4822bd4b442ff51063d | succeeded | agent_result:succeeded |
| 01KYJ375G0QD57AA4FJQ9FEQC8 | wiki_ingest | source_fae2a4af713687d5cc2b | succeeded | agent_result:succeeded |
| 01KYJ375G0T6R7K6CFXQ41FRK3 | wiki_ingest | source_d73911b42ea0e59df247 | succeeded | agent_result:succeeded |
| 01KYJ375G0WMPK21QK0P3N740K | wiki_ingest | source_41b6971c55327a48da17 | succeeded | agent_result:succeeded |
| 01KYJ375G0WQ2JSDXYADZJ3P0Y | wiki_ingest | source_ec7e0dc0a1e4897e9ed2 | succeeded | agent_result:succeeded |
| 01KYJNRAY85KVM8GXJ9NBBJPP1 | wiki_ingest | source_e5d2d85e77932d3bf56d | succeeded | agent_result:succeeded |
| 01KYJNRAY8GX0YQRMN752801GZ | wiki_ingest | source_8b43e53b8703087510ef | succeeded | agent_result:succeeded |
| 01KYK9KN0RA5MF0NY9H8SNC0HM | relationship_research | relationship_7e9fd9486e494dd05bb5 | skipped | agent_result:skipped |
| 01KYK9KN0REKGW54MN71Z4RMGM | relationship_research | relationship_392da6d90e7c969945a2 | skipped | agent_result:skipped |
| 01KYJRBRVRYF8A87DQ7ERPBEKX | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYJSHDY8XP7DQBKQZ0Y89VB8 | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYJW8TT88FABWWEA768FAY5W | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYJYXWG0MJ1AW4PRHTNPDJVJ | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYK1HXYGF3WFHK55J80E59WB | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYK4GBE0GRKW530MT8BDY0CD | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYK6THERRQJDKVS4XTWX4D7M | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYK810X0752BWF8DVGBN4PXS | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYK9JPR0ZFYN74ZZCE6RT3FY | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYKB6WNG7WAMZKVY6K54WRMA | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYKCWS90GEN33QFG13GAAQJD | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYKEAYT8J6HYFAKKJ12YBKGV | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYKFK3Z8WCHDCG6N64EAXZXT | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYKGVZK0MJCCSVCD4AFCG735 | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYKJ3DA01SRSXFKEBYV85X4S | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | agent_result:skipped |
| 01KYKK7AQ89YCHPG5CQFWYR6E5 | strategy_research | strategy_bd005fc3733b1475b6f9 | succeeded | agent_result:succeeded |
| 01KYHYBWR02F32H3VYKHJWJS2S | opportunity_research | opportunity_0985d882fffd8547f839 | skipped | superseded_indicator_transition |
| 01KYKMN5GRRR06EH04KA07V2N9 | execute_strategy | strategy_bd005fc3733b1475b6f9 | skipped | superseded_allocation_plan:allocation_plan_02b52e8899b55922bf4e |
| 01KYKMV10R0ZW502NKJCHQQ29V | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | superseded_allocation_plan:allocation_plan_02b52e8899b55922bf4e |
| 01KYKQ6E3G6E39783E8DV18W0Q | strategy_research | strategy_bd005fc3733b1475b6f9 | succeeded | agent_result:succeeded |
| 01KYKS86K8A5F4K0QD1XCN4A0Z | execute_strategy | strategy_bd005fc3733b1475b6f9 | skipped | signal_not_ready:cancelled |
| 01KYKTZJ2R6F2WMM32BEJV3A1B | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | superseded_allocation_plan:allocation_plan_02b52e8899b55922bf4e |
| 01KYKV4N5G1PN472NXJR651SYK | execute_strategy | strategy_bd005fc3733b1475b6f9 | succeeded | agent_result:succeeded |
| 01KYKVJX78J2EE4VMWVGHJBAQZ | strategy_research | strategy_bd005fc3733b1475b6f9 | skipped | contract_instructions_corrected |
| 01KYKWP08RY8ST1TENJRN7EY4A | strategy_research | strategy_bd005fc3733b1475b6f9 | succeeded | agent_result:succeeded |
| 01KYKX54MRDBWHGFKQERB0YG2Q | execute_strategy | strategy_bd005fc3733b1475b6f9 | succeeded | agent_result:succeeded |

### Complete active queue

- `waiting` `01KYEWGWBRV9EV6YN1WQA6G3WF` — `security_research` for `security_cb88f9154cfeaa15e878`
- `waiting` `01KYEXAGNREGCP02XCC9VBV80V` — `security_research` for `security_c5a9e460d3350284d157`
- `waiting` `01KYFXFKB04HSHKYVSPNGXVJX0` — `security_research` for `security_66cdcf90aac0d83e76f3`

### Open issues and delivery failures

No open issues.

### Machine decision provenance

- `validated_open_actions` — Validated opening paper actions are pending.
- `allocation_targets`: `a62682fb14bc8e3a349309e479d38bff28d6e74946562f29bfeeace9fc37702d`
- `cash_ledger`: `01818c9c63f8b80fdf927abba96e6553d53e28f4e491dcc0201a06f4f4cbc8d1`
- `configuration`: `6bfbcfa74f10e7c26fb5d945f6c4e0e7748c06714ce07d22e70a46ae67973c83`
- `csv_contracts`: `006db7fd09c8f810fa6b0be26cd8e4dbd772b3f76b60957660c996d239f16115`
- `decision_schema`: `af6b26a6dbd262948e4e20bb45ac0f948268dcd7d2e761e5942bdd1b2cd6c68b`
- `executions`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `fx_aud_eur`: `864a5a889ba1a00e99f4452c13d1e13aa2e8ccd07dbd4a51a3d6a67826bb42c4`
- `fx_gbp_eur`: `ed630d4aa0575ebc9b49dc47600b307b562f4da85553806e46844cd83c520ba5`
- `fx_usd_eur`: `cca01ec6551258350b6a1c1d4ca1a2c1a42a0b6573c0d80aa526f7b1149f7a1d`
- `indicators`: `8441fa114ec18bccef932641d54ccb02daf2f94fb899ee6d7b73f20edb62c690`
- `issues`: `8ec08e226e3adc256c1afbbc66dd9773ccd1f8f1be6e93366b9440fbc5e7bb20`
- `market_latest`: `41e1bae1941968c1f65af4de19c5fcb696549e2f98e01c9f651cd66f74f4f204`
- `operation_payloads`: `00e32e40137900a693883f13341b3f68f81fddceb8a1da5abbd09a04db8537db`
- `operations_history`: `ab5bf9fdc4f85d9732b9e0807f3ad64e44e86ad0615359708ee4d7d1fabe6c16`
- `operations_todo`: `10605ca428fb9d5289d8b2a504f94b74987a7ba4dd24f56e037196142f8e8c96`
- `order_legs`: `3512aeb3a497f47ab696f3794bd08b84fbf86957e471550449c0a70530347040`
- `orders`: `d0f2ee8739f8fa1dc4bc541d3afc4e2ff1ec0257c65bb748e905adfbcd6e1a34`
- `performance_daily`: `81ec42c1bc37f53e0efe95e0b4784faf3c6ff024d1858f72221b88cc1d6feca9`
- `portfolio`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `relationships`: `392b56955048368279eb1b760300ca93ba0f7a7c6f1589a9fe99c844f0d1601a`
- `runs`: `11b94a564cf1fa5eada1283b3406c7dc008592afe184bcd9b1acaa62a7c4b35b`
- `securities`: `27755cada53d56b9ed13aed460c0d021d6cc19566d10f959e3219c2094e7294c`
- `security_assessments`: `ac28c0f6ae59647dfebf00489148b564aa804429d6957bfd2b09a2d865b3820e`
- `signals`: `b0ba7fe72e4ae3dcc4d4aa432b31d631ac633135add41d1d8ea563a652b86a78`
- `source_registry`: `44ba7eb17462647c3506226c6c827e801aa15c47d05cdf64820a1f611b2c1299`
- `strategies`: `3dfcfa54d1fe8a5464bba5f679a7f297c80b6590d65566f5739434919d5ebf67`
- `strategy_legs`: `c814365d6571e84fc619f0905e14a9b7671dd7e312222d4505c732719d26dddf`
- `wiki_inbox`: `760500710233a0493a99d2fffd33aaafff6d9f5e5d417bedb204e14cb514448e`

### Links

- [[index|Investor dashboard]]
- [[model-portfolio|Model portfolio]]
- [[signals|Signals]]
- [[system-status|System status]]
- GitHub report: https://github.com/kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260728.md

---
title: "PaperTrader daily report — 2026-07-27"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-27"
updated: "2026-07-27"
provenance: deterministic-report-generator
run_id: "local-20260727-daily-all-07"
snapshot_id: "decision_92141fd14fdcbfd70916"
---

# PaperTrader daily report — 2026-07-27

## 1. Investor decision summary

<!-- papertrader-investor-brief:start -->
# No trade — hold 100% cash

- **Data status:** Degraded — review coverage and data gaps
- **As of:** `2026-07-27T23:35:28Z`
- **Snapshot:** `decision_92141fd14fdcbfd70916`
- **Cash:** 100000 EUR (100%)
- **Gross exposure:** 0 EUR
- **Approved target cash:** 100000 EUR (100%)
- **Actionable signals:** 0

## Approved target changes

No approved target changes.

## Actionable signals

No actionable trade signals.

## Top blocker or near miss

- **ISRG — Intuitive Surgical, Inc.:** The eligible set is not sufficiently diversified.
<!-- papertrader-investor-brief:end -->

### Deterministic reasons

- The reconciled model portfolio is entirely cash.
- No strategy has produced a current actionable trade signal.

## 2. Model portfolio and approved changes

- Current equity: 100000 EUR
- Current cash: 100000 EUR (100%)
- Current gross exposure: 0 EUR
- Approved target cash: 100000 EUR (100%)
- Pending-order targets are estimates at the snapshot mark; only fills change accounting.

| Holding | Sleeve | Current weight | Approved target | Current value | Target value | Action | State |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Cash | cash | 100% | 100% | 100000  | 100000  | No trade | No action |

## 3. Actionable signals and pending orders

No actionable trade signals.

No pending paper orders.

## 4. Candidates and near misses

| Candidate | State | Score | Base upside | Main reason |
| --- | --- | ---: | ---: | --- |
| [ISRG — Intuitive Surgical, Inc.](securities/security_1f9cce545ede94cd6349) | Risk blocked | 63 | 2.5% | The eligible set is not sufficiently diversified. |
| [GEV — GE Vernova Inc.](securities/security_4b61970aa8f574446819) | Valuation unattractive | 42.8 | 1.9% | A current accepted idea-to-security relationship is unavailable. |
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

- Coinbase is a medium-confidence ineligible security: stablecoin growth and positive operating cash flow support the rails thesis, but trading cyclicality, a GAAP loss, concentration, custody obligations, dilution, and unsupported valuation prevent allocation eligibility; no conviction strategy was queued. Evidence: `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1679788/000167978826000054/coin-20260331.htm`, `https://www.sec.gov/Archives/edgar/data/1679788/000167978826000080/coin-20260722.htm`.
- Rocket Lab is a medium-confidence baseline near miss: Q1 revenue, backlog, gross margin, balance-sheet liquidity, and trading liquidity are strong enough for comparison, but the USD 66.94 mark stands far above the USD 13.87 downside and USD 28.83 base scenario values, while Neutron, cash burn, dilution, concentration, and the pending relationship review block conviction treatment. Evidence: `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1819994/000181999426000028/rklb-20260331.htm`.
- Enphase Energy remains a medium-confidence watch but is currently ineligible for allocation: net-cash resilience, positive Q1 cash generation, and liquid trading do not overcome contracting US sell-through, policy-timed revenue, tariffs, poor pre-results timing, and the absence of a supportable downside-aware valuation. Evidence: `Current comparable assessment`, `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1463101/000146310126000047/enph-20260331.htm`.
- Recursion Pharmaceuticals is currently ineligible for allocation: early clinical milestones and runway into early 2028 do not overcome continued losses, likely capital needs, dilution, low confidence, and the absence of a supportable risk-adjusted pipeline valuation. Evidence: `Current comparable assessment`, `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1601830/000160183026000078/rxrx-20260331.htm`.
- Eaton is a medium-confidence baseline near miss: electrical demand, margins, positive operating cash flow, and liquidity are strengths, but acquisition leverage and concentration remain risks, while the USD 398.64 mark stands above the USD 248.64 downside and USD 320.00 base scenario values. Evidence: `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1551182/000155118226000013/etn-20260331.htm`.

- [[inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-3a01ce587bee]]
- [[inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-9327af26235b]]
- [[inbox/market-security_4627aea1bf7d8943d3d8-rsi_oversold-e0b5f3290c6e]]
- [[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-7a832eb2d5ae]]
- [[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-c288bb87ff70]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-22069206cbf5]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-c4c8f0b60fc6]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-fac3019c4101]]
- [[inbox/market-security_66cdcf90aac0d83e76f3-rsi_oversold-c65ee3726752]]
- [[inbox/market-security_cc4dcb8f002b61dffe00-bollinger_below_lower-8276293d6517]]
- [[inbox/market-security_f2b9760d847b2ba59324-bollinger_below_lower-48b7e8fa112e]]
- [[inbox/market-security_fb87fac302a5446a1ced-rsi_oversold-97348588c910]]
- [[model-portfolio]]
- [[performance]]
- [[relationships/relationship_3570e003fd90cd83d26f]]
- [[research-catalog]]
- [[securities/security_18a3ab0ee6086ee85d0f]]
- [[securities/security_1c055eb9b2bb1f5a8ff2]]
- [[securities/security_1f9cce545ede94cd6349]]
- [[securities/security_37ddcbdaad296ad831f2]]
- [[securities/security_4627aea1bf7d8943d3d8]]
- [[securities/security_4b61970aa8f574446819]]
- [[securities/security_6f9a1450edceb9307c9a]]
- [[securities/security_7ca095d63423c55a90e3]]
- [[securities/security_a9eb9838940ef5ceaa0c]]
- [[securities/security_bdc2f87dadf134760c3a]]
- [[securities/security_c9a37d277445869a8809]]
- [[securities/security_ed7d5b616a196969c815]]
- [[securities/security_f2b9760d847b2ba59324]]
- [[signals]]
- [[system-status]]

## 7. Data-quality and coverage impact

- Data status: **degraded**
- Assessments: 13/24
- Fresh-evidence assessments: 13/24
- Current accepted relationships: 4/24
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market-data success/failure: 24/0
- Research alerts (not trade signals): 14

No current system impacts.

## 8. Audit appendix

### Run diagnostics

- Run ID: `local-20260727-daily-all-07`
- Run status: `succeeded`
- Generated (UTC): `2026-07-27T23:35:28Z`
- Decision snapshot: `decision_92141fd14fdcbfd70916`

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
| — | — | — | no orders | — |

| Execution ID | Order ID | Security ID | Side | Quantity | Fill | Fees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| — | — | — | — | 0 | no executions | 0 |

### Allocation audit

- Plan ID: `allocation_plan_1b9fa357487bb93ccaab`
- Mode: `active`
- Deployment budget: 15000 EUR
- Capital allocated: 2196.574068502268102832154989 EUR
- Capital unallocated: 57803.42593149773189716784501 EUR

| Rank | Security ID | Target weight | Disposition | Machine reasons |
| ---: | --- | ---: | --- | --- |
| 1 | security_1f9cce545ede94cd6349 | 2.2% | open | above_cash_hurdle\|insufficient_diversification |
| — | security_18a3ab0ee6086ee85d0f | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_1c055eb9b2bb1f5a8ff2 | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_22c2b9d782a62d7a9b86 | 0% | excluded | assessment_missing |
| — | security_2c779e81c27b78c556bb | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_2dbe878dfc899d7ee867 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_37ddcbdaad296ad831f2 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_4627aea1bf7d8943d3d8 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:accounting_uncertain,solvency_risk,valuation_unsupported\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_4b61970aa8f574446819 | 0% | excluded | relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_59304f90c440def31dc5 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_66cdcf90aac0d83e76f3 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_6ad1af8d10d6276a0221 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_6f9a1450edceb9307c9a | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_7ca095d63423c55a90e3 | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_8472507d7d320aa388a7 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_9d4049ed6669a52815d6 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_a9eb9838940ef5ceaa0c | 0% | excluded | score_below_cash_hurdle |
| — | security_bdc2f87dadf134760c3a | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_c120e9f26ebb6159adf9 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_c9a37d277445869a8809 | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_cc4dcb8f002b61dffe00 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_ed7d5b616a196969c815 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:valuation_unsupported\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_f2b9760d847b2ba59324 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_fb87fac302a5446a1ced | 0% | excluded | assessment_missing\|relationship_missing_or_stale |

### Research-operation audit

| Operation ID | Type | Entity ID | Disposition | Machine reason |
| --- | --- | --- | --- | --- |
| 01KYHW571007ZFM5FZV8G4M1W4 | security_research | security_1f9cce545ede94cd6349 | succeeded | agent_result:succeeded |
| 01KYHYBWR02MKG5ZAA14RJA67V | opportunity_research | opportunity_a43652ddf2bcb897b05e | skipped | freshness_cooldown:01KYFWWE20EZTW3FG97T7RH499 |
| 01KYHYBWR0T5ZYN0Q2J4MJWX3X | opportunity_research | opportunity_faaa156712c5800ea197 | skipped | freshness_cooldown:01KYFWWE20571YGGDAV45A1F68 |
| 01KYHYBWR00D5T9ND9VBJPW9F7 | opportunity_research | opportunity_1c07342ea13d0d8dc54b | succeeded | agent_result:succeeded |
| 01KYHW57100KA2CGTK6S88B8BQ | security_research | security_c9a37d277445869a8809 | succeeded | agent_result:succeeded |
| 01KYJMQ5DGT37XMDQPFJ4Q6KPT | security_research | security_18a3ab0ee6086ee85d0f | skipped | semantic_merge:01KYHW5710FSY7A9Y5NMEBG9AD:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGJ5CA6M2570DDWHJR | security_research | security_1c055eb9b2bb1f5a8ff2 | skipped | semantic_merge:01KYHW57105B8KTZJRX0B57X1T:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG8Q27ES49NXRNSNC4 | security_research | security_22c2b9d782a62d7a9b86 | skipped | semantic_merge:01KYHW5710QRVPBXMBAY8GAWDM:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG1VF51QQ8BV8AK0X5 | security_research | security_2c779e81c27b78c556bb | skipped | semantic_merge:01KYHW5710RZHZ6RPTYKEGH9JB:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGZ6R10VZYDA67Z6TG | security_research | security_2dbe878dfc899d7ee867 | skipped | semantic_merge:01KYHW5710HN1HFEQB9TRTX6S2:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG4SXWWFYWASYWHCED | security_research | security_37ddcbdaad296ad831f2 | skipped | semantic_merge:01KYHW57107CVMKHT24J77V9RA:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG1X7GRAJHRNK4ATG9 | security_research | security_4627aea1bf7d8943d3d8 | skipped | semantic_merge:01KYHW57107AC3EW2ZRC9BZKMR:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGSV08ARAM6RTZVHDG | security_research | security_4b61970aa8f574446819 | skipped | semantic_merge:01KYHW57103C5W6MMF3SR497D7:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG0YRFYJ06YA1JXX48 | security_research | security_59304f90c440def31dc5 | skipped | semantic_merge:01KYHW5710M89EMQMNDY940EKH:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGB4MDG4CAQ2CKHE2C | security_research | security_66cdcf90aac0d83e76f3 | skipped | semantic_merge:01KYHW5710WGW08Q1BA7KTM2W5:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGXXR19KAAF593X9SN | security_research | security_6ad1af8d10d6276a0221 | skipped | semantic_merge:01KYHW5710FXAD3C0SE0K34K90:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGDH89FP70EQEDXDNA | security_research | security_6f9a1450edceb9307c9a | skipped | semantic_merge:01KYHW57105SVXPKV0ES1M1H13:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGXVP7PM18JYNFSF02 | security_research | security_7ca095d63423c55a90e3 | skipped | semantic_merge:01KYHW5710B851YNG53P4YQZW6:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG0N7Q73VZV57GBFGQ | security_research | security_8472507d7d320aa388a7 | skipped | semantic_merge:01KYHW5710YVB0Z61AF9G5XS4X:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGK7QF98E9F7HJVDY9 | security_research | security_9d4049ed6669a52815d6 | skipped | semantic_merge:01KYHW5710QD07N3J66DEV37C1:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGZ1XZRJB0C739N11V | security_research | security_a9eb9838940ef5ceaa0c | skipped | semantic_merge:01KYHW57103NJ31X4TRFP7SD3D:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGZSDR4T45T586V63C | security_research | security_bdc2f87dadf134760c3a | skipped | semantic_merge:01KYHW57101205S02R9SC1YWG7:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGC670NPDBYANQMWWE | security_research | security_c120e9f26ebb6159adf9 | skipped | semantic_merge:01KYHW5710RKVS0S8HF233BBTR:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGMTTJX2KYNW3WM4WR | security_research | security_cc4dcb8f002b61dffe00 | skipped | semantic_merge:01KYHW5710WP98V55QRM5RBXSQ:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGPXXVX75A1MZB4CTC | security_research | security_ed7d5b616a196969c815 | skipped | semantic_merge:01KYHW5710ENZ9WVA185W24RGA:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGFYE964F2B0NK7CX2 | security_research | security_f2b9760d847b2ba59324 | skipped | semantic_merge:01KYHW5710EB6CDPT0EF3CX9MM:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG6ZHJNAKKZM1EWC01 | security_research | security_fb87fac302a5446a1ced | skipped | semantic_merge:01KYHW5710GCKR1DK8EH3ECASN:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGCZ6YXJB2NC4VNBWQ | relationship_research | relationship_87b95f713a902d531f2f | skipped | semantic_merge:01KYHW5710NPPFPFY0HTDAME01:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGDCK93YKX582HA8C2 | relationship_research | relationship_392da6d90e7c969945a2 | skipped | semantic_merge:01KYHW5710DS9JV64CJDQBVCMV:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGF1YN5AEP8Z0Y5YAG | relationship_research | relationship_510158d3d515d91d5c14 | skipped | semantic_merge:01KYHW5710C90D1S5BAXB10915:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGBM6CHWRSMBHB5EMA | relationship_research | relationship_def43e5b4e13577e2b99 | skipped | semantic_merge:01KYHW57102CCNPR5A5GNX8WVG:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGD3T1RGWAW74B6JWA | relationship_research | relationship_f2efab6050df0edcb762 | skipped | semantic_merge:01KYHW5710MA7RMCX7VSSRBN3W:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG3M20E3KC0TRJQ8BG | relationship_research | relationship_670ed88c8e4616316a19 | skipped | semantic_merge:01KYHW5710Y3GNPD64A26Y4GF4:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGSPRR0K58Y6Y0Q05S | relationship_research | relationship_cbdd07edda84994325d6 | skipped | semantic_merge:01KYHW5710YS6ZF4HJTWXCZ0X8:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGEJZQPNBSFCXAEJGP | relationship_research | relationship_1655ac715c33506ec7da | skipped | semantic_merge:01KYHW5710KX0AQTGA5359Y5WF:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGNM3CYDJ8G7YDCFHS | relationship_research | relationship_871e21ff73620ab8eb14 | skipped | semantic_merge:01KYHW57105JV3P74FXN3P4HZ6:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG10N3ZZCYZJS2DY3X | relationship_research | relationship_9befaccc50d8cd94372b | skipped | semantic_merge:01KYHW5710ZHRS9ZVRME3SGQC5:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGMHAV5FGGF47X2H7P | relationship_research | relationship_e5f55616b9beaf661080 | skipped | semantic_merge:01KYHW5710K4BSCNVNKX25GXD9:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG1YZRGAE1J9D8AMXJ | relationship_research | relationship_297f9e36fb4e93a808e8 | skipped | semantic_merge:01KYHW57102ZB98NS7QHW3JSD9:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG2KCYZ9QXJTS51SB0 | relationship_research | relationship_228f56aa5d91f3688b67 | skipped | semantic_merge:01KYHW5710QM7X1WMPT8PR0MTQ:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGG22GTT4WYM29SQGZ | relationship_research | relationship_9773364a04293a4febaf | skipped | semantic_merge:01KYHW5710S59C4PZQJD9311NB:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGXWPZVNJY0FKNNV1V | relationship_research | relationship_250194f6a9e3a1817632 | skipped | semantic_merge:01KYHW5710VH8HSMT8N209A500:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGHPAV1WBKZSC8XWQJ | relationship_research | relationship_afac7205cd7e09800edf | skipped | semantic_merge:01KYHW5710X7RTKPR6BKG7S9YA:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGTYZ3GD4KQPM3W0JS | relationship_research | relationship_7e9fd9486e494dd05bb5 | skipped | semantic_merge:01KYHW5710J70PNSC8E3ET3904:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG3N8V46WVTB1989Q6 | relationship_research | relationship_c829dae21648bb133cc7 | skipped | semantic_merge:01KYHW5710RH631A9AKFJ8KRGG:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGQ22JT58QPK35C5QK | relationship_research | relationship_9e7b4700174908755cbc | skipped | semantic_merge:01KYHW5710HN9JVFYSCM4C3KKT:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DGVHXBBW4Z9K5S2SSB | relationship_research | relationship_ad2f37b49980dbc73a08 | skipped | semantic_merge:01KYHW5710BWYZSZ0Z4ASMB8EM:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJNRAY8Q06M0ZSGE26MF1AE | opportunity_research | opportunity_774ef4e748390c70d9a9 | skipped | freshness_cooldown:01KYFWWE20VFS02GS517HNPRB7 |
| 01KYJMQ5DG45HKS1DT01QB8X4N | security_research | security_c9a37d277445869a8809 | succeeded | agent_result:succeeded |
| 01KYJMQ5DGT0HRARBP4GVJTC0X | relationship_research | relationship_d9c8f578040386a487be | skipped | semantic_merge:01KYHW57104SC0RP9HX81QSW7K:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG5AB3XJP4VWQJZS8S | security_research | security_1f9cce545ede94cd6349 | succeeded | agent_result:succeeded |
| 01KYJMQ5DG3GHE5SE79GNY4DSH | relationship_research | relationship_3570e003fd90cd83d26f | skipped | semantic_merge:01KYHW5710GZWDV54QMTWS2159:Equivalent active allocation maintenance objective for the same immutable entity. |
| 01KYJMQ5DG5M4WTHXVSN42HYHJ | relationship_research | relationship_solar_storage_grid_atkr | skipped | agent_result:skipped |
| 01KYJMQ5DGD4PR1C190FE8PMM6 | relationship_research | relationship_solar_storage_grid_enph | skipped | agent_result:skipped |
| 01KYJMQ5DGE5Q6M13H1GD369F1 | relationship_research | relationship_solar_storage_grid_flnc | skipped | agent_result:skipped |
| 01KYJNRAY8BZJ53TFC3XS4EKHW | opportunity_research | opportunity_3a7d63385ab5f180d2ad | succeeded | agent_result:succeeded |
| 01KYHW57101205S02R9SC1YWG7 | security_research | security_bdc2f87dadf134760c3a | succeeded | agent_result:succeeded |
| 01KYHW57103C5W6MMF3SR497D7 | security_research | security_4b61970aa8f574446819 | succeeded | agent_result:succeeded |
| 01KYHW57103NJ31X4TRFP7SD3D | security_research | security_a9eb9838940ef5ceaa0c | succeeded | agent_result:succeeded |
| 01KYHW57105B8KTZJRX0B57X1T | security_research | security_1c055eb9b2bb1f5a8ff2 | succeeded | agent_result:succeeded |
| 01KYHW57105SVXPKV0ES1M1H13 | security_research | security_6f9a1450edceb9307c9a | succeeded | agent_result:succeeded |
| 01KYHW57107AC3EW2ZRC9BZKMR | security_research | security_4627aea1bf7d8943d3d8 | succeeded | agent_result:succeeded |
| 01KYHW57107CVMKHT24J77V9RA | security_research | security_37ddcbdaad296ad831f2 | succeeded | agent_result:succeeded |
| 01KYHW5710B851YNG53P4YQZW6 | security_research | security_7ca095d63423c55a90e3 | succeeded | agent_result:succeeded |
| 01KYHW5710EB6CDPT0EF3CX9MM | security_research | security_f2b9760d847b2ba59324 | succeeded | agent_result:succeeded |
| 01KYHW5710ENZ9WVA185W24RGA | security_research | security_ed7d5b616a196969c815 | succeeded | agent_result:succeeded |
| 01KYHW5710FSY7A9Y5NMEBG9AD | security_research | security_18a3ab0ee6086ee85d0f | succeeded | agent_result:succeeded |

### Complete active queue

- `waiting` `01KYEWGWBRV9EV6YN1WQA6G3WF` — `security_research` for `security_cb88f9154cfeaa15e878`
- `waiting` `01KYEXAGNREGCP02XCC9VBV80V` — `security_research` for `security_c5a9e460d3350284d157`
- `waiting` `01KYFXFKB04HSHKYVSPNGXVJX0` — `security_research` for `security_66cdcf90aac0d83e76f3`
- `ready` `01KYHW5710NPPFPFY0HTDAME01` — `relationship_research` for `relationship_87b95f713a902d531f2f`
- `ready` `01KYHW5710DS9JV64CJDQBVCMV` — `relationship_research` for `relationship_392da6d90e7c969945a2`
- `ready` `01KYHW5710GZWDV54QMTWS2159` — `relationship_research` for `relationship_3570e003fd90cd83d26f`
- `ready` `01KYHW5710QRVPBXMBAY8GAWDM` — `security_research` for `security_22c2b9d782a62d7a9b86`
- `ready` `01KYHW5710RZHZ6RPTYKEGH9JB` — `security_research` for `security_2c779e81c27b78c556bb`
- `waiting` `01KYHW5710C90D1S5BAXB10915` — `relationship_research` for `relationship_510158d3d515d91d5c14`
- `ready` `01KYHW5710HN1HFEQB9TRTX6S2` — `security_research` for `security_2dbe878dfc899d7ee867`
- `waiting` `01KYHW57102CCNPR5A5GNX8WVG` — `relationship_research` for `relationship_def43e5b4e13577e2b99`
- `ready` `01KYHW5710MA7RMCX7VSSRBN3W` — `relationship_research` for `relationship_f2efab6050df0edcb762`
- `ready` `01KYHW5710Y3GNPD64A26Y4GF4` — `relationship_research` for `relationship_670ed88c8e4616316a19`
- `ready` `01KYHW5710YS6ZF4HJTWXCZ0X8` — `relationship_research` for `relationship_cbdd07edda84994325d6`
- `ready` `01KYHW5710M89EMQMNDY940EKH` — `security_research` for `security_59304f90c440def31dc5`
- `waiting` `01KYHW5710KX0AQTGA5359Y5WF` — `relationship_research` for `relationship_1655ac715c33506ec7da`
- `ready` `01KYHW5710WGW08Q1BA7KTM2W5` — `security_research` for `security_66cdcf90aac0d83e76f3`
- `waiting` `01KYHW57105JV3P74FXN3P4HZ6` — `relationship_research` for `relationship_871e21ff73620ab8eb14`
- `ready` `01KYHW5710FXAD3C0SE0K34K90` — `security_research` for `security_6ad1af8d10d6276a0221`
- `waiting` `01KYHW5710ZHRS9ZVRME3SGQC5` — `relationship_research` for `relationship_9befaccc50d8cd94372b`
- `ready` `01KYHW5710K4BSCNVNKX25GXD9` — `relationship_research` for `relationship_e5f55616b9beaf661080`
- `ready` `01KYHW57102ZB98NS7QHW3JSD9` — `relationship_research` for `relationship_297f9e36fb4e93a808e8`
- `ready` `01KYHW5710YVB0Z61AF9G5XS4X` — `security_research` for `security_8472507d7d320aa388a7`
- `waiting` `01KYHW5710QM7X1WMPT8PR0MTQ` — `relationship_research` for `relationship_228f56aa5d91f3688b67`
- `ready` `01KYHW5710QD07N3J66DEV37C1` — `security_research` for `security_9d4049ed6669a52815d6`
- `waiting` `01KYHW5710S59C4PZQJD9311NB` — `relationship_research` for `relationship_9773364a04293a4febaf`
- `ready` `01KYHW5710VH8HSMT8N209A500` — `relationship_research` for `relationship_250194f6a9e3a1817632`
- `ready` `01KYHW5710RKVS0S8HF233BBTR` — `security_research` for `security_c120e9f26ebb6159adf9`
- `waiting` `01KYHW5710X7RTKPR6BKG7S9YA` — `relationship_research` for `relationship_afac7205cd7e09800edf`
- `ready` `01KYHW57104SC0RP9HX81QSW7K` — `relationship_research` for `relationship_d9c8f578040386a487be`
- `ready` `01KYHW5710WP98V55QRM5RBXSQ` — `security_research` for `security_cc4dcb8f002b61dffe00`
- `waiting` `01KYHW5710J70PNSC8E3ET3904` — `relationship_research` for `relationship_7e9fd9486e494dd05bb5`
- `ready` `01KYHW5710RH631A9AKFJ8KRGG` — `relationship_research` for `relationship_c829dae21648bb133cc7`
- `ready` `01KYHW5710HN9JVFYSCM4C3KKT` — `relationship_research` for `relationship_9e7b4700174908755cbc`
- `ready` `01KYHW5710GCKR1DK8EH3ECASN` — `security_research` for `security_fb87fac302a5446a1ced`
- `waiting` `01KYHW5710BWYZSZ0Z4ASMB8EM` — `relationship_research` for `relationship_ad2f37b49980dbc73a08`
- `blocked` `01KYHYBWR02F32H3VYKHJWJS2S` — `opportunity_research` for `opportunity_0985d882fffd8547f839`
- `ready` `01KYJ375G0AV63H4YP5TXQN6QM` — `wiki_ingest` for `source_1272c9af68af3c39b32e`
- `ready` `01KYJ375G0WMPK21QK0P3N740K` — `wiki_ingest` for `source_41b6971c55327a48da17`
- `ready` `01KYJ375G0CK6TQJZ3Y927QK2P` — `wiki_ingest` for `source_88641b43d89ee178051e`
- `ready` `01KYJ375G0T6R7K6CFXQ41FRK3` — `wiki_ingest` for `source_d73911b42ea0e59df247`
- `ready` `01KYJ375G07WRVDAAGCMTAMJAX` — `wiki_ingest` for `source_5392f8ab153edf73d1e7`
- `ready` `01KYJ375G0GN464TRX7KH9748R` — `wiki_ingest` for `source_e4822bd4b442ff51063d`
- `ready` `01KYJ375G06AA8K2J4SVCQZED7` — `wiki_ingest` for `source_960b91fa563fb8a926b9`
- `ready` `01KYJ375G0WQ2JSDXYADZJ3P0Y` — `wiki_ingest` for `source_ec7e0dc0a1e4897e9ed2`
- `ready` `01KYJ375G0QD57AA4FJQ9FEQC8` — `wiki_ingest` for `source_fae2a4af713687d5cc2b`
- `ready` `01KYJNRAY85KVM8GXJ9NBBJPP1` — `wiki_ingest` for `source_e5d2d85e77932d3bf56d`
- `ready` `01KYJNRAY8GX0YQRMN752801GZ` — `wiki_ingest` for `source_8b43e53b8703087510ef`
- `ready` `01KYJRBRVRYF8A87DQ7ERPBEKX` — `strategy_research` for `strategy_bd005fc3733b1475b6f9`
- `ready` `01KYJSHDY8XP7DQBKQZ0Y89VB8` — `strategy_research` for `strategy_bd005fc3733b1475b6f9`
- `ready` `01KYJW8TT88FABWWEA768FAY5W` — `strategy_research` for `strategy_bd005fc3733b1475b6f9`
- `ready` `01KYJYXWG0MJ1AW4PRHTNPDJVJ` — `strategy_research` for `strategy_bd005fc3733b1475b6f9`

### Open issues and delivery failures

No open issues.

### Machine decision provenance

- `portfolio_all_cash` — The reconciled model portfolio is entirely cash.
- `no_actionable_signals` — No strategy has produced a current actionable trade signal.
- `allocation_targets`: `ca5a6379ed262db6bfa99a6b7fec714dda8eed958008292660348139a6d21dc0`
- `cash_ledger`: `01818c9c63f8b80fdf927abba96e6553d53e28f4e491dcc0201a06f4f4cbc8d1`
- `configuration`: `6bfbcfa74f10e7c26fb5d945f6c4e0e7748c06714ce07d22e70a46ae67973c83`
- `csv_contracts`: `006db7fd09c8f810fa6b0be26cd8e4dbd772b3f76b60957660c996d239f16115`
- `decision_schema`: `af6b26a6dbd262948e4e20bb45ac0f948268dcd7d2e761e5942bdd1b2cd6c68b`
- `executions`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `fx_aud_eur`: `864a5a889ba1a00e99f4452c13d1e13aa2e8ccd07dbd4a51a3d6a67826bb42c4`
- `fx_gbp_eur`: `ed630d4aa0575ebc9b49dc47600b307b562f4da85553806e46844cd83c520ba5`
- `fx_usd_eur`: `cca01ec6551258350b6a1c1d4ca1a2c1a42a0b6573c0d80aa526f7b1149f7a1d`
- `indicators`: `8441fa114ec18bccef932641d54ccb02daf2f94fb899ee6d7b73f20edb62c690`
- `issues`: `31255ef1ab4783f62d8e37cd1608266b741a5cb75929e155cd6c2c5e45bfb457`
- `market_latest`: `41e1bae1941968c1f65af4de19c5fcb696549e2f98e01c9f651cd66f74f4f204`
- `operation_payloads`: `d71b1be0c90a09a8467fda8c3d7d19d0d96dba283d89e010db270f5c96de48bd`
- `operations_history`: `f2e6c8983768ef47279eea13e38541205674cc1c857275456628c36706b4494e`
- `operations_todo`: `28e57963564e929fcae30edb7c4227a9dfee3cdf73a0342061103f20cf35d1a5`
- `order_legs`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `orders`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `performance_daily`: `b7a3e9cf94d74dc28d2fb51f7ccc1f232ed25a6b3a4f823f7f92d1b5e73463d8`
- `portfolio`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `relationships`: `ebb7c43e2334e97ec06974ddca9f06f1710d5fa4015e31df94e9336554319e23`
- `runs`: `e8b733f8d33df2ab99dce4f8ba9d4b4a237b0fb1814741ad14971dfb93286866`
- `securities`: `43903638446fa305053e73649919d65305f3dbeb0b861d9e36435108729ff755`
- `security_assessments`: `26e28f13dba6df4c44f037e4326e4d82b06b90cc984742eb2fe16d2dc1754b13`
- `signals`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `source_registry`: `2d2d30d766dfec23070e44588eb658bee4e118d45b693662d2ff81c0f3d0f27d`
- `strategies`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `strategy_legs`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `wiki_inbox`: `760500710233a0493a99d2fffd33aaafff6d9f5e5d417bedb204e14cb514448e`

### Links

- [[index|Investor dashboard]]
- [[model-portfolio|Model portfolio]]
- [[signals|Signals]]
- [[system-status|System status]]
- GitHub report: https://github.com/Kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260727.md

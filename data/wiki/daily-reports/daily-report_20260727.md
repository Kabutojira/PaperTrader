---
title: "PaperTrader daily report — 2026-07-27"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-27"
updated: "2026-07-27"
provenance: deterministic-report-generator
run_id: "gha-30280283355-1"
snapshot_id: "decision_7eae4d9fa5380e578266"
---

# PaperTrader daily report — 2026-07-27

## 1. Investor decision summary

<!-- papertrader-investor-brief:start -->
# No trade — hold 100% cash

- **Data status:** Degraded — review coverage and data gaps
- **As of:** `2026-07-27T15:39:59Z`
- **Snapshot:** `decision_7eae4d9fa5380e578266`
- **Cash:** 100000 EUR (100%)
- **Gross exposure:** 0 EUR
- **Approved target cash:** 100000 EUR (100%)
- **Actionable signals:** 0

## Approved target changes

No approved target changes.

## Actionable signals

No actionable trade signals.

## Top blocker or near miss

- **ISRG — Intuitive Surgical, Inc.:** A current accepted idea-to-security relationship is unavailable.
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
| [ISRG — Intuitive Surgical, Inc.](securities/security_1f9cce545ede94cd6349) | Relationship research pending | 66 | 8.8% | A current accepted idea-to-security relationship is unavailable. |
| [RBLX — Roblox Corporation](securities/security_c9a37d277445869a8809) | Valuation unattractive | 30.6 | -18.4% | The assessed base case has no positive upside. |

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

- Roblox has a medium-confidence baseline assessment but is uncompetitive with cash: a bounded 12-month scenario indicates 46.9% downside and 18.4% base-case downside from the current mark, while safety headwinds and dilution remain material. Evidence: `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1315098/000162828026028882/ex991-q12026earningsshar.htm`.

- [[inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-3a01ce587bee]]
- [[inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-9327af26235b]]
- [[inbox/market-security_4627aea1bf7d8943d3d8-rsi_oversold-e0b5f3290c6e]]
- [[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-7a832eb2d5ae]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-22069206cbf5]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-fac3019c4101]]
- [[inbox/market-security_66cdcf90aac0d83e76f3-rsi_oversold-c65ee3726752]]
- [[inbox/market-security_f2b9760d847b2ba59324-bollinger_below_lower-48b7e8fa112e]]
- [[inbox/market-security_fb87fac302a5446a1ced-rsi_oversold-97348588c910]]
- [[model-portfolio]]
- [[performance]]
- [[research-catalog]]
- [[securities/security_1f9cce545ede94cd6349]]
- [[securities/security_c9a37d277445869a8809]]
- [[securities/security_f2b9760d847b2ba59324]]
- [[signals]]
- [[system-status]]

## 7. Data-quality and coverage impact

- Data status: **degraded**
- Assessments: 2/24
- Fresh-evidence assessments: 2/24
- Current accepted relationships: 3/24
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market-data success/failure: 22/2
- Research alerts (not trade signals): 9

### Current system impacts

- **affects candidate** — FCX Freeport-McMoRan Inc.: Daily preparation degraded: security\_2dbe878dfc899d7ee867
- **affects candidate** — SQM Sociedad Quimica y Minera de Chile S.A.: Daily preparation degraded: security\_9d4049ed6669a52815d6
- **publication only**: Telegram delivery failed: 798017b585f7de9127a798eb52aac52052f72786
- **publication only**: Telegram delivery failed: d3c816d22ba7ec5bb52ac8278b8f231f68dace74

## 8. Audit appendix

### Run diagnostics

- Run ID: `gha-30280283355-1`
- Run status: `degraded`
- Generated (UTC): `2026-07-27T15:39:59Z`
- Decision snapshot: `decision_7eae4d9fa5380e578266`

### Complete market freshness

| Security ID | Price date | Retrieved at | Status | Error |
| --- | --- | --- | --- | --- |
| security_18a3ab0ee6086ee85d0f | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_1c055eb9b2bb1f5a8ff2 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_1f9cce545ede94cd6349 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_22c2b9d782a62d7a9b86 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_2c779e81c27b78c556bb | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_2dbe878dfc899d7ee867 | 2026-07-24 | 2026-07-27T22:30:44Z | error | MarketDataError: invalid OHLC range on 2026-07-27 for security_2dbe878dfc899d7ee867 |
| security_37ddcbdaad296ad831f2 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_4627aea1bf7d8943d3d8 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_4b61970aa8f574446819 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_59304f90c440def31dc5 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_66cdcf90aac0d83e76f3 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_6ad1af8d10d6276a0221 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_6f9a1450edceb9307c9a | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_7ca095d63423c55a90e3 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_8472507d7d320aa388a7 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_9d4049ed6669a52815d6 | 2026-07-24 | 2026-07-27T22:30:44Z | error | MarketDataError: invalid OHLC range on 2026-07-27 for security_9d4049ed6669a52815d6 |
| security_a9eb9838940ef5ceaa0c | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_bdc2f87dadf134760c3a | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_c120e9f26ebb6159adf9 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_c9a37d277445869a8809 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_cc4dcb8f002b61dffe00 | 2026-07-27 | 2026-07-27T22:30:44Z | error | MarketDataError: invalid OHLC range on 2026-07-27 for security_cc4dcb8f002b61dffe00 |
| security_ed7d5b616a196969c815 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_f2b9760d847b2ba59324 | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |
| security_fb87fac302a5446a1ced | 2026-07-27 | 2026-07-27T22:30:44Z | ok | — |

### Orders and executions

| Order ID | Strategy ID | Fill policy | Status | Created |
| --- | --- | --- | --- | --- |
| — | — | — | no orders | — |

| Execution ID | Order ID | Security ID | Side | Quantity | Fill | Fees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| — | — | — | — | 0 | no executions | 0 |

### Allocation audit

- Plan ID: `allocation_plan_dd60c33245e32ae29a71`
- Mode: `active`
- Deployment budget: 15000 EUR
- Capital allocated: 0 EUR
- Capital unallocated: 60000 EUR

| Rank | Security ID | Target weight | Disposition | Machine reasons |
| ---: | --- | ---: | --- | --- |
| — | security_18a3ab0ee6086ee85d0f | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_1c055eb9b2bb1f5a8ff2 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_1f9cce545ede94cd6349 | 0% | excluded | relationship_missing_or_stale |
| — | security_22c2b9d782a62d7a9b86 | 0% | excluded | assessment_missing |
| — | security_2c779e81c27b78c556bb | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_2dbe878dfc899d7ee867 | 0% | excluded | assessment_missing\|market_data_not_ok\|relationship_missing_or_stale |
| — | security_37ddcbdaad296ad831f2 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_4627aea1bf7d8943d3d8 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_4b61970aa8f574446819 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_59304f90c440def31dc5 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_66cdcf90aac0d83e76f3 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_6ad1af8d10d6276a0221 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_6f9a1450edceb9307c9a | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_7ca095d63423c55a90e3 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_8472507d7d320aa388a7 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_9d4049ed6669a52815d6 | 0% | excluded | assessment_missing\|market_data_not_ok\|relationship_missing_or_stale |
| — | security_a9eb9838940ef5ceaa0c | 0% | excluded | assessment_missing |
| — | security_bdc2f87dadf134760c3a | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_c120e9f26ebb6159adf9 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_c9a37d277445869a8809 | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle |
| — | security_cc4dcb8f002b61dffe00 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_ed7d5b616a196969c815 | 0% | excluded | assessment_missing\|relationship_missing_or_stale |
| — | security_f2b9760d847b2ba59324 | 0% | excluded | assessment_missing |
| — | security_fb87fac302a5446a1ced | 0% | excluded | assessment_missing\|relationship_missing_or_stale |

### Research-operation audit

| Operation ID | Type | Entity ID | Disposition | Machine reason |
| --- | --- | --- | --- | --- |
| 01KYHW571007ZFM5FZV8G4M1W4 | security_research | security_1f9cce545ede94cd6349 | succeeded | agent_result:succeeded |
| 01KYHYBWR02MKG5ZAA14RJA67V | opportunity_research | opportunity_a43652ddf2bcb897b05e | skipped | freshness_cooldown:01KYFWWE20EZTW3FG97T7RH499 |
| 01KYHYBWR0T5ZYN0Q2J4MJWX3X | opportunity_research | opportunity_faaa156712c5800ea197 | skipped | freshness_cooldown:01KYFWWE20571YGGDAV45A1F68 |
| 01KYHYBWR00D5T9ND9VBJPW9F7 | opportunity_research | opportunity_1c07342ea13d0d8dc54b | succeeded | agent_result:succeeded |
| 01KYHW57100KA2CGTK6S88B8BQ | security_research | security_c9a37d277445869a8809 | succeeded | agent_result:succeeded |
| 01KYJV7BH0Q06M0ZSGE26MF1AE | opportunity_research | opportunity_774ef4e748390c70d9a9 | skipped | freshness_cooldown:01KYFWWE20VFS02GS517HNPRB7 |
| 01KYHW57101205S02R9SC1YWG7 | security_research | security_bdc2f87dadf134760c3a | succeeded | agent_result:succeeded |
| 01KYHW57103C5W6MMF3SR497D7 | security_research | security_4b61970aa8f574446819 | succeeded | agent_result:succeeded |
| 01KYHW57103NJ31X4TRFP7SD3D | security_research | security_a9eb9838940ef5ceaa0c | succeeded | agent_result:succeeded |
| 01KYHW57105B8KTZJRX0B57X1T | security_research | security_1c055eb9b2bb1f5a8ff2 | succeeded | agent_result:succeeded |
| 01KYHW57105SVXPKV0ES1M1H13 | security_research | security_6f9a1450edceb9307c9a | succeeded | agent_result:succeeded |

### Complete active queue

- `waiting` `01KYEWGWBRV9EV6YN1WQA6G3WF` — `security_research` for `security_cb88f9154cfeaa15e878`
- `waiting` `01KYEXAGNREGCP02XCC9VBV80V` — `security_research` for `security_c5a9e460d3350284d157`
- `waiting` `01KYFXFKB04HSHKYVSPNGXVJX0` — `security_research` for `security_66cdcf90aac0d83e76f3`
- `ready` `01KYHW5710FSY7A9Y5NMEBG9AD` — `security_research` for `security_18a3ab0ee6086ee85d0f`
- `waiting` `01KYHW5710NPPFPFY0HTDAME01` — `relationship_research` for `relationship_87b95f713a902d531f2f`
- `ready` `01KYHW57105B8KTZJRX0B57X1T` — `security_research` for `security_1c055eb9b2bb1f5a8ff2`
- `waiting` `01KYHW5710DS9JV64CJDQBVCMV` — `relationship_research` for `relationship_392da6d90e7c969945a2`
- `ready` `01KYHW5710GZWDV54QMTWS2159` — `relationship_research` for `relationship_3570e003fd90cd83d26f`
- `ready` `01KYHW5710QRVPBXMBAY8GAWDM` — `security_research` for `security_22c2b9d782a62d7a9b86`
- `ready` `01KYHW5710RZHZ6RPTYKEGH9JB` — `security_research` for `security_2c779e81c27b78c556bb`
- `waiting` `01KYHW5710C90D1S5BAXB10915` — `relationship_research` for `relationship_510158d3d515d91d5c14`
- `ready` `01KYHW5710HN1HFEQB9TRTX6S2` — `security_research` for `security_2dbe878dfc899d7ee867`
- `waiting` `01KYHW57102CCNPR5A5GNX8WVG` — `relationship_research` for `relationship_def43e5b4e13577e2b99`
- `ready` `01KYHW57107CVMKHT24J77V9RA` — `security_research` for `security_37ddcbdaad296ad831f2`
- `waiting` `01KYHW5710MA7RMCX7VSSRBN3W` — `relationship_research` for `relationship_f2efab6050df0edcb762`
- `ready` `01KYHW57107AC3EW2ZRC9BZKMR` — `security_research` for `security_4627aea1bf7d8943d3d8`
- `waiting` `01KYHW5710Y3GNPD64A26Y4GF4` — `relationship_research` for `relationship_670ed88c8e4616316a19`
- `ready` `01KYHW57103C5W6MMF3SR497D7` — `security_research` for `security_4b61970aa8f574446819`
- `waiting` `01KYHW5710YS6ZF4HJTWXCZ0X8` — `relationship_research` for `relationship_cbdd07edda84994325d6`
- `ready` `01KYHW5710M89EMQMNDY940EKH` — `security_research` for `security_59304f90c440def31dc5`
- `waiting` `01KYHW5710KX0AQTGA5359Y5WF` — `relationship_research` for `relationship_1655ac715c33506ec7da`
- `ready` `01KYHW5710WGW08Q1BA7KTM2W5` — `security_research` for `security_66cdcf90aac0d83e76f3`
- `waiting` `01KYHW57105JV3P74FXN3P4HZ6` — `relationship_research` for `relationship_871e21ff73620ab8eb14`
- `ready` `01KYHW5710FXAD3C0SE0K34K90` — `security_research` for `security_6ad1af8d10d6276a0221`
- `waiting` `01KYHW5710ZHRS9ZVRME3SGQC5` — `relationship_research` for `relationship_9befaccc50d8cd94372b`
- `ready` `01KYHW57105SVXPKV0ES1M1H13` — `security_research` for `security_6f9a1450edceb9307c9a`
- `waiting` `01KYHW5710K4BSCNVNKX25GXD9` — `relationship_research` for `relationship_e5f55616b9beaf661080`
- `ready` `01KYHW5710B851YNG53P4YQZW6` — `security_research` for `security_7ca095d63423c55a90e3`
- `waiting` `01KYHW57102ZB98NS7QHW3JSD9` — `relationship_research` for `relationship_297f9e36fb4e93a808e8`
- `ready` `01KYHW5710YVB0Z61AF9G5XS4X` — `security_research` for `security_8472507d7d320aa388a7`
- `waiting` `01KYHW5710QM7X1WMPT8PR0MTQ` — `relationship_research` for `relationship_228f56aa5d91f3688b67`
- `ready` `01KYHW5710QD07N3J66DEV37C1` — `security_research` for `security_9d4049ed6669a52815d6`
- `waiting` `01KYHW5710S59C4PZQJD9311NB` — `relationship_research` for `relationship_9773364a04293a4febaf`
- `ready` `01KYHW57103NJ31X4TRFP7SD3D` — `security_research` for `security_a9eb9838940ef5ceaa0c`
- `ready` `01KYHW57101205S02R9SC1YWG7` — `security_research` for `security_bdc2f87dadf134760c3a`
- `waiting` `01KYHW5710VH8HSMT8N209A500` — `relationship_research` for `relationship_250194f6a9e3a1817632`
- `ready` `01KYHW5710RKVS0S8HF233BBTR` — `security_research` for `security_c120e9f26ebb6159adf9`
- `waiting` `01KYHW5710X7RTKPR6BKG7S9YA` — `relationship_research` for `relationship_afac7205cd7e09800edf`
- `ready` `01KYHW57104SC0RP9HX81QSW7K` — `relationship_research` for `relationship_d9c8f578040386a487be`
- `ready` `01KYHW5710WP98V55QRM5RBXSQ` — `security_research` for `security_cc4dcb8f002b61dffe00`
- `waiting` `01KYHW5710J70PNSC8E3ET3904` — `relationship_research` for `relationship_7e9fd9486e494dd05bb5`
- `ready` `01KYHW5710ENZ9WVA185W24RGA` — `security_research` for `security_ed7d5b616a196969c815`
- `waiting` `01KYHW5710RH631A9AKFJ8KRGG` — `relationship_research` for `relationship_c829dae21648bb133cc7`
- `waiting` `01KYHW5710HN9JVFYSCM4C3KKT` — `relationship_research` for `relationship_9e7b4700174908755cbc`
- `ready` `01KYHW5710EB6CDPT0EF3CX9MM` — `security_research` for `security_f2b9760d847b2ba59324`
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

### Open issues and delivery failures

- `warning` **`issue_1681e7daa698c45f8006`** — Daily preparation degraded: security\_2dbe878dfc899d7ee867: security\_2dbe878dfc899d7ee867: MarketDataError: invalid OHLC range on 2026-07-27 for security\_2dbe878dfc899d7ee867
- `warning` **`issue_7c3336b8354d9c076ebc`** — Telegram delivery failed: 798017b585f7de9127a798eb52aac52052f72786: report=data/wiki/daily-reports/daily-report\_20260727.md commit=798017b585f7de9127a798eb52aac52052f72786 next\_chunk=0 total\_chunks=6 error=Telegram HTTP 401: {"ok":false,"error\_code":401,"description":"Unauthorized"}
- `warning` **`issue_9141a7a5538fd458f54f`** — Telegram delivery failed: d3c816d22ba7ec5bb52ac8278b8f231f68dace74: report=data/wiki/daily-reports/daily-report\_20260724.md commit=d3c816d22ba7ec5bb52ac8278b8f231f68dace74 next\_chunk=0 total\_chunks=2 error=Telegram HTTP 401: {"ok":false,"error\_code":401,"description":"Unauthorized"}
- `warning` **`issue_9b4cbf2dec47a2d5f28b`** — Daily preparation degraded: security\_9d4049ed6669a52815d6: security\_9d4049ed6669a52815d6: MarketDataError: invalid OHLC range on 2026-07-27 for security\_9d4049ed6669a52815d6

### Machine decision provenance

- `portfolio_all_cash` — The reconciled model portfolio is entirely cash.
- `no_actionable_signals` — No strategy has produced a current actionable trade signal.
- `allocation_targets`: `84d611c0e7302ad45e4af8963d1f151f22cf40ed5c4069dff0702c8fa05d2b87`
- `cash_ledger`: `01818c9c63f8b80fdf927abba96e6553d53e28f4e491dcc0201a06f4f4cbc8d1`
- `configuration`: `6bfbcfa74f10e7c26fb5d945f6c4e0e7748c06714ce07d22e70a46ae67973c83`
- `csv_contracts`: `006db7fd09c8f810fa6b0be26cd8e4dbd772b3f76b60957660c996d239f16115`
- `decision_schema`: `af6b26a6dbd262948e4e20bb45ac0f948268dcd7d2e761e5942bdd1b2cd6c68b`
- `executions`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `fx_aud_eur`: `a76d737b7096aa9ed1053791f4fd628fcf37dba796e4ccea1c73926bc5817bd6`
- `fx_gbp_eur`: `46d428f9eeb172fd5e03fe57755faf25343f1edf95cc1efc2292217042aa4ca0`
- `fx_usd_eur`: `9d516e4bf482cf2bf8ea57b37a61537038ca76d1a694ee6a1ad2958618e33466`
- `indicators`: `6f9f8c0ee5c780621ca460d61dc845d5d2f0eb7a0fa588bd93e572d247ce94fb`
- `issues`: `e41846993063327262728b4d413f1fcc94fae852e1fe1596382a87f0a240fd05`
- `market_latest`: `308ee173a9a42628137097021444e71397e6793d03f4ab612189198436e0af31`
- `operation_payloads`: `ca932e1497ce845e16b92dbf551e134dca439e9e087f2faaa9338ed955987d94`
- `operations_history`: `5718a5ef527174a173a9a65bc5204a7adc4eb1f68573cf5eee06f054be1416b0`
- `operations_todo`: `fd3aecf44e6263125f7d3ee1f62fb97aff394ee47a8d6d9d7c17c488e4ad5082`
- `order_legs`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `orders`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `performance_daily`: `b7a3e9cf94d74dc28d2fb51f7ccc1f232ed25a6b3a4f823f7f92d1b5e73463d8`
- `portfolio`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `relationships`: `3660e84d77bb6fa7dd2a1cabdc9d4fa3151ef8b90a86d6102dc2e6e9f6668c3d`
- `runs`: `7e3070dca4956bb8237856d63f127c96e2eac15fa6670086dd99fd2f60452ac3`
- `securities`: `b5c8bda251af356c5d09f700de2952417fe561f873565c90653e33ee2e7c797b`
- `security_assessments`: `a39d2084f6a88de8cd202980ae7835ddc87859f433df06a2f94fac9c3334286f`
- `signals`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `source_registry`: `26e2918e27cfae3daf0d22ecc32d528c07363924172c390503bf5d5c41f51d89`
- `strategies`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `strategy_legs`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `wiki_inbox`: `759b16a08ce60f887a20b5190e75d1c98d77476c0b472073116539873791be87`

### Links

- [[index|Investor dashboard]]
- [[model-portfolio|Model portfolio]]
- [[signals|Signals]]
- [[system-status|System status]]
- GitHub report: https://github.com/kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260727.md

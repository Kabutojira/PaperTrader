---
title: "PaperTrader daily report — 2026-07-27"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-27"
updated: "2026-07-27"
provenance: deterministic-report-generator
run_id: "gha-30273371484-1"
---

# PaperTrader daily report — 2026-07-27

## 1. Run status and data freshness

- Run: `gha-30273371484-1`
- Status: `degraded`
- Generated (UTC): `2026-07-27T14:12:11Z`

| Security | Price date | Retrieved at | Status | Error |
| --- | --- | --- | --- | --- |
| security_18a3ab0ee6086ee85d0f | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_1c055eb9b2bb1f5a8ff2 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_1f9cce545ede94cd6349 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_22c2b9d782a62d7a9b86 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_2c779e81c27b78c556bb | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_2dbe878dfc899d7ee867 | 2026-07-24 | 2026-07-27T14:06:24Z | error | MarketDataError: invalid OHLC range on 2026-07-27 for security_2dbe878dfc899d7ee867 |
| security_37ddcbdaad296ad831f2 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_4627aea1bf7d8943d3d8 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_4b61970aa8f574446819 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_59304f90c440def31dc5 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_66cdcf90aac0d83e76f3 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_6ad1af8d10d6276a0221 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_6f9a1450edceb9307c9a | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_7ca095d63423c55a90e3 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_8472507d7d320aa388a7 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_9d4049ed6669a52815d6 | 2026-07-24 | 2026-07-27T14:06:24Z | error | MarketDataError: invalid OHLC range on 2026-07-27 for security_9d4049ed6669a52815d6 |
| security_a9eb9838940ef5ceaa0c | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_bdc2f87dadf134760c3a | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_c120e9f26ebb6159adf9 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_c9a37d277445869a8809 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_cc4dcb8f002b61dffe00 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_ed7d5b616a196969c815 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_f2b9760d847b2ba59324 | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |
| security_fb87fac302a5446a1ced | 2026-07-24 | 2026-07-27T14:06:24Z | ok | — |

## 2. Orders and executions

### Orders created

| Order | Strategy | Policy | Status | Created |
| --- | --- | --- | --- | --- |
| — | — | — | no orders | — |

### Executions

| Execution | Order | Security | Side | Quantity | Fill | Fees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| — | — | — | — | 0 | no executions | 0 |

## 3. Current portfolio, cash, exposure, and P/L

- Cash: 100000 EUR
- Equity: 100000 EUR
- Gross exposure: 0 EUR
- Net exposure: 0 EUR
- Realized P/L: 0 EUR
- Unrealized P/L: 0 EUR
- Daily return: 0%
- Cumulative return: 0%

| Position | Security | Instrument | Side | Quantity | Mark | Market value (base) | Unrealized P/L |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| — | — | — | — | 0 | — | 0 | 0 |

## 4. Opportunity-cost-aware allocation

- Allocation mode: `active`
- Cash: 100000 EUR
- Minimum cash reserve: 25000 EUR
- Current invested exposure: 0 EUR
- Target invested exposure: 60000 EUR
- Current conviction exposure: 0 EUR
- Current baseline exposure: 0 EUR
- Maximum baseline exposure: 30000 EUR
- Deployment budget: 15000 EUR
- Capital allocated this plan: 0 EUR
- Capital left unallocated: 60000 EUR
- Eligible candidate count: 0
- Excluded candidate count: 24

Cash remains unallocated because: `assessment_missing`, `insufficient_diversification`, `insufficient_eligible_candidates`, `market_data_not_ok`, `relationship_missing_or_stale`

| Rank | Security | Sleeve | Effective score | Current weight | Pending weight | Target weight | Delta | Disposition | Reason | Assessment date |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| — | security_18a3ab0ee6086ee85d0f | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_1c055eb9b2bb1f5a8ff2 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_1f9cce545ede94cd6349 | baseline | 66 | 0% | 0% | 0% | 0 | excluded | relationship_missing_or_stale | 2026-07-27T13:32:49Z |
| — | security_22c2b9d782a62d7a9b86 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing | — |
| — | security_2c779e81c27b78c556bb | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_2dbe878dfc899d7ee867 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|market_data_not_ok\|relationship_missing_or_stale | — |
| — | security_37ddcbdaad296ad831f2 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_4627aea1bf7d8943d3d8 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_4b61970aa8f574446819 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_59304f90c440def31dc5 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_66cdcf90aac0d83e76f3 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_6ad1af8d10d6276a0221 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_6f9a1450edceb9307c9a | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_7ca095d63423c55a90e3 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_8472507d7d320aa388a7 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_9d4049ed6669a52815d6 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|market_data_not_ok\|relationship_missing_or_stale | — |
| — | security_a9eb9838940ef5ceaa0c | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing | — |
| — | security_bdc2f87dadf134760c3a | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_c120e9f26ebb6159adf9 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_c9a37d277445869a8809 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_cc4dcb8f002b61dffe00 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_ed7d5b616a196969c815 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_f2b9760d847b2ba59324 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing | — |
| — | security_fb87fac302a5446a1ced | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |

## 5. Research operations and dispositions

| Operation | Type | Entity | Disposition | Reason |
| --- | --- | --- | --- | --- |
| 01KYHW571007ZFM5FZV8G4M1W4 | security_research | security_1f9cce545ede94cd6349 | succeeded | agent_result:succeeded |
| 01KYHYBWR02MKG5ZAA14RJA67V | opportunity_research | opportunity_a43652ddf2bcb897b05e | skipped | freshness_cooldown:01KYFWWE20EZTW3FG97T7RH499 |
| 01KYHYBWR0T5ZYN0Q2J4MJWX3X | opportunity_research | opportunity_faaa156712c5800ea197 | skipped | freshness_cooldown:01KYFWWE20571YGGDAV45A1F68 |
| 01KYHYBWR00D5T9ND9VBJPW9F7 | opportunity_research | opportunity_1c07342ea13d0d8dc54b | succeeded | agent_result:succeeded |

### Evidence-linked narrative

- Enphase Energy's 22.262229% 25 June–24 July decline and marginal lower-Bollinger breach were classified as risk, not a validated opportunity; current issuer product releases do not explain the move, and queued security revalidation will assess the imminent Q2 evidence. Evidence: `92c3146da6c6940e7d58b99f1f18861956acbac2fcbdcbfbfe909be3e9df0c96`, `data/operations/operations_TODO.csv`, `https://investor.enphase.com/news-releases/news-release-details/enphase-energy-announces-conference-call-review-second-12`, `https://investor.enphase.com/news-releases/news-release-details/enphase-energy-expands-iq9n-microinverters-gan-technology`, `https://investor.enphase.com/news-releases/news-release-details/enphase-energy-highlights-safety-and-reliability-iq-ev-charger-2`, `https://investor.enphase.com/news-releases/news-release-details/enphase-energy-unlocks-backup-and-expandable-storage-existing-iq`.

## 6. New or changed research entities

- [[inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-9327af26235b]]
- [[inbox/market-security_4627aea1bf7d8943d3d8-rsi_oversold-e0b5f3290c6e]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-fac3019c4101]]
- [[inbox/market-security_f2b9760d847b2ba59324-bollinger_below_lower-48b7e8fa112e]]
- [[securities/security_1f9cce545ede94cd6349]]
- [[securities/security_f2b9760d847b2ba59324]]

## 7. Risks, blockers, and scheduled follow-ups

- `warning` **issue_112dbc198a16c17e54e7** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_f2b9760d847b2ba59324-bollinger_below_lower-48b7e8fa112e.md
- `warning` **issue_1681e7daa698c45f8006** — Daily preparation degraded: security_2dbe878dfc899d7ee867
- `warning` **issue_4183021e1363fc3aa642** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-7a832eb2d5ae.md
- `warning` **issue_4b309fbac75c644b6dc5** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_59304f90c440def31dc5-rsi_overbought-fac3019c4101.md
- `warning` **issue_9141a7a5538fd458f54f** — Telegram delivery failed: d3c816d22ba7ec5bb52ac8278b8f231f68dace74
- `warning` **issue_9b4cbf2dec47a2d5f28b** — Daily preparation degraded: security_9d4049ed6669a52815d6
- `warning` **issue_a3c2febb69c6663ae333** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_4627aea1bf7d8943d3d8-rsi_oversold-e0b5f3290c6e.md
- `warning` **issue_b9bb38b0435eee030308** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-3a01ce587bee.md
- `warning` **issue_c035ba6451c092224a7f** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_fb87fac302a5446a1ced-rsi_oversold-97348588c910.md
- `warning` **issue_c74225aa581c50e9a829** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_59304f90c440def31dc5-rsi_overbought-22069206cbf5.md
- `warning` **issue_d759882b3af9c8ff2505** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_66cdcf90aac0d83e76f3-rsi_oversold-c65ee3726752.md
- `warning` **issue_e6aff19b80293e0c91cd** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-9327af26235b.md

### Active operation queue

- `waiting` 01KYEWGWBRV9EV6YN1WQA6G3WF — security_research for `security_cb88f9154cfeaa15e878`
- `waiting` 01KYEXAGNREGCP02XCC9VBV80V — security_research for `security_c5a9e460d3350284d157`
- `waiting` 01KYFXFKB04HSHKYVSPNGXVJX0 — security_research for `security_66cdcf90aac0d83e76f3`
- `ready` 01KYHW5710FSY7A9Y5NMEBG9AD — security_research for `security_18a3ab0ee6086ee85d0f`
- `waiting` 01KYHW5710NPPFPFY0HTDAME01 — relationship_research for `relationship_87b95f713a902d531f2f`
- `ready` 01KYHW57105B8KTZJRX0B57X1T — security_research for `security_1c055eb9b2bb1f5a8ff2`
- `waiting` 01KYHW5710DS9JV64CJDQBVCMV — relationship_research for `relationship_392da6d90e7c969945a2`
- `ready` 01KYHW5710GZWDV54QMTWS2159 — relationship_research for `relationship_3570e003fd90cd83d26f`
- `ready` 01KYHW5710QRVPBXMBAY8GAWDM — security_research for `security_22c2b9d782a62d7a9b86`
- `ready` 01KYHW5710RZHZ6RPTYKEGH9JB — security_research for `security_2c779e81c27b78c556bb`
- `waiting` 01KYHW5710C90D1S5BAXB10915 — relationship_research for `relationship_510158d3d515d91d5c14`
- `ready` 01KYHW5710HN1HFEQB9TRTX6S2 — security_research for `security_2dbe878dfc899d7ee867`
- `waiting` 01KYHW57102CCNPR5A5GNX8WVG — relationship_research for `relationship_def43e5b4e13577e2b99`
- `ready` 01KYHW57107CVMKHT24J77V9RA — security_research for `security_37ddcbdaad296ad831f2`
- `waiting` 01KYHW5710MA7RMCX7VSSRBN3W — relationship_research for `relationship_f2efab6050df0edcb762`
- `ready` 01KYHW57107AC3EW2ZRC9BZKMR — security_research for `security_4627aea1bf7d8943d3d8`
- `waiting` 01KYHW5710Y3GNPD64A26Y4GF4 — relationship_research for `relationship_670ed88c8e4616316a19`
- `ready` 01KYHW57103C5W6MMF3SR497D7 — security_research for `security_4b61970aa8f574446819`
- `waiting` 01KYHW5710YS6ZF4HJTWXCZ0X8 — relationship_research for `relationship_cbdd07edda84994325d6`
- `ready` 01KYHW5710M89EMQMNDY940EKH — security_research for `security_59304f90c440def31dc5`
- `waiting` 01KYHW5710KX0AQTGA5359Y5WF — relationship_research for `relationship_1655ac715c33506ec7da`
- `ready` 01KYHW5710WGW08Q1BA7KTM2W5 — security_research for `security_66cdcf90aac0d83e76f3`
- `waiting` 01KYHW57105JV3P74FXN3P4HZ6 — relationship_research for `relationship_871e21ff73620ab8eb14`
- `ready` 01KYHW5710FXAD3C0SE0K34K90 — security_research for `security_6ad1af8d10d6276a0221`
- `waiting` 01KYHW5710ZHRS9ZVRME3SGQC5 — relationship_research for `relationship_9befaccc50d8cd94372b`
- `ready` 01KYHW57105SVXPKV0ES1M1H13 — security_research for `security_6f9a1450edceb9307c9a`
- `waiting` 01KYHW5710K4BSCNVNKX25GXD9 — relationship_research for `relationship_e5f55616b9beaf661080`
- `ready` 01KYHW5710B851YNG53P4YQZW6 — security_research for `security_7ca095d63423c55a90e3`
- `waiting` 01KYHW57102ZB98NS7QHW3JSD9 — relationship_research for `relationship_297f9e36fb4e93a808e8`
- `ready` 01KYHW5710YVB0Z61AF9G5XS4X — security_research for `security_8472507d7d320aa388a7`
- `waiting` 01KYHW5710QM7X1WMPT8PR0MTQ — relationship_research for `relationship_228f56aa5d91f3688b67`
- `ready` 01KYHW5710QD07N3J66DEV37C1 — security_research for `security_9d4049ed6669a52815d6`
- `waiting` 01KYHW5710S59C4PZQJD9311NB — relationship_research for `relationship_9773364a04293a4febaf`
- `ready` 01KYHW57103NJ31X4TRFP7SD3D — security_research for `security_a9eb9838940ef5ceaa0c`
- `ready` 01KYHW57101205S02R9SC1YWG7 — security_research for `security_bdc2f87dadf134760c3a`
- `waiting` 01KYHW5710VH8HSMT8N209A500 — relationship_research for `relationship_250194f6a9e3a1817632`
- `ready` 01KYHW5710RKVS0S8HF233BBTR — security_research for `security_c120e9f26ebb6159adf9`
- `waiting` 01KYHW5710X7RTKPR6BKG7S9YA — relationship_research for `relationship_afac7205cd7e09800edf`
- `ready` 01KYHW57100KA2CGTK6S88B8BQ — security_research for `security_c9a37d277445869a8809`
- `waiting` 01KYHW57104SC0RP9HX81QSW7K — relationship_research for `relationship_d9c8f578040386a487be`
- `ready` 01KYHW5710WP98V55QRM5RBXSQ — security_research for `security_cc4dcb8f002b61dffe00`
- `waiting` 01KYHW5710J70PNSC8E3ET3904 — relationship_research for `relationship_7e9fd9486e494dd05bb5`
- `ready` 01KYHW5710ENZ9WVA185W24RGA — security_research for `security_ed7d5b616a196969c815`
- `waiting` 01KYHW5710RH631A9AKFJ8KRGG — relationship_research for `relationship_c829dae21648bb133cc7`
- `waiting` 01KYHW5710HN9JVFYSCM4C3KKT — relationship_research for `relationship_9e7b4700174908755cbc`
- `ready` 01KYHW5710EB6CDPT0EF3CX9MM — security_research for `security_f2b9760d847b2ba59324`
- `ready` 01KYHW5710GCKR1DK8EH3ECASN — security_research for `security_fb87fac302a5446a1ced`
- `waiting` 01KYHW5710BWYZSZ0Z4ASMB8EM — relationship_research for `relationship_ad2f37b49980dbc73a08`
- `ready` 01KYHYBWR02F32H3VYKHJWJS2S — opportunity_research for `opportunity_0985d882fffd8547f839`

## 8. Links

- [[index|Wiki index]]
- GitHub report: https://github.com/Kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260727.md

---
title: "PaperTrader daily report — 2026-07-27"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-27"
updated: "2026-07-27"
provenance: deterministic-report-generator
run_id: "gha-30310927695-1"
---

# PaperTrader daily report — 2026-07-27

## 1. Run status and data freshness

- Run: `gha-30310927695-1`
- Status: `degraded`
- Generated (UTC): `2026-07-27T23:14:02Z`

| Security | Price date | Retrieved at | Status | Error |
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

Cash remains unallocated because: `assessment_ineligible`, `assessment_missing`, `base_upside_not_positive`, `hard_blocker:valuation_unsupported`, `insufficient_diversification`, `insufficient_eligible_candidates`, `market_data_not_ok`, `relationship_missing_or_stale`, `score_below_cash_hurdle`

| Rank | Security | Sleeve | Effective score | Current weight | Pending weight | Target weight | Delta | Disposition | Reason | Assessment date |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| — | security_18a3ab0ee6086ee85d0f | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_1c055eb9b2bb1f5a8ff2 | baseline | 8.2 | 0% | 0% | 0% | 0 | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|relationship_missing_or_stale\|score_below_cash_hurdle | 2026-07-27T23:01:58Z |
| — | security_1f9cce545ede94cd6349 | baseline | 66 | 0% | 0% | 0% | 0 | excluded | relationship_missing_or_stale | 2026-07-27T13:32:49Z |
| — | security_22c2b9d782a62d7a9b86 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing | — |
| — | security_2c779e81c27b78c556bb | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_2dbe878dfc899d7ee867 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|market_data_not_ok\|relationship_missing_or_stale | — |
| — | security_37ddcbdaad296ad831f2 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_4627aea1bf7d8943d3d8 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_4b61970aa8f574446819 | baseline | 45.2 | 0% | 0% | 0% | 0 | excluded | relationship_missing_or_stale\|score_below_cash_hurdle | 2026-07-27T22:42:35Z |
| — | security_59304f90c440def31dc5 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_66cdcf90aac0d83e76f3 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_6ad1af8d10d6276a0221 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_6f9a1450edceb9307c9a | baseline | 38.4 | 0% | 0% | 0% | 0 | excluded | relationship_missing_or_stale\|score_below_cash_hurdle | 2026-07-27T23:11:38Z |
| — | security_7ca095d63423c55a90e3 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_8472507d7d320aa388a7 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_9d4049ed6669a52815d6 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|market_data_not_ok\|relationship_missing_or_stale | — |
| — | security_a9eb9838940ef5ceaa0c | baseline | 16 | 0% | 0% | 0% | 0 | excluded | score_below_cash_hurdle | 2026-07-27T22:53:08Z |
| — | security_bdc2f87dadf134760c3a | baseline | 34.6 | 0% | 0% | 0% | 0 | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle | 2026-07-27T22:36:09Z |
| — | security_c120e9f26ebb6159adf9 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|relationship_missing_or_stale | — |
| — | security_c9a37d277445869a8809 | baseline | 30.6 | 0% | 0% | 0% | 0 | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle | 2026-07-27T15:37:00Z |
| — | security_cc4dcb8f002b61dffe00 | baseline | 0 | 0% | 0% | 0% | 0 | excluded | assessment_missing\|market_data_not_ok\|relationship_missing_or_stale | — |
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
| 01KYHW57100KA2CGTK6S88B8BQ | security_research | security_c9a37d277445869a8809 | succeeded | agent_result:succeeded |
| 01KYJV7BH0Q06M0ZSGE26MF1AE | opportunity_research | opportunity_774ef4e748390c70d9a9 | skipped | freshness_cooldown:01KYFWWE20VFS02GS517HNPRB7 |
| 01KYHW57101205S02R9SC1YWG7 | security_research | security_bdc2f87dadf134760c3a | succeeded | agent_result:succeeded |
| 01KYHW57103C5W6MMF3SR497D7 | security_research | security_4b61970aa8f574446819 | succeeded | agent_result:succeeded |
| 01KYHW57103NJ31X4TRFP7SD3D | security_research | security_a9eb9838940ef5ceaa0c | succeeded | agent_result:succeeded |
| 01KYHW57105B8KTZJRX0B57X1T | security_research | security_1c055eb9b2bb1f5a8ff2 | succeeded | agent_result:succeeded |
| 01KYHW57105SVXPKV0ES1M1H13 | security_research | security_6f9a1450edceb9307c9a | succeeded | agent_result:succeeded |

### Evidence-linked narrative

- Palantir was revalidated with current issuer evidence and a fresh USD 131.53 mark. Exceptional growth and liquidity do not offset valuation: the bounded 12-month downside and base values are USD 58.32 and USD 106.71, so it remains medium-confidence watching with no strategy follow-up. Evidence: `data/market/latest.csv`, `https://www.sec.gov/Archives/edgar/data/1321655/000132165526000026/a2026q1ex991pressrelease.htm`, `https://www.sec.gov/Archives/edgar/data/1321655/000132165526000028/pltr-20260331.htm`.
- GE Vernova was revalidated with current Q2 issuer evidence and a fresh USD 996.57 mark. Record backlog and cash conversion confirm the operating thesis, but the bounded 12-month downside and base values are USD 571.58 and USD 1,016.02, so it remains medium-confidence watching with no conviction strategy follow-up. Evidence: `Bounded 12-month free-cash-flow sensitivity`, `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1996810/000199681026000147/gevpressrelease2q26.htm`, `https://www.sec.gov/Archives/edgar/data/1996810/000199681026000148/gev-20260630.htm`.
- Fluence Energy was revalidated with current fiscal Q2 issuer evidence and a fresh USD 13.51 mark. Backlog confirms direct storage exposure, but thin margins and cash use constrain quality; bounded 12-month downside and base values are USD 7.35 and USD 14.73, so it remains medium-confidence watching with no conviction strategy follow-up. Evidence: `Bounded 12-month revenue sensitivity`, `PaperTrader deterministic market and FX caches`, `https://www.sec.gov/Archives/edgar/data/1868941/000110465926056304/flnc-20260331x10q.htm`, `https://www.sec.gov/Archives/edgar/data/1868941/000186894126000014/flncq2fy26earningspressrel.htm`.
- Rio Tinto was revalidated with current Q2 2026 production evidence and a fresh USD 91.95 ADR mark. Oyu Tolgoi's ramp supports the copper thesis, but diversified exposure, lower Q2 copper output, and pending half-year financials leave valuation unsupported; the current assessment is ineligible and no strategy was queued. Evidence: `Comparable assessment gate`, `PaperTrader deterministic market and FX caches`, `https://www.riotinto.com/en/news/releases/2026/rio-tinto-releases-second-quarter-2026-production-results`.
- Arista Networks was revalidated with current primary evidence and a fresh USD 170.76 mark. Strong AI-networking growth, margins and liquidity do not overcome valuation: bounded 12-month downside and base values are USD 110.81 and USD 174.56, so it remains medium-confidence baseline eligible with no conviction strategy follow-up. Evidence: `data/market/fx/USD_EUR.csv`, `data/market/latest.csv and bounded valuation sensitivity`, `https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2026/Arista-Networks-Inc--Reports-First-Quarter-2026-Financial-Results/default.aspx`, `https://www.sec.gov/Archives/edgar/data/1596532/000159653226000078/anet-20260331.htm`.

## 6. New or changed research entities

- [[inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-3a01ce587bee]]
- [[inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-9327af26235b]]
- [[inbox/market-security_4627aea1bf7d8943d3d8-rsi_oversold-e0b5f3290c6e]]
- [[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-7a832eb2d5ae]]
- [[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-b275f066a05b]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-22069206cbf5]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-a6de68653afb]]
- [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-fac3019c4101]]
- [[inbox/market-security_66cdcf90aac0d83e76f3-rsi_oversold-c65ee3726752]]
- [[inbox/market-security_f2b9760d847b2ba59324-bollinger_below_lower-48b7e8fa112e]]
- [[inbox/market-security_fb87fac302a5446a1ced-rsi_oversold-97348588c910]]
- [[securities/security_1c055eb9b2bb1f5a8ff2]]
- [[securities/security_1f9cce545ede94cd6349]]
- [[securities/security_4b61970aa8f574446819]]
- [[securities/security_6f9a1450edceb9307c9a]]
- [[securities/security_a9eb9838940ef5ceaa0c]]
- [[securities/security_bdc2f87dadf134760c3a]]
- [[securities/security_c9a37d277445869a8809]]
- [[securities/security_f2b9760d847b2ba59324]]

## 7. Risks, blockers, and scheduled follow-ups

- `warning` **issue_1681e7daa698c45f8006** — Daily preparation degraded: security_2dbe878dfc899d7ee867
- `warning` **issue_52fa2eca35c0f0d7f8d0** — Telegram delivery failed: 50e05153546202df24c702aab7f4dd7f20265a5a
- `warning` **issue_7c3336b8354d9c076ebc** — Telegram delivery failed: 798017b585f7de9127a798eb52aac52052f72786
- `warning` **issue_8063efca3ea5402f7588** — Daily preparation degraded: security_cc4dcb8f002b61dffe00
- `warning` **issue_9141a7a5538fd458f54f** — Telegram delivery failed: d3c816d22ba7ec5bb52ac8278b8f231f68dace74
- `warning` **issue_9b4cbf2dec47a2d5f28b** — Daily preparation degraded: security_9d4049ed6669a52815d6

### Active operation queue

- `waiting` 01KYEWGWBRV9EV6YN1WQA6G3WF — security_research for `security_cb88f9154cfeaa15e878`
- `waiting` 01KYEXAGNREGCP02XCC9VBV80V — security_research for `security_c5a9e460d3350284d157`
- `waiting` 01KYFXFKB04HSHKYVSPNGXVJX0 — security_research for `security_66cdcf90aac0d83e76f3`
- `ready` 01KYHW5710FSY7A9Y5NMEBG9AD — security_research for `security_18a3ab0ee6086ee85d0f`
- `waiting` 01KYHW5710NPPFPFY0HTDAME01 — relationship_research for `relationship_87b95f713a902d531f2f`
- `ready` 01KYHW5710DS9JV64CJDQBVCMV — relationship_research for `relationship_392da6d90e7c969945a2`
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
- `ready` 01KYHW5710YS6ZF4HJTWXCZ0X8 — relationship_research for `relationship_cbdd07edda84994325d6`
- `ready` 01KYHW5710M89EMQMNDY940EKH — security_research for `security_59304f90c440def31dc5`
- `waiting` 01KYHW5710KX0AQTGA5359Y5WF — relationship_research for `relationship_1655ac715c33506ec7da`
- `ready` 01KYHW5710WGW08Q1BA7KTM2W5 — security_research for `security_66cdcf90aac0d83e76f3`
- `waiting` 01KYHW57105JV3P74FXN3P4HZ6 — relationship_research for `relationship_871e21ff73620ab8eb14`
- `ready` 01KYHW5710FXAD3C0SE0K34K90 — security_research for `security_6ad1af8d10d6276a0221`
- `waiting` 01KYHW5710ZHRS9ZVRME3SGQC5 — relationship_research for `relationship_9befaccc50d8cd94372b`
- `ready` 01KYHW5710K4BSCNVNKX25GXD9 — relationship_research for `relationship_e5f55616b9beaf661080`
- `ready` 01KYHW5710B851YNG53P4YQZW6 — security_research for `security_7ca095d63423c55a90e3`
- `waiting` 01KYHW57102ZB98NS7QHW3JSD9 — relationship_research for `relationship_297f9e36fb4e93a808e8`
- `ready` 01KYHW5710YVB0Z61AF9G5XS4X — security_research for `security_8472507d7d320aa388a7`
- `waiting` 01KYHW5710QM7X1WMPT8PR0MTQ — relationship_research for `relationship_228f56aa5d91f3688b67`
- `ready` 01KYHW5710QD07N3J66DEV37C1 — security_research for `security_9d4049ed6669a52815d6`
- `waiting` 01KYHW5710S59C4PZQJD9311NB — relationship_research for `relationship_9773364a04293a4febaf`
- `ready` 01KYHW5710VH8HSMT8N209A500 — relationship_research for `relationship_250194f6a9e3a1817632`
- `ready` 01KYHW5710RKVS0S8HF233BBTR — security_research for `security_c120e9f26ebb6159adf9`
- `waiting` 01KYHW5710X7RTKPR6BKG7S9YA — relationship_research for `relationship_afac7205cd7e09800edf`
- `ready` 01KYHW57104SC0RP9HX81QSW7K — relationship_research for `relationship_d9c8f578040386a487be`
- `ready` 01KYHW5710WP98V55QRM5RBXSQ — security_research for `security_cc4dcb8f002b61dffe00`
- `waiting` 01KYHW5710J70PNSC8E3ET3904 — relationship_research for `relationship_7e9fd9486e494dd05bb5`
- `ready` 01KYHW5710ENZ9WVA185W24RGA — security_research for `security_ed7d5b616a196969c815`
- `waiting` 01KYHW5710RH631A9AKFJ8KRGG — relationship_research for `relationship_c829dae21648bb133cc7`
- `waiting` 01KYHW5710HN9JVFYSCM4C3KKT — relationship_research for `relationship_9e7b4700174908755cbc`
- `ready` 01KYHW5710EB6CDPT0EF3CX9MM — security_research for `security_f2b9760d847b2ba59324`
- `ready` 01KYHW5710GCKR1DK8EH3ECASN — security_research for `security_fb87fac302a5446a1ced`
- `waiting` 01KYHW5710BWYZSZ0Z4ASMB8EM — relationship_research for `relationship_ad2f37b49980dbc73a08`
- `blocked` 01KYHYBWR02F32H3VYKHJWJS2S — opportunity_research for `opportunity_0985d882fffd8547f839`
- `ready` 01KYJ375G0AV63H4YP5TXQN6QM — wiki_ingest for `source_1272c9af68af3c39b32e`
- `ready` 01KYJ375G0WMPK21QK0P3N740K — wiki_ingest for `source_41b6971c55327a48da17`
- `ready` 01KYJ375G0CK6TQJZ3Y927QK2P — wiki_ingest for `source_88641b43d89ee178051e`
- `ready` 01KYJ375G0T6R7K6CFXQ41FRK3 — wiki_ingest for `source_d73911b42ea0e59df247`
- `ready` 01KYJ375G07WRVDAAGCMTAMJAX — wiki_ingest for `source_5392f8ab153edf73d1e7`
- `ready` 01KYJ375G0GN464TRX7KH9748R — wiki_ingest for `source_e4822bd4b442ff51063d`
- `ready` 01KYJ375G06AA8K2J4SVCQZED7 — wiki_ingest for `source_960b91fa563fb8a926b9`
- `ready` 01KYJ375G0WQ2JSDXYADZJ3P0Y — wiki_ingest for `source_ec7e0dc0a1e4897e9ed2`
- `ready` 01KYJ375G0QD57AA4FJQ9FEQC8 — wiki_ingest for `source_fae2a4af713687d5cc2b`
- `ready` 01KYJV7BH06VQ7GGR2TWBB4A64 — wiki_ingest for `source_b2d45bca8d0a249be557`
- `ready` 01KYJV7BH02PK4VT3WTS7SQQ61 — wiki_ingest for `source_ad511f12b8de63d3a443`

## 8. Links

- [[index|Wiki index]]
- GitHub report: https://github.com/Kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260727.md

---
title: "PaperTrader daily report — 2026-07-27"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-27"
updated: "2026-07-27"
provenance: deterministic-report-generator
run_id: "local-20260727T092114Z"
---

# PaperTrader daily report — 2026-07-27

## 1. Run status and data freshness

- Run: `local-20260727T092114Z`
- Status: `succeeded`
- Generated (UTC): `2026-07-27T09:23:05Z`

| Security | Price date | Retrieved at | Status | Error |
| --- | --- | --- | --- | --- |
| security_18a3ab0ee6086ee85d0f | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_1c055eb9b2bb1f5a8ff2 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_1f9cce545ede94cd6349 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_22c2b9d782a62d7a9b86 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_2c779e81c27b78c556bb | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_2dbe878dfc899d7ee867 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_37ddcbdaad296ad831f2 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_4627aea1bf7d8943d3d8 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_4b61970aa8f574446819 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_59304f90c440def31dc5 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_66cdcf90aac0d83e76f3 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_6ad1af8d10d6276a0221 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_6f9a1450edceb9307c9a | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_7ca095d63423c55a90e3 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_8472507d7d320aa388a7 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_9d4049ed6669a52815d6 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_a9eb9838940ef5ceaa0c | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_bdc2f87dadf134760c3a | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_c120e9f26ebb6159adf9 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_c9a37d277445869a8809 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_cc4dcb8f002b61dffe00 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_ed7d5b616a196969c815 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_f2b9760d847b2ba59324 | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |
| security_fb87fac302a5446a1ced | 2026-07-24 | 2026-07-27T09:21:34Z | ok | — |

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

- Allocation mode: `report_only`
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
- Excluded candidate count: 0

Cash remains unallocated because: `insufficient_diversification`, `insufficient_eligible_candidates`

| Rank | Security | Sleeve | Effective score | Current weight | Pending weight | Target weight | Delta | Disposition | Reason | Assessment date |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| — | — | baseline | — | 0% | 0% | 0% | 0 | no candidates | — | — |

## 5. Research operations and dispositions

| Operation | Type | Entity | Disposition | Reason |
| --- | --- | --- | --- | --- |
| — | — | — | no completed operations | — |

## 6. New or changed research entities

No maintained research pages changed today.

## 7. Risks, blockers, and scheduled follow-ups

- `warning` **issue_4183021e1363fc3aa642** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-7a832eb2d5ae.md
- `warning` **issue_9141a7a5538fd458f54f** — Telegram delivery failed: d3c816d22ba7ec5bb52ac8278b8f231f68dace74
- `warning` **issue_b9bb38b0435eee030308** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_2c779e81c27b78c556bb-bollinger_above_upper-3a01ce587bee.md
- `warning` **issue_c035ba6451c092224a7f** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_fb87fac302a5446a1ced-rsi_oversold-97348588c910.md
- `warning` **issue_c74225aa581c50e9a829** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_59304f90c440def31dc5-rsi_overbought-22069206cbf5.md
- `warning` **issue_d759882b3af9c8ff2505** — Daily preparation degraded: classifier blocked for data/wiki/inbox/market-security_66cdcf90aac0d83e76f3-rsi_oversold-c65ee3726752.md

### Active operation queue

- `waiting` 01KYEWGWBRV9EV6YN1WQA6G3WF — security_research for `security_cb88f9154cfeaa15e878`
- `waiting` 01KYEXAGNREGCP02XCC9VBV80V — security_research for `security_c5a9e460d3350284d157`
- `waiting` 01KYFXFKB04HSHKYVSPNGXVJX0 — security_research for `security_66cdcf90aac0d83e76f3`

## 8. Links

- [[index|Wiki index]]
- GitHub report: https://github.com/Kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260727.md

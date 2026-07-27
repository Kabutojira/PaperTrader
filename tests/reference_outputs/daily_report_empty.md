---
title: "PaperTrader daily report — 2026-07-24"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-24"
updated: "2026-07-24"
provenance: deterministic-report-generator
run_id: "run-report"
snapshot_id: "decision_104a0c7daccbc3bb897c"
---

# PaperTrader daily report — 2026-07-24

## 1. Investor decision summary

<!-- papertrader-investor-brief:start -->
# No trade — hold 100% cash

- **Data status:** Current
- **As of:** `2026-07-24T22:00:00Z`
- **Snapshot:** `decision_104a0c7daccbc3bb897c`
- **Cash:** 100000 EUR (100%)
- **Gross exposure:** 0 EUR
- **Approved target cash:** 100000 EUR (100%)
- **Actionable signals:** 0

## Approved target changes

No approved target changes.

## Actionable signals

No actionable trade signals.

## Top blocker or near miss

No assessed near miss is available; research coverage remains incomplete.
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

No assessed near misses are available; incomplete assessments remain coverage gaps.

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

- No material market move required a research follow-up. Evidence: `data/market/latest.csv`.

- [[model-portfolio]]
- [[performance]]
- [[research-catalog]]
- [[signals]]
- [[system-status]]

## 7. Data-quality and coverage impact

- Data status: **current**
- Assessments: 0/0
- Fresh-evidence assessments: 0/0
- Current accepted relationships: 0/0
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market-data success/failure: 0/0
- Research alerts (not trade signals): 0

No current system impacts.

## 8. Audit appendix

### Run diagnostics

- Run ID: `run-report`
- Run status: `succeeded`
- Generated (UTC): `2026-07-24T22:00:00Z`
- Decision snapshot: `decision_104a0c7daccbc3bb897c`

### Complete market freshness

| Security ID | Price date | Retrieved at | Status | Error |
| --- | --- | --- | --- | --- |
| — | — | — | no monitored securities | — |

### Orders and executions

| Order ID | Strategy ID | Fill policy | Status | Created |
| --- | --- | --- | --- | --- |
| — | — | — | no orders | — |

| Execution ID | Order ID | Security ID | Side | Quantity | Fill | Fees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| — | — | — | — | 0 | no executions | 0 |

### Allocation audit

No allocation plan was generated for this run.

| Rank | Security ID | Target weight | Disposition | Machine reasons |
| ---: | --- | ---: | --- | --- |
| — | — | 0% | no candidates | — |

### Research-operation audit

| Operation ID | Type | Entity ID | Disposition | Machine reason |
| --- | --- | --- | --- | --- |
| — | — | — | no completed operations | — |

### Complete active queue

No scheduled follow-up operations.

### Open issues and delivery failures

No open issues.

### Machine decision provenance

- `portfolio_all_cash` — The reconciled model portfolio is entirely cash.
- `no_actionable_signals` — No strategy has produced a current actionable trade signal.
- `allocation_targets`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `cash_ledger`: `643b368149442110c1e0776eaa1b119e5cabe41f1617ee68328cc468cfa71dff`
- `configuration`: `6bfbcfa74f10e7c26fb5d945f6c4e0e7748c06714ce07d22e70a46ae67973c83`
- `csv_contracts`: `006db7fd09c8f810fa6b0be26cd8e4dbd772b3f76b60957660c996d239f16115`
- `decision_schema`: `af6b26a6dbd262948e4e20bb45ac0f948268dcd7d2e761e5942bdd1b2cd6c68b`
- `executions`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `indicators`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `issues`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `market_latest`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `operation_payloads`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `operations_history`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `operations_todo`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `order_legs`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `orders`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `performance_daily`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `portfolio`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `relationships`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `runs`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `securities`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `security_assessments`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `signals`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `source_registry`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `strategies`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `strategy_legs`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `wiki_inbox`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

### Links

- [[index|Investor dashboard]]
- [[model-portfolio|Model portfolio]]
- [[signals|Signals]]
- [[system-status|System status]]
- GitHub report: https://github.com/example/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260724.md

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
snapshot_id: "decision_befca976f1d15614a9b3"
---

# PaperTrader daily report — 2026-07-24

## 1. Investor decision summary

<!-- papertrader-investor-brief:start -->
# No trade — hold 100% cash

- **Investment data:** Current
- **Operations:** Current
- **As of:** `2026-07-24T22:00:00Z`
- **Cash:** 100000 EUR (100%)
- **Gross exposure:** 0 EUR
- **Target cash:** 100000 EUR (100%)
- **Actionable signals:** 0
- **Evidence state:** definitive cash preference

## Target changes

No target changes.

## Actionable signals

No actionable trade signals.

## Leading Buy / Initiate research candidate

No security currently has both a Buy rating and an Initiate action.

## Comparison-only research benchmark

This equal-weight research benchmark is analytical only, not copy-ready, and cannot create signals, orders, or allocation targets.
- CASH 100% (Unrated)
<!-- papertrader-investor-brief:end -->

### Deterministic reasons

- No validated copy-ready signal or pending paper order exists.
- The reconciled model portfolio is entirely cash.
- No strategy has produced a current actionable trade signal.

## 2. Model portfolio and target changes

- Current equity: 100000 EUR
- Current cash: 100000 EUR (100%)
- Current gross exposure: 0 EUR
- Target cash: 100000 EUR (100%)
- Pending-order targets are estimates at the snapshot mark; only fills change accounting.

| Holding | Sleeve | Current weight | Target | Current value | Target value | Action | State |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Cash | cash | 100% | 100% | 100000  | 100000  | No trade | No action |

## 3. Actionable signals and pending orders

No actionable trade signals.

No pending orders.

## 4. Buy / Initiate research candidates

No security currently has both a Buy rating and an Initiate action.

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

- No material market move required a research follow-up. Evidence is retained in the canonical run artifacts.

- [[model-portfolio|PaperTrader model portfolio]]
- [[performance|PaperTrader performance and risk]]
- [[research-catalog|PaperTrader research catalog]]
- [[security-catalog|PaperTrader tracked securities]]
- [[signals|PaperTrader signals and research alerts]]
- [[system-status|PaperTrader system status and audit]]

## 7. Data-quality and coverage impact

- Investment data status: **current**
- Operations status: **current**
- Assessments: 0/0
- Fresh-evidence assessments: 0/0
- Relationship reviews: 0/0
- Accepted relationships: 0
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market-data success/failure: 0/0
- Research alerts (not trade signals): 0

No current system impacts.

## 8. Audit appendix

### Run diagnostics

- Report date: 2026-07-24
- Run status: succeeded
- Generated (UTC): `2026-07-24T22:00:00Z`

### Complete market freshness

| Security | Price date | Retrieved at | Status | Error |
| --- | --- | --- | --- | --- |
| — | — | — | no monitored securities | — |

### Orders and executions

| Order | Strategy | Fill policy | Status | Created |
| --- | --- | --- | --- | --- |
| — | — | — | no orders | — |

| Fill | Order | Security | Side | Quantity | Fill price | Fees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| — | — | — | — | 0 | no executions | 0 |

### Allocation audit

No allocation plan was generated for this run.

| Rank | Security | Target weight | Disposition | Reasons |
| ---: | --- | ---: | --- | --- |
| — | — | 0% | no candidates | — |

### Research-operation audit

| Research operation | Entity | Disposition | Reason |
| --- | --- | --- | --- |
| — | — | no completed operations | — |

### Complete active queue

No scheduled follow-up operations.

### Open issues and delivery failures

No open issues.

### Decision provenance

- The reconciled model portfolio is entirely cash.
- No strategy has produced a current actionable trade signal.

### Links

- [[index|Investor dashboard]]
- [[model-portfolio|Model portfolio]]
- [[signals|Signals]]
- [[system-status|System status]]
- GitHub report: https://github.com/example/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260724.md

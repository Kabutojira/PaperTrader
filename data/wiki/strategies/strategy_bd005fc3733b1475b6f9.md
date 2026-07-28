---
title: Intuitive Surgical valuation watch
type: strategy
status: maintained
tags: [strategy, research, risk]
created: "2026-07-28"
updated: "2026-07-28"
provenance: "source_isrg_q2_2026_sec_exhibit; allocation_plan_8859abf5cf5708b35855"
strategy_id: strategy_bd005fc3733b1475b6f9
relationship_id: relationship_3570e003fd90cd83d26f
security_id: security_1f9cce545ede94cd6349
sleeve: baseline
allocation_plan_id: allocation_plan_8859abf5cf5708b35855
confidence: high
next_review: "2026-08-04"
---

# Intuitive Surgical valuation watch

## Decision

Keep [[securities/security_1f9cce545ede94cd6349|Intuitive Surgical]] on the valuation watchlist and
hold cash. The strategy is **paused**: assessed base-case upside is 2.5%, below the configured 10%
entry minimum, while the 23.2% downside case makes the upside-to-downside ratio about 0.11:1,
below the required 1:1. A score above the cash hurdle is no longer sufficient on its own.

The two unfilled orders, `order_3b1467697b731e2bf689` and `order_745a7a020ecf89d5734d`, and their
signals were cancelled before the capital resize. No ISRG position was filled.

## Why the entry is paused

The current assessment does not meet the full conviction gate. At the validated USD 356.83 mark,
the bounded 12-month downside case is USD 274.20, or 23.2% below market, while the USD 365.60 base
case offers only 2.5% upside. That fails both payoff gates and is below the configured 20%
margin-of-safety threshold. Timing is
also unfavorable: the 27 July close remains below the 20-, 50-, and 200-day averages, RSI(14) is
40.46, the 20-day return is -11.83%, and MACD remains negative. Timing remains a ranking input, but
the valuation/payoff failures independently prevent a buy.

Soft gaps retained: `margin_of_safety_below_target`, `timing_unfavorable`, and
`valuation_not_compelling`. There is no hard data blocker; this is an unattractive payoff decision
under assessment identity `2026-07-27T21:28:56Z`.

## Structure and sizing

- Sleeve and possible future structure: baseline, long common equity only.
- Current action: no entry and no increase.
- Reactivation gate: a fresh assessment must show at least 10% base-case upside, at least 1:1
  base-upside-to-downside, clear the cash score, and retain acceptable evidence and risk state.
- Risk ceiling after any future reactivation: 5%, matching the baseline-position cap.
- Review: after material price or fundamental change, and no later than 26 August 2026.

## Execution handoff

There is no execution handoff while the strategy is paused. Deterministic allocation, signal, and
order gates now enforce the same payoff thresholds, and fill processing cancels a stale baseline
entry before selecting a market bar. Any later reactivation requires a new current allocation plan
and a fresh strategy review.

## Downside, base case, and exit conditions

The downside case is USD 274.20 based on 30 times the annualized first-half GAAP diluted-EPS run
rate. The base case is USD 365.60 at 40 times that run rate. These are bounded 12-month scenarios,
not perpetual values; both require refresh after Q3 evidence.

If exposure exists after a future reactivation, reduce or close when a current deterministic plan
says `reduce` or `close`, when valuation no longer clears every payoff gate, or when exposure
breaches an applicable cap. Exit or pause on a hard blocker, superseded assessment, stale price or FX, material safety or training deterioration,
slowing procedure or installed-base growth, recurring revenue decoupling from utilization,
hospital-budget deferrals, reimbursement or regulatory constraints, competitive erosion, tariff or
supply pressure that prevents cash conversion, or Q3 evidence that invalidates the earnings range.

## Evidence

The SEC-filed Q2 2026 exhibit reports combined procedure growth of about 16%, da Vinci and Ion
installed-base growth of 12% and 21%, instruments and accessories revenue growth of 18% to USD 1.73
billion, total revenue growth of 19%, GAAP operating-income growth of 31% to USD 972 million, and
USD 8.63 billion of cash and investments. See
[[ideas/idea_precision_biology_healthcare_automation|the linked idea]] and the maintained security
review for the evidence limits and source link.

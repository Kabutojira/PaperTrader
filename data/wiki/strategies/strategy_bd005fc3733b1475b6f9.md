---
title: Intuitive Surgical bounded baseline allocation
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

# Intuitive Surgical bounded baseline allocation

## Decision

Use a **long-equity baseline** structure for
[[securities/security_1f9cce545ede94cd6349|Intuitive Surgical]] under immutable allocation plan
`allocation_plan_8859abf5cf5708b35855`. The plan ranks the security first with an effective score
of 63, above the configured cash hurdle of 60, and sets a 4.39% target from a 0% filled weight and a
2.2% pending weight. Its `increase` disposition therefore represents an incremental 2.196574% of
model equity, not permission to exceed the deterministic target. This is a lower-conviction
allocation, not a conviction trade and not personalized investment advice.

The bounded increase is preferable to retaining the incremental 2.196574% in cash because the accepted
[[relationships/relationship_3570e003fd90cd83d26f|healthcare-automation relationship]], high
business quality, balance-sheet strength, liquidity, recurring procedure economics, and score above
the cash hurdle provide a modest positive portfolio-ranking edge. The allocation remains below the
5% baseline-position cap and materially below the 10% general single-position cap.

## Why conviction failed

The current assessment does not meet the full conviction gate. At the validated USD 356.83 mark,
the bounded 12-month downside case is USD 274.20, or 23.2% below market, while the USD 365.60 base
case offers only 2.5% upside. That is below the configured 20% margin-of-safety threshold. Timing is
also unfavorable: the 27 July close remains below the 20-, 50-, and 200-day averages, RSI(14) is
40.46, the 20-day return is -11.83%, and MACD remains negative. The plan also reports insufficient
diversification, so the deterministic 4.39% target must not be enlarged.

Soft gaps retained: `margin_of_safety_below_target`, `timing_unfavorable`, and
`valuation_not_compelling`. There is no current hard blocker, and assessment identity
`2026-07-27T21:28:56Z` remains unchanged.

## Structure and sizing

- Sleeve and structure: baseline, long common equity only.
- Entry action: use the `open` signal lifecycle action for the plan's `increase` disposition only
  while the same allocation plan and assessment remain current, the USD equity mark and USD/EUR
  rate remain fresh, and deterministic risk validation accepts the order.
- Fill policy: a later `execute_strategy` operation may create a pending `next_open` paper order;
  this research operation creates no order or fill.
- Existing state: prior signal `signal_6c82d41c9f217bdab771` and its pending paper order represent
  the plan's 2.2% pending weight; this research operation does not alter either artifact.
- Target-size limit: 4.39% of model equity, EUR 4,393.148137004536205664309978, with an incremental
  plan delta of EUR 2,196.574068502268102832154989 after pending exposure.
- Normalized research leg: buy the same long ISRG common-equity identity. No new share quantity is
  selected here; deterministic baseline execution must derive the exact whole-share delta from the
  live plan, holdings, pending orders, fresh price, and FX and may create a smaller or no order if
  state changes.
- Risk ceiling: 5%, matching the configured baseline-position cap. The current plan-owned target
  remains 4.39%; no short, option, leverage, or multi-leg structure is eligible in baseline mode.
- Strategy review: 4 August 2026, or immediately if the plan, assessment, price, FX, or relationship
  is superseded.

## Execution handoff

The corrected lifecycle contract maps both baseline `open` and `increase` allocation dispositions
to an `open` signal. Signal `signal_98939c5cb11dd6d9d2ae` represents only a request to review the
incremental allocation under the current plan; it selects no quantity and creates no order or fill.
Exactly one separate `execute_strategy` follow-up, `01KYKX54MRDBWHGFKQERB0YG2Q`, must revalidate the plan,
assessment, mark, FX, pending order, cash, and risk limits before deterministic code derives any
positive whole-share delta. The prior pending paper order remains unchanged.

## Downside, base case, and exit conditions

The downside case is USD 274.20 based on 30 times the annualized first-half GAAP diluted-EPS run
rate. The base case is USD 365.60 at 40 times that run rate. These are bounded 12-month scenarios,
not perpetual values; both require refresh after Q3 evidence.

Reduce or close when a current deterministic plan says `reduce` or `close`, when valuation no
longer clears the cash hurdle, or when exposure breaches an applicable cap. Exit or pause on a hard
blocker, superseded assessment, stale price or FX, material safety or training deterioration,
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

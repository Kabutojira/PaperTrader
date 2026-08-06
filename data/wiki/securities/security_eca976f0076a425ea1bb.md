---
title: UiPath, Inc. Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-06"
updated: "2026-08-06"
provenance: "source_uipath_q1_fy2027_10q_sec; source_uipath_q1_fy2027_results_sec_ex99_1; deterministic market and FX caches"
security_id: security_eca976f0076a425ea1bb
issuer_id: issuer_179c5fbd81cd6cf197cf
confidence: medium
next_review: "2026-08-20"
---

# UiPath, Inc. Class A common stock

## Identity

- Immutable security: `security_eca976f0076a425ea1bb`
- Issuer: `issuer_179c5fbd81cd6cf197cf`
- Instrument: Class A common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `PATH` / `XNYS` / `USD` / equity

The identity matches the maintained [[security-catalog|security catalog]]. No accepted investment-idea
relationship or strategy currently links to this security.

## Changes since prior review

- **Facts and evidence changed:** this is the first completed review and first comparable assessment.
  UiPath's fiscal Q1 2027 Form 10-Q and SEC-filed results release establish current recurring-revenue
  growth, retention, profitability, cash generation, liquidity, dilution and guidance.
- **Assumptions and valuation changed:** the prior state was unassessed. A `mature_compounder`
  earnings-multiple valuation now normalizes cash earnings after stock compensation, dilution and
  reinvestment rather than capitalizing one seasonally strong cash-flow quarter.
- **Scenario outputs changed:** no prior outputs existed. New 12-month bear/base/bull fair values are
  USD 8.50/USD 15.50/USD 26.50 with 25%/50%/25% probabilities. Their weighted value is USD 16.50
  versus the USD 13.82 reference mark.
- **Thesis, catalysts and risks:** 12% ARR growth, 109% net retention, 82% gross margin, first-quarter
  GAAP operating profit and a net-cash balance support the platform thesis. Slowing growth, competition,
  product-transition execution, stock compensation and uncertain agentic-AI monetization remain material.
- **Blockers and gaps:** there is no missing-evidence hard blocker. Medium confidence, downside payoff,
  overbought timing, normalization uncertainty and the absence of an accepted relationship block allocation.
- **Rating and action:** scenario economics support **Buy / Initiate** as a valuation label, but not a
  paper position. The bear asymmetry and relationship gate make the operative disposition **Watch / no action**.
- **Unchanged conclusion:** watchlist exposure remains appropriate. A lower-risk entry or evidence that
  agentic products sustain growth and per-share cash earnings is required before strategy work.

## Current economics and thesis

UiPath sells enterprise automation and orchestration software spanning robotic process automation,
workflow, document processing and agentic tools. The investment mechanism is that a large installed base
standardizes on UiPath to govern both deterministic automations and AI agents, lifting subscription
revenue, retention and per-share cash earnings while the company contains sales and development costs.
The mechanism is falsifiable: weaker retention, stalled ARR growth, cloud and AI competition, or stock
compensation consuming operating gains would impair it.

Fiscal Q1 2027 revenue rose 17% year over year to USD 418.4 million. Subscription-services revenue was
USD 252.9 million, licenses USD 149.3 million and professional services USD 16.2 million. ARR rose 12% to
USD 1.901 billion, net new ARR was USD 49 million and dollar-based net retention improved to 109% from
108%. No customer represented 10% of revenue. Remaining performance obligations were USD 1.413 billion,
64% expected within 12 months. These figures support recurring demand, but 12% ARR growth is not yet
proof that agentic products will reaccelerate the business.

GAAP gross margin remained 82%. Operating income improved to USD 28.0 million from a USD 16.4 million
loss, and operating cash flow rose to USD 131.9 million from USD 119.0 million. Stock compensation was
still USD 53.3 million, more than GAAP net income of USD 22.5 million, so valuation must treat dilution
and compensation as economic costs. Management guided fiscal 2027 revenue to USD 1.776-1.781 billion,
ARR to USD 2.058-2.063 billion and non-GAAP operating income to about USD 430 million.

Liquidity is a major strength. Cash, restricted cash and marketable securities totaled USD 1.417 billion
at 30 April against no funded debt disclosed in the balance-sheet liabilities. The company nevertheless
used USD 235.7 million to repurchase Class A shares during the quarter and USD 149.4 million for
acquisitions. Class A and Class B shares outstanding totaled about 520.5 million, while diluted weighted
average shares were 527.8 million. Capital returns help offset dilution, but their price discipline and
the recurring stock-compensation burden remain material.

## Evidence and market alert

Primary evidence: [fiscal Q1 2027 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1734722/000173472226000041/path-20260430.htm)
and [SEC-filed fiscal Q1 results release](https://www.sec.gov/Archives/edgar/data/1734722/000173472226000037/path-2026430xex991.htm).

The [[inbox/market-security_eca976f0076a425ea1bb-bollinger_above_upper-4b2db672f17a|4 August
Bollinger breakout]] and [[inbox/market-security_eca976f0076a425ea1bb-rsi_overbought-d6eb134c7089|RSI
overbought transition]] followed a 21.03% adjusted-close rise from 7 July to USD 14.10. The retained
primary filings predate that period and no newer issuer filing identifies a fundamental cause, so the move
cannot be attributed to a verified company catalyst. On 5 August the close fell 1.99% to USD 13.82; RSI
had eased to 67.58 and price was just below the USD 13.90 upper Bollinger band, while MACD remained
positive. The alert is therefore **adverse entry timing after an unexplained momentum rally**, not thesis
confirmation.

## Valuation

Template: `mature_compounder`; method: `earnings_multiple`; horizon: 12 months.

The cases value normalized per-share cash earnings after stock compensation, dilution and reinvestment,
then add a conservative per-share value for surplus cash and securities after leases, acquisitions and
operating needs. The bear case uses USD 0.35 at 18x plus USD 2.20 of net financial value; base uses USD
0.55 at 24x plus USD 2.30; bull uses USD 0.80 at 30x plus USD 2.50. The range reflects strong recurring
economics and net cash without treating non-GAAP income or one quarter's cash conversion as fully
available to common shareholders.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 8.50 | USD 0.35 normalized per-share cash earnings at 18x plus USD 2.20 surplus cash; ARR growth slows, retention weakens, competition raises spending and dilution persists. |
| Base | 50% | USD 15.50 | USD 0.55 at 24x plus USD 2.30; ARR grows near low double digits, gross margin stays resilient, operating discipline improves and buybacks broadly offset dilution. |
| Bull | 25% | USD 26.50 | USD 0.80 at 30x plus USD 2.50; agentic orchestration sustains stronger growth, retention and margins while stock compensation falls as a share of revenue. |

The weighted value is USD 16.50, 19.39% above the USD 13.82 mark. Base upside is 12.16%, while the bear
case implies 38.49% downside and the bull case 91.75% upside. Medium confidence reduces usable expected
return to about 14.54%. The expected and base returns clear headline hurdles, but base-upside-to-bear-
downside and expected-upside-to-bear-downside payoff remain weak; the stock also lacks an accepted causal
relationship. A scenario label alone therefore does not justify a position.

## Catalysts, risks and invalidation

Catalysts are delivery of fiscal 2027 guidance, ARR and net-retention stability, production adoption of
agentic orchestration, sustained GAAP operating profitability, lower stock compensation as a percentage
of revenue, durable per-share free cash flow and disciplined buybacks. A price below the USD 12.40
base-case buy-below level could improve asymmetry without a thesis upgrade.

Invalidate or downgrade if ARR growth or retention weakens materially, agentic products fail to convert
pilots into production revenue, cloud or automation competitors take share, gross margin erodes, sales or
research costs reaccelerate without growth, stock compensation and dilution overwhelm buybacks, capital
allocation consumes net cash without adequate returns, cybersecurity or AI-governance failures impair
trust, or fiscal 2027 guidance is cut.

## Disposition

Status: **watching**, confidence **medium**, valuation label **Buy / Initiate**, operative disposition
**Watch / no action**. Recurring growth, improving profitability and net cash support continued coverage,
but payoff asymmetry, overbought timing, medium confidence and the absent accepted relationship block
allocation and strategy research. Review after fiscal Q2 results or a material product, retention,
guidance, capital-allocation or competitive change, no later than **2026-08-20**.

[[research-catalog|Back to the research catalog]]

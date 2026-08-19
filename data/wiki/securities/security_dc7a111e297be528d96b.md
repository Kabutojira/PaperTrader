---
title: "Tesla, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-07-29"
updated: "2026-08-19"
provenance: "source_tsla_q2_2026_10q|source_tsla_q2_2026_deliveries|source_tsla_sec_submissions_20260819"
security_id: security_dc7a111e297be528d96b
issuer_id: issuer_a1f77a81ab2e06de9e77
ticker: TSLA
venue_mic: XNAS
provider_symbol: TSLA
currency: USD
confidence: medium
next_review: "2026-09-18"
---

# Tesla, Inc. common stock

## Decision

**Rating: Sell. Portfolio action: Avoid.** A scenario-complete sum-of-parts review values Tesla at
USD 137 / USD 272 / USD 491 per share in the bear/base/bull cases over 12 months, with 25% / 50% /
25% probabilities and USD 293 probability-weighted value. Against the USD 336.87 mark, expected
return is about negative 13%; the base case remains below the market price and the bear case shows
substantial downside. Strong liquidity and real automotive, energy-storage and AI development
capacity do not offset weak current operating leverage, exceptional capital intensity and the
market value already assigned to AI-enabled businesses without disclosed mature economics. Avoid
until supported component economics or a materially lower price clears the canonical return,
payoff and margin-of-safety gates; downgrade further if demand, margins, cash conversion,
autonomy execution, capital productivity, governance or liquidity deteriorates.

## Immutable identity

- Security ID: `security_dc7a111e297be528d96b`
- Issuer ID: `issuer_a1f77a81ab2e06de9e77`
- Instrument: Tesla, Inc. common stock
- Listing: Nasdaq Global Select Market (`XNAS`)
- Provider symbol: `TSLA`
- Currency: `USD`

Tesla's Form 10-Q confirms its common stock trades as `TSLA` on Nasdaq. No duplicate
issuer-instrument-venue-currency-provider identity exists in the canonical security table.

## Alert review

The canonical market record covers 2026-06-29 through 2026-07-28:

- Adjusted close fell from USD 411.84 to USD 306.86, a **25.49%** decline.
- RSI reached **26.93**, creating the `rsi_oversold` transition.
- The close remained just above the USD 306.33 lower Bollinger band.
- The latest volume z-score was **0.67**, below the abnormal-volume threshold.
- After Tesla released Q2 results following the July 22 close, the shares fell **14.52%** on July
  23, with 115.6 million shares traded versus 30.6 million in the prior session.

The filing is temporally aligned with the largest one-session repricing in the alert period and
contains material mixed evidence, but it does not prove that every part of the month-long decline
was caused by the release. The move is material because the post-results price action confirms
that stronger volume and revenue did not remove concern about operating leverage, capital
intensity, or the valuation assigned to future autonomy and robotics economics.

### 2026-08-19 quick check of the August 7 alert

The payload-bound period runs from 2026-07-09 through 2026-08-07. Adjusted close rose **3.38%** to
USD 328.58 and MACD crossed above its signal line. By 2026-08-18 the close was USD 336.87, **2.52%**
above the alert mark and **6.58%** above the prior review's USD 316.06 reference price. MACD remained
above signal, but both were negative; RSI was neutral at 46.28 and no current transition was active.
This is stabilization after the post-results selloff, not evidence that the operating or valuation
gates improved.

The SEC submissions index contained no periodic operating filing or earnings release after the Q2
Form 10-Q through this check. The Q2 revenue, delivery, liquidity, margin, capital-intensity,
autonomy, governance and invalidation assumptions therefore remain unchanged. A newly accepted
[[relationships/relationship_terafab_tsla|Terafab relationship]] adds a plausible custom-silicon
supply-security and iteration channel, but the disclosed framework is non-binding and supplies no
capacity, price, volume or shareholder-return evidence. It changes the relationship frontier, not
the valuation conclusion.

## Changes since prior review

- **Facts and evidence:** the Q2 Form 10-Q was rechecked on August 19 and remains the latest primary
  operating evidence. No revenue, margin, liquidity, share-count or capital-spending fact changed
  from the quick check, and no contradictory later filing was found.
- **Assumptions and scenarios:** the unsupported legacy USD 169.26 / USD 264.97 two-case revenue
  sensitivity is replaced by a current sum of parts. The new bear/base/bull values are USD 137 /
  USD 272 / USD 491 with 25% / 50% / 25% probabilities. They separately bound annualized
  automotive-and-services revenue, energy revenue, AI-enabled option value, USD 34.444 billion of
  net cash and 3.540 billion diluted shares. The resulting USD 293 weighted value is below the
  market price; no supported buy zone is reached.
- **Thesis, catalysts and risks:** the thesis is neither upgraded nor invalidated. Vehicle and
  energy scale plus balance-sheet capacity remain constructive; operating leverage, more than USD
  25 billion of expected 2026 capital spending, autonomy economics, dilution, governance and
  execution remain material risks. Margin improvement, profitable autonomy, durable energy margins
  and productive capital conversion remain the catalysts.
- **Blockers and gaps:** the hard `valuation_unsupported` blocker is resolved by the complete
  scenario set. Medium confidence, unfavorable timing, a below-target margin of safety and
  uncompelling valuation remain soft gaps. The accepted medium-confidence Terafab relationship
  completes the relationship frontier but adds no current component value because its framework is
  non-binding and unquantified.
- **Rating and action:** the deterministic conclusion changes from Unrated / Watch to Sell / Avoid.
  Allocation remains ineligible, and the prior conclusion that the MACD stabilization does not
  justify a conviction strategy remains unchanged.

## Business and financial evidence

Tesla delivered 480,126 vehicles and deployed 13.5 GWh of energy storage in Q2. Revenue increased
26% year over year to USD 28.236 billion and gross profit increased to USD 4.751 billion. However,
operating expenses rose to USD 4.353 billion and operating income fell 57% to USD 398 million.
Quarterly common-stockholder net income was USD 1.114 billion, down 5%, and included non-operating
income that makes headline earnings less representative of core operating progress.

At June 30, cash and short-term investments totaled USD 43.524 billion against USD 9.08 billion of
debt principal. Six-month operating cash flow was USD 8.634 billion, but USD 8.282 billion of
capital expenditures consumed almost all of it before other investing activity. Management
expects more than USD 25 billion of 2026 capital expenditures for AI compute, data centers,
manufacturing and research lines, company-operated AI-enabled assets, and supporting
infrastructure. Liquidity is strong; the economic return on this spending remains the decisive
uncertainty.

## Thesis, contrary evidence, and invalidation

The thesis is that Tesla can use manufacturing scale, vehicle data, software, energy storage, and
vertical integration to create durable cash flows from electric vehicles while building valuable
autonomy, Robotaxi, and Optimus businesses. Q2 delivery and revenue growth and the strong balance
sheet support the ability to fund that option set.

Contrary evidence is weak operating leverage despite higher revenue, expanding stock-based and
research costs, more than USD 25 billion of planned annual capital spending, cyclical vehicle
demand, policy and tariff exposure, execution risk across several simultaneous ramps, and the lack
of disclosed mature economics for the AI-enabled businesses supporting much of the valuation.

Catalysts are sustained automotive margin improvement, profitable Robotaxi scaling, measurable
software or fleet economics, energy-storage growth with stable margins, lower unit costs, and
capital spending that converts into durable free cash flow. Invalidate the constructive case if
vehicle demand or margins deteriorate persistently, autonomy fails to achieve safe commercial
scale, AI and manufacturing investment remains structurally cash consumptive, dilution rises
without commensurate per-share value, or liquidity weakens materially.

## Valuation

The repository's `other` template with a `sum_of_parts` method fits because Tesla combines a
profitable but cyclical automotive-and-services base, a growing energy segment, and pre-profit or
economically undisclosed autonomy, robotics and AI optionality. No specialized template spans all
three. Debt and dilution are explicit: the filing reports USD 43.524 billion of cash and short-term
investments, USD 9.080 billion of disclosed debt principal and 3.540 billion diluted weighted-average
shares.

The 12-month scenarios annualize Q2 automotive-and-services revenue of USD 25.097 billion and
energy revenue of USD 3.139 billion. This strong-quarter annualization is deliberately transparent;
the lower cases offset it with lower multiples and bounded option value rather than treating
unproven AI businesses as current earnings.

- **Bear — USD 137, 25% probability.** Automotive and services receive 3x annualized revenue,
  energy receives 4x, AI-enabled optionality receives USD 100 billion, and net cash is added.
  Demand or margins weaken, capital spending stays above cash conversion, and autonomy and robotics
  do not establish material profit pools.
- **Base — USD 272, 50% probability.** Automotive and services receive 4.5x annualized revenue,
  energy receives 6x, AI-enabled optionality receives USD 400 billion, and net cash is added.
  Scale and energy growth persist, but operating leverage improves only gradually and AI economics
  remain promising rather than mature.
- **Bull — USD 491, 25% probability.** Automotive and services receive 6x annualized revenue,
  energy receives 8x, AI-enabled optionality receives USD 1 trillion, and net cash is added.
  Vehicle margins recover, energy compounds with durable margins, and autonomy or robotics reaches
  safe commercial scale with demonstrable cash economics.

The probability-weighted fair value is **USD 293**. Against the August 18 adjusted close of USD
336.87, the bear/base/bull returns are approximately **negative 59.3% / negative 19.3% / positive
45.8%**, and expected return is approximately **negative 13.0%** before the deterministic
confidence adjustment. The scenario set is complete but not attractive: the base case, expected
return, downside payoff and margin of safety do not support an entry or a conviction strategy.

## Sources

- [Tesla Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm)
  (`source_tsla_q2_2026_10q`, rechecked 2026-08-19).
- [Tesla Q2 2026 production, deliveries and deployments](https://ir.tesla.com/press-release/tesla-second-quarter-2026-production-deliveries-and-deployments)
  (`source_tsla_q2_2026_deliveries`, checked 2026-07-29).
- [Tesla SEC submissions index](https://data.sec.gov/submissions/CIK0001318605.json)
  (`source_tsla_sec_submissions_20260819`, checked 2026-08-19).
- Canonical market and indicator state: `data/market/latest.csv`,
  `data/market/indicators.csv`, and
  `data/market/prices/security_dc7a111e297be528d96b.csv`, retrieved
  `2026-08-19T09:08:06Z` for the current comparison; the immutable alert packet retains the
  `2026-08-08T11:01:36Z` payload observation.

Next review: **2026-09-18**, or sooner after material delivery, margin, autonomy, regulatory,
capital-spending, financing, Terafab, governance or guidance evidence.

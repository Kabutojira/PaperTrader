---
title: "Tesla, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-07-29"
updated: "2026-07-29"
provenance: "source_tsla_q2_2026_10q|source_tsla_q2_2026_deliveries"
security_id: security_dc7a111e297be528d96b
issuer_id: issuer_a1f77a81ab2e06de9e77
ticker: TSLA
venue_mic: XNAS
provider_symbol: TSLA
currency: USD
confidence: medium
next_review: "2026-08-28"
---

# Tesla, Inc. common stock

## Decision

**Baseline comparison; no conviction strategy.** Tesla's Q2 filing shows strong delivery and
revenue growth, substantial liquidity, and continuing investment in autonomy, robotics, energy
storage, and manufacturing. Those positives are offset by a 57% year-over-year decline in
quarterly operating income, sharply higher research and overhead spending, capital expenditures
that nearly doubled, and a valuation still dependent on unproven AI-enabled profit pools. The
RSI-oversold transition followed a material post-results repricing, but the bounded base case
remains below the market mark. The alert is therefore valuation and execution risk, not a
paper-trade signal.

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

At the USD 306.86 mark and 3.540 billion diluted weighted-average shares, Tesla's equity value is
about USD 1.09 trillion. Annualizing Q2 revenue gives USD 112.944 billion. The company has about
USD 34.444 billion of cash and short-term investments net of disclosed debt principal.

A bounded 12-month sensitivity applies deliberately generous revenue multiples to recognize the
autonomy, robotics, software, and energy-storage option set without assuming those businesses have
already achieved mature economics:

- Downside: **5x** annualized revenue plus net cash, or about USD 169.26 per share and **44.8%
  downside**.
- Base: **8x** annualized revenue plus net cash, or about USD 264.97 per share and **13.6%
  downside**.

This is a scenario range, not a precise intrinsic target. It is favorable to the equity because it
uses annualized strong-quarter revenue, does not discount future capital spending, and gives a
premium multiple to economics that remain partly unproven. The oversold decline has not created
the configured 10% base upside or an adequate upside-to-downside ratio.

## Sources

- [Tesla Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm)
  (`source_tsla_q2_2026_10q`, checked 2026-07-29).
- [Tesla Q2 2026 production, deliveries and deployments](https://ir.tesla.com/press-release/tesla-second-quarter-2026-production-deliveries-and-deployments)
  (`source_tsla_q2_2026_deliveries`, checked 2026-07-29).
- Canonical market and indicator state: `data/market/latest.csv`,
  `data/market/indicators.csv`, and
  `data/market/prices/security_dc7a111e297be528d96b.csv`, retrieved
  `2026-07-29T16:55:24Z`.

Next review: **2026-08-28**, or sooner after material delivery, margin, autonomy, regulatory,
capital-spending, financing, or guidance evidence.

---
title: NVIDIA Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-05"
updated: "2026-08-05"
provenance: "source_nvda_q1_fy2027_10q; source_nvda_q1_fy2027_results"
security_id: security_33d9c44facc75c726c7d
issuer_id: issuer_7f0f0b334051a9c9a06b
confidence: medium
next_review: "2026-08-19"
---

# NVIDIA Corporation common stock

## Identity

- Immutable security: `security_33d9c44facc75c726c7d`
- Issuer: `issuer_7f0f0b334051a9c9a06b`
- Instrument: common stock, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `NVDA` / `XNAS` / `USD` / equity

NVIDIA supplies accelerated-computing processors, networking, systems, and software. Its economics
are a direct comparison for cloud-platform capital spending at
[[securities/security_204be2a44063993de1a8|Microsoft]] and for AI-cluster networking at
[[securities/security_6f9a1450edceb9307c9a|Arista Networks]], but no accepted canonical
idea-security relationship currently exists for this instrument.

## Economics and thesis

The investable thesis is that NVIDIA's integrated GPU, interconnect, networking, systems, and
software platform can retain a large share of expanding AI-infrastructure spending while rapid
product cycles and scale sustain exceptional margins and cash generation. The counterpoint is that
current expectations already require continued hyperscaler and broader AI-factory investment,
flawless Blackwell-to-Rubin execution, adequate power and manufacturing capacity, and limited
competitive or regulatory erosion.

For the quarter ended 26 April 2026, revenue rose 85% year over year and 20% sequentially to USD
81.615 billion. Data Center revenue was USD 75.246 billion, up 92% year over year and 21%
sequentially; compute reached USD 60.4 billion and networking USD 14.8 billion. GAAP gross margin
was 74.9%, operating income was USD 53.536 billion, and operating cash flow was USD 50.344 billion.
These figures strongly support demand, platform breadth, pricing, and operating leverage, although
USD 15.9 billion of equity-security gains inflated GAAP net income and are excluded from normalized
earnings.

## Evidence and decision gates

| Evidence | Interpretation |
| --- | --- |
| Q2 fiscal 2027 revenue guidance is USD 91.0 billion plus or minus 2%, with 74.9%-75.0% gross-margin guidance. | Near-term demand and economics remain strong, but the market already discounts substantial continued growth. |
| Data Center represented about 92% of Q1 revenue; Hyperscale remained about half of Data Center while other AI-cloud, industrial, enterprise, and sovereign customers supplied the balance. | Customer mix is broadening, but AI infrastructure and large-customer capital budgets remain concentrated economic exposures. |
| No Data Center Hopper shipments to China occurred in Q1, and Q2 guidance assumes no China Data Center compute revenue. | Export controls remove a major addressable market and can create inventory, product-design, and license uncertainty. |
| Cash plus marketable debt securities was USD 50.335 billion against USD 8.470 billion total debt; Q1 free cash flow before equipment-financing principal was about USD 48.6 billion. | Net financial strength and cash generation provide substantial resilience and fund research, capacity, repurchases, and dividends. |
| Inventory rose sequentially to USD 25.797 billion, supply-related commitments reached USD 119.0 billion, and cloud-service commitments reached USD 30.0 billion. | Securing supply supports growth but magnifies demand-forecast, transition, counterparty, and obsolescence risk. |
| Rubin is expected to begin shipping in the second half of fiscal 2027. | A successful cadence is a catalyst; delay, yield, quality, or customer-transition friction is a key invalidation path. |

Primary evidence is the [quarterly report filed 20 May 2026](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm)
as `source_nvda_q1_fy2027_10q` and the [SEC-filed Q1 results release](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000051/q1fy27pr.htm)
as `source_nvda_q1_fy2027_results`, both checked 5 August 2026.

## Valuation

The `mature_compounder` template uses a 12-month `earnings_multiple`. Normalized forward earnings
include stock compensation, exclude volatile equity-security gains, and treat the USD 41.865 billion
net cash position as downside support rather than adding it separately to an equity-value multiple.
The scenarios vary revenue growth, operating margin, normalized EPS, and the multiple that investors
may pay after another year of execution. Against the 4 August close of USD 211.94000244140625:

| Scenario | Probability | Fair value | Assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 180.00 | USD 7.50 forward EPS at 24x as AI-infrastructure growth decelerates, China remains unavailable, Rubin or supply execution adds cost, and the valuation multiple compresses. |
| Base | 50% | USD 252.00 | USD 9.00 forward EPS at 28x as Q2 guidance converts, Blackwell remains strong, Rubin ships broadly on schedule, and roughly mid-70% gross margin supports continued cash generation. |
| Bull | 25% | USD 374.00 | USD 11.00 forward EPS at 34x as sovereign, enterprise, networking, and hyperscale demand compound, Rubin expands performance and platform breadth, and margins remain exceptional. |

Probability-weighted fair value is USD 264.50, 24.8% above the mark. The base case offers 18.9%
upside, while the bear case implies 15.1% downside; base upside to bear downside is only about 1.25x.
The valuation therefore supports continued monitoring but lacks robust downside asymmetry at the
current price. Medium confidence reflects the unusually wide outcome range, dependence on sustained
customer capital spending, and sensitivity to both normalized EPS and the terminal multiple.

## Alert review, catalysts, and risks

From 7 July through 4 August the adjusted close rose 7.62% to USD 211.94. On 4 August MACD crossed
above its signal line with deterministic strength 0.5629; RSI was 56.94, the close remained below
the USD 216.91 upper Bollinger band, and the move did not coincide with a new operating filing.
The transition is therefore improving momentum, not independent proof of a fundamental change. It
is neutral-to-positive timing evidence, but the limited bear/base asymmetry prevents treating it as
a paper-buy signal.

Catalysts are delivery against Q2 guidance, continued Blackwell 300 and networking growth, Rubin
shipments in the second half of fiscal 2027, broader enterprise and sovereign adoption, durable
mid-70% gross margins, and continued conversion of earnings to cash. Risks are export restrictions,
large-customer and AI-capex concentration, dependence on third-party manufacturing and packaging,
power and data-center constraints, rapid product transitions, competition and customer-designed
silicon, USD 119 billion of supply commitments, investment-value volatility, and valuation-multiple
compression.

Invalidate the thesis if customer returns fail to sustain AI infrastructure budgets, Data Center
growth or margins deteriorate materially, Rubin is delayed or fails to win broad adoption, supply
commitments produce material provisions, competing architectures erode platform economics, or
normalized per-share earnings and cash flow cease compounding despite heavy reinvestment.

## Disposition

Status: **watching**, confidence **medium**. Research and scenario valuation are complete. Strong
business quality, net financial strength, and current growth are offset by 15.1% modeled bear-case
downside, only 1.25x base-upside-to-bear-downside, medium confidence, and the absence of an accepted
canonical relationship. The deterministic economic and relationship gates therefore keep the
security allocation-ineligible at Watch. Review by **2026-08-19**, or sooner after Q2 results,
material export-control changes, Rubin timing evidence, a guidance revision, or a major customer
capital-spending change. No conviction strategy, signal, or paper order is justified.

## Changes since prior review

- **Prior state:** this is the first structured security assessment; the mandatory context contained no
  prior assessment, prior successful result, retained source, accepted relationship, strategy, or
  research-page hash.
- **Facts and evidence:** the Q1 filing and results establish current revenue, segment growth, margins,
  cash flow, liquidity, debt, share count, supply commitments, China exposure, and Q2 guidance.
- **Assumptions and valuation:** a new scenario-complete earnings-multiple assessment sets
  bear/base/bull values of USD 180/USD 252/USD 374 at 25%/50%/25%; there are no prior values to
  revise.
- **Thesis, catalysts, and risks:** exceptional platform economics and AI-infrastructure demand
  support the thesis, while export controls, customer-capex dependence, supply commitments,
  product-transition execution, competition, and valuation sensitivity constrain it.
- **Blockers, gaps, rating, and action:** no hard research blocker remains. Bear/base asymmetry is
  insufficient, confidence is medium, and the absent accepted relationship independently prevents
  allocation. The initial disposition is watching with no strategy or signal.

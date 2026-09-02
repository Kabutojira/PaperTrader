---
title: Atkore Inc. common stock
type: security
status: maintained
tags:
  - security
  - research
  - risk
created: "2026-07-25"
updated: "2026-07-28"
provenance: "source_atkr_q2_2026_10q; source_atkr_q2_2026_results; source_atkr_june_2026_litigation_8k"
security_id: security_22c2b9d782a62d7a9b86
issuer_id: issuer_24dfad17964141504f03
confidence: medium
next_review: "2026-08-15"
---

# Atkore Inc. common stock

## Identity

- Immutable security: `security_22c2b9d782a62d7a9b86`
- Issuer: `issuer_24dfad17964141504f03`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `ATKR` / `XNYS` / `USD` / equity

The SEC filing confirms the common stock and NYSE listing. This page evaluates the instrument
through [[ideas/idea_solar_storage_grid_flexibility_reset]] and its accepted
[[relationships/relationship_solar_storage_grid_atkr|causal relationship]], never ticker text
alone.

## Business economics

Atkore makes electrical conduit, cable-management, and infrastructure products used in data
centres, utilities, commercial construction, and other electrification projects. Demand exposure is
useful only if product pricing catches input inflation and incremental volume converts into cash.

For the quarter ended 27 March 2026, net sales were USD 731.4 million, up 4.2% year over year.
Electrical sales rose 8.1% to USD 532.5 million, helped by volume, foreign exchange, and modest
average-selling-price gains. Consolidated gross margin nevertheless fell to 18.6% from 26.4%:
input costs increased by USD 82.1 million while selling prices contributed only USD 10.2 million.
Adjusted EBITDA declined 30.4% to USD 81.1 million, and Electrical adjusted EBITDA margin fell to
14.0% from 18.5%.

Management maintained fiscal-2026 adjusted EBITDA guidance of USD 340-360 million and adjusted
diluted EPS guidance of USD 5.05-5.55. It also closed plants and divested the HDPE pipe-and-conduit
and Belgian coatings businesses to narrow the portfolio toward electrical infrastructure.

The latest substantive SEC filing is a 4 June 2026 Form 8-K. It adds a USD 50 million settlement
with the third putative class in the PVC pipe antitrust litigation, subject to court approval and
funded from cash on hand. This is incremental to the USD 136.5 million of settlements recognized in
fiscal Q2. Management said the additional payment was not expected to have a material adverse
effect on liquidity or leverage metrics, but the combined USD 186.5 million burden remains relevant
to downside and cash-conversion analysis.

## Thesis

Atkore has positive sensitivity to grid reinforcement, data-centre construction, and electrical
equipment demand. The Q2 volume contribution indicates that end-market demand can grow, but the
same quarter shows that volume alone is insufficient: input-cost inflation overwhelmed pricing and
compressed margins. The survivor thesis requires proof that the post-divestiture electrical
portfolio restores pricing discipline and cash conversion without sacrificing share.

## Evidence and contrary evidence

| Evidence | Interpretation |
| --- | --- |
| Electrical segment sales increased 8.1%, including a USD 28.4 million volume benefit. | Supports real demand exposure rather than a purely narrative link. |
| Consolidated input costs rose USD 82.1 million while selling prices added USD 10.2 million. | Pricing lag is the clearest current disconfirmation of operating leverage. |
| Electrical adjusted EBITDA margin fell 450 basis points to 14.0%. | Higher volume did not translate into stronger segment economics. |
| Six-month operating cash flow was negative USD 27.2 million versus positive USD 160.9 million a year earlier. | Working-capital and tax outflows make cash conversion an unresolved gate. |
| Cash was USD 442.3 million against about USD 760.6 million carrying value of debt. | Liquidity is meaningful, but net debt and the combined USD 186.5 million announced settlements reduce flexibility. |
| Fiscal-2026 adjusted EBITDA guidance was maintained. | Provides a measurable recovery milestone, but it is non-GAAP and not yet delivered. |

Primary evidence: [Atkore fiscal Q2 2026 results](https://investors.atkore.com/investors/news/news-details/2026/Atkore-Inc--Announces-Second-Quarter-2026-Results/default.aspx)
and the [SEC Form 10-Q for 27 March 2026](https://www.sec.gov/Archives/edgar/data/1666138/000162828026030764/atkr-20260327.htm).
The [4 June 2026 Form 8-K](https://www.sec.gov/Archives/edgar/data/1666138/000166613826000014/atkr-20260604.htm)
updates the litigation settlement burden. All three sources were fetched successfully and
registered on 28 July 2026.

## Valuation

The deterministic cache records a USD 75.29 close on 27 July 2026. A bounded 12-month earnings
scenario uses management's maintained fiscal-2026 adjusted diluted EPS range rather than the
litigation-distorted GAAP loss. Applying 10 times the USD 5.05 low end gives a USD 50.50 downside
value, 32.9% below the mark. Applying 14 times the USD 5.55 high end gives a USD 77.70 base value,
only 3.2% above the mark. The low multiples reflect shrinking adjusted EBITDA, pricing lag, weak
cash conversion, net debt, portfolio transition, and settlement cash use. This range is suitable
for comparable ranking, not a precise price target: both the adjusted earnings input and multiple
remain sensitive to post-divestiture normalization.

## Catalysts and confirmation

- fiscal-2026 adjusted EBITDA guidance delivered with improving quarterly cash conversion;
- selling-price increases catching input-cost inflation without material volume loss;
- Electrical adjusted EBITDA margin stabilising and then recovering;
- data-centre, utility, and electrical-infrastructure volume remaining positive; and
- proceeds and cost savings from portfolio simplification reducing net leverage.

## Risks and invalidation

Invalidate the positive case if input costs continue to outrun selling prices, Electrical margins
remain structurally below management's recovery assumptions, infrastructure demand weakens,
working capital consumes cash despite volume growth, litigation or restructuring costs escalate,
or the post-divestiture portfolio cannot convert maintained guidance into free cash flow.

## Disposition

Status: **watching** with **medium** confidence and **baseline** allocation eligibility. Research
again by **2026-08-15** after the next earnings update or sooner after a material pricing,
input-cost, litigation, divestiture, or guidance change. The current mark and bounded valuation now
support comparison, but the 3.2% base upside is below the configured 20% margin-of-safety hurdle;
margin recovery, cash conversion, and post-divestiture normalization remain unproven. No conviction
strategy or paper signal is justified.

## Visual evidence

<!-- papertrader:technical-chart:start -->
This deterministic monitoring chart is derived from the repository-local market cache. Its source CSV remains downloadable and does not feed research scoring or trading state.

```echart
{
  "schema_version": 2,
  "chart_id": "market-technicals",
  "kind": "technical",
  "title": "One-year price, volume, and technical indicators",
  "description": "Adjusted daily OHLC with Bollinger bands and moving averages, followed by volume, RSI, and MACD panels from the deterministic PaperTrader market cache.",
  "security_id": "security_22c2b9d782a62d7a9b86",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_22c2b9d782a62d7a9b86.csv",
  "sources": [
    {
      "label": "Canonical PaperTrader price cache and deterministic TA-Lib projection"
    }
  ],
  "notes": [
    "Adjusted OHLC aligns price history with indicators calculated from adjusted close.",
    "Technical indicators are research alerts, not trade signals."
  ]
}
```
<!-- papertrader:technical-chart:end -->

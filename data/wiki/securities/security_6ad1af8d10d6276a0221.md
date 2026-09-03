---
title: Southern Copper Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-21"
provenance: "source_scco_q2_2026_results; source_scco_q2_2026_10q; source_scco_sec_submissions_20260821; deterministic market and FX caches"
security_id: security_6ad1af8d10d6276a0221
issuer_id: issuer_4a82928ad9dfe58ec4f2
confidence: medium
next_review: "2026-09-04"
---

# Southern Copper Corporation common stock

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
  "security_id": "security_6ad1af8d10d6276a0221",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_6ad1af8d10d6276a0221.csv",
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

## Identity

- Immutable security: `security_6ad1af8d10d6276a0221`
- Issuer: `issuer_4a82928ad9dfe58ec4f2`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `SCCO` / `XNYS` / `USD` / equity

The immutable identity is unchanged and remains unique in the tracked-security table.

## Changes since prior review

- **Evidence unchanged:** a fresh August 21 retrieval of the SEC submissions index matched the
  retained hash and still showed no operating filing after the July 31 Form 10-Q. The July 21
  results release and Q2 filing therefore remain the current primary operating evidence.
- **Market state changed:** the August 21 adjusted close rose 8.69% in one session to USD 216 and
  20.48% from July 24. Volume reached a 2.46 z-score and the close moved above the USD 209.03 upper
  Bollinger band; RSI remained below the configured overbought threshold at 67.33.
- **Assumptions unchanged:** the thesis, normalized earnings, multiples, 30%/50%/20% probabilities,
  catalysts, risks and invalidation conditions remain supported. No price-only move changes
  production, grade, cost, project, leverage or dilution assumptions.
- **Valuation changed only through the mark:** the unchanged USD 91/USD 135/USD 187 scenarios now
  imply bear/base/bull returns of about -57.87%/-37.50%/-13.43%. The USD 132.20 weighted value
  implies about -38.80%, while the USD 108 buy-below price remains unreached.
- **Disposition unchanged:** the volume anomaly and upper-band breach strengthen timing and
  valuation risk rather than the fundamental thesis. Strong Sell / Avoid, allocation ineligibility,
  Hold / Watch research status and the existing review date remain appropriate; no full review,
  strategy, signal or paper trade is justified.

## Economics and thesis

Southern Copper operates integrated mines, smelters, and refineries in Peru and Mexico. Its claimed
51.1 million tonnes of contained copper reserves and low costs provide long-duration price leverage,
but concentrated jurisdictions, controlling ownership, project permissions, and by-product prices
matter materially.

The SEC-filed second-quarter release reports record quarterly sales of USD 4.289 billion, net income
attributable to Southern Copper of USD 1.670 billion, diluted earnings of USD 2.01 per share and an
adjusted EBITDA margin of 66.6%. First-half operating cash flow was USD 3.683 billion. These results
show powerful price leverage: copper sales volume fell 1.5% in the quarter while LME and COMEX price
comparisons rose 39.8% and 30.5%, respectively.

Operating transmission remains imperfect. Quarterly copper production fell 3.5% to 230,662 tonnes,
including a 12.0% decline in Peru, and first-half copper production fell 3.8% to 461,206 tonnes due
mainly to lower Peruvian grades. Second-quarter cash cost after by-product credits was USD 0.05 per
pound, with the improvement driven by a 51.4% increase in those credits. First-half capital
investment rose 56.2% to USD 864.7 million. Tía María had USD 693 million invested at June 30 and is
targeted for initial production in the second half of 2027, but the filing retains legal, permitting,
social and execution risks around the project program.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q2 sales, net income and adjusted EBITDA reached records while first-half operating cash flow was USD 3.683 billion. | Current metal prices are converting into earnings and cash. |
| Q2 copper production fell 3.5%; first-half output fell 3.8% because of lower Peruvian grades. | Price, not volume, is the main earnings driver and operational recovery remains unproven. |
| Q2 cash cost after credits was USD 0.05/lb; the improvement depended on 51.4% higher by-product credits. | Reported cost leadership is real but materially sensitive to silver, zinc and molybdenum prices. |
| Cash was USD 5.665 billion and long-term debt USD 7.994 billion after a USD 1.25 billion project note. | Liquidity is strong, while the large project program raises fixed funding and execution exposure. |
| Diluted EPS was USD 2.01 in Q2 and USD 3.93 for the first half; 834.3 million shares were outstanding. | Peak-price earnings require normalization and stock dividends dilute per-share comparisons. |

Registered primary evidence: [second-quarter 2026 results](https://www.sec.gov/Archives/edgar/data/1001838/000110465926085515/scco-20260721xex99d1.htm)
(`source_scco_q2_2026_results`) and [Q2 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1001838/000110465926089169/scco-20260630x10q.htm)
(`source_scco_q2_2026_10q`). The [dated SEC submissions index](https://data.sec.gov/submissions/CIK0001001838.json)
(`source_scco_sec_submissions_20260821`) confirms no later operating filing through August 21.

## Market alert

The canonical August 21 adjusted close was USD 216, up 20.4752% from July 24 and 8.6902% for the
session. Volume of 1,672,255 produced a 2.4616 z-score and entered the configured anomaly state.
The close exceeded the USD 209.03 upper Bollinger band; RSI was 67.33, and MACD of 5.0575 remained
above its 3.5742 signal. The exact indicator row matches source-price hash
`7ffd15b60608a4b1ad0cbbfad463fd91a7c4fe161323bf137534449ffa26318a`.

The move remains **valuation risk rather than an actionable opportunity**. Record Q2 results and
strong metal prices support the direction of the thesis, but they were public before the measured
period began and the unchanged SEC submissions index contains no later operating evidence. High
volume and an upper-band breach do not repair negative scenario returns or the missing margin of
safety.

## Valuation, catalysts, and risks

The cyclical-commodity template uses normalized earnings rather than capitalizing record spot-price
results. The 12-month bear case applies 14 times USD 6.50 normalized EPS for USD 91, assuming copper
and by-product prices normalize, grades remain weak and project spending rises. The base case applies
18 times USD 7.50 for USD 135, assuming planned production stabilization and adequate self-funding.
The bull case applies 22 times USD 8.50 for USD 187, requiring sustained metal prices, grade recovery
and disciplined Tía María execution. Probabilities are 30%, 50% and 20%. At USD 216, even the bull
case remains below market; confidence is medium because metal prices, grades, by-product credits,
taxes, capex, debt and stock-dividend dilution create wide normalization uncertainty.

Catalysts are grade recovery, achievement of 2026 production guidance, disciplined Tía María
execution, permitting progress, sustained cash generation and realized copper strength that survives
normalization. Invalidate if grades do not recover, costs rise after credits normalize, projects are
delayed or overrun, social or fiscal terms worsen, debt and dividends outpace prudent funding, or
copper demand and prices weaken.

## Idea exposure map

- **Accepted-needs-review — positive:** [[ideas/idea_critical_minerals_copper|critical minerals and
  structural copper scarcity]]. Copper is the core product, so scarcity can raise realized revenue,
  margins, reserve value and project returns. The canonical edge is accepted but its August 15
  review date has passed; existing queued relationship review `01KZGGJ4M0HCXGWR7Z9E9MEPZ5` should
  test the updated production, cost, debt and project evidence.
- **Candidate — positive:** [[ideas/idea_structural_silver_deficit|structural silver deficit]]. Silver
  is a by-product rather than the core product, but Q2 evidence shows by-product credits materially
  reduced reported copper cash cost. A separate relationship review must test silver attribution,
  sensitivity and whether the mechanism is material after zinc and molybdenum are separated.
- **Rejected-no-link:** [[ideas/idea_ai_infrastructure_power|AI infrastructure and power]],
  [[ideas/idea_solar_storage_grid_flexibility_reset|solar, storage and grid flexibility]] and
  [[ideas/idea_humanoid_robotics_embodied_ai_components|humanoid robotics]] can add copper demand,
  but the issuer does not disclose decision-useful attributable exposure to those end markets; they
  are generic demand adjacencies already captured by the copper-scarcity edge. The maintained gold,
  lithium, uranium and industrial-policy ideas likewise lack a distinct material transmission path.

## Disposition

Status: **watching**, confidence **medium**, and review by **2026-09-04**. Current evidence supports a
complete comparable assessment, but lower production, by-product sensitivity, jurisdiction, debt,
project execution, dilution and all three scenario values below market make the security allocation-
ineligible. The August volume anomaly, upper-band breach and bullish MACD state are not strategy
catalysts. No conviction strategy, signal or paper order is justified.

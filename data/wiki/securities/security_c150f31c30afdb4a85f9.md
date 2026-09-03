---
title: "Crocs, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-08-01"
updated: "2026-08-01"
provenance: "source_crox_q2_2026_10q|source_crox_q2_2026_results"
security_id: security_c150f31c30afdb4a85f9
issuer_id: issuer_1f6c9036716fafed5a2a
ticker: CROX
venue_mic: XNAS
provider_symbol: CROX
currency: USD
confidence: medium
next_review: "2026-08-31"
---

# Crocs, Inc. common stock

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
  "security_id": "security_c150f31c30afdb4a85f9",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_c150f31c30afdb4a85f9.csv",
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

## Decision

**Watch; no conviction strategy.** Record Q2 revenue, direct-to-consumer growth, positive cash
conversion, a raised full-year outlook, and continued repurchases support the core Crocs brand.
Wholesale contraction, lower gross margin, continued HEYDUDE weakness, leverage, and the sharp
post-results selloff temper that evidence. A bounded 12-month earnings-multiple valuation has a USD
145.43 base case but only USD 140.27 probability-weighted value versus the USD 128.01 mark. The
confidence-adjusted expected return and downside payoff remain below the required gates.

## Immutable identity

- Security ID: `security_c150f31c30afdb4a85f9`
- Issuer ID: `issuer_1f6c9036716fafed5a2a`
- Instrument: Crocs, Inc. common stock
- Listing: Nasdaq Global Select Market (`XNAS`)
- Provider symbol: `CROX`
- Currency: `USD`

The SEC filing identifies Crocs, Inc. common stock on Nasdaq under `CROX`, matching the canonical
issuer, instrument, venue, provider, and currency identity. No duplicate canonical identity exists.

## Alert review

The payload's canonical observation period is 2026-07-01 through 2026-07-30:

- The adjusted close ended at USD 123.66, down **0.41%** over the period.
- July 30 volume rose to 3.007 million shares, producing the recorded `volume_anomaly` entry with
  strength **0.9304**.
- Crocs released Q2 results before the July 30 session. Despite revenue and guidance beating the
  prior outlook, the close fell **7.38%** from July 29, making the event relevant to the alert.
- On July 31 the close recovered **3.52%** to USD 128.01. Volume fell to 1.674 million, the volume
  z-score was **1.143**, and the canonical trigger state was empty. RSI was neutral at **48.23**;
  MACD remained below its signal line.

The alert is **risk with mixed evidence**, not a durable opportunity signal. The abnormal-volume
selloff is consistent with concern about wholesale contraction, lower margin, HEYDUDE weakness, and
modest full-year growth despite the raised outlook. The next-session rebound and exited volume
trigger show that the one-day reaction did not independently establish a new trend or an entry.

## Business and financial evidence

Crocs sells the Crocs and HEYDUDE footwear brands through direct-to-consumer and wholesale channels
in more than 85 countries. Brand recognition, a distinctive molded product, personalization through
Jibbitz charms, broad price accessibility, international distribution, and a growing direct channel
support attractive margins and cash generation. Fashion sensitivity and low switching costs limit
the durability of that advantage.

Q2 consolidated revenue rose 2.6% to USD 1.179 billion. Direct-to-consumer revenue grew 12.0%, while
wholesale revenue fell 7.2%. Crocs Brand revenue rose 4.3% to more than USD 1.0 billion, with 7.8%
international growth and 0.4% North American growth. HEYDUDE revenue fell 5.7% to USD 179 million;
its wholesale revenue fell 17.2%, partially offset by 7.2% direct-to-consumer growth.

Gross margin declined to 59.4% from 61.7%, and adjusted gross margin declined 170 basis points to
60.0%. Adjusted operating income fell 4.5% to USD 296 million, with adjusted operating margin down
to 25.1% from 26.9%. Adjusted diluted EPS nevertheless rose 7.6% to USD 4.55 as the diluted share
count fell. Reported year-over-year comparisons benefit from the prior-year HEYDUDE trademark and
goodwill impairments and should not be read as equivalent recurring growth.

First-half operating cash flow was USD 270.8 million and free cash flow was USD 232.0 million. At
June 30, cash was USD 170.3 million, long-term borrowings were USD 1.308 billion, inventory was USD
389.2 million, and 48.1 million common shares were outstanding. The company repurchased 2.3 million
shares for USD 251 million in Q2 and repaid USD 31 million of debt. Repurchases below fair value can
increase per-share value, but the expanded authorization is discretionary and leverage constrains
capital-allocation flexibility.

Management raised 2026 revenue guidance to growth of 1%-2%, Crocs Brand growth to 2%-3%, and
adjusted diluted EPS to USD 13.70-14.00. HEYDUDE is still expected to contract 2%-4%. Third-quarter
revenue is expected to be approximately flat, with adjusted operating margin near 21.5%.

## Thesis, contrary evidence, catalysts, and invalidation

The thesis is that the core Crocs brand can compound per-share value through direct-to-consumer and
international growth, product innovation, high margins, cash conversion, debt reduction, and
accretive repurchases. Current Crocs Brand, direct-channel, international, free-cash-flow, guidance,
and share-count evidence supports that mechanism.

Contrary evidence includes falling wholesale revenue, gross-margin compression, slow North American
growth, persistent HEYDUDE contraction after substantial historical impairment, fashion and
consumer-discretionary cyclicality, retailer inventory risk, foreign exchange, sourcing and tariff
exposure, imitation, debt, and the possibility that repurchases outrun deleveraging. A strong core
brand does not guarantee successful rehabilitation of HEYDUDE.

Potential catalysts are sustained double-digit direct-channel growth, renewed wholesale demand,
HEYDUDE stabilization, margin recovery, further debt reduction, and repurchases materially below
intrinsic value. The thesis would be invalidated by sustained Crocs Brand contraction, continued
HEYDUDE decline without a credible stabilization path, structural gross-margin erosion, weak cash
conversion, rising inventories and markdowns, covenant or refinancing pressure, or capital returns
that weaken the balance sheet without improving per-share value.

## Valuation

A 12-month `mature_compounder` earnings-multiple valuation uses the latest filing, the USD
13.70-14.00 adjusted diluted EPS guidance, 48.1 million period-end shares, first-half free cash flow,
and net debt. Scenario earnings normalize channel mix, margin, HEYDUDE performance, interest,
repurchases, and fashion-cycle risk:

- Bear, 30%: USD **88.00**, using USD 11.00 normalized EPS at 8x as wholesale weakness, HEYDUDE
  contraction, markdowns, and leverage compress earnings and the multiple.
- Base, 50%: USD **145.43**, using the USD 13.85 guidance midpoint at 10.5x as direct and
  international growth offset wholesale and HEYDUDE weakness while margins remain below peak.
- Bull, 20%: USD **205.80**, using USD 14.70 normalized EPS at 14x as brand growth broadens,
  HEYDUDE stabilizes, margins recover, debt falls, and repurchases remain accretive.

Against USD 128.01, the cases imply **-31.3%**, **+13.6%**, and **+60.8%**. Probability-weighted fair
value is USD 140.27, or **+9.6%** before the medium-confidence adjustment and **+7.2%** after it. The
base-upside-to-bear-downside ratio is only **0.44**, and the 20% margin-of-safety buy zone is USD
116.34. The current mark therefore fails confidence-adjusted return, bear/base payoff, expected/bear
payoff, and margin-of-safety gates.

## Sources

- [Crocs Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1334036/000133403626000052/crox-20260630.htm)
  (`source_crox_q2_2026_10q`, checked 2026-08-01).
- [Crocs Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1334036/000133403626000050/croxq22026-pressrelease.htm)
  (`source_crox_q2_2026_results`, checked 2026-08-01).
- Canonical market and indicator state: `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_c150f31c30afdb4a85f9.csv`, market date 2026-07-31 and retrieved
  2026-08-01.

Next review: **2026-08-31**, or sooner after a material guidance, margin, HEYDUDE, wholesale,
inventory, debt, repurchase, sourcing, tariff, or consumer-demand development.

Related navigation: [[security-catalog|Securities]], [[signals|Signals and research alerts]], and
[[research-catalog|Research catalog]].

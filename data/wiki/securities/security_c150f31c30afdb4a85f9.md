---
title: "Crocs, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-08-01"
updated: "2026-09-04"
provenance: "source_crox_q2_2026_10q|source_crox_q2_2026_results|source_crox_sec_submissions_20260903"
security_id: security_c150f31c30afdb4a85f9
issuer_id: issuer_1f6c9036716fafed5a2a
ticker: CROX
venue_mic: XNAS
provider_symbol: CROX
currency: USD
confidence: medium
next_review: "2026-10-03"
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

The lower-band breach is monitoring evidence rather than a trading rule. It is interpreted below
against unchanged primary operating evidence and a fresh identity-matched mark.

```echart
{
  "schema_version": 1,
  "chart_id": "q2-revenue-and-adjusted-operating-income",
  "kind": "series",
  "title": "Second-quarter revenue and adjusted operating income",
  "description": "Revenue increased modestly while adjusted operating income declined, showing that the record top line did not translate into operating leverage.",
  "as_of": "2026-06-30",
  "sources": [{"label": "Crocs Q2 2026 SEC-filed results release", "url": "https://www.sec.gov/Archives/edgar/data/1334036/000133403626000050/croxq22026-pressrelease.htm", "observed_at": "2026-09-04T00:12:16Z"}],
  "x_axis": {"type": "category", "label": "Quarter ended June 30", "values": ["2025", "2026"]},
  "y_axes": [{"label": "USD millions", "unit": "USD million", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["1149.373", "1179.468"]},
    {"name": "Adjusted operating income", "render": "bar", "y_axis": 0, "values": ["309", "296"]}
  ],
  "notes": [
    "Revenue is GAAP; adjusted operating income is the issuer's non-GAAP measure and is shown only for like-for-like operating comparison.",
    "The prior-year GAAP operating result included material HEYDUDE impairment charges, so it is not used in this comparison."
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "valuation-scenarios",
  "kind": "series",
  "title": "Twelve-month fair-value scenarios versus the fresh mark",
  "description": "The fresh mark is below the base-case buy-below level, but expected-to-bear payoff remains below its threshold and a current accepted idea relationship remains unavailable.",
  "as_of": "2026-09-03T23:56:03Z",
  "sources": [
    {"label": "Crocs Q2 2026 Form 10-Q and SEC-filed results release", "url": "https://www.sec.gov/Archives/edgar/data/1334036/000133403626000052/crox-20260630.htm", "observed_at": "2026-09-04T00:12:16Z"},
    {"label": "PaperTrader identity-matched market cache", "observed_at": "2026-09-03T23:56:03Z"}
  ],
  "x_axis": {"type": "category", "label": "Scenario", "values": ["Bear (30%)", "Base (50%)", "Bull (20%)"]},
  "y_axes": [{"label": "USD per share", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Fair value", "render": "bar", "y_axis": 0, "values": ["88", "145.425", "205.8"]},
    {"name": "Fresh mark", "render": "line", "y_axis": 0, "values": ["116.01000213623047", "116.01000213623047", "116.01000213623047"]}
  ],
  "notes": [
    "Probabilities total 100%; probability-weighted fair value is USD 140.2725.",
    "The scenarios are unchanged because fresh SEC retrievals found no newer operating evidence."
  ]
}
```

## Decision

**Buy / Initiate research disposition; Watch conviction with no strategy.** The USD 116.01
fresh mark is below the USD 116.34 base-case buy-below level, and unchanged scenarios now imply
20.91% expected return and 15.69% after the medium-confidence adjustment. Base-to-bear payoff at
1.05 and expected-to-bear payoff at 0.87 remain below their required thresholds. That valuation
improvement comes entirely from an 18.35% price decline, not new operating evidence. The payoff
shortfall and absence of a current accepted causal idea relationship keep the security
allocation-ineligible, so no strategy, signal, order, or paper trade is justified.

## Changes since prior review

- **Facts and evidence:** fresh retrievals at `2026-09-04T00:12:16Z` reproduce the registered Q2
  Form 10-Q and results-release hashes. The current SEC submissions index contains no operating
  filing newer than July 30; later entries are ownership or resale-registration filings. The
  operating evidence is unchanged.
- **Alert and timing:** from August 4 through September 1 the adjusted close fell 18.35%, from USD
  141.19 to USD 115.28. The September 1 close entered and then strengthened below the lower
  Bollinger band. On September 3 the close was USD 116.01, above its USD 113.45 lower band; RSI
  remained weak at 34.89 and MACD remained below signal. The configured trigger had exited.
- **Assumptions and valuation:** normalized EPS, multiples, probabilities and USD 88 / USD 145.425 /
  USD 205.80 bear/base/bull fair values are unchanged. The fresh mark implies scenario returns of
  -24.14%, +25.36% and +77.40%; probability-weighted fair value remains USD 140.2725.
- **Thesis, catalysts and risks:** the core-brand, direct-channel, cash-conversion and repurchase
  thesis is unchanged. Wholesale contraction, margin pressure, HEYDUDE weakness, leverage,
  fashion-cycle exposure and capital-allocation risk remain unresolved. No catalyst or invalidation
  was added or removed.
- **Blockers and gaps:** expected-return and margin-of-safety gaps remain resolved through price.
  Both payoff ratios, medium confidence, cyclical normalization uncertainty, adverse technical
  momentum and the missing accepted relationship remain. There is no hard identity, evidence,
  liquidity, price or FX blocker.
- **Rating, action and provenance:** Buy / Initiate and Watch conviction remain unchanged, while
  allocation remains ineligible. This clean assessment is sourced only to remediation operation
  `01M1MAEMCRRVVECT8KPRWASBYB`, superseding the prior operation's duplicate-version incident
  without editing or deleting either immutable historical version.

## Immutable identity

- Security ID: `security_c150f31c30afdb4a85f9`
- Issuer ID: `issuer_1f6c9036716fafed5a2a`
- Instrument: Crocs, Inc. common stock
- Listing: Nasdaq Global Select Market (`XNAS`)
- Provider symbol: `CROX`
- Currency: `USD`

The SEC filing identifies Crocs, Inc. common stock on Nasdaq under `CROX`, matching the canonical
issuer, instrument, venue, provider, and currency identity. The refreshed submissions index matches
CIK 0001334036. No duplicate canonical identity exists.

## Alert review

The canonical August 4 through September 1 observation period ended with an 18.35% decline and a
new `bollinger_below_lower` entry that strengthened during the September 1 refresh. Price at USD
115.28 was marginally below the USD 115.33 lower band. The September 3 close was USD 116.01, the
lower band was USD 113.45, RSI was 34.89, and MACD at -3.50 remained below its -2.44 signal line.

The breach is a **valuation opportunity but continuing timing risk**, not an actionable signal.
Price entered the prior buy zone, but no primary operating development explains or validates the
decline and the breach exited after one session. The weak momentum warrants monitoring rather than
assuming mean reversion.

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

Against USD 116.01, the cases imply **-24.14%**, **+25.36%**, and **+77.40%**. Probability-weighted
fair value is USD 140.2725, or **+20.91%** before the medium-confidence adjustment and **+15.69%**
after it. The base-upside-to-bear-downside ratio is **1.05**, expected-to-bear payoff is **0.87**, and
the 20% margin-of-safety buy zone is USD 116.34. Both payoff ratios remain below their required
thresholds, and the missing accepted relationship independently prevents allocation eligibility.

## Idea exposure map

Canonical relationship state contains no accepted Crocs edge. The complete maintained idea catalog
was searched. [[ideas/idea_defensive_consumer_cash_return|Defensive consumer cash-return
resilience]] was evaluated as **rejected-no-link**: Crocs' discretionary, fashion-sensitive footwear
demand does not provide the idea's recurring grocery, frozen-food, or franchise-demand mechanism,
and Q2 wholesale contraction and HEYDUDE weakness reinforce that mismatch. The other 27 maintained
ideas were also rejected-no-link because none has a specific material transmission mechanism to
Crocs' products, customers, suppliers, costs, catalysts, or invalidation conditions. There is no
accepted-needs-review or candidate pairing, so no relationship or idea follow-up is warranted.

## Sources

- [Crocs Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1334036/000133403626000052/crox-20260630.htm)
  (`source_crox_q2_2026_10q`, hash reproduced 2026-09-04).
- [Crocs Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1334036/000133403626000050/croxq22026-pressrelease.htm)
  (`source_crox_q2_2026_results`, hash reproduced 2026-09-04).
- [Crocs SEC submissions index](https://data.sec.gov/submissions/CIK0001334036.json)
  (`source_crox_sec_submissions_20260903`, checked 2026-09-04).
- Canonical market and indicator state: `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_c150f31c30afdb4a85f9.csv`, market date 2026-09-03 and retrieved at
  2026-09-03T23:56:03Z. The identity-matched USD/EUR rate was 0.8631600141525269 at the same time.

Next review: **2026-10-03**, or sooner after a material guidance, margin, HEYDUDE, wholesale,
inventory, debt, repurchase, sourcing, tariff, or consumer-demand development.

Related navigation: [[security-catalog|Securities]], [[signals|Signals and research alerts]], and
[[research-catalog|Research catalog]].

---
title: Intel Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-06"
updated: "2026-08-06"
provenance: "source_intc_q2_2026_10q_sec; source_intc_q2_2026_results_sec_ex99_1; deterministic market and FX caches"
security_id: security_dfa34d4b9050964b465e
issuer_id: issuer_e5ff2f53cd2ac8db4f85
confidence: medium
next_review: "2026-08-20"
---

# Intel Corporation common stock

## Identity

- Immutable security: `security_dfa34d4b9050964b465e`
- Issuer: `issuer_e5ff2f53cd2ac8db4f85`
- Instrument: common stock, Nasdaq Stock Market (`XNAS`), USD
- Provider identity: `INTC` / `XNAS` / `USD` / equity

The identity matches the maintained [[security-catalog|security catalog]]. No accepted investment-idea
relationship or strategy currently links to this security.

## Changes since prior review

- **Facts and evidence changed:** this is the first completed review and first comparable assessment.
  Intel's second-quarter Form 10-Q and SEC-filed results release establish current product and foundry
  growth, margins, normalized earnings, liquidity, cash generation, investment requirements and risks.
- **Assumptions and valuation changed:** the prior state was unassessed. A `mature_compounder`
  earnings-multiple valuation now makes normalized earnings, turnaround execution and terminal-multiple
  assumptions explicit rather than capitalizing the quarter's non-cash GAAP loss.
- **Scenario outputs changed:** no prior outputs existed. New 12-month bear/base/bull fair values are
  USD 33/USD 80/USD 133 with 25%/50%/25% probabilities. Their weighted value is USD 81.50 versus the
  USD 101.06 reference mark.
- **Thesis, catalysts and risks:** AI-led server demand, stronger client demand, better factory yields,
  improving margins and nascent external-foundry revenue support the turnaround. Net debt, heavy
  reinvestment, foundry execution, dilution, competition and policy dependence remain material.
- **Blockers and gaps:** there is no missing-evidence hard blocker, but medium confidence, cyclical
  normalization uncertainty, a negative margin of safety and no accepted relationship block allocation.
- **Rating and action:** the initial conclusion is **Hold / Watch**. Strong momentum and execution do
  not provide an adequate risk-adjusted entry at the current price; no strategy, signal or order is
  justified.
- **Unchanged conclusion:** watchlist exposure remains appropriate. Research is now complete, but paper
  ownership requires a lower price or evidence supporting sustained earnings above the base path.

## Current economics and thesis

Intel combines a large x86 client and server processor franchise with an integrated manufacturing and
external-foundry turnaround. The investment case depends on AI and conventional compute demand lifting
product revenue while yield, cycle-time and utilization gains expand margins, and on Intel Foundry
turning advanced process and packaging investment into credible external revenue. That mechanism is
falsifiable: weak product competitiveness, delayed process ramps or persistently uneconomic foundry
investment would impair it.

Second-quarter revenue was USD 16.1 billion, up 25% year over year. Client Computing and Physical AI
revenue was USD 8.9 billion, up 13%; Data Center and AI was USD 6.3 billion, up 59%; total Intel Products
revenue was USD 15.1 billion, up 28%. Intel Foundry segment revenue was USD 5.8 billion, up 31%, though
most remained intersegment; the filing reports only USD 293 million of quarterly third-party foundry and
assembly-and-test revenue. GAAP gross margin recovered to 40.4% and operating margin to 11.1%.
Non-GAAP EPS was USD 0.42. The USD 11.0 billion GAAP net loss principally reflected a USD 12.6 billion
non-operating charge, including mark-to-market losses on government-related escrowed shares, so it is
not a useful stand-alone measure of recurring earning power.

Management guided third-quarter revenue to USD 15.8-16.8 billion, GAAP gross margin to about 41% and
non-GAAP EPS to USD 0.38. Financial capacity is adequate but not strong: cash and short-term investments
were USD 29.7 billion against USD 50.5 billion of debt at 27 June. First-half operating cash flow was
USD 8.1 billion. Quarterly operating cash flow was USD 7.0 billion, but company-defined adjusted free
cash flow was negative USD 8.4 billion after capital spending, finance leases and a large net partner-
contribution outflow. The turnaround therefore still requires disciplined capital allocation.

## Evidence and market alert

Primary evidence: [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/50863/000005086326000157/intc-20260627.htm)
and [SEC-filed Q2 results release](https://www.sec.gov/Archives/edgar/data/50863/000005086326000155/q226earningsrelease.htm).

The [[inbox/market-security_dfa34d4b9050964b465e-macd_cross_above_signal-181ec6e47f3f|4 August
bullish MACD crossover]] occurred as the adjusted close declined 3.67% from 3 August to USD 101.20.
That is a short-horizon momentum improvement, not evidence of a new fundamental catalyst. At the
fresher 5 August USD 101.06 close, MACD was -5.25 above its -6.17 signal, RSI was 49.52 and no threshold
alert remained active. The price stayed below the 50-day SMA of USD 111.52 but above the 200-day SMA of
USD 67.95. The alert is therefore **constructive timing inside a still-incomplete trend recovery**, not
a valuation-based entry signal.

## Valuation

Template: `mature_compounder`; method: `earnings_multiple`; horizon: 12 months.

The cases normalize earnings around the Q2 USD 0.42 non-GAAP EPS and Q3 USD 0.38 guidance rather than
capitalizing the escrow-share mark-to-market loss or assuming one quarter's growth persists unchanged.
They use USD 1.50/USD 2.50/USD 3.50 of normalized forward EPS and 22x/32x/38x multiples. The range
reflects Intel's valuable franchises and operating leverage, but also foundry execution risk, net debt,
capital intensity, dilution and strong competition. Liquidity is not added separately because these
risks are already embedded in earnings and multiples.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 33 | USD 1.50 EPS at 22x as product growth normalizes, foundry losses and investment stay heavy, and execution or competitive setbacks compress the multiple. |
| Base | 50% | USD 80 | USD 2.50 EPS at 32x as product demand remains healthy, yield and utilization improve, and external foundry grows gradually without yet earning mature returns. |
| Bull | 25% | USD 133 | USD 3.50 EPS at 38x as AI compute demand, product share, advanced-node execution and credible external-foundry wins produce substantial operating leverage. |

The weighted value is USD 81.50, about 19.4% below the USD 101.06 mark. The base case is about 20.8%
below market, the bear case implies roughly 67.3% downside, and the bull case offers about 31.6% upside.
Medium confidence further reduces the usable expected return. Improved quality and timing cannot justify
an entry when expected return, base return, downside payoff and margin of safety remain unfavorable.

## Catalysts, risks and invalidation

Catalysts are delivery near the top of Q3 guidance, sustained DCAI growth, product-share stabilization,
further yield and cycle-time gains, a credible advanced-node ramp, external-foundry customer wins,
margin expansion, and free-cash-flow recovery after the investment peak. A lower stock price can create
an opportunity without any thesis upgrade.

Invalidate or downgrade if product competitiveness or market share deteriorates, process or packaging
roadmaps slip, external-foundry demand fails to scale, gross margin recovery stalls, partner and capital
funding requirements exceed operating cash generation, leverage rises, dilution worsens, subsidies or
policy support weaken, export controls constrain demand, or restructuring impairs execution.

## Disposition

Status: **watching**, confidence **medium**, expected rating **Hold / Watch**. Revenue growth, margin
recovery and the bullish MACD transition are constructive, but the current price exceeds weighted and
base fair value while downside asymmetry, capital intensity and the absent accepted relationship block
allocation. Review after third-quarter evidence or sooner after a material process, customer, funding,
competitive or policy change, no later than **2026-08-20**.

[[research-catalog|Back to the research catalog]]

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
  "security_id": "security_dfa34d4b9050964b465e",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_dfa34d4b9050964b465e.csv",
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

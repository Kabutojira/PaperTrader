---
title: Intel Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-06"
updated: "2026-09-05"
provenance: "Intel Q2 2026 Form 10-Q and results release; August 2026 equity-offering Form 8-K; canonical market and FX caches"
security_id: security_dfa34d4b9050964b465e
issuer_id: issuer_e5ff2f53cd2ac8db4f85
confidence: medium
next_review: "2026-10-05"
---

# Intel Corporation common stock

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

```echart
{
  "schema_version": 1,
  "chart_id": "intc-q2-operating-recovery-2026",
  "kind": "series",
  "title": "Second-quarter revenue, gross profit, and GAAP operating income",
  "description": "Intel's second-quarter comparison shows materially higher revenue and gross profit and a swing to positive GAAP operating income, supporting operational recovery while one quarter does not establish durable foundry economics.",
  "as_of": "2026-06-27",
  "sources": [
    {
      "label": "Intel second-quarter 2026 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/50863/000005086326000108/intc-20260627.htm",
      "observed_at": "2026-09-04T06:38:08Z"
    }
  ],
  "notes": [
    "Values are GAAP USD billions for the three months ended June 28, 2025 and June 27, 2026.",
    "The reported 2026 net loss is dominated by a non-cash mark-to-market loss; operating income is the cleaner operating comparison."
  ],
  "x_axis": {"type": "category", "label": "Second quarter", "values": ["2025", "2026"]},
  "y_axes": [{"label": "USD billions", "unit": "USD bn", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["12.859", "16.128"]},
    {"name": "Gross profit", "render": "bar", "y_axis": 0, "values": ["3.542", "6.509"]},
    {"name": "GAAP operating income", "render": "line", "y_axis": 0, "values": ["-3.176", "1.796"]}
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "intc-scenario-values-20260905",
  "kind": "series",
  "title": "Scenario fair values versus the current market mark",
  "description": "The current mark remains above both base and probability-weighted fair value after incorporating the equity raise, so the post-crossover price rebound does not create a valuation-supported entry.",
  "as_of": "2026-09-04",
  "sources": [
    {
      "label": "Intel second-quarter 2026 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/50863/000005086326000108/intc-20260627.htm",
      "observed_at": "2026-09-04T06:38:08Z"
    },
    {
      "label": "Intel August 2026 equity-offering Form 8-K",
      "url": "https://www.sec.gov/Archives/edgar/data/50863/000119312526346806/d117670d8k.htm",
      "observed_at": "2026-09-04T06:38:08Z"
    },
    {"label": "Canonical PaperTrader market mark", "observed_at": "2026-09-05T17:14:55Z"}
  ],
  "notes": [
    "Bear, base and bull probabilities are 25%, 50% and 25%; their probability-weighted fair value is USD 79.50.",
    "Scenario values apply 16x, 20x and 25x to USD 2.00, USD 3.90 and USD 5.20 normalized forward diluted EPS, respectively.",
    "Normalized EPS explicitly allows for the approximately 4.8% increase from the completed August offering relative to June 27 common shares outstanding."
  ],
  "x_axis": {"type": "category", "label": "Case", "values": ["Bear", "Weighted value", "Base", "Current mark", "Bull"]},
  "y_axes": [{"label": "USD per share", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [{"name": "Value", "render": "bar", "y_axis": 0, "values": ["32.00", "79.50", "78.00", "95.80000305175781", "130.00"]}]
}
```

## Identity

- Immutable security: `security_dfa34d4b9050964b465e`
- Issuer: `issuer_e5ff2f53cd2ac8db4f85`
- Instrument: common stock, Nasdaq Stock Market (`XNAS`), USD
- Provider identity: `INTC` / `XNAS` / `USD` / equity

The identity matches the maintained [[security-catalog|security catalog]] and current SEC filing;
the instrument, venue, currency and provider symbol are unchanged, and no duplicate identity was
found. No accepted investment-idea relationship or strategy currently links to this security.

## Changes since prior review

- **Facts and evidence unchanged:** the 17:18 UTC SEC submissions retrieval is byte-identical to the
  morning check. It adds no periodic operating filing or earnings release; the second-quarter filing
  and August offering Form 8-K remain the operating and capital baselines. The canonical market and
  FX caches were refreshed at 17:14 UTC but retain the same September 4 USD 95.80 close and
  USD/EUR 0.8604999780654907 rate used by the immediately preceding assessment.
- **Assumptions and scenario inputs unchanged:** normalized forward diluted EPS remains USD
  2.00/USD 3.90/USD 5.20 at 16x/20x/25x. Fair values remain USD 32/USD 78/USD 130 at
  25%/50%/25% probabilities because the timestamp refresh supplies no new evidence about product
  demand, yield, foundry customers, dilution or post-offering deployment.
- **Scenario outputs unchanged:** the USD 79.50 weighted value remains 17.01% below market and the
  USD 78 base value remains 18.58% below it. Bear downside remains 66.60% and bull upside 35.70%; all
  expected-return, payoff and margin-of-safety failures therefore remain unchanged.
- **Thesis, catalysts, risks, blockers, and gaps unchanged:** product and DCAI recovery remain
  supported; 18A yield, external 14A commitments, margin recovery and cash conversion remain the
  catalysts. Foundry economics, capital intensity, dilution, post-offering cash deployment,
  downside asymmetry, medium confidence, unfavorable timing, valuation and the missing accepted
  idea edge remain unresolved. There is no new contradiction.
- **Rating and portfolio action unchanged:** the deterministic conclusion remains **Sell / Avoid**,
  conviction remains **Watch**, and allocation remains ineligible. The earlier bullish MACD
  transition and September 4 rebound remain noise with modest timing improvement, not grounds for a
  strategy, signal or paper order.
- **Unchanged conclusion:** foundry economics remain unproven and watchlist monitoring remains
  appropriate pending a materially lower price or stronger primary evidence.

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
non-GAAP EPS to USD 0.38. Cash and short-term investments were USD 29.7 billion against USD 50.5
billion of debt at 27 June. First-half operating cash flow was USD 8.1 billion. Quarterly operating
cash flow was USD 7.0 billion, but company-defined adjusted free cash flow was negative USD 8.4
billion after capital spending, finance leases and a large net partner-contribution outflow.

The August offering substantially strengthens liquidity: the base offering generated approximately
USD 19.7 billion net before the exercised over-allotment. It also issued 242,105,262 shares in total,
about 4.8% of the 5.043 billion shares outstanding at June 27. Because proceeds may fund capital
expenditure and working capital, the cash cannot be treated as evidence that 18A/14A or external
foundry investment will earn its cost of capital.

## Alert review: opportunity, risk, or noise?

The [[inbox/market-security_dfa34d4b9050964b465e-macd_cross_above_signal-7ecada46ac6f|3 September
bullish MACD crossover]] covers 2026-08-06 through 2026-09-03. The adjusted close fell 8.16%, from
USD 99.81 to USD 91.67, even as MACD crossed just above its signal line at -3.031 versus -3.228.
RSI was neutral at 45.48 and volume was not anomalous. The close remained below its 20-day and
50-day averages of USD 94.24 and USD 101.35, while staying above the USD 73.85 200-day average.

This is **noise with a modest timing improvement**, not a fundamental opportunity: one lagging
crossover did not reverse the alert-period decline or clear the valuation frontier. The September 4
close rebounded 4.51% to USD 95.80, but that market move arrived without new fundamental evidence and
made the unchanged scenario valuation less attractive. The latest fundamental change remains the
equity raise, which improves liquidity but also dilutes per-share recovery.

## Valuation

Template: `mature_compounder`; method: `earnings_multiple`; horizon: 12 months.

The cases normalize earnings around the Q2 USD 0.42 non-GAAP EPS and Q3 USD 0.38 guidance rather than
capitalizing the escrow-share mark-to-market loss or assuming one quarter's growth persists unchanged.
They use USD 2.00/USD 3.90/USD 5.20 of normalized forward diluted EPS and 16x/20x/25x multiples.
The range reflects valuable franchises and operating leverage, but also approximately 4.8% offering
dilution, foundry execution risk, capital intensity and strong competition. The new cash lowers
financing risk but is not added separately because the EPS paths and multiples already reflect the
funding, reinvestment and execution outcomes.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 32 | USD 2.00 EPS at 16x as product growth normalizes, foundry losses and investment stay heavy, and dilution and competitive setbacks suppress per-share recovery. |
| Base | 50% | USD 78 | USD 3.90 EPS at 20x as product demand remains healthy, yield and utilization improve, and offering proceeds fund a gradual external-foundry ramp without mature returns. |
| Bull | 25% | USD 130 | USD 5.20 EPS at 25x as AI compute demand, product share, advanced-node execution and credible external-foundry wins produce substantial operating leverage after dilution. |

The weighted value is USD 79.50, 17.01% below the USD 95.80 mark. The base case is 18.58% below
market, the bear case implies 66.60% downside, and the bull case offers 35.70% upside. Medium
confidence further reduces the usable expected return. Improved liquidity and timing cannot justify
an entry when expected return, base return, downside payoff and margin of safety remain unfavorable.

## Assessment anchors

- **Thesis 80/100:** multiple current primary sources support the product and DCAI recovery,
  management explicitly cites AI-compute demand, and failure conditions are falsifiable.
- **Business quality 60/100:** product franchises and process assets are differentiated, but
  foundry losses, execution history and competition prevent a higher anchor.
- **Balance sheet 80/100:** the offering substantially strengthens liquidity and lowers near-term
  refinancing risk, though capital expenditure and foundry requirements constrain flexibility.
- **Valuation 40/100:** the September 4 rebound increased overvaluation; expected and base returns
  remain negative and bear downside remains severe.
- **Timing 40/100:** MACD crossed above signal during the payload period and the next session
  rebounded, but the September 4 close remains below its 50-day average and one session does not
  establish a durable catalyst.
- **Liquidity 100/100:** Nasdaq trading liquidity is ample for paper execution.
- **Risk 80/100:** risks are specific and monitored, and liquidity is improved, but foundry and
  capital-allocation outcomes remain uncertain.

## Catalysts, risks and invalidation

Catalysts are delivery near the top of Q3 guidance, sustained DCAI growth, product-share stabilization,
further yield and cycle-time gains, a credible advanced-node ramp, external-foundry customer wins,
margin expansion, and free-cash-flow recovery after the investment peak. A lower stock price can create
an opportunity without any thesis upgrade.

Invalidate or downgrade if product competitiveness or market share deteriorates, process or packaging
roadmaps slip, external-foundry demand fails to scale, gross margin recovery stalls, partner and capital
funding requirements exceed operating cash generation, leverage rises, dilution worsens, subsidies or
policy support weaken, export controls constrain demand, or restructuring impairs execution.

## Idea exposure map

- **Candidate:** [[ideas/idea_ai_compute_networking_hyperscaler_monetization]], positive direction,
  high potential materiality. AI-infrastructure demand can transmit through Xeon server CPUs,
  Ethernet, advanced packaging, foundry wafers and purpose-built silicon; Q2 DCAI revenue rose 59%
  and Intel explicitly cited AI-compute demand when funding additional capital needs. The evidence
  does not yet prove durable margins or external foundry returns. Invalidation: DCAI growth reverses,
  custom accelerators displace Xeon attach, or 18A/14A and packaging demand fail to become cash.
  This is not canonical until bounded relationship research accepts it.
- **Rejected-no-link:** [[ideas/idea_terafab_ai_industrial_stack]] / existing
  [[relationships/relationship_terafab_intc]]. The canonical edge remains rejected because the new
  offering contains no Terafab order, contract, investment, ownership link or quantified economics.
  Invalidation of rejection still requires a binding attributable agreement.
- **Rejected-no-link:** [[ideas/idea_wide_bandgap_power_semiconductors]] and the remaining maintained
  catalog. Intel's general semiconductor, AI, physical-AI and manufacturing exposure does not
  establish material SiC/GaN economics or a specific causal edge to the other ideas without
  customer, contract, product-revenue, ownership or policy evidence.

Exactly one relationship review remains required for the AI-compute candidate; the existing
dependent queue row already provides it, so this retry creates no duplicate. There is no payload
idea and no accepted canonical relationship, so this operation creates no idea-refresh follow-up.

## Disposition

Status: **watching**, confidence **medium**, research rating **Sell / Avoid**, portfolio action
**Avoid**, conviction **Watch**, and allocation eligibility **no**. Revenue growth, margin recovery,
liquidity and the bullish MACD transition are constructive, but the USD 95.80 mark exceeds weighted
and base fair value while downside asymmetry, capital intensity and the absent accepted relationship
block allocation. Review after third-quarter evidence or sooner after a material process, customer,
capital-allocation, competitive or policy change, no later than **2026-10-05**.

## Sources

- [Intel Q2 2026 earnings release](https://www.sec.gov/Archives/edgar/data/50863/000005086326000105/q226earningsrelease.htm)
- [Intel Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/50863/000005086326000108/intc-20260627.htm)
- [Intel August 2026 equity-offering Form 8-K](https://www.sec.gov/Archives/edgar/data/50863/000119312526346806/d117670d8k.htm)
- [Intel SEC submissions index](https://data.sec.gov/submissions/CIK0000050863.json)
- Canonical market and FX files: `data/market/prices/security_dfa34d4b9050964b465e.csv`,
  `data/market/indicators.csv`, `data/market/latest.csv`, and `data/market/fx/USD_EUR.csv`.

[[research-catalog|Back to the research catalog]]

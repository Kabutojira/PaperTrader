---
title: Intel Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-06"
updated: "2026-09-04"
provenance: "Intel Q2 2026 Form 10-Q and results release; August 2026 equity-offering Form 8-K; canonical market and FX caches"
security_id: security_dfa34d4b9050964b465e
issuer_id: issuer_e5ff2f53cd2ac8db4f85
confidence: medium
next_review: "2026-10-04"
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
  "chart_id": "intc-scenario-values-20260904",
  "kind": "series",
  "title": "Scenario fair values versus the current market mark",
  "description": "The current mark remains above both base and probability-weighted fair value after incorporating the equity raise, so the bullish MACD crossover does not create a valuation-supported entry.",
  "as_of": "2026-09-03",
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
    {"label": "Canonical PaperTrader market mark", "observed_at": "2026-09-04T06:09:28Z"}
  ],
  "notes": [
    "Bear, base and bull probabilities are 25%, 50% and 25%; their probability-weighted fair value is USD 79.50.",
    "Scenario values apply 16x, 20x and 25x to USD 2.00, USD 3.90 and USD 5.20 normalized forward diluted EPS, respectively.",
    "Normalized EPS explicitly allows for the approximately 4.8% increase from the completed August offering relative to June 27 common shares outstanding."
  ],
  "x_axis": {"type": "category", "label": "Case", "values": ["Bear", "Weighted value", "Base", "Current mark", "Bull"]},
  "y_axes": [{"label": "USD per share", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [{"name": "Value", "render": "bar", "y_axis": 0, "values": ["32.00", "79.50", "78.00", "91.66999816894533", "130.00"]}]
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

- **Facts and evidence changed:** Intel completed a USD 20 billion underwritten offering of
  210,526,315 shares at USD 95 and the underwriters bought 31,578,947 additional shares. The base
  deal was expected to provide about USD 19.7 billion net; proceeds are for general purposes,
  including capital expenditure and working capital. The current SEC index contains no newer
  periodic operating filing, so the unchanged second-quarter filing remains the operating baseline.
- **Assumptions and valuation changed:** normalized forward diluted EPS is revised from USD
  1.50/USD 2.50/USD 3.50 to USD 2.00/USD 3.90/USD 5.20. The improved operating evidence supports
  more earnings, while approximately 4.8% offering dilution and foundry execution risk constrain
  per-share outcomes. Multiples move from 22x/32x/38x to 16x/20x/25x to avoid capitalizing one strong
  quarter at a proven-compounder multiple. Fair values change from USD 33/USD 80/USD 133 to
  USD 32/USD 78/USD 130 at unchanged 25%/50%/25% probabilities.
- **Scenario outputs changed:** the lower USD 91.67 mark narrows overvaluation, but USD 79.50 weighted
  value remains 13.28% below market and the USD 78 base value remains 14.91% below it. Bear downside
  is 65.09%; bull upside is 41.81%.
- **Thesis, catalysts, risks, blockers, and gaps:** stronger liquidity reduces financing risk, but
  dilution and capital-allocation risk rise before external foundry returns are proven. DCAI demand,
  18A yield and external 14A commitments remain catalysts. Negative expected/base return, downside
  asymmetry, margin of safety and the missing accepted idea edge remain blockers; post-offering cash
  deployment is a new evidence gap.
- **Rating and portfolio action:** deterministic state changes from **Sell / Avoid** to
  **Hold / Watch** as the lower market price and improved balance-sheet score lift the
  confidence-adjusted expected return above the sell threshold. Conviction remains **Watch** and
  allocation remains ineligible because the return, payoff, margin-of-safety and relationship gates
  still fail. The bullish MACD crossover does not justify a strategy, signal or paper order.
- **Unchanged conclusion:** product and DCAI recovery remain supported, foundry economics remain
  unproven, and watchlist monitoring remains appropriate pending a lower price or stronger evidence.

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
crossover does not reverse the alert-period decline or clear the valuation frontier. The latest
fundamental change is the equity raise, which improves liquidity but also dilutes per-share recovery.

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

The weighted value is USD 79.50, 13.28% below the USD 91.67 mark. The base case is 14.91% below
market, the bear case implies 65.09% downside, and the bull case offers 41.81% upside. Medium
confidence further reduces the usable expected return. Improved liquidity and timing cannot justify
an entry when expected return, base return, downside payoff and margin of safety remain unfavorable.

## Assessment anchors

- **Thesis 80/100:** multiple current primary sources support the product and DCAI recovery,
  management explicitly cites AI-compute demand, and failure conditions are falsifiable.
- **Business quality 60/100:** product franchises and process assets are differentiated, but
  foundry losses, execution history and competition prevent a higher anchor.
- **Balance sheet 80/100:** the offering substantially strengthens liquidity and lowers near-term
  refinancing risk, though capital expenditure and foundry requirements constrain flexibility.
- **Valuation 40/100:** the lower mark reduces overvaluation, but expected and base returns remain
  negative and bear downside remains severe.
- **Timing 40/100:** MACD crossed above signal, but the close remains below its 20-day and 50-day
  averages after an 8.16% alert-period decline.
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

Exactly one relationship review is required for the AI-compute candidate. There is no payload idea
and no accepted canonical relationship, so this operation creates no idea-refresh follow-up.

## Disposition

Status: **watching**, confidence **medium**, research rating **Hold / Watch**, portfolio action
**Watch**, conviction **Watch**, and allocation eligibility **no**. Revenue growth, margin recovery,
liquidity and the bullish MACD transition are constructive, but price exceeds weighted and base fair
value while downside asymmetry, capital intensity and the absent accepted relationship block
allocation. Review after third-quarter evidence or sooner after a material process, customer,
capital-allocation, competitive or policy change, no later than **2026-10-04**.

## Sources

- [Intel Q2 2026 earnings release](https://www.sec.gov/Archives/edgar/data/50863/000005086326000105/q226earningsrelease.htm)
- [Intel Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/50863/000005086326000108/intc-20260627.htm)
- [Intel August 2026 equity-offering Form 8-K](https://www.sec.gov/Archives/edgar/data/50863/000119312526346806/d117670d8k.htm)
- [Intel SEC submissions index](https://data.sec.gov/submissions/CIK0000050863.json)
- Canonical market and FX files: `data/market/prices/security_dfa34d4b9050964b465e.csv`,
  `data/market/indicators.csv`, `data/market/latest.csv`, and `data/market/fx/USD_EUR.csv`.

[[research-catalog|Back to the research catalog]]

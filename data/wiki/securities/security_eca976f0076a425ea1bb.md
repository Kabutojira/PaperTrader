---
title: UiPath, Inc. Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-06"
updated: "2026-09-05"
provenance: "source_uipath_q2_fy2027_results_sec_ex99_1; source_uipath_q1_fy2027_10q_sec; deterministic market and FX caches"
security_id: security_eca976f0076a425ea1bb
issuer_id: issuer_179c5fbd81cd6cf197cf
confidence: medium
next_review: "2026-10-03"
---

# UiPath, Inc. Class A common stock

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
  "security_id": "security_eca976f0076a425ea1bb",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_eca976f0076a425ea1bb.csv",
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
  "chart_id": "quarterly-revenue-and-operating-income",
  "kind": "series",
  "title": "Quarterly revenue and GAAP operating income",
  "description": "Like-for-like fiscal Q1 and Q2 results show continued revenue growth and a shift from GAAP operating losses to profits.",
  "as_of": "2026-07-31",
  "sources": [
    {
      "label": "UiPath fiscal Q2 2027 results filed with the SEC",
      "url": "https://www.sec.gov/Archives/edgar/data/1734722/000173472226000047/path-2026731xex991.htm",
      "observed_at": "2026-09-05T10:45:22Z"
    }
  ],
  "x_axis": {"type": "category", "label": "Fiscal quarter", "values": ["Q1", "Q2"]},
  "y_axes": [
    {"label": "Revenue", "unit": "USD millions", "format": "currency", "currency": "USD"},
    {"label": "GAAP operating income (loss)", "unit": "USD millions", "format": "currency", "currency": "USD"}
  ],
  "series": [
    {"name": "FY2026 revenue", "render": "bar", "y_axis": 0, "values": ["356.624", "361.728"]},
    {"name": "FY2027 revenue", "render": "bar", "y_axis": 0, "values": ["418.382", "410.256"]},
    {"name": "FY2026 GAAP operating income (loss)", "render": "line", "y_axis": 1, "values": ["-16.412", "-20.185"]},
    {"name": "FY2027 GAAP operating income", "render": "line", "y_axis": 1, "values": ["27.987", "31.604"]}
  ],
  "notes": [
    "Fiscal Q1 values are the six-month totals less fiscal Q2; all figures use the same issuer definitions and USD basis.",
    "Revenue growth decelerated from 17% in fiscal Q1 to 13% in fiscal Q2, while cost discipline produced a second consecutive GAAP operating profit."
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "valuation-scenarios",
  "kind": "series",
  "title": "Twelve-month valuation scenarios",
  "description": "Bear, base, and bull fair values are compared with the identity-matched 4 September 2026 market close.",
  "as_of": "2026-09-04",
  "sources": [
    {
      "label": "UiPath fiscal Q2 2027 results filed with the SEC",
      "url": "https://www.sec.gov/Archives/edgar/data/1734722/000173472226000047/path-2026731xex991.htm",
      "observed_at": "2026-09-05T10:45:22Z"
    },
    {
      "label": "Canonical PaperTrader identity-matched market cache"
    }
  ],
  "x_axis": {"type": "category", "label": "Scenario", "values": ["Bear (25%)", "Base (50%)", "Bull (25%)"]},
  "y_axes": [
    {"label": "Per-share value", "unit": "USD per share", "format": "currency", "currency": "USD"}
  ],
  "series": [
    {"name": "Fair value", "render": "bar", "y_axis": 0, "values": ["9", "17", "27"]},
    {"name": "4 September close", "render": "line", "y_axis": 0, "values": ["15.1899995803833", "15.1899995803833", "15.1899995803833"]}
  ],
  "notes": [
    "The probability-weighted fair value is USD 17.50; medium-confidence adjustment reduces the expected return available to the decision gate.",
    "Scenario values normalize stock compensation, dilution, reinvestment, and surplus financial assets rather than capitalizing non-GAAP guidance."
  ]
}
```

## Identity

- Immutable security: `security_eca976f0076a425ea1bb`
- Issuer: `issuer_179c5fbd81cd6cf197cf`
- Instrument: Class A common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `PATH` / `XNYS` / `USD` / equity

The identity matches the maintained [[security-catalog|security catalog]]. Canonical relationship state
still contains no accepted investment-idea relationship or strategy for this security.

## Changes since prior review

- **Facts and evidence changed:** fiscal Q2 revenue rose 13% to USD 410.3 million, ARR rose 12% to
  USD 1.938 billion, retention held at 109%, and GAAP operating income reached USD 31.6 million.
  Full-year revenue, ARR and non-GAAP operating-income guidance increased modestly. Hitesh Ramani became
  CFO as Ashim Gupta narrowed his remit to COO, adding an execution transition to monitor.
- **Assumptions changed:** a second profitable quarter and lower stock compensation support modestly
  higher normalized per-share earnings, but revenue growth slowed from 17% and net-new ARR fell from
  USD 49 million to USD 37 million. The model still discounts non-GAAP earnings and preserves a large
  operating reserve against gross cash and securities.
- **Valuation inputs and outputs changed:** bear/base/bull fair values move from USD 8.50/USD 15.50/
  USD 26.50 to USD 9/USD 17/USD 27. Weighted value rises from USD 16.50 to USD 17.50, while the
  reference price rises from USD 13.82 to USD 15.19. Expected return falls from 19.39% to 15.21%; base
  upside is 11.92% and bear downside is 40.75%.
- **Thesis and catalysts:** platform orchestration, stable retention, subscription growth, Maestro Case
  and Maestro Flow, sustained GAAP profitability and raised guidance support the thesis. No disclosed
  agentic-product revenue or reacceleration yet proves the strongest version.
- **Risks, blockers and gaps:** competition, slowing net-new ARR, product-transition execution, leadership
  change, stock compensation, buyback discipline and unquantified agentic monetization remain material.
  There is no evidence hard blocker, but medium confidence, downside payoff, weak asymmetry, timing and the
  absence of an accepted relationship block allocation.
- **Rating and portfolio action:** the fresh assessment remains **Buy / Initiate** as a valuation label but
  **Watch / no action** operationally. No strategy work is justified.
- **Unchanged conclusions:** net financial strength and recurring economics merit coverage; relationship
  and payoff gates still prevent a paper position.

## Current economics and thesis

UiPath sells enterprise automation and orchestration software spanning robotic process automation,
workflow, document processing and agentic tools. The investment mechanism is that a large installed base
standardizes on UiPath to govern both deterministic automations and AI agents, lifting subscription
revenue, retention and per-share cash earnings while the company contains sales and development costs.
The mechanism is falsifiable: weaker retention, stalled ARR growth, cloud and AI competition, or stock
compensation consuming operating gains would impair it.

Fiscal Q2 2027 revenue rose 13% to USD 410.3 million, including USD 266.1 million subscription services,
USD 123.8 million licenses and USD 20.3 million professional services. ARR rose 12% to USD 1.938 billion,
net-new ARR was USD 37 million and retention held at 109%. Revenue growth therefore remains healthy but
decelerated from 17% in Q1, and the lower net-new ARR does not establish agentic reacceleration.

GAAP gross margin was 80%, down from 82%, partly because lower-margin professional services grew sharply.
GAAP operating income improved to USD 31.6 million from a USD 20.2 million loss. Quarterly stock
compensation fell to USD 45.0 million from USD 78.0 million but still exceeded GAAP operating income.
Six-month operating cash flow was USD 162.6 million; Q2 contributed only USD 30.7 million after the
seasonally strong Q1, reinforcing the need to normalize cash conversion.

Cash and marketable securities were USD 1.405 billion at 31 July, with no funded debt shown in the release's
balance sheet and roughly 523.0 million diluted weighted-average shares. Six-month repurchases consumed
USD 268.5 million and acquisitions USD 149.4 million. Net financial strength remains substantial, but
stock compensation and capital-allocation discipline determine how much reaches each share.

## Evidence and market alert

Primary evidence is the [SEC-filed fiscal Q2 2027 results release](https://www.sec.gov/Archives/edgar/data/1734722/000173472226000047/path-2026731xex991.htm),
supplemented for prior-period context by the [fiscal Q1 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1734722/000173472226000041/path-20260430.htm).

The canonical [[inbox/market-security_eca976f0076a425ea1bb-volume_anomaly-502b5b004541|4 September
volume anomaly]] spans 7 August through 4 September and shows only a 0.93% period return. The USD 15.19
close was nevertheless 16.63% below the prior session after fiscal Q2 results, on 104.5 million shares and
a 2.37 volume z-score. RSI fell from 71.04 to 45.27 and MACD moved below its signal. The requested trigger
is therefore a **material adverse earnings-reaction risk signal despite a low endpoint-to-endpoint return**,
not noise: raised guidance and profitability were insufficient for the market's prior expectations.

## Idea exposure map

Canonical accepted edges: **none**. The complete maintained idea catalog and relationship table were
searched; no specific material causal exposure met the threshold for a candidate relationship.

| Pairing | Classification | Reason |
| --- | --- | --- |
| [[ideas/idea_ai_native_smb_financial_operating_systems|AI-native SMB financial operating systems]] | `rejected-no-link` | UiPath supplies broad enterprise automation but does not own the authoritative SMB accounting, payroll, tax or payment rails that define this idea's mechanism. |
| [[ideas/idea_ai_compute_networking_hyperscaler_monetization|AI compute, networking, and hyperscaler monetization]] | `rejected-no-link` | AI adoption may influence automation demand, but UiPath has no direct hyperscaler or networking-capacity economics and is not a material transmission endpoint for this infrastructure thesis. |
| [[ideas/idea_precision_biology_healthcare_automation|Precision biology and healthcare automation]] | `rejected-no-link` | Generic workflow capability does not establish material exposure to regulated discovery, diagnostic, laboratory or procedure economics. |

These rejections prevent superficial references to AI or automation from being represented as accepted
causal relationships. New issuer evidence quantifying a material vertical or infrastructure revenue channel
would justify reconsideration.

## Valuation

Template: `mature_compounder`; method: `earnings_multiple`; horizon: 12 months.

The cases value normalized per-share cash earnings after stock compensation, dilution and reinvestment,
then add conservative surplus financial value after leases, acquisitions and operating needs. Bear uses
USD 0.35 at 19x plus USD 2.35; base uses USD 0.60 at 24x plus USD 2.60; bull uses USD 0.80 at 30x plus
USD 3.00. Continued GAAP profitability supports the higher base input, while slower growth, quarterly cash
seasonality and economic stock compensation cap the multiple and usable cash.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 9 | USD 0.35 normalized per-share cash earnings at 19x plus USD 2.35 surplus value; ARR slows, retention weakens, competition raises spending and dilution persists. |
| Base | 50% | USD 17 | USD 0.60 at 24x plus USD 2.60; ARR grows near low double digits, margins improve, and buybacks broadly offset dilution. |
| Bull | 25% | USD 27 | USD 0.80 at 30x plus USD 3.00; orchestration sustains stronger growth and retention while stock compensation declines as a share of revenue. |

Weighted value is USD 17.50, 15.21% above the USD 15.19 mark. Base upside is 11.92%, bear downside is
40.75%, and bull upside is 77.75%. Medium confidence reduces usable expected return to 11.41%. Expected
and base returns clear headline hurdles, but base-to-bear and expected-to-bear payoff ratios of 0.29 and
0.37 fail even starter asymmetry; bear downside also exceeds the starter bound. The missing accepted
relationship independently blocks allocation. The USD 13.60 base-case buy-below level would provide a
20% discount to base fair value, but price alone cannot resolve the relationship or thesis-evidence gates.

## Catalysts, risks and invalidation

Catalysts are delivery of raised fiscal 2027 guidance, ARR and retention stability, disclosed production
adoption and monetization of Maestro products, sustained GAAP profitability, lower stock compensation as
a percentage of revenue, durable per-share free cash flow and disciplined buybacks.

Invalidate or downgrade if ARR growth or retention weakens materially, agentic products fail to convert
pilots into production revenue, cloud or automation competitors take share, gross margin erodes, sales or
research costs reaccelerate without growth, stock compensation and dilution overwhelm buybacks, capital
allocation consumes net cash without adequate returns, cybersecurity or AI-governance failures impair
trust, or fiscal 2027 guidance is cut.

## Disposition

Status: **watching**, confidence **medium**, valuation label **Buy / Initiate**, operative disposition
**Watch / no action**. Recurring growth, improving profitability and net cash support continued coverage,
but weak downside payoff, the adverse post-results reaction, medium confidence and the absent accepted
relationship block allocation and strategy research. Review after fiscal Q3 results or a material product,
retention, guidance, leadership, capital-allocation or competitive change, no later than **2026-10-03**.

[[research-catalog|Back to the research catalog]]

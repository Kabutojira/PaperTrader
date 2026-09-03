---
title: Ternium S.A. ADS
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-06"
provenance: "source_ternium_q2_2026_results_sec; source_ternium_july_2026_sustainability_6k; source_ternium_q1_2026_results; source_ustr_usmca_joint_statement_20260723; deterministic market cache"
security_id: security_2c779e81c27b78c556bb
issuer_id: issuer_bc5aa26231f1e18e929d
confidence: medium
next_review: "2026-08-20"
---

# Ternium S.A. ADS

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
  "security_id": "security_2c779e81c27b78c556bb",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_2c779e81c27b78c556bb.csv",
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

- Immutable security: `security_2c779e81c27b78c556bb`
- Issuer: `issuer_bc5aa26231f1e18e929d`
- Instrument: ADS, NYSE (`XNYS`), USD; each ADS represents ten ordinary shares
- Provider identity: `TX` / `XNYS` / `USD` / equity

Ternium is a capacity-builder and materials exposure within
[[ideas/idea_nearshoring_friendshoring_manufacturing]]. The accepted
[[relationships/relationship_510158d3d515d91d5c14|nearshoring relationship]] defines the causal
link; deterministic price alerts are market context, not fundamental evidence.

## Changes since prior review

- **New evidence:** Ternium reported Q2 2026 revenue of USD 4.34 billion, adjusted EBITDA of USD
  717 million at a 17% margin, and equity-holder net income of USD 344 million, or USD 1.75 per ADS.
  Steel shipments rose 4% sequentially and year over year to 3.858 million tonnes.
- **Thesis:** Stronger Mexican market conditions, import substitution and recovering commercial
  shipments improve the operating evidence for the accepted nearshoring mechanism. The Pesquería
  steel shop was described as progressing on schedule, but the issuer still disclosed no
  project-specific utilization, customer qualification, return, or attributable earnings.
- **Balance sheet and cash:** Q2 operating cash flow was USD 256 million after a USD 418 million
  working-capital build, below USD 431 million of capex. Ternium moved from USD 327 million net cash
  at March end to USD 112 million net debt at June end after capex and the final 2025 dividend.
- **Valuation:** The prior one-quarter annualization is replaced by a complete cyclical normalized-
  earnings assessment. USD 28/USD 50/USD 78 bear/base/bull values imply USD 51.50 weighted value
  against the fresher USD 53.71 mark. Better results do not create a margin of safety after the rally.
- **Alerts and decision:** From 8 July through 5 August, the adjusted close rose 25.23%; the 5 August
  session added 6.69% on 1.62 million shares. RSI 78.07, a close above the USD 52.19 upper band, and
  a 2.42 volume z-score make the merged alerts adverse entry timing rather than an independent
  signal. The conclusion remains Hold / Watch, with no strategy or paper order.

## Economics and thesis

Ternium produces flat and long steel across Mexico, Brazil, Argentina, Colombia and Central
America. Its Pesquería investment can expand locally compliant Mexican supply for automotive,
appliance, construction and industrial customers. Q2 management said Mexican market fundamentals
strengthened as inventories normalized and measures against unfair imports became more effective;
it also cited new pipeline projects, substitution of Asian imports at several OEMs and public
infrastructure as sources of additional volume.

The mechanism is credible but not pure. Brazil, Argentina, iron ore, currencies, steel prices,
trade policy, Usiminas, non-controlling interests and a large capital program all affect ADS-holder
returns. Q2 consolidated net income was USD 465 million, but only USD 344 million was attributable
to equity holders. Management expects Q3 adjusted EBITDA to rise again on higher shipments and
margin, yet this is forward-looking guidance rather than realized cash conversion.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q2 steel shipments were 3.858 million tonnes, up 4% sequentially and year over year. | Demand and utilization improved, including in Mexico, but company-wide volume does not isolate nearshoring demand. |
| Revenue rose 10% sequentially and year over year to USD 4.34 billion; adjusted EBITDA rose 50% sequentially to USD 717 million. | Price, volume and margin improved together, a meaningful operating confirmation. |
| Equity-holder net income was USD 344 million, or USD 1.75 per ADS. | Attributable earnings improved, but two quarters do not establish mid-cycle earnings. |
| Operating cash flow was USD 256 million after a USD 418 million working-capital build; capex was USD 431 million. | Earnings have not yet translated into self-funding free cash flow during the buildout. |
| Net debt was USD 112 million versus USD 327 million net cash at March end. | Leverage remains modest, but balance-sheet flexibility is trending down. |
| Pesquería's steel shop was progressing on schedule. | Schedule risk eased, while commissioning, customer qualification, utilization and returns remain unproven. |

Primary evidence: [Ternium's SEC-filed Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1342874/000134287426000044/prternium2q2026.htm),
the [8 July 2026 sustainability filing](https://www.sec.gov/Archives/edgar/data/1342874/000155485526001509/MainDocument.htm),
[Q1 2026 results](https://www.sec.gov/Archives/edgar/data/1342874/000134287426000030/prternium1q2026.htm),
and the [23 July U.S.-Mexico USMCA-review statement](https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/joint-statement-ambassador-jamieson-greer-and-mexican-secretary-economy-marcelo-ebrard).

## Valuation, catalysts, and risks

The 12-month valuation uses the repository's `cyclical_commodity` template and
`normalized_earnings` method. It deliberately does not capitalize the annualized USD 2.84 of first-
half ADS earnings as a permanent run rate. The **bear** case uses USD 3.50 normalized ADS earnings
and an 8 times multiple for weak steel pricing, working-capital pressure and ramp friction, yielding
USD 28. The **base** case uses USD 5.00 and 10 times for improved but cyclical margins, yielding USD
50. The **bull** case uses USD 6.50 and 12 times for sustained Mexican volume, favorable pricing and
clean commissioning, yielding USD 78. At 25%/50%/25%, weighted value is USD 51.50 versus the USD
53.71 mark. The base case has 6.91% downside and the bear case 47.87% downside, so payoff asymmetry
and margin of safety fail despite the bull case's 45.22% upside.

Catalysts are further Mexican shipment and margin growth, customer qualification, on-schedule
steel-shop commissioning, working-capital release and operating cash flow above capex. Invalidate
the thesis if USMCA or tariffs fragment rather than support regional demand, imports pressure
prices, commissioning slips, customers do not qualify or use capacity, working capital stays
elevated, or Usiminas, currencies, litigation and non-Mexican operations absorb the benefit.

## Disposition

Status: **watching**, allocation eligibility **ineligible**, conviction tier **watch**, confidence
**medium**. Canonical conclusion: **Hold / Watch**. Results materially improved, the accepted
relationship remains current, and the balance sheet is still manageable. Nevertheless, negative
weighted and base returns, severe bear asymmetry, no margin of safety, incomplete project-level
economics, and overbought post-results timing block allocation and strategy work. Review by
**2026-08-20**, or earlier after material commissioning, cash-conversion, trade-policy, or pricing
evidence. See the complete [[research-catalog]] and append-only [[log]].

---
title: Ternium S.A. ADS
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-09-06"
provenance: "source_ternium_h1_2026_financials_sec; source_ternium_q2_2026_results_sec; source_ternium_july_2026_sustainability_6k; source_ternium_q1_2026_results; source_ustr_usmca_joint_statement_20260723; deterministic market cache"
security_id: security_2c779e81c27b78c556bb
issuer_id: issuer_bc5aa26231f1e18e929d
confidence: medium
next_review: "2026-09-20"
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

The bullish MACD crossover improves short-term momentum, but the USD 58 close is above both the
USD 57.55 upper Bollinger band and the unchanged USD 51.50 probability-weighted fair value. That
combination is adverse entry timing rather than evidence that normalized earnings changed.

```echart
{
  "schema_version": 1,
  "chart_id": "quarterly-operating-recovery",
  "kind": "series",
  "title": "Quarterly shipments, sales, and adjusted EBITDA",
  "description": "Ternium's second-quarter recovery combined higher shipments with stronger sales and adjusted EBITDA.",
  "as_of": "2026-06-30",
  "sources": [
    {
      "label": "Ternium second-quarter and first-half 2026 results filed with the SEC",
      "url": "https://www.sec.gov/Archives/edgar/data/1342874/000134287426000044/prternium2q2026.htm",
      "observed_at": "2026-09-06T14:48:45Z"
    }
  ],
  "x_axis": {
    "type": "category",
    "label": "Quarter",
    "values": ["Q2 2025", "Q1 2026", "Q2 2026"]
  },
  "y_axes": [
    {"label": "USD million", "unit": "USD million", "format": "currency", "currency": "USD"},
    {"label": "Steel shipments", "unit": "thousand tons", "format": "decimal"}
  ],
  "series": [
    {"name": "Net sales", "render": "bar", "y_axis": 0, "values": ["3947", "3934", "4340"]},
    {"name": "Adjusted EBITDA", "render": "line", "y_axis": 0, "values": ["403", "479", "717"]},
    {"name": "Steel shipments", "render": "line", "y_axis": 1, "values": ["3719", "3709", "3858"]}
  ],
  "notes": [
    "Adjusted EBITDA is the issuer's non-GAAP measure; net sales and shipments use the issuer's consistent quarterly definitions.",
    "The three observations show recovery, not a complete steel cycle, so valuation continues to use normalized rather than annualized peak earnings."
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "valuation-scenarios-versus-market",
  "kind": "series",
  "title": "Valuation scenarios versus the September market price",
  "description": "The unchanged normalized-earnings scenarios leave both base and probability-weighted value below the September 4 adjusted close.",
  "as_of": "2026-09-04",
  "sources": [
    {
      "label": "Ternium Q2 and H1 2026 SEC filings",
      "url": "https://www.sec.gov/Archives/edgar/data/1342874/000134287426000046/a2026junternium6-k.htm",
      "observed_at": "2026-09-06T14:48:45Z"
    },
    {
      "label": "PaperTrader deterministic adjusted market cache",
      "observed_at": "2026-09-06T13:51:39Z"
    }
  ],
  "x_axis": {
    "type": "category",
    "label": "Reference",
    "values": ["Bear", "Base", "Weighted value", "Market price", "Bull"]
  },
  "y_axes": [
    {"label": "USD per ADS", "unit": "USD", "format": "currency", "currency": "USD"}
  ],
  "series": [
    {"name": "Value", "render": "bar", "y_axis": 0, "values": ["28", "50", "51.5", "58", "78"]}
  ],
  "notes": [
    "Each ADS represents ten ordinary shares.",
    "Bear, base, and bull probabilities remain 25%, 50%, and 25%; the market price is not assigned a scenario probability.",
    "The chart is presentation only and does not feed the assessment or allocation state."
  ]
}
```

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

- **Evidence:** The SEC-filed consolidated interim statements confirm the first-half income
  statement, share count, debt, liquidity and contingent-liability detail used in the prior review.
  The SEC submissions index shows no later operating-results filing through 6 September; the
  intervening August filings are specialized-disclosure reports rather than new trading evidence.
- **Facts and thesis:** The last reported operating facts remain Q2 revenue of USD 4.34 billion,
  adjusted EBITDA of USD 717 million, 3.858 million tonnes of steel shipments and USD 344 million
  of equity-holder net income. Mexican demand and import substitution still support the accepted
  nearshoring mechanism, but Pesquería utilization, customer qualification and project returns
  remain undisclosed. The thesis score and medium confidence are unchanged.
- **Balance sheet, catalysts, risks, blockers and gaps:** June net debt of USD 112 million and Q2
  operating cash flow below capex remain manageable but constraining. Commissioning, customer
  qualification, working-capital release and USMCA policy remain the catalysts; cyclicality,
  non-Mexican exposures, Usiminas, currencies and trade policy remain risks. There is no new hard
  blocker. Medium confidence, normalization uncertainty, weak timing and insufficient margin of
  safety remain soft gaps; none was resolved by the technical crossover.
- **Valuation assumptions and outputs:** USD 28/USD 50/USD 78 bear/base/bull fair values and
  25%/50%/25% probabilities are unchanged because no new fundamental evidence supports revising
  normalized ADS earnings or multiples. Weighted value remains USD 51.50, now compared with the
  fresher USD 58 mark rather than USD 53.71, worsening the expected, base and bear return frontier.
- **Alert, rating and action:** From 7 August through 4 September, adjusted close rose 7.61% to USD
  58. MACD crossed above its signal by 0.0336, while RSI remained overbought at 73.76 and price
  stayed above the USD 57.55 upper band. This is constructive momentum but adverse entry timing,
  not a fundamental opportunity. The conclusion remains **Hold / Watch**, with no strategy,
  signal or paper order.

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
the [SEC-filed consolidated interim financial statements](https://www.sec.gov/Archives/edgar/data/1342874/000134287426000046/a2026junternium6-k.htm),
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
58 mark. Base and bear values are now further below market, so payoff asymmetry and margin of
safety fail despite the bull case remaining above market. The deterministic assessment owns the
exact return calculations.

Catalysts are further Mexican shipment and margin growth, customer qualification, on-schedule
steel-shop commissioning, working-capital release and operating cash flow above capex. Invalidate
the thesis if USMCA or tariffs fragment rather than support regional demand, imports pressure
prices, commissioning slips, customers do not qualify or use capacity, working capital stays
elevated, or Usiminas, currencies, litigation and non-Mexican operations absorb the benefit.

## Disposition

Status: **watching**, allocation eligibility **ineligible**, conviction tier **watch**, confidence
**medium**. Canonical conclusion: **Hold / Watch**. Results materially improved, the accepted
relationship remains economically supported but is overdue for its separate canonical refresh,
and the balance sheet is still manageable. Nevertheless, negative weighted and base returns,
severe bear asymmetry, no margin of safety, incomplete project-level economics, and an overbought
price above the upper band block allocation and strategy work. Review by **2026-09-20**, or earlier
after material commissioning, cash-conversion, trade-policy, or pricing evidence. See the complete
[[research-catalog]] and append-only [[log]].

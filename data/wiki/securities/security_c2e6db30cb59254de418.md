---
title: Xometry, Inc. Class A common stock
type: security
status: maintained
tags:
  - security
  - research
  - risk
created: "2026-09-06"
updated: "2026-09-06"
provenance: "source_xmtr_2025_10k; source_xmtr_q2_2026_10q; source_xmtr_q2_2026_results; source_xmtr_ai_marketplace_20260303; deterministic market cache"
security_id: security_c2e6db30cb59254de418
issuer_id: issuer_dbdde9b294689a9af3d5
confidence: medium
next_review: "2026-10-04"
---

# Xometry, Inc. Class A common stock

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
  "security_id": "security_c2e6db30cb59254de418",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_c2e6db30cb59254de418.csv",
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
  "chart_id": "xmtr-financial-progression-2023-2025",
  "kind": "series",
  "title": "Xometry growth is producing improving, but still negative, GAAP operating leverage",
  "description": "Audited annual revenue, gross profit and operating loss. Revenue and gross profit expanded while the operating loss narrowed, but GAAP operating profitability was not reached.",
  "as_of": "2025-12-31",
  "sources": [
    {"label": "Xometry 2025 Form 10-K", "url": "https://www.sec.gov/Archives/edgar/data/1657573/000119312526066959/xmtr-20251231.htm", "observed_at": "2026-09-06T13:57:12Z"}
  ],
  "notes": [
    "USD millions; values are rounded from audited USD thousands.",
    "Operating loss is shown as a negative value and includes stock-based compensation."
  ],
  "x_axis": {"type": "category", "label": "Financial year", "values": ["2023", "2024", "2025"]},
  "y_axes": [{"label": "Financial result", "unit": "USD million", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["463.406", "545.529", "686.631"]},
    {"name": "Gross profit", "render": "line", "y_axis": 0, "values": ["178.259", "215.624", "268.773"]},
    {"name": "Operating loss", "render": "line", "y_axis": 0, "values": ["-73.6", "-56.149", "-45.516"]}
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "xmtr-valuation-scenarios-2026",
  "kind": "series",
  "title": "Xometry needs the bull case to offer upside from the current price",
  "description": "Twelve-month per-share fair values from the pre-profit-growth revenue-multiple assessment compared with the 4 September 2026 identity-matched market mark.",
  "as_of": "2026-09-06",
  "sources": [
    {"label": "Xometry Q2 2026 Form 10-Q", "url": "https://www.sec.gov/Archives/edgar/data/1657573/000119312526332776/xmtr-20260630.htm", "observed_at": "2026-09-06T13:57:12Z"},
    {"label": "Xometry Q2 2026 filed results", "url": "https://www.sec.gov/Archives/edgar/data/1657573/000119312526331547/xmtr-ex99_1.htm", "observed_at": "2026-09-06T13:57:12Z"},
    {"label": "Canonical PaperTrader market cache", "observed_at": "2026-09-06T13:51:39Z"}
  ],
  "notes": [
    "Scenario probabilities are 25% bear, 50% base and 25% bull; probability-weighted fair value is USD87.50.",
    "Fair values model revenue growth, gross-margin durability, cash conversion, net liquidity and dilution; deterministic code calculates returns and eligibility."
  ],
  "x_axis": {"type": "category", "label": "Scenario", "values": ["Bear", "Base", "Bull"]},
  "y_axes": [{"label": "Fair value per Class A share", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Scenario fair value", "render": "bar", "y_axis": 0, "values": ["50", "85", "130"]},
    {"name": "Current price", "render": "line", "y_axis": 0, "values": ["92.52999877929688", "92.52999877929688", "92.52999877929688"]}
  ]
}
```

Comparable peer multiples, marketplace cohort retention and AI-attributed order conversion are omitted because the bounded primary evidence does not provide a common, current definition across three or more observations.

## Research status

Research is complete through the quarter ended 30 June 2026 and the 4 September 2026 market close. The schema-version-two assessment uses the `pre_profit_growth` template and `revenue_multiple` method. The evidence supports a **Hold / Watch** conclusion, not allocation: the base and probability-weighted values are below the market price, downside is material, confidence is medium and the causal relationship to AI-generated physical creation remains pending. No strategy, signal or paper order is justified.

## Identity and instrument

- Immutable security: `security_c2e6db30cb59254de418`
- Canonical issuer: `issuer_dbdde9b294689a9af3d5`
- Instrument: Xometry, Inc. Class A common stock, Nasdaq primary listing (`XNAS`), USD
- Provider identity: `XMTR` / `XNAS` / `USD` / equity
- SEC registrant identity: CIK 1657573
- Canonical reference: USD92.52999877929688 adjusted close on 4 September 2026, retrieved successfully at 2026-09-06T13:51:39Z

The canonical security row, provider identity and SEC registrant all identify Xometry Class A common stock. The earlier failed attempt used a conflicting issuer identifier that is not present in the current validated payload; this review preserves the canonical issuer and makes no immutable-identity change.

## Business and marketplace economics

Xometry operates a two-sided manufacturing marketplace. Buyers upload CAD files and configure jobs; the platform prices and routes work across a supplier network. Revenue comes primarily from marketplace transactions, with a smaller supplier-services business. The economic proposition is faster quoting, broad process availability and capacity matching without Xometry owning most production equipment.

Audited revenue grew from USD463.4 million in 2023 to USD545.5 million in 2024 and USD686.6 million in 2025. Gross profit increased from USD178.3 million to USD268.8 million over the same period, while GAAP operating loss narrowed from about USD73.6 million to USD45.5 million. Operating cash flow turned positive in 2025, but stock compensation increased and GAAP profitability remained absent.

Q2 2026 revenue was USD229.3 million, up 41%, with USD87.2 million gross profit and a USD5.5 million GAAP operating loss. Marketplace revenue grew 45%; active buyers rose 20% to 89,557 and accounts spending at least USD50,000 increased 23% to 2,039. Adjusted EBITDA reached USD14.1 million, but the non-GAAP result does not remove the economic cost of equity compensation, and GAAP net loss remained USD5.3 million.

## AI-native mechanism and competitive position

The issuer says its models combine geometry, quote configuration, customer history, supplier performance and delivery outcomes to predict lead times and personalize pricing. That is evidence of a closed data loop: more jobs can improve pricing and routing decisions, which can improve buyer experience and supplier utilization. It is a plausible marketplace advantage because geometry and actual fulfillment outcomes are difficult to reproduce from public data alone.

The evidence does not disclose model accuracy, price-improvement lift, AI-originated design demand, buyer retention by cohort or incremental contribution margin. The phrase “AI-native” therefore describes architecture rather than a proven incremental earnings stream. Traditional contract manufacturers, vertically integrated digital manufacturers and other sourcing platforms can compete on price, lead time, quality and customer relationship. Supplier fragmentation can create breadth, but it also requires quality control and leaves some economics with suppliers.

## Balance sheet, dilution and cash conversion

At 30 June 2026, cash and marketable securities were USD516.7 million and convertible notes were USD328.7 million. This is adequate net liquidity, but not pure downside protection: the June financing materially increased both liquidity and potential dilution. The filing reports 57.0 million issued common shares before treasury shares, and continuing stock compensation adds dilution even if operating cash flow remains positive.

First-half operating cash flow was USD17.5 million. That improvement matters, but one half does not establish durable free-cash-flow conversion at the current valuation. The key test is whether marketplace gross profit can keep growing faster than sales, support, product-development and administrative costs after normalizing equity compensation.

## Valuation

A revenue-multiple framework is appropriate while GAAP earnings remain negative. It uses the latest filing for liquidity and dilution, annual and quarterly operating evidence for growth and margin trajectory, and explicit per-share outcomes rather than treating enterprise value as equity value.

- **Bear — USD50, 25% probability.** Growth decelerates toward the low teens, marketplace gross margin fails to expand, cash conversion weakens and dilution approaches 60 million shares; roughly three times forward revenue plus reduced net cash.
- **Base — USD85, 50% probability.** Revenue grows around 20%, gross margin remains near the high-thirties, operating leverage continues but GAAP profitability remains limited, and dilution reaches about 59 million shares; roughly four-and-a-half times forward revenue plus net liquidity.
- **Bull — USD130, 25% probability.** Revenue growth remains near 30%, data-driven pricing and routing lift gross profit, durable positive free cash flow emerges and dilution is contained; roughly six times forward revenue plus net liquidity.

The weighted value is USD87.50 versus USD92.53. The base case is also below the market price, while the bear case implies substantial downside. This is not a sufficient margin of safety for a new paper position.

## Idea exposure map

### Candidate awaiting relationship review

- [[ideas/idea_ai_driven_democratization_physical_creation]] — **candidate; positive; potentially high materiality.** Mechanism: easier AI-generated geometry can increase demand for instant manufacturability feedback, quoting, process selection and outsourced fulfillment; Xometry can capture value only if generated designs become production-ready orders and its marketplace economics improve. Evidence confirms the closed-loop quoting and fulfillment architecture but not AI-attributed conversion. Invalidation: no measurable AI-originated order growth, deteriorating marketplace gross margin, poor supplier outcomes or design tools routing demand elsewhere. The canonical relationship is not yet accepted, and the already queued dependent relationship review remains the only authority for that edge.

### Evaluated but rejected in this review

- [[ideas/idea_nearshoring_friendshoring_manufacturing]] — **rejected-no-link for now.** A distributed supplier network could route localized capacity, but current bounded evidence does not quantify reshoring-driven revenue, domestic capacity exposure or a material policy sensitivity.
- [[ideas/idea_terafab_ai_industrial_stack]] — **rejected-no-link.** Xometry is an indirect procurement marketplace rather than a demonstrated owner of the constrained power, semiconductor or factory-automation bottlenecks in that thesis.
- [[ideas/idea_humanoid_robotics_embodied_ai_components]] — **rejected-no-link.** Prototype demand is conceivable, but no primary evidence shows material robotics revenue or customer concentration.

The complete maintained idea catalog was searched. Other ideas lacked a specific, material causal transmission mechanism under the available primary evidence and were rejected rather than presented as thematic exposure.

## Catalysts

- Marketplace revenue and gross profit continue to outgrow total revenue while larger-account adoption deepens.
- GAAP operating profitability and sustained free-cash-flow conversion emerge without accelerating stock compensation.
- Xometry discloses measurable improvements in quote accuracy, lead-time reliability, repeat ordering or AI-originated design-to-order conversion.
- Net retention, cohort economics or enterprise-wallet expansion demonstrate durable marketplace effects.

## Risks and contrary evidence

- The current valuation already discounts continued high growth; base and weighted values are below the market mark.
- GAAP losses and stock compensation mean adjusted EBITDA can overstate owner economics.
- Convertible financing and equity issuance increase per-share dilution risk.
- Manufacturing demand is cyclical and can be delayed by weak industrial activity or customer budgets.
- Buyer and supplier multi-homing can limit network effects; quality failures can damage trust and increase support costs.
- AI design tools may create more concepts without creating manufacturable, paid orders, or may route demand to competing fulfillment channels.

## Invalidation and monitoring

Invalidate the positive operating thesis if marketplace growth falls below total-company growth for two reported quarters, active-buyer or larger-account growth stalls materially, gross margin deteriorates without a temporary explanation, or operating cash flow reverses while dilution accelerates. Invalidate the proposed AI-physical-creation link if primary evidence fails to connect easier design creation to completed manufacturing orders or if fulfillment economics worsen as demand scales.

Upgrade only if a lower price or stronger primary evidence raises both base and confidence-adjusted expected returns above the canonical gates, downside payoff improves, cash conversion persists and the candidate relationship is accepted. Downgrade if growth, gross profit, buyer quality, supplier performance, cash conversion or dilution deteriorates. Review by 4 October 2026 or earlier after material results, financing or relationship evidence.

## Sources

- [Xometry 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1657573/000119312526066959/xmtr-20251231.htm) — audited annual financials, cash flow, stock compensation and risks; checked 6 September 2026.
- [Xometry Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1657573/000119312526332776/xmtr-20260630.htm) — current operating results, liquidity, convertible notes and share count; checked 6 September 2026.
- [Xometry Q2 2026 filed results](https://www.sec.gov/Archives/edgar/data/1657573/000119312526331547/xmtr-ex99_1.htm) — marketplace growth, buyer metrics and adjusted EBITDA bridge; checked 6 September 2026.
- [Xometry AI-native marketplace release](https://investors.xometry.com/news-releases/news-release-details/xometry-deepens-ai-native-marketplace-advantage-new-enterprise) — issuer description of geometry, quote, supplier and delivery data models; checked 6 September 2026. This issuer claim does not establish incremental AI economics.

Related: [[ideas/idea_ai_driven_democratization_physical_creation]] · [[research-catalog]] · [[security-catalog]]

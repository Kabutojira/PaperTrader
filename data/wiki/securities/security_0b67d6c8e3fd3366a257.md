---
title: Powell Industries, Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-09-05"
updated: "2026-09-05"
provenance: "source_powl_fy2025_10k|source_powl_q1_fy2026_release|source_powl_q2_fy2026_release|source_powl_q3_fy2026_10q|source_powl_q3_fy2026_release"
security_id: security_0b67d6c8e3fd3366a257
issuer_id: issuer_66e23c832f2f063cbcc2
ticker: POWL
venue_mic: XNAS
provider_symbol: POWL
currency: USD
confidence: medium
next_review: "2026-10-05"
---

# Powell Industries, Inc. common stock

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
  "security_id": "security_0b67d6c8e3fd3366a257",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_0b67d6c8e3fd3366a257.csv",
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
  "chart_id": "powl-orders-backlog-fy2026",
  "kind": "series",
  "title": "Orders and backlog accelerated through fiscal Q3 2026",
  "description": "Reported quarterly bookings and period-end backlog show the step-up driven by data-center, utility, LNG and industrial awards.",
  "as_of": "2026-06-30",
  "sources": [
    {"label": "Powell fiscal Q1 2026 results", "url": "https://www.sec.gov/Archives/edgar/data/80420/000008042026000013/ex991-powlq1xfy2026earning.htm"},
    {"label": "Powell fiscal Q2 2026 results", "url": "https://www.sec.gov/Archives/edgar/data/80420/000008042026000063/ex991-powlq2xfy2026earning.htm"},
    {"label": "Powell fiscal Q3 2026 results", "url": "https://www.sec.gov/Archives/edgar/data/80420/000008042026000103/ex991-powlq3xfy2026earning.htm"}
  ],
  "x_axis": {"type": "category", "label": "Fiscal quarter", "values": ["Q1 FY2026", "Q2 FY2026", "Q3 FY2026"]},
  "y_axes": [{"label": "USD millions", "unit": "USD mn", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "New orders", "render": "bar", "y_axis": 0, "values": ["439", "490", "934"]},
    {"name": "Period-end backlog", "render": "line", "y_axis": 0, "values": ["1600", "1800", "2400"]}
  ],
  "notes": [
    "Book-to-bill was approximately 1.7x, 1.7x and 3.0x in fiscal Q1, Q2 and Q3.",
    "Backlog is not guaranteed revenue and may be changed, cancelled or reduced."
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "powl-revenue-margin-fy2026",
  "kind": "series",
  "title": "Revenue growth retained high gross margins",
  "description": "Fiscal 2026 quarterly revenue and gross margin show volume recovery and favorable project execution.",
  "as_of": "2026-06-30",
  "sources": [
    {"label": "Powell fiscal Q1 2026 results", "url": "https://www.sec.gov/Archives/edgar/data/80420/000008042026000013/ex991-powlq1xfy2026earning.htm"},
    {"label": "Powell fiscal Q2 2026 results", "url": "https://www.sec.gov/Archives/edgar/data/80420/000008042026000063/ex991-powlq2xfy2026earning.htm"},
    {"label": "Powell fiscal Q3 2026 results", "url": "https://www.sec.gov/Archives/edgar/data/80420/000008042026000103/ex991-powlq3xfy2026earning.htm"}
  ],
  "x_axis": {"type": "category", "label": "Fiscal quarter", "values": ["Q1 FY2026", "Q2 FY2026", "Q3 FY2026"]},
  "y_axes": [
    {"label": "Revenue", "unit": "USD mn", "format": "currency", "currency": "USD"},
    {"label": "Gross margin", "unit": "%", "format": "percent"}
  ],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["251.184", "296.615", "311.740"]},
    {"name": "Gross margin", "render": "line", "y_axis": 1, "values": ["28.4", "29.6", "30.6"]}
  ],
  "notes": ["Margins benefit from execution, mix and project estimates and should not be extrapolated mechanically."]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "powl-valuation-scenarios-20260905",
  "kind": "series",
  "title": "Twelve-month valuation scenarios",
  "description": "Bear, base and bull fair values are compared with the identity-matched 4 September 2026 close.",
  "as_of": "2026-09-04",
  "sources": [
    {"label": "Powell fiscal Q3 2026 Form 10-Q", "url": "https://www.sec.gov/Archives/edgar/data/80420/000008042026000107/powl-20260630.htm"},
    {"label": "Canonical PaperTrader identity-matched market cache"}
  ],
  "x_axis": {"type": "category", "label": "Scenario", "values": ["Bear (30%)", "Base (50%)", "Bull (20%)"]},
  "y_axes": [{"label": "USD per share", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Scenario fair value", "render": "bar", "y_axis": 0, "values": ["105", "180", "270"]},
    {"name": "4 September close", "render": "line", "y_axis": 0, "values": ["181.1699981689453", "181.1699981689453", "181.1699981689453"]}
  ],
  "notes": [
    "Probability-weighted fair value is USD 175.50; valuation is a bounded scenario analysis, not a price prediction.",
    "The configured 20% valuation haircut produces a USD 144 buy-below price."
  ]
}
```

## Decision

**HOLD / Watch at USD 181.17.** Powell has unusually direct, now contract-backed exposure to the
power-distribution bottleneck created by larger data centers, while electric-utility and LNG demand
diversify the order book. Record bookings, a USD 2.4 billion backlog, roughly USD 800 million of
fiscal-2026 data-center awards, a net-cash balance sheet and expanding margins make the operating
case strong. The current price, however, is about 34.8x trailing split-adjusted earnings and slightly
above the USD 180 base value. The USD 175.50 probability-weighted fair value implies a **-3.13%**
expected return; the base-case margin of safety is **-0.65%**, and the configured **buy-below price
is USD 144**. There is no paper position or strategy.

This is the first full review of Powell in PaperTrader, so there is no prior security thesis or
scenario set to reconcile.

## Immutable identity

- Security: `security_0b67d6c8e3fd3366a257`
- Issuer: `issuer_66e23c832f2f063cbcc2`
- Instrument: common stock, Nasdaq Global Market (`XNAS`), USD
- Provider identity: `POWL` / `XNAS` / `USD` / equity
- Market reference: USD 181.1699981689453 close on 2026-09-04

The April 2026 three-for-one split is reflected in the canonical price history and scenario values.

## Business model and operating structure

Powell designs, manufactures and services custom-engineered systems that distribute, control,
monitor and protect electrical energy. The core portfolio includes power-control rooms and
electrical houses, medium-voltage switchgear, control gear, circuit breakers, motor-control centers,
bus duct, switches, monitoring and communications systems, plus installation, commissioning,
retrofit, repair and spare-parts services. It sells directly to end users and through engineering,
procurement and construction contractors, usually through competitive, project-specific bids.

Powell reports **one operating and reportable segment**. Its chief operating decision-maker does
not receive disaggregated cost or profitability by end market, product or service. Oil & Gas,
Electric Utility, Commercial & Other Industrial, Petrochemical, Light Rail and Other are therefore
end-market revenue categories, not GAAP segments, and no data-center margin is disclosed.

For the first nine months of fiscal 2026, revenue was USD 859.5 million. Oil & Gas excluding
petrochemical contributed USD 316.9 million (36.9%), Electric Utility USD 238.4 million (27.7%),
Commercial & Other Industrial USD 171.4 million (19.9%), Petrochemical USD 68.8 million (8.0%),
Light Rail USD 25.6 million (3.0%) and Other USD 38.5 million (4.5%). Oil & Gas plus Petrochemical
still represented about 44.9% of revenue: Powell is not an AI pure play.

## Real exposure to data centers, AI infrastructure and electrification

The exposure is physical and contract-backed, not merely thematic. Higher-density computing raises
medium-voltage power requirements; Powell supplies the switchgear, packaged electrical rooms,
control and protection systems between on-site or grid-connected generation and data-center loads.
In fiscal Q1 2026, data-center orders exceeded USD 100 million, including an approximately USD 75
million megaproject. Fiscal Q2 added another data-center award above USD 75 million. Fiscal Q3
included Powell's largest order ever, above USD 400 million, for a behind-the-meter design around
on-site generation assets. Management reported **more than USD 800 million of data-center awards
in the first nine months of fiscal 2026**.

The limits matter. Data-center revenue is embedded within Commercial & Other Industrial and is not
separately reported. Commercial & Other Industrial was only 19.9% of nine-month revenue, even though
it had risen to 40% of backlog at June 30. The USD 800 million figure is booked contract value rather
than recognized revenue, includes a single order above USD 400 million, and supplies no disclosed
AI-versus-conventional data-center split. Powell does not own generation assets or compute capacity.

Electrification is broader and more diversified. Electric Utility was 27.7% of nine-month revenue
and 24% of backlog; grid modernization, load growth, generation additions and large-load
interconnections all require Powell-compatible equipment. Oil & Gas excluding petrochemical was a
further 24% of backlog, including renewed LNG activity. This breadth lowers dependence on AI, but
also preserves commodity-project cyclicality.

## Orders, backlog and demand quality

New orders accelerated from USD 439 million in fiscal Q1 to USD 490 million in Q2 and USD 934
million in Q3, versus quarterly revenue of USD 251.2 million, USD 296.6 million and USD 311.7
million. Book-to-bill was about 1.7x, 1.7x and 3.0x. First-nine-month bookings reached USD 1.9
billion, up 112%, and backlog reached USD 2.4 billion, up roughly 73% from September 2025. Powell
expects about USD 1.3 billion of that backlog to convert within twelve months.

Backlog at June 30 was 40% Commercial & Other Industrial, 24% Oil & Gas excluding petrochemical and
24% Electric Utility. The demand signal is therefore broader than one end market, but the recent
step-up is concentrated in a few large awards. Backlog excludes service and maintenance work that
is invoiced as performed, may not be comparable with peer definitions, and can be changed,
cancelled, delayed or reduced. Contract termination terms may reimburse cost and reasonable margin,
but recovery is not guaranteed. Backlog is strong evidence of demand, not guaranteed future profit.

## Margins, cash flow and balance sheet

Fiscal Q3 revenue rose 9% to USD 311.7 million; gross profit rose to USD 95.3 million and gross
margin reached 30.6%. Nine-month revenue was USD 859.5 million, gross profit USD 254.7 million,
operating income USD 164.4 million and net income USD 139.4 million. Quarterly gross margin improved
from 28.4% in Q1 to 29.6% in Q2 and 30.6% in Q3 on project execution, volume and mix.

Nine-month operating cash flow was USD 195.0 million versus USD 106.9 million a year earlier;
capital expenditure was USD 10.4 million, producing approximately **USD 184.7 million of free cash
flow** before acquisitions and financing. Conversion is excellent, but not all structural:
contract liabilities/customer advances increased to USD 466.4 million from USD 297.9 million at
September 2025, while accounts receivable increased to USD 362.4 million from USD 217.1 million.
Large-project milestones can make cash conversion lumpy or reverse as work is performed.

At June 30 Powell held USD 633.6 million of cash and no borrowings, against total equity of USD
756.2 million. Current assets of USD 1.231 billion covered current liabilities of USD 624.7 million
about 2.0x. Its USD 150 million revolver was undrawn, although USD 103.9 million of letters of credit
left only USD 46.1 million immediately available. Surety bonds totaled USD 492.4 million. The balance
sheet can fund working capital and capacity, but guarantees, customer advances and project exposure
make headline cash less freely distributable than ordinary excess cash.

## Customer and project concentration

No individual customer exceeded 10% of consolidated fiscal-2025 revenue. That is reassuring only at
the annual revenue level. Powell says a small number of specific contracts and customers can account
for a significant portion of revenue in a period or at a facility. The single data-center order
above USD 400 million equals at least 16.7% of June backlog, and total reported fiscal-2026
data-center awards above USD 800 million equal roughly one-third of backlog. The customer identities,
cross-project overlap and cancellation protections are not disclosed. Project concentration is
therefore a key soft gap even though reported annual customer concentration remained below 10%.

## Valuation and scenarios

The 2026-09-04 close of USD 181.17 is approximately 34.8x trailing split-adjusted EPS of about USD
5.21. The scenario set uses a mature-compounder earnings multiple because Powell is profitable,
cash-generative and debt-free, but explicitly normalizes unusually strong project margins and the
transition from bookings to revenue:

| Scenario | Probability | Assumption | Fair value | Return vs USD 181.17 |
| --- | ---: | --- | ---: | ---: |
| Bear | 30% | FY2027 normalized EPS USD 5.00 × 21x; mega-project delay/cancellation, gross-margin normalization and weaker industrial mix. | USD 105 | -42.04% |
| Base | 50% | FY2027 normalized EPS USD 6.25 × 28.8x; orderly backlog conversion, high-20s gross margin and controlled capacity execution. | USD 180 | -0.65% |
| Bull | 20% | FY2027 normalized EPS USD 7.50 × 36x; data-center and utility awards broaden, capacity scales cleanly and margins remain near recent highs. | USD 270 | +49.03% |

The probability-weighted fair value is **USD 175.50**, giving an **expected return of -3.13%**.
Medium-confidence adjustment makes the decision input about -2.35%. The base-case margin of safety
is **-0.65%**. PaperTrader's required 20% discount to base value produces a **USD 144 buy-below
price**. A richer multiple could be justified by sustained data-center growth, but capitalizing the
record Q3 order rate before customer breadth and conversion are visible would double-count the
upside.

## Peer comparison: AI power infrastructure

The table combines each peer's latest maintained PaperTrader probability-weighted fair value with a
same-date 4 September 2026 market mark. Peer theses were not silently rewritten; the refreshed return
is a price-only comparison and inherits each page's source date and uncertainty.

| Company | AI-power transmission | Quality / resilience | Growth signal | Current mark | Maintained probabilistic FV | Refreshed expected return | View today |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| **Powell** | Direct MV switchgear and packaged power systems; >USD 800m FY2026 data-center awards | Net cash and strong cash conversion; smaller, project-concentrated | Orders +112% for nine months; backlog USD 2.4bn | USD 181.17 | **USD 175.50** | **-3.13%** | **Best relative risk/reward; HOLD** |
| Vertiv | Most direct compute-facility power and thermal pure play | Strong franchise; materially higher multiple | Fastest pure-play AI growth | USD 280.53 | USD 270.98 | -3.41% | HOLD / Watch |
| Eaton | Broadest high-quality electrical platform | Highest diversification and durable margins; acquisition leverage | Strong data-center and electrical backlog | USD 410.85 | USD 358.75 | -12.68% | AVOID at current price |
| Quanta Services | Grid, transmission and large-load construction | Scarce labor and scale; debt/acquisition/project risk | Record Electric backlog and RPO | USD 624.41 | USD 538.58 | -13.75% | AVOID at current price |
| Schneider Electric | Broad global electrical, automation and data-center stack | Very high quality and diversification | Strong electrification/data-center demand | EUR 288.00 | EUR 250.00 | -13.19% | AVOID at current price |

On quality alone, Eaton and Schneider rank ahead of Powell. On thematic purity and growth, Vertiv
ranks first. On the current combination of balance sheet, contracted growth and valuation, Powell
edges Vertiv, but by too little to clear an absolute buy threshold. The conclusion is therefore not
“buy the cheapest peer”; it is **watch POWL first and require USD 144 or better, or stronger evidence
that base earnings exceed USD 6.25 without concentration or margin deterioration**.

## Catalysts

- Conversion of the USD 1.3 billion twelve-month backlog into revenue at high-20s or better gross margin.
- More data-center awards spread across multiple customers, sites and architectures rather than one megaproject.
- Electric-utility and LNG awards that keep book-to-bill above 1x after the Q3 spike.
- Timely completion of the Jacintoport expansion and disciplined additional capacity without cost overruns.
- Continued free-cash-flow generation after working-capital outflows and customer-advance normalization.
- Better disclosure of data-center revenue, customer breadth, project economics and backlog conversion.

## Risks and thesis invalidation

Principal risks are cancellation or delay of the >USD 400 million data-center project, hidden
customer concentration, fixed-price estimation errors, liquidated damages, labor/capacity bottlenecks,
steel/copper/aluminum inflation, limited or single-source components, EPC/customer credit, tariffs,
cyclical Oil & Gas/LNG spending and valuation compression. At June 30, probable liquidated-damage
exposure was USD 6.3 million and could rise to USD 9.3 million; USD 5.1 million had already reduced
revenue.

Invalidate or materially downgrade the thesis if any of the following occurs:

- backlog falls below USD 1.8 billion or book-to-bill stays below 1x without planned conversion;
- the >USD 400 million data-center award is cancelled, materially delayed or repriced, or data-center orders fail to broaden beyond a few customers;
- gross margin falls below 25% for two consecutive quarters without a clearly temporary mix cause;
- backlog growth fails to convert into revenue, operating cash flow and receivable collections;
- customer advances unwind while receivables and contract assets rise enough to drive sustained negative free cash flow;
- material project losses, liquidated damages, warranty issues or capacity overruns emerge;
- management adds meaningful debt or makes a large acquisition before proving capacity and backlog execution;
- medium-voltage architecture, on-site generation design or customer insourcing reduces Powell content per data-center project.

Upgrade to BUY only if the market price reaches the USD 144 buy-below level with the operating thesis
intact, or if new primary evidence raises normalized base value enough to create at least a 20%
discount without relying on a higher multiple. Downgrade to AVOID if the thesis invalidation tests
trigger or the price rises materially while base earnings evidence does not.

## Sources

- [Fiscal 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/80420/000008042025000152/powl-20250930.htm)
  (`source_powl_fy2025_10k`, checked 2026-09-05).
- [Fiscal Q1 2026 earnings release](https://www.sec.gov/Archives/edgar/data/80420/000008042026000013/ex991-powlq1xfy2026earning.htm)
  (`source_powl_q1_fy2026_release`, checked 2026-09-05).
- [Fiscal Q2 2026 earnings release](https://www.sec.gov/Archives/edgar/data/80420/000008042026000063/ex991-powlq2xfy2026earning.htm)
  (`source_powl_q2_fy2026_release`, checked 2026-09-05).
- [Fiscal Q3 2026 earnings release](https://www.sec.gov/Archives/edgar/data/80420/000008042026000103/ex991-powlq3xfy2026earning.htm)
  (`source_powl_q3_fy2026_release`, checked 2026-09-05).
- [Fiscal Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/80420/000008042026000107/powl-20260630.htm)
  (`source_powl_q3_fy2026_10q`, checked 2026-09-05).
- Canonical market, split and indicator state: `data/market/latest.csv`,
  `data/market/corporate_actions.csv`, `data/market/prices/security_0b67d6c8e3fd3366a257.csv`,
  and `data/market/technical/security_0b67d6c8e3fd3366a257.csv`.
- Peer comparison: maintained PaperTrader security assessments and identity-matched 2026-09-04 marks
  for `ETN`, `VRT`, `PWR` and `SU.PA`.

Next review: **2026-10-05**, or sooner after fiscal Q4 results, a material data-center award change,
capacity decision, backlog cancellation, margin break or working-capital reversal.

[[security-catalog|Tracked securities]] · [[research-catalog|Research catalog]] ·
[[ideas/idea_ai_infrastructure_power|AI infrastructure and power bottlenecks]]

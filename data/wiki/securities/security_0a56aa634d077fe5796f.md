---
title: Applied Materials, Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-08"
updated: "2026-09-03"
provenance: "source_amat_q2_2026_results; source_amat_q2_2026_10q; source_amat_q3_2026_results; source_amat_q3_2026_10q; source_amat_sec_submissions_20260819; deterministic market and FX caches"
security_id: security_0a56aa634d077fe5796f
issuer_id: issuer_0f91c69d2d38e1a7920d
confidence: medium
next_review: "2026-10-03"
---

# Applied Materials, Inc. common stock

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
  "security_id": "security_0a56aa634d077fe5796f",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_0a56aa634d077fe5796f.csv",
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
  "chart_id": "amat-fiscal-2026-quarterly-performance",
  "kind": "series",
  "title": "Fiscal 2026 quarterly revenue and GAAP operating income",
  "description": "The first three quarters show accelerating revenue and operating profit, supporting stronger normalized earnings while also raising the cycle-expectations hurdle.",
  "as_of": "2026-07-26",
  "sources": [
    {
      "label": "Applied Materials fiscal Q3 2026 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm",
      "observed_at": "2026-09-03T12:34:21Z"
    }
  ],
  "notes": [
    "Values are GAAP USD billions for Applied Materials fiscal quarters.",
    "Fiscal Q3 net income includes investment gains; operating income is the cleaner comparable operating measure."
  ],
  "x_axis": {"type": "category", "label": "Fiscal quarter", "values": ["Q1 2026", "Q2 2026", "Q3 2026"]},
  "y_axes": [{"label": "USD billions", "unit": "USD bn", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["7.012", "7.910", "9.115"]},
    {"name": "GAAP operating income", "render": "line", "y_axis": 0, "values": ["1.831", "2.523", "3.075"]}
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "amat-scenario-values-20260903",
  "kind": "series",
  "title": "Scenario fair values versus the current market mark",
  "description": "The current mark is close to base and probability-weighted fair value, leaving little expected return and substantial bear-case asymmetry despite strong execution.",
  "as_of": "2026-09-02",
  "sources": [
    {
      "label": "Applied Materials fiscal Q3 2026 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm",
      "observed_at": "2026-09-03T12:34:21Z"
    },
    {"label": "Canonical PaperTrader market mark", "observed_at": "2026-09-03T12:29:04Z"}
  ],
  "notes": [
    "Bear, base and bull probabilities are 30%, 50% and 20%; their probability-weighted fair value is USD 439.00.",
    "Scenario values apply 22x, 28x and 34x to USD 13, USD 16 and USD 19 normalized forward diluted EPS, respectively."
  ],
  "x_axis": {"type": "category", "label": "Case", "values": ["Bear", "Current mark", "Weighted value", "Base", "Bull"]},
  "y_axes": [{"label": "USD per share", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [{"name": "Value", "render": "bar", "y_axis": 0, "values": ["286.00", "438.4599914550781", "439.00", "448.00", "646.00"]}]
}
```

## Identity

- Immutable security: `security_0a56aa634d077fe5796f`
- Issuer: `issuer_0f91c69d2d38e1a7920d`
- Instrument: common stock, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `AMAT` / `XNAS` / `USD` / equity

Applied Materials' SEC filing identifies its common stock as trading under AMAT on Nasdaq. The
identity matches canonical state and no duplicate immutable identity was found. No canonical idea,
accepted relationship, or strategy is currently linked to this security. Related system context:
[[index]] and [[security-catalog]].

## Changes since prior review

- **Facts and evidence changed:** the August 20 fiscal-Q3 Form 10-Q now confirms the release and
  supplies complete GAAP statements. Fiscal-2026 quarterly revenue rose from USD 7.012 billion to
  USD 7.910 billion and USD 9.115 billion, while GAAP operating income rose from USD 1.831 billion
  to USD 2.523 billion and USD 3.075 billion. The August 27 Form 8-K only appointed a director and
  does not change the thesis.
- **Assumptions and valuation changed:** the withdrawn valuation is rebuilt as a complete
  `mature_compounder` earnings-multiple assessment. Bear/base/bull values are USD 286/USD 448/USD
  646 at 30%/50%/20%, based on USD 13/USD 16/USD 19 normalized forward diluted EPS and 22x/28x/34x
  multiples. The USD 439 weighted value and USD 448 base value are essentially reached at the USD
  438.46 mark; this is not a margin-of-safety entry.
- **Thesis and rating changed:** the materials-intensity and installed-base service thesis remains
  intact, and Q3 strengthens business-quality evidence. The complete result moves from **Unrated /
  Watch** to **Hold / Avoid** because expected return is only 0.12%, base upside 2.18%, bear downside
  34.77%, and the bear/base payoff ratio only 0.06.
- **Catalysts, risks, blockers, and gaps:** valuation support is no longer missing, resolving the
  prior hard blocker. The lower-Bollinger alert is a valuation reset but not a canonical entry:
  customer concentration, China/export controls, cyclicality, working-capital absorption, multiple
  compression, medium confidence, weak timing and an unaccepted idea relationship remain limiting.

## Alert review: opportunity, risk, or noise?

The canonical alert covers August 4 through September 1. The adjusted close fell to USD 441.85,
below the USD 444.00 lower Bollinger band, with RSI 34.04 and MACD 5.15 points below signal. The
September 2 close weakened to USD 438.46, while the active lower-band state cleared as the band
fell to USD 434.78. The price decline from USD 539.14 at the original August 7 review to USD 438.46
is material, but it followed record fiscal-Q3 results rather than a newly disclosed operating
impairment.

The alert is therefore **a valuation opportunity to recheck, but not a current action signal**.
The reset closes the gap to weighted and base value; it does not create adequate expected return,
base upside, bear/base payoff or margin of safety. Technical weakness and the absence of a current
accepted relationship reinforce the Hold / Avoid result rather than override fundamental evidence.

## Economics and thesis

Applied Materials supplies deposition, etch, thermal processing, planarization, metrology,
inspection, packaging and implantation systems used in semiconductor manufacturing. Applied Global
Services supplies spares, service agreements, equipment optimization and factory software. Fiscal
Q3 2026 revenue rose 25% to a record USD 9.115 billion, GAAP gross margin reached 50.3%, GAAP
operating margin reached 33.7%, and diluted EPS rose 43% to USD 3.17.

Semiconductor Systems revenue was USD 7.040 billion and segment operating margin expanded to 37.7%.
Foundry, logic and other represented 67% of segment revenue, DRAM 26%, and flash 7%. AGS revenue was
USD 1.781 billion with a 30.1% operating margin, providing a recurring installed-base counterweight
to equipment cyclicality. Management guided fiscal Q4 revenue to USD 10.25 billion, plus or minus
USD 500 million, with non-GAAP diluted EPS of USD 4.02, plus or minus USD 0.20.

The thesis is that more complex leading-edge logic, DRAM and advanced packaging raise materials-
engineering intensity, while the installed base compounds service demand. The counter-thesis is
that the current price capitalizes prolonged above-cycle growth despite customer concentration,
China and export-control exposure, semiconductor cyclicality, supply execution and weak recent
free-cash-flow conversion.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q3 revenue rose 25% and GAAP operating margin expanded 3.1 points to 33.7%. | Demand and pricing converted into strong operating leverage. |
| Semiconductor Systems revenue was USD 7.040 billion; AGS revenue was USD 1.781 billion. | Product leadership and installed-base services both contributed. |
| Cash plus investments was USD 14.501 billion versus USD 6.444 billion total debt at July 26. | Net financial strength provides substantial downside resilience. |
| Two customers represented 21% and 15% of fiscal-2026 revenue through Q3. | Concentration can amplify spending-cycle volatility. |
| China represented 28% of Q3 revenue, down from 35% a year earlier. | Export controls and regional concentration remain material, current risks. |
| Q3 operating cash flow reached a record USD 3.04 billion and non-GAAP free cash flow was USD 2.33 billion. | Cash conversion improved materially from Q2 and must be normalized in a full valuation review. |

Registered primary evidence: [fiscal Q2 2026 results furnished on Form 8-K](https://www.sec.gov/Archives/edgar/data/6951/000162828026035071/exhibit991q22026earningsre.htm)
(`source_amat_q2_2026_results`) and [fiscal Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/6951/000162828026037227/amat-20260426.htm)
(`source_amat_q2_2026_10q`). The current check adds the [fiscal Q3 2026 results furnished on Form
8-K](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm)
(`source_amat_q3_2026_results`), the [fiscal Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm)
(`source_amat_q3_2026_10q`), and the [current SEC submissions index](https://data.sec.gov/submissions/CIK0000006951.json)
(`source_amat_sec_submissions_20260819`).

## Idea exposure map

- **Candidate — [[ideas/idea_ai_compute_networking_hyperscaler_monetization|AI compute,
  networking, and hyperscaler monetization]], positive direction, high materiality:** AI-led
  leading-edge logic, DRAM and advanced-packaging expansion increases process steps and demand for
  Applied deposition, etch, planarization, metrology and service capacity. Q3 segment mix and growth
  support the transmission, while direct AI-attributed revenue is not disclosed. A bounded
  relationship review must accept or reject this edge; it is not canonical yet. Invalidate it if
  AI-related fab demand proves immaterial, customer capex rolls over, or competition and export
  controls absorb the materials-intensity benefit.
- **Rejected-no-link — [[ideas/idea_terafab_ai_industrial_stack|Terafab and the vertically
  coordinated AI hardware stack]]:** semiconductor-fab equipment is thematically relevant, but the
  maintained idea explicitly lacks an Applied tool order, process selection, customer commitment or
  attributable economics. No relationship review is warranted without new Terafab-specific evidence.
- **Rejected-no-link — [[ideas/idea_japan_sanaenomics_strategic_investment|Japan strategic
  investment]]:** Applied has broad semiconductor exposure, but the policy mechanism is aimed at
  Japanese strategic programs and this review found no attributable Applied order or subsidy.
- **Complete-catalog screen:** the remaining maintained ideas concern end markets or mechanisms
  without a specific material transmission to Applied's disclosed economics. They are rejected for
  this review rather than retained as unexplained thematic associations.

Canonical relationship state remains empty for this security. The candidate above is clearly
separate from accepted state and cannot support allocation or strategy work unless reviewed.

## Valuation, catalysts, and risks

The selected `mature_compounder` template uses normalized earnings rather than mechanically
annualizing fiscal Q3. The **bear case** applies 22x to USD 13 diluted EPS for a fab-spending
slowdown, tighter export controls, concentration volatility, working-capital absorption and
multiple compression, producing USD 286. The **base case** applies 28x to USD 16 as Q4 guidance
broadly converts, leading-edge logic, DRAM, packaging and AGS grow, and margins normalize below the
latest peak, producing USD 448. The **bull case** applies 34x to USD 19 as materials intensity, new
DRAM/packaging systems, service growth and share gains sustain above-cycle economics, producing USD
646. Probabilities of 30%/50%/20% yield USD 439 weighted value.

Against the USD 438.4599914550781 September 2 mark, weighted return is **0.12%**, base return
**2.18%**, bear return **-34.77%**, bull return **47.33%**, base-upside-to-bear-downside is **0.06**,
and margin of safety to base value is only **2.13%**. Confidence is medium: complete filed evidence
supports the model, but normalized cycle earnings and an appropriate premium multiple remain
uncertain. A buy-below level must be derived by deterministic assessment logic rather than prose.

Catalysts are fiscal-Q4 guidance conversion, further leading-edge and DRAM technology transitions,
advanced-packaging adoption, EPIC partner commercialization, AGS growth and sustained cash
conversion. Risks include equipment cyclicality, two-customer concentration, China exposure,
export-control changes and compliance, tariffs, supply constraints, competition, execution of new
products and capacity, working-capital absorption and valuation compression. Invalidate the thesis
if leading-edge and DRAM demand weaken together, AGS growth stalls, gross margin reverses without
productive reinvestment, free cash flow persistently trails earnings, or export restrictions
materially impair addressable demand.

## Disposition

Status: **watching**, confidence **medium**, rating **Hold**, portfolio action **Avoid**, and
**allocation ineligible**. Q3 strengthens the operating thesis, cash conversion and balance-sheet
evidence, while the lower-Bollinger decline removes the former gross overvaluation. It still does
not clear expected-return, base-upside, downside-payoff, margin-of-safety, timing or relationship
gates. No conviction strategy, signal, order or paper trade is justified. Upgrade only after a
lower price or stronger primary-evidence normalized earnings clears every canonical economic gate
and a relationship is accepted; downgrade the operating thesis if leading-edge or DRAM demand
weakens, AGS stalls, margins reverse, cash conversion deteriorates, export restrictions intensify,
or concentration drives material volatility. Review by **2026-10-03**, or sooner after fiscal-Q4
results, a material export-control change, or another large price move.

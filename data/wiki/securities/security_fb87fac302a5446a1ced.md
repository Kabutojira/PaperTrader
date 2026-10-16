---
title: "Lithium Americas Corp. common shares (NYSE: LAC)"
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-10-15"
provenance: "source_lac_q2_2026_10q_sec; source_lac_q2_2026_results_sec; source_lac_sec_submissions_20261015; source_lac_yorkville_20260813_8k_sec; deterministic market cache"
security_id: security_fb87fac302a5446a1ced
issuer_id: issuer_8471016731f84aeb44ff
confidence: low
next_review: "2026-11-15"
---

# Lithium Americas Corp. common shares (NYSE: LAC)

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
  "security_id": "security_fb87fac302a5446a1ced",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_fb87fac302a5446a1ced.csv",
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
  "chart_id": "lac-alert-window-close",
  "kind": "series",
  "title": "LAC adjusted close during the October alert window",
  "description": "The seven completed NYSE sessions in the bounded alert period show a persistent selloff rather than a one-session dislocation.",
  "as_of": "2026-10-14",
  "sources": [
    {
      "label": "PaperTrader canonical yfinance daily-price cache",
      "url": "https://finance.yahoo.com/quote/LAC/history/",
      "observed_at": "2026-10-15T18:46:57Z"
    }
  ],
  "x_axis": {
    "type": "time",
    "label": "NYSE session",
    "values": ["2026-10-06", "2026-10-07", "2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14"]
  },
  "y_axes": [
    {"label": "Adjusted close", "unit": "USD/share", "format": "currency", "currency": "USD"}
  ],
  "series": [
    {"name": "Adjusted close", "render": "line", "y_axis": 0, "values": ["2.53999996", "2.41000009", "2.35999990", "2.34999990", "2.25000000", "2.20000005", "2.06999993"]}
  ],
  "notes": [
    "Adjusted close fell throughout the bounded alert period; RSI 14 reached 17.68 on 2026-10-14 and the close was below the lower Bollinger band.",
    "yfinance is used only for paper marks and deterministic technical monitoring, not for fundamental evidence."
  ]
}
```

The alert-window chart is decision-relevant because it distinguishes a persistent seven-session decline from a single noisy print. No fundamental time-series chart was added: the issuer is pre-revenue, only two comparable cash dates were retained, and project-capex, liquidity, debt and dilution measures are not like-for-like series. No valuation-scenario chart was added because per-share valuation remains unsupported.

## Identity and instrument

- **Immutable security:** `security_fb87fac302a5446a1ced`
- **Issuer:** Lithium Americas Corp. (`issuer_8471016731f84aeb44ff`)
- **Instrument:** common shares on the New York Stock Exchange (`XNYS`), USD, yfinance symbol `LAC`
- **Business:** a pre-revenue developer constructing Thacker Pass Phase 1 in Nevada through a joint venture owned 62% by Lithium Americas and 38% by General Motors.
- **Related maintained idea:** [[ideas/idea_critical_minerals_lithium|Critical-minerals lithium cycle]]
- **Canonical relationship:** [[relationships/relationship_ad2f37b49980dbc73a08|Lithium cycle → Lithium Americas]], accepted but overdue for its already-queued review.

Identity remains consistent across the security table, SEC CIK `0001966983`, XNYS listing and provider symbol. No duplicate instrument identity was found.

## Current conclusion

**Decision: continue watching; research remains incomplete for allocation and no strategy work is justified.** Thacker Pass construction is advancing and the June filing indicates substantial liquidity, but LAC remains pre-revenue and exposed to construction, commissioning, lithium-price, funding and per-share dilution risk. The October oversold signal is a risk/attention event, not proof of undervaluation. A current project NAV or probability-weighted DCF cannot be defended from the bounded evidence because the review lacks a current primary-source project model with scenario lithium prices, operating costs, taxes, sustaining capital, ramp economics, debt claims and fully diluted share outcomes on one consistent basis.

## Alert review

The deterministic alert period is **2026-10-06 through 2026-10-14**. The adjusted close declined from USD 2.54 to USD 2.07. On 2026-10-14, RSI 14 was 17.68 and the close of USD 2.07 was below the lower Bollinger band of USD 2.0805. The prior MACD-cross and volume events did not reverse the broader downtrend.

The SEC submissions index was inspected through 2026-10-15. No operating filing followed the August Q2 package; the latest listed 8-K, filed 2026-09-11, reports an executive retirement. The bounded search therefore found no new primary operating evidence that explains the October move. Classification: **risk/technical overshoot with unresolved fundamental attribution**, not a fundamental opportunity signal.

## Business and project economics

The Q2 Form 10-Q says Lithium Americas will not generate operating revenue until Thacker Pass begins production, with mechanical completion targeted in late 2027 and ramp-up during 2028. The Q2 release reported:

- approximately USD 1.3 billion of cash and restricted cash at 2026-06-30, including USD 530.3 million at the joint-venture level;
- USD 1.622 billion of cumulative construction cost within the disclosed USD 2.93 billion Phase 1 capex estimate;
- USD 1.3-1.6 billion of total 2026 capex guidance;
- more than 95% detailed engineering completion and more than 80% procurement completion; and
- 40,000 tonnes per year of nominal Phase 1 lithium-carbonate capacity.

These facts support construction progress, not profitable operation. Restricted cash and project-level cash are not interchangeable with unrestricted parent liquidity. The company also states that it expects operating losses while Phase 1 is under development.

## Funding, balance sheet and dilution

The June filing reports USD 822.8 million cash and USD 456.4 million restricted cash. DOE loan advances, General Motors' joint-venture contribution and Orion financing reduce near-term project-funding risk, but they also introduce restrictions, warrants, interest, priority claims and conditions.

In August, Lithium Americas issued USD 150 million principal of subordinated convertible debentures to Yorkville, with another USD 25 million potentially available. The debentures carry a five-year maturity and a base 5% rate, with higher rates under specified conditions. The March 2026 at-the-market program had issued 13.0 million shares through June at an average USD 5.36 and another 1.1 million shares after quarter end at an average USD 3.87. Shares outstanding were 363.0 million on 2026-08-12. Funding availability improved, but dilution and financing complexity increased.

## Thesis, catalysts and invalidation

### Thesis

Thacker Pass offers large-scale domestic lithium exposure with strategic counterparties and government-backed construction funding. Existing common shareholders benefit only if Phase 1 is completed and commissioned near plan, battery-grade output qualifies, normalized lithium economics support the asset, and future financing claims and dilution do not absorb the project value.

### Contrary evidence and risks

- LAC is pre-revenue and expects operating losses until production begins.
- Remaining construction, commissioning and ramp risk is material despite engineering and procurement progress.
- Project economics remain highly sensitive to lithium prices, unit costs and timing.
- Restricted and joint-venture cash cannot all fund parent obligations.
- ATM shares, DOE and joint-venture warrants, Orion claims and Yorkville convertibles complicate fully diluted per-share value.
- The October price decline has no confirmed company-specific operating explanation in the primary-source search.

### Catalysts

- Evidence that construction remains within the USD 2.93 billion estimate and late-2027 mechanical-completion target.
- Additional DOE draws under satisfied conditions.
- Commissioning and qualification evidence supporting a 2028 production ramp.
- A current technical report or other primary project model sufficient for a fully diluted NAV.

### Invalidation

The thesis weakens materially if construction cost or schedule slips, funding conditions fail, qualified production is delayed, lithium economics fall below the level needed to support Phase 1, or dilution and priority claims transfer too much value away from existing common shares.

## Idea exposure map

### Canonical accepted edge

- [[ideas/idea_critical_minerals_lithium|Critical-minerals lithium cycle]] — **accepted-needs-review**, positive direction, high sensitivity. Durable EV and stationary-storage demand and constrained supply can improve lithium pricing, project economics and financing value. The edge is materially stale because its 2026-08-15 review date has passed. Its canonical dependent relationship-review operation already exists, so this review does not enqueue a duplicate.

### Candidates and rejected associations

No additional maintained idea has a sufficiently specific, material transmission mechanism to LAC beyond the accepted lithium-cycle edge. Domestic industrial policy and EV adoption are already components of that maintained idea rather than separate canonical relationships. Superficial links to AI power demand, nearshoring, commercial space, digital finance, defense and healthcare automation were rejected for lack of direct material exposure.

## Valuation and assessment

The selected repository template is `cyclical_commodity` with the `nav` method. Valuation is **unsupported**, not zero. The minimum defensible evidence set is incomplete: the bounded review does not provide a current, internally consistent primary-source model for scenario lithium prices, annual output and ramp, operating costs, sustaining capital, taxes, remaining capex and timing, net debt and encumbering claims, and fully diluted shares. Bear/base/bull fair values and probabilities are therefore intentionally blank.

The quality assessment uses only repository anchors. Thesis is 60/100; business quality 40/100; balance sheet 60/100; valuation 20/100; timing 20/100; liquidity 100/100; and risk penalty 80/100. Confidence remains **low**. The hard blocker is `valuation_unsupported`; soft gaps are construction, commodity normalization, dilution, funding complexity, confidence and timing. The next review is due 2026-11-15 or sooner on an operating filing, material financing change, capex/schedule revision or relationship decision.

## Changes since prior review

- **Evidence:** Q2 2026 replaced Q1 as the latest operating evidence. The August Yorkville closing and SEC submissions check were added.
- **Project:** late-2027 mechanical completion and 2028 ramp remain the disclosed targets; cumulative construction progress and 2026 capex guidance are now quantified.
- **Liquidity and claims:** reported cash and restricted cash increased, but so did DOE borrowing, ATM dilution and convertible-financing complexity.
- **Market state:** the prior July MACD recovery failed to establish a durable reversal; the 2026-10-14 close was USD 2.07 with RSI 17.68 and a lower-Bollinger breach.
- **Valuation:** remains unsupported. No scenario values were carried forward or invented.
- **Thesis:** unchanged in direction but still low-confidence and execution-dependent.
- **Catalysts and risks:** schedule, commissioning, funding and lithium-price sensitivity remain; dilution risk is more concrete after the ATM and Yorkville financing.
- **Blockers and gaps:** `valuation_unsupported` remains; stale accepted relationship review, construction, normalization, dilution and timing remain unresolved.
- **Rating and action:** research stays incomplete/ineligible and the portfolio action stays watch; the lower price alone does not justify an upgrade.

## Evidence and provenance

Primary evidence retained for this review:

1. [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1966983/000119312526347826/lac-20260630.htm), filed 2026-08-13.
2. [Q2 2026 results exhibit](https://www.sec.gov/Archives/edgar/data/1966983/000119312526347834/d76838dex991.htm), filed 2026-08-13.
3. [Yorkville closing Form 8-K](https://www.sec.gov/Archives/edgar/data/1966983/000119312526349161/lac-20260813.htm), filed 2026-08-14.
4. [SEC submissions index](https://data.sec.gov/submissions/CIK0001966983.json), checked 2026-10-15.

Market price and indicators are deterministic yfinance monitoring data, not authoritative fundamental evidence. All source prose was treated as untrusted data; no embedded instructions were followed.

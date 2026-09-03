---
title: Vale S.A. sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-13"
updated: "2026-08-25"
provenance: "source_vale_q2_2026_ifrs; source_vale_q2_2026_ifrs_amendment_20260824; source_vale_q2_2026_production; source_vale_q2_2026_results; source_vale_salobo_cpf_20260812; source_vale_fundao_municipalities_20260820"
security_id: security_b2116dcf976c96974d7b
issuer_id: issuer_a3cc545e137b5f2e3a04
confidence: medium
next_review: "2026-09-24"
---

# Vale S.A. sponsored ADR

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
  "security_id": "security_b2116dcf976c96974d7b",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_b2116dcf976c96974d7b.csv",
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

- Immutable security: `security_b2116dcf976c96974d7b`
- Issuer: `issuer_a3cc545e137b5f2e3a04`
- Instrument: sponsored ADR, New York Stock Exchange (`XNYS`), USD
- Provider identity: `VALE` / `XNYS` / `USD` / equity

This assessment compares Vale's diversified iron-ore and base-metals economics with
[[securities/security_1c055eb9b2bb1f5a8ff2|Rio Tinto]] and addresses the deterministic
[[inbox/market-security_b2116dcf976c96974d7b-volume_anomaly-5974ff93bdc6|24 August volume anomaly]].

## Economics and thesis

Vale is a globally significant iron-ore producer with copper and nickel growth options. Its high-grade
ore system, logistics network and S11D assets can support through-cycle cash generation, while the
Bacaba project and other base-metals investments add longer-duration copper exposure. The investment
case is nevertheless dominated by cyclical iron-ore prices, Chinese steel demand, Brazilian operating
and regulatory exposure, capital intensity, and tailings and remediation liabilities.

Current primary evidence supports operational improvement rather than a structural de-risking. In
2Q26, sales rose year over year across iron ore, copper and nickel; realized iron-ore fines prices
averaged USD 95.0/t. Pro forma EBITDA was USD 4.066 billion, free cash flow was USD 1.505 billion,
and net debt was USD 13.173 billion. First-half net income attributable to Vale shareholders was USD
3.268 billion, or USD 0.77 per diluted share. The board also approved USD 1.7 billion of dividends
and interest on capital and extended the buyback, but distributions do not remove commodity or
liability risk.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| 2Q26 pro forma EBITDA was USD 4.066 billion and recurring free cash flow was USD 1.505 billion. | Current cash generation is sound, but one quarter at resilient iron-ore prices is not a mid-cycle base. |
| Iron-ore, copper and nickel sales rose 3%, 10% and 7% year over year. | Execution improved across segments and supports the operating thesis. |
| Realized iron-ore fines price was USD 95.0/t, up 12% year over year. | Price helped results and must be normalized rather than capitalized. |
| Net debt was USD 13.173 billion; expanded net debt was USD 16.677 billion. | Funding is manageable but not a net-cash downside buffer. |
| First-half attributable earnings were USD 3.268 billion and diluted EPS was USD 0.77. | Per-share profitability is current and positive, while commodity sensitivity remains high. |
| 4.256 billion common shares were outstanding in July 2026. | The sponsored ADR represents one common share and scenario values are stated per ADR. |

Registered primary evidence: [Vale 2Q26 performance](https://www.sec.gov/Archives/edgar/data/917851/000129281426004002/valepr2q26_6k.htm)
(`source_vale_q2_2026_results`), [interim IFRS statements](https://www.sec.gov/Archives/edgar/data/917851/000129281426004012/valedfifrs2q26_6k.htm)
(`source_vale_q2_2026_ifrs`), and [2Q26 production and sales](https://www.sec.gov/Archives/edgar/data/917851/000129281426003838/vale20260721_6k1.htm)
(`source_vale_q2_2026_production`).

## Changes since prior review

- **Primary evidence:** Vale's 24 August Form 6-K/A adds only the Exhibit 101 interactive-data file to
  the 31 July interim-financial filing and explicitly leaves all other information unchanged. The
  current 2Q26 financial, production, Salobo and Fundão facts therefore remain the bounded operating
  evidence; no operating, balance-sheet or liability assumption changed.
- **Thesis, catalysts and risks:** The diversified iron-ore and base-metals thesis, Salobo growth
  catalyst, broader Fundão adherence, commodity normalization, net-debt, capital-intensity and
  liability risks remain intact. No catalyst or invalidation condition fired.
- **Market and timing:** The 24 August adjusted close rose to USD 15.04, up 1.76% over the exact 27
  July through 24 August period. Volume reached 49.76 million shares, 81.19% above the prior session,
  and its 2.84 z-score entered the configured anomaly. The move is attention evidence, not a
  fundamental entry, because the monthly price change is modest and the amendment is non-substantive.
- **Valuation and action:** The USD 9.00 / USD 14.50 / USD 20.00 scenarios and USD 11.60 buy-below
  price remain unchanged. Their USD 13.95 weighted value is 7.25% below the new mark, so Vale remains
  Hold / Watch and allocation-ineligible. No strategy or signal is justified.
- **Idea graph, blockers and gaps:** No canonical relationship exists. A complete catalog search now
  identifies [[ideas/idea_critical_minerals_copper|critical minerals and structural copper scarcity]]
  as a plausible but unaccepted positive edge through Vale's copper growth and Salobo execution.
  Relationship review remains a blocker; confidence, cyclical-normalization, margin-of-safety,
  timing and valuation gaps are otherwise unchanged.

Current additional primary evidence: [Salobo CPF execution update](https://www.sec.gov/Archives/edgar/data/917851/000129281426004212/vale20260812_6k.htm)
(`source_vale_salobo_cpf_20260812`) and [Fundão municipal-adherence update](https://www.sec.gov/Archives/edgar/data/917851/000129281426004308/vale20260820_6k.htm)
(`source_vale_fundao_municipalities_20260820`). The [24 August Form 6-K/A](https://www.sec.gov/Archives/edgar/data/917851/000129281426004322/valedfifrs2q26_6ka.htm)
(`source_vale_q2_2026_ifrs_amendment_20260824`) explicitly adds only Exhibit 101 and changes no
other information in the original filing.

## Alert review

The 24 August close was USD 15.04 after a 1.76% rise over the exact 27 July through 24 August period.
Volume reached 49,764,700 shares and its 2.8380 z-score entered the configured anomaly above 2.0.
RSI was neutral at 59.86; MACD was -0.10994 versus a -0.20427 signal and did not create a new
crossover. The move is noise for valuation and action: it is a modest price change with elevated
turnover, no substantive new issuer fact, and a price still above weighted value and buy-below.

## Idea exposure map

- **Candidate — [[ideas/idea_critical_minerals_copper|critical minerals and structural copper
  scarcity]] (positive):** Salobo execution and broader copper-volume growth can transmit structural
  copper tightness into a larger base-metals contribution and cash flow. Current 2Q26 sales growth
  and the Salobo CPF update support plausibility, but iron ore still dominates Vale's economics and
  no canonical edge is accepted. A separate relationship review must test materiality and reject the
  edge if copper remains immaterial to normalized value or project, cost and capital demands absorb
  the commodity benefit.

The complete idea-catalog search rejected the remaining maintained ideas for lack of a specific,
material causal transmission mechanism to Vale's normalized economics.

## Valuation, catalysts, and risks

The `cyclical_commodity` template uses `mid_cycle_cash_flow`. The valuation deliberately normalizes
rather than capitalizes the annualized 2Q26 free-cash-flow rate. Against the 24 August close of USD
15.04, the unchanged 12-month scenarios are:

| Scenario | Probability | Fair value | Assumptions |
| --- | ---: | ---: | --- |
| Bear | 30% | USD 9.00 | Iron ore falls toward a stressed part of the cycle, Chinese steel demand weakens, unit costs rise, and remediation and growth spending absorb cash while net debt remains elevated. |
| Base | 50% | USD 14.50 | Iron ore normalizes below the recent realized price, operational gains and base-metals growth offset part of the price decline, and recurring free cash flow supports distributions without increasing leverage. |
| Bull | 20% | USD 20.00 | Iron ore remains resilient, S11D and other assets deliver volume and cost gains, copper projects advance, and stronger cash conversion reduces net debt while liabilities remain controlled. |

Probability-weighted fair value is USD 13.95, about 7.25% below the mark. The base case is about
3.59% below market, the bear case about 40.16% below market, and the bull case offers about 32.98%
upside. The USD 11.60 buy-below level remains about 22.87% below the current
price. These outputs do not offer the required downside protection or margin of safety.

Catalysts are sustained operating delivery, S11D improvements, Bacaba and other copper milestones,
unit-cost reduction, and net-debt reduction. Invalidate or downgrade the thesis if iron-ore demand
or realized prices deteriorate without cost offsets, production reliability reverses, projects
overrun, remediation or tailings obligations rise materially, net debt increases, or distributions
crowd out high-return reinvestment and liability funding.

## Disposition

Status: **watching**, confidence **medium**. The current filings make valuation supportable, but the
scenario frontier remains ineligible: expected and base returns are below the economic hurdle,
bear/base payoff is poor, the margin of safety is below target, and no accepted causal relationship
exists. The volume anomaly is attention evidence, not a paper-trade signal, and changes no material
gate. Review by
**2026-09-24** or sooner after a material iron-ore price, Chinese-demand, production, project,
remediation, or leverage change. No strategy or signal is justified.

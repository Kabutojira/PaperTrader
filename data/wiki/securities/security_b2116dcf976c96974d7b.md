---
title: Vale S.A. sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-13"
updated: "2026-08-13"
provenance: "source_vale_q2_2026_ifrs; source_vale_q2_2026_production; source_vale_q2_2026_results"
security_id: security_b2116dcf976c96974d7b
issuer_id: issuer_a3cc545e137b5f2e3a04
confidence: medium
next_review: "2026-08-27"
---

# Vale S.A. sponsored ADR

## Identity

- Immutable security: `security_b2116dcf976c96974d7b`
- Issuer: `issuer_a3cc545e137b5f2e3a04`
- Instrument: sponsored ADR, New York Stock Exchange (`XNYS`), USD
- Provider identity: `VALE` / `XNYS` / `USD` / equity

This assessment compares Vale's diversified iron-ore and base-metals economics with
[[securities/security_1c055eb9b2bb1f5a8ff2|Rio Tinto]] and addresses the deterministic
[[inbox/market-security_b2116dcf976c96974d7b-bollinger_below_lower-acc942b6f4a6|Bollinger-band breach]].

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

## Alert review

The 13 August close was USD 13.80, down 4.30% for the session and 6.25% over the canonical
five-session period. It closed below the USD 13.9684 lower Bollinger band with RSI 35.8; volume was
20.6 million shares and did not show a configured volume anomaly. The exact market transition is a
short-term risk and possible mean-reversion setup, but no current primary evidence reviewed here
establishes a company-specific fundamental impairment on 13 August. The breach therefore changes
timing, not the through-cycle thesis or valuation.

## Valuation, catalysts, and risks

The `cyclical_commodity` template uses `mid_cycle_cash_flow`. The valuation deliberately normalizes
rather than capitalizes the annualized 2Q26 free-cash-flow rate. Against the 13 August close of USD
13.80, the 12-month scenarios are:

| Scenario | Probability | Fair value | Assumptions |
| --- | ---: | ---: | --- |
| Bear | 30% | USD 9.00 | Iron ore falls toward a stressed part of the cycle, Chinese steel demand weakens, unit costs rise, and remediation and growth spending absorb cash while net debt remains elevated. |
| Base | 50% | USD 14.50 | Iron ore normalizes below the recent realized price, operational gains and base-metals growth offset part of the price decline, and recurring free cash flow supports distributions without increasing leverage. |
| Bull | 20% | USD 20.00 | Iron ore remains resilient, S11D and other assets deliver volume and cost gains, copper projects advance, and stronger cash conversion reduces net debt while liabilities remain controlled. |

Probability-weighted fair value is USD 14.20, only 2.9% above the mark; medium confidence reduces the
expected return further. The base case offers about 5.1% upside, the bear case about 34.8% downside,
and the USD 10.88 buy-below level is well below the current price. These outputs do not offer the
required downside protection or margin of safety.

Catalysts are sustained operating delivery, S11D improvements, Bacaba and other copper milestones,
unit-cost reduction, and net-debt reduction. Invalidate or downgrade the thesis if iron-ore demand
or realized prices deteriorate without cost offsets, production reliability reverses, projects
overrun, remediation or tailings obligations rise materially, net debt increases, or distributions
crowd out high-return reinvestment and liability funding.

## Disposition

Status: **watching**, confidence **medium**. The current filings make valuation supportable, but the
scenario frontier remains ineligible: expected and base returns are below the economic hurdle,
bear/base payoff is poor, the margin of safety is below target, and no accepted causal relationship
exists. The Bollinger breach is risk evidence, not a paper-trade signal. Review by **2026-08-27** or
sooner after a material iron-ore price, Chinese-demand, production, project, remediation, or leverage
change. No strategy or signal is justified.

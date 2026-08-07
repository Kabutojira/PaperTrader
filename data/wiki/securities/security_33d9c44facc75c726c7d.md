---
title: NVIDIA Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-05"
updated: "2026-08-07"
provenance: "source_nvda_q1_fy2027_10q; source_nvda_q1_fy2027_results; source_nvda_space_computing_20260316; source_nvda_vera_spacexai_20260531; source_spacex_terafab_prospectus_20260605"
security_id: security_33d9c44facc75c726c7d
issuer_id: issuer_7f0f0b334051a9c9a06b
confidence: medium
next_review: "2026-08-19"
---

# NVIDIA Corporation common stock

## Identity

- Immutable security: `security_33d9c44facc75c726c7d`
- Issuer: `issuer_7f0f0b334051a9c9a06b`
- Instrument: common stock, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `NVDA` / `XNAS` / `USD` / equity

NVIDIA supplies accelerated-computing processors, networking, systems, and software. Its economics
are now linked by accepted canonical relationships to
[[ideas/idea_ai_compute_networking_hyperscaler_monetization|AI compute and networking]],
[[ideas/idea_humanoid_robotics_embodied_ai_components|embodied AI]], and
[[ideas/idea_terafab_ai_industrial_stack|Terafab]]. They remain a direct comparison for
cloud-platform capital spending at
[[securities/security_204be2a44063993de1a8|Microsoft]] and for AI-cluster networking at
[[securities/security_6f9a1450edceb9307c9a|Arista Networks]]. The wide-bandgap and AI-drug-
discovery associations were reviewed and rejected because current product relevance does not yet
create material NVIDIA shareholder economics.

## Economics and thesis

The investable thesis is that NVIDIA's integrated GPU, interconnect, networking, systems, and
software platform can retain a large share of expanding AI-infrastructure spending while rapid
product cycles and scale sustain exceptional margins and cash generation. The counterpoint is that
current expectations already require continued hyperscaler and broader AI-factory investment,
flawless Blackwell-to-Rubin execution, adequate power and manufacturing capacity, and limited
competitive or regulatory erosion.

For the quarter ended 26 April 2026, revenue rose 85% year over year and 20% sequentially to USD
81.615 billion. Data Center revenue was USD 75.246 billion, up 92% year over year and 21%
sequentially; compute reached USD 60.4 billion and networking USD 14.8 billion. GAAP gross margin
was 74.9%, operating income was USD 53.536 billion, and operating cash flow was USD 50.344 billion.
These figures strongly support demand, platform breadth, pricing, and operating leverage, although
USD 15.9 billion of equity-security gains inflated GAAP net income and are excluded from normalized
earnings.

## Evidence and decision gates

| Evidence | Interpretation |
| --- | --- |
| Q2 fiscal 2027 revenue guidance is USD 91.0 billion plus or minus 2%, with 74.9%-75.0% gross-margin guidance. | Near-term demand and economics remain strong, but the market already discounts substantial continued growth. |
| Data Center represented about 92% of Q1 revenue; Hyperscale remained about half of Data Center while other AI-cloud, industrial, enterprise, and sovereign customers supplied the balance. | Customer mix is broadening, but AI infrastructure and large-customer capital budgets remain concentrated economic exposures. |
| No Data Center Hopper shipments to China occurred in Q1, and Q2 guidance assumes no China Data Center compute revenue. | Export controls remove a major addressable market and can create inventory, product-design, and license uncertainty. |
| Cash plus marketable debt securities was USD 50.335 billion against USD 8.470 billion total debt; Q1 free cash flow before equipment-financing principal was about USD 48.6 billion. | Net financial strength and cash generation provide substantial resilience and fund research, capacity, repurchases, and dividends. |
| Inventory rose sequentially to USD 25.797 billion, supply-related commitments reached USD 119.0 billion, and cloud-service commitments reached USD 30.0 billion. | Securing supply supports growth but magnifies demand-forecast, transition, counterparty, and obsolescence risk. |
| Rubin is expected to begin shipping in the second half of fiscal 2027. | A successful cadence is a catalyst; delay, yield, quality, or customer-transition friction is a key invalidation path. |

Primary evidence is the [quarterly report filed 20 May 2026](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm)
as `source_nvda_q1_fy2027_10q` and the [SEC-filed Q1 results release](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000051/q1fy27pr.htm)
as `source_nvda_q1_fy2027_results`, both checked 5 August 2026.

## New relationships and Terafab evidence

The accepted [[relationships/relationship_ai_compute_nvda|AI-compute relationship]] is the direct
core edge: accelerated compute, networking, systems and software already produce material revenue,
margin and cash flow. The accepted [[relationships/relationship_humanoid_nvda|embodied-AI edge]] is
smaller and less certain because robot-maker integrations and NVIDIA's safety stack do not quantify
attributable revenue or repeat paid deployment economics.

The accepted [[relationships/relationship_terafab_nvda|Terafab edge]] adds a customer and orbital-
compute option, not a new near-term earnings assumption. NVIDIA's
[space-computing release](https://nvidianews.nvidia.com/news/space-computing)
(`source_nvda_space_computing_20260316`) introduced a Vera Rubin-derived Space-1 module for later
availability. Its [Vera release](https://nvidianews.nvidia.com/news/nvidia-unveils-vera-the-cpu-for-agents)
(`source_nvda_vera_spacexai_20260531`) names SpaceXAI among organizations exploring the CPU. The
[SpaceX prospectus](https://content.spacex.com/cms-assets/FINAL_Documents%20and%20Updates/SpaceX%20-%20EU%20Prospectus%20%28Approved%20by%20Bafin%29%20-%20June%205%2C%202026.pdf)
(`source_spacex_terafab_prospectus_20260605`) expects significant third-party compute sourcing to
continue while describing an ambitious internal mask, logic, memory and packaging workflow.

These sources support near-term platform demand and a long-run substitution risk. They disclose no
NVIDIA order value, SpaceXAI purchase volume, Terafab investment, exclusivity, capacity guarantee or
NVIDIA wafer-production agreement. The prior USD 7.50/USD 9.00/USD 11.00 normalized-EPS scenarios
therefore remain unchanged rather than capitalizing unannounced economics.

## Valuation

The `mature_compounder` template uses a 12-month `earnings_multiple`. Normalized forward earnings
include stock compensation, exclude volatile equity-security gains, and treat the USD 41.865 billion
net cash position as downside support rather than adding it separately to an equity-value multiple.
The scenarios vary revenue growth, operating margin, normalized EPS, and the multiple that investors
may pay after another year of execution. Against the canonical 6 August close of USD
218.99000549316406:

| Scenario | Probability | Fair value | Assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 180.00 | USD 7.50 forward EPS at 24x as AI-infrastructure growth decelerates, China remains unavailable, Rubin or supply execution adds cost, and the valuation multiple compresses. |
| Base | 50% | USD 252.00 | USD 9.00 forward EPS at 28x as Q2 guidance converts, Blackwell remains strong, Rubin ships broadly on schedule, and roughly mid-70% gross margin supports continued cash generation. |
| Bull | 25% | USD 374.00 | USD 11.00 forward EPS at 34x as sovereign, enterprise, networking, and hyperscale demand compound, Rubin expands performance and platform breadth, and margins remain exceptional. |

Probability-weighted fair value remains USD 264.50, about 20.8% above the mark. The base case offers
about 15.1% upside, while the bear case implies about 17.8% downside; base upside to bear downside is
only about 0.85x. The unchanged USD 201.60 buy-below price remains unreached and base-case margin of
safety has narrowed to about 13.1%. The valuation therefore supports continued monitoring but does
not clear the canonical downside-payoff and margin-of-safety frontiers. Medium confidence reflects
the unusually wide outcome range, dependence on sustained customer capital spending, and sensitivity
to both normalized EPS and the terminal multiple.

## Alert review, catalysts, and risks

The canonical mark advanced from USD 211.94 on 4 August to USD 219.22 on 5 August and closed at USD
218.99 on 6 August. The current RSI is 61.38, the close remains below the USD 221.17 upper Bollinger
band, and MACD is 1.9038 versus a -0.0620 signal. The price extension improves momentum but weakens
the valuation frontier; the new relationship evidence is fundamental context rather than the cause
of the full two-session move. It remains neutral-to-positive timing evidence, not a paper-buy signal.

Catalysts are delivery against Q2 guidance, continued Blackwell 300 and networking growth, Rubin
shipments in the second half of fiscal 2027, broader enterprise and sovereign adoption, durable
mid-70% gross margins, and continued conversion of earnings to cash. Risks are export restrictions,
large-customer and AI-capex concentration, dependence on third-party manufacturing and packaging,
power and data-center constraints, rapid product transitions, competition and customer-designed
silicon, USD 119 billion of supply commitments, investment-value volatility, and valuation-multiple
compression.

Invalidate the thesis if customer returns fail to sustain AI infrastructure budgets, Data Center
growth or margins deteriorate materially, Rubin is delayed or fails to win broad adoption, supply
commitments produce material provisions, competing architectures erode platform economics, or
normalized per-share earnings and cash flow cease compounding despite heavy reinvestment.

## Disposition

Status: **watching**, confidence **medium**. Research and scenario valuation are complete, and three
accepted canonical relationships resolve the prior relationship blocker. Strong business quality,
net financial strength and current growth are offset by 17.8% modeled bear-case downside, only about
0.85x base-upside-to-bear-downside, an unreached USD 201.60 buy-below price, a roughly 13.1% base-case
margin of safety and medium confidence. The deterministic economic frontiers therefore keep the
security allocation-ineligible at Watch even after the graph repair. Review by **2026-08-19**, or
sooner after Q2 results,
material export-control changes, Rubin timing evidence, a guidance revision, or a major customer
capital-spending change. No conviction strategy, signal, or paper order is justified.

## Changes since prior review

- **Facts and evidence changed:** NVIDIA introduced a Space-1 Vera Rubin module, named SpaceXAI as a
  prospective Vera adopter, and SpaceX disclosed a Terafab ambition alongside continued third-party
  compute sourcing. These sources establish a product and customer channel, not order volume or
  financial contribution. Q1 filing facts and Q2 guidance remain the newest decisive financial
  evidence.
- **Relationships changed:** AI compute, embodied AI and Terafab are now accepted canonical edges.
  AI drug discovery and wide-bandgap power were reviewed and rejected as current NVIDIA investment
  edges because attributable economics are immaterial or unquantified.
- **Assumptions and scenarios unchanged:** Terafab and orbital evidence does not justify altering
  normalized EPS, multiples or probabilities. Bear/base/bull fair values remain USD 180/USD 252/USD
  374 at 25%/50%/25%, with USD 264.50 probability-weighted fair value.
- **Outputs changed with price:** the reference mark rose from USD 211.94 to USD 218.99. Expected
  return falls from 24.8% to about 20.8%; base upside falls from 18.9% to about 15.1%; bear downside
  widens from 15.1% to about 17.8%; base/bear payoff falls from 1.25x to about 0.85x; and base-case
  margin of safety falls from 15.9% to about 13.1%.
- **Thesis, catalysts and risks changed:** the core AI-platform thesis is stronger at the graph level,
  and SpaceXAI, orbital computing and physical AI add bounded option value. Unannounced customer
  economics, internal customer silicon and Terafab's long-run substitution ambition add explicit
  uncertainty; export, capex, supply and Rubin risks are unchanged.
- **Blockers, gaps, rating and action:** the prior `relationship_pending` blocker is resolved and no
  hard research blocker exists. Medium confidence and concentration remain soft gaps, while economic
  downside-payoff and margin-of-safety frontiers remain unmet. Watching, no strategy and no paper
  action remain unchanged, now for valuation rather than relationship completeness.

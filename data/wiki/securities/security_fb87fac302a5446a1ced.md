---
title: Lithium Americas Corp. common shares
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-07-29"
provenance: "source_lac_q1_2026_10q; source_fae2a4af713687d5cc2b; deterministic market cache"
security_id: security_fb87fac302a5446a1ced
issuer_id: issuer_8471016731f84aeb44ff
confidence: low
next_review: "2026-08-15"
---

# Lithium Americas Corp. common shares

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

## Identity

- Immutable security: `security_fb87fac302a5446a1ced`
- Issuer: `issuer_8471016731f84aeb44ff`
- Instrument: Canadian common shares, New York Stock Exchange (`XNYS`), USD
- Provider identity: `LAC` / `XNYS` / `USD` / equity

The Form 10-Q confirms the dual-listed common shares. This review links them to
[[ideas/idea_critical_minerals_lithium]].

## Economics and thesis

Lithium Americas is a pre-revenue developer whose value is concentrated in its 62%-owned Thacker
Pass joint venture with General Motors. Phase 1 targets late-2027 mechanical completion and a 2028
production ramp. At 31 March 2026 the company reported USD 1.3 billion of capitalized construction
and project costs, including USD 1.1 billion within the technical report's USD 2.93 billion Phase 1
capex estimate. Fiscal-2026 Thacker Pass capex guidance was USD 1.3-1.6 billion.

Funding is substantial but conditional. Cash was USD 758.5 million and restricted cash was USD
449.1 million. GM owns 38% of the joint venture, the DOE loan remains subject to draw conditions,
and the 20-year Phase 1 offtake can cover up to all production based on GM requirements. The company
remains pre-revenue and loss-making, had sold 43.3 million shares through a prior ATM, opened a new
USD 250 million ATM in March 2026, and issued DOE a near-zero-strike warrant tied to 5% of then-
outstanding shares. Strategic support reduces completion risk but does not make the common equity a
funded, undiluted claim on the technical report's project value.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| USD 1.1 billion of the USD 2.93 billion technical-report capex estimate was spent by 31 March 2026. | Material progress, with most cost and commissioning risk still ahead. |
| Fiscal-2026 project capex guidance was USD 1.3-1.6 billion. | Construction remains highly capital intensive before any operating revenue. |
| Mechanical completion targets late 2027; ramp 2028. | No near-term operating cash flow supports the equity. |
| DOE and GM funding, restricted cash, offtake, and warrants fund and encumber the project. | Strategic support reduces funding risk but complicates common-share attribution. |
| 43.3 million ATM shares sold and another USD 250 million program opened. | Dilution is an observed funding mechanism, not a remote risk. |

Primary evidence: [Lithium Americas Q1 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1966983/000119312526222727/lac-20260331.htm) (`source_lac_q1_2026_10q`).

## Valuation, catalysts, and risks

The fresh 28 July 2026 paper mark is USD 2.80, with 5.73 million shares traded; the current 29 July
USD/EUR rate is 0.8782. Those observations support price, FX, and trading-liquidity checks, not
fundamental valuation. No supportable common-share valuation is recorded because the available
evidence does not provide a current project model that reconciles 62% ownership, DOE and other
claims, warrants, offtake pricing, remaining capex, future dilution, ramp probability, and lithium-
price scenarios. Technical-report NPV cannot be treated as equity value, and an arbitrary price
target would conceal rather than resolve those gaps.

The deterministic monitor first recorded entry into the RSI-oversold condition on **2026-07-24**,
after a **26.45%** adjusted-close decline from 25 June to 24 July, at a USD 2.8315 close and trigger
strength of 0.1879. This [[inbox/market-security_fb87fac302a5446a1ced-rsi_oversold-97348588c910|indicator
transition]] corroborates weak momentum and near-term timing risk; it does not explain the move,
establish intrinsic value, or override the financing, dilution, construction, and valuation gates.

The oversold condition strengthened on **2026-07-28**: the USD 2.80 close was down **25.73%** from
29 June, RSI fell to **26.75**, and the daily return was **-3.45%**. Volume was not abnormal
(`z=0.48`), the close remained **11.42% above** the lower Bollinger band, and MACD remained
marginally above its signal line. The [[inbox/market-security_fb87fac302a5446a1ced-rsi_oversold-2aef2a392f63|strengthened
alert]] therefore confirms weak momentum without independent price or volume confirmation. The
unchanged SEC-filed Q1 evidence documents construction progress and substantial liquidity but no
new operating event that explains the observation-period decline. This remains commodity,
financing, dilution, construction, and timing risk rather than a contrarian opportunity.

Catalysts are construction milestones, cost control, DOE draws, commissioning, and qualified
battery-grade production. Invalidate if cost-to-complete rises materially, financing conditions
fail, schedule slips, product qualification misses, lithium prices weaken, or dilution transfers
project value away from current holders.

## Disposition

Status: **watching**, confidence **low**, allocation assessment **ineligible**. The explicit hard
blocker is `valuation_unsupported`; project concentration, cyclical normalization, completion
timing, financing, dilution, and commissioning remain risks. Review by **2026-08-15** after the next
quarterly construction, liquidity, and share-count disclosure. No strategy is proposed because the
full valuation and evidence gate does not pass, and the strengthened oversold condition is not
independently a trade signal.

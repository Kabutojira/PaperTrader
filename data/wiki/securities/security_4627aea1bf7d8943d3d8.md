---
title: Sigma Lithium Corporation common shares
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-06"
provenance: "source_sgml_aug_2026_q2_schedule; source_sgml_q1_2026_mda; source_sgml_july_2026_update; deterministic market cache"
security_id: security_4627aea1bf7d8943d3d8
issuer_id: issuer_e012f2de036ed7a1d738
confidence: low
next_review: "2026-08-15"
---

# Sigma Lithium Corporation common shares

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
  "security_id": "security_4627aea1bf7d8943d3d8",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_4627aea1bf7d8943d3d8.csv",
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

- Immutable security: `security_4627aea1bf7d8943d3d8`
- Issuer: `issuer_e012f2de036ed7a1d738`
- Instrument: Canadian common shares, Nasdaq (`XNAS`), USD
- Provider identity: `SGML` / `XNAS` / `USD` / equity

The issuer filing confirms the Nasdaq common shares. This review links them to
[[ideas/idea_critical_minerals_lithium]] through the accepted
[[relationships/relationship_670ed88c8e4616316a19|critical-minerals relationship]].

## Changes since prior review

- **Primary evidence:** An SEC-filed 5 August release reiterates Q2 production of 35,000 tonnes,
  6% above guidance, and first-half production of 58,000 tonnes above target. It schedules full Q2
  financial and operating results for **14 August 2026** but supplies no new balance sheet, cash
  flow, receivable, debt, control-remediation, financing, or environmental-settlement evidence.
- **Thesis and catalysts:** Mine execution remains the one improved assumption. The decisive
  liquidity, going-concern, control, cash-conversion, Phase 2 funding and valuation blockers are
  unchanged. Q2 accounts remain the bounded next catalyst already covered by the 15 August review.
- **Market state:** The 30 July bullish MACD crossover followed a 19.58% decline from 1 July. The
  4 August 50-day average crossing below the 200-day average followed a 5.93% decline from 7 July.
  The fresher 5 August close was USD 10.55, down 4.95% in one session; RSI was neutral at 45.05,
  MACD remained above its signal, and the 50-day average remained below the 200-day average.
- **Valuation and decision:** The USD 10.55 mark does not make valuation supportable while the
  named solvency and accounting inputs remain unresolved. The mixed alerts are rebound volatility
  inside a weak long-term trend, not an entry condition or invalidation. No full review is enqueued
  before the scheduled Q2 accounts because no decision-support gate changed.

## Economics and thesis

Sigma owns the producing Grota do Cirilo hard-rock operation in Brazil. Q1 2026 production and
sales were 23.6 kt concentrate equivalent during a mine restructuring, far below the roughly 68 kt
produced a year earlier. Revenue was USD 42.3 million, net income USD 11.1 million, and adjusted
EBITDA USD 16.7 million, but operating cash flow was negative USD 2.7 million.

The July production update was directionally better: Sigma reported 35 kt of second-quarter
concentrate, 6% above its 33 kt guidance, with 70% recovery and an approximately 20% yield. The
5 August filing confirms that milestone and 58 kt of first-half production but does not demonstrate
cash conversion. The July filing also disclosed negotiations with Minas Gerais after approximately
USD 540,000 of environmental fines, adding a live regulatory issue while the company disputes the
allegations.

Liquidity remains decisive: March cash was USD 3.9 million, total loans and export prepayment USD
133.9 million, and negative working capital USD 144.5 million, which the filing says may cast
substantial doubt on going concern. Customer cash receipts were only USD 16.3 million while trade
receivables rose USD 20.4 million. Phase 2's USD 107 million budget therefore depends on stabilized
operations and external funding despite reported accounting profit.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q1 output was 23.6 kt versus 68.3 kt a year earlier. | Ramp and mine-plan execution were not established in the financial baseline. |
| Q2 output was 35 kt, 6% above guidance; first-half output was 58 kt above target. | Mine execution improved, but production alone does not resolve cash and funding risk. |
| Adjusted EBITDA margin was 39.5% but Q1 operating cash flow was negative. | Accounting margin did not convert into cash. |
| March cash was USD 3.9 million versus USD 133.9 million loans/prepayment. | Financing and counterparty dependence are acute. |
| Negative working capital was USD 144.5 million. | Going-concern disclosure overrides headline earnings. |
| Internal control was ineffective with multiple material weaknesses. | Reporting and governance risk require remediation. |
| Full Q2 results are scheduled for 14 August. | A near-dated filing should provide the missing financial update; no premature broad review is warranted. |

Primary evidence: [Sigma Q1 2026 MD&A](https://www.sec.gov/Archives/edgar/data/1848309/000129281426003065/ex99-1.htm),
the [July production and environmental update](https://www.sec.gov/Archives/edgar/data/1848309/000129281426003854/ex99-1.htm),
and the [5 August Q2-results schedule](https://www.sec.gov/Archives/edgar/data/1848309/000129281426004055/ex99-1.htm).

## Valuation, catalysts, and risks

No supportable downside or base-case valuation exists while liquidity, working capital, receivable
collection, controls, and Phase 2 funding are unresolved. The USD 10.55 close on 2026-08-05 and
1,688,000-share volume provide a fresh, liquid paper mark, but price availability does not make the
fundamental inputs supportable. A later model must use verified cash collections, net debt,
prepayment terms, normalized output and costs, expansion funding, diluted shares, and lithium price
scenarios.

Catalysts are Q2 accounts, sustained production, receivable collection, positive operating cash,
refinancing, and control remediation. Invalidate if output remains unstable, receivables or supplier
disputes grow, financing tightens, controls remain ineffective, or Phase 2 spending begins without
funded liquidity.

## Market indicator context

The deterministic 24 July packet recorded an entered RSI-oversold transition after a 20.74% decline
from 25 June. The [[inbox/market-security_4627aea1bf7d8943d3d8-macd_cross_above_signal-714b4dd20b98|30
July MACD crossover]] then followed a 19.58% decline from 1 July, while the
[[inbox/market-security_4627aea1bf7d8943d3d8-sma_50_cross_below_200-fe17d3d3655f|4 August bearish
moving-average crossover]] followed a 5.93% decline from 7 July. At the current 5 August state, RSI
was 45.05 and MACD remained above its signal, while the 50-day average of USD 10.52 was below the
USD 12.53 200-day average. This is mixed rebound volatility inside a weak long-term trend, not a
valuation input, catalyst, invalidation, or trade signal.

## Disposition

Status: **watching**, confidence **low**, research status **unsupported**, allocation assessment
**ineligible**, and conviction tier **watch**. Canonical conclusion: **Unrated / Avoid**. Review by
**2026-08-15** after the scheduled 14 August Q2 accounts or a financing update.
`accounting_uncertain`, `solvency_risk`, and `valuation_unsupported` remain hard blockers. The fresh
mark, improved production, and mixed rebound signals do not justify a strategy because liquidity,
control, funding, and valuation risks can overwhelm lithium upside. This quick check found no
material gate change and therefore did not enqueue a premature full review.

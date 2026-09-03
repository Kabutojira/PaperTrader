---
title: Palantir Technologies Inc. Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-11"
provenance: "source_pltr_q1_2026_earnings; source_pltr_q2_2026_10q; Warp Speed material; U.S. Army procurement notice"
security_id: security_bdc2f87dadf134760c3a
issuer_id: issuer_7273af0280c612edebab
confidence: medium
next_review: "2026-08-25"
---

# Palantir Technologies Inc. Class A common stock

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
  "security_id": "security_bdc2f87dadf134760c3a",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_bdc2f87dadf134760c3a.csv",
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

- Immutable security: `security_bdc2f87dadf134760c3a`
- Issuer: `issuer_7273af0280c612edebab`
- Instrument: Class A common stock, Nasdaq (`XNAS`), USD
- Provider identity: `PLTR` / `XNAS` / `USD` / equity

This review tests Palantir as an indirect public exposure to
[[ideas/idea_anduril_product_company_disruption]]. It is not ownership in Anduril.

## Economics and thesis

The SEC-filed Q2 2026 Form 10-Q supersedes the Q1 operating baseline. Q2 revenue grew 93% to USD
1.935 billion. U.S. commercial revenue grew 149% to USD 764 million and U.S. government revenue
grew 90% to USD 809 million. GAAP operating income was USD 912 million, a 47% margin, and cash from
operations was USD 1.216 billion. Management raised full-year revenue guidance to USD 8.150-8.158
billion and adjusted free-cash-flow guidance to USD 4.5-4.7 billion. Growth, profitability and cash
conversion therefore strengthened rather than invalidated the broad operating thesis.

The balance sheet remains a strength. At 30 June 2026, cash and equivalents plus marketable
securities were USD 9.409 billion against USD 1.794 billion of total liabilities. Six-month stock
compensation was USD 467 million and 2.403 billion common shares were outstanding at quarter end,
so dilution and per-share economics remain material despite strong GAAP profitability and liquidity.

The Anduril link is operational but economically unquantified. Anduril uses Palantir Warp Speed in
production, and the companies participate together in the Army TITAN ecosystem. Palantir does not
disclose Anduril-derived revenue, margin, contract duration, or concentration. The Army's separate
Anduril enterprise contract has a maximum potential value up to USD 20 billion, but the Army says
that amount is not obligated; it is not Palantir revenue.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q2 revenue rose 93%; U.S. commercial revenue rose 149%. | Palantir has powerful organic growth independent of the proxy thesis. |
| GAAP operating margin was 47%; operating cash flow was USD 1.216 billion. | Scale is converting into accounting profit and cash. |
| Six-month stock compensation was USD 467 million. | Per-share dilution remains a material valuation input. |
| Cash and marketable securities were USD 9.409 billion. | Solvency and near-term liquidity are not blockers. |
| Anduril uses Warp Speed and partners on TITAN. | The operating relationship is real. |
| No Anduril-linked revenue is disclosed. | Proxy materiality cannot be measured. |
| Anduril's USD 20 billion Army ceiling is not obligated. | Procurement ceiling cannot be treated as backlog or pull-through. |

Primary evidence: [Palantir Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm),
[Q2 earnings release](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000039/a2026q2ex991pressrelease.htm),
[Warp Speed](https://www.palantir.com/warpspeed/), [TITAN](https://www.palantir.com/titan/), and
[U.S. Army Anduril contract notice](https://www.army.mil/article/291074/u_s_army_awards_enterprise_contract_for_it_commercial_solutions).

## Changes since prior review

- **Evidence:** Fresh retrievals confirm that the Q2 Form 10-Q and SEC-filed earnings release are
  unchanged since the quick check. Q2 remains the current operating baseline, and no new evidence
  quantifies Anduril-derived revenue, margin, contract duration or cash flow.
- **Assumptions and scenarios:** The unsupported legacy two-case revenue sensitivity is replaced by
  a scenario-complete `mature_compounder` free-cash-flow-yield valuation. It starts from the USD
  8.154 billion midpoint of 2026 revenue guidance, explicitly normalizes the unusually high 2026
  adjusted free-cash-flow margin, includes USD 7.615 billion of net liquid assets, and models
  dilution above the 2.570 billion Q2 diluted weighted-average share count. Bear/base/bull fair
  values are now USD 52.29/USD 99.24/USD 162.50 with 25%/50%/25% probabilities; the prior review had
  no accepted scenarios or buy-below value.
- **Thesis and evidence quality:** The broad growth, profitability, cash-conversion and balance-sheet
  thesis remains strong rather than receiving another upgrade. The proxy thesis remains unproven
  because Anduril economics are still undisclosed. Confidence remains medium.
- **Catalysts, risks and invalidation:** Sustained organic growth, durable GAAP profitability and
  disclosed Warp Speed economics remain catalysts. Multiple compression, growth and margin
  normalization, stock compensation, dilution and government concentration remain risks. The
  invalidation tests are unchanged.
- **Blockers and gaps:** `valuation_unsupported` is resolved by the ordered scenarios. The remaining
  valuation and timing gaps become measured rather than unbounded: even the bull value is below the
  USD 175.23 mark. The rejected, low-confidence
  [[relationships/relationship_250194f6a9e3a1817632|Anduril relationship]] remains unchanged and
  independently prevents the proxy idea from supporting allocation.
- **Rating and action:** The conclusion changes from **Unrated / Watch** to **Strong Sell / Avoid**.
  Allocation remains ineligible, now because scenario returns and margin of safety fail rather than
  because valuation is unsupported. No strategy, signal or paper order is justified.
- **Unchanged conclusion:** The 7 July–4 August cluster remains earnings-backed momentum and adverse
  entry timing, not a buy signal. By 10 August the close was USD 175.23, RSI remained overbought and
  price remained above the upper Bollinger band, while the one-session MACD-cross and volume anomaly
  were no longer active.

## Valuation, catalysts, and risks

The selected repository template is `mature_compounder` and the permitted method is
`free_cash_flow_yield`. The 12-month model starts with the issuer's USD 8.150-8.158 billion 2026
revenue guidance and USD 4.5-4.7 billion adjusted free-cash-flow guidance. It deliberately uses
2027 free-cash-flow margins below the 56.4% 2026 guidance midpoint, includes USD 7.615 billion of
net liquid assets from the Q2 balance sheet, and raises scenario share counts above the Q2 diluted
weighted average to treat stock compensation and dilution explicitly.

| Scenario | Probability | Explicit assumptions | Value per share | Return from USD 175.23 |
| --- | ---: | --- | ---: | ---: |
| Bear | 25% | 30% 2027 revenue growth, 42% FCF margin, 30x FCF, USD 7.615 billion net liquid assets, 2.70 billion diluted shares | USD 52.29 | -70.2% |
| Base | 50% | 45% 2027 revenue growth, 48% FCF margin, 45x FCF, USD 7.615 billion net liquid assets, 2.65 billion diluted shares | USD 99.24 | -43.4% |
| Bull | 25% | 60% 2027 revenue growth, 53% FCF margin, 60x FCF, USD 7.615 billion net liquid assets, 2.60 billion diluted shares | USD 162.50 | -7.3% |

The probability-weighted fair value is USD 103.32, a -41.0% expected return before the deterministic
medium-confidence adjustment. The 20% research margin-of-safety policy implies a USD 82.65
buy-below price; the current price is about 69.6% above weighted fair value. These outcomes are
severe overvaluation even though the scenarios grant exceptional growth, free-cash-flow conversion
and valuation multiples. The model assigns no value to the Anduril Army ceiling because neither
revenue attribution nor obligation is disclosed.

Catalysts are sustained organic growth, disclosed Warp Speed customer expansion, durable GAAP cash
conversion, and measurable defence-manufacturing revenue. Invalidate the proxy if Anduril-linked
economics remain immaterial; invalidate the broader thesis if growth decelerates sharply, government
concentration or termination rights hurt visibility, dilution offsets earnings, or valuation leaves
no downside margin.

## Disposition

Status: **watching**, confidence **medium**, rating **Strong Sell**, portfolio action **Avoid**, and
allocation eligibility **ineligible**. Q2 materially strengthened the operating checklist, but the
USD 175.23 mark exceeds even the bull fair value and fails expected-return, base-return, payoff and
margin-of-safety gates. Revisit after material operating evidence or near the USD 82.65 buy-below
frontier; no strategy or signal is created. See [[research-catalog]] for the maintained research
graph.

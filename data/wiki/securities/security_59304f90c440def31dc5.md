---
title: RTX Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-21"
provenance: "source_rtx_q2_2026_10q_sec; source_rtx_q2_2026_results; source_rtx_q2_2026_results_sec_ex99; source_rtx_sec_submissions_20260821; source_5392f8ab153edf73d1e7; source_e4822bd4b442ff51063d; source_d73911b42ea0e59df247; source_e5d2d85e77932d3bf56d; source_8b43e53b8703087510ef; source_ad511f12b8de63d3a443; source_b2d45bca8d0a249be557; deterministic market cache"
security_id: security_59304f90c440def31dc5
issuer_id: issuer_7e0bd218f603cf838669
confidence: medium
next_review: "2026-09-04"
---

# RTX Corporation common stock

## Identity

- Immutable security: `security_59304f90c440def31dc5`
- Issuer: `issuer_7e0bd218f603cf838669`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `RTX` / `XNYS` / `USD` / equity

RTX's release confirms the listed instrument and three operating segments. This page evaluates it
through [[ideas/idea_defense_aerospace]], never ticker text alone, and separately records the
[[inbox/market-security_59304f90c440def31dc5-rsi_overbought-22069206cbf5|24 July RSI-overbought
entry]], [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-fac3019c4101|same-session
strengthening]], [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-c4c8f0b60fc6|27 July
RSI strengthening]], [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-a6de68653afb|scheduled-run
RSI reconciliation]], [[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-7a832eb2d5ae|upper-Bollinger entry]],
and [[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-c288bb87ff70|27 July
upper-Bollinger strengthening]], plus its
[[inbox/market-security_59304f90c440def31dc5-bollinger_above_upper-b275f066a05b|scheduled-run
reconciliation]].

The repeat check also covers the [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-1d1f51178b2e|31 July
RSI re-entry]], [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-2a2e6bf5ce40|4 August
strengthening]], and [[inbox/market-security_59304f90c440def31dc5-rsi_overbought-8910e4772383|5 August
strengthening]], followed by the [[inbox/market-security_59304f90c440def31dc5-bollinger_below_lower-19de952490e0|21 August
lower-Bollinger entry]].

## Business economics

Collins Aerospace supplies commercial and defence systems; Pratt & Whitney supplies engines and
aftermarket service; Raytheon supplies missiles, air defence, sensors, and naval systems. The mix
diversifies demand but makes the equity more than a pure rearmament exposure.

Q2 2026 sales were USD 24.7 billion, GAAP EPS USD 1.57, operating cash flow USD 3.5 billion, and
company-defined free cash flow USD 2.9 billion. Backlog was USD 289 billion: USD 170 billion
commercial and USD 119 billion defence. All three segments expanded adjusted margin, while Raytheon
sales grew 18% on Patriot, Standard Missile, AMRAAM, naval, and air-defence volume. The filed
quarterly report also shows first-half operating cash flow of USD 5.402 billion, up from USD 1.763
billion, although working-capital timing contributed to the improvement.

## Thesis and contrary evidence

Funded allied replenishment supports Raytheon volume, while commercial aftermarket growth supports
Collins and Pratt. The Q2 record confirms demand and margin conversion rather than backlog alone.
Counterweights are Pratt's powder-metal inspection program, fixed-price and program-accounting risk,
supply constraints, defence budget timing, commercial aviation cyclicality, and acquisition
accounting adjustments. At 30 June 2026, RTX had USD 8.305 billion of cash against USD 37.383
billion of total debt. Current assets of USD 63.912 billion only narrowly exceeded current
liabilities of USD 63.245 billion, including USD 5.296 billion of debt due currently; operating cash
generation and market access therefore matter to balance-sheet resilience.

| Evidence | Interpretation |
| --- | --- |
| Defence backlog reached USD 119 billion and Raytheon sales rose 18%. | Replenishment is translating into funded demand. |
| Raytheon adjusted operating margin rose to 12.6% from 11.6%. | Volume and mix improved economics, but contract execution remains critical. |
| Pratt sales rose 16% and adjusted margin was 8.3%. | Aftermarket and military demand help, while GTF liabilities and OE mix remain constraints. |
| Collins adjusted margin was 16.7% on 8% reported sales growth. | Commercial aerospace provides a profitable second engine but adds cycle sensitivity. |
| Full-year free-cash-flow guidance rose to USD 8.50-8.75 billion. | Cash normalization is progressing, subject to engine remediation, working capital, and capital returns. |

Primary evidence: [RTX Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/101829/000010182926000027/rtx-20260630.htm)
(`source_rtx_q2_2026_10q_sec`) and [RTX Q2 2026 results](https://www.rtx.com/news/news-center/2026/07/23/rtx-reports-q2-2026-results)
(`source_rtx_q2_2026_results`). The broader demand mechanism remains documented in
[[ideas/idea_defense_aerospace]].

## Valuation and market context

The current deterministic close is USD 209.91000366210938 for 21 August 2026, retrieved at
22:17:01Z, with identity-matched USD/EUR FX of 0.8562999963760376 at the same timestamp. RTX's SEC-filed Q2 results
exhibit raises 2026 adjusted EPS guidance to USD 7.10-7.25 and free-cash-flow guidance to USD
8.50-8.75 billion. The 10-Q reports USD 8.305 billion of cash, USD 37.383 billion of total debt,
and 1,365.0 million diluted weighted-average shares for the quarter. The market price is therefore
about 30.7-31.3 times guided adjusted EPS before separately normalizing acquisition-accounting and
other excluded items.

The repository's `mature_compounder` template and `earnings_multiple` method provide a bounded
12-month comparison. The cases deliberately vary both earnings delivery and the multiple because
backlog growth and raised guidance coexist with net debt, Pratt remediation, fixed-price execution,
supply constraints, and commercial-cycle risk. They are scenario values, not price targets.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 142.00 | Low-end USD 7.10 adjusted EPS at 20x; remediation, contract, supply, or cycle pressure prevents further normalization and compresses the premium multiple. |
| Base | 50% | USD 179.375 | USD 7.175 guidance midpoint at 25x; backlog converts and raised cash guidance is delivered, but leverage, remediation, and cycle risk retain a discount to the current multiple. |
| Bull | 25% | USD 246.50 | High-end USD 7.25 adjusted EPS at 34x; defense and commercial demand convert cleanly, margins and cash strengthen, and remediation and execution risks recede enough to sustain a premium multiple. |

At the current mark, deterministic scenario returns are approximately **-32.35% / -14.55% /
+17.43%** for bear/base/bull. Probability-weighted fair value is USD 186.8125, an expected return
of about **-11.00%** before the medium-confidence adjustment. The configured 20% margin-of-safety
buy-below price is USD 143.50. A complete valuation is now supportable, but it is decisively
unattractive relative to cash at the current mark.

The deterministic monitor first recorded entry into the RSI-overbought condition on **2026-07-24**
after a **13.35%** adjusted-close gain from 25 June to 24 July, at a USD 211.50 close and trigger
strength of 0.1071. This indicator transition corroborates strong momentum and near-term entry risk;
it does not explain the move, establish intrinsic value, or independently support a short or other
paper trade. The current valuation and fundamental gates remain controlling.

A later deterministic packet for the same 24 July endpoint recorded a strengthened trigger after
the adjusted close refreshed to USD 212.79: the period gain was **14.04%** and trigger strength rose
to 0.1347 from 0.1071. This refines the measured intensity of the same overbought condition rather
than establishing a separate catalyst or trade thesis; the fresher 27 July mark and valuation above
remain controlling for the current assessment.

The 27 July RSI packet records a further strengthening at the USD 218.42 close: the adjusted-close
gain from 26 June through 27 July was **16.19%**, and trigger strength rose to 0.2458 from 0.1347.
The shifted measurement window and refreshed bars make this a later observation rather than a
replacement for either 24 July packet. It reinforces strong momentum and near-term entry risk but
does not explain the price move, establish a catalyst or intrinsic value, or independently support
a short or other paper trade; the fundamental and valuation gates remain controlling.

A scheduled-run packet reconciled the same 26 June–27 July window and USD 218.42 close with the
same **16.19%** return. Its trigger strength was 0.2443 from 0.1347, slightly below the earlier
0.2458 observation because its deterministic source-price snapshot had a different hash. This is
corroborating measurement variation, not a new catalyst or contradictory market conclusion, and it
does not change the valuation, timing, or paper-trade disposition.

A parallel deterministic packet for the initial USD 211.50 close recorded entry above the upper
Bollinger band on **2026-07-24**, after the same **13.35%** adjusted-close gain from 25 June to 24
July, with trigger strength 0.0173 from zero previously. This corroborates the breakout-like
momentum already captured by the RSI observations but does not explain the move, establish a
separate catalyst or intrinsic value, or independently support a short or other paper trade.

The 27 July deterministic packet then recorded the upper-Bollinger condition strengthening at the
USD 218.42 close: the adjusted-close gain from 26 June through 27 July was **16.19%**, and trigger
strength rose to 0.0286 from 0.0153 in the monitor's immediately preceding observation. The changed
measurement window and refreshed bars make those strength values distinct from the initial 24 July
packet rather than replacements for it. The observation corroborates stronger near-term momentum
and entry risk, but still supplies no price explanation, separate catalyst, intrinsic-value evidence,
short thesis, or paper-trade support; the fundamental and valuation gates remain controlling.

The scheduled-run upper-Bollinger packet reconciled that same 26 June–27 July window and USD 218.42
close with the same **16.19%** return. It measured trigger strength at 0.0271 from 0.0215, modestly
below the earlier 0.0286 observation because the deterministic source-price snapshot had a different
hash. As with the parallel RSI reconciliation, this is corroborating measurement variation rather
than a new catalyst or contradictory market conclusion. It does not alter the valuation, timing, or
paper-trade disposition.

## Quick check — 2026-08-05

The deterministic close rose from USD 215.22 on 31 July to USD 217.93 on 4 August and USD 222.31 on
5 August. Over the payload's merged alert sequence, RSI-overbought first re-entered with an 8.02%
period return, then strengthened, reaching RSI 75.81 and a 14.06% 20-session return on 5 August.
The latest source-price hash is
`145058c76665a7cd75a02203139ad13ba3eadef94c856ba566cdea4d52263ef5`. Price remains below the
USD 227.31 upper Bollinger band, so the controlling observation is persistent overbought momentum,
not a fresh upper-band breakout.

The SEC-hosted Q2 filing was retrieved again on 5 August with HTTP 200 and the unchanged registered
SHA-256 `9f013f79edcb3e5eba91055c1da62413a58f51ba47e7380d33744949362f3ec2`.
The SEC submissions record showed no later RTX company financial filing through the check; later
entries were insider Forms 4 and selling-holder Forms 144. The issuer release URL returned HTTP 403
to the bounded unauthenticated check, so it was not treated as newly verified evidence. The
unchanged SEC filing continues to support the backlog, segment, cash-flow, debt, contract-risk, and
Pratt-remediation checklist, but no new primary evidence changes those assumptions.

At USD 222.31, the old bounded downside and base reference values of USD 142.00 and USD 179.38 were
about 36.1% and 19.3% below the mark, respectively. The quick check correctly treated that legacy
two-case work as incomplete. This full review resolves the schema gap with the explicit three-case
valuation above; it confirms rather than reverses the adverse entry conclusion.

## Alert review — 2026-08-21

The exact 24 July–21 August packet records a USD 209.91000366210938 adjusted close, a **-1.35%**
period return, and entry **0.56% below** the lower Bollinger band. Canonical indicators show RSI
45.04, a negative MACD histogram, and a five-session return of **-5.86%**. This reverses the prior
overbought timing condition, but the shallow band breach is a technical **opportunity to recheck**,
not primary evidence of improved earnings power or a fundamental catalyst. The price remains above
the USD 186.8125 weighted value and USD 179.375 base value, so no paper action is justified.

The Q2 Form 10-Q and SEC-filed results exhibit were retrieved with HTTP 200 and unchanged hashes on
21 August. The dated SEC submissions index lists the 23 July Form 10-Q and results Form 8-K as the
latest operating filings through 21 August; later entries are Forms 4 and 144. No current primary
filing explains the pullback or changes guidance, backlog, cash, leverage, remediation, or contract
assumptions.

## Changes since prior review

- **Evidence:** the Q2 Form 10-Q and SEC-filed results exhibit are unchanged, and the newly retained
  dated SEC submissions index confirms no later operating filing through 21 August. The exact new
  deterministic evidence is the lower-Bollinger transition at USD 209.91.
- **Assumptions and scenarios:** unchanged. The `mature_compounder` earnings-multiple cases remain
  USD 142.00/USD 179.375/USD 246.50 with 25%/50%/25% probabilities because no new fundamental
  evidence changes guided earnings or the scenario drivers. Weighted value remains USD 186.8125;
  the lower mark improves expected return from about -15.97% to -11.00% but does not clear a gate.
- **Thesis:** unchanged. Funded backlog, segment growth, margin improvement, and cash generation
  support the causal thesis, while RTX remains a diversified commercial-and-defense instrument.
- **Catalysts, risks, and invalidation:** unchanged. Awards, backlog conversion, cash delivery, and
  remediation progress remain catalysts; Pratt liabilities, leverage, fixed-price execution,
  suppliers, budget timing, and commercial cyclicality remain controlling risks.
- **Idea exposure map:** the accepted, positive, medium-sensitivity
  [[relationships/relationship_1655ac715c33506ec7da|defense-and-aerospace relationship]] remains
  current on evidence but is due for its already-queued separate review. The complete maintained
  idea catalog produced no additional pairing with a specific, material RTX transmission mechanism;
  drone, space, AI-power, and broad manufacturing themes were rejected as superficial overlaps.
- **Blockers and gaps:** expected return, base return, payoff asymmetry, and margin of safety still
  fail. Medium confidence and cyclical normalization remain soft gaps; timing improves from adverse
  to weak because the overbought condition reversed, but the lower-band breach lacks a catalyst.
- **Rating and action:** **Sell / Avoid** remains unchanged. The security is unowned, the technical
  pullback is not a short signal, and no strategy, signal, order, allocation, or accounting change
  is warranted.

## Catalysts and invalidation

Catalysts are funded missile awards, capacity expansion, backlog conversion, GTF remediation
progress, aftermarket growth, and delivery of raised cash-flow guidance. Invalidate the positive
case if fixed-price losses or engine liabilities rise, cash flow misses guidance, defence awards are
delayed or cancelled, supply constraints cap delivery, or commercial aerospace demand turns down.

## Disposition

Status: **watching** with **medium** confidence and a scenario-complete but **allocation-ineligible**
assessment. Business quality, funded demand, cash generation, the accepted relationship, and deep
trading liquidity support continued research coverage. The USD 186.8125 weighted value, USD 179.375
base value, and USD 143.50 buy-below level do not support ownership at the USD 209.91 mark despite
the lower-Bollinger transition. The canonical conclusion is **Sell / Avoid**, not a short signal. Review by
**2026-09-04**, or sooner after a major award, program charge, engine-liability, guidance, or
valuation change. No conviction strategy or paper signal is justified. See the complete
[[research-catalog]] and append-only [[log]] for context.

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
  "security_id": "security_59304f90c440def31dc5",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_59304f90c440def31dc5.csv",
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

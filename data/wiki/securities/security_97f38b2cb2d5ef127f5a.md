---
title: Planet Labs PBC Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-29"
updated: "2026-09-11"
provenance: "source_pl_q1_fy2027_10q; source_pl_q1_fy2027_results_sec; source_pl_q2_fy2027_10q; source_pl_q2_fy2027_results_sec; source_pl_sec_submissions_20260910"
security_id: security_97f38b2cb2d5ef127f5a
issuer_id: issuer_f0de6eb64ff0330bf082
confidence: medium
next_review: "2026-09-25"
---

# Planet Labs PBC Class A common stock

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
  "security_id": "security_97f38b2cb2d5ef127f5a",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_97f38b2cb2d5ef127f5a.csv",
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

The full Q2 review now incorporates reported growth, liquidity, capex and dilution into a refreshed
scenario range. Stronger operations do not offset the valuation and downside asymmetry at the
current mark.

```echart
{
  "schema_version": 1,
  "chart_id": "q2-fy2027-scenario-values",
  "kind": "series",
  "title": "Q2 FY2027 scenario values versus the reference price",
  "description": "The refreshed bear and base fair values remain below the 10 September reference price; only the low-probability bull case offers upside.",
  "as_of": "2026-09-10",
  "sources": [
    {
      "label": "Planet Labs Q2 fiscal 2027 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/1836833/000119312526382016/pl-20260731.htm",
      "observed_at": "2026-09-10T20:04:05Z"
    },
    {
      "label": "PaperTrader deterministic adjusted-close cache",
      "observed_at": "2026-09-10T20:48:19Z"
    }
  ],
  "x_axis": {
    "type": "category",
    "label": "Scenario",
    "values": ["Bear", "Base", "Bull"]
  },
  "y_axes": [
    {
      "label": "USD per share",
      "unit": "USD/share",
      "format": "currency",
      "currency": "USD"
    }
  ],
  "series": [
    {
      "name": "Refreshed fair value",
      "render": "bar",
      "y_axis": 0,
      "values": ["6.30", "12.71", "24.00"]
    },
    {
      "name": "Reference price",
      "render": "line",
      "y_axis": 0,
      "values": ["16.690000534057617", "16.690000534057617", "16.690000534057617"]
    }
  ],
  "notes": [
    "Scenario values use Q2 filing inputs, scenario-specific FY2028 revenue, enterprise-value-to-revenue multiples, post-investment net cash and diluted shares.",
    "The chart is research presentation only and is not an allocation, signal, or order input."
  ]
}
```

Q2 growth came with gross-profit expansion, but GAAP operating losses persisted. This separates
improving service economics from the still-unproven conversion to durable free cash flow.

```echart
{
  "schema_version": 1,
  "chart_id": "q2-revenue-gross-profit-operating-loss",
  "kind": "series",
  "title": "Q2 revenue, gross profit, and GAAP operating loss",
  "description": "Comparable fiscal-second-quarter results show revenue and gross-profit growth alongside a smaller but continuing GAAP operating loss.",
  "as_of": "2026-07-31",
  "sources": [
    {
      "label": "Planet Labs Q2 fiscal 2027 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/1836833/000119312526382016/pl-20260731.htm",
      "observed_at": "2026-09-11T05:51:50Z"
    }
  ],
  "x_axis": {
    "type": "category",
    "label": "Fiscal second quarter",
    "values": ["FY2026", "FY2027"]
  },
  "y_axes": [
    {
      "label": "USD millions",
      "unit": "USD millions",
      "format": "currency",
      "currency": "USD"
    }
  ],
  "series": [
    {
      "name": "Revenue",
      "render": "bar",
      "y_axis": 0,
      "values": ["73.386", "116.052"]
    },
    {
      "name": "Gross profit",
      "render": "bar",
      "y_axis": 0,
      "values": ["42.268", "65.632"]
    },
    {
      "name": "GAAP operating loss",
      "render": "line",
      "y_axis": 0,
      "values": ["-17.960", "-13.509"]
    }
  ],
  "notes": [
    "Amounts are issuer-reported US dollars converted from thousands to millions; periods and definitions are directly comparable.",
    "Adjusted EBITDA is excluded because the chart compares GAAP statement-of-operations measures."
  ]
}
```

## Identity

- Immutable security: `security_97f38b2cb2d5ef127f5a`
- Issuer: `issuer_f0de6eb64ff0330bf082`
- Instrument: Class A common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `PL` / `XNYS` / `USD` / equity

The SEC filing confirms Planet Labs PBC and its NYSE-listed Class A share identity. Planet is
thematically relevant to commercial-space infrastructure research, but no accepted canonical
idea-security relationship currently exists; this review does not create one from thematic fit
alone.

## Business economics

Planet operates Earth-observation satellite constellations and sells imagery, data subscriptions,
analytics, dedicated tasking capacity, and satellite services. The model combines high recurring
contract value with continuing satellite, software, launch, hosting, and research investment.
Government demand improves contract visibility but introduces appropriation and termination-for-
convenience exposure.

For the quarter ended 31 July 2026, revenue was USD 116.1 million, up 58% year over year; 98% of
annual contract value was recurring, six-month net dollar retention was 109%, and remaining
performance obligations were USD 753.1 million. Reported backlog was USD 814.9 million. Gross
margin was 57%, adjusted EBITDA was positive USD 13.9 million, and year-to-date operating and free
cash flow were positive USD 68.4 million and USD 21.3 million. Cash and short-term investments
totaled USD 865.4 million, including approximately USD 120 million raised through ATM share sales.

## Thesis and contrary evidence

Daily global imagery, a deep archive, improving high-resolution capacity, and analytics can create
valuable recurring data economics. Q2 growth, retention, RPO, backlog, and cash generation show
real demand and better operating leverage. The contrary case is that satellite replacement, capex, hosting,
research, and stock compensation consume part of the apparent software-like economics, while
large government and satellite-services awards can make growth lumpy and cancellable.

| Evidence | Interpretation |
| --- | --- |
| Revenue grew 58% to USD 116.1 million and recurring ACV was 98%. | Demand and recurrence remain strong, although satellite-hardware delivery contributed to growth and one quarter does not prove durable GAAP profitability. |
| RPO was USD 753.1 million and backlog USD 814.9 million. | Visibility remains substantial but both measures declined sequentially and retain cancellation and appropriation limitations. |
| Cash and short-term investments totaled USD 865.4 million. | Liquidity strengthened, but approximately USD 120 million came from ATM issuance rather than operations. |
| Adjusted EBITDA was USD 13.9 million and year-to-date free cash flow was positive. | Operating leverage improved, while adjusted metrics still exclude stock compensation and satellite depreciation and capex is rising. |
| Common shares reached 363.7 million at quarter-end after 3.8 million ATM shares. | Capital access lowers liquidity risk but confirms material per-share dilution. |

Primary evidence: [Planet Q2 FY2027 results filed with the SEC](https://www.sec.gov/Archives/edgar/data/1836833/000119312526381874/pl-ex99_1.htm)
and [Planet Q2 FY2027 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1836833/000119312526382016/pl-20260731.htm).

## 2026-09-10 Q2 and oversold-alert quick check

From 12 August through 10 September, the adjusted close declined 31.88% from USD 24.50 to USD
16.69. RSI fell to 24.16, the close remained below the USD 20.85 20-day and USD 22.77 50-day
averages, and MACD stayed below its signal. The 3 September results session fell 8.20% on 31.95
million shares, followed by continued weakness including a further 3.08% decline on 10 September.
The repeated and strengthening alerts are a materially oversold condition and adverse timing
signal, not by themselves a valuation catalyst.

The new Q2 filing changes the evidence set rather than invalidating the operating thesis. Revenue
growth, adjusted EBITDA, cash flow, and liquidity improved; fiscal 2027 revenue guidance is USD
430-441 million. Against that, RPO and backlog declined sequentially, Q2 growth included
satellite-hardware delivery, fiscal-year capex guidance rose to USD 100-115 million, and the ATM
issued approximately USD 120 million of equity. These changes affect growth quality, cash,
capital-intensity, and diluted-share assumptions and therefore require a bounded full valuation
review.

The August bear/base/bull fair values of USD 6.42/USD 14.36/USD 27.73 are retained only as a
provisional comparison. At USD 16.69, the weighted USD 14.65 value remains 12.21% below market,
the base case remains 13.96% below market, and the USD 11.49 buy zone remains 31.16% below market.
The lower price improves prospective returns but does not clear the expected-return, base-return,
bear-payoff, margin-of-safety, confidence, or accepted-relationship gates. The prior **Sell / Avoid**
reading remains the provisional scenario comparison, while the comparable current assessment is
**Unrated / Watch** because Q2 has made those valuation inputs incomplete. No paper trade is
justified pending full review.

## 2026-07-28 price-action review

The deterministic USD 20.20 close fell 35.42% from 29 June through 28 July and 3.81% in the final
session. RSI entered oversold territory at 25.77, while the close remained above the USD 17.63
lower Bollinger band and volume anomaly was only 0.63. The price was below both the USD 25.47
50-day and USD 32.44 200-day averages, and MACD remained below its signal without a new crossing.

No current filing or issuer release identified a fundamental deterioration that explains the
specific July 28 move. Planet instead reported the successful Pelican-11 launch on 7 July, after
the strong June quarter. The alert is therefore **valuation and momentum risk with an oversold
technical condition**, not verified fundamental invalidation and not a sufficient opportunity.
The absence of abnormal volume and the still-demanding valuation prevent treating RSI alone as
capitulation evidence.

## Changes since prior review

- **Changed facts and evidence:** fresh retrieval of the Q2 Form 10-Q and SEC-filed results found no
  source drift, and the SEC submissions index showed no newer operating filing. Quarterly revenue
  rose 58% year over year to USD 116.1 million, GAAP gross margin reached 57%, and six-month operating
  cash flow was USD 68.4 million. Property-and-equipment purchases of USD 44.7 million show why
  durable free cash flow remains a harder hurdle than operating cash flow.
- **Changed assumptions and valuation:** the prior USD 6.42/USD 14.36/USD 27.73 scenarios used Q1
  evidence. The full Q2 review now incorporates USD 865.4 million of cash and short-term investments,
  USD 448.3 million carrying-value convertible notes, 363.7 million common shares, 23.9 million
  unvested RSUs, 13.5 million options, fiscal 2027 revenue guidance of USD 430-441 million and capex
  guidance of USD 100-115 million. Refreshed bear/base/bull values are USD 6.30/USD 12.71/USD 24.00.
- **Thesis and evidence change:** Q2 growth, 109% net dollar retention, positive adjusted EBITDA and
  stronger liquidity support the recurring-data thesis. Lower sequential RPO and backlog, a hardware
  contribution, ATM issuance and higher capex keep business quality and confidence below the top
  anchors.
- **Catalysts, risks, blockers and gaps:** RPO conversion, Pelican monetization, recurring retention
  and post-investment cash generation remain the catalysts. Contract cancellation, launch or
  satellite failure, gross-margin reversal, capex, stock compensation and note conversion remain
  the main risks. The quick check's `valuation_unsupported` hard blocker is resolved; negative
  expected and base returns, downside asymmetry, timing, medium confidence, no margin of safety and
  no accepted relationship still prevent allocation.
- **Rating and action:** **Sell / Avoid** and `no_new_position` are unchanged. The lower reference
  price does not clear the canonical expected-return, base-return, payoff, margin-of-safety or
  relationship gates, so no strategy, signal or paper order is justified.
- **Unchanged conclusion:** watchlist monitoring remains appropriate, but an oversold reading alone
  is neither a buy zone nor fundamental invalidation.

## 2026-08-28 lower-band and volume-alert review

From 31 July through 28 August, the adjusted close declined 2.44% from USD 20.48 to USD 19.98. The
path was less benign than that endpoint comparison: the close fell 19.27% from its USD 24.75 interim
high on 13 August and 5.58% in the final session. The latest close sits just below the USD 20.11
lower Bollinger band, below the USD 22.72 50-day and USD 32.09 200-day averages, with MACD below its
signal. Volume of 8.24 million shares was about 95% above the prior session and 3.25 times its recent
baseline.

Fresh SEC retrieval found no new operating filing capable of explaining the move or changing the
Q1 fundamentals. The combination is therefore **price and timing risk with a technically stretched
condition**, not verified thesis invalidation and not a sufficient opportunity. A lower price helps
valuation mechanically, but the mark remains well above both weighted fair value and the buy zone.

## 2026-08-09 full review of the 2026-07-31 MACD alert

The payload-bound 31 July close was USD 20.48, down 34.74% from 2 July, when MACD crossed above
its signal. By 7 August, the deterministic close had recovered to USD 23.93 and MACD remained above
its signal, but no new transition was active; RSI was neutral at 48.72 and volume remained non-
anomalous. The alert is a technical recovery after an oversold decline, not independent evidence
that the operating thesis or intrinsic value improved.

The current SEC submissions index contains no later earnings release or periodic operating filing
after the retained Q1 evidence. A 29 July Schedule 13G amendment and a 7 August ownership filing do
not update revenue, RPO, backlog, cash generation, guidance, dilution, or satellite-execution
assumptions. The Q1 thesis, catalysts, invalidation conditions, and risks therefore remain intact.

## Valuation

Template: `pre_profit_growth`; method: `revenue_multiple`; horizon: 12 months. This method is used
because Planet remains GAAP loss-making and durable free cash flow is not yet demonstrated. The Q2
filing supplies the template's required current filing, cash-runway, dilution and unit-economics
evidence.

At 31 July, cash and short-term investments were USD 865.4 million and convertible notes had a USD
448.3 million carrying value. Reported common shares were 363.7 million, before 23.9 million
unvested RSUs, 13.5 million options, 1.1 million other warrants and potential note conversion.
The scenarios therefore use explicit post-investment net cash and progressively wider diluted-share
counts rather than treating current liquidity as fully distributable or current shares as fully
diluted.

Each case projects FY2028 revenue from the USD 430-441 million FY2027 guidance range, applies an
enterprise-value-to-revenue multiple, adds scenario post-investment net cash and divides by diluted
shares. The multiples compress from the current high-growth valuation as risk rises. None of the
cases capitalizes adjusted EBITDA as GAAP earnings, and each allows for the issuer's USD 100-115
million FY2027 capex guidance, stock compensation, satellite replacement and contract variability.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 30% | USD 6.30 | FY2028 revenue reaches USD 470 million, a 5x multiple reflects weak RPO conversion or margin execution, post-investment net cash falls to USD 200 million, and dilution reaches 405 million shares. |
| Base | 50% | USD 12.71 | FY2028 revenue reaches USD 560 million, a 9x multiple recognizes durable growth but continuing capital intensity, post-investment net cash is USD 300 million, and equity awards and other dilution lift shares to 420 million. |
| Bull | 20% | USD 24.00 | FY2028 revenue reaches USD 680 million, a 15x multiple rewards sustained retention, backlog conversion, margin expansion and improving free cash flow, post-investment net cash reaches USD 600 million, and option, RSU and net convertible dilution lifts shares to 450 million. |

The probability-weighted fair value is USD 13.05, about 21.8% below the USD 16.69 reference price.
The base case is about 23.8% below market, the bear case implies about 62.3% downside, and the bull
case offers about 43.8% upside. Medium confidence further shrinks usable expected return. The base
case and weighted value remain below market, bear downside exceeds bull upside, and the completed
scenarios establish neither a current buy zone nor a margin of safety.

## Idea exposure map

- **Candidate — [[ideas/idea_commercial_space_infrastructure|Commercial space infrastructure and
  geospatial data]]:** positive direction, awaiting relationship review. Planet's recurring imagery,
  analytics, dedicated tasking and satellite services provide a direct mechanism by which commercial
  and government demand can become ACV, RPO, backlog, revenue and cash flow. Materiality is supported
  by Q2 recurrence and contract visibility; reject the edge if backlog does not convert, government
  awards are cancelled or unfunded, satellite execution fails, or capital intensity and dilution
  prevent per-share cash generation. The existing relationship review remains pending; this is not
  a canonical accepted relationship.
- **Candidate — [[ideas/idea_defense_aerospace|Defense and aerospace]]:** positive direction,
  awaiting relationship review. Government imagery, monitoring and dedicated-tasking requirements
  can transmit defense and security budgets into contracted revenue and backlog. Reject the edge if
  defense exposure is immaterial, awards are unfunded or cancelled, or satellite execution prevents
  delivery. This is not a canonical accepted relationship.
- **Rejected-no-link — other maintained ideas:** the complete catalog was searched. European defense
  rearmament was rejected because the evidence does not isolate Europe as a material driver; AI
  software consolidation was rejected because Planet sells geospatial outputs rather than a general
  software stack. Power, commodity, consumer, finance and industrial themes lack both a specific
  transmission mechanism and material evidenced exposure.

## Catalysts and invalidation

Catalysts are conversion of RPO and backlog into recurring revenue, Pelican capacity monetization,
sustained net retention, margin expansion, and positive free cash flow after satellite and software
investment. Invalidate the constructive operating case if RPO fails to convert,
government awards are cancelled or unfunded, retention weakens, satellite or launch failures
interrupt service, gross margin declines persistently, or equity and note dilution overwhelms
per-share growth.

## Disposition

Status: **watching** with **medium** confidence and current rating **Sell / Avoid**. Q2 confirms
strong growth, recurrence, operating leverage and liquidity, while lower sequential RPO and backlog,
higher capex, hardware-driven revenue, ATM issuance and continuing dilution constrain per-share
value. The refreshed scenarios show negative expected and base returns, severe bear downside, weak
payoff ratios and no margin of safety. Review by **2026-09-25**, or sooner after material contract
cancellation, satellite failure, guidance change, financing, dilution or capital-allocation news.
No conviction strategy or paper signal is justified.

See the complete [[research-catalog]] and append-only [[log]].

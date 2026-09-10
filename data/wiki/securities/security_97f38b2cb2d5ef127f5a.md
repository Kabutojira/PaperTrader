---
title: Planet Labs PBC Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-29"
updated: "2026-09-10"
provenance: "source_pl_q1_fy2027_10q; source_pl_q1_fy2027_results_sec; source_pl_q2_fy2027_10q; source_pl_q2_fy2027_results_sec; source_pl_sec_submissions_20260910"
security_id: security_97f38b2cb2d5ef127f5a
issuer_id: issuer_f0de6eb64ff0330bf082
confidence: medium
next_review: "2026-09-11"
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

The August scenarios remain provisional until the queued full review incorporates the new Q2
filing, but the current mark has moved materially closer to the retained range.

```echart
{
  "schema_version": 1,
  "chart_id": "provisional-scenario-values-september-2026",
  "kind": "series",
  "title": "Provisional scenario values versus the 10 September close",
  "description": "The latest close remains above the retained bear and base fair values even after a material decline; the Q2 filing requires a full valuation refresh before these scenario values can support a new decision.",
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
      "name": "Retained fair value",
      "render": "bar",
      "y_axis": 0,
      "values": ["6.42", "14.36", "27.73"]
    },
    {
      "name": "10 September close",
      "render": "line",
      "y_axis": 0,
      "values": ["16.690000534057617", "16.690000534057617", "16.690000534057617"]
    }
  ],
  "notes": [
    "Scenario values are the 28 August baseline and are not refreshed Q2 estimates.",
    "The chart is research presentation only and is not an allocation, signal, or order input."
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

- **Evidence:** fresh retrieval on 28 August reproduced the registered Q1 Form 10-Q and SEC-filed
  results-release hashes. The current SEC submissions index lists no operating or financial filing
  after the 10 July Form 8-K; subsequent ownership filings do not change revenue, RPO, backlog,
  guidance, cash generation, dilution, or satellite-execution evidence.
- **Market state:** the 28 August close of USD 19.98 is 2.44% below the 31 July close and 19.27% below
  the 13 August interim high. It fell 5.58% in the latest session on 8.24 million shares, entered
  below the USD 20.11 lower Bollinger band, and printed volume 3.25 times its recent baseline. The
  sharp downside transition is a risk signal, not independent evidence that intrinsic value changed.
- **Assumptions and scenario outputs:** the `pre_profit_growth` revenue-multiple assumptions and
  USD 6.42/USD 14.36/USD 27.73 bear/base/bull fair values remain unchanged because there is no newer
  operating filing. The lower mark improves all scenario returns, but the USD 14.65 weighted value
  remains about 26.7% below market and the USD 11.49 buy zone remains about 42.5% below market.
- **Thesis, catalysts, risks, and invalidation:** unchanged. Growth, recurring contract value, RPO,
  backlog and liquidity support the thesis; capital intensity, cash burn, government-contract
  cancellation, satellite execution, stock compensation and convertible dilution remain material.
- **Blockers and gaps:** no hard valuation blocker returns. Negative expected and base returns,
  severe bear downside, medium confidence, adverse timing, no margin of safety, and the absence of
  an accepted relationship still prevent allocation. The pending Q2 evidence remains a soft timing
  gap rather than a basis for invented assumptions.
- **Rating and action:** **Sell / Avoid** is unchanged. The lower price does not clear the expected-
  return, base-return, downside-payoff, margin-of-safety, timing, confidence, or relationship gates;
  no strategy, signal or paper order is justified.
- **Unchanged conclusion:** watchlist monitoring remains appropriate, but neither a lower-band breach
  nor exceptional volume establishes capitulation, a buy zone, or a changed operating thesis.

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

Template: `pre_profit_growth`; method: `revenue_multiple`; horizon: 12 months. The scenario table
below is the 28 August baseline and is retained provisionally; the 3 September Q2 filing requires
the queued full review to refresh its revenue, net-cash, capex, dilution, and multiple assumptions.

At USD 23.93 and 356.4 million reported common shares at 30 April, equity value is approximately USD
8.53 billion. Subtracting USD 730.8 million of cash and short-term investments and adding the USD
460 million face value of the 2030 convertible notes gives an approximate USD 8.26 billion
enterprise value, or 19.1 times the USD 433 million midpoint of FY2027 revenue guidance. The 10-Q
also reports 27.6 million unvested RSUs, 13.7 million outstanding options, and an initial 38.5
million-share conversion equivalent for the notes; capped calls offset conversion dilution only
through their USD 18.04 cap price.

The scenarios project FY2028 revenue, assign enterprise-value-to-revenue multiples, carry explicit
post-investment cash or net-cash assumptions, and divide by scenario-specific diluted shares. They
do not capitalize one quarter's positive operating cash flow as durable free cash flow: Q1 free
cash flow was negative USD 2.5 million, FY2027 capex guidance is USD 80-95 million, and the issuer
states only that available liquidity should meet at least twelve months of working-capital and capex
needs.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 30% | USD 6.42 | FY2028 revenue reaches USD 460 million, a 5x multiple reflects weak RPO conversion or margin execution, net cash after note principal and investment falls to USD 170.8 million, and dilution reaches 385 million shares. |
| Base | 50% | USD 14.36 | FY2028 revenue reaches USD 540 million, a 10x multiple recognizes durable growth but continuing capital intensity, net cash is USD 270.8 million, and RSU, option and other dilution lifts shares to 395 million. |
| Bull | 20% | USD 27.73 | FY2028 revenue reaches USD 620 million, an exceptional 18x multiple rewards sustained retention, RPO conversion and improving free cash flow, gross cash after investment is USD 680.8 million, and option, RSU and net convertible dilution lifts shares to 427 million. |

The probability-weighted fair value is USD 14.65, about 26.7% below the USD 19.98 mark. The base
case is about 28.1% below market, the bear case implies about 67.9% downside, and the deliberately
rich bull case offers about 38.8% upside. The wider bull upside does not compensate for the weighted
loss or bear asymmetry, and medium confidence further reduces usable expected return. The completed
scenarios therefore still establish no current buy zone or margin of safety.

## Idea exposure map

- **Candidate — [[ideas/idea_commercial_space_infrastructure|Commercial space infrastructure and
  geospatial data]]:** positive direction, awaiting relationship review. Planet's recurring imagery,
  analytics, dedicated tasking and satellite services provide a direct mechanism by which commercial
  and government demand can become ACV, RPO, backlog, revenue and cash flow. Materiality is supported
  by Q1 recurrence and contract visibility; reject the edge if backlog does not convert, government
  awards are cancelled or unfunded, satellite execution fails, or capital intensity and dilution
  prevent per-share cash generation. This is not a canonical accepted relationship.
- **Rejected-no-link — all other maintained ideas:** the complete catalog was checked, but no other
  idea has both a specific causal transmission mechanism and material evidenced exposure. Generic AI,
  defence, power, commodity, consumer, finance and industrial themes are too superficial to retain
  without new primary evidence.

## Catalysts and invalidation

Catalysts are Q2 revenue and margin delivery, conversion of RPO into recurring revenue, Pelican
capacity monetization, sustained net retention, and positive free cash flow after satellite and
software investment. Invalidate the constructive operating case if RPO fails to convert,
government awards are cancelled or unfunded, retention weakens, satellite or launch failures
interrupt service, gross margin declines persistently, or equity and note dilution overwhelms
per-share growth.

## Disposition

Status: **watching** with **medium** confidence and current rating **Unrated / Watch**. Q2 confirms
strong growth, recurrence, operating leverage, and liquidity, while lower RPO and backlog, higher
capex, hardware-driven revenue, and ATM dilution make the old scenario inputs incomplete. The
strengthening oversold alert is not a paper-trade entry: the provisional scenarios still show negative expected
and base returns, severe bear downside, weak payoff ratios, and no margin of safety. Complete the
queued full review by **2026-09-11**, or sooner after material contract cancellation, satellite
failure, guidance change, financing, dilution, or capital-allocation news. No conviction strategy
or paper signal is justified.

See the complete [[research-catalog]] and append-only [[log]].

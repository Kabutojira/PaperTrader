---
title: Albemarle Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-09-05"
provenance: "source_alb_q2_2026_10q_sec; source_alb_q2_2026_results_sec; source_alb_sec_submissions_20260905; source_alb_ceo_succession_20260903_sec; deterministic market and FX caches"
security_id: security_66cdcf90aac0d83e76f3
issuer_id: issuer_76c4dda166e8f840fb77
confidence: medium
next_review: "2026-10-05"
---

# Albemarle Corporation common stock

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
  "security_id": "security_66cdcf90aac0d83e76f3",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_66cdcf90aac0d83e76f3.csv",
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

The refreshed evidence supports three analytical views. Q2 year-over-year operating improvement is
large, but the current mark still sits close to the probability-weighted scenario value; the alert
window shows that the 4 September volume spike accompanied a sharp fall rather than a breakout.

```echart
{"schema_version":1,"chart_id":"alb-q2-operating-rebound","kind":"series","title":"Q2 operating rebound","description":"Reported net sales and company-defined adjusted EBITDA for the June quarters; both are USD millions, but adjusted EBITDA is non-GAAP.","as_of":"2026-06-30","sources":[{"label":"Albemarle Q2 2026 SEC-filed results exhibit","url":"https://www.sec.gov/Archives/edgar/data/915913/000091591326000101/a2q26earningsreleaseex991.htm","observed_at":"2026-09-05T17:31:04Z"}],"notes":["Q2 2025 includes the prior-period Ketjen refining-catalyst business; Albemarle sold a 51% stake on 2 March 2026.","Adjusted EBITDA is management-defined and should not be read as recurring free cash flow."],"x_axis":{"type":"category","label":"Quarter","values":["Q2 2025","Q2 2026"]},"y_axes":[{"label":"Reported amount","unit":"USD millions","format":"currency","currency":"USD"}],"series":[{"name":"Net sales","render":"bar","y_axis":0,"values":["1329.992","1743.313"]},{"name":"Adjusted EBITDA","render":"bar","y_axis":0,"values":["336.5","858.1"]}]}
```

```echart
{"schema_version":1,"chart_id":"alb-current-scenario-values","kind":"series","title":"Scenario fair values versus the 4 September mark","description":"Unchanged twelve-month normalized-earnings fair values compared with the fresh adjusted close used by this assessment.","as_of":"2026-09-04","sources":[{"label":"Albemarle Q2 2026 SEC-filed results exhibit","url":"https://www.sec.gov/Archives/edgar/data/915913/000091591326000101/a2q26earningsreleaseex991.htm","observed_at":"2026-09-05T17:31:04Z"},{"label":"PaperTrader deterministic ALB market cache","observed_at":"2026-09-05T09:19:19Z"}],"notes":["Bear/base/bull probabilities are 25%/50%/25%; probability-weighted fair value is USD 126.0125.","The USD 126.27999877929688 reference is an adjusted close, not a live quote or execution price."],"x_axis":{"type":"category","label":"Scenario","values":["Bear","Base","Bull"]},"y_axes":[{"label":"Common-share value","unit":"USD/share","format":"currency","currency":"USD"}],"series":[{"name":"Fair value","render":"bar","y_axis":0,"values":["9.93","131.25","231.62"]},{"name":"Reference mark","render":"line","y_axis":0,"values":["126.27999877929688","126.27999877929688","126.27999877929688"]}]}
```

```echart
{"schema_version":1,"chart_id":"alb-august-september-alert-window","kind":"candlestick","title":"ALB alert window through the 4 September volume anomaly","description":"Adjusted daily OHLC and volume across the exact 7 August to 4 September observation period supplied by the deterministic alert.","as_of":"2026-09-04","sources":[{"label":"PaperTrader deterministic ALB market cache","observed_at":"2026-09-05T09:19:19Z"}],"notes":["Adjusted close fell 3.68% across the full period and 4.45% on 4 September; 4 September volume was 3,239,400 shares with a 2.0198 z-score.","Yfinance is used only for monitoring marks, not fundamental evidence or trade execution."],"currency":"USD","rows":[{"at":"2026-08-07","open":"129.25","close":"131.11000061035156","low":"125.63999938964844","high":"132.99000549316406","volume":"2632600"},{"at":"2026-08-10","open":"131.3800048828125","close":"131.2100067138672","low":"129","high":"133.22000122070312","volume":"2424800"},{"at":"2026-08-11","open":"130.4499969482422","close":"129.36000061035156","low":"128.6199951171875","high":"132.47000122070312","volume":"1482500"},{"at":"2026-08-12","open":"131.77000427246094","close":"128.33999633789062","low":"127.55999755859375","high":"132.3300018310547","volume":"1921600"},{"at":"2026-08-13","open":"128","close":"130.47999572753906","low":"127.12000274658203","high":"133.6699981689453","volume":"2106100"},{"at":"2026-08-14","open":"132.02999877929688","close":"136.14999389648438","low":"131.64999389648438","high":"137.32000732421875","volume":"2340800"},{"at":"2026-08-17","open":"135.13999938964844","close":"133.99000549316406","low":"132.19000244140625","high":"135.4499969482422","volume":"1976800"},{"at":"2026-08-18","open":"131","close":"132.7100067138672","low":"129.85000610351562","high":"132.92999267578125","volume":"1277800"},{"at":"2026-08-19","open":"134.41000366210938","close":"134.27999877929688","low":"131.19000244140625","high":"135.9499969482422","volume":"1545200"},{"at":"2026-08-20","open":"132.89999389648438","close":"134.19000244140625","low":"132.8000030517578","high":"136.05999755859375","volume":"1618800"},{"at":"2026-08-21","open":"139.85000610351562","close":"143.25","low":"139.22000122070312","high":"143.94000244140625","volume":"3302100"},{"at":"2026-08-24","open":"143.25","close":"141.50999450683594","low":"140","high":"144.05999755859375","volume":"2174500"},{"at":"2026-08-25","open":"136.3000030517578","close":"133.17999267578125","low":"132.1300048828125","high":"137.1999969482422","volume":"2271000"},{"at":"2026-08-26","open":"132.57000732421875","close":"134.50999450683594","low":"131","high":"135.49000549316406","volume":"1538500"},{"at":"2026-08-27","open":"134.91000366210938","close":"135.77000427246094","low":"132.44000244140625","high":"136.88999938964844","volume":"1109200"},{"at":"2026-08-28","open":"138.75","close":"137.36000061035156","low":"135.72999572753906","high":"141.22000122070312","volume":"1446000"},{"at":"2026-08-31","open":"137.5800018310547","close":"134.97000122070312","low":"133.5399932861328","high":"138.02000427246094","volume":"1982700"},{"at":"2026-09-01","open":"132","close":"135.5399932861328","low":"131.41000366210938","high":"138.0800018310547","volume":"1553400"},{"at":"2026-09-02","open":"133.94000244140625","close":"137.75","low":"132.92999267578125","high":"138.0500030517578","volume":"2394900"},{"at":"2026-09-03","open":"135.99000549316406","close":"132.16000366210938","low":"131.92999267578125","high":"138.0500030517578","volume":"2862900"},{"at":"2026-09-04","open":"126.9000015258789","close":"126.27999877929688","low":"122.44999694824219","high":"129.25","volume":"3239400"}]}
```

## Identity

- Immutable security: `security_66cdcf90aac0d83e76f3`
- Issuer: `issuer_76c4dda166e8f840fb77`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `ALB` / `XNYS` / `USD` / equity

The verified instrument remains linked to [[ideas/idea_critical_minerals_lithium]] through
[[relationships/relationship_871e21ff73620ab8eb14]].

## Idea exposure map

- **Accepted-current — [[ideas/idea_critical_minerals_lithium]] (positive):** tighter lithium
  supply and durable EV and storage demand can raise Energy Storage realizations, volume, margins
  and cash flow. The Q2 filing and results remain current; falling prices, supply response, contract
  lags, cost, tax, capex or dilution would invalidate the edge.
- **Rejected-no-link — [[ideas/idea_solar_storage_grid_flexibility_reset]]:** stationary storage is
  a plausible lithium-demand channel, but current filings do not disclose a separately material
  stationary-storage exposure for Albemarle. It adds no measurable transmission mechanism beyond
  the accepted broader lithium-cycle relationship.
- **Rejected-no-link — [[ideas/idea_critical_minerals_copper]]:** incoming CEO Ragnar Udd's copper
  experience does not create Albemarle copper economics; no copper revenue or asset exposure is
  established.
- **Rejected-no-link — all other maintained ideas:** the complete catalog was checked against
  Albemarle's products, customers, inputs, assets, catalysts and risks. None supplies a specific,
  material causal exposure distinct from the accepted lithium-cycle edge.

## Changes since prior review

- **Facts and evidence changed:** the SEC index confirms that Q2 remains the latest operating
  filing. A 3 September Form 8-K appoints BHP commercial executive Ragnar Udd as CEO from no later
  than 1 February 2027 while Kent Masters becomes Executive Chair. It introduces transition risk
  and resource-sector operating experience but no revised guidance, cash flow or valuation input.
- **Alert changed:** the exact 7 August-4 September adjusted-close period fell 3.68%. On 4 September
  ALB fell 4.45% to USD 126.27999877929688 on 3.2394 million shares and a 2.0198 volume z-score.
  This is **risk**, not an opportunity or thesis invalidation: it follows the CEO announcement, but
  neither the filing nor the price record proves causation or a new operating impairment.
- **Assumptions unchanged:** the `cyclical_commodity` normalized-earnings method still uses
  management's USD 10/USD 20/USD 30 per kg LCE cases, normalized depreciation, interest and tax,
  136 million diluted shares, and cycle-sensitive multiples. No newer operating filing supersedes
  those inputs.
- **Scenario outputs changed only through the mark:** USD 9.93/USD 131.25/USD 231.62 fair values and
  25%/50%/25% probabilities are unchanged. The USD 126.0125 weighted value is now 0.21% below the
  USD 126.28 mark; base upside contracts to 3.94% and bear downside is 92.14%.
- **Thesis, catalysts and risks:** Q2 pricing, volume, Specialties, liquidity and capex evidence is
  unchanged. CEO handoff joins lithium-price sensitivity, contract lags, Talison disruption,
  working-capital normalization, tax, geopolitics and mandatory-convertible dilution as a monitor,
  not a hard blocker.
- **Blockers and gaps:** no hard blocker is added. Medium confidence, cyclical normalization,
  unfavorable timing, inadequate expected return and weak bear/base and expected/bear payoffs
  remain. The stale controller validation issue can resolve once this assessment validates.
- **Rating and action unchanged:** **Hold / Watch**, status **watching**, and no paper trade. The
  fresh mark removes the prior modest weighted upside but does not cross the deterministic sell
  threshold; no strategy or signal is justified.

## Current economics and thesis

Q2 confirms a substantial operating rebound. Energy Storage net sales were USD 1.277 billion and
adjusted EBITDA USD 723.5 million as realized lithium pricing rose to USD 19.53/kg LCE and volume to
65 kt. Specialties net sales rose 20.5% to USD 423.5 million and adjusted EBITDA rose 61.3% to USD
117.7 million. First-half operating cash flow was USD 1.1 billion and capex USD 170 million.

The balance sheet is materially stronger: 30 June cash was USD 1.632 billion, total debt about USD
1.877 billion, and disclosed liquidity about USD 3.2 billion. The diluted share count of about 136
million includes mandatory-convertible treatment. These facts improve resilience but do not make a
commodity producer's peak earnings recurring.

## Evidence and market alert

Primary evidence: [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/915913/000091591326000102/alb-20260630.htm),
[SEC-filed Q2 results exhibit](https://www.sec.gov/Archives/edgar/data/915913/000091591326000101/a2q26earningsreleaseex991.htm),
the [SEC submissions index](https://data.sec.gov/submissions/CIK0000915913.json), and the
[3 September CEO-succession Form 8-K](https://www.sec.gov/Archives/edgar/data/915913/000114036126035623/ef20081522_8k.htm).

The [[inbox/market-security_66cdcf90aac0d83e76f3-volume_anomaly-be69ea94fbb1|4 September volume
anomaly]] is adverse timing evidence. The close fell from USD 137.75 on 2 September to USD 132.16
on the CEO announcement date and USD 126.28 on 4 September, but the filing contains no revised
operating outlook. The current RSI of 42.09 is neutral, the close is below the 20-day average and
barely above the lower Bollinger band, while MACD remains above its signal. That mixed state and an
isolated volume event do not replace primary operating evidence.

## Valuation

Template: `cyclical_commodity`; method: `normalized_earnings`; horizon: 12 months.

The cases start with management's 2026 adjusted-EBITDA ranges at approximately USD 10, USD 20 and
USD 30/kg LCE. They use USD 0.67 billion normalized depreciation and amortization, USD 0.13 billion
interest, a 25% normalized tax rate and 136 million diluted shares. The bear/base/bull multiples are
12x/14x/12x normalized earnings; the bull multiple is deliberately lower so peak commodity earnings
are not capitalized as permanent.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 9.93 | USD 0.95 billion EBITDA near USD 10/kg LCE; contract lags, fixed costs and supply response leave only trough earnings. |
| Base | 50% | USD 131.25 | USD 2.50 billion EBITDA near USD 20/kg LCE; volume, costs and contracts broadly follow current guidance. |
| Bull | 25% | USD 231.62 | USD 4.30 billion EBITDA near USD 30/kg LCE; strong pricing persists, volumes deliver and execution remains controlled, but a cycle discount remains. |

The weighted value is USD 126.0125, about 0.21% below the USD 126.27999877929688 mark. Base upside
is about 3.94%, while bear downside is about 92.14%; medium confidence leaves usable expected return
slightly negative and below the configured 8% gate. Scenario dispersion and weak payoff asymmetry,
rather than missing valuation evidence, remain the central constraints. The fresh USD/EUR rate is
0.8604999780654907 as of 4 September, making the mark about EUR 108.66 for base-currency comparison;
the valuation itself remains in the instrument's USD currency.

## Catalysts, risks, and invalidation

Catalysts are sustained realized lithium pricing, delivery of 225-235 kt Energy Storage volume,
Specialties resilience, recurring operating cash flow after timing benefits, Wodgina offsetting the
Talison CGP3 fire, capex discipline and further leverage reduction.

Invalidate or downgrade if lithium prices revert toward the low case, contract realizations lag,
Chinese or other supply restores surplus, Talison disruption broadens, working-capital benefits
reverse, costs or taxes rise, capex discipline fails, geopolitical disruption affects joint ventures,
or mandatory-convertible dilution absorbs the recovery.

## Disposition

Status: **watching**, confidence **medium**, expected rating **Hold / Watch**. The current operating
thesis remains supported, but expected return, base upside, bear/base and expected/bear payoff, and
confidence-adjusted return do not justify allocation or a conviction strategy. Review after Q3
tests pricing and recurring cash conversion, or earlier if the CEO transition changes strategy,
guidance or capital allocation, no later than **2026-10-05**.

---
title: Albemarle Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-06"
provenance: "source_alb_q2_2026_10q_sec; source_alb_q2_2026_results_sec; deterministic market and FX caches"
security_id: security_66cdcf90aac0d83e76f3
issuer_id: issuer_76c4dda166e8f840fb77
confidence: medium
next_review: "2026-08-20"
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

## Identity

- Immutable security: `security_66cdcf90aac0d83e76f3`
- Issuer: `issuer_76c4dda166e8f840fb77`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `ALB` / `XNYS` / `USD` / equity

The verified instrument remains linked to [[ideas/idea_critical_minerals_lithium]] through
[[relationships/relationship_871e21ff73620ab8eb14]].

## Changes since prior review

- **Facts and evidence changed:** Q2 replaced Q1 as the latest reported quarter. Net sales were USD
  1.743 billion, adjusted EBITDA USD 858 million, operating cash flow USD 710 million, and
  company-defined free cash flow USD 638 million. Energy Storage realized price reached USD 19.53/kg
  LCE and volume 65 kt LCE, up 60.5% and 11% year over year. Cash conversion benefited from a larger
  Talison dividend and non-recurring working-capital timing, so it is not fully recurring.
- **Assumptions and valuation changed:** the former `valuation_unsupported` blocker is resolved.
  Management retained explicit USD 10/USD 20/USD 30 per kg LCE cases, disclosed approximately 136
  million diluted shares, and reduced expected capex to approximately USD 500 million. A
  `cyclical_commodity` normalized-earnings assessment now uses those three observed-price cases,
  normalized depreciation, interest, tax and cycle-sensitive multiples.
- **Scenario outputs changed:** no prior scenario values existed. New 12-month bear/base/bull common-
  share values are USD 9.93/USD 131.25/USD 231.62 with 25%/50%/25% probabilities. The probability-
  weighted value is about USD 126.01 versus the USD 118.84 reference mark.
- **Thesis, catalysts, and risks:** stronger realized pricing, volume, Specialties performance,
  liquidity and lower capex upgrade current operating evidence. Lithium-price sensitivity, contract
  lags, Talison disruption, working-capital normalization, tax, geopolitical exposure and mandatory-
  convertible dilution remain material rather than resolved.
- **Blockers and gaps:** `valuation_unsupported` is removed. Medium confidence, uncertain cyclical
  normalization, weak payoff asymmetry, inadequate expected-return compensation and event timing
  remain; no new hard blocker is added.
- **Rating and action:** the conclusion moves from an unrated unsupported valuation to **Hold /
  Watch**. The base case is modestly above market, but confidence-adjusted expected return and the
  bear-case payoff remain below the portfolio gates, so no allocation or strategy is justified.
- **Unchanged conclusion:** status remains **watching** and there is no paper trade. The accepted
  lithium-cycle relationship remains relevant, and the thesis still depends primarily on sustained
  realized lithium pricing rather than one quarter's accounting profit or cash timing.

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

Primary evidence: [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/915913/000091591326000102/alb-20260630.htm)
and [SEC-filed Q2 results exhibit](https://www.sec.gov/Archives/edgar/data/915913/000091591326000101/a2q26earningsreleaseex991.htm).

The [[inbox/market-security_66cdcf90aac0d83e76f3-volume_anomaly-11e8b42f0b00|31 July volume
anomaly]] followed a 13.22% adjusted-close decline from 2 July to USD 117.64 on volume of 3.65
million shares. It is classified as **risk**, not a valuation signal: Q2 had not yet been released,
and the alert showed elevated trading around a falling one-month trend without primary evidence of
a company-specific impairment. By 5 August the deterministic close was USD 118.84, RSI was 38.33,
and volume z-score 0.30; momentum had stabilized but remained below the 50-day and 200-day averages.
Because results were published after the 5 August close, this reference mark does not yet contain a
regular-session reaction to Q2.

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

The weighted value is about USD 126.01, only about 6.0% above the USD 118.84 mark. Base upside is
about 10.4%, but bear downside is about 91.6%; medium confidence further reduces the usable expected
return below the configured 8% gate. Scenario dispersion, rather than a lack of explicit valuation,
is now the central constraint.

## Catalysts, risks, and invalidation

Catalysts are sustained realized lithium pricing, delivery of 225-235 kt Energy Storage volume,
Specialties resilience, recurring operating cash flow after timing benefits, Wodgina offsetting the
Talison CGP3 fire, capex discipline and further leverage reduction.

Invalidate or downgrade if lithium prices revert toward the low case, contract realizations lag,
Chinese or other supply restores surplus, Talison disruption broadens, working-capital benefits
reverse, costs or taxes rise, capex discipline fails, geopolitical disruption affects joint ventures,
or mandatory-convertible dilution absorbs the recovery.

## Disposition

Status: **watching**, confidence **medium**, expected rating **Hold / Watch**. Q2 improves the
operating thesis and removes the unsupported-valuation blocker, but expected return, bear/base and
expected/bear payoff, and confidence-adjusted return do not justify a conviction strategy. Review
after a regular trading session has absorbed Q2 and when another quarter tests whether pricing and
cash conversion persist, no later than **2026-08-20**.

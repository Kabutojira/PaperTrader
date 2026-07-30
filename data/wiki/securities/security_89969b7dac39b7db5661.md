---
title: YASKAWA Electric Corporation Frankfurt ordinary shares
type: security
status: maintained
tags:
  - security
  - research
  - risk
created: "2026-07-29"
updated: "2026-07-30"
provenance: "source_yaskawa_fy2026_q1_results; source_yaskawa_fy2026_q1_briefing; source_yaskawa_fy2026_q1_qa; deterministic market cache"
security_id: security_89969b7dac39b7db5661
issuer_id: issuer_a10383b9a5262a1907f8
ticker: YEC.F
venue_mic: XFRA
currency: EUR
confidence: medium
next_review: "2026-08-31"
---

# YASKAWA Electric Corporation Frankfurt ordinary shares

## Decision

**Ineligible for paper allocation.** Yaskawa has credible motion-control and industrial-robotics
economics, but the Frankfurt `YEC.F` line has insufficient liquidity for a reproducible paper
entry. The 29 July alert is a real price decline on the monitored line, not a standalone buy
signal. No conviction strategy is justified.

## Identity

- Immutable security: `security_89969b7dac39b7db5661`
- Issuer: YASKAWA Electric Corporation
- Instrument: ordinary equity traded in Frankfurt
- Venue and provider identity: `XFRA` / `YEC.F`
- Trading and valuation currency: EUR
- Issuer primary listing: Tokyo and Fukuoka, code `6506`

The monitored Frankfurt identity is unique in canonical state. It is not interchangeable with a
ticker-only reference to the more liquid Japanese line.

## Alert review

The adjusted close fell from EUR 39.20 on 1 July to EUR 25.00 on 29 July, a **36.22%** decline over
the canonical observation period. RSI was **28.44**, crossing into oversold territory. The close
remained above the EUR 21.83 lower Bollinger band and the volume z-score was **-0.46** in the
triggering snapshot. That snapshot reported 29 July turnover of 30 shares; a subsequent provider
refresh revised the same bar to zero volume without changing its OHLC or adjusted close. The
refreshed cache has nine of 21 observation-period sessions and 126 of 254 cached sessions at zero
volume, strengthening rather than resolving the venue-liquidity concern.

The move spans Yaskawa's 10 July first-quarter results. Those results provide a plausible
fundamental contributor: revenue increased 10.6%, while operating profit fell 19.2% and profit
attributable to owners fell 21.7%. Robotics revenue grew 2.0%, but Robotics operating profit fell
82.3% because of production disruption from the new ERP system and European restructuring costs.
The issuer nevertheless kept its full-year forecast unchanged and reported firm orders. The
conclusion is **operating-execution and venue-liquidity risk**, not a confirmed thesis break and
not an actionable oversold opportunity.

## Business thesis

Yaskawa sells AC servo motors and controllers, drives, industrial robots, and system-engineering
products. Motion Control participates in semiconductor equipment and data-center cooling demand;
Robotics adds exposure to automotive, general-industry, semiconductor-transfer, collaborative,
and AI-enabled robots. This provides a credible incumbent route into the broader
[[ideas/idea_humanoid_robotics_embodied_ai_components|humanoid robotics and embodied-AI component
supply chain]], but the wiki currently has no accepted canonical relationship between that idea
and this security.

First-quarter Motion Control revenue rose 21.5% and operating profit rose 50.1%. Management also
reported semiconductor-related AC-servo orders up more than 200% year on year and semiconductor
Robotics orders up 141%. These figures support demand. Contrary evidence is the severe Robotics
margin compression, dependence on cyclical capital spending, and the need to prove that ERP
normalization converts orders into deliveries and profit.

## Financial position

At 31 May 2026, Yaskawa reported JPY 57.6 billion of cash, JPY 104.7 billion of current and
non-current bonds and borrowings, and a 58.8% equity ratio. First-quarter operating cash flow was
JPY 21.4 billion and purchases of property, plant, equipment, and intangibles were JPY 7.6 billion.
The balance sheet is adequate, but not net-cash, and inventory of JPY 215.2 billion remains a
meaningful working-capital exposure.

## Bounded valuation

Management maintained FY2026 guidance of JPY 580 billion revenue, JPY 60 billion operating profit,
JPY 47 billion profit attributable to owners, and JPY 181.21 EPS. Using the issuer's JPY 170 per
EUR planning rate, a bounded **16x–20x** forward-earnings scenario implies approximately
**EUR 17.05–21.32** per share over 12 months. Against the EUR 25.00 monitored close, that is about
**31.8% downside** to the downside case and **14.7% downside** to the base case.

This is a scenario range, not a price target. It does not compensate for the monitored line's
poor liquidity, and no same-timestamp primary-market parity check is available in canonical state.

## Catalysts, risks, and invalidation

Potential catalysts are normalization of ERP-affected production, conversion of strong
semiconductor orders, recovery in European automation, and restoration of Robotics margins.
Material risks are extended ERP disruption, European restructuring costs, cyclical semiconductor
and automotive orders, inventory and working-capital pressure, foreign-exchange sensitivity, and
the Frankfurt line's sparse trading.

The operating thesis weakens if production fails to normalize, orders do not convert into revenue,
or Robotics margins remain near first-quarter levels after temporary costs recede. The monitored
instrument remains ineligible until turnover becomes sufficient for deterministic fills and a
fresh cross-venue parity check confirms the EUR line is representative.

## Evidence

- [Yaskawa FY2026 first-quarter results, 10 July 2026](https://www.yaskawa-global.com/wp-content/uploads/2026/07/20260710_en.pdf)
- [Yaskawa FY2026 first-quarter results briefing](https://www.yaskawa-global.com/wp-content/uploads/2026/07/20260710_haifu_en.pdf)
- [Yaskawa FY2026 first-quarter briefing Q&A](https://www.yaskawa-global.com/wp-content/uploads/2026/07/261Q_QA_EN.pdf)
- PaperTrader triggering market and indicator snapshot as of `2026-07-29T16:55:24Z`, source-price
  hash `13913fe9f36b6c39970bc802b6f80acc2755effa73cd8b31d7606adf7e8f16a8`
- PaperTrader subsequent cache refresh at `2026-07-30T06:16:16Z`, which preserved the EUR 25.00
  close and RSI-oversold state while revising 29 July volume to zero; source-price hash
  `15d085715e784c95486d59249904aa72c7d723a28f7f1fd58866ec716a43b91c`

Review by **2026-08-31**, or earlier after evidence that ERP operations stabilized, a material
forecast change, or a durable improvement in Frankfurt liquidity.

See the complete [[research-catalog]] and append-only [[log]].

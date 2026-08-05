---
title: "Fanuc Corporation Frankfurt ordinary shares"
type: security
status: maintained
tags:
  - security
  - research
  - risk
created: "2026-08-05"
updated: "2026-08-05"
provenance: "FANUC Corporation; deterministic market monitor"
security_id: security_96ba305ee7cd586bc348
issuer_id: issuer_b000ffd888e42845fe36
confidence: medium
next_review: "2026-08-19"
sources:
  - source_fanuc_q1_fy2026_results
  - source_fanuc_q1_fy2026_reference
---

# Fanuc Corporation Frankfurt ordinary shares

## Identity

- **Immutable security:** `security_96ba305ee7cd586bc348`
- **Issuer:** FANUC Corporation (`issuer_b000ffd888e42845fe36`)
- **Instrument:** ordinary shares traded in Frankfurt
- **Ticker / provider:** `FUC.F` / `FUC.F`
- **Venue / currency / type:** `XFRA` / EUR / equity
- **Primary economic exposure:** Japanese factory automation, industrial robots, robomachines,
  controls, drives, service, and associated physical-AI adoption.

Identity is instrument-specific: this page concerns the Frankfurt EUR line, not ticker text alone
and not the Tokyo listing as a substitutable execution venue.

## Decision summary

**Watch; no paper strategy or signal.** FANUC's quarter ended 30 June 2026 provides current primary
evidence of a strong cyclical recovery: sales rose 17.7%, operating income rose 26.1%, and the
company raised full-year guidance. The balance sheet remains exceptionally strong. However, an
earnings-multiple assessment at the EUR 35.7400016784668 Frankfurt mark produces only EUR 36.3775
probability-weighted value and a EUR 36.38 base case. That return does not clear the repository's
economic gates, the Frankfurt line is thinly traded, and no accepted idea-security relationship
currently completes the allocation gate.

The 4 August bullish MACD crossover is therefore **improving technical momentum, not a verified
fundamental opportunity**. It followed a 2.99% decline over 7 July–4 August and has very small
positive trigger strength; the 5 August mark remains below neither a conservative buy zone nor a
fundamentally changed scenario.

## Changes since prior review

This is the first full security review. There is no predecessor assessment or prior security page
to revise. The review establishes the immutable identity, registers current issuer evidence,
creates a scenario-complete valuation, and sets explicit catalysts, risks, blockers, gaps, and
review conditions. No earlier thesis, rating, allocation action, scenario, catalyst, risk, blocker,
or gap was silently replaced.

## Alert review

- **Canonical trigger:** `macd_cross_above_signal`, entered on **2026-08-04**.
- **Exact observation period:** 2026-07-07 through 2026-08-04.
- **Period return:** -2.9943%; 4 August adjusted close: EUR 35.959999084472656.
- **Current assessment mark:** EUR 35.7400016784668 on 2026-08-05, retrieved at
  2026-08-05T18:22:39Z.
- **Source-price hash:** `20c79ccb05957caa272b377ce01b842f64ca1c74fd7696606987e23ab44fb46f`.
- **Disposition:** modestly constructive momentum but not a catalyst, valuation dislocation, or
  standalone entry signal. The very low Frankfurt volume reinforces caution about reading the
  crossover as broad price discovery.

See the deterministic packet [[inbox/market-security_96ba305ee7cd586bc348-macd_cross_above_signal-3076adb7c502]].

## Current primary evidence

FANUC's consolidated results for the quarter ended 30 June 2026 reported net sales of JPY 231.035
billion, operating income of JPY 53.492 billion, ordinary income of JPY 68.193 billion, and net
income attributable to owners of JPY 50.981 billion. Year over year, these rose 17.7%, 26.1%,
32.3%, and 34.7%, respectively. The operating margin was about 23.2%, versus about 21.6% in the
prior-year quarter.

The issuer raised FY2026 guidance to JPY 948.1 billion of sales, JPY 218.0 billion of operating
income, and JPY 198.0 billion of attributable net income, or JPY 212.18 per share. The assumptions
for July 2026 through March 2027 are JPY 150/USD and JPY 175/EUR. The reference material says FA
sales increased with demand in China and India, robotics grew in the Americas and China, and
robomachine sales grew in China. These are broad industrial-cycle signals; the issuer does not
separately establish material humanoid revenue.

At 30 June 2026, cash and bank deposits were JPY 721.468 billion, marketable securities JPY 40.800
billion, investment securities JPY 231.110 billion, total liabilities JPY 198.875 billion, and
net assets JPY 1.910 trillion. Average shares in the quarter were 933.158 million and period-end
shares excluding treasury stock were about 933.158 million. This financial capacity is a major
source of resilience, although excess cash does not eliminate cyclicality or valuation risk.

Primary evidence:

- [FANUC consolidated quarterly financial results, quarter ended 30 June 2026](https://www.fanuc.co.jp/en/ir/announce/pdf/2026/financialresult202606_e.pdf)
- [FANUC Q1 FY2026 financial-results reference material](https://www.fanuc.co.jp/en/ir/announce/pdf/2026/reference202606_e.pdf)

## Thesis and causal mechanism

FANUC can benefit as manufacturers expand automation and physical-AI capabilities. Its control,
servo, robot, robomachine, application, and service stack can monetize factory investment without
requiring general-purpose humanoids to reach scale. Installed-base expertise, reliability,
integrated controls, global support, and a fortress balance sheet support durable economics through
a cycle.

This is relevant to [[ideas/idea_humanoid_robotics_embodied_ai_components]], but only as a bounded
candidate link. Current results demonstrate conventional automation demand and platform capability;
they do **not** prove repeat paid humanoid deployments, humanoid-specific revenue materiality, or an
accepted canonical relationship.

## Contrary evidence and risks

- Automation demand is cyclical and sensitive to machine-tool, electronics, automotive, China, and
  global capital-spending conditions.
- Trade policy, geopolitical restrictions, and exchange rates can alter reported earnings and
  demand. The revised forecast embeds explicit JPY 150/USD and JPY 175/EUR assumptions.
- Chinese competitors and customer localization can pressure pricing and share.
- Humanoid and physical-AI demonstrations may not translate into reliable, high-margin deployments.
- The Frankfurt line's intermittent zero-volume sessions and low recent volume create material
  spread and execution-quality risk even though the underlying issuer is large.
- A large net-cash position supports downside but can depress capital efficiency if not deployed or
  returned productively.

## Valuation

**Template:** `mature_compounder`; **method:** `earnings_multiple`; **horizon:** 12 months.

The starting point is issuer guidance of JPY 212.18 FY2026 EPS. Using the issuer's JPY 175/EUR
forecast assumption implies about EUR 1.21 per ordinary share before scenario adjustments. The
cases vary cycle strength, margin conversion, FX, and the earnings multiple; they do not capitalize
the current quarter as a permanent peak.

| Case | Probability | Fair value | Key assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | EUR 24.25 | About 20x guided-equivalent earnings as China/capital spending weakens, FX is less helpful, and competitive pricing limits margin conversion. |
| Base | 50% | EUR 36.38 | About 30x guided-equivalent earnings; raised guidance is broadly delivered, conventional automation grows, and margins remain near normalized strong levels. |
| Bull | 25% | EUR 48.50 | About 40x guided-equivalent earnings as broad automation demand, physical-AI adoption, service mix, and margins exceed the revised plan. |

Probability-weighted fair value is **EUR 36.3775**, only about **1.78%** above the EUR
35.7400016784668 mark before confidence adjustment. The base case offers about 1.79% upside while
the bear case implies about 32.15% downside. This fails expected-return, base-upside, payoff, and
margin-of-safety gates. A buy zone would require a materially lower mark or materially stronger,
primary-evidence-backed per-share earnings assumptions—not the MACD transition alone.

## Catalysts, invalidation, and review

Potential positive catalysts are delivery against the raised FY2026 forecast, broad-based order
and sales growth across FA/robot/robomachine, sustained or improving operating margin, physical-AI
commercial wins with disclosed economics, and productive capital returns. Negative catalysts are
a guidance cut, China or global capex contraction, material margin pressure, adverse FX, or weak
cash deployment.

The thesis is invalidated if FANUC cannot sustain competitive economics through the automation
cycle, loses material control/robot share, or physical-AI investment fails to produce profitable
commercial demand while valuation continues to price it in.

Review by **2026-08-19**, or sooner upon revised guidance, material order disclosure, a large FX or
price move, evidence on paid physical-AI deployments, or a change in Frankfurt trading liquidity.
Upgrade only if fresh scenarios clear all canonical gates and the relationship evidence is
accepted. Downgrade if earnings, margins, competitive position, or liquidity deteriorates.

## Assessment anchors

- Thesis: **60** — current primary evidence supports conventional automation, but humanoid-specific
  economics remain unproven.
- Business quality: **80** — integrated technology, installed base, margins, and resilience indicate
  durable advantages.
- Balance sheet: **100** — net financial strength provides substantial downside protection.
- Valuation: **40** — scenario expected return is below the economic hurdle.
- Timing: **40** — weak crossover confirmation and no near-term valuation gap.
- Liquidity: **40** — the Frankfurt line has material volume and spread constraints.
- Risk penalty: **60** — cyclical, China, FX, competition, and listing-liquidity risks constrain
  sizing.
- Confidence: **medium**.
- Hard blockers: none; canonical soft gaps are `confidence_medium`, `timing_unfavorable`, and
  `valuation_not_compelling`. The deterministic allocation frontier separately captures the
  pending relationship, while Frankfurt liquidity and unproven humanoid revenue remain explicit
  research risks.

See the complete [[research-catalog]], current [[index]], and append-only [[log]].

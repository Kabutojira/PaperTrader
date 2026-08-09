---
title: Arista Networks, Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-09"
provenance: "source_anet_q1_2026_earnings; source_anet_q1_2026_10q; source_anet_q2_2026_earnings; source_anet_q2_2026_10q; source_anet_q2_2026_8k_exhibit; source_anet_sec_submissions_20260808"
security_id: security_6f9a1450edceb9307c9a
issuer_id: issuer_29ad971dc8b75eac1b79
confidence: medium
next_review: "2026-08-23"
---

# Arista Networks, Inc. common stock

## Identity

- Immutable security: `security_6f9a1450edceb9307c9a`
- Issuer: `issuer_29ad971dc8b75eac1b79`
- Instrument: common stock, NYSE (`XNYS`), USD
- Provider identity: `ANET` / `XNYS` / `USD` / equity

Arista is a direct networking exposure within
[[ideas/idea_ai_compute_networking_hyperscaler_monetization]] through the accepted
[[relationships/relationship_e5f55616b9beaf661080]].

## Changes since prior review

- **Facts and evidence:** no new issuer facts appeared after the accepted 8 August quick check. The
  SEC-hosted Q2 filing and results exhibit were fetched again on 9 August and retained identical
  hashes. Q2 revenue, USD 0.95 GAAP diluted EPS, USD 2.7765 billion of first-half operating cash
  flow, USD 13.3433 billion of cash plus current marketable securities, Q3 guidance, and USD 9.7
  billion of purchase commitments remain the current primary evidence.
- **Assumptions:** the prior unsupported state is resolved through a full `mature_compounder`
  earnings-multiple review. The 12-month scenarios normalize forward GAAP EPS at USD 4.00, USD 4.80,
  and USD 5.60 and apply 30x, 38x, and 45x multiples. The base and bull cases require sustained AI
  demand and operating leverage; the bear case captures customer, mix, commitment, and multiple
  compression.
- **Valuation inputs and outputs:** valuation changes from unsupported with no scenarios to USD
  120.00/USD 182.40/USD 252.00 bear/base/bull values at 25%/50%/25% probabilities. Probability-
  weighted fair value is USD 184.20. At USD 188.67, expected return is about -2.37%, base return
  about -3.32%, bear return about -36.40%, and bull return about 33.57%.
- **Thesis, catalysts, and risks:** Q2 upgrades the evidence for demand conversion, margins, and
  liquidity. Q3 guide execution and broader AI Ethernet adoption remain catalysts. Customer and
  supplier concentration, demand timing, inventory, binding commitments, and premium valuation are
  unchanged risks and are now reflected explicitly in the scenarios.
- **Blockers and gaps:** the hard valuation-support blocker is resolved. Medium confidence,
  concentration sensitivity, unfavorable timing, insufficient margin of safety, and an
  uncompelling expected return remain soft gaps.
- **Rating and portfolio action:** the accepted Unrated / Watch quick-check conclusion becomes Hold
  / Watch after completing valuation. The portfolio action remains unchanged: no strategy, signal,
  order, or paper exposure.

## Economics and thesis

Q2 revenue was USD 3.036 billion, up 37.7% year over year, with 45.4% GAAP operating margin and USD
0.95 diluted GAAP EPS. First-half operating cash flow was USD 2.7765 billion. At 30 June, USD 2.2902
billion of cash plus USD 11.0531 billion of current marketable securities provide substantial
resilience. Q3 revenue guidance of approximately USD 3.3 billion supports continued growth.

Arista's Ethernet switching, routing, EOS software, and services can convert AI and cloud-network
investment into revenue, earnings, and cash. That mechanism remains exposed to a limited set of
large buyers, customer-built alternatives, competing architectures, merchant silicon, qualification
and acceptance periods, and volatile AI capital expenditure. Non-cancellable purchase commitments
of USD 9.7 billion, including USD 9.4 billion expected within 12 months, amplify forecast error.

## Valuation

Template: `mature_compounder`; method: `earnings_multiple`; horizon: 12 months.

| Scenario | Probability | Normalized forward GAAP EPS | Multiple | Fair value | Return vs USD 188.67 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Bear | 25% | USD 4.00 | 30x | USD 120.00 | -36.40% |
| Base | 50% | USD 4.80 | 38x | USD 182.40 | -3.32% |
| Bull | 25% | USD 5.60 | 45x | USD 252.00 | 33.57% |

The probability-weighted fair value is USD 184.20, about 2.37% below the mark. The valuation is
per-share and uses GAAP earnings so stock compensation and dilution remain inside the denominator.
The base case assumes substantial delivery against Q3 guidance with durable AI-networking demand;
the bull case requires sustained wins, software attachment, and operating leverage; the bear case
allows growth deceleration, customer weakness, gross-margin pressure, commitment losses, and
multiple compression.

## Catalysts, risks, and invalidation

Catalysts are Q3 revenue and GAAP earnings delivery, durable AI back-end and front-end Ethernet wins
with profitable software and service attachment, and broader customer contribution. Invalidate if
Ethernet loses share, major customers slow or internalize networking, AI capex or acceptance slows,
supplier concentration constrains launches, commitments create inventory losses, or per-share
earnings decelerate enough that a premium multiple cannot be supported.

Upgrade requires a lower entry price or higher auditable per-share earnings that clears expected-
return, base-return, downside-payoff, margin-of-safety, confidence, and relationship gates.

## Disposition

Status: **watching**, rating **Hold / Watch**, confidence **medium**, and allocation **ineligible**.
The USD 188.67 mark exceeds both base and probability-weighted fair values. No conviction strategy,
signal, order, or paper trade is justified. Review by **2026-08-23**, or earlier after a material
customer, architecture, earnings, guidance, commitment, or price change.

## Evidence and provenance

- [Arista Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1596532/000159653226000175/anet-20260630.htm)
  — financial statements, cash flow, concentration, inventory, commitments, and risks; hash checked
  unchanged on 2026-08-09.
- [Arista Q2 2026 results, SEC-filed Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/1596532/000159653226000174/ex991q226-earningsrelease.htm)
  — Q2 revenue, margins, EPS, and Q3 guidance; hash checked unchanged on 2026-08-09.
- `data/market/latest.csv`, `data/market/indicators.csv`, and `data/market/fx/USD_EUR.csv` —
  identity-matched paper mark, deterministic market state, and USD/EUR conversion observed
  2026-08-09T11:05:22Z, with market data as of 2026-08-08T19:23:43Z.

See the complete [[index]] and append-only [[log]] for repository context.

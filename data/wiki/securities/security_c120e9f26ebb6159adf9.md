---
title: ABB Ltd sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-07-28"
provenance: "source_abb_q2_2026_results; source_abb_share_listing_2026"
security_id: security_c120e9f26ebb6159adf9
issuer_id: issuer_e60cfde16e515ef00e35
confidence: medium
next_review: "2026-08-27"
---

# ABB Ltd sponsored ADR

## Identity

- Immutable security: `security_c120e9f26ebb6159adf9`
- Issuer: `issuer_e60cfde16e515ef00e35`
- Instrument: non-listed Level I ADR traded over the counter (`XOTC`), USD
- Provider identity: `ABBNY` / `XOTC` / `USD` / equity

ABB's current listing page confirms that ABBNY is a non-listed Level I ADR and reports
1,814,919,203 ABB shares outstanding at June 30, 2026. The instrument distinction matters for
venue and liquidity controls. The bounded review tests exposure to
[[ideas/idea_humanoid_robotics_embodied_ai_components]].

## Economics and thesis

ABB's current operating business is performing strongly. Q2 2026 orders were USD 12.042 billion,
up 30%, revenue was USD 9.475 billion, up 14%, operational EBITA margin was 20.2%, and continuing-
operations operating cash flow rose 34% to USD 1.303 billion. First-half free cash flow was USD
2.131 billion, up 42%. Net debt was USD 2.320 billion and net debt to EBITDA was 0.3. This supports
ABB as a high-quality electrification and industrial-automation company.

It does not support ABB as a durable public robotics proxy. ABB still expects about USD 4.8 billion
of net proceeds from the Robotics divestment in the second half of 2026 and plans to redeploy those
proceeds toward the roughly USD 5.5 billion Rotork acquisition. Shareholders therefore lose the
direct Robotics exposure while assuming acquisition and integration risk. ABB still does not
separately disclose recurring RobotStudio revenue or installed-base service economics.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q2 orders rose 30%, revenue 14%, and backlog 27%. | Electrification and automation demand is converting, with book-to-bill of 1.27. |
| Continuing-operations operating cash flow rose 34%; first-half free cash flow rose 42%. | Group cash conversion is strong. |
| Net debt was USD 2.320 billion and net debt/EBITDA was 0.3. | The balance sheet has capacity, although the planned transaction consumes it. |
| Robotics net proceeds are expected in the second half of 2026. | ABB is a temporary, not durable, direct robotics exposure. |
| ABB proposes a roughly USD 5.5 billion Rotork acquisition. | Actuator exposure expands, but integration and capital-allocation risk rise. |
| The current ADR mark is USD 96.97 with 118,209 shares of daily provider volume. | Price and trading data are current, though OTC liquidity is weaker than a primary exchange listing. |

Primary evidence: [ABB Q2 2026 results](https://search.abb.com/library/Download.aspx?DocumentID=9AKK108472A9735&LanguageCode=en&DocumentPartId=&Action=Launch)
and [ABB share listing data](https://global.abb/group/en/investors/investor-and-shareholder-resources/share-listing).

## Valuation, catalysts, and risks

ABBNY closed at USD 96.97 on 2026-07-27. A bounded 12-month downside scenario applies a 24-times
multiple to USD 2.70 of earnings per share, producing USD 64.80, or 33.2% downside. A base scenario
allows earnings per share to reach USD 3.05 and applies a 28-times multiple, producing USD 85.40,
or 11.9% downside. The USD 2.70 downside case is below the USD 2.82 annualized first-half basic EPS;
the base case assumes continued operating growth. These are scenarios rather than price targets:
the multiples are judgmental, and disposal, tax, separation, Rotork integration, capital returns,
and ADR mechanics can change per-share outcomes. Both values remain below the current mark and fail
the configured 20% margin-of-safety requirement.

Catalysts are disposal completion at expected net proceeds, disciplined redeployment, sustained
positive book-to-bill, and margin/cash conversion. Invalidate the physical-AI relationship on the
Robotics sale; invalidate the broader quality thesis if large acquisitions dilute returns, data-
centre and industrial orders reverse, margins normalize sharply, or cash conversion weakens.

## Disposition

Status: **watching**, assessment **baseline**, confidence **medium**. Current evidence, balance-
sheet strength, a fresh mark and adequate paper-monitoring liquidity clear hard eligibility gates.
The pending Robotics exit, Rotork integration, OTC instrument, judgmental transaction-adjusted
valuation, negative base-case upside, unfavorable timing, and unavailable accepted relationship are
explicit gaps. Review by **2026-08-27**, or sooner on disposal or acquisition completion. No
conviction strategy is justified because ABB will cease to be the requested direct robotics
exposure and both bounded values remain below the market price.

See [[index]] for the current paper-only investor decision.

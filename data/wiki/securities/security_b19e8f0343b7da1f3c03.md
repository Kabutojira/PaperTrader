---
title: Shenzhen Creality 3D Technology Co., Ltd. H shares
type: security
status: maintained
tags:
  - security
  - research
  - risk
created: "2026-09-06"
updated: "2026-09-06"
provenance: "source_creality_2026_prospectus; source_creality_2026_interim_report; source_creality_2026_august_monthly_return; deterministic market cache"
security_id: security_b19e8f0343b7da1f3c03
issuer_id: issuer_dbce14a826d1d2860ea4
confidence: medium
next_review: "2026-09-20"
---

# Shenzhen Creality 3D Technology Co., Ltd. H shares

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
  "security_id": "security_b19e8f0343b7da1f3c03",
  "currency": "HKD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_b19e8f0343b7da1f3c03.csv",
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
```echart
{
  "schema_version": 1,
  "chart_id": "creality-product-mix-2023-2025",
  "kind": "series",
  "title": "Creality revenue mix is shifting beyond printer hardware",
  "description": "Audited annual revenue by product category. Consumables and scanners expanded much faster than printers, while digital products and services remained immaterial.",
  "as_of": "2025-12-31",
  "sources": [
    {"label": "Creality global offering prospectus", "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0520/2026052000023.pdf", "observed_at": "2026-09-06T09:58:00Z"}
  ],
  "notes": [
    "RMB millions; figures are rounded from audited RMB thousands.",
    "Digital services include cloud memberships, model commissions and printed products, and are grouped as services here."
  ],
  "x_axis": {"type": "category", "label": "Financial year", "values": ["2023", "2024", "2025"]},
  "y_axes": [{"label": "Revenue", "unit": "RMB million", "format": "currency", "currency": "CNY"}],
  "series": [
    {"name": "3D printers", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["1403.796", "1416.124", "1784.952"]},
    {"name": "Consumables", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["136.203", "261.534", "418.408"]},
    {"name": "3D scanners", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["41.530", "207.585", "365.701"]},
    {"name": "Laser engravers", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["111.232", "163.423", "225.434"]},
    {"name": "Accessories and other", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["188.341", "236.330", "326.261"]},
    {"name": "Digital and print services", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["1.760", "3.332", "6.284"]}
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "creality-growth-versus-cash-2023-2025",
  "kind": "series",
  "title": "Revenue growth has not yet produced durable cash conversion",
  "description": "Audited revenue, gross profit, adjusted net profit and operating cash flow. Revenue growth accelerated in 2025, but adjusted profit declined and operating cash flow turned negative.",
  "as_of": "2025-12-31",
  "sources": [
    {"label": "Creality global offering prospectus", "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0520/2026052000023.pdf", "observed_at": "2026-09-06T09:58:00Z"}
  ],
  "notes": [
    "RMB millions; figures are rounded from audited RMB thousands.",
    "Adjusted net profit is an issuer-defined non-IFRS measure and excludes share compensation, listing costs and the 2025 pre-IPO investor charge."
  ],
  "x_axis": {"type": "category", "label": "Financial year", "values": ["2023", "2024", "2025"]},
  "y_axes": [{"label": "Financial result", "unit": "RMB million", "format": "currency", "currency": "CNY"}],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["1882.862", "2288.328", "3127.040"]},
    {"name": "Gross profit", "render": "line", "y_axis": 0, "values": ["599.529", "707.801", "974.890"]},
    {"name": "Adjusted net profit", "render": "line", "y_axis": 0, "values": ["130.134", "97.199", "92.385"]},
    {"name": "Operating cash flow", "render": "line", "y_axis": 0, "values": ["161.123", "172.911", "-63.977"]}
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "creality-h1-product-growth-2026",
  "kind": "series",
  "title": "Consumables led first-half 2026 growth while printer revenue stalled",
  "description": "Like-for-like unaudited first-half revenue by product group. This is the clearest issuer-level evidence for the utilization-times-consumables hypothesis.",
  "as_of": "2026-06-30",
  "sources": [
    {"label": "Creality 2026 interim report", "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0831/2026083102371.pdf", "observed_at": "2026-09-06T09:58:00Z"}
  ],
  "notes": [
    "RMB millions; product grouping follows the interim report.",
    "Growth does not prove revenue per installed printer because Creality does not disclose installed-base or print-hour cohorts."
  ],
  "x_axis": {"type": "category", "label": "Period", "values": ["H1 2025", "H1 2026"]},
  "y_axes": [{"label": "Revenue", "unit": "RMB million", "format": "currency", "currency": "CNY"}],
  "series": [
    {"name": "3D printers", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["841.196", "842.417"]},
    {"name": "Scanners and engravers", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["279.295", "325.860"]},
    {"name": "Consumables", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["186.543", "276.556"]},
    {"name": "Accessories and other", "render": "bar", "y_axis": 0, "stack": "revenue", "values": ["133.554", "181.000"]}
  ]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "creality-valuation-scenarios-2026",
  "kind": "series",
  "title": "Creality scenario fair values remain below the current price in bear and base cases",
  "description": "Twelve-month per-share fair values from the accepted revenue-multiple assessment compared with the identity-matched 4 September 2026 market mark.",
  "as_of": "2026-09-06",
  "sources": [
    {"label": "Creality 2026 interim report", "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0831/2026083102371.pdf", "observed_at": "2026-09-06T10:10:00Z"},
    {"label": "Creality global offering prospectus", "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0520/2026052000023.pdf", "observed_at": "2026-09-06T10:10:00Z"},
    {"label": "Canonical PaperTrader market cache", "observed_at": "2026-09-06T10:07:27Z"}
  ],
  "notes": [
    "Scenario probabilities are 30% bear, 50% base and 20% bull; the probability-weighted fair value is HKD18.40.",
    "Fair values are judgment-owned research outputs; deterministic code calculates returns, the weighted value, buy-below price and margin of safety."
  ],
  "x_axis": {"type": "category", "label": "Scenario", "values": ["Bear", "Base", "Bull"]},
  "y_axes": [{"label": "Fair value per H share", "unit": "HKD/share", "format": "currency", "currency": "HKD"}],
  "series": [
    {"name": "Scenario fair value", "render": "bar", "y_axis": 0, "values": ["10", "18", "32"]},
    {"name": "Current price", "render": "line", "y_axis": 0, "values": ["26", "26", "26"]}
  ]
}
```

Installed-base, print-hours, consumables per printer and like-for-like peer multiples are omitted
because Creality does not disclose comparable primary-source series.

## Changes since prior review

The operating evidence, thematic conclusion and risk assessment are unchanged from the immediately
preceding blocked review. The deterministic market refresh restored an identity-matched `ok` mark
of HKD26.00 and the matching HKD/EUR conversion record. This resolves the sole hard blocker and
allows the first scenario-complete assessment. The new HKD10/HKD18/HKD32 bear/base/bull range does
not support the current price: probability-weighted value is HKD18.40, so the security moves from
unrated/watch-only to **Sell / Avoid**. No thesis, catalyst or evidence-source confidence was
upgraded, no canonical relationship was accepted, and no strategy or paper order was created.

## Research status

The research is complete through the 2026 interim report and the 4 September 2026 market close.
The schema-version-two assessment uses a `pre_profit_growth` template and a `revenue_multiple`
method. Its canonical rating is **Sell**, its portfolio action is **Avoid**, and it is ineligible
for allocation because expected and base returns, payoff asymmetry and margin of safety all fail
the required gates; the causal relationship also remains pending. No strategy, signal or paper
order is justified.

## Identity and listing

- Immutable security: `security_b19e8f0343b7da1f3c03`
- Issuer: `issuer_dbce14a826d1d2860ea4`
- Instrument: ordinary H shares, primary listing on the Hong Kong Stock Exchange (`XHKG`), HKD
- Provider identity: `3388.HK` / `XHKG` / `HKD` / equity
- Issued shares: 477,854,151 H shares and no treasury shares at 31 August 2026
- Canonical reference: HKD 26.00 close on 4 September 2026, retrieved successfully at
  2026-09-06T10:07:27Z

At the cached price and official issued-share count, the implied equity value is approximately
HKD12.42 billion. Converting June cash less borrowings on the approximate prospectus offer-rate
basis gives a contextual enterprise value near HKD11.38 billion, or about 3.2 times 2025 revenue.
This normalization is approximate rather than a current CNY/HKD market input and is used only to
frame the scenario multiples, not as a deterministic accounting value.

## Business and revenue mix

Creality is a global consumer 3D-creation company spanning desktop printers, filament and other
consumables, scanners, laser engravers, accessories, slicing and cloud workflows, model content and
an early physical-goods marketplace. It sells directly online and through distributors. Its 2025
network covered about 140 countries and regions, 81 online stores and 2,422 distributors; online
sales increased from 35.7% of 2023 revenue to 48.5% in 2025.

Revenue grew from RMB1.88 billion in 2023 to RMB3.13 billion in 2025. Hardware remains the economic
base, but printer share fell from 74.6% to 57.1% while consumables rose from 7.2% to 13.4%, scanners
from 2.2% to 11.7%, and accessories and other from 10.0% to 10.4%. Cloud memberships, model
commissions and printed products were only 0.2% of 2025 revenue. The platform narrative is therefore
strategically relevant but financially immature.

America generated RMB662.4 million, Europe RMB404.1 million, Greater China RMB391.8 million and
other regions RMB167.5 million in H1 2026. International exposure adds scale but also tariffs,
channel cost and currency sensitivity.

## Theme exposure and causal mechanism

The link to [[ideas/idea_ai_driven_democratization_physical_creation]] is a **candidate**, not an
accepted relationship. Exposure is very high and positive:

`AI or scan-generated geometry → easier slicing and printability repair → more users and objects →
more printer utilization → more branded filament, accessories and cloud activity`.

Near term, the i7 photo-to-model function, image-to-3D tools, automated mesh repair and MakeNow apps
can reduce creation friction. Medium term, RFID profiles, multi-colour and multi-material systems
could translate utilization into repeat materials purchases. Long term, Creality Cloud and Nexbie
could combine content, creation, commerce and physical fulfillment, but current service revenue is
too small to value as a proven platform.

H1 2026 supports the recurring-consumables mechanism more strongly than the hardware thesis:
printer revenue grew only 0.1%, consumables 48.3%, and scanners plus engravers 16.7%. Management
attributes higher consumption to multi-colour use, RFID-enabled ease and a broader material range.
Cloud newly registered users grew 77.1%, monthly active users 68.3%, active creators 94.3%, public
models 137.6% and membership revenue 60.1%. These are issuer-defined activity metrics without
absolute cohorts, retention, ARPU or platform gross profit.

## Competitive advantage and market position

Potential advantages are breadth, a large global channel, brand, an integrated printer-scanner-
material-cloud workflow, direct-commerce data, 957 granted patents and a 890-person R&D team at
June 2026. Creality spent RMB143.4 million, or 8.8% of H1 revenue, on R&D.

The prospectus' commissioned CIC study placed Creality second in global consumer-printer 2025 GMV
with 11.2% and first in consumer scanners with 45.3%. These estimates are not independent audited
market shares. More importantly, the same study reported an unnamed private leader above 40% and
said Creality's printer share declined from 2021 to 2025. The private leader's profile corresponds
to the competitive pattern represented by Bambu Lab in the theme page: integrated ease of use and
fast product iteration can compress price, shorten product cycles and force higher R&D and marketing.

Printer gross margin declined from 30.9% in 2023 to 28.4% in 2025; consumables improved from 30.0%
to 35.5%. This is useful but not yet proof of lock-in. Creality sells more than 1,400 consumables
SKUs, but filament remains contestable, third-party compatible and partly externally manufactured.

## Growth, margins and operating leverage

Company gross margin was 31.8% in 2023, 30.9% in 2024 and 31.2% in 2025. Adjusted net profit fell
from RMB130.1 million to RMB92.4 million while revenue grew, and 2025 operating cash flow turned
negative. H1 2026 made the tension clearer: revenue rose 12.9% to RMB1.63 billion, but gross margin
fell 360 basis points to 30.8%, GAAP net profit became a RMB59.1 million loss and adjusted net profit
became a RMB15.7 million loss.

The decline reflects lower launch margins and clearance pricing, rising PCB, memory and chip input
costs, marketing expense up 29.3%, G&A up 51.2%, R&D up 37.6%, and a RMB35.4 million foreign-exchange
loss. This is not the operating leverage expected from an expanding ecosystem. Evidence of gross
profit growing faster than support, marketing and R&D is required before platform optionality earns
a premium.

## Cash flow, balance sheet and capital intensity

H1 operating cash outflow worsened to RMB257.0 million from RMB149.6 million. Inventory reached
RMB772.4 million and inventory days rose to 112.5 from 98.3, increasing obsolescence risk in a fast
product cycle. The IPO and over-allotment contributed RMB1.32 billion of gross financing proceeds,
lifting cash and equivalents to RMB1.45 billion. Borrowings were RMB534.9 million, leaving about
RMB916.6 million of cash less borrowings before leases and other adjustments, but 57.4% of borrowing
matures within one year and pledged assets secure part of it.

The balance sheet is post-IPO liquid, not self-funding. Future headquarters investment, product
launches, overseas stores, cloud operations and inventory can consume the cash cushion. Share-based
compensation was RMB15.0 million in H1 2026; the August monthly return showed no additional issued
shares or treasury shares during that month.

## Customers and concentration

The five largest customers declined from 19.9% of 2023 revenue to 11.0% in 2025; the largest fell
from 5.7% to 4.0%. Concentration is therefore moderate and improving. Dependence shifts instead to
short-duration distributor contracts, online platforms, overseas consumers and paid acquisition.
Amazon/TikTok commissions and broader promotion contributed to H1 selling-cost growth. No disclosed
end customer appears individually thesis-defining.

## Catalysts

- Evidence that consumables revenue and gross profit continue to outgrow printers, with stable
  attachment, repeat purchase and lower failure rates.
- K3 multi-material commercialization, i7 adoption, further accessible printers and scanners, and
  verified AI-to-print conversion rather than app usage alone.
- Creality Cloud membership monetization with absolute users, retention, ARPU and platform margin.
- Gross-margin recovery after launch and clearance pressure, inventory normalization and positive
  operating cash flow.
- Disciplined use of IPO proceeds across R&D, overseas operations, brand and working capital.

## Risks and contrary evidence

- The strongest direct competitor already has far greater reported market share; price and feature
  competition can pass AI-created demand to users rather than shareholders.
- Hardware is still 52% of H1 2026 revenue and its growth stalled. Consumables are growing rapidly
  but were only 17% of the half-year total and are not proven proprietary.
- Cloud membership grew quickly from an undisclosed base, while digital and printed services were
  only 0.2% of 2025 revenue.
- Falling gross margin, negative adjusted profit and worsening operating cash flow contradict a
  near-term operating-leverage thesis.
- Inventory, short product cycles, channel costs, tariffs, USD/EUR exposure, IP disputes, product
  quality and liability, data and cloud security, and founder-chairman concentration add risk.
- AI-generated meshes may not be manufacturable or may increase free content without increasing
  paid printers, materials, memberships or physical-goods demand.

## Valuation

The appropriate repository template is `pre_profit_growth` with a `revenue_multiple` method because
current adjusted earnings and free cash flow are negative. A valid assessment must model 12-month
revenue growth, gross margin, cash burn, net cash, dilution and a credible route to positive free
cash flow. The official share count supports per-share calculation; the prospectus and interim
report support fundamentals and cash runway.

The accepted 12-month scenarios are:

- **Bear — HKD10.00, 30% probability:** low-single-digit revenue growth, 28–30% gross margin,
  continuing cash burn and price competition; about 1.1 times revenue after lower net cash and
  dilution.
- **Base — HKD18.00, 50% probability:** roughly 12–15% revenue growth, 31–33% gross margin and a
  credible break-even path; about 1.8–1.9 times revenue plus residual net cash.
- **Bull — HKD32.00, 20% probability:** roughly 20–25% revenue growth, at least 34% gross margin,
  positive free cash flow and a higher materials/cloud mix; about 3 times revenue plus net cash.

Against HKD26.00, bear/base/bull returns are approximately -61.5%, -30.8% and +23.1%.
Probability-weighted fair value is HKD18.40, implying an expected return of approximately -29.2%;
medium-confidence adjustment reduces the decision input to approximately -21.9%. The base-value
margin of safety is approximately -44.4%, and the required 20% discount makes HKD14.40 the
deterministic buy-below price. The IPO offer price of HKD18.80 is useful history: the current price
is about 38% higher even though H1 2026 adjusted profit and operating cash flow were negative.

## Disposition and invalidation

Research conclusion: **Sell / Avoid**. Thematic exposure is excellent, and the consumables evidence
supports the core utilization hypothesis, but excellent exposure is not an attractive investment
at this price. Current economics show weak cash conversion, launch and clearance margin pressure,
and material competitive risk; the weighted value and base case remain materially below the mark.

Invalidate the positive company-specific thesis if consumables growth converges to printer growth,
branded attachment or margin deteriorates, cloud usage fails to monetize, Creality keeps losing
printer share, gross margin remains near or below H1 2026 levels, inventory and operating cash burn
persist, or management consumes IPO proceeds without a credible path to positive free cash flow.
Upgrade only if a lower market price or stronger primary evidence on recurring gross profit, cash
conversion and competitive position clears every expected-return, base-return, payoff and
margin-of-safety gate after the candidate relationship is accepted.

## Sources

- [2026 interim report](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0831/2026083102371.pdf), published 31 August 2026.
- [Global offering prospectus](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0520/2026052000023.pdf), published 20 May 2026.
- [August 2026 monthly return](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0903/2026090300994.pdf), submitted 3 September 2026.

See the complete [[research-catalog]], [[security-catalog]], and append-only [[log]].

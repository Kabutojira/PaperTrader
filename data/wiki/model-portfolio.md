---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-09-10"
updated: "2026-09-10"
provenance: deterministic-decision-projection
snapshot_id: "decision_3f0087c0f474f071d325"
as_of: "2026-09-10T19:03:58Z"
---

# Model portfolio

**As of `2026-09-10T19:03:58Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="93.871528" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-09-10T19:03:58Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>97.172267%</dd></div>
<div><dt>Target</dt><dd>93.871528%</dd></div>
<div><dt>Action</dt><dd>Trim</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-10T19:03:58Z</dd></div>
<div><dt>As of</dt><dd>2026-09-10T19:03:58Z</dd></div>
</dl>

</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="4.242464" data-mark="35.29499816894531" data-fx="1" data-mark-currency="EUR" data-market-data-as-of="2026-09-10T15:30:00Z" data-ticker="PRX" data-company="Prosus N.V.">
<h3><a href="securities/security_8b703a8adf5f864acaa4">PRX — Prosus N.V.</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>2.827733%</dd></div>
<div><dt>Target</dt><dd>4.242464%</dd></div>
<div><dt>Action</dt><dd>Add</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>35.29499816894531 EUR</dd></div>
<div><dt>Base mark</dt><dd>35.29499816894531 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-10T19:03:58Z</dd></div>
<div><dt>As of</dt><dd>2026-09-10T15:30:00Z</dd></div>
</dl>
<p><a href="strategies/strategy_8caa208dfc702a2584a7">Strategy research</a></p>
</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="1.886008" data-mark="54.689998626708984" data-fx="0.8607000112533569" data-mark-currency="USD" data-market-data-as-of="2026-09-10T18:10:21Z" data-ticker="TCEHY" data-company="Tencent Holdings Limited">
<h3><a href="securities/security_de0d83229b369a426b99">TCEHY — Tencent Holdings Limited</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>0%</dd></div>
<div><dt>Target</dt><dd>1.886008%</dd></div>
<div><dt>Action</dt><dd>Buy</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>54.689998626708984 USD</dd></div>
<div><dt>Base mark</dt><dd>47.07168243345449593566606939 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>0.8607000112533569 · 2026-09-10T18:10:21Z</dd></div>
<div><dt>As of</dt><dd>2026-09-10T18:10:21Z</dd></div>
</dl>
<p><a href="strategies/strategy_ef910e9aff5203a0b901">Strategy research</a></p>
</article>
</div>
<p class="portfolio-base">Values use the committed EUR snapshot.</p>

<div class="portfolio-controls" aria-label="Portfolio copy and scaling tools">
<button type="button" id="copy-portfolio">Copy portfolio as TSV</button>
<a class="button-link" href="data/model_portfolio.csv" download>Download committed CSV</a>
<a class="button-link" href="data/decision_snapshot.json" download>Download snapshot JSON</a>
<label for="reference-notional">Reference portfolio value</label>
<input id="reference-notional" type="number" min="0" step="100" inputmode="decimal">
<button type="button" id="scale-portfolio">Calculate whole-share quantities</button>
</div>
<p class="scaler-notice">The calculation runs only in this browser and does not write portfolio state.</p>
<div id="scaled-portfolio" aria-live="polite"></div>

## Valuation and thesis detail

| Holding | Rating / action | Bear / base / bull | Expected | Buy below | Review | Thesis or cash role |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Cash | Unrated / Hold | —% / —% / —% | —% | — | — | Capital retained as the configured portfolio alternative. |
| [PRX — Prosus N.V.](securities/security_8b703a8adf5f864acaa4) | Buy / Initiate | -15.00212053730653548039245669% / 47.3296577353353385006530751% / 98.328385412951417212417601% | 38.8298697890659920486923207% | 41.6 | 2026-09-27T19:18:00Z | Prosus offers Tencent-dominated look-through value, growing ecommerce exposure and per-share accretion from repurchases below NAV; the current plan's economics justify a bounded long-equity baseline increase because medium confidence, holding-company concentration, private-asset valuation uncertainty, central debt, governance, capital-allocation transmission, weak momentum and insufficient diversification prevent conviction treatment. |
| [TCEHY — Tencent Holdings Limited](securities/security_de0d83229b369a426b99) | Buy / Initiate | -26.86048454119876587740257908% / 18.851712620552005449220809% / 64.5639097823027767758441971% | 18.851712620552005449220809% | 52 | 2026-09-27T19:23:20Z | Tencent's gaming, advertising and Weixin ecosystem support cash generation and repurchases; the current plan's starter economics justify only bounded long-equity exposure because medium confidence, China policy and governance exposure, investment-portfolio volatility, artificial-intelligence spending and insufficient diversification prevent conviction treatment. |

[[index|Back to today's decision]]

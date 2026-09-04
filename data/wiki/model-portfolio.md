---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-09-04"
updated: "2026-09-04"
provenance: deterministic-decision-projection
snapshot_id: "decision_23ebc3398ed8251d0a55"
as_of: "2026-09-04T05:04:33Z"
---

# Model portfolio

**As of `2026-09-04T05:04:33Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="95.072021" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-09-04T05:04:33Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>100%</dd></div>
<div><dt>Target</dt><dd>95.072021%</dd></div>
<div><dt>Action</dt><dd>Trim</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-04T05:04:33Z</dd></div>
<div><dt>As of</dt><dd>2026-09-04T05:04:33Z</dd></div>
</dl>

</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="2.960607" data-mark="37" data-fx="1" data-mark-currency="EUR" data-market-data-as-of="2026-09-03T23:56:03Z" data-ticker="PRX" data-company="Prosus N.V.">
<h3><a href="securities/security_8b703a8adf5f864acaa4">PRX — Prosus N.V.</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>0%</dd></div>
<div><dt>Target</dt><dd>2.960607%</dd></div>
<div><dt>Action</dt><dd>Buy</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>37 EUR</dd></div>
<div><dt>Base mark</dt><dd>37 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-04T05:04:33Z</dd></div>
<div><dt>As of</dt><dd>2026-09-03T23:56:03Z</dd></div>
</dl>
<p><a href="strategies/strategy_8caa208dfc702a2584a7">Strategy research</a></p>
</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="1.967372" data-mark="75.95999908447266" data-fx="0.8631600141525269" data-mark-currency="USD" data-market-data-as-of="2026-09-03T23:56:03Z" data-ticker="UBER" data-company="Uber Technologies, Inc.">
<h3><a href="securities/security_e4822686f60a96824b6e">UBER — Uber Technologies, Inc.</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>0%</dd></div>
<div><dt>Target</dt><dd>1.967372%</dd></div>
<div><dt>Action</dt><dd>Buy</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>75.95999908447266 USD</dd></div>
<div><dt>Base mark</dt><dd>65.56563388477935157257469296 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>0.8631600141525269 · 2026-09-03T23:56:03Z</dd></div>
<div><dt>As of</dt><dd>2026-09-03T23:56:03Z</dd></div>
</dl>
<p><a href="strategies/strategy_e4ada1a4934691d1f7ee">Strategy research</a></p>
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
| [PRX — Prosus N.V.](securities/security_8b703a8adf5f864acaa4) | Buy / Initiate | -18.91891891891891891891891892% / 40.5405405405405405405405405% / 89.1891891891891891891891892% | 32.4324324324324324324324324% | 41.6 | 2026-09-27T19:18:00Z | Prosus offers Tencent-dominated look-through value, growing ecommerce exposure and per-share accretion from repurchases below NAV; the current plan's economics justify bounded long-equity baseline exposure because medium confidence, holding-company concentration, private-asset valuation uncertainty, central debt, governance, capital-allocation transmission and insufficient diversification prevent conviction treatment. |
| [UBER — Uber Technologies, Inc.](securities/security_e4822686f60a96824b6e) | Buy / Initiate | -27.59346937480044257612575332% / 18.4834137503265485117942218% / 57.9778850004353980157256291% | 16.8378107815720131157970799% | 72 | 2026-09-27T19:27:50Z | Uber's scaled demand, dispatch, payments, delivery, advertising and membership network supports cash generation and may distribute autonomous supply; the current plan's starter economics justify only bounded long-equity exposure because medium confidence, a material bear case, autonomy disintermediation, insurance, regulation, incentives and dilution prevent conviction treatment. |

[[index|Back to today's decision]]

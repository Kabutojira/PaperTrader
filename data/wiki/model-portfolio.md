---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-09-03"
updated: "2026-09-03"
provenance: deterministic-decision-projection
snapshot_id: "decision_873172862c55f2655ee6"
as_of: "2026-09-03T23:19:29Z"
---

# Model portfolio

**As of `2026-09-03T23:19:29Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="98.04026" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-09-03T23:19:29Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>100%</dd></div>
<div><dt>Target</dt><dd>98.04026%</dd></div>
<div><dt>Action</dt><dd>Trim</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-03T23:19:29Z</dd></div>
<div><dt>As of</dt><dd>2026-09-03T23:19:29Z</dd></div>
</dl>

</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="1.95974" data-mark="75.95999908447266" data-fx="0.8598999977111816" data-mark-currency="USD" data-market-data-as-of="2026-09-03T21:34:54Z" data-ticker="UBER" data-company="Uber Technologies, Inc.">
<h3><a href="securities/security_e4822686f60a96824b6e">UBER — Uber Technologies, Inc.</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>0%</dd></div>
<div><dt>Target</dt><dd>1.95974%</dd></div>
<div><dt>Action</dt><dd>Buy</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>75.95999908447266 USD</dd></div>
<div><dt>Base mark</dt><dd>65.3180030388793967654758215 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>0.8598999977111816 · 2026-09-03T21:34:54Z</dd></div>
<div><dt>As of</dt><dd>2026-09-03T21:34:54Z</dd></div>
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
| [UBER — Uber Technologies, Inc.](securities/security_e4822686f60a96824b6e) | Buy / Initiate | -27.59346937480044257612575332% / 18.4834137503265485117942218% / 57.9778850004353980157256291% | 16.8378107815720131157970799% | 72 | 2026-09-27T19:27:50Z | Uber's scaled demand, dispatch, payments, delivery, advertising and membership network supports cash generation and may distribute autonomous supply; the current plan's starter economics justify only bounded long-equity exposure because medium confidence, a material bear case, autonomy disintermediation, insurance, regulation, incentives and dilution prevent conviction treatment. |

[[index|Back to today's decision]]

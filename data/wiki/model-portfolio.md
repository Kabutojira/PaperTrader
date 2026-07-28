---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-07-28"
updated: "2026-07-28"
provenance: deterministic-decision-projection
snapshot_id: "decision_420b3864086b1c654369"
as_of: "2026-07-28T09:50:10Z"
---

# Model portfolio

**Snapshot `decision_420b3864086b1c654369` · As of `2026-07-28T09:50:10Z`**

This is a paper-only, non-personalized research portfolio. Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="95.604746" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-07-28T09:50:10Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>100%</dd></div>
<div><dt>Approved target</dt><dd>95.604746%</dd></div>
<div><dt>Action</dt><dd>Trim</dd></div>
<div><dt>State</dt><dd>Pending validated paper order</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>As of</dt><dd>2026-07-28T09:50:10Z</dd></div>
</dl>

</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="4.395254" data-mark="356.8299865722656" data-fx="0.879800021648407" data-mark-currency="USD" data-market-data-as-of="2026-07-28T09:44:43Z" data-ticker="ISRG" data-company="Intuitive Surgical, Inc.">
<h3>ISRG — Intuitive Surgical, Inc.</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>0%</dd></div>
<div><dt>Approved target</dt><dd>4.395254%</dd></div>
<div><dt>Action</dt><dd>Buy</dd></div>
<div><dt>State</dt><dd>Pending validated paper order</dd></div>
<div><dt>Reference mark</dt><dd>356.8299865722656 USD</dd></div>
<div><dt>As of</dt><dd>2026-07-28T09:44:43Z</dd></div>
</dl>
<p><a href="strategies/strategy_bd005fc3733b1475b6f9">Complete research</a></p>
</article>
</div>
<p class="portfolio-base">Values use the committed EUR snapshot.</p>

<div class="portfolio-controls" aria-label="Portfolio copy and scaling tools">
<button type="button" id="copy-portfolio">Copy portfolio as TSV</button>
<a class="button-link" href="data/model_portfolio.csv" download>Download committed CSV</a>
<a class="button-link" href="data/decision_snapshot.json" download>Download snapshot JSON</a>
<label for="reference-notional">Illustrative reference notional</label>
<input id="reference-notional" type="number" min="0" step="100" inputmode="decimal">
<button type="button" id="scale-portfolio">Scale long-equity targets locally</button>
</div>
<p class="scaler-notice"><strong>Illustrative scaling only.</strong> Your scaled quantities have not passed PaperTrader's portfolio-level risk checks.</p>
<div id="scaled-portfolio" aria-live="polite"></div>

## Valuation and thesis detail

| Holding | Confidence | Downside | Base upside | Review | Thesis or cash role |
| --- | --- | ---: | ---: | --- | --- |
| Cash | — | —% | —% | — | Capital retained as the configured portfolio alternative. |
| [ISRG — Intuitive Surgical, Inc.](strategies/strategy_bd005fc3733b1475b6f9) | high | -23.2% | 2.5% | 2026-08-26T21:28:56Z | High-quality recurring procedure economics, balance-sheet strength, liquidity, and an effective score of 63 above the cash hurdle justify only the allocator's bounded 4.39% baseline target after 2.2% pending exposure; limited base upside, a 23.2% downside case, weak timing, and insufficient diversification prevent conviction treatment. |

[[index|Back to today's decision]]

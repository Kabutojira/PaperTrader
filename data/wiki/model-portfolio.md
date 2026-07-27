---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-07-27"
updated: "2026-07-27"
provenance: deterministic-decision-projection
snapshot_id: "decision_7eae4d9fa5380e578266"
as_of: "2026-07-27T15:39:59Z"
---

# Model portfolio

**Snapshot `decision_7eae4d9fa5380e578266` · As of `2026-07-27T15:39:59Z`**

This is a paper-only, non-personalized research portfolio. Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="100" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-07-27T15:39:59Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>100%</dd></div>
<div><dt>Approved target</dt><dd>100%</dd></div>
<div><dt>Action</dt><dd>No trade</dd></div>
<div><dt>State</dt><dd>No action</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>As of</dt><dd>2026-07-27T15:39:59Z</dd></div>
</dl>

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

[[index|Back to today's decision]]

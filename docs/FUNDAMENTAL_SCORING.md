# Fundamental scoring contract — rubric 1

FinanceAlerts consumes `data/tables/security_assessments.csv` by exact immutable
`security_id`. It owns its prices, technical indicators and downstream decisions.
PaperTrader remains research only and imports no FinanceAlerts data or credentials.
Scores are research components, not orders, portfolio advice or a composite rating.
The existing long-universe opinion calculations remain unchanged. For explicit
`short_candidate` instruments, current sourced business-quality, balance-sheet and
risk components also gate the stricter Short opinion described in
[data/wiki/rating-methodology.md](../data/wiki/rating-methodology.md). There is no
aggregate fundamental score or extra return penalty.

## Export and evidence

The five optional numeric columns are `valuation_score`, `business_quality_score`,
`thesis_score`, `balance_sheet_score` and `risk_penalty`. A value is a finite decimal
in [0, 100], inclusive. Higher is stronger/more attractive except `risk_penalty`,
where higher means more risk. Empty means **unassessed or unsupported**, never zero
or a neutral 50. Zero is a supported endpoint and must retain its evidence.

Every assessment carries `scoring_rubric_version="1"` and `score_details`, a JSON
object with exactly those five column names. Each component contains exactly:

```json
{"rationale":"Evidence, dates, anchor and judgment, or the specific evidence gap.","source_ids":["exact_assessment_source_id"]}
```

For a numeric component, the list must be nonempty and a subset of the assessment's
`source_ids`. Each source must be valid and associated with this instrument. New
research must open those sources through the existing broker and cite their URLs
in its final Markdown. A citation is traceability, not automatic proof of the
judgment: the rationale must connect facts, measurement period and contrary evidence
to the selected anchor. Reuse `limitations` for common uncertainties, with each
component explaining its own effect. Missing components still require a rationale;
their source list may be empty. A verified business component may be scored even
when per-share valuation is unsupported.

The CSV writer uses fixed schema columns, sorts by `security_id`, and canonicalizes
the JSON keys and whitespace. Strings remain RFC 4180 CSV cells; JSON source lists
do not change the existing pipe-separated assessment `source_ids` format. There is
no `expires_at` alias: `assessed_at` and `valid_until` retain their existing meaning.

## Anchors and overlap

Use 0/25/50/75/100 anchors consistently. Interpolation requires a reason grounded in
observed evidence; these scores are not probabilities. An unknown anchor is empty.

| Component | 0 | 25 | 50 | 75 | 100 |
| --- | --- | --- | --- | --- | --- |
| Business quality | Structurally impaired economics | Fragile economics | Evidenced mixed economics | Durable profitable advantages | Exceptional durable advantages and cash conversion |
| Thesis | Invalidated | Major contrary evidence | Balanced supporting/contrary evidence | Strongly corroborated | All material current evidence supports the thesis and risks were tested |
| Balance sheet | Insolvency pressure | Material refinancing risk | Manageable but constrained | Resilient liquidity and debt coverage | Ample liquidity and very low financial stress |
| Risk penalty | Low identified residual risk | Limited residual risk | Material residual risk | High residual risk | Severe residual risk |

Business quality owns operating economics, competitive durability and cash
conversion **before financing effects**; it excludes current price and leverage.
Balance sheet owns liquidity, maturities, leverage, financing claims and solvency;
explain sector-appropriate metrics and financial-statement dates. Thesis measures
evidence for the specific hypothesis, including falsification and contrary evidence,
rather than repeating quality or upside. Risk penalty owns residual cyclicality,
concentration, governance, regulatory and evidence uncertainty. Do not charge
financing risk again in risk penalty. Shared facts may inform more than one
explanation, but identify the distinct inference and any remaining overlap.

Scenario probabilities and fair values already reflect the valuation's operating
and financing assumptions. Do not apply these scores as additional valuation
haircuts, subtract risk from another component, or multiply by confidence again.
There is deliberately no aggregate score; downstream consumers must account for
correlation rather than summing the five numbers. Low identified risk requires
positive investigation, not absence of information.

## Valuation reference and formula

`valuation_score` compares the assessment's probability-weighted per-share scenario
fair value F with a verified positive per-share reference price P:

```text
F = sum(case_fair_value * case_probability_pct / 100)
valuation_score = round_half_even(clamp(50 + 100 * (F/P - 1), 0, 100), 1 decimal)
```

Thus F/P of 0.5, 0.75, 1, 1.25 and 1.5 maps to 0, 25, 50, 75 and 100. Values
outside that range are clipped. Use the stored scenario probabilities and
`horizon_months`; this is not an annualized return or an independent appraisal.
Valuation requires `research_status=supported`, valid scenarios and evidence for
both the scenarios and reference quote. Python validates the formula and range.

`valuation_reference_price` is P in the assessment/instrument's native `currency`
per share or GDR, after any explicit quote-unit conversion (for example GBp / 100
to GBP). `valuation_reference_at` identifies the reference price's latest completed
exchange session **as of `assessed_at`**; its UTC date must match that session and
it cannot be after `assessed_at`. Retain the actual quote time when known; if only
the session label is known, `00:00:00Z` is the documented date-only convention, not
a claim about an intraday quotation. The rationale identifies the price source,
session, currency, quote units and share/GDR entitlement. Leave valuation score
and both reference fields empty if any of that evidence is unavailable.

Never join by ticker or issuer, substitute a related listing's quote, or copy a
common-share valuation onto a preferred instrument. Samsung common `SSU.VI`
(`security_567d0d575bbd30aaa91d`) and preferred `SSUN.VI`
(`security_d08d763780400dfbffce`) retain separate rows and EUR per-GDR bases even
though they share an issuer. Quality evidence may be shared only with an explicit
instrument link; valuation and entitlement must be independently reconciled.

This is an assessment-time snapshot. Market refresh never recalculates scores or
changes research dates; new prices can change live opinions without changing this
export. Consumers must check `assessed_at <= now < valid_until`, rubric version and
component presence, and separately decide whether the recorded price basis remains
useful. Expired scores remain historical data, not current scores.

## Migration and missing coverage

The initial metadata migration leaves all five scores and both reference fields
empty. It records rubric 1 with an explicit historical-unscored explanation for
each component. It preserves every pre-existing assessment field, source, identity,
currency, scenario, `assessed_at` and `valid_until`. The pinned legacy migration
also discards old scores lacking this rubric's contemporaneous evidence contract;
it never reverse-engineers them from narrative sentiment or Buy/Hold/Sell labels.
Adding scoring metadata does not mean an assessment was reviewed under this rubric.

Only a new, validated, source-backed `research_security` result can publish numeric
scores. Missing scores alone do not fan out research or reset attempts. Missing
assessment coverage uses the existing priority-75 coverage queue, at most 30 tasks
and one active task per issuer, with the normal three sequential operations and two
attempts. VLTO (`security_1b773169da5023ce4682`) and XYL
(`security_d2be67701e612ee6625d`) remain cataloged, unassessed and queued for coverage;
no synthetic assessment is exported for either. This describes initial rollout,
not a permanent exemption from future research.

# Operating PaperTrader

The supported entry point is `uv run papertrader --help`. Configuration is
research.ini; schema authority is schemas/research_contracts.yaml. No old trading
CLI, operations history, accounting tables, alert inbox or final-buy gate exists.

## Schedule and independent phases

`market.yml` triggers daily at13:00 America/New_York (DST-aware). GitHub may delay
scheduled starts. Scheduled completion triggers `research.yml`, including after
partial market degradation. Manual market previews never trigger live research.
Research and market serialize repository writes; Pages builds independently.

Manual Actions runs default to dry-run. Set dry_run=false for bounded real work.
Research may target entity_type=security or idea and its immutable entity_id; leave
both empty for the queue. The discovery input includes a cadence-limited discovery
attempt within the daily three-operation budget. It never creates dependent tasks.

`pages.yml` accepts an exact40-character commit SHA and publish_pages=true to retry
publication alone. Automatic publication consumes the controller's committed SHA
artifact, including valid partial updates from a degraded phase. It never executes
research. No changed content means no deployment; failure retains the previous site.

## Local commands

```sh
uv run papertrader validate
uv run papertrader context security SECURITY_ID
uv run papertrader enqueue security SECURITY_ID
uv run papertrader enqueue idea IDEA_ID
uv run papertrader market                      # zero-request preview
uv run papertrader market --apply              # bounded real market update
uv run papertrader research                    # zero-model preview
uv run papertrader research --entity-type security --entity-id SECURITY_ID --apply
uv run papertrader research --entity-type idea --entity-id IDEA_ID --apply
uv run papertrader discover                    # zero-call preview
uv run papertrader discover --apply            # weekly cadence enforced
uv run papertrader import-candidates --request /tmp/candidates.json
uv run papertrader publish --apply             # deterministic derived views
```

`--force` on discovery is an explicit manual cadence override, preserving proposal
and request budgets. Candidate imports default to preview; --apply verifies primary
URLs and independent yfinance identity before atomic creation. New entities remain
unresearched; no task is forced immediately. See docs/migration/M5.md for the request.

Real model execution requires the pinned Hermes Python/code paths and an isolated
HERMES_HOME/auth.json supplied outside the checkout. Never export Git, age identity,
Telegram or deployment credentials to the model. Only the existing encrypted OAuth
ciphertext may be committed after an actual refresh. Auth cleanup always runs.

## Health and recovery

Exit0: success/preview;2: degraded market;3: degraded research;4: invalid canonical
input;5: Git/infrastructure failure. GitHub Pages reports its own outcome separately.
data/status.json contains only current/last phase status, counters and useful
success/attempt times, plus weekly discovery cadence. It does not grow a history.

Market retains the last good bar and records ticker-specific stale/unavailable.
Freshness uses exchange sessions, not elapsed weekend hours. A repeated closed
session makes zero provider calls. Weekly reconciliation checks provider corrections;
a split requires a fresh valuation. One ticker failure does not undo others.

Research failures retain prior assessment/page/source records. A compact code names
stage, safe exception class, project code location and known validation field; it
never includes rejected values, prompts, source prose or secrets. Failed tasks retry
within budget/backoff; attempts exhausted leave the queue as needs_attention. An
explicit manual retry can bypass failed backoff but does not reset its attempt count.
Automatic attention skips exhausted entities.

A temporary .cache/research-transaction.json journal restores an interrupted logical
write on the next lock acquisition. It is ignored and removed after success, not a
research history. Do not hand-edit canonical CSVs around a failed transaction.

The post-agent controller validates a phase-specific path allowlist and checks
remote main before a single commit/push. Divergence never rebases or overwrites.
A failed push/conflict leaves a three-day Actions recovery artifact with allowlisted
accepted changed files, deletions and base SHA. Review it against current main or
rerun the affected phase; never blindly extract an untrusted archive.

## Validation, publication and migration

CI runs Ruff, formatting, MyPy, strict current schemas/identity/source/wiki links,
unit/integration tests, TypeScript, Markdown publication checks and Quartz build/link
checks. Agent operations run only their relevant current-result validation, not full
CI or site builds. Analytical ECharts use local pinned assets and remain optional;
retired price/indicator charts and technical-series downloads are absent.

Quartz stages current company/idea research and its linked source closure outside
the repository, excluding retired product pages. Old referenced pages resolve to
the verified backup ref. Current stale research is marked in the company catalog;
only fresh supported opinions with current quotes/evidence enter Top10 lists.

One-time tools remain separate from runtime:

```sh
uv run python -m papertrader.migration_inventory --help
uv run python -m papertrader.research_migration --help
uv run python -m papertrader.migration_queue --help
```

They read a pinned Git revision and default to read-only preview or explicit staging
outside active data. The verified pre-research-only-20261018 tag is the backup, not
another permanent active copy. See root PLAN.md and docs/migration/ for exact SHAs,
run links, blocked-task dispositions, actual-vs-mocked checks and outstanding work.

Published artifacts include their exact committed revision, build timestamp and
independent deployment run link. This is artifact metadata, not an assertion that
a newer failed deployment succeeded. The previous site's metadata remains served
on failure. Every company page also shows derived current rating, entity status
and assessment expiry before historical prose; these annotations do not rewrite
research dates, fair values or citations.

## Watchlist valuation coverage

Every active/watchlist instrument is a research coverage target: a sourced thesis,
valuation method, explicit bear/base/bull per-share fair values and probabilities,
case assumptions, downside, catalysts and invalidation conditions. Coverage counts
instruments independently; another share class's valuation does not cover a missing
instrument. The company queue still permits only one active task per issuer.

Missing, unsupported or incomplete valuations receive priority75, above ordinary
expiry refreshes60 and below severe price movement80/material evidence90/manual100.
A newly completed unsupported review waits until its next eligible refresh rather
than retrying every day. Exhausted entities remain visibly needs_attention.
The30-task queue refills from the canonical watchlist on subsequent market cycles;
entities outside the queue remain coverage targets in the catalog. The homepage
reports baseline completeness separately from freshness, and the company catalog
shows each instrument's bear/base/bull values and coverage gaps. Historical complete
research never becomes a fresh ranking merely by being counted as baseline coverage.

Existing defaults remain3 sequential research operations per daily cycle, including
weekly discovery. No valuation is fabricated to satisfy a coverage target; unavailable
evidence stays explicit and Unrated until sourced scenarios can be supported.

Each model operation receives a new temporary Hermes profile. Only inference auth
and controller-owned configuration are copied in; valid refreshed auth is copied
back for deterministic encryption after the phase. Generated profile memory,
hooks, plugins and logs are discarded between operations. A failed profile guard
can consume an operation attempt without invoking the model; phase operation
counters are budgeted attempts, not measured API calls. Inspect per-entity stage
and observed web usage when distinguishing inference from preflight failures.

The web broker receives a bounded current source-identity index (ID, exact URL,
license only; at most5000 rows/1MB), outside the model's research context. Opened
sources return source_id/source_url/source_license for reuse. Existing legacy
same-URL aliases retain their identities and citations; new duplicate URL IDs and
URL/license changes under existing IDs remain invalid. This lookup makes no
additional network or model request and grants no source-content trust exception.

Research explanations must remain nonempty even for unsupported conclusions: state
what is unknown and why, while leaving unsupported scenario numbers empty. Prefer
primary financial evidence; justified, clearly attributed trustworthy secondary
reporting can fill identified gaps with appropriate confidence/limitations. A
corporate homepage alone is not financial evidence. Broker failures expose safe
static categories and numeric HTTP status, never provider reason/body. Unreadable PDFs are reported explicitly rather than as a generic
network error. Bounded text-PDF extraction is described below. Per-operation request/time/content limits remain unchanged.

First-time research context includes a canonical target_page even when the catalog
has no page yet, explicit missing valuation fields, compact request reasons and
up to12 recently checked relevant source records. Verified manual source leads
remain metadata-only until the research operation reopens and cites them. Prefer
direct issuer releases when a public search endpoint returns irrelevant results;
search snippets and IR navigation links do not establish financial facts.

The HTML reader excludes navigation/header/footer text from the bounded financial
excerpt while exposing up to20 IR/source locator URLs. It executes no page script.
A stale company review records its review time for the7-day cooldown but never
renews assessed_at/valid_until, fair values or cited evidence without an accepted
research result. Coverage counts do not increase for skipped/unchanged reviews.

Reference lists (`source_ids`, `related_entity_ids`) use exact immutable IDs joined
with `|`. URLs, display citation labels, shortened IDs and comma-separated lists
are invalid. Every assessment/idea/relationship source token must match a source
row in the result or current context; a verified lead still needs a complete valid
source update after reopening. An unresolved source reference is a rejected result,
not evidence that a company cannot be valued.

An unassessed company may have `needs_attention` with no research page after its
bounded attempts are exhausted. This records a failed review, never a valuation.
Assessed or researched companies still require their current valid page. Global
candidate validation reports only static page/assessment/integrity categories;
raw rejected results and source text are not published. If Git rejects an invalid
failure state, recover the observed spent attempt through the deterministic queue
controller after repair; do not reset attempts or silently repeat a model call.

The research reader also handles text PDFs with pinned `pypdf==6.21.1`, following
its [security configuration](https://pypdf.readthedocs.io/en/6.21.1/user/security.html).
Use `research_web` open with a one-based `page` integer to read later financial
statements. Each read fetches at most2MB and returns up to3 pages within the same
12k-character excerpt/request ceiling; the file has at most250 pages. Parser
stream/decode/object limits are bounded. Encrypted, malformed, excessively complex
and image-only documents return static errors. There is no OCR, decryption,
embedded-code execution or external renderer. Do not infer that financial evidence
is unavailable just because a document requires a later page.

PDF bytes and extracted text stay inside the isolated operation. The controller
retains bounded excerpts from all seen windows for the existing copying check;
only metadata, citations, verified facts and original synthesis can reach the
current repository. Source hashes bind the fetched document. No model-turn,
external-request or research-operation budget increases with PDF support.

Historical scenario completeness can be repaired only from existing explicit prose:
`uv run python -m papertrader.research_migration --recover-narratives` previews;
add `--apply` after reviewing each proposed excerpt. This manual migration is never
called by the scheduled runtime. It requires expired supported research, exact
security/issuer identity, page date matching the assessment date, and all existing
source references present in the page. It refuses ambiguity and leaves incomplete
records for real research. Only missing downside/catalyst/invalidation fields can
change; it preserves dates, values, probabilities, sources, pages and queue state.
Regenerate deterministic views and validate after applying. Historical completeness
and current valuation freshness remain separate: recovery cannot renew research or
admit expired research into Buy/Sell rankings. Repeat application is a no-op.

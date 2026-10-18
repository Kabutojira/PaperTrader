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

# PaperTrader

PaperTrader is a public, Git-native research system for paper trading. The repository is the
source of truth: research, queued work, market snapshots, simulated accounting records, and the
published wiki all live under `data/`.

PaperTrader never places a real order. The application has no live-order mode, broker adapter, or
brokerage credential path; its order and fill lifecycle is always simulated.

## Local setup

Python 3.12 or newer and [uv](https://docs.astral.sh/uv/) are required.

```bash
cp .env.example .env
set -a
. ./.env
set +a
export WIKI_PATH="$PWD/data/wiki"
uv sync --locked --all-groups
```

The project skills are stored in `skills/`. Hermes should set `skills.external_dirs` to the
checkout's `skills` directory. A local agentic harness can read the same `SKILL.md` files directly
and must follow `AGENTS.md`, use the project CLI for structured state, and run operations
sequentially.

## Run an operation from Codex instead of Hermes

The local harness boundary lets an existing Codex shell execute the repository skills without
starting Hermes or decrypting Hermes OAuth state. It still claims one queue row, records a
content-addressed baseline outside the checkout, audits structured CLI writes, validates the exact
result, and owns the terminal queue transition.

Prepare a daily run and start one already-enqueued operation:

```bash
RUN_ID="local-$(date -u +%Y%m%dT%H%M%SZ)"
OPERATION_ID="<operation ULID>"
BASE_SHA="$(git rev-parse HEAD)"

uv run papertrader daily prepare \
  --run-id "$RUN_ID" \
  --trigger local \
  --source-sha "$BASE_SHA" \
  --offline \
  --skip-classifier

uv run papertrader agent harness start \
  --run-id "$RUN_ID" \
  --operation-id "$OPERATION_ID"
```

The `--offline --skip-classifier` flags make the example reproducible without market or classifier
network access. Omit them when you want the normal daily market retrieval and configured inbox
classification phases.

The start command returns the payload, trusted controller prompt, exact controller/operation skill
paths, result path, and command-audit path. In the Codex shell, read those files completely and
perform exactly one operation. For every agent-side `papertrader` command, set the returned audit
context:

```bash
export PAPERTRADER_AUDIT_RUN_ID="$RUN_ID"
export PAPERTRADER_AUDIT_OPERATION_ID="$OPERATION_ID"
export PAPERTRADER_AUDIT_PATH="data/runs/$RUN_ID/$OPERATION_ID/command_audit.json"
```

Write `data/runs/$RUN_ID/$OPERATION_ID/agent_result.json` last. Then let the deterministic
controller validate and terminalize the operation, and finish the daily phases:

```bash
unset PAPERTRADER_AUDIT_RUN_ID PAPERTRADER_AUDIT_OPERATION_ID PAPERTRADER_AUDIT_PATH

uv run papertrader agent harness finish \
  --run-id "$RUN_ID" \
  --operation-id "$OPERATION_ID"

REPORT_DATE="$(date -u +%Y%m%d)"
uv run papertrader daily finalize \
  --run-id "$RUN_ID" \
  --github-report-url \
  "https://github.com/Kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_${REPORT_DATE}.md"
```

When `daily prepare` exists for the run ID, `harness finish` also records the validated outcome in
that run's sequential agent batch. Omit the daily prepare/finalize commands for a standalone
single-operation debug run. A failed finish writes a validation report, records a repository-local
issue, and applies the bounded retry policy; it never silently marks invalid work complete. Run
artifacts are immutable, so fix the cause and use a new `RUN_ID` for a bounded retry rather than
deleting or overwriting the failed attempt.

## Add an investment idea

Adding an idea means queueing one bounded `idea_research` operation; it does not create an
unresearched wiki stub or skip directly to a strategy. Put the substantial seed in repository JSON:

```bash
mkdir -p data/operations/requests
editor data/operations/requests/idea-grid-flexibility.json
```

```json
{
  "operation_type": "idea_research",
  "entity_type": "idea",
  "entity_id": "idea_grid_flexibility",
  "dedupe_key": "idea_research:idea_grid_flexibility:manual:2026-07",
  "prompt": "Research one grid-flexibility investment idea.",
  "inputs": {
    "idea_id": "idea_grid_flexibility",
    "seed_claim": "Load growth and constrained grids may reward selected flexibility suppliers."
  },
  "source": "manual",
  "priority": 50,
  "freshness_days": 30,
  "depends_on": [],
  "not_before": "now",
  "deadline": "",
  "source_refs": [],
  "max_attempts": 3
}
```

```bash
uv run papertrader queue enqueue \
  --request data/operations/requests/idea-grid-flexibility.json
uv run papertrader queue prepare
uv run papertrader queue validate
```

The enqueue output contains the immutable operation ULID to pass to `agent harness start`.

## Add a security

Security addition is deterministic and identity-only. It does not invent a thesis or valuation:

```bash
mkdir -p data/operations/requests
editor data/operations/requests/security-enphase.json
```

```json
{
  "watchlist_reason": "Candidate beneficiary of solar-plus-storage normalization; research pending.",
  "source": "https://investor.enphase.com/",
  "securities": [
    {
      "company_name": "Enphase Energy, Inc.",
      "instrument_name": "Enphase Energy, Inc. common stock",
      "instrument_type": "equity",
      "ticker": "ENPH",
      "exchange_code": "NMS",
      "venue_mic": "XNAS",
      "provider_symbol": "ENPH",
      "currency": "USD",
      "country": "US",
      "sector": "Technology",
      "industry": "Solar"
    }
  ]
}
```

```bash
uv run papertrader watchlist import \
  --request data/operations/requests/security-enphase.json
```

Use the returned immutable `security_id` in a separately enqueued `security_research` operation.
Ticker text alone is never an identity. A new `watchlist` row is immediately included in
deterministic price monitoring and alerts, while validated research is still required before it can
participate in allocation, strategy, signal, or paper-order decisions.

## Hermes execution

GitHub Actions uses a dedicated Hermes profile and one controller process per operation. The
controller preloads native `llm-wiki`, `papertrader-controller`, and the selected operation skill;
enables only the `web`, `file`, and `terminal` toolsets; and invokes `hermes chat` with `--yolo`.
Delegation, messaging, memory, hooks, MCP servers, worktrees, and background fan-out are disabled.

Use a dedicated `HERMES_HOME`; configuration intentionally refuses to overwrite a normal personal
profile unless `--replace-unmanaged` is explicit. The native `llm-wiki` skill must already exist
under that profile's `skills/` directory. The official container initializes bundled skills there.

```bash
export HERMES_HOME=/tmp/papertrader-hermes
uv run papertrader agent configure --hermes-home "$HERMES_HOME" --replace-unmanaged
hermes skills opt-in --sync
uv run papertrader agent preflight \
  --hermes-home "$HERMES_HOME" \
  --operation-type opportunity_research
uv run papertrader agent run \
  --hermes-home "$HERMES_HOME" \
  --run-id local-20260724-01
```

The subprocess receives repository paths, safe process settings, and the isolated profile's
`auth.json`. Main reasoning remains fixed to `openai-codex`; `AUXILIARY_MODEL` configures only
Web ExtractPage summarization and defaults to `openai-codex:gpt-5.6-terra`. `MAX_OPERATIONS`
controls the per-invocation Hermes turn budget and defaults to 180. An `openrouter:<model>`
auxiliary override forwards only `OPENROUTER_API_KEY`; GitHub, Telegram, deployment, brokerage,
Actions OIDC, age identity, and runtime tokens are never forwarded.

Every agent-side project command creates an operation-scoped receipt in
`data/runs/<run_id>/<operation_id>/command_audit.json`. Post-run validation compares a
content-addressed before/after snapshot with `files_changed`, requires receipts for every structured
change, rejects symlinks/deletions/path escapes and skill-scope violations, verifies newly created
operations/issues, and runs strict integrity, wiki, and portfolio checks before queue completion.

## Deterministic core

The Step 2 core owns every numeric and structured state transition:

- `papertrader market update` retrieves normalized yfinance daily bars and every allowed
  non-base FX pair, applies exchange calendars, and maintains committed 365-day price/FX caches
  plus the durable corporate-action ledger. It discards unfinished sessions before validation;
  a yfinance bar whose open or close falls outside its reported high/low is normalized only by
  widening that envelope to the provider's own OHLC extrema and carries an explicit repair marker.
  Later provider revisions append signed dividend corrections or multiplicative split corrections;
  they never replace an observed action, and any related cash change is a separate correction entry.
- `papertrader indicators update --classify-opportunities` calculates the pinned TA-Lib
  indicators, writes candidate inbox packets, asks the configured cheap classifier for an
  `ingest` or `ignore` decision, and enqueues deduplicated follow-up work.
- `papertrader youtube scan --run-id <id> [--dry-run]` validates the six curated channel
  handle/immutable-ID pairs, scans only eligible regular uploads through the selected Data API or
  anonymous Videos-tab provider, and directly enqueues one bounded transcript review per unseen
  video. `--dry-run` validates configuration and writes its run manifest without network access.
- `papertrader seekingalpha schedule --run-id <id> [--dry-run]` queues at most one expiring,
  search-index-only discovery operation for the UTC day; the command performs no network access.
- `papertrader seekingalpha enqueue-leads --request <json>` validates one discovery artifact and
  queues each selected analysis or news lead at most once by immutable kind and numeric article ID.
- `papertrader queue prepare`, `queue claim`, and the terminal queue commands enforce one live
  lease, dependencies, cooldowns, bounded retries, terminal history, and run budgets.
- Queue preparation deterministically skips strategy and execution requests tied to a superseded
  allocation plan before they can consume an LLM operation.
- `papertrader queue resolve-blocked --request <json>` terminalizes only an adjudicated blocked
  request as `skipped` or `cancelled`, retaining its prior agent-result provenance in history.
- `papertrader signal create`, `order create`, and `fills process` accept repository-local JSON
  request files. Signals and pending orders do not affect accounting; only an eligible
  deterministic paper fill appends executions and cash entries.
- Baseline orders use `order create-baseline`; the deterministic command derives quantity from
  current plan/portfolio/price/FX state and retires superseded ready signals rather than trusting
  model-supplied sizing.
- Baseline allocation `open` and `increase` dispositions both use the `open` signal lifecycle
  action; deterministic order code distinguishes the current plan state and computes only its
  remaining whole-share delta.
- A baseline strategy stores the configured maximum-position percentage as its stable risk ceiling;
  its rounded current target is descriptive and never replaces the exact plan-owned target value.
- `papertrader portfolio reconcile --strict` replays append-only ledgers, verifies cash links and
  exact Decimal arithmetic, and checks the generated portfolio against canonical state.
- `papertrader research source record`, `research security upsert`, `research assessment upsert`,
  `research relationship upsert`, and `research strategy upsert` are the only agent-facing routes
  for their structured research tables. They preserve immutable identities and require linked wiki
  pages to exist before the CSV state changes.
- `papertrader allocation plan --run-id <run-id>` scores fresh comparable assessments against
  cash, applies reserve/deployment/position/sector/theme/diversification limits, and writes current
  generated targets plus immutable allocation history. It never creates a signal, order, or fill.
- `papertrader allocation maintain --run-id <run-id> [--backfill]` enqueues stable assessment and
  canonical idea-relationship refresh work for researched securities. `allocation readiness
  --strict` reports coverage and fails until evidence, assessments, relationships, and backfill
  terminal states are activation-ready.
- `papertrader watchlist import --request <json>` atomically adds identity-only securities with
  deterministic IDs. It leaves research fields empty until a bounded security-research operation
  creates the linked wiki page and evidence-backed summary.

## Curated YouTube research

`data/tables/youtube_channels.csv` is the human-approved subscription list. The daily reusable
runtime calls `.github/actions/scan-youtube` before restoring OAuth. When the optional
`YOUTUBE_DATA_API` secret is nonempty, discovery reads each immutable channel's uploads playlist
and video metadata through the YouTube Data API; otherwise it walks the anonymous `pytubefix`
Videos tab. Both paths scan newest-first to the cursor with a 50-entry bound and write
`data/runs/<run_id>/youtube_scan.json`. Bootstrap queues exactly the newest five regular videos per
channel at priority 60; later discoveries use priority 65. The immutable video ID drives source
identity and dedupe, so active queue rows, terminal history, and registered sources prevent a
second request. A channel error becomes a stable repository issue while other channels and market
monitoring continue; a configured Data API failure never silently falls back. Because the Data API
has no authoritative Shorts flag, its regular-video policy excludes live content and videos of
180 seconds or less. Malformed configuration fails before network access or queue mutation.
An explicit curated backlog extension uses
`papertrader youtube backfill --run-id <id> --channel-id <id> --count <n>`; it queues the next
unseen regular videos older than that channel's cursor at bootstrap priority without advancing the
daily-discovery cursor.

Each operation uses `pytubefix==10.10.1` to try human English captions before auto-generated
English with three anonymous, non-interactive clients. Caption failure ends that operation as
`skipped` with `youtube_transcript_unavailable`; it does not fall back to metadata-only analysis or
stall the remaining sequential batch. Successful reviews inspect every bounded timestamped chunk
and treat speaker claims as leads. Material facts must be corroborated with current primary
sources before any maintained entity conclusion changes. Transcript, media, thumbnails, and full
descriptions are never committed; only a transcript hash, no more than 25 quoted words,
timestamped links, source records, corroborated entity edits, bounded priority-66 idea/security
follow-ups, and the original non-published
`data/runs/<run_id>/<operation_id>/youtube_analysis.md` synthesis may persist. A video by itself can
never change an assessment, strategy, signal, allocation, order, or accounting state.

The maintained [pytubefix package](https://pypi.org/project/pytubefix/) remains pinned for anonymous
discovery fallback and caption extraction instead of the older
[pytube package](https://pypi.org/project/pytube/). The historical
[YouTube Telegram Summaries](https://github.com/Stell0/youtubetelegramsummaries) project is a
behavioral reference only; PaperTrader copies neither its GPL code nor its LangChain dependency.

## Seeking Alpha search-index leads

The daily runtime calls `.github/actions/schedule-seekingalpha` before restoring OAuth. The action
does not scrape or fetch Seeking Alpha: it queues one priority-69 `source_discovery` operation for
the current UTC day. That bounded operation uses only search-provider result metadata associated
with the public Trending Analysis and Trending News URLs, tries at most three searches, examines
at most 12 analysis and 12 news candidates from the prior three days, and dynamically retains zero
through five material leads. Direct access to Seeking Alpha domains and use of subscriber
credentials are disabled in validated configuration.

Only normalized title/URL metadata, the immutable numeric article ID, a hash of the transient
search summary, and an original selection reason enter the queue. Search summaries and article
bodies are never committed. Each retained analysis lead becomes a priority-67 `wiki_ingest`;
entity-linked news uses priority 66. The exact-once key
`wiki_ingest:seekingalpha:<analysis|news>:<article_id>:v1` is checked against active work, every
terminal history state, and registered sources, so retries and later daily runs cannot ingest the
same article twice.

Ingestion treats the indexed lead as a hypothesis, not evidence, and never claims that the article
was read. It verifies material facts and instrument identities independently from current primary
sources. A retained analysis may enqueue one idea review and import at most two independently
verified public-security identities, each with exactly one priority-68 security review. News can
update only already-related ideas or securities and may enqueue at most one bounded refresh. No
lead can directly change a strategy, signal, allocation, order, or accounting state. Original
synthesis is stored only in the operation's non-published `seekingalpha_analysis.md` artifact; a
three-attempt search failure finishes `skipped` with `seekingalpha_search_unavailable`, appears in
daily operations degradation, and does not stall later sequential work.

## Iterative research loop

Idea research maps the complete material value chain, searches beyond the issuers already named in
the seed, imports evidence-backed public instruments as identity-only watchlist rows, links their
tickers from the idea page, and queues one bounded security review per new or stale candidate. A
security review then queues one idea refresh for each payload-linked or accepted-relationship idea.
That refresh replaces stale queued-candidate text with the security's disposition, decision, and
reason and may discover the next bounded set of investable candidates. Operations remain strictly
sequential, and a fresh security result is not reflexively sent back through security research.

### Merged alerts and quick checks

Price alerts for the same immutable security no longer create competing queued security reviews.
Before a review is claimed, each distinct RSI, Bollinger, volume, crossing, or repeat-day cause is
appended to its payload, dependencies and source references are combined, and priority rises by one
up to 100. Exact duplicate dedupe keys remain idempotent. The accepted result therefore evaluates
all accumulated causes in one auditable operation.

When the latest successful full security review is no more than ten days old, a new price alert
queues `quick_check_research` instead. That bounded operation re-verifies the stored thesis,
valuation or buy zone, catalysts, invalidation, risks, and confidence against current prices and
primary evidence. It updates the comparable security state and queues one normal
`security_research` follow-up when a material gate changed or a full review cause was merged into
the quick check.

## Daily podcast

Podcast generation is off by default. Enable it for a manual daily run with the
`generate_podcast` workflow-dispatch toggle, or set the GitHub Actions repository/environment
variable `GENERATE_PODCAST` to `true` for scheduled runs. An enabled non-dry daily workflow
finishes with one priority-100 `daily_podcast` operation after the canonical report and decision
snapshot exist. Deterministic code collects all accepted operation results for that run into
`data/runs/<run_id>/podcast_context.json`; the podcast skill combines related alerts, orders the
material arguments, and writes an original 2,400-3,600 word transcript under
`data/wiki/podcasts/`.

Hermes receives its TTS toolset only for this operation. It synthesizes bounded chunks strictly
sequentially, and `papertrader podcast assemble` validates the transcript length, assembles the
chunks with `ffmpeg`, verifies a 16-24 minute duration, and atomically publishes the dated MP3. The
daily report links the result. Podcast queue and payload state is delivery-only and excluded from
decision source hashes, so this generated view cannot feed back into or invalidate the immutable
investment snapshot.

Do not hand-edit structured runtime CSVs. Use the CLI so identity, schema, atomic-write,
paper-only, risk, and audit contracts are enforced. `executions.csv`, `cash_ledger.csv`,
`corporate_actions.csv`, allocation history, operation history, and run history are append-only.

## Opportunity-cost-aware allocation

Security research now ends with one comparable assessment in
`data/tables/security_assessments.csv`. The operation records its evidence-backed component scores,
confidence, downside/base upside, valuation horizon, soft gaps, and either an eligible disposition
or explicit hard blockers. Agents must write it through a repository request file:

```bash
uv run papertrader research assessment upsert \
  --request data/runs/<run-id>/<operation-id>/assessment-request.json
```

After fills, portfolio rebuild, reconciliation, and performance, the daily controller runs the
allocator. It compares positive risk-adjusted candidate edge with the configured cash hurdle and
requires at least 10% base-case upside and at least 1:1 base-upside-to-downside before opening or
increasing a baseline position. Timing affects ranking but cannot override those payoff gates.
Pending baseline exposure receives no repeated deployment tranche. The fill path cancels an entry
if its assessment, payoff gates, strategy, or allocation plan is no longer current. The allocator
keeps cash whenever candidates or capacity are insufficient. To inspect the same deterministic
plan locally:

```bash
RUN_ID="allocation-$(date -u +%Y%m%dT%H%M%SZ)"
uv run papertrader allocation plan --run-id "$RUN_ID"
```

The versioned `[allocation]` mode is `active`; the operator explicitly waived the original five
live shadow cycles. Use `report_only` for a non-handoff diagnostic run: it writes only generated
`allocation_targets.csv`, append-only `allocation_history.csv`, and its run summary. Active mode
enqueues normal, sequential `strategy_research` work only for material baseline deltas whose
assessment and relationship gates pass. Missing readiness retains cash rather than forcing a
trade. Baseline strategies
are long equity, retain the immutable plan ID, and proceed through the existing signal, order,
fill, and reconciliation boundaries. Deterministic order guards own final share quantity, cash
reserve, cumulative target risk-budget, canonical-leg, and concentration enforcement. A single
instrument position cannot mix baseline and conviction ownership because the generated portfolio
cannot safely attribute an aggregated quantity to two sleeves.

The plan ID is content-addressed from economic inputs only. Re-running or publishing an unchanged
plan keeps that ID stable even though the run timestamp changes; allocation history records each
plan/run/security observation separately. A strategy or signal is therefore superseded only by a
changed economic plan, not by routine daily finalization.

`capital_unallocated_base` is the remaining gap to the configured invested-exposure target after
the current plan, not merely unused one-run deployment budget. The plan artifact and daily report
list the binding reserve, sleeve, deployment, diversification, candidate, and rounding constraints
that intentionally leave it in cash.

FX caches live at `data/market/fx/<currency>_<base_currency>.csv`. A missing or stale rate excludes
a new allocation candidate and defers a pending foreign-currency order; it never substitutes a
rate or mutates accounting. Current targets are generated state and agents must never edit either
allocation table directly.

The configured account size is 10,000 EUR. The original 100,000 EUR capital entry remains in the
append-only ledger; a 90,000 EUR `capital_withdrawal` starts the current performance epoch. Future
capital changes use `papertrader account rebase --request <json>`, append a contribution or
withdrawal, and preserve prior epoch returns as audit history.

## Investor decision publication

The public Quartz homepage is a results-first investment dashboard. One deterministic
projection in `src/papertrader/advice.py` joins the reconciled account, validated pending orders,
signals, allocation candidates, research alerts, performance, coverage, and issues. The projection
does not feed allocation, orders, fills, or accounting back into the system.

```bash
uv run papertrader advice refresh --run-id <completed-run-id>
uv run papertrader advice validate --strict
```

Each refresh writes an immutable `data/runs/<run-id>/decision_snapshot.json` and atomically updates
the latest validated publication files:

- `data/published/decision_snapshot.json`;
- `data/published/model_portfolio.csv`;
- `data/published/actionable_signals.csv`.

The same snapshot generates the Today, Model portfolio, Securities, Signals, Performance, System
status, and Research catalog pages plus the investor-first daily report and Telegram brief. Every
identity-valid security is market-monitored before research; research status gates investment
decisions, not RSI, Bollinger, configured volume-anomaly, SMA 50/200 crossing, or MACD crossing
alerts. A new price-alert transition creates one priority-95 security review for the affected
security, with all due reviews still executed strictly one at a time.
Allocation targets
without a valid strategy remain candidates, indicator transitions remain visibly labelled research
alerts, and only a validated non-terminal paper order can be copy ready. An all-cash conclusion is
published explicitly as `No trade — hold 100% cash`.

The model-portfolio page works without JavaScript and provides committed CSV/JSON downloads.
Progressive enhancement can copy rows as TSV and scale long-equity target weights to a notional in
browser memory. It rounds down to whole shares, reports residual cash and separate market/FX
timestamps, does not persist the portfolio value, and never contacts a broker or server.

## Daily automation and publication

The scheduled controller in `.github/workflows/daily.yml` runs at 17:00 `Europe/Rome` every day and
uses one serialized path for both cron and manual runs. It performs curated YouTube discovery with
an optional purpose-bound Data API key and schedules the search-index-only Seeking Alpha discovery
before OAuth restoration, then prepares market and queue state,
executes at most the configured number of
Hermes operations one at a time, processes eligible paper fills, rebuilds and reconciles
accounting, generates the allocation plan and deterministic decision snapshot, refreshes the
investor pages, writes the canonical daily report, and runs the complete validation gate. Manual
runs expose
`operation_id`, `operation_type`, `max_operations`, `dry_run`, `publish_pages`, and
`send_telegram`; `dry_run` defaults to true and performs no inference, commit, push, deployment,
or delivery. Its YouTube phase uses the same offline dry-run mode and the Seeking Alpha action only
validates and writes its dry-run schedule artifact, so neither source phase makes a network request.

Hermes and the commit boundary are separate jobs. The read-only runtime decrypts the repository's
age-encrypted OpenAI Codex OAuth state into its isolated Hermes home, then exports a hash-bound
binary runtime patch and, only after a token refresh, a separate ciphertext-only artifact. A clean
checkout at the exact base commit verifies and applies the allowed artifacts, repeats the gate,
rebases, validates the rebased diff, and pushes only when a non-empty validated change exists. If
inference fails after a refresh, the commit boundary discards all runtime data and may commit only
the exact encrypted OAuth file. The GitHub write token is introduced only for that final push, and
the write job never receives the OAuth secret or plaintext. The post-commit jobs then:

- build the wiki and its canonical daily reports from an exact commit with Quartz;
- deploy the verified `site/public` artifact when Pages publication is enabled;
- read the exact committed report with `git show` and send its investor brief as bounded Telegram
  Rich Markdown, preserving headings, lists, code, and emphasis; the brief lists every current
  price alert, its research decision and reason, and every research result completed in the run;
- convert security, idea, strategy, and report links to the public GitHub Pages site rather than
  repository blob URLs;
- retain one stable latest-only Telegram delivery issue without rolling back the runtime commit;
  when a newer report exists, older missed reports are not replayed.

Repository setup requires `OPENAI_OAUTH_SECRET` and the matching
`.papertrader/credentials/openai-oauth-auth.json.age`. Optional repository variables
`MAX_OPERATIONS` and `AUXILIARY_MODEL` override the 180-turn and
`openai-codex:gpt-5.6-terra` defaults. `OPENROUTER_API_KEY` is required only for an OpenRouter
auxiliary override, and `YOUTUBE_DATA_API` optionally enables keyed discovery; each secret is
exposed only to its purpose-bound step and never to terminal tools. Delivery additionally requires
`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Configure GitHub Pages to use **GitHub Actions** as its
source, and enable repository secret scanning. See the operating runbook for OAuth seeding,
verification, rotation, and revoked-grant recovery. A deployment can be retried independently by
manually dispatching `pages.yml` with the committed SHA. Telegram can be retried by dispatching
`reporting.yml` with the same `commit_sha`, `report_path`, and `run_id`.
For a committed local run, use `papertrader telegram deliver-run --commit-sha <sha> --run-id
<run-id> --repository-url https://github.com/Kabutojira/PaperTrader`.

The `[classifier]` command is the repository bridge to a tool-free, one-shot Hermes turn using the
isolated OpenAI Codex OAuth profile. It defaults to the cost-sensitive `gpt-5.6-luna` model, emits
only the closed `ingest|ignore` JSON contract, and retries previously pending or blocked packets on
the next non-dry daily run. Deterministic code never substitutes a heuristic ingestion decision.

See the [operating runbook](docs/OPERATIONS.md) for queue examples, local skill execution, manual
workflow dispatch, configuration changes, failed-run recovery, replay by run ID, publication
retry, and project-skill maintenance.

## Development architecture

PaperTrader separates deterministic state ownership from agent judgment. The repository is the
database, every durable mutation is reviewable in Git, and no component has a real-order adapter.

```text
request JSON -> validated queue -> one claimed operation -> Hermes or local Codex harness
             -> completed edits + agent_result.json -> deterministic result validator
             -> terminal history -> fills/accounting -> allocation plan -> decision snapshot
             -> investor pages/report -> write-controlled Git boundary
```

| Layer | Owns | Main implementation |
| --- | --- | --- |
| Contracts and policy | CSV/JSON schemas, IDs, limits, paths, paper-only settings | `AGENTS.md`, `schemas/`, `config.ini`, `src/papertrader/config.py` |
| Deterministic state | Queue, market/FX data, allocation, orders, fills, ledgers, portfolio, advice projection, reports | `src/papertrader/*.py` through the `papertrader` CLI |
| Agent judgment | Research synthesis, causal theses, bounded follow-ups, strategy decisions | `skills/papertrader-*/SKILL.md` plus native `llm-wiki` in Hermes |
| Agent boundary | One-operation claim, prompt construction, CLI receipts, exact delta/result validation | `agent_runner.py`, `local_harness.py`, `command_audit.py`, `result_validator.py` |
| Persistence | Canonical research/runtime state and immutable history | `data/` |
| Automation | Read-only inference, validated artifact handoff, sole write-enabled commit job | `.github/workflows/reusable-llm.yml` |
| Publication | Decision snapshot/exports, investor pages, canonical report, Quartz Pages, post-commit Telegram brief | `advice.py`, `investor_pages.py`, `reports.py`, `site/`, `reporting.yml`, `pages.yml` |

Structured CSVs must never be hand-edited by an agent. Wiki Markdown is the agent's direct write
surface within the selected skill scope; request-bearing CLI commands are the only route to
structured state. `agent_result.json` describes changes already made and is written last. The
validator compares it with a pre-run content snapshot, command receipts, queue/issue identities,
the runtime whitelist, strict wiki lint, integrity, and accounting reconciliation before the queue
can advance.

## Validation

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run papertrader integrity --strict
uv run papertrader advice validate --strict
uv run papertrader wiki lint --strict
uv run papertrader portfolio reconcile --strict
cd site && npm run check && PAPERTRADER_BASE_URL=localhost npm run build
```

Validate paths staged for an automated runtime commit with:

```bash
uv run papertrader runtime-whitelist validate --staged
```

Development changes may touch source, tests, schemas, skills, workflows, and site configuration.
Automated runtime commits are intentionally restricted to the data paths documented in
`AGENTS.md`.

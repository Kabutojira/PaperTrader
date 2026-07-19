# AGENTS.md

## Mission

Build and operate PaperTrader as a traceable, deterministic, safety-first paper-trading system. Google Sheets is the central operational registry; Hermes supplies qualitative analysis and orchestration, not unchecked financial authority.

## Instruction precedence

1. Explicit user instructions that do not weaken safety controls.
2. This file and the active `Skills/papertrader/SKILL.md` contract.
3. Deterministic risk, broker, market-data, and reconciliation outputs.
4. Model-generated analysis.

When a model conclusion conflicts with verified market data, broker state, spreadsheet state, or a risk rule, the deterministic source wins.

## Default state

- Operate in `PAPER` mode.
- Keep the global kill switch active until readiness checks pass.
- Require human approval while the system is being built and commissioned.
- Treat every `[DA DEFINIRE]` value as unresolved and blocking when it affects order submission or risk.
- Use `Europe/Rome` for the trading-day boundary unless configuration explicitly changes it.

## Required workflow

For every proposed trade or position change:

1. Read current configuration and confirm mode.
2. Reconcile broker account, positions, and open orders.
3. Fetch a fresh quote and verified instrument metadata.
4. Read the active thesis, current position, and same-day order history.
5. Produce or ingest a JSON signal that conforms to the repository schema.
6. Validate the JSON deterministically.
7. Recompute `InstrumentKey`; never trust the model-provided key without checking it.
8. Acquire a per-date/per-instrument transactional lock.
9. Recount distinct broker-bound `OrderID` values for that instrument and date.
10. Reject the order when the count is already 2.
11. Recalculate quantity, risk, exposure, cash, and margin deterministically.
12. Check stale data, duplicates, daily loss, kill switch, session, spread, liquidity, and order coherence.
13. Create stable `OrderID`, `CorrelationID`, and `IdempotencyKey` values.
14. Submit only after all gates pass.
15. Record the broker response immediately.
16. Reconcile every fill and update positions/P&L from the execution ledger.

Never rely on a visible spreadsheet formula alone as the final concurrency control. The pre-submit recount and reservation must occur atomically in the integration layer.

## Authority matrix

Hermes may author:

- thesis summaries and versioned thesis updates;
- qualitative catalysts and risks;
- trigger and invalidation proposals;
- proposed action, side, order type, stop, target, and validity time;
- concise trade rationale;
- structured JSON conforming to the signal schema.

Hermes must not be authoritative for:

- quantity or number of option contracts;
- current price, option multiplier, contract identity, or market session;
- risk budget, cash, margin, exposure, or daily-loss calculations;
- realized or unrealized P&L;
- the daily operation count;
- final order authorization;
- order, fill, cancellation, rejection, exercise, or assignment state;
- kill-switch reset.

## Trading constraints

- Maximum 2 broker-bound operations per exact `InstrumentKey` per `Europe/Rome` date.
- Partial fills and state updates under the same `OrderID` do not consume extra slots.
- A cancel/replace that creates a new broker order consumes another slot.
- A locally rejected order that never reached the broker does not consume a slot.
- An unknown broker submission state consumes a slot until reconciled and activates the kill switch.
- Broker-rejected orders count when configured to do so; default is conservative counting.
- Costs, fees, slippage, and multipliers are mandatory in P&L and risk.
- Naked short options are disabled by default.
- A stop is not a guaranteed execution price.

## Repository conventions

- `Skills/<skill-name>/SKILL.md` is the Hermes entrypoint.
- Put detailed operating knowledge in `references/`.
- Put schemas and example payloads in `templates/`.
- Put deterministic helpers required by a skill in that skill's `scripts/` directory.
- Root `scripts/` contains repository installation and validation tooling.
- Keep scripts dependency-light; prefer the Python standard library for validators.
- Do not duplicate risk logic in prose, formulas, and code without identifying the code path that is authoritative.
- Version schemas and prompts. Persist hashes of accepted model outputs.

## Change rules

Before modifying a safety-critical file:

1. Inspect the current file and its consumers.
2. State which invariant is changing.
3. Add or update a deterministic validation case.
4. Run `./scripts/check.sh`.
5. Explain migration impact for existing Sheets data or order records.

Safety-critical files include:

- `AGENTS.md`
- `Skills/papertrader/SKILL.md`
- signal schemas and validators
- broker/order-state code
- position/P&L code
- risk limits and kill-switch logic

## Secrets and sensitive data

- Never commit credentials, tokens, cookies, service-account JSON, private keys, account numbers, or raw broker payloads containing secrets.
- Never print secrets in logs, prompts, issues, or pull requests.
- Store only hashes or external references when a raw payload is sensitive.
- Use least-privilege identities and separate paper/live credentials.

## Error policy

Fail closed for new exposure when any of these occur:

- missing or stale market data;
- invalid JSON;
- duplicate identifiers;
- unknown broker order state;
- broker/Sheet position mismatch;
- unavailable cash or margin preview;
- incomplete risk configuration;
- heartbeat timeout;
- repeated integration errors;
- formula or schema validation failure.

Risk-reducing `CLOSE` or `REDUCE` actions may proceed only through a specifically tested deterministic path. Do not improvise emergency liquidation behavior.

## Definition of done

A task affecting trading behavior is complete only when:

- deterministic checks pass;
- relevant failure cases are tested;
- audit fields are preserved;
- no secret was added;
- documentation and schema versions agree;
- paper-mode behavior is verified;
- unresolved assumptions are marked `[DA DEFINIRE]`;
- the change does not imply guaranteed profitability.

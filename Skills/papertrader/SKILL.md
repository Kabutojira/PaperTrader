---
name: papertrader
description: Operate PaperTrader with deterministic risk controls
version: 0.1.0
author: Kabutojira
metadata:
  hermes:
    tags: [paper-trading, google-sheets, risk, options]
    category: finance
    requires_toolsets: [terminal]
    config:
      - key: papertrader.sheet_id
        description: Google Sheets spreadsheet ID used as the registry
        default: "[DA DEFINIRE]"
        prompt: PaperTrader Google Sheets spreadsheet ID
      - key: papertrader.mode
        description: Trading mode; remain in PAPER until acceptance gates pass
        default: "PAPER"
        prompt: PaperTrader mode (PAPER or LIVE)
      - key: papertrader.timezone
        description: Time zone used for trading-day boundaries
        default: "Europe/Rome"
        prompt: Operational time zone
      - key: papertrader.broker
        description: Broker or broker adapter identifier
        default: "[DA DEFINIRE]"
        prompt: Paper-trading broker or adapter
      - key: papertrader.market_data_source
        description: Authoritative market and options data source
        default: "[DA DEFINIRE]"
        prompt: Market-data and options-data source
---
# PaperTrader Skill

Use this skill to inspect and orchestrate the PaperTrader Google Sheets registry, update qualitative theses, validate model-produced signals, and coordinate deterministic risk and order workflows. It does not make profits predictable, calculate final position size through language-model judgment, or authorize broker orders by itself.

## When to Use

Load this skill when the user asks to:

- review the PaperTrader system or Dashboard;
- analyze instruments in the Watchlist;
- create or update a thesis;
- propose a structured paper trade;
- diagnose a blocked signal or risk check;
- reconcile positions, orders, fills, or P&L;
- inspect the two-operations-per-day constraint;
- test broker, market-data, Google Sheets, or kill-switch behavior.

Do not use it as a claim that a security is suitable, safe, or guaranteed to be profitable.

## Prerequisites

Before performing an operational workflow, verify:

1. `papertrader.mode` is `PAPER`, unless a separately approved live release exists.
2. The target spreadsheet ID is configured and accessible.
3. The spreadsheet time zone is `Europe/Rome`, unless explicitly changed.
4. Broker/API and market-data sources are configured; unresolved `[DA DEFINIRE]` values block broker-bound actions.
5. The global kill switch state is known.
6. Current broker account, open-order, and position data can be reconciled.
7. A fresh quote and authoritative instrument metadata are available.
8. The deterministic validator is available at `scripts/validate_signal.py`.

Read these references as needed:

- `references/google-sheets-contract.md`
- `references/operating-rules.md`
- `templates/signal.schema.json`

## How to Run

Typical invocation:

```text
/papertrader review system readiness
```

Validate a model-produced signal locally:

```bash
python3 scripts/validate_signal.py /path/to/signal.json
```

Optionally enforce a maximum data age:

```bash
python3 scripts/validate_signal.py /path/to/signal.json --max-age-minutes 5
```

The validator checks structure and semantic coherence. It is not the complete risk engine and does not authorize submission.

## Quick Reference

| Need | Authoritative source |
|---|---|
| Current price and option contract | Market-data adapter/broker |
| Account equity, cash, margin | Broker account snapshot |
| Thesis and model rationale | Versioned `Tesi` / `Segnali` rows |
| Quantity and contracts | Deterministic risk engine |
| Operation count | Distinct broker-bound `OrderID` ledger entries |
| Order/fill state | Broker plus reconciliation ledger |
| Realized P&L | Sequential fill/position engine |
| Unrealized P&L | Position engine using verified mark |
| Final authorization | Atomic deterministic pre-submit gate |
| Kill-switch reset | Audited operator procedure |

Exact instrument keys:

```text
AZIONE|AAPL
OPZIONE|AAPL|CALL|220|2026-09-18|100
```

## Procedure

### 1. Establish system state

Read `Configurazione` and determine:

- mode;
- kill-switch state and mode;
- configuration completeness;
- broker and market-data health;
- heartbeat age;
- session status;
- equity, cash, margin, and daily P&L;
- risk limits and unresolved placeholders.

If a required value is missing or non-numeric, report it and stop new-exposure processing.

### 2. Reconcile before analysis that could lead to an order

Compare the broker with the Sheet for:

- positions and signed quantities;
- average prices;
- open orders;
- fills and commissions;
- cash, equity, and margin;
- option contract identities;
- protective orders.

A mismatch blocks new exposure and should create an `Eventi_Errori` record.

### 3. Acquire fresh market data

Verify:

- instrument identity and `InstrumentKey`;
- timestamp and source;
- bid, ask, last, and selected mark;
- session;
- spread;
- volume;
- for options: underlying, call/put, strike, expiration, multiplier, open interest, IV, and available Greeks.

Never fill missing facts by guessing. Mark missing fields and fail closed.

### 4. Perform qualitative analysis

Hermes may produce:

- a concise base, bull, and bear case;
- catalysts and risks;
- a thesis summary;
- trigger and invalidation;
- proposed action, side, order type, stop, target, validity, and confidence.

Confidence is informational only. Use `NO_TRADE` when evidence is insufficient, contradictory, or stale.

### 5. Generate and validate JSON

Conform exactly to `templates/signal.schema.json`. Do not add quantity, contracts, risk budget, margin, authorization, or send-order fields.

Run the deterministic validator. Then independently:

- recompute the instrument key;
- verify option metadata;
- compare the model reference price with a fresh quote;
- confirm the signal has not expired;
- hash the canonical JSON;
- reject duplicate `SignalID` or output hash values.

### 6. Run the deterministic risk gate

For exposure-increasing actions, verify all of the following outside the model:

- fresh and complete data;
- global kill switch is off;
- paper/live mode is allowed;
- daily loss capacity remains;
- risk-per-trade budget remains;
- quantity is positive and integral where required;
- projected instrument, underlying, and global exposure are within limits;
- option premium/risk and liquidity are within limits;
- cash and broker margin preview are sufficient;
- stop/target/order relationships are coherent;
- market session and order type are permitted;
- maximum open positions and global daily orders are not exceeded.

For long options, treat the entire premium plus costs as potentially at risk. For short options, require a deterministic bounded-risk model; naked short options remain disabled.

### 7. Enforce the two-operation rule atomically

Under a lock scoped to local date and exact `InstrumentKey`:

1. reconcile broker orders;
2. recompute the local trading date in `Europe/Rome`;
3. count distinct broker-bound `OrderID` values where `ContaNelLimite=TRUE`;
4. reject when the count is already 2;
5. reserve/create the order intent with a stable idempotency key;
6. submit once;
7. record accepted, rejected, or unknown state immediately.

A spreadsheet formula is a monitoring aid, not the concurrency lock.

### 8. Submit and reconcile

Only the deterministic integration layer submits. Distinguish:

- `INVIATO`
- `PARZIALMENTE_ESEGUITO`
- `ESEGUITO`
- `ANNULLATO`
- `RIFIUTATO`
- `STATO_SCONOSCIUTO`

A timeout with uncertain submission state is counted conservatively and activates the kill switch until reconciliation.

### 9. Update the registry

For each broker event:

- append an immutable order event or fill;
- deduplicate by event/execution ID;
- update position quantity and average price sequentially;
- allocate commissions and fees;
- calculate realized P&L only on closing quantity;
- calculate unrealized P&L with signed quantity and multiplier;
- update signal and position states;
- update Dashboard and daily snapshot inputs;
- append errors rather than hiding them.

### 10. Report to the user

State:

- data timestamp and source;
- mode and kill-switch state;
- whether the request was analysis-only or broker-bound;
- deterministic risk result;
- operation count before submission;
- any unresolved `[DA DEFINIRE]` values;
- order and reconciliation identifiers when applicable;
- explicit uncertainty and option-specific risk.

## Pitfalls

- Counting partial fills as separate daily operations.
- Treating an empty `FILTER` result as one unique order.
- Trusting a model-provided option multiplier or price.
- Using an option stop as a guaranteed maximum loss.
- Double-counting slippage after it is already reflected in the fill price.
- Updating the current position without preserving the immutable fill ledger.
- Retrying a timed-out order with a new idempotency key.
- Allowing intraday profits to increase the daily loss budget automatically.
- Resetting the kill switch before order and position reconciliation.
- Storing credentials or sensitive broker payloads in the Sheet or repository.

## Verification

A workflow passes only when:

1. the JSON validator returns `VALID`;
2. the market-data timestamp is within the configured age limit;
3. instrument metadata matches the broker/provider;
4. broker positions and orders reconcile;
5. the atomic operation count is below 2 before submission;
6. all risk and funding checks pass;
7. the broker result is recorded with stable IDs;
8. fills, commissions, multiplier, and P&L reconcile;
9. no secret appears in logs or artifacts;
10. the system remains in paper mode unless a separately documented live gate has passed.

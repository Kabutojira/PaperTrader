# Google Sheets contract

The spreadsheet is the central operational registry and human-readable audit surface. It is not the sole concurrency primitive for order submission.

## Required tabs

### `Configurazione`

Stores static limits and runtime health. Required settings include:

- broker and market-data source;
- mode and time zone;
- global kill switch and mode;
- maximum 2 operations per instrument/day;
- maximum risk per trade;
- maximum daily loss;
- instrument, underlying, and gross exposure limits;
- slippage and commission assumptions;
- option DTE, spread, and open-interest limits;
- account equity, cash, margin, P&L, heartbeat, and connection state.

Any safety-critical `[DA DEFINIRE]` value blocks new exposure.

### `Dati_Mercato`

One current row per exact instrument. It includes:

- normalized `InstrumentKey`;
- UTC and local timestamps;
- ticker, type, underlying, call/put, strike, expiration, multiplier;
- bid, ask, last, mid, selected price;
- volume, open interest, IV, and Greeks when available;
- source, session, quality, duplicate, missing, age, and stale flags.

### `Watchlist`

Contains monitored instruments, priority, state, active thesis, trigger, invalidation, proposed levels, current quote fields, liquidity fields, and eligibility flags.

### `Tesi`

Append-only version history. Key fields:

- timestamp, `TesiID`, version, `InstrumentKey`, state;
- horizon, summary, catalysts, risks, trigger, invalidation;
- indicative stop/target and confidence;
- data cut-off, model, prompt version, JSON hash;
- approval identity and timestamp.

### `Portafoglio`

Current position state. Every position must track:

- `PositionID`, ticker, type, `InstrumentKey`, underlying;
- signed quantity, direction, average price, current price;
- market value and risk exposure;
- realized and unrealized P&L;
- commissions, fees, and slippage diagnostics;
- thesis, trigger, invalidation, stop, target;
- opening date, last update, status, residual risk, and flags.

Options additionally require call/put, strike, expiration, premium, multiplier, and contract count.

### `Segnali`

Stores model proposals and deterministic risk results. Model-owned qualitative fields and deterministic fields must remain distinguishable.

Required audit fields include:

- `SignalID`, `TesiID`, instrument metadata;
- action, side, order type, reference price, stop, target, validity;
- rationale, risks, confidence;
- calculated quantity, risk budget, unit/total risk, post-trade exposure;
- same-day operation count;
- missing, stale, duplicate, coherence, exposure, funding, daily-loss, and eligibility flags;
- aggregate risk result, signal state, human approval, final authorization snapshot;
- order ID, error code, model, prompt version, and JSON hash.

### `Operazioni`

Append-only order and fill ledger. Every row tracks:

- UTC/local timestamp and immutable `EventID`;
- record type, internal/broker order IDs, execution ID;
- signal, thesis, position, and correlation identifiers;
- exact instrument metadata;
- side, position effect, order type, time-in-force;
- requested/executed quantity, order/fill/reference prices;
- commissions, other fees, slippage diagnostic, and net cash flow;
- pre/post position state and realized net P&L;
- stop, target, rationale, state, outcome, and errors;
- broker-submission flag, daily-limit flag, idempotency key, source, and payload hash;
- duplicate, missing, and incoherence flags.

### `Storico Giornaliero`

Append-only end-of-day snapshots containing equity, external cash flows, realized/unrealized P&L, costs, exposure, position/order counts, drawdown, kill-switch events, timestamp, and snapshot hash.

### `Dashboard`

Derived monitoring only. It must not be an input authority for order submission.

### `Eventi_Errori`

Append-only normalized errors with correlation IDs, severity, component, retryability, attempts, related order/signal/instrument IDs, action taken, resolution, and kill-switch status.

## Instrument keys

```text
Stock:  AZIONE|<TICKER>
Option: OPZIONE|<UNDERLYING>|<CALL_OR_PUT>|<STRIKE>|<YYYY-MM-DD>|<MULTIPLIER>
```

Normalize symbols and call/put to uppercase. Use a stable decimal representation for strike.

## Operation-count contract

Count distinct broker-bound `OrderID` values for the exact `InstrumentKey` and local trading date where `ContaNelLimite=TRUE`.

Count:

- submitted/accepted orders;
- partial or fully executed orders;
- cancelled orders that were submitted;
- unknown submission states;
- broker rejections when conservative counting is enabled.

Do not count:

- local risk rejections before broker submission;
- repeated status events for one order;
- multiple fills under one order;
- duplicate webhooks.

A cancel/replace with a new broker order and new `OrderID` consumes another slot.

## State enumerations

Signal states:

```text
PROPOSTO
VALIDATO
BLOCCATO_RISCHIO
INVIATO
ESEGUITO
SCADUTO
ANNULLATO
```

Order states:

```text
BOZZA
VALIDATO
INVIATO
PARZIALMENTE_ESEGUITO
ESEGUITO
ANNULLATO
RIFIUTATO
STATO_SCONOSCIUTO
```

Position states:

```text
APERTA
RIDOTTA
CHIUSA
SOSPESA
```

## Data authority

| Data | Authority |
|---|---|
| Thesis/rationale | Approved model output and versioned Sheet record |
| Quote and contract metadata | Market-data provider/broker |
| Quantity and risk | Deterministic risk engine |
| Cash/equity/margin | Broker |
| Order and fill state | Broker plus reconciliation |
| Position and P&L | Sequential fill/position engine |
| Operation count | Immutable order ledger under lock |
| Final authorization | Deterministic pre-submit transaction |

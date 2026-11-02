# Manual company research with subagents

This is an explicitly launched, company-only alternative to the Hermes executor.
It does not use Hermes OAuth, change Actions, schedule work, discover companies,
commit/push, or deploy Pages. The existing Python controller still claims exactly
one immutable security, preserves retry counters, owns current source observations,
validates the completed result, atomically applies it, and regenerates health/views.
Preview is the default. Preparing this integration does not authorize a live review.

## Required subagent isolation

The research subagent must have **no executable tools**, shell, filesystem access,
network, MCP connectors, credentials, or child-agent delegation. Give it only the
returned context and broker responses as conversation messages. It returns JSON
messages to its coordinator. The coordinator alone calls the controller and performs
development/publication operations after the researcher exits.

The current shared-tools `spawn_agent` interface does not expose a per-agent tool
allowlist. A prompt telling such an agent not to use tools is not isolation. Use
this integration only with a runtime that demonstrably enforces a tool-less worker.
If unavailable, stop before `--apply` or spawning a researcher and report
`BLOCKED_RESEARCH_ISOLATION`. Do not replace that check with a self-attestation flag.
This transport deliberately does not claim to provision a sandbox itself.

## Controller protocol

Run commands on a POSIX host from a clean checkout with installed locked dependencies.
First preview:

```sh
uv run papertrader research-manual --entity-id SECURITY_ID
```

After checking isolation and explicit authorization for a real review, start the
controller in a supervised process, with its output captured. Supply the actual
subagent model identifier, not an inferred alias:

```sh
uv run papertrader research-manual --entity-id SECURITY_ID --model EXACT_MODEL --apply
```

It prints `{"status":"awaiting_subagent","socket":"/tmp/pt-manual-.../controller.sock"}`.
The private socket is a coordinator capability: never give its path or access to
the researcher. Keep the controller alive while relaying the following JSON files:

```sh
uv run papertrader research-manual-call --socket SOCKET_PATH --request /tmp/request.json
```

| Coordinator request | Meaning |
| --- | --- |
| `{"action":"context"}` | Obtain sanitized context, complete policy, skill, contracts and limits. Pass only `context` to a fresh tool-less subagent. |
| `{"action":"web","request":{"action":"open","url":"https://issuer.example/results","page":1}}` | Execute the researcher's source request using the existing broker. Return only `web` to the subagent as untrusted evidence. |
| `{"action":"web","request":{"action":"search","query":"issuer results"}}` | Broker search; consumes the same source budget. |
| `{"action":"result","result":{...}}` | Submit the complete result object from the researcher. The controller, not the model, supplies observations and usage. |
| `{"action":"abort"}` | Stop the operation; its spent attempt follows normal failure handling. |

Each researcher reply must be exactly one `web` or `result` envelope. Relay one
reply per model turn; do not combine calls, conceal intermediate turns or start
another researcher. The default controller permits at most24 relay turns,12 broker
requests and600 seconds per operation; context delivery is not a research turn.
The external runtime must also enforce the model's turn/runtime limits and disable
automatic retries. Controller expiry does not independently interrupt a remote
model: the coordinator must stop it on expiry, abort or completion. Invalid relay
requests consume budget. Source failures remain explicit; do not use another
browser/tool to bypass the broker or fabricate observation metadata.

`received_pending_validation` acknowledges transport receipt only. Wait for the
controller's final JSON and process exit. Only exit0 plus a successful entity
outcome establishes accepted research. Exit3 records a degraded/failed attempt,
retains accepted research and follows normal two-attempt exhaustion behavior.
Do not reset counters or hand-edit canonical data. Unsupported evidence remains
Unrated with empty scenarios. Never substitute an error-free transport receipt
for actual schema/citation/Markdown acceptance.

The socket and evidence memory are discarded when the operation ends. Keep relay
files outside Git, remove them when finished, and retain lawful original synthesis
and current citations only. Use the normal deterministic commit/push/CI and exact-SHA
Pages process after accepted research; a manual review does not publish itself.

## Launch prompt

Copy [the launch prompt](prompts/manual-company-research.md) into a session with the
required enforced subagent isolation. It targets FCEL, C3.ai and Virgin Galactic
sequentially, with discovery disabled and at most the configured three operations.

## Verification boundary

Automated tests use synthetic company results and mocked source reads. They do not
establish live model access, a tool-less runtime, real company research or deployment.
Local verification passed9 manual integration tests and320 full-suite tests, Ruff,
formatting, MyPy21 modules and strict current validation. Exact-SHA locked CI is a
separate gate; these local checks used the available development environment.

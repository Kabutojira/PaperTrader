# Manual company research

## Dedicated isolated runner

`research-isolated` is the explicitly authorized alternative when the host cannot
audit or enforce an external subagent's capabilities and limits. It loads the
repository `company_researcher` instructions and sanitized company context, but
does not spawn a Codex subagent or load its inherited tools. The remote model can
request only the `research_web` function or return a result envelope. Trusted
Python dispatches that exact function to the existing `ResearchWeb` broker; there
is no shell, interpreter, filesystem, MCP/app discovery or delegation dispatcher.
The existing queue/controller validates and atomically applies the completed
result. Scheduled Hermes and Actions behavior is unchanged.

From a clean checkout with locked dependencies installed:

```sh
uv run papertrader research-isolated --entity-id SECURITY_ID
uv run papertrader research-isolated --entity-id SECURITY_ID --preflight
uv run papertrader research-isolated --entity-id SECURITY_ID --model EXACT_MODEL --apply
```

Preview does not read credentials, call a provider or write canonical state.
`--preflight` reads the existing private Codex ChatGPT OAuth cache outside this
repository and performs one bounded model-catalog read, without inference or a
queue claim. It prints the actual function schema supplied to inference, exact
selected catalog model, zero automatic retries and configured limits. The catalog
is not proof of inference entitlement. Every completed inference response must
report that same model; mismatch, incomplete streams, unknown tools and malformed
results fail closed. `--apply` repeats preflight before admitting/claiming a task
and explicitly skips instruments already marked `needs_attention`.

The trusted HTTP transport uses the documented
[Codex inference endpoint](https://learn.chatgpt.com/docs/enterprise/connect-to-a-gateway)
and [Responses function calling](https://developers.openai.com/api/docs/guides/function-calling).
It reads `CODEX_HOME/auth.json` (default `~/.codex/auth.json`) only in trusted code,
requires private file permissions, and never copies, prints, refreshes or writes
tokens. Tokens and account headers are absent from model input. Missing/rejected
auth stops preflight; renew the normal Codex login outside this command if needed.
There is no credential or provider fallback, environment proxy, HTTP redirect,
SDK retry or model switch.

One CLI process owns one fresh company conversation and exits after validation.
Its POSIX signal deadline interrupts blocking inference and broker reads; the
response stream closes on exit. No local researcher process survives it. Each
inference submission consumes one of `research.max_turns`, and broker calls plus
final submission share the same relay-turn cap. All source reads share
`research.max_web_calls`; failed/repeated reads retain the broker's accounting.
Input and streamed output sizes are bounded. `inference_requests` counts this
runner's HTTP submission attempts, not provider generations or billable calls;
disconnecting a stream does not prove when remote computation stopped.

Use at most `research.max_daily_operations` company attempts across the authorized
batch, one invocation at a time. Preserve counters, skip exhausted entities and
never retry a failed company in the same batch. Wait for the final CLI outcome
and exit code, not merely `response.completed`: Python still has to validate
citations, schemas and Markdown. The existing commit/push/CI and independent
exact-SHA Pages procedure follows accepted research. A catalog read, runtime audit
or mocked test is not completed live research.

## External subagent transport

This is an explicitly launched, company-only alternative to the Hermes executor.
It does not use Hermes OAuth, change Actions, schedule work, discover companies,
commit/push, or deploy Pages. The existing Python controller still claims exactly
one immutable security, preserves retry counters, owns current source observations,
validates the completed result, atomically applies it, and regenerates health/views.
Preview is the default. Preparing this integration does not authorize a live review.

## Repository researcher and allowed tools

[company_researcher](../.codex/agents/company_researcher.toml) is a project-scoped
research role. Its permitted executable tool is **research_web**, with `search`
and `open` actions for public pages and PDFs. The tool uses the existing broker's
request, time, response-size, source-identity and citation-observation checks.
The role disables supported shell, app, plugin, memory and permission-request
features. It inherits the verified parent model rather than hardcoding one.

The researcher must not receive shell/filesystem tools, repository writes,
credentials, native web/browser tools that bypass the broker, unrelated MCP tools
or child-agent delegation. Give it only the controller's sanitized context. It
uses research_web for evidence and returns final JSON to the coordinator, who
alone submits results and performs post-research development/publication work.

Custom-agent files can disable supported features, but cannot override parent
permissions or MCP connections. Do not add an ineffective sandbox_mode or an
invented tools allowlist to the role. Configure the parent appropriately and audit
the runtime's **effective tool inventory** before a real claim. A read-only tool
annotation or an agent's promise is not access control. If the role cannot be
loaded or the broker is not its only executable capability, stop before `--apply`
or researcher spawn and report `BLOCKED_RESEARCH_ISOLATION`.

These boundaries follow [official Codex agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).
A runtime/configuration reload is required to discover a new repository role.
The checkout must also be trusted for Codex to load its `.codex` layer. The CLI's
`codex mcp get/list` commands inspect the user-managed registry and are not a
project-layer audit. Use the reloaded runtime's effective configuration/tool list.

## Read-only broker MCP bridge

The repository's `.codex/config.toml` registers `papertrader_research`, exposing
only research_web via `uv run --locked papertrader research-manual-tools`. Start
Codex from the repository root with locked dependencies installed. The stdio MCP
server can initialize/list tools before any controller exists; it makes no model
call and needs no OAuth. All source calls require an active manual controller.
Its UV cache stays in the ignored project `.cache/uv` directory, including in
managed environments where the user's ordinary cache is read-only.

The controller publishes a private, ignored `.cache/manual-research/connection.json`
descriptor and removes it on exit. The bridge reads it internally; never give the
descriptor or socket to the model. Every tool call must include the random
`manual_operation_id` from that company's context as `operation_id`. Both bridge
and controller check the operation identity so a stale worker cannot read sources
for the next company after the descriptor changes. Missing/expired connections
fail closed. The bridge offers no context, result, apply, abort or filesystem API.

Example model tool arguments:

```json
{"operation_id":"COPY_CONTEXT_MANUAL_OPERATION_ID","action":"search","query":"issuer quarterly results"}
```

For page/PDF reads use `action: open`, `url` and optional one-based `page` instead
of `query`. Search metadata is a lead; reopen financial sources before citing them.

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
| `{"action":"context"}` | Obtain sanitized context, operation ID, complete policy, skill, contracts and limits. Pass only `context` to a fresh company_researcher. |
| `{"action":"web","request":{"action":"open","url":"https://issuer.example/results","page":1}}` | Execute the researcher's source request using the existing broker. Return only `web` to the subagent as untrusted evidence. |
| `{"action":"web","request":{"action":"search","query":"issuer results"}}` | Broker search; consumes the same source budget. |
| `{"action":"result","result":{...}}` | Submit the complete result object from the researcher. The controller, not the model, supplies observations and usage. |
| `{"action":"abort"}` | Stop the operation; its spent attempt follows normal failure handling. |

The researcher uses its research_web MCP tool directly, then returns exactly one
final `result` envelope. The legacy coordinator-relayed web envelope remains an
alternative transport for the same broker; do not execute a request twice. Each
broker call and final submission consumes a controller relay turn. The default
controller permits at most24 relay turns,12 broker requests and600 seconds per
operation; context delivery is not a research turn.
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
establish live model access, a verified research-only runtime, real company research
or deployment. Static feature flags and a successful MCP handshake alone do not
prove the complete effective subagent tool list is restricted.
Local verification passed9 manual integration tests and320 full-suite tests, Ruff,
formatting, MyPy21 modules and strict current validation. Exact-SHA locked CI is a
separate gate; these local checks used the available development environment.

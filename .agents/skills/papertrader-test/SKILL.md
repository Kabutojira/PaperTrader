---
name: papertrader-test
description: Run PaperTrader local tests or a bounded test-fix-push-GitHub Actions loop. Use for requests to test changes, validate a branch, commit/push and test, watch CI, run the daily workflow, or keep repairing failures until green; substantive fixes must go to the stronger code_fixer agent.
---

# PaperTrader test and CI loop

Delegate the loop to the project custom agent `test_operator`, which uses GPT-5.6 Luna. It owns evidence collection, classification, local verification, bounded retries, and remote monitoring. It routes Git/GitHub mechanics to `git_operator` and substantive repairs to the stronger `code_fixer`. All agents and commands run sequentially; after a fixer returns, control always returns to `test_operator`.

When the installed Codex build does not expose custom-agent spawning inside a subagent session,
`test_operator` returns the unchanged bounded package with `REQUEST_PARENT_RELAY_TO=<agent>`. The
parent spawns that named agent, waits, and sends its result back to the same `test_operator` thread.
This relay is transport only: the parent does not redo triage, and `test_operator` continues to own
the loop.

Default `MAX_TEST_FIX_ATTEMPTS` to 3. A lower caller-supplied limit wins. Stop early when the same material failure signature remains after two consecutive repair attempts without meaningful progress.

## Test selection

Inspect the actual diff and reuse repository commands:

- Start with affected unit or integration tests.
- For Python changes, include relevant Ruff and MyPy checks before broad completion.
- For schema, configuration, canonical-data, reporting, or workflow-sensitive changes, run the applicable strict `papertrader` validations from `.github/workflows/ci.yml`.
- For `site/` changes, use the locked npm check/build commands from CI.
- For pre-merge validation, reproduce the complete CI gate unless the caller limits scope.

Do not update golden/reference outputs unless the change is intentional, the repository's documented regeneration command is used, and the diff is reviewed.

## Failure classification and handoff

Luna may apply only safe mechanical corrections permitted by `test_operator`. For every substantive or ambiguous code failure, send `code_fixer` this bounded package:

```text
TASK
Repository / branch:
Current SHA:
Requested operation:

TEST FAILURE
Command:
Test/job:
Exit code:
Failure signature:

EVIDENCE
Relevant logs:
Relevant files:
Remote workflow:
Run ID / URL:

ATTEMPTS
Previous fixes:
Previous results:

CONSTRAINTS
Do not change:
Expected behavior:

REQUEST
Investigate the root cause, make the smallest appropriate fix, run the narrowest relevant test, and return control without committing or pushing.
```

Never autonomously change financial data or protected investment, valuation, portfolio, allocation, risk, strategy, signal, order, fill, or accounting logic unless the original task explicitly authorizes that domain and the capable fixer receives that constraint. Testing verifies those rules; it does not casually rewrite them.

## State machine

```text
inspect -> targeted local tests
  -> pass -> optional git_operator commit/push -> optional remote dispatch/watch
  -> fail -> collect and classify
       -> safe mechanical correction -> retest
       -> substantive -> code_fixer -> test_operator inspects/retests
remote failure -> collect job/step/logs -> classify -> bounded repair -> retest -> push -> recheck
stop -> green | attempt limit | repeated signature | protected scope | genuine human blocker
```

For push-triggered CI, bind the run to the pushed SHA. Do not dispatch a duplicate workflow if the push already launched the required run. For a manual daily workflow, default to dry-run mode with Pages and Telegram disabled; a live daily run requires explicit authorization.

Keep an iteration history with attempt number, SHA, failure signature, fixer summary, changed files, and local/remote result. Return concise evidence:

```text
STATUS: success | failed | blocked
BRANCH:
FINAL_SHA:
LOCAL_COMMANDS_AND_RESULTS:
WORKFLOW:
RUN_ID:
RUN_URL:
RUN_CONCLUSION:
ATTEMPT_HISTORY:
BLOCKER:
NEXT_ACTION:
```

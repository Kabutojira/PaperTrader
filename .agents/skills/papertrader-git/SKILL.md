---
name: papertrader-git
description: Perform routine PaperTrader Git and GitHub Actions operations such as status, commit, push, workflow dispatch, monitoring, and failure-log retrieval. Use for requests like commit this, commit and push, trigger the daily workflow, watch CI, or inspect a remote run failure; do not use it to fix application code.
---

# PaperTrader Git operations

Delegate one bounded operation at a time to the project custom agent `git_operator`, which uses GPT-5.6 Luna. Keep execution sequential and wait for its result before any next operation. Supply the caller's exact authorization, intended paths, workflow, branch or SHA, dispatch inputs, and required stopping point. Do not ask it to rediscover conclusions already established by the parent.

## Workflow

1. Ask `git_operator` to inspect branch, HEAD, status, remotes, upstream, and the relevant diff.
2. For a commit, identify the intended paths. The operator stages only those paths, reviews the staged diff, derives the message from that diff, and commits only when authorized.
3. Push only when requested. Stop on divergence, rejection, conflicts, ambiguous scope, or unexpected changes.
4. For workflow work, reuse `.github/workflows/*.yml` and `docs/OPERATIONS.md`. Resolve the run by workflow, branch/event, and SHA; capture its ID and URL. Monitor at a moderate interval and retrieve failed logs only when needed.
5. Treat a daily dispatch as a dry run with `publish_pages=false` and `send_telegram=false` unless the caller explicitly authorizes non-dry state changes and delivery.

Never let this skill or agent modify code, tests, workflows, research, canonical tables, generated financial views, credentials, or Git history to make the requested operation succeed. Never force-push, delete refs, bypass protection, or resolve a non-trivial conflict without explicit authority.

## Result

Return only applicable fields:

```text
STATUS: success | failed | blocked
BRANCH:
COMMIT_SHA:
COMMIT_MESSAGE:
PUSH_RESULT:
WORKFLOW:
RUN_ID:
RUN_URL:
RUN_STATUS:
RUN_CONCLUSION:
FAILED_JOB_STEP:
FAILURE_SIGNATURE:
RELEVANT_LOGS:
NEXT_ACTION:
```


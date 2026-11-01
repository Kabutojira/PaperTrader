"""Sanitized transport wrapper for the isolated Hermes worker."""

from __future__ import annotations

import contextlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

FAILURE_CODES = {
    "agent_initialization_failed",
    "final_response_invalid",
    "model_unavailable",
    "provider_auth_failed",
    "provider_billing_failed",
    "provider_inference_failed",
    "provider_network_failed",
    "provider_rate_limited",
    "provider_timeout",
    "provider_unavailable",
    "runtime_import_failed",
    "worker_execution_failed",
    "worker_import_failed",
    "worker_request_invalid",
    "worker_serialization_failed",
}


def execute(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text())
        if not isinstance(document, dict):
            raise ValueError
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return {"status": "error", "code": "worker_request_invalid"}
    with contextlib.redirect_stdout(sys.stderr):
        try:
            module = importlib.import_module("papertrader.research_worker")
        except Exception:
            return {"status": "error", "code": "worker_import_failed"}
        try:
            response = module.worker(document)
        except module.WorkerFailure as exc:
            code = exc.diagnostic_code
            return {
                "status": "error",
                "code": code if code in FAILURE_CODES else "worker_execution_failed",
            }
        except Exception:
            return {"status": "error", "code": "worker_execution_failed"}
    return {"status": "ok", "response": response}


def main() -> int:
    envelope = execute(Path(sys.argv[1]))
    try:
        output = json.dumps(envelope, separators=(",", ":"))
    except (TypeError, ValueError, RecursionError):
        output = '{"status":"error","code":"worker_serialization_failed"}'
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

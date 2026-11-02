"""Manual Responses loop: one executable function, no model-controlled local runtime.

The model receives JSON and can request research_web or return text. Trusted Python
owns HTTP/auth, dispatch and validation; no shell, interpreter, MCP or app is loaded.
"""

from __future__ import annotations

import json
import os
import re
import stat
import time
import tomllib
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any, BinaryIO, cast
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

import jsonschema

from papertrader.research_agent import MAX_AUTH_BYTES, ManualResearchError, ResearchLimits
from papertrader.research_manual import MAX_MESSAGE_BYTES, _deadline, manual_context
from papertrader.research_manual_tools import TOOL
from papertrader.research_web import ResearchWeb

BASE_URL = "https://chatgpt.com/backend-api/codex"
# Catalog compatibility version, not a model or a claim about the installed CLI.
CATALOG_VERSION = "0.166.0"
MAX_PROVIDER_BYTES = 2_000_000
MAX_INPUT_BYTES = 2_000_000


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _json_bytes(value: Any, maximum: int) -> bytes:
    raw = json.dumps(value, allow_nan=False).encode()
    if len(raw) > maximum:
        raise RuntimeError("isolated_message_oversized")
    return raw


def _completed_response(stream: BinaryIO) -> dict[str, Any]:
    """Bound SSE bytes and require a terminal completion, never partial model text."""
    total = 0
    data: list[bytes] = []
    while True:
        line = stream.readline(MAX_PROVIDER_BYTES + 1)
        total += len(line)
        if total > MAX_PROVIDER_BYTES:
            raise RuntimeError("isolated_response_oversized")
        if not line:
            raise RuntimeError("isolated_stream_incomplete")
        if line in {b"\n", b"\r\n"}:
            if not data:
                continue
            event = json.loads(b"\n".join(data))
            data = []
            if not isinstance(event, dict):
                raise RuntimeError("isolated_response_invalid")
            kind = event.get("type")
            if kind in {"error", "response.failed", "response.incomplete"}:
                raise RuntimeError("isolated_provider_failed")
            if kind == "response.completed":
                result = event.get("response")
                if not isinstance(result, dict) or result.get("status") != "completed":
                    raise RuntimeError("isolated_response_invalid")
                return result
        elif line.startswith(b"data:"):
            data.append(line[5:].strip())


class CodexResponses:
    """Read the existing local Codex OAuth cache; never refresh, copy or write it."""

    def __init__(self, root: Path) -> None:
        auth_file = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
        if auth_file.resolve().is_relative_to(root.resolve()):
            raise RuntimeError("isolated_auth_inside_repository")
        try:
            descriptor = os.open(auth_file, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "rb") as stream:
                metadata = os.fstat(stream.fileno())
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
                    raise RuntimeError("isolated_auth_permissions")
                raw = stream.read(MAX_AUTH_BYTES + 1)
            if len(raw) > MAX_AUTH_BYTES:
                raise ValueError("oversized auth")
            document = json.loads(raw)
            if document.get("auth_mode") != "chatgpt":
                raise ValueError("OAuth required")
            tokens = document["tokens"]
            access, account = tokens["access_token"], tokens["account_id"]
            if any(
                not isinstance(value, str) or not value or "\r" in value or "\n" in value
                for value in (access, account)
            ):
                raise ValueError("invalid auth")
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            raise RuntimeError("isolated_auth_unavailable") from None
        self._headers = {
            "Authorization": "Bearer " + access,
            "ChatGPT-Account-ID": account,
            "User-Agent": "PaperTrader/0.1 manual-research",
        }
        # No environment proxies, redirects, SDK retries or inherited connectors.
        self._opener = build_opener(ProxyHandler({}), _NoRedirect())

    def _open(self, request: Request, timeout: float) -> Any:
        try:
            return self._opener.open(request, timeout=timeout)
        except TimeoutError:
            raise
        except HTTPError as exc:
            status = exc.code
            exc.close()
            code = "isolated_auth_rejected" if status in {401, 403} else "isolated_provider_failed"
            raise RuntimeError(code) from None
        except (URLError, OSError):
            raise RuntimeError("isolated_provider_unavailable") from None

    def check_model(self, model: str, timeout: float) -> None:
        request = Request(
            BASE_URL + "/models?client_version=" + CATALOG_VERSION,
            headers=self._headers,
        )
        with self._open(request, timeout) as response:
            raw = response.read(MAX_PROVIDER_BYTES + 1)
        if len(raw) > MAX_PROVIDER_BYTES:
            raise RuntimeError("isolated_response_oversized")
        try:
            document = json.loads(raw)
            models = document["models"]
            found = isinstance(models, list) and any(
                isinstance(item, dict) and item.get("slug") == model for item in models
            )
        except (ValueError, TypeError, KeyError, AttributeError):
            raise RuntimeError("isolated_catalog_invalid") from None
        if not found:
            raise RuntimeError("isolated_model_unavailable")

    def complete(self, body: dict[str, Any], timeout: float) -> dict[str, Any]:
        request = Request(
            BASE_URL + "/responses",
            data=_json_bytes(body, MAX_INPUT_BYTES),
            headers={
                **self._headers,
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            method="POST",
        )
        with self._open(request, timeout) as response:
            return _completed_response(response)


def function_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "name": "research_web",
        "description": TOOL["description"],
        "parameters": TOOL["inputSchema"],
        "strict": False,
    }


class IsolatedResearch:
    """Single-company, synchronous tool loop; use preflight before queue admission."""

    def __init__(self, model: str, client: CodexResponses | None = None) -> None:
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}", model) is None:
            raise ValueError("exact isolated model identifier required")
        self.model = model
        self.client = client
        self.inference_requests = 0
        self._ready = False
        self._used = False
        self._instructions = ""
        self._limits: ResearchLimits | None = None

    def audit(self, limits: ResearchLimits) -> dict[str, Any]:
        return {
            "execution": "isolated_responses",
            "model": self.model,
            "tools": [function_tool()],
            "automatic_retries": 0,
            "parallel_tool_calls": False,
            "max_inference_requests": limits.max_turns,
            "max_web_requests": limits.max_web_calls,
            "timeout_seconds": limits.timeout_seconds,
            "response_model_must_match": True,
        }

    def preflight(self, root: Path, limits: ResearchLimits) -> dict[str, Any]:
        if self._used:
            raise RuntimeError("isolated_runner_already_used")
        role = tomllib.loads((root / ".codex/agents/company_researcher.toml").read_text())
        instructions = role.get("developer_instructions")
        if not isinstance(instructions, str) or not instructions or len(instructions) > 20_000:
            raise RuntimeError("isolated_role_invalid")
        self._instructions = instructions
        if self.client is None:
            self.client = CodexResponses(root)
        with _deadline(min(30, limits.timeout_seconds)):
            self.client.check_model(self.model, min(30, limits.timeout_seconds))
        self._limits = replace(limits, model=self.model)
        self._ready = True
        return {**self.audit(limits), "status": "preflight_passed", "catalog_model_verified": True}

    def __call__(
        self, root: Path, packet: dict[str, Any], limits: ResearchLimits
    ) -> dict[str, Any]:
        if not self._ready or self._used or replace(limits, model=self.model) != self._limits:
            raise RuntimeError("isolated_preflight_required")
        self._used = True
        limits = replace(limits, model=self.model)
        broker = ResearchWeb(
            max_calls=limits.max_web_calls,
            runtime=limits.timeout_seconds,
            source_identities=packet.get("_source_identity_index", []),
        )
        context = manual_context(packet, limits)
        try:
            with _deadline(limits.timeout_seconds):
                result = self._loop(context, broker, limits)
        except TimeoutError:
            raise ManualResearchError("manual_timeout", broker.calls) from None
        except ManualResearchError:
            raise
        except Exception:
            raise ManualResearchError("isolated_provider_failed", broker.calls) from None
        return {
            "result": result,
            "observations": broker.observations,
            "usage": {"web_requests": broker.calls},
        }

    def _loop(
        self, context: dict[str, Any], broker: ResearchWeb, limits: ResearchLimits
    ) -> dict[str, Any]:
        deadline = time.monotonic() + limits.timeout_seconds
        assert self.client is not None
        history: list[dict[str, Any]] = [{"role": "user", "content": json.dumps(context)}]
        relay_turns = 0
        for _ in range(limits.max_turns):
            if time.monotonic() >= deadline:
                raise TimeoutError("expired")
            body = {
                "model": self.model,
                "instructions": self._instructions,
                "input": history,
                "tools": [function_tool()],
                "parallel_tool_calls": False,
                "store": False,
                "stream": True,
                "include": ["reasoning.encrypted_content"],
            }
            # This exact request is the complete model tool inventory. There is no
            # plugin discovery, dynamic dispatch, eval or subprocess execution.
            _json_bytes(body, MAX_INPUT_BYTES)
            self.inference_requests += 1
            response = self.client.complete(body, max(0.001, deadline - time.monotonic()))
            if time.monotonic() >= deadline:
                raise TimeoutError("expired")
            if response.get("model") != self.model:
                raise ManualResearchError("isolated_model_mismatch", broker.calls)
            output = response.get("output")
            if response.get("status") != "completed" or not isinstance(output, list):
                raise ManualResearchError("isolated_response_invalid", broker.calls)
            if any(
                not isinstance(item, dict)
                or item.get("type") not in {"reasoning", "function_call", "message"}
                for item in output
            ):
                raise ManualResearchError("isolated_tool_forbidden", broker.calls)
            calls = [item for item in output if item["type"] == "function_call"]
            if len(calls) > 1 or any(item.get("name") != "research_web" for item in calls):
                raise ManualResearchError("isolated_tool_forbidden", broker.calls)
            if relay_turns >= limits.max_turns:
                raise ManualResearchError("manual_turn_budget", broker.calls)
            if calls:
                call = calls[0]
                arguments = json.loads(call["arguments"])
                jsonschema.validate(arguments, cast(Mapping[str, Any], TOOL["inputSchema"]))
                if arguments["operation_id"] != context["manual_operation_id"]:
                    raise ManualResearchError("isolated_tool_forbidden", broker.calls)
                if broker.calls >= limits.max_web_calls:
                    web = {"error": "budget_exhausted"}
                else:
                    broker.timeout = max(1, min(15, int(deadline - time.monotonic())))
                    web = json.loads(
                        broker.tool(
                            {
                                key: value
                                for key, value in arguments.items()
                                if key != "operation_id"
                            }
                        )
                    )
                relay_turns += 1
                history.extend(output)
                history.append(
                    {
                        "type": "function_call_output",
                        "call_id": call["call_id"],
                        "output": json.dumps(web),
                    }
                )
                continue
            text = "".join(
                part["text"]
                for item in output
                if item["type"] == "message"
                for part in item.get("content", [])
                if part.get("type") == "output_text"
            )
            envelope = json.loads(text)
            _json_bytes(envelope, MAX_MESSAGE_BYTES)
            if (
                not isinstance(envelope, dict)
                or set(envelope) != {"action", "result"}
                or envelope["action"] != "result"
                or not isinstance(envelope["result"], dict)
            ):
                raise ManualResearchError("isolated_response_invalid", broker.calls)
            return dict(envelope["result"])
        raise ManualResearchError("manual_turn_budget", broker.calls)

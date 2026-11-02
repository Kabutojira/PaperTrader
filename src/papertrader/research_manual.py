"""Manual, parent-mediated research; no inference client or credentials."""

from __future__ import annotations

import json
import signal
import socket
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import replace
from pathlib import Path
from typing import Any

from papertrader.research_agent import ManualResearchError, ResearchLimits
from papertrader.research_web import ResearchWeb
from papertrader.research_worker import POLICY

MAX_MESSAGE_BYTES = 300_000


@contextmanager
def _deadline(seconds: float) -> Iterator[None]:
    """Interrupt blocking DNS/HTTP as well as idle coordination in the CLI process."""
    if signal.getitimer(signal.ITIMER_REAL)[0]:
        raise RuntimeError("manual controller requires its own process")

    def expired(number: int, frame: Any) -> None:
        raise TimeoutError("manual research deadline exceeded")

    previous = signal.signal(signal.SIGALRM, expired)
    try:
        signal.setitimer(signal.ITIMER_REAL, seconds)
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _receive(connection: socket.socket) -> Any:
    stream = connection.makefile("rb")
    try:
        raw = stream.readline(MAX_MESSAGE_BYTES + 1)
    finally:
        stream.close()
    if len(raw) > MAX_MESSAGE_BYTES or not raw.endswith(b"\n"):
        raise ValueError("invalid manual research message")
    return json.loads(raw)


def _send(connection: socket.socket, value: Any) -> None:
    raw = json.dumps(value, allow_nan=False).encode() + b"\n"
    if len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError("manual research message too large")
    connection.sendall(raw)


def manual_call(endpoint: Path, request: Any) -> dict[str, Any]:
    """Called by the trusted coordinator, never exposed to the research worker."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(20)
        connection.connect(str(endpoint))
        _send(connection, request)
        response = _receive(connection)
    if not isinstance(response, dict):
        raise ValueError("invalid manual research response")
    return response


class ManualResearch:
    """Keep broker observations in the controller while a parent relays model turns.

    This is a transport, not a subagent sandbox. The launcher must independently
    enforce a tool-less research worker; a shared-tools subagent is insufficient.
    """

    def __init__(self, model: str) -> None:
        if not model.strip() or len(model) > 120:
            raise ValueError("exact manual subagent model required")
        self.model = model

    def __call__(
        self, root: Path, packet: dict[str, Any], limits: ResearchLimits
    ) -> dict[str, Any]:
        limits = replace(limits, model=self.model)
        broker = ResearchWeb(
            max_calls=limits.max_web_calls,
            runtime=limits.timeout_seconds,
            source_identities=packet.get("_source_identity_index", []),
        )
        context = {key: value for key, value in packet.items() if not key.startswith("_")}
        context["limits"] = vars(limits)
        context["policy"] = (
            "Manual transport: you have no tools. Return one web or result envelope "
            "per turn to your coordinator. References to research_web below mean "
            "a web envelope for the coordinator's broker. The following final-result "
            "contract describes the inner result object of a result envelope.\n\n" + POLICY
        )
        try:
            with _deadline(limits.timeout_seconds):
                return self._serve(context, broker, limits)
        except TimeoutError:
            raise ManualResearchError("manual_timeout", broker.calls) from None

    def _serve(
        self, context: dict[str, Any], broker: ResearchWeb, limits: ResearchLimits
    ) -> dict[str, Any]:
        deadline = time.monotonic() + limits.timeout_seconds
        turns = 0
        with tempfile.TemporaryDirectory(prefix="pt-manual-") as directory:
            endpoint = Path(directory) / "controller.sock"
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                server.bind(str(endpoint))
                endpoint.chmod(0o600)
                server.listen(1)
                print(
                    json.dumps({"status": "awaiting_subagent", "socket": str(endpoint)}),
                    flush=True,
                )
                while time.monotonic() < deadline:
                    server.settimeout(min(1, max(0.001, deadline - time.monotonic())))
                    try:
                        connection, _ = server.accept()
                    except TimeoutError:
                        continue
                    with connection:
                        connection.settimeout(min(1, max(0.001, deadline - time.monotonic())))
                        try:
                            request = _receive(connection)
                            if time.monotonic() >= deadline:
                                raise TimeoutError("manual research deadline exceeded")
                            broker.timeout = max(1, min(15, int(deadline - time.monotonic())))
                            response, result, turns = self._dispatch(
                                request, context, broker, turns, limits.max_turns
                            )
                            if time.monotonic() >= deadline:
                                raise TimeoutError("manual research deadline exceeded")
                        except RuntimeError:
                            with suppress(OSError):
                                _send(connection, {"error": "manual_research_stopped"})
                            raise
                        except (ValueError, UnicodeDecodeError, TimeoutError, OSError):
                            response, result = {"error": "invalid_manual_request"}, None
                            turns += 1
                            if turns > limits.max_turns:
                                raise ManualResearchError(
                                    "manual_turn_budget", broker.calls
                                ) from None
                        with suppress(OSError):
                            _send(connection, response)
                        if result is not None:
                            return {
                                "result": result,
                                "observations": broker.observations,
                                "usage": {"web_requests": broker.calls},
                            }
            raise ManualResearchError("manual_timeout", broker.calls)

    @staticmethod
    def _dispatch(
        request: Any,
        context: dict[str, Any],
        broker: ResearchWeb,
        turns: int,
        maximum_turns: int,
    ) -> tuple[dict[str, Any], dict[str, Any] | None, int]:
        if not isinstance(request, dict):
            raise ValueError("invalid manual request")
        action = request.get("action")
        if request == {"action": "context"}:
            return {"context": context, "turns_used": turns}, None, turns
        if request == {"action": "abort"}:
            raise ManualResearchError("manual_aborted", broker.calls)
        if turns >= maximum_turns:
            raise ManualResearchError("manual_turn_budget", broker.calls)
        if action == "web" and set(request) == {"action", "request"}:
            if not isinstance(request["request"], dict):
                raise ValueError("invalid broker request")
            result = json.loads(broker.tool(request["request"]))
            return {"web": result, "turns_used": turns + 1}, None, turns + 1
        if action == "result" and set(request) == {"action", "result"}:
            if not isinstance(request["result"], dict):
                raise ValueError("invalid completed result")
            return {"status": "received_pending_validation"}, request["result"], turns + 1
        raise ValueError("unknown manual request")

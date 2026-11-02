"""Manual, parent-mediated research; no inference client or credentials."""

from __future__ import annotations

import json
import signal
import socket
import tempfile
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import replace
from pathlib import Path
from typing import Any

from papertrader.atomic_io import atomic_write_text
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
    enforce a research-tools-only worker; a shared-tools subagent is insufficient.
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
        context["manual_operation_id"] = uuid.uuid4().hex
        context["policy"] = (
            "Manual transport: research_web is your only permitted executable tool. "
            "Include context.manual_operation_id as operation_id on every tool call. "
            "If using coordinator-relayed web envelopes, relay one per turn. Return "
            "your completed result envelope to the coordinator. The final-result "
            "contract describes the inner result object of a result envelope.\n\n" + POLICY
        )
        directory = root / ".cache/manual-research"
        for parent in (root / ".cache", directory):
            if parent.is_symlink():
                raise ValueError("symlink manual connection directory forbidden")
            parent.mkdir(mode=0o700, exist_ok=True)
        connection_file = directory / "connection.json"
        if connection_file.is_symlink():
            raise ValueError("symlink manual connection descriptor forbidden")
        try:
            with _deadline(limits.timeout_seconds):
                return self._serve(context, broker, limits, connection_file)
        except TimeoutError:
            raise ManualResearchError("manual_timeout", broker.calls) from None
        finally:
            connection_file.unlink(missing_ok=True)

    def _serve(
        self,
        context: dict[str, Any],
        broker: ResearchWeb,
        limits: ResearchLimits,
        connection_file: Path,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + limits.timeout_seconds
        turns = 0
        with tempfile.TemporaryDirectory(prefix="pt-manual-") as directory:
            endpoint = Path(directory) / "controller.sock"
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                server.bind(str(endpoint))
                endpoint.chmod(0o600)
                server.listen(1)
                atomic_write_text(
                    connection_file,
                    json.dumps(
                        {"socket": str(endpoint), "operation_id": context["manual_operation_id"]}
                    ),
                    allowed_root=connection_file.parent,
                )
                connection_file.chmod(0o600)
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
        if action == "web" and set(request) in (
            {"action", "request"},
            {"action", "request", "operation_id"},
        ):
            if (
                "operation_id" in request
                and request["operation_id"] != context["manual_operation_id"]
            ):
                raise ValueError("manual operation mismatch")
            if not isinstance(request["request"], dict):
                raise ValueError("invalid broker request")
            result = json.loads(broker.tool(request["request"]))
            return {"web": result, "turns_used": turns + 1}, None, turns + 1
        if action == "result" and set(request) == {"action", "result"}:
            if not isinstance(request["result"], dict):
                raise ValueError("invalid completed result")
            return {"status": "received_pending_validation"}, request["result"], turns + 1
        raise ValueError("unknown manual request")

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest

from papertrader.research_manual import MAX_MESSAGE_BYTES
from papertrader.research_manual_tools import TOOL, dispatch, serve, web_call


def rpc(method: str, params: Any = None) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": 1, "method": method, "params": {} if params is None else params}


def test_researcher_role_disables_development_features_without_fake_permission_overrides(
    repository_root: Path,
) -> None:
    role = tomllib.loads((repository_root / ".codex/agents/company_researcher.toml").read_text())
    assert role["name"] == "company_researcher" and role["developer_instructions"]
    assert all(
        role["features"][key] is False
        for key in ("shell_tool", "apps", "plugins", "memories", "request_permissions_tool")
    )
    assert not {"sandbox_mode", "approval_policy", "mcp_servers", "tools", "model"} & role.keys()
    config = tomllib.loads((repository_root / ".codex/config.toml").read_text())
    broker = config["mcp_servers"]["papertrader_research"]
    assert broker["enabled_tools"] == ["research_web"]
    assert "--locked" in broker["args"] and broker["args"][-1] == "research-manual-tools"


def test_mcp_initializes_and_lists_only_read_only_web_without_active_research(
    tmp_path: Path,
) -> None:
    path = tmp_path / "absent.json"
    initialization = dispatch(rpc("initialize", {"protocolVersion": "2025-11-25"}), path)
    assert initialization is not None
    assert initialization["result"]["capabilities"] == {"tools": {}}
    listed = dispatch(rpc("tools/list"), path)
    assert listed is not None and listed["result"]["tools"] == [TOOL]
    assert TOOL["annotations"]["readOnlyHint"] is True
    assert dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}, path) is None
    assert not path.exists()


@pytest.mark.parametrize("name", ["result", "apply", "abort", "context", "shell", "read_file"])
def test_mcp_never_exposes_controller_or_filesystem_methods(tmp_path: Path, name: str) -> None:
    response = dispatch(rpc("tools/call", {"name": name, "arguments": {}}), tmp_path / "absent")
    assert response is not None and response["error"]["code"] == -32601


@pytest.mark.parametrize(
    "arguments",
    [
        None,
        {"action": "open", "url": "https://example.com"},
        {"operation_id": "a" * 32, "action": ["open"]},
        {"operation_id": "a" * 32, "action": "result", "result": {}},
        {"operation_id": "a" * 32, "action": "search", "query": "x", "socket": "/tmp/other"},
        {"operation_id": "a" * 32, "action": "open", "url": "https://example.com", "page": True},
        {"operation_id": "a" * 32, "action": "search", "query": "x" * 501},
    ],
)
def test_mcp_rejects_untrusted_arguments_before_touching_controller(
    tmp_path: Path,
    arguments: Any,
) -> None:
    assert web_call(tmp_path / "absent", arguments) == {"error": "invalid_request"}


def test_mcp_missing_controller_and_operation_mismatch_are_redacted(tmp_path: Path) -> None:
    path = tmp_path / "connection.json"
    arguments = {"operation_id": "a" * 32, "action": "search", "query": "issuer results"}
    assert web_call(path, arguments) == {"error": "controller_unavailable"}
    path.write_text(json.dumps({"operation_id": "b" * 32, "socket": "/private/controller"}))
    assert web_call(path, arguments) == {"error": "operation_mismatch"}


def test_mcp_stdio_handshake_invalid_input_and_message_limit(tmp_path: Path) -> None:
    frames = [rpc("initialize", {"protocolVersion": []}), rpc("tools/list"), rpc("ping")]
    source = io.BytesIO(
        b"not json\n" + b"".join(json.dumps(row).encode() + b"\n" for row in frames)
    )
    destination = io.StringIO()
    assert serve(tmp_path / "absent", source, destination) == 0
    responses = [json.loads(line) for line in destination.getvalue().splitlines()]
    assert responses[0]["error"]["code"] == -32700
    assert responses[1]["result"]["protocolVersion"] == "2025-06-18"
    assert len(responses[2]["result"]["tools"]) == 1
    assert responses[3]["result"] == {}
    assert (
        serve(tmp_path / "absent", io.BytesIO(b"x" * (MAX_MESSAGE_BYTES + 1)), io.StringIO()) == 4
    )


def test_mcp_cli_entrypoint_initializes_without_active_research(repository_root: Path) -> None:
    frames = b"".join(
        json.dumps(rpc(method)).encode() + b"\n" for method in ("initialize", "tools/list")
    )
    environment = {**os.environ, "PYTHONPATH": str(repository_root / "src")}
    process = subprocess.run(
        [sys.executable, "-m", "papertrader", "research-manual-tools"],
        input=frames,
        capture_output=True,
        cwd=repository_root,
        env=environment,
        timeout=10,
        check=False,
    )
    assert process.returncode == 0
    replies = [json.loads(line) for line in process.stdout.splitlines()]
    assert replies[1]["result"]["tools"] == [TOOL]

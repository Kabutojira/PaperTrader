from __future__ import annotations

import io
import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from papertrader import research_isolated
from papertrader.research_agent import ManualResearchError, ResearchLimits
from papertrader.research_isolated import CodexResponses, IsolatedResearch, _completed_response

MODEL = "test-model-exact"


def completed(output: list[dict[str, Any]], model: str = MODEL) -> dict[str, Any]:
    return {"status": "completed", "model": model, "output": output}


def message(envelope: Any = None) -> dict[str, Any]:
    return {
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": json.dumps(
                    envelope or {"action": "result", "result": {"outcome": "unsupported"}}
                ),
            }
        ],
    }


class FakeClient:
    def __init__(self, replies: list[Any]) -> None:
        self.replies = iter(replies)
        self.requests: list[dict[str, Any]] = []
        self.catalog_reads = 0

    def check_model(self, model: str, timeout: float) -> None:
        assert model == MODEL and timeout <= 30
        self.catalog_reads += 1

    def complete(self, body: dict[str, Any], timeout: float) -> dict[str, Any]:
        self.requests.append(json.loads(json.dumps(body)))
        reply = next(self.replies)
        return reply(body) if callable(reply) else reply


@pytest.fixture
def runner_root(tmp_path: Path) -> Path:
    role = tmp_path / ".codex/agents/company_researcher.toml"
    role.parent.mkdir(parents=True)
    role.write_text('developer_instructions = "Research one supplied company."\n')
    return tmp_path


def prepared(root: Path, client: Any, limits: ResearchLimits) -> IsolatedResearch:
    runner = IsolatedResearch(MODEL, client)
    runner.preflight(root, limits)
    return runner


def call(body: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    context = json.loads(body["input"][0]["content"])
    arguments = {
        "action": "search",
        "query": "issuer results",
        "operation_id": context["manual_operation_id"],
    }
    arguments.update(overrides)
    return completed(
        [
            {
                "type": "function_call",
                "name": "research_web",
                "call_id": "call_1",
                "arguments": json.dumps(arguments),
            }
        ]
    )


def test_runtime_advertises_only_web_and_never_sends_private_context(runner_root: Path) -> None:
    client = FakeClient([completed([message()])])
    limits = ResearchLimits(max_turns=2)
    runner = prepared(runner_root, client, limits)
    outcome = runner(
        runner_root,
        {
            "identity": {"security_id": "s1"},
            "_source_identity_index": [
                {
                    "source_id": "private",
                    "url": "https://issuer.example/source",
                    "license": "marker",
                }
            ],
        },
        limits,
    )
    assert outcome["result"]["outcome"] == "unsupported"
    assert client.catalog_reads == runner.inference_requests == 1
    body = client.requests[0]
    assert [(tool["type"], tool["name"]) for tool in body["tools"]] == [
        ("function", "research_web")
    ]
    assert body["parallel_tool_calls"] is body["store"] is False
    assert body["stream"] is True and body["model"] == MODEL
    assert "marker" not in json.dumps(body)
    assert runner.audit(limits)["automatic_retries"] == 0
    with pytest.raises(RuntimeError, match="preflight_required"):
        runner(runner_root, {}, limits)


@pytest.mark.parametrize(
    "reply,code",
    [
        (completed([{"type": "function_call", "name": "shell"}]), "isolated_tool_forbidden"),
        (completed([{"type": "web_search_call"}]), "isolated_tool_forbidden"),
        (completed([message()], "different-model"), "isolated_model_mismatch"),
        (
            completed([message({"action": "result", "result": {}, "observations": {}})]),
            "isolated_response_invalid",
        ),
        (completed([message(), message()]), "isolated_provider_failed"),
    ],
)
def test_runtime_rejects_tools_model_switches_and_forged_envelopes(
    runner_root: Path, reply: dict[str, Any], code: str
) -> None:
    client = FakeClient([reply])
    limits = ResearchLimits()
    runner = prepared(runner_root, client, limits)
    with pytest.raises(ManualResearchError) as error:
        runner(runner_root, {}, limits)
    assert error.value.diagnostic_code == code and error.value.web_requests == 0
    assert runner.inference_requests == len(client.requests) == 1


def test_wrong_operation_is_rejected_before_broker_access(
    runner_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        research_isolated.ResearchWeb,
        "tool",
        lambda *args: pytest.fail("broker must not be called"),
    )
    client = FakeClient([lambda body: call(body, operation_id="f" * 32)])
    limits = ResearchLimits()
    with pytest.raises(ManualResearchError) as error:
        prepared(runner_root, client, limits)(runner_root, {}, limits)
    assert error.value.diagnostic_code == "isolated_tool_forbidden"


def test_shared_web_and_inference_budgets_are_hard_limits(
    runner_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def web(broker: Any, arguments: Any) -> str:
        broker.calls += 1
        return json.dumps({"untrusted_source_text": "evidence"})

    monkeypatch.setattr(research_isolated.ResearchWeb, "tool", web)
    client = FakeClient([call, call, completed([message()])])
    limits = ResearchLimits(max_turns=3, max_web_calls=1)
    runner = prepared(runner_root, client, limits)
    result = runner(runner_root, {}, limits)
    assert result["usage"]["web_requests"] == 1
    assert runner.inference_requests == 3
    last_tool_output = client.requests[-1]["input"][-1]
    assert json.loads(last_tool_output["output"]) == {"error": "budget_exhausted"}
    exhausted = prepared(
        runner_root, FakeClient([call, call]), ResearchLimits(max_turns=2, max_web_calls=1)
    )
    with pytest.raises(ManualResearchError) as error:
        exhausted(runner_root, {}, ResearchLimits(max_turns=2, max_web_calls=1))
    assert error.value.diagnostic_code == "manual_turn_budget"
    assert exhausted.inference_requests == 2


def test_runtime_interrupts_blocked_inference_without_retry(runner_root: Path) -> None:
    def blocked(body: Any) -> Any:
        time.sleep(5)

    client = FakeClient([blocked])
    limits = ResearchLimits(timeout_seconds=1)
    runner = prepared(runner_root, client, limits)
    start = time.monotonic()
    with pytest.raises(ManualResearchError) as error:
        runner(runner_root, {}, limits)
    assert error.value.diagnostic_code == "manual_timeout"
    assert time.monotonic() - start < 3
    assert len(client.requests) == 1


@pytest.mark.parametrize(
    "events",
    [
        [],
        [{"type": "response.failed", "response": {"error": {"message": "private"}}}],
        [{"type": "response.incomplete"}],
    ],
)
def test_sse_rejects_partial_and_failed_responses(events: list[Any]) -> None:
    stream = io.BytesIO(
        b"".join(b"data: " + json.dumps(event).encode() + b"\n\n" for event in events)
    )
    with pytest.raises(RuntimeError) as error:
        _completed_response(stream)
    assert "private" not in str(error.value)


def test_sse_requires_completed_status_and_bounds_stream_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = completed([message()])
    raw = (
        b"data: "
        + json.dumps({"type": "response.completed", "response": response}).encode()
        + b"\n\n"
    )
    assert _completed_response(io.BytesIO(raw)) == response
    monkeypatch.setattr(research_isolated, "MAX_PROVIDER_BYTES", 30)
    with pytest.raises(RuntimeError, match="oversized"):
        _completed_response(io.BytesIO(raw))


def test_oauth_is_transport_only_and_redirects_are_forbidden(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    auth = tmp_path / "private/auth.json"
    auth.parent.mkdir()
    auth.write_text(
        json.dumps(
            {"auth_mode": "chatgpt", "tokens": {"access_token": "SECRET", "account_id": "ACCOUNT"}}
        )
    )
    auth.chmod(0o600)
    monkeypatch.setenv("CODEX_HOME", str(auth.parent))
    root = tmp_path / "repository"
    client = CodexResponses(root)
    requests: list[Request] = []

    class Opener:
        def open(self, request: Request, timeout: float) -> Any:
            requests.append(request)
            raise HTTPError(request.full_url, 302, "SECRET", {}, io.BytesIO(b"SECRET"))

    client._opener = Opener()  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="isolated_provider_failed") as error:
        client.complete({"model": MODEL}, 1)
    assert "SECRET" not in str(error.value)
    assert len(requests) == 1 and requests[0].get_header("Authorization") == "Bearer SECRET"
    assert "SECRET" not in requests[0].data.decode()  # type: ignore[union-attr]
    assert research_isolated._NoRedirect().redirect_request() is None
    assert auth.read_text().count("SECRET") == 1
    auth.chmod(0o644)
    with pytest.raises(RuntimeError, match="auth_permissions"):
        CodexResponses(root)


def test_auth_inside_repository_and_symlinks_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "auth"))
    with pytest.raises(RuntimeError, match="inside_repository"):
        CodexResponses(tmp_path)
    auth = tmp_path / "auth"
    auth.mkdir()
    (auth / "auth.json").symlink_to(tmp_path / "other")
    with pytest.raises(RuntimeError, match="auth_unavailable"):
        CodexResponses(tmp_path / "repository")

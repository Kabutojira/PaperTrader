from __future__ import annotations

import json
from collections.abc import Mapping
from email.message import Message
from pathlib import Path

import pytest

import papertrader.grok_tts as grok_tts
from papertrader.grok_tts import (
    GrokTTSError,
    latest_podcast_transcripts,
    load_podcast_transcript,
    request_grok_tts_chunk,
    safe_output_directory,
    send_rendered_podcasts,
    split_tts_text,
)


def _transcript(path: Path, *, locale: str | None = None) -> None:
    stamp = path.name.removeprefix("daily-podcast_").split("_", maxsplit=1)[0].removesuffix(".md")
    language = f'language: "{locale}"\n' if locale else ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f'title: "Podcast {stamp}"\n'
        "type: podcast\n"
        f'daily_cycle_id: "daily-{stamp}"\n'
        f"{language}"
        "---\n"
        "<!-- papertrader-spoken-transcript:start -->\n"
        "A complete spoken paragraph for testing.\n"
        "<!-- papertrader-spoken-transcript:end -->\n",
        encoding="utf-8",
    )


def test_latest_transcripts_include_localized_file_and_bind_languages(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    directory = repository / "data" / "wiki" / "podcasts"
    names = (
        "daily-podcast_20260905T102108Z.md",
        "daily-podcast_20260905T171454Z.md",
        "daily-podcast_20260905T235530Z.md",
        "daily-podcast_20260905T235530Z_it-IT.md",
        "daily-podcast_20260904T060928Z.md",
    )
    for name in names:
        _transcript(directory / name, locale="it-IT" if "_it-IT" in name else None)

    selected = latest_podcast_transcripts(repository, count=4)

    assert [item.path.name for item in selected] == [
        "daily-podcast_20260905T235530Z_it-IT.md",
        "daily-podcast_20260905T235530Z.md",
        "daily-podcast_20260905T171454Z.md",
        "daily-podcast_20260905T102108Z.md",
    ]
    assert [(item.locale, item.grok_language) for item in selected] == [
        ("it-IT", "it"),
        ("en-US", "en"),
        ("en-US", "en"),
        ("en-US", "en"),
    ]


def test_transcript_locale_must_match_localized_filename(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    path = repository / "data" / "wiki" / "podcasts" / "daily-podcast_20260905T235530Z_it-IT.md"
    _transcript(path, locale="en-US")

    with pytest.raises(GrokTTSError, match="language conflicts"):
        load_podcast_transcript(repository, path)


def test_tts_chunking_stays_bounded_and_preserves_words() -> None:
    text = "First sentence has useful context. " * 50 + "\n\n" + "Second paragraph follows. " * 50

    chunks = split_tts_text(text, limit=180)

    assert len(chunks) > 2
    assert all(len(chunk) <= 180 for chunk in chunks)
    assert " ".join(" ".join(chunks).split()) == " ".join(text.split())


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.headers = Message()
        self.headers["Content-Type"] = "audio/mpeg"

    def read(self) -> bytes:
        return self.body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def test_grok_request_sends_explicit_transcript_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_open(request: object, timeout_seconds: int) -> _FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout_seconds
        return _FakeResponse(b"ID3-audio")

    monkeypatch.setattr(grok_tts, "_open_url", fake_open)

    result = request_grok_tts_chunk(
        "Benvenuti al podcast.",
        api_key="xai-secret",
        language="it",
        voice="helix",
        sleeper=lambda _: None,
    )

    request = captured["request"]
    assert isinstance(request, grok_tts.urllib.request.Request)
    assert captured["timeout"] == 180
    assert request.full_url == "https://api.x.ai/v1/tts"
    assert request.get_header("Authorization") == "Bearer xai-secret"
    assert json.loads(request.data or b"{}") == {
        "text": "Benvenuti al podcast.",
        "voice_id": "helix",
        "language": "it",
        "output_format": {"codec": "mp3", "sample_rate": 44100, "bit_rate": 128000},
    }
    assert result == b"ID3-audio"


def test_output_directory_inside_repository_is_rejected(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()

    with pytest.raises(GrokTTSError, match="outside the repository"):
        safe_output_directory(repository, repository / "tmp" / "audio")


class _FakeTelegram:
    def __init__(self) -> None:
        self.calls: list[tuple[dict[str, str], Path]] = []

    def preflight(self, token: str, chat_id: str, *, timeout_seconds: int) -> None:
        assert token == "telegram-secret"
        assert chat_id == "-123"
        assert timeout_seconds == 60

    def send_audio(
        self,
        token: str,
        payload: Mapping[str, str],
        audio_path: Path,
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]:
        del token, timeout_seconds
        self.calls.append((dict(payload), audio_path))
        return {"ok": True}


def test_successful_telegram_send_uses_locale_and_deletes_audio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = tmp_path / "repository"
    transcript_path = (
        repository / "data" / "wiki" / "podcasts" / "daily-podcast_20260905T235530Z_it-IT.md"
    )
    _transcript(transcript_path, locale="it-IT")
    transcript = load_podcast_transcript(repository, transcript_path)
    output = tmp_path / "audio"
    output.mkdir()
    audio = output / transcript.audio_filename
    audio.write_bytes(b"ID3-audio")
    manifest = output / transcript.manifest_filename
    manifest.write_text(
        json.dumps(
            {
                "grok_tts_manifest_version": 1,
                "endpoint": "https://api.x.ai/v1/tts",
                "transcript_path": ("data/wiki/podcasts/daily-podcast_20260905T235530Z_it-IT.md"),
                "transcript_sha256": grok_tts.hashlib.sha256(
                    transcript.path.read_bytes()
                ).hexdigest(),
                "spoken_transcript_sha256": grok_tts.hashlib.sha256(
                    transcript.text.encode("utf-8")
                ).hexdigest(),
                "daily_cycle_id": transcript.cycle_id,
                "locale": "it-IT",
                "language": "it",
                "audio_filename": audio.name,
                "audio_sha256": grok_tts.hashlib.sha256(audio.read_bytes()).hexdigest(),
                "audio_size": audio.stat().st_size,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(grok_tts, "probe_mp3", lambda _: 1200.0)
    transport = _FakeTelegram()

    sent = send_rendered_podcasts(
        (transcript,),
        output,
        token="telegram-secret",
        chat_id="-123",
        transport=transport,
        sleeper=lambda _: None,
    )

    assert sent == (audio,)
    assert transport.calls[0][0]["caption"].endswith("it-IT — 20260905T235530Z")
    assert not audio.exists()
    assert not manifest.exists()

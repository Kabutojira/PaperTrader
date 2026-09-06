"""Manual, ephemeral Grok TTS rendering for committed podcast transcripts."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from http.client import HTTPResponse
from pathlib import Path
from typing import Protocol, cast

import yaml

from papertrader.podcast import PodcastError, spoken_transcript
from papertrader.telegram import CHAT_ID, TelegramDeliveryError, UrllibTelegramTransport

GROK_TTS_ENDPOINT = "https://api.x.ai/v1/tts"
GROK_TTS_CHARACTER_LIMIT = 15_000
GROK_TTS_CHUNK_LIMIT = 14_500
GROK_TTS_MAXIMUM_ATTEMPTS = 3
TELEGRAM_AUDIO_MAXIMUM_BYTES = 50_000_000
DEFAULT_GROK_VOICE = "helix"
DEFAULT_LATEST_COUNT = 4
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_TELEGRAM_TIMEOUT_SECONDS = 60
TRANSCRIPT_DIRECTORY = Path("data/wiki/podcasts")
TRANSCRIPT_FILE = re.compile(
    r"^daily-podcast_(?P<stamp>[0-9]{8}T[0-9]{6}Z)"
    r"(?:_(?P<locale>[a-z]{2}-[A-Z]{2}))?\.md$"
)
LOCALE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
GROK_VOICES = frozenset(
    {
        "altair",
        "ara",
        "atlas",
        "aurora",
        "carina",
        "castor",
        "celeste",
        "cosmo",
        "eve",
        "helios",
        "helix",
        "iris",
        "kepler",
        "leo",
        "liora",
        "lumen",
        "luna",
        "lux",
        "naksh",
        "orion",
        "perseus",
        "rex",
        "rigel",
        "sal",
        "sirius",
        "ursa",
        "zagan",
        "zenith",
    }
)
GROK_LANGUAGE_CODES = frozenset(
    {
        "ar-EG",
        "ar-SA",
        "ar-AE",
        "bn",
        "de",
        "en",
        "es-ES",
        "es-MX",
        "fr",
        "hi",
        "id",
        "it",
        "ja",
        "ko",
        "pt-BR",
        "pt-PT",
        "ru",
        "tr",
        "vi",
        "zh",
    }
)
PRIMARY_LANGUAGE_CODES = frozenset(
    {"bn", "de", "en", "fr", "hi", "id", "it", "ja", "ko", "ru", "tr", "vi", "zh"}
)
SECRET_NAMES = frozenset({"X_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"})


class GrokTTSError(RuntimeError):
    """Raised when the maintenance helper cannot render or deliver audio safely."""


class PodcastTelegramTransport(Protocol):
    def preflight(self, token: str, chat_id: str, *, timeout_seconds: int) -> None: ...

    def send_audio(
        self,
        token: str,
        payload: Mapping[str, str],
        audio_path: Path,
        *,
        timeout_seconds: int,
    ) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class PodcastTranscript:
    path: Path
    title: str
    cycle_id: str
    locale: str
    grok_language: str
    text: str

    @property
    def audio_filename(self) -> str:
        return f"{self.path.stem}_grok.mp3"

    @property
    def manifest_filename(self) -> str:
        return f"{self.path.stem}_grok.json"


@dataclass(frozen=True, slots=True)
class RenderedPodcast:
    transcript: PodcastTranscript
    audio_path: Path
    manifest_path: Path
    audio_sha256: str
    duration_seconds: float
    chunk_count: int


def _regular_file(path: Path, *, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise GrokTTSError(f"{label} must be a regular file: {path}")


def _within(path: Path, parent: Path) -> bool:
    return path == parent or path.is_relative_to(parent)


def _resolved_transcript_path(repository_root: Path, path: Path) -> Path:
    root = repository_root.resolve()
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve()
    transcript_root = (root / TRANSCRIPT_DIRECTORY).resolve()
    if not _within(resolved, transcript_root):
        raise GrokTTSError("podcast transcript must be beneath data/wiki/podcasts")
    _regular_file(resolved, label="podcast transcript")
    return resolved


def grok_language_for_locale(locale: str) -> str:
    """Convert a transcript locale to an explicitly supported Grok TTS language code."""

    if LOCALE.fullmatch(locale) is None:
        raise GrokTTSError(f"podcast transcript locale is invalid: {locale}")
    if locale in GROK_LANGUAGE_CODES:
        return locale
    primary = locale.split("-", maxsplit=1)[0]
    if primary in PRIMARY_LANGUAGE_CODES:
        return primary
    raise GrokTTSError(f"Grok TTS does not explicitly support transcript locale {locale}")


def _frontmatter(markdown: str) -> Mapping[str, object]:
    if not markdown.startswith("---\n") or "\n---\n" not in markdown[4:]:
        raise GrokTTSError("podcast transcript lacks YAML frontmatter")
    raw, _ = markdown[4:].split("\n---\n", maxsplit=1)
    try:
        value = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise GrokTTSError("podcast transcript has invalid YAML frontmatter") from exc
    if not isinstance(value, dict):
        raise GrokTTSError("podcast transcript frontmatter must be an object")
    return cast(Mapping[str, object], value)


def load_podcast_transcript(repository_root: Path, path: Path) -> PodcastTranscript:
    """Read one canonical podcast page and bind its filename, locale, and spoken section."""

    resolved = _resolved_transcript_path(repository_root, path)
    match = TRANSCRIPT_FILE.fullmatch(resolved.name)
    if match is None:
        raise GrokTTSError(f"podcast transcript filename is not canonical: {resolved.name}")
    try:
        markdown = resolved.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise GrokTTSError("podcast transcript is not UTF-8") from exc
    metadata = _frontmatter(markdown)
    if metadata.get("type") != "podcast":
        raise GrokTTSError("podcast transcript frontmatter has the wrong type")
    expected_cycle = f"daily-{match.group('stamp')}"
    if metadata.get("daily_cycle_id") != expected_cycle:
        raise GrokTTSError("podcast transcript cycle conflicts with its filename")
    filename_locale = match.group("locale")
    metadata_locale = metadata.get("language")
    if metadata_locale is not None and not isinstance(metadata_locale, str):
        raise GrokTTSError("podcast transcript language metadata is invalid")
    locale = metadata_locale or filename_locale or "en-US"
    if filename_locale is not None and filename_locale != locale:
        raise GrokTTSError("podcast transcript language conflicts with its filename")
    title = metadata.get("title")
    if not isinstance(title, str) or not title.strip():
        raise GrokTTSError("podcast transcript title is missing")
    try:
        text = spoken_transcript(markdown)
    except PodcastError as exc:
        raise GrokTTSError(str(exc)) from exc
    return PodcastTranscript(
        path=resolved,
        title=title.strip(),
        cycle_id=expected_cycle,
        locale=locale,
        grok_language=grok_language_for_locale(locale),
        text=text,
    )


def latest_podcast_transcripts(
    repository_root: Path, *, count: int = DEFAULT_LATEST_COUNT
) -> tuple[PodcastTranscript, ...]:
    """Return the newest canonical transcript files, including localized publications."""

    if count <= 0:
        raise GrokTTSError("latest transcript count must be positive")
    directory = repository_root.resolve() / TRANSCRIPT_DIRECTORY
    if directory.is_symlink() or not directory.is_dir():
        raise GrokTTSError("podcast transcript directory is unavailable")
    candidates = [
        path
        for path in directory.iterdir()
        if path.is_file() and not path.is_symlink() and TRANSCRIPT_FILE.fullmatch(path.name)
    ]
    selected = sorted(candidates, key=lambda item: item.name, reverse=True)[:count]
    if len(selected) != count:
        raise GrokTTSError(f"requested {count} transcripts but found {len(selected)}")
    return tuple(load_podcast_transcript(repository_root, path) for path in selected)


def split_tts_text(text: str, *, limit: int = GROK_TTS_CHUNK_LIMIT) -> tuple[str, ...]:
    """Split spoken prose beneath the xAI limit, preferring paragraph and sentence boundaries."""

    if limit <= 0 or limit > GROK_TTS_CHARACTER_LIMIT:
        raise ValueError("Grok TTS chunk limit is invalid")
    remaining = text.strip()
    if not remaining:
        raise GrokTTSError("spoken transcript is empty")
    chunks: list[str] = []
    while len(remaining) > limit:
        boundaries = (
            remaining.rfind("\n\n", 0, limit + 1),
            remaining.rfind(". ", 0, limit + 1),
            remaining.rfind("? ", 0, limit + 1),
            remaining.rfind("! ", 0, limit + 1),
            remaining.rfind("; ", 0, limit + 1),
            remaining.rfind(", ", 0, limit + 1),
            remaining.rfind(" ", 0, limit + 1),
        )
        split_at = max(boundaries)
        if split_at < limit // 2:
            split_at = limit
        elif remaining[split_at : split_at + 2] in {". ", "? ", "! ", "; ", ", "}:
            split_at += 1
        chunk = remaining[:split_at].strip()
        if not chunk:
            raise GrokTTSError("spoken transcript cannot be split safely")
        chunks.append(chunk)
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    if any(len(chunk) > limit for chunk in chunks):
        raise GrokTTSError("Grok TTS chunk exceeds its deterministic limit")
    return tuple(chunks)


def _open_url(request: urllib.request.Request, timeout_seconds: int) -> HTTPResponse:
    response = urllib.request.urlopen(request, timeout=timeout_seconds)
    return cast(HTTPResponse, response)


def _redacted_remote_error(prefix: str, body: bytes, *, secret: str) -> GrokTTSError:
    detail = " ".join(body.decode("utf-8", errors="replace").split())[:300]
    detail = detail.replace(secret, "[redacted]")
    return GrokTTSError(f"{prefix}: {detail}" if detail else prefix)


def request_grok_tts_chunk(
    text: str,
    *,
    api_key: str,
    language: str,
    voice: str = DEFAULT_GROK_VOICE,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    maximum_attempts: int = GROK_TTS_MAXIMUM_ATTEMPTS,
    sleeper: Callable[[float], None] = time.sleep,
) -> bytes:
    """Render one bounded chunk with retry only for transient xAI failures."""

    if not api_key:
        raise GrokTTSError("X_API_KEY is required")
    if not text or len(text) > GROK_TTS_CHARACTER_LIMIT:
        raise GrokTTSError("Grok TTS text must contain at most 15,000 characters")
    if language not in GROK_LANGUAGE_CODES:
        raise GrokTTSError(f"unsupported Grok TTS language: {language}")
    canonical_voice = voice.lower()
    if canonical_voice not in GROK_VOICES:
        raise GrokTTSError(f"unsupported Grok TTS voice: {voice}")
    if timeout_seconds <= 0 or maximum_attempts <= 0 or maximum_attempts > 5:
        raise GrokTTSError("Grok TTS retry settings are invalid")
    payload = json.dumps(
        {
            "text": text,
            "voice_id": canonical_voice,
            "language": language,
            "output_format": {"codec": "mp3", "sample_rate": 44_100, "bit_rate": 128_000},
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        GROK_TTS_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    for attempt in range(1, maximum_attempts + 1):
        try:
            with _open_url(request, timeout_seconds) as response:
                audio = response.read()
            if not audio:
                raise GrokTTSError("Grok TTS returned empty audio")
            return audio
        except urllib.error.HTTPError as exc:
            body = exc.read()
            transient = exc.code == 429 or 500 <= exc.code < 600
            if not transient or attempt == maximum_attempts:
                raise _redacted_remote_error(
                    f"Grok TTS HTTP {exc.code}", body, secret=api_key
                ) from exc
        except (TimeoutError, urllib.error.URLError) as exc:
            if attempt == maximum_attempts:
                raise GrokTTSError(f"Grok TTS transport failed: {exc}") from exc
        if attempt < maximum_attempts:
            sleeper(float(2 ** (attempt - 1)))
    raise GrokTTSError("Grok TTS retry loop ended unexpectedly")


def _subprocess_environment() -> Mapping[str, str]:
    """Keep API and Telegram credentials out of ffmpeg and ffprobe child processes."""

    environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    for name in ("LANG", "LC_ALL"):
        if value := os.environ.get(name):
            environment[name] = value
    return environment


def safe_output_directory(repository_root: Path, output_directory: Path) -> Path:
    """Create or validate an output directory that cannot enter the checkout."""

    root = repository_root.resolve()
    output = output_directory.resolve()
    if _within(output, root):
        raise GrokTTSError("Grok TTS output directory must remain outside the repository")
    if output.exists() and (output.is_symlink() or not output.is_dir()):
        raise GrokTTSError("Grok TTS output path must be a real directory")
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise GrokTTSError("Grok TTS output directory must not be a symlink")
    return output


def probe_mp3(path: Path) -> float:
    """Return a positive duration after ffprobe confirms the final artifact is MP3."""

    _regular_file(path, label="Grok TTS audio")
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=format_name,duration",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_environment(),
    )
    if result.returncode != 0:
        raise GrokTTSError(f"ffprobe rejected Grok TTS audio: {result.stderr.strip()[:300]}")
    try:
        payload = json.loads(result.stdout)
        audio_format = payload["format"]
        format_name = str(audio_format["format_name"])
        duration = float(audio_format["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise GrokTTSError("ffprobe returned invalid Grok TTS metadata") from exc
    if "mp3" not in format_name.split(",") or not math.isfinite(duration) or duration <= 0:
        raise GrokTTSError("Grok TTS output is not a positive-duration MP3")
    return duration


def _write_bytes(path: Path, value: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    temporary = path.with_name(f".{path.name}.partial")
    temporary.unlink(missing_ok=True)
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _assemble_chunks(chunks: Sequence[Path], destination: Path, temporary_root: Path) -> None:
    if not chunks:
        raise GrokTTSError("Grok TTS produced no chunks")
    partial = destination.with_name(f".{destination.name}.partial.mp3")
    if partial.exists():
        partial.unlink()
    if len(chunks) == 1:
        shutil.copyfile(chunks[0], partial)
    else:
        concat = temporary_root / "concat.txt"
        concat.write_text("".join(f"file '{chunk.name}'\n" for chunk in chunks), encoding="utf-8")
        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "1",
                "-i",
                concat.name,
                "-c",
                "copy",
                str(partial),
            ],
            cwd=temporary_root,
            check=False,
            capture_output=True,
            text=True,
            env=_subprocess_environment(),
        )
        if result.returncode != 0:
            partial.unlink(missing_ok=True)
            raise GrokTTSError(f"ffmpeg could not join Grok TTS chunks: {result.stderr[:300]}")
    os.replace(partial, destination)


def render_podcast_transcript(
    repository_root: Path,
    transcript: PodcastTranscript,
    output_directory: Path,
    *,
    api_key: str,
    voice: str = DEFAULT_GROK_VOICE,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> RenderedPodcast:
    """Render one transcript sequentially and atomically publish its ephemeral MP3."""

    output = safe_output_directory(repository_root, output_directory)
    destination = output / transcript.audio_filename
    manifest_path = output / transcript.manifest_filename
    for path in (destination, manifest_path):
        if path.exists() or path.is_symlink():
            raise GrokTTSError(f"refusing to overwrite existing Grok TTS output: {path}")
    text_chunks = split_tts_text(transcript.text)
    with tempfile.TemporaryDirectory(prefix=".grok-tts-", dir=output) as directory:
        temporary_root = Path(directory)
        audio_chunks: list[Path] = []
        for index, text_chunk in enumerate(text_chunks, start=1):
            audio = request_grok_tts_chunk(
                text_chunk,
                api_key=api_key,
                language=transcript.grok_language,
                voice=voice,
                timeout_seconds=timeout_seconds,
            )
            chunk_path = temporary_root / f"chunk-{index:03d}.mp3"
            _write_bytes(chunk_path, audio)
            audio_chunks.append(chunk_path)
        _assemble_chunks(audio_chunks, destination, temporary_root)
    try:
        duration = probe_mp3(destination)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    audio_sha256 = hashlib.sha256(destination.read_bytes()).hexdigest()
    try:
        transcript_relative = transcript.path.resolve().relative_to(repository_root.resolve())
    except ValueError as exc:
        destination.unlink(missing_ok=True)
        raise GrokTTSError("podcast transcript is outside the repository") from exc
    manifest = {
        "grok_tts_manifest_version": 1,
        "endpoint": GROK_TTS_ENDPOINT,
        "transcript_path": transcript_relative.as_posix(),
        "transcript_sha256": hashlib.sha256(transcript.path.read_bytes()).hexdigest(),
        "spoken_transcript_sha256": hashlib.sha256(transcript.text.encode("utf-8")).hexdigest(),
        "daily_cycle_id": transcript.cycle_id,
        "locale": transcript.locale,
        "language": transcript.grok_language,
        "voice": voice.lower(),
        "audio_filename": destination.name,
        "audio_sha256": audio_sha256,
        "audio_size": destination.stat().st_size,
        "duration_seconds": duration,
        "chunk_count": len(text_chunks),
    }
    try:
        _write_json(manifest_path, manifest)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return RenderedPodcast(
        transcript=transcript,
        audio_path=destination,
        manifest_path=manifest_path,
        audio_sha256=audio_sha256,
        duration_seconds=duration,
        chunk_count=len(text_chunks),
    )


def _safe_delivery_error(error: BaseException, token: str, chat_id: str) -> str:
    value = " ".join(str(error).split())
    for secret in (token, chat_id):
        if secret:
            value = value.replace(secret, "[redacted]")
    return value[:500]


def _validate_render_manifest(
    transcript: PodcastTranscript, output_directory: Path
) -> tuple[Path, Path]:
    audio_path = output_directory.resolve() / transcript.audio_filename
    manifest_path = output_directory.resolve() / transcript.manifest_filename
    _regular_file(audio_path, label="Grok TTS audio")
    _regular_file(manifest_path, label="Grok TTS manifest")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GrokTTSError(f"Grok TTS manifest is invalid: {manifest_path.name}") from exc
    if not isinstance(manifest, dict) or manifest.get("grok_tts_manifest_version") != 1:
        raise GrokTTSError(f"Grok TTS manifest contract is invalid: {manifest_path.name}")
    expected = {
        "endpoint": GROK_TTS_ENDPOINT,
        "transcript_path": (TRANSCRIPT_DIRECTORY / transcript.path.name).as_posix(),
        "transcript_sha256": hashlib.sha256(transcript.path.read_bytes()).hexdigest(),
        "spoken_transcript_sha256": hashlib.sha256(transcript.text.encode("utf-8")).hexdigest(),
        "daily_cycle_id": transcript.cycle_id,
        "locale": transcript.locale,
        "language": transcript.grok_language,
        "audio_filename": audio_path.name,
        "audio_sha256": hashlib.sha256(audio_path.read_bytes()).hexdigest(),
        "audio_size": audio_path.stat().st_size,
    }
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise GrokTTSError(f"Grok TTS audio differs from its manifest: {audio_path.name}")
    return audio_path, manifest_path


def send_rendered_podcasts(
    transcripts: Sequence[PodcastTranscript],
    output_directory: Path,
    *,
    token: str,
    chat_id: str,
    delete_after_send: bool = True,
    transport: PodcastTelegramTransport | None = None,
    timeout_seconds: int = DEFAULT_TELEGRAM_TIMEOUT_SECONDS,
    maximum_attempts: int = 3,
    sleeper: Callable[[float], None] = time.sleep,
) -> tuple[Path, ...]:
    """Send matched MP3s sequentially and remove each only after Telegram accepts it."""

    if not token or CHAT_ID.fullmatch(chat_id) is None:
        raise GrokTTSError("TELEGRAM_BOT_TOKEN and canonical TELEGRAM_CHAT_ID are required")
    if timeout_seconds <= 0 or maximum_attempts <= 0 or maximum_attempts > 5:
        raise GrokTTSError("Telegram retry settings are invalid")
    selected_transport = transport or UrllibTelegramTransport()
    try:
        selected_transport.preflight(token, chat_id, timeout_seconds=timeout_seconds)
    except (OSError, TelegramDeliveryError, ValueError) as exc:
        raise GrokTTSError(_safe_delivery_error(exc, token, chat_id)) from exc
    sent: list[Path] = []
    for transcript in transcripts:
        audio_path, manifest_path = _validate_render_manifest(transcript, output_directory)
        if audio_path.stat().st_size > TELEGRAM_AUDIO_MAXIMUM_BYTES:
            raise GrokTTSError(f"Grok TTS audio exceeds Telegram's limit: {audio_path.name}")
        probe_mp3(audio_path)
        payload = {
            "chat_id": chat_id,
            "title": transcript.title[:128],
            "performer": "PaperTrader",
            "caption": (
                f"PaperTrader podcast — {transcript.locale} — "
                f"{transcript.cycle_id.removeprefix('daily-')}"
            ),
        }
        failure = ""
        for attempt in range(1, maximum_attempts + 1):
            try:
                response = selected_transport.send_audio(
                    token,
                    payload,
                    audio_path,
                    timeout_seconds=timeout_seconds,
                )
                if response.get("ok") is not True:
                    raise TelegramDeliveryError(
                        str(response.get("description", "Telegram rejected the audio"))
                    )
                failure = ""
                break
            except (OSError, TelegramDeliveryError, ValueError) as exc:
                failure = _safe_delivery_error(exc, token, chat_id)
                if attempt < maximum_attempts:
                    sleeper(float(2 ** (attempt - 1)))
        if failure:
            raise GrokTTSError(f"Telegram delivery failed for {audio_path.name}: {failure}")
        sent.append(audio_path)
        if delete_after_send:
            audio_path.unlink()
            manifest_path.unlink()
    return tuple(sent)


def load_environment_file(path: Path, *, names: Sequence[str]) -> None:
    """Load only explicitly requested secrets from a dotenv-style file without shell execution."""

    _regular_file(path, label="environment file")
    requested = set(names)
    if not requested <= SECRET_NAMES:
        raise GrokTTSError("environment file request contains an unsupported variable")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        if key not in requested or os.environ.get(key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[key] = value


__all__ = [
    "DEFAULT_GROK_VOICE",
    "DEFAULT_LATEST_COUNT",
    "GrokTTSError",
    "PodcastTranscript",
    "RenderedPodcast",
    "grok_language_for_locale",
    "latest_podcast_transcripts",
    "load_environment_file",
    "load_podcast_transcript",
    "probe_mp3",
    "render_podcast_transcript",
    "request_grok_tts_chunk",
    "safe_output_directory",
    "send_rendered_podcasts",
    "split_tts_text",
]

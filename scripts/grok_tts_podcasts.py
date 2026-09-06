#!/usr/bin/env python3
"""Render podcast transcripts with Grok TTS or send prior renders to Telegram."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from pathlib import Path

from papertrader.grok_tts import (
    DEFAULT_GROK_VOICE,
    DEFAULT_LATEST_COUNT,
    GrokTTSError,
    PodcastTranscript,
    latest_podcast_transcripts,
    load_environment_file,
    load_podcast_transcript,
    render_podcast_transcript,
    safe_output_directory,
    send_rendered_podcasts,
)


def _positive_int(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _add_selection_arguments(parser: argparse.ArgumentParser) -> None:
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--latest",
        type=_positive_int,
        help=f"select the newest N transcript files (default: {DEFAULT_LATEST_COUNT})",
    )
    selection.add_argument(
        "--transcript",
        type=Path,
        action="append",
        help="select one transcript path; repeat to preserve an explicit order",
    )


def _selected_transcripts(
    repository_root: Path,
    latest: int | None,
    paths: Sequence[Path] | None,
) -> tuple[PodcastTranscript, ...]:
    if paths:
        return tuple(load_podcast_transcript(repository_root, path) for path in paths)
    return latest_podcast_transcripts(
        repository_root, count=latest if latest is not None else DEFAULT_LATEST_COUNT
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=_repository_root())
    parser.add_argument(
        "--env-file",
        type=Path,
        help="ignored dotenv file; each phase reads only the credentials it needs",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="create MP3 files with Grok TTS")
    _add_selection_arguments(render)
    render.add_argument("--output-dir", type=Path, required=True)
    render.add_argument("--voice", default=DEFAULT_GROK_VOICE)
    render.add_argument("--timeout-seconds", type=_positive_int, default=180)

    send = subparsers.add_parser("send", help="send matching rendered MP3 files to Telegram")
    _add_selection_arguments(send)
    send.add_argument("--output-dir", type=Path, required=True)
    send.add_argument("--timeout-seconds", type=_positive_int, default=60)
    send.add_argument("--keep-audio", action="store_true")
    return parser


def _load_phase_environment(arguments: argparse.Namespace) -> None:
    irrelevant_names = (
        ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
        if arguments.command == "render"
        else ("X_API_KEY",)
    )
    for name in irrelevant_names:
        os.environ.pop(name, None)
    if arguments.env_file is None:
        return
    names = (
        ("X_API_KEY",)
        if arguments.command == "render"
        else ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    )
    load_environment_file(arguments.env_file, names=names)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    try:
        _load_phase_environment(arguments)
        repository_root = arguments.repository_root.resolve()
        transcripts = _selected_transcripts(repository_root, arguments.latest, arguments.transcript)
        output_directory = safe_output_directory(repository_root, arguments.output_dir)
        if arguments.command == "render":
            api_key = os.environ.get("X_API_KEY", "")
            if not api_key:
                raise GrokTTSError("X_API_KEY is required for rendering")
            for transcript in transcripts:
                result = render_podcast_transcript(
                    repository_root,
                    transcript,
                    output_directory,
                    api_key=api_key,
                    voice=arguments.voice,
                    timeout_seconds=arguments.timeout_seconds,
                )
                print(
                    f"rendered {result.audio_path.name}: locale={transcript.locale} "
                    f"language={transcript.grok_language} voice={arguments.voice.lower()} "
                    f"chunks={result.chunk_count} duration={result.duration_seconds:.1f}s "
                    f"sha256={result.audio_sha256}; manifest={result.manifest_path.name}"
                )
        else:
            token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
            sent = send_rendered_podcasts(
                transcripts,
                output_directory,
                token=token,
                chat_id=chat_id,
                delete_after_send=not arguments.keep_audio,
                timeout_seconds=arguments.timeout_seconds,
            )
            disposition = "kept outside repository" if arguments.keep_audio else "deleted"
            for path, transcript in zip(sent, transcripts, strict=True):
                print(f"sent {path.name}: locale={transcript.locale}; local audio {disposition}")
    except (GrokTTSError, OSError, ValueError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

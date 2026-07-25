"""Validate the encrypted OAuth handoff at the write-controlled boundary."""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path, PurePosixPath

from papertrader.atomic_io import atomic_write_bytes
from papertrader.utils import content_hash

OAUTH_CIPHERTEXT_PATH = PurePosixPath(".papertrader/credentials/openai-oauth-auth.json.age")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class OAuthCredentialArtifactError(RuntimeError):
    """Raised when the ciphertext-only artifact violates its exact contract."""


def _artifact_entries(root: Path) -> tuple[PurePosixPath, ...]:
    entries: list[PurePosixPath] = []
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in (*directory_names, *file_names):
            path = current_path / name
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise OAuthCredentialArtifactError("OAuth artifact must not contain symlinks")
            if name in file_names:
                if not stat.S_ISREG(metadata.st_mode):
                    raise OAuthCredentialArtifactError(
                        "OAuth artifact must contain only a regular ciphertext file"
                    )
                entries.append(PurePosixPath(path.relative_to(root).as_posix()))
            elif not stat.S_ISDIR(metadata.st_mode):
                raise OAuthCredentialArtifactError(
                    "OAuth artifact must not contain special directories"
                )
    return tuple(sorted(entries))


def apply_oauth_ciphertext_artifact(
    repository_root: Path,
    artifact_directory: Path,
    *,
    expected_sha256: str,
) -> Path:
    """Verify one exact ciphertext artifact and copy it into the clean checkout."""

    if not SHA256.fullmatch(expected_sha256):
        raise OAuthCredentialArtifactError("OAuth artifact digest must be a SHA-256 value")
    root = artifact_directory.absolute()
    if root.is_symlink() or not root.is_dir():
        raise OAuthCredentialArtifactError("OAuth artifact root must be a regular directory")
    entries = _artifact_entries(root)
    if entries != (OAUTH_CIPHERTEXT_PATH,):
        raise OAuthCredentialArtifactError(
            "OAuth artifact must contain exactly " + OAUTH_CIPHERTEXT_PATH.as_posix()
        )
    source = root.joinpath(*OAUTH_CIPHERTEXT_PATH.parts)
    ciphertext = source.read_bytes()
    if not ciphertext:
        raise OAuthCredentialArtifactError("OAuth ciphertext artifact must not be empty")
    if content_hash(ciphertext) != expected_sha256:
        raise OAuthCredentialArtifactError("OAuth ciphertext artifact digest mismatch")

    checkout = repository_root.resolve(strict=True)
    destination = checkout.joinpath(*OAUTH_CIPHERTEXT_PATH.parts)
    current = checkout
    for part in OAUTH_CIPHERTEXT_PATH.parent.parts:
        current /= part
        if current.is_symlink():
            raise OAuthCredentialArtifactError(
                "OAuth ciphertext destination must not traverse a symlink"
            )
        if current.exists() and not current.is_dir():
            raise OAuthCredentialArtifactError(
                "OAuth ciphertext destination parent must be a directory"
            )
        current.mkdir(exist_ok=True)
    if destination.is_symlink():
        raise OAuthCredentialArtifactError("OAuth ciphertext destination must not be a symlink")
    atomic_write_bytes(destination, ciphertext, allowed_root=checkout)
    return destination


__all__ = [
    "OAUTH_CIPHERTEXT_PATH",
    "OAuthCredentialArtifactError",
    "apply_oauth_ciphertext_artifact",
]

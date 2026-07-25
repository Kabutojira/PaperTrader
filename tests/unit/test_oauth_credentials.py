from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from papertrader.oauth_credentials import (
    OAUTH_CIPHERTEXT_PATH,
    OAuthCredentialArtifactError,
    apply_oauth_ciphertext_artifact,
)
from papertrader.utils import content_hash

AGE = shutil.which("age")
AGE_KEYGEN = shutil.which("age-keygen")
HAS_AGE = AGE is not None and AGE_KEYGEN is not None
AUTH_FIXTURE = b'{"active_provider":"openai-codex","version":1}\n'
REFRESHED_AUTH_FIXTURE = b'{"active_provider":"openai-codex","refreshed":true,"version":1}\n'


def _age_identity(tmp_path: Path, name: str = "identity.agekey") -> tuple[Path, str]:
    assert AGE_KEYGEN is not None
    identity = tmp_path / name
    subprocess.run(
        [AGE_KEYGEN, "-o", str(identity)],
        check=True,
        capture_output=True,
        text=True,
    )
    recipient = subprocess.run(
        [AGE_KEYGEN, "-y", str(identity)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert recipient.startswith("age1")
    return identity, recipient


def _encrypt(plaintext: Path, recipient: str, ciphertext: Path) -> None:
    assert AGE is not None
    subprocess.run(
        [AGE, "--encrypt", "--recipient", recipient, "--output", ciphertext, plaintext],
        check=True,
        capture_output=True,
        text=True,
    )


def _decrypt(ciphertext: Path, identity: Path, plaintext: Path) -> subprocess.CompletedProcess[str]:
    assert AGE is not None
    return subprocess.run(
        [AGE, "--decrypt", "--identity", identity, "--output", plaintext, ciphertext],
        check=False,
        capture_output=True,
        text=True,
    )


def _artifact(root: Path, ciphertext: bytes = b"age-encryption.org/v1\nfixture\n") -> Path:
    path = root.joinpath(*OAUTH_CIPHERTEXT_PATH.parts)
    path.parent.mkdir(parents=True)
    path.write_bytes(ciphertext)
    return path


def test_exact_ciphertext_artifact_is_validated_and_applied(
    sandbox_repository: Path,
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "artifact"
    source = _artifact(artifact_root)

    destination = apply_oauth_ciphertext_artifact(
        sandbox_repository,
        artifact_root,
        expected_sha256=content_hash(source.read_bytes()),
    )

    assert (
        destination.relative_to(sandbox_repository).as_posix() == OAUTH_CIPHERTEXT_PATH.as_posix()
    )
    assert destination.read_bytes() == source.read_bytes()
    assert not any(path.name == "auth.json" for path in artifact_root.rglob("*"))
    assert not any(path.suffix in {".agekey", ".key"} for path in artifact_root.rglob("*"))


@pytest.mark.parametrize("mutation", ["extra", "empty", "digest"])
def test_ciphertext_artifact_fails_closed(
    sandbox_repository: Path,
    tmp_path: Path,
    mutation: str,
) -> None:
    artifact_root = tmp_path / "artifact"
    source = _artifact(artifact_root)
    digest = content_hash(source.read_bytes())
    if mutation == "extra":
        (artifact_root / "auth.json").write_text("{}", encoding="utf-8")
    elif mutation == "empty":
        source.write_bytes(b"")
        digest = content_hash(b"")
    else:
        digest = "0" * 64

    with pytest.raises(OAuthCredentialArtifactError):
        apply_oauth_ciphertext_artifact(
            sandbox_repository,
            artifact_root,
            expected_sha256=digest,
        )


def test_ciphertext_artifact_rejects_a_symlink(
    sandbox_repository: Path,
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "artifact"
    source = _artifact(artifact_root)
    source.unlink()
    source.symlink_to(tmp_path / "outside.age")

    with pytest.raises(OAuthCredentialArtifactError, match="symlinks"):
        apply_oauth_ciphertext_artifact(
            sandbox_repository,
            artifact_root,
            expected_sha256="0" * 64,
        )


def test_only_ciphertext_enters_git_staging(
    sandbox_repository: Path,
    tmp_path: Path,
) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=sandbox_repository, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=sandbox_repository, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=sandbox_repository,
        check=True,
    )
    subprocess.run(["git", "add", "--all"], cwd=sandbox_repository, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=sandbox_repository,
        check=True,
        capture_output=True,
    )
    artifact_root = tmp_path / "artifact"
    source = _artifact(artifact_root)
    destination = apply_oauth_ciphertext_artifact(
        sandbox_repository,
        artifact_root,
        expected_sha256=content_hash(source.read_bytes()),
    )
    subprocess.run(["git", "add", "--", destination], cwd=sandbox_repository, check=True)
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=sandbox_repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    assert staged == [OAUTH_CIPHERTEXT_PATH.as_posix()]
    assert not (sandbox_repository / ".papertrader" / "credentials" / "auth.json").exists()
    assert not any(
        path.suffix in {".agekey", ".key"}
        for path in (sandbox_repository / ".papertrader").rglob("*")
    )


@pytest.mark.skipif(not HAS_AGE, reason="age and age-keygen are required")
def test_disposable_age_fixture_round_trip_and_failure_modes(tmp_path: Path) -> None:
    identity, recipient = _age_identity(tmp_path)
    wrong_identity, _ = _age_identity(tmp_path, "wrong.agekey")
    original = tmp_path / "auth.json"
    original.write_bytes(AUTH_FIXTURE)
    ciphertext = tmp_path / "auth.json.age"
    _encrypt(original, recipient, ciphertext)

    restored = tmp_path / "restored.json"
    assert _decrypt(ciphertext, identity, restored).returncode == 0
    assert restored.read_bytes() == AUTH_FIXTURE

    invalid = tmp_path / "invalid.age"
    invalid.write_bytes(b"not age ciphertext")
    assert _decrypt(invalid, identity, tmp_path / "invalid.json").returncode != 0
    assert _decrypt(ciphertext, wrong_identity, tmp_path / "wrong.json").returncode != 0


@pytest.mark.skipif(not HAS_AGE, reason="age and age-keygen are required")
def test_unchanged_plaintext_keeps_ciphertext_and_refresh_round_trips(tmp_path: Path) -> None:
    identity, recipient = _age_identity(tmp_path)
    before = tmp_path / "before.json"
    auth = tmp_path / "auth.json"
    before.write_bytes(AUTH_FIXTURE)
    auth.write_bytes(AUTH_FIXTURE)
    ciphertext = tmp_path / "auth.json.age"
    _encrypt(auth, recipient, ciphertext)
    initial_ciphertext = ciphertext.read_bytes()

    unchanged = subprocess.run(["cmp", "-s", before, auth], check=False).returncode == 0
    if not unchanged:
        _encrypt(auth, recipient, ciphertext)
    assert unchanged is True
    assert ciphertext.read_bytes() == initial_ciphertext

    auth.write_bytes(REFRESHED_AUTH_FIXTURE)
    assert subprocess.run(["cmp", "-s", before, auth], check=False).returncode != 0
    refreshed_ciphertext = tmp_path / "refreshed.json.age"
    _encrypt(auth, recipient, refreshed_ciphertext)
    assert refreshed_ciphertext.read_bytes() != initial_ciphertext
    verified = tmp_path / "verified.json"
    assert _decrypt(refreshed_ciphertext, identity, verified).returncode == 0
    assert verified.read_bytes() == REFRESHED_AUTH_FIXTURE

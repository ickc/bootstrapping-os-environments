"""Tests for the conda lock pointer (bsos.installers._locks) — no network."""

import hashlib
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from bsos.installers._locks import (
    LockChecksumError,
    LockPointer,
    LockPointerError,
    fetch_lock,
    format_pointer,
    parse_pointer,
    read_pointer,
)

URL = "https://github.com/owner/repo/releases/download/conda-2026.11.16"


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _pointer(**locks: bytes) -> LockPointer:
    return LockPointer("conda-2026.11.16", URL, {f"{name}-lock.yml": _digest(c) for name, c in locks.items()})


def test_round_trip_is_sorted_and_lossless() -> None:
    pointer = _pointer(system=b"s", py311=b"p", jupyterlab=b"j")
    text = format_pointer(pointer)
    assert parse_pointer(text) == pointer
    body = [line for line in text.splitlines() if not line.startswith("#")]
    assert [line.split("  ")[1] for line in body] == ["jupyterlab-lock.yml", "py311-lock.yml", "system-lock.yml"]
    assert "# tag: conda-2026.11.16" in text.splitlines()
    assert f"# url: {URL}" in text.splitlines()


def test_body_is_sha256sum_check_compatible(tmp_path: Path) -> None:
    """`sha256sum -c` (GNU) skips the comment lines and checks every entry."""
    for name, content in {"system": b"s\n", "py311": b"p\n"}.items():
        (tmp_path / f"{name}-lock.yml").write_bytes(content)
    (tmp_path / "locks.sha256").write_text(format_pointer(_pointer(system=b"s\n", py311=b"p\n")))
    try:
        result = subprocess.run(
            ["sha256sum", "--strict", "-c", "locks.sha256"], cwd=tmp_path, capture_output=True, text=True
        )
    except FileNotFoundError:
        pytest.skip("no GNU sha256sum")
    assert result.returncode == 0, result.stdout + result.stderr


def test_bash_tools_read_the_pointer(tmp_path: Path) -> None:
    """What bootstrap.sh and the smoke test do: sed for the URL, awk for an entry."""
    path = tmp_path / "locks.sha256"
    path.write_text(format_pointer(_pointer(system=b"s", py311=b"p")))
    url = subprocess.run(["sed", "-n", "s/^# url: //p", str(path)], capture_output=True, text=True, check=True)
    sha = subprocess.run(
        ["awk", '$2 == "system-lock.yml" { print $1 }', str(path)], capture_output=True, text=True, check=True
    )
    assert url.stdout.strip() == URL
    assert sha.stdout.strip() == _digest(b"s")


@pytest.mark.parametrize(
    "text, message",
    [
        (f"# url: {URL}\n{'0' * 64}  system-lock.yml\n", "missing '# tag"),
        (f"# tag: t\n{'0' * 64}  system-lock.yml\n", "missing '# url"),
        (f"# tag: t\n# url: {URL}\n", "no lock entries"),
        (f"# tag: t\n# url: {URL}\n{'0' * 64} system-lock.yml\n", "not '<sha256>"),
        (f"# tag: t\n# url: {URL}\n{'0' * 63}  system-lock.yml\n", "not '<sha256>"),
        (f"# tag: t\n# url: {URL}\n{'0' * 64}  system.yml\n", "not '<sha256>"),
        (f"# tag: t\n# url: {URL}\n{'0' * 64}  a-lock.yml\n{'1' * 64}  a-lock.yml\n", "duplicate"),
    ],
)
def test_malformed_pointer_is_rejected(text: str, message: str) -> None:
    with pytest.raises(LockPointerError, match=message):
        parse_pointer(text)


def test_missing_entry_names_what_is_pinned() -> None:
    with pytest.raises(LockPointerError, match="has no py39-lock.yml; it pins: system-lock.yml"):
        _pointer(system=b"s").expected("py39-lock.yml")


def test_read_pointer_names_the_file_in_errors(tmp_path: Path) -> None:
    path = tmp_path / "locks.sha256"
    path.write_text("garbage\n")
    with pytest.raises(LockPointerError, match=str(path)):
        read_pointer(path)


def _serve(content: bytes):
    """A stand-in for download_file that writes *content* and records the URL."""
    urls = []

    def fake_download(url: str, dest: Path) -> None:
        urls.append(url)
        Path(dest).write_bytes(content)

    return fake_download, urls


def test_fetch_lock_downloads_from_the_release_and_keeps_the_name(tmp_path: Path) -> None:
    fake, urls = _serve(b"lock\n")
    with patch("bsos.installers._locks.download_file", side_effect=fake):
        path = fetch_lock(_pointer(system=b"lock\n"), "system-lock.yml", tmp_path)
    assert urls == [f"{URL}/system-lock.yml"]
    assert path == tmp_path / "system-lock.yml"
    assert path.read_bytes() == b"lock\n"


def test_fetch_lock_checksum_mismatch_fails_hard_and_leaves_nothing(tmp_path: Path) -> None:
    fake, _ = _serve(b"tampered\n")
    with patch("bsos.installers._locks.download_file", side_effect=fake):
        with pytest.raises(LockChecksumError, match="refusing to use it"):
            fetch_lock(_pointer(system=b"lock\n"), "system-lock.yml", tmp_path)
    assert not (tmp_path / "system-lock.yml").exists()

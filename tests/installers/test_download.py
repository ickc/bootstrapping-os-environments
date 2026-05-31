"""Tests for installer download and extraction helpers."""

import io
import tarfile
import urllib.error
from pathlib import Path
from unittest.mock import patch

import pytest

from bsos.installers._download import _extract_tar_legacy_safe, _open_url


def _tarfile_with_members(*members: tuple[str, bytes]) -> io.BytesIO:
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as tar:
        for name, payload in members:
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
    data.seek(0)
    return data


def test_open_url_retries_transient_http_error() -> None:
    response = object()
    error = urllib.error.HTTPError("https://example.invalid", 502, "Bad Gateway", hdrs=None, fp=None)

    with (
        patch("bsos.installers._download.urllib.request.urlopen", side_effect=[error, response]) as urlopen,
        patch("bsos.installers._download.time.sleep") as sleep,
    ):
        assert _open_url("https://example.invalid") is response

    assert urlopen.call_count == 2
    sleep.assert_called_once_with(1)


def test_open_url_retries_read_timeout() -> None:
    # A read timeout while following a redirect surfaces as a bare TimeoutError
    # (not wrapped in URLError); it must still be retried.
    response = object()

    with (
        patch(
            "bsos.installers._download.urllib.request.urlopen", side_effect=[TimeoutError("read timed out"), response]
        ) as urlopen,
        patch("bsos.installers._download.time.sleep") as sleep,
    ):
        assert _open_url("https://example.invalid") is response

    assert urlopen.call_count == 2
    sleep.assert_called_once_with(1)


def test_open_url_does_not_retry_non_transient_http_error() -> None:
    error = urllib.error.HTTPError("https://example.invalid", 404, "Not Found", hdrs=None, fp=None)

    with (
        patch("bsos.installers._download.urllib.request.urlopen", side_effect=error) as urlopen,
        patch("bsos.installers._download.time.sleep") as sleep,
        pytest.raises(urllib.error.HTTPError),
    ):
        _open_url("https://example.invalid")

    assert urlopen.call_count == 1
    sleep.assert_not_called()


def test_legacy_tar_extracts_safe_member(tmp_path: Path) -> None:
    data = _tarfile_with_members(("bin/tool", b"ok"))

    with tarfile.open(fileobj=data, mode="r:*") as tar:
        _extract_tar_legacy_safe(tar, tmp_path)

    assert (tmp_path / "bin" / "tool").read_bytes() == b"ok"


def test_legacy_tar_rejects_parent_traversal(tmp_path: Path) -> None:
    data = _tarfile_with_members(("../escaped", b"bad"))

    with tarfile.open(fileobj=data, mode="r:*") as tar:
        with pytest.raises(RuntimeError, match="Unsafe tar member path"):
            _extract_tar_legacy_safe(tar, tmp_path)

    assert not (tmp_path.parent / "escaped").exists()


def test_legacy_tar_rejects_absolute_symlink(tmp_path: Path) -> None:
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as tar:
        info = tarfile.TarInfo("bin/tool")
        info.type = tarfile.SYMTYPE
        info.linkname = "/tmp/tool"
        tar.addfile(info)
    data.seek(0)

    with tarfile.open(fileobj=data, mode="r:*") as tar:
        with pytest.raises(RuntimeError, match="Unsafe tar link target"):
            _extract_tar_legacy_safe(tar, tmp_path)

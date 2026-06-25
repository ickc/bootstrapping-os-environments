"""Tests for installer download and extraction helpers."""

import io
import tarfile
import urllib.error
from pathlib import Path
from unittest.mock import call, patch

import pytest

import bsos.installers._download as download_mod
from bsos.installers._download import (
    _extract_tar_legacy_safe,
    _open_url,
    download_file,
    download_to_tempdir,
    resolve_latest_github_tag,
)


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
        patch("bsos.installers._download.urllib.request.urlopen", side_effect=[error, error, response]) as urlopen,
        patch("bsos.installers._download.time.sleep") as sleep,
    ):
        assert _open_url("https://example.invalid") is response

    assert urlopen.call_count == 3
    assert sleep.call_args_list == [call(1), call(2)]


def test_open_url_retries_read_timeout() -> None:
    # A read timeout while following a redirect surfaces as a bare TimeoutError
    # (not wrapped in URLError); it must still be retried.
    response = object()

    with (
        patch(
            "bsos.installers._download.urllib.request.urlopen",
            side_effect=[TimeoutError("read timed out"), TimeoutError("read timed out"), response],
        ) as urlopen,
        patch("bsos.installers._download.time.sleep") as sleep,
    ):
        assert _open_url("https://example.invalid") is response

    assert urlopen.call_count == 3
    assert sleep.call_args_list == [call(1), call(2)]


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


class _FailingResponse:
    url = "https://example.invalid/file"

    def __init__(self) -> None:
        self._sent_partial = False

    def __enter__(self) -> "_FailingResponse":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        if not self._sent_partial:
            self._sent_partial = True
            return b"partial"
        raise TimeoutError("read timed out")


def test_download_file_removes_partial_destination_on_read_failure(tmp_path: Path) -> None:
    dest = tmp_path / "tool"

    with (
        patch("bsos.installers._download._open_url", return_value=_FailingResponse()),
        pytest.raises(TimeoutError, match="read timed out"),
    ):
        download_file("https://example.invalid/tool", dest)

    assert not dest.exists()
    assert list(tmp_path.iterdir()) == []


def test_download_to_tempdir_cleans_up_failed_extract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    leaked = tmp_path / "bsos-leak"

    def fake_mkdtemp(prefix: str) -> str:
        leaked.mkdir()
        return str(leaked)

    def fail_extract(url: str, dest: Path) -> None:
        (dest / "partial").write_text("partial")
        raise RuntimeError("boom")

    monkeypatch.setattr(download_mod.tempfile, "mkdtemp", fake_mkdtemp)
    monkeypatch.setattr(download_mod, "download_and_extract_tar", fail_extract)

    with pytest.raises(RuntimeError, match="boom"):
        download_to_tempdir("https://example.invalid/archive.tar.gz")

    assert not leaked.exists()


class _RedirectResponse:
    def __init__(self, url: str) -> None:
        self.url = url

    def __enter__(self) -> "_RedirectResponse":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None


def test_resolve_latest_github_tag_requires_tag_url() -> None:
    with (
        patch("bsos.installers._download._open_url", return_value=_RedirectResponse("https://github.com/o/r/releases")),
        pytest.raises(RuntimeError, match="not a release tag URL"),
    ):
        resolve_latest_github_tag("o", "r")


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

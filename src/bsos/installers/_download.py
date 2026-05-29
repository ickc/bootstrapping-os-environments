"""Download and archive extraction helpers — stdlib only."""

import io
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Union

from bsos import __version__

_USER_AGENT = f"bsos-installer/{__version__}"

PathLike = Union[str, Path]


def _open_url(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    return urllib.request.urlopen(req)  # noqa: S310 — URL is from our own dispatch table


def _extract_tar(data: io.BytesIO, dest_dir: Path) -> None:
    with tarfile.open(fileobj=data, mode="r:*") as tar:
        # filter="data" (PEP 706) rejects absolute/parent paths and strips
        # unsafe mode bits (CVE-2007-4559). Fall back on Pythons that predate it.
        try:
            tar.extractall(dest_dir, filter="data")
        except TypeError:
            tar.extractall(dest_dir)


def download_file(url: str, dest: PathLike) -> None:
    """Download *url* to a local file at *dest*."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with _open_url(url) as resp, dest.open("wb") as f:
        shutil.copyfileobj(resp, f)


def download_and_extract_tar(url: str, dest_dir: PathLike) -> None:
    """Download a tar archive and extract into *dest_dir*."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    with _open_url(url) as resp:
        data = io.BytesIO(resp.read())
    _extract_tar(data, dest_dir)


def download_and_extract_zip(url: str, dest_dir: PathLike) -> None:
    """Download a zip archive and extract into *dest_dir*."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    with _open_url(url) as resp:
        data = io.BytesIO(resp.read())
    with zipfile.ZipFile(data) as zf:
        zf.extractall(dest_dir)


def download_to_tempdir(url: str, extract: str = "tar") -> Path:
    """Download and extract an archive into a fresh temp directory.

    Returns the temp directory path (caller is responsible for cleanup).
    *extract* is ``"tar"`` or ``"zip"``.
    """
    tmp = Path(tempfile.mkdtemp(prefix="bsos-"))
    if extract == "tar":
        download_and_extract_tar(url, tmp)
    elif extract == "zip":
        download_and_extract_zip(url, tmp)
    else:
        raise ValueError(f"Unknown extract format: {extract}")
    return tmp

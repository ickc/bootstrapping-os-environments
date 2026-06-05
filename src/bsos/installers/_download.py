"""Download and archive extraction helpers — stdlib only."""

import io
import os
import shutil
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import warnings
import zipfile
from pathlib import Path
from typing import Any, Union

from bsos import __version__

_USER_AGENT = f"bsos-installer/{__version__}"
_OPEN_URL_ATTEMPTS = 3
_OPEN_URL_TIMEOUT = 60
_TRANSIENT_HTTP_STATUS = {408, 429, 500, 502, 503, 504}

PathLike = Union[str, Path]


def _open_url(url: str) -> Any:
    for attempt in range(_OPEN_URL_ATTEMPTS):
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        try:
            return urllib.request.urlopen(req, timeout=_OPEN_URL_TIMEOUT)  # noqa: S310 — URL is from our dispatch table
        except urllib.error.HTTPError as exc:
            if exc.code not in _TRANSIENT_HTTP_STATUS or attempt == _OPEN_URL_ATTEMPTS - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            # URLError covers connection-phase failures; a read timeout while
            # reading the response (e.g. following the /releases/latest
            # redirect) surfaces as a bare TimeoutError, not wrapped in
            # URLError. Both are transient and worth retrying.
            if attempt == _OPEN_URL_ATTEMPTS - 1:
                raise
        time.sleep(2**attempt)
    raise RuntimeError(f"Could not open URL after retries: {url}")


def _extract_tar(data: io.BytesIO, dest_dir: Path) -> None:
    with tarfile.open(fileobj=data, mode="r:*") as tar:
        # filter="data" (PEP 706) rejects absolute/parent paths and strips
        # unsafe mode bits (CVE-2007-4559). Use an explicit validator on
        # Pythons that predate it instead of the unsafe legacy extractall path.
        try:
            tar.extractall(dest_dir, filter="data")
        except TypeError:
            _extract_tar_legacy_safe(tar, dest_dir)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _extract_tar_legacy_safe(tar: tarfile.TarFile, dest_dir: Path) -> None:
    """Extract tar members safely on Pythons without tarfile data filters."""
    root = dest_dir.resolve()
    members = []
    for member in tar.getmembers():
        target = (dest_dir / member.name).resolve()
        if not _is_relative_to(target, root):
            raise RuntimeError(f"Unsafe tar member path: {member.name!r}")
        if member.isdev():
            raise RuntimeError(f"Unsafe tar member type: {member.name!r}")
        if member.issym() or member.islnk():
            link = Path(member.linkname)
            link_target = (target.parent / link).resolve() if not link.is_absolute() else link.resolve()
            if not _is_relative_to(link_target, root):
                raise RuntimeError(f"Unsafe tar link target: {member.name!r} -> {member.linkname!r}")
        member.mode &= 0o755
        members.append(member)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        tar.extractall(dest_dir, members=members)


def download_file(url: str, dest: PathLike) -> None:
    """Download *url* to a local file at *dest*."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{dest.name}.", suffix=".tmp", dir=dest.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f, _open_url(url) as resp:
            shutil.copyfileobj(resp, f)
        tmp.replace(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


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


def resolve_latest_github_tag(owner: str, repo: str) -> str:
    """Return the latest release tag for a GitHub repo without calling the GitHub API.

    Follows the /releases/latest redirect URL; the final URL ends with /tag/<tagname>.
    Avoids the GitHub API (60 req/hour unauthenticated limit).
    """
    url = f"https://github.com/{owner}/{repo}/releases/latest"
    with _open_url(url) as resp:
        final_url = str(resp.url).rstrip("/")
    if "/tag/" not in final_url:
        raise RuntimeError(
            f"Could not resolve latest release tag for {owner}/{repo}: "
            f"{url} ended at {final_url!r}, not a release tag URL"
        )
    tag = final_url.rsplit("/tag/", 1)[1].split("/", 1)[0]
    if not tag or tag in {"latest", "releases"}:
        raise RuntimeError(f"Could not resolve latest release tag for {owner}/{repo}")
    return tag


def download_to_tempdir(url: str, extract: str = "tar") -> Path:
    """Download and extract an archive into a fresh temp directory.

    Returns the temp directory path (caller is responsible for cleanup).
    *extract* is ``"tar"`` or ``"zip"``.
    """
    tmp = Path(tempfile.mkdtemp(prefix="bsos-"))
    try:
        if extract == "tar":
            download_and_extract_tar(url, tmp)
        elif extract == "zip":
            download_and_extract_zip(url, tmp)
        else:
            raise ValueError(f"Unknown extract format: {extract}")
        return tmp
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise

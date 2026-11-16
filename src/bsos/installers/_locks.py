"""The conda lock pointer: which release holds the pinned conda-lock files.

The generated ``conda/<name>-lock.yml`` files are not kept in git — each
refresh is a diff of 10,000+ lines — but published as assets of a dated
GitHub Release.  Git keeps ``conda/locks.sha256`` instead: the release tag,
its download URL and the sha256 of every lock.  An envoy commit therefore
still pins the exact environments, a download is verified against a checksum
that is itself in git, and a rollback is a ``git revert`` of the pointer.

The format is trivial on purpose, so that ``bootstrap.sh`` can read it with
``sed``/``awk`` before any Python exists.  The body is ``sha256sum -c``
compatible (GNU ``sha256sum`` skips the ``#`` lines)::

    # conda-lock files pinned by this commit, published as release assets.
    # tag: conda-2026.11.16
    # url: https://github.com/ickc/bootstrapping-os-environments/releases/download/conda-2026.11.16
    08109170…  jupyterlab-lock.yml
    a598fd71…  py311-lock.yml

Entries are sorted by name, one per conda-lock file.  The URL is in the file,
rather than derived from the repository, so the pointer alone says where to
fetch from — in a fork too.

stdlib only: compiled into the standalone installer scripts.
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from bsos.installers._download import download_file

POINTER_NAME = "locks.sha256"

# The pointer on main, for a script run without a clone (``curl | python3``).
REMOTE_POINTER_URL = "https://raw.githubusercontent.com/ickc/bootstrapping-os-environments/main/conda/locks.sha256"

_DESCRIPTION = "# conda-lock files pinned by this commit, published as release assets."
_HEADER = re.compile(r"^# (tag|url): (\S+)$")
_ENTRY = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._-]+-lock\.yml)$")


class LockPointerError(RuntimeError):
    """The pointer is malformed, or has no entry for the lock asked for."""


class LockChecksumError(RuntimeError):
    """A downloaded lock does not match the sha256 the pointer records."""


@dataclass(frozen=True)
class LockPointer:
    tag: str
    url: str
    sha256: Dict[str, str]  # conda-lock filename -> hex digest

    def expected(self, filename: str) -> str:
        """The pinned sha256 of *filename*, or :class:`LockPointerError`."""
        digest = self.sha256.get(filename)
        if digest is None:
            known = ", ".join(sorted(self.sha256)) or "none"
            raise LockPointerError(f"the lock pointer (release {self.tag}) has no {filename}; it pins: {known}")
        return digest

    def asset_url(self, filename: str) -> str:
        return f"{self.url.rstrip('/')}/{filename}"


def parse_pointer(text: str, source: str = POINTER_NAME) -> LockPointer:
    """Parse pointer *text*; *source* names it in error messages."""
    headers: Dict[str, str] = {}
    entries: Dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        if line.startswith("#"):
            header = _HEADER.match(line)
            if header:
                headers[header.group(1)] = header.group(2)
            continue
        entry = _ENTRY.match(line)
        if entry is None:
            raise LockPointerError(f"{source}:{number}: not '<sha256>  <name>-lock.yml': {line!r}")
        digest, name = entry.groups()
        if name in entries:
            raise LockPointerError(f"{source}:{number}: duplicate entry for {name}")
        entries[name] = digest
    for key in ("tag", "url"):
        if key not in headers:
            raise LockPointerError(f"{source}: missing '# {key}: …' header")
    if not entries:
        raise LockPointerError(f"{source}: no lock entries")
    return LockPointer(headers["tag"], headers["url"], entries)


def format_pointer(pointer: LockPointer) -> str:
    """Render *pointer*; :func:`parse_pointer` reads it back unchanged."""
    lines = [_DESCRIPTION, f"# tag: {pointer.tag}", f"# url: {pointer.url}"]
    lines += [f"{pointer.sha256[name]}  {name}" for name in sorted(pointer.sha256)]
    return "\n".join(lines) + "\n"


def read_pointer(path: Path) -> LockPointer:
    return parse_pointer(path.read_text(encoding="utf-8"), str(path))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_lock(pointer: LockPointer, filename: str, dest_dir: Path) -> Path:
    """Download *filename* from the pointer's release into *dest_dir* and verify it.

    The local name stays *filename*: micromamba and mamba recognize a
    conda-lock file by its ``-lock.yml`` suffix, and misnamed they silently
    create an empty env.  A checksum mismatch removes the file and raises
    :class:`LockChecksumError` — never install a lock the pointer does not pin.
    """
    expected = pointer.expected(filename)
    dest = dest_dir / filename
    url = pointer.asset_url(filename)
    download_file(url, dest)
    actual = sha256_file(dest)
    if actual != expected:
        dest.unlink()
        raise LockChecksumError(f"{url} has sha256 {actual}, but the lock pointer pins {expected}; refusing to use it")
    return dest

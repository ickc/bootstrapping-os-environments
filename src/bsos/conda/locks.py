"""Publish side of the conda lock pointer (``conda/locks.sha256``).

``conda-generate`` writes the conda-lock files to ``conda/`` (gitignored);
this module decides whether they need a new release and, if so, writes the
pointer that names it and stages the files to attach. The format and the
consumer side live in :mod:`bsos.installers._locks`, which the stdlib-only
installers compile in.

Used by the ``conda-generate`` workflow::

    pixi run conda-locks-pointer -- --repo owner/name   # prints the new tag, or nothing
    pixi run conda-locks-stage -- DIR                   # the assets to attach, flat
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

import defopt

from bsos.installers._locks import POINTER_NAME, LockPointer, format_pointer, read_pointer, sha256_file

DEFAULT_REPO = "ickc/bootstrapping-os-environments"
TAG_PREFIX = "conda-"


def lock_checksums(conda_dir: Path) -> dict[str, str]:
    """sha256 of every ``<conda_dir>/<name>-lock.yml``, keyed by filename."""
    return {path.name: sha256_file(path) for path in sorted(conda_dir.glob("*-lock.yml"))}


def choose_tag(today: date, existing: Iterable[str]) -> str:
    """``conda-YYYY.MM.DD``, or with ``.2``, ``.3``, … when that tag is taken.

    Tags are unique and sort by date; a second release on one day (a
    hand-started run after the weekly one, a CSV edit landing) gets a suffix.
    """
    taken = set(existing)
    base = f"{TAG_PREFIX}{today:%Y.%m.%d}"
    if base not in taken:
        return base
    n = 2
    while f"{base}.{n}" in taken:
        n += 1
    return f"{base}.{n}"


def download_base(repo: str, tag: str) -> str:
    """A release's asset download base: a plain redirect, no API call."""
    return f"https://github.com/{repo}/releases/download/{tag}"


def remote_tags(remote: str = "origin") -> set[str]:
    """The ``conda-*`` tags on *remote*, release or not."""
    out = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", remote, f"refs/tags/{TAG_PREFIX}*"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return {line.split("refs/tags/", 1)[1] for line in out.splitlines() if "refs/tags/" in line}


def update_pointer(conda_dir: Path, repo: str, today: date, existing: Iterable[str]) -> str | None:
    """Point ``conda_dir/locks.sha256`` at a new release if the locks changed.

    Returns the new tag, or ``None`` when the generated locks are exactly the
    ones the pointer already pins — then nothing needs publishing and the
    pointer is left byte-for-byte alone.
    """
    checksums = lock_checksums(conda_dir)
    if not checksums:
        raise FileNotFoundError(f"no *-lock.yml in {conda_dir}; run `pixi run conda-generate` first")
    path = conda_dir / POINTER_NAME
    if path.is_file() and read_pointer(path).sha256 == checksums:
        return None
    tag = choose_tag(today, existing)
    path.write_text(format_pointer(LockPointer(tag, download_base(repo, tag), checksums)), encoding="utf-8")
    return tag


def stage_assets(conda_dir: Path, out: Path) -> list[Path]:
    """Copy the release assets into *out* under flat, distinct names.

    Every ``<name>-lock.yml`` as is, and each ``<stem>/pixi.lock`` as
    ``<stem>-pixi.lock``. The pixi locks are for provenance only — the pointer
    does not list them and nothing downloads them.
    """
    out.mkdir(parents=True, exist_ok=True)
    sources = {path.name: path for path in sorted(conda_dir.glob("*-lock.yml"))}
    sources.update({f"{path.parent.name}-pixi.lock": path for path in sorted(conda_dir.glob("*/pixi.lock"))})
    staged = []
    for name, source in sources.items():
        dest = out / name
        shutil.copyfile(source, dest)
        staged.append(dest)
    return staged


def pointer(*, conda_dir: Path = Path("conda"), repo: str = DEFAULT_REPO, remote: str = "origin") -> None:
    """Write conda/locks.sha256 for a new release if the locks changed; print its tag.

    Prints nothing (and leaves the pointer alone) when the generated locks
    are already the pinned ones. The date is today's in UTC.

    :param conda_dir: directory holding the generated ``*-lock.yml``
    :param repo: GitHub owner/name the release is published on
    :param remote: git remote whose tags are checked for a collision
    """
    tag = update_pointer(conda_dir, repo, datetime.now(timezone.utc).date(), remote_tags(remote))
    if tag is not None:
        print(tag)


def stage(out: Path, *, conda_dir: Path = Path("conda")) -> None:
    """Copy the release assets into OUT (flat names), one path per line.

    :param out: directory to copy into
    :param conda_dir: directory holding the generated files
    """
    for path in stage_assets(conda_dir, out):
        print(path)


def cli() -> None:
    defopt.run([pointer, stage])


if __name__ == "__main__":
    cli()

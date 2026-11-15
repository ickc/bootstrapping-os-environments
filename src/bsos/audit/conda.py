"""Checks on the pinned conda environments.

Everything here is computed from two things the generator already has: the
committed ``conda/<env>-lock.yml`` files and the anaconda.org package JSON
(read through the same cache as ``conda-generate``, so right after a
generate run this makes no network requests).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping

import tomlkit
import yaml
from rattler import Version

from bsos.audit.report import Finding
from bsos.conda.web_api import PRERELEASE, CondaPackages

#: A lock whose newest pinned build is older than this has stopped being
#: refreshed (weekly bot + 7-day cooldown, plus slack for a missed week).
STALE_LOCK_DAYS = 28
#: A pinned build older than this predates most of what it links against.
OLD_BUILD_DAYS = 3 * 365
#: How long a package gets to publish a build for a new Python.
PYTHON_GRACE_DAYS = 365

Files = list[dict[str, Any]]
"""The ``files`` list of an anaconda.org package record."""


@dataclass(frozen=True)
class Locked:
    version: str
    url: str


LockIndex = dict[str, dict[str, Locked]]
"""``{package name: {platform: Locked}}`` for one conda-lock file."""


@dataclass(frozen=True)
class Pin:
    """One package as pinned in one environment on one platform."""

    env: str
    platform: str
    version: str
    built: datetime | None  # when the pinned build was uploaded; None if the API no longer lists it


def python_release(minor: int) -> date:
    """Release date of Python 3.*minor* — every October since 3.9 (PEP 602)."""
    return date(2011 + minor, 10, 1)


def load_lock(path: Path) -> LockIndex:
    with path.open(encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.CSafeLoader)
    index: LockIndex = {}
    for package in data["package"]:
        index.setdefault(package["name"], {})[package["platform"]] = Locked(str(package["version"]), package["url"])
    return index


@lru_cache(maxsize=None)
def load_tables(conda_dir: Path) -> dict[str, CondaPackages]:
    """Every ``conda/<stem>.csv`` with its package metadata, keyed by stem."""
    return {csv.stem: CondaPackages.read_csv(csv) for csv in sorted(conda_dir.glob("*.csv"))}


def _uploaded(file: Mapping[str, Any]) -> datetime:
    uploaded = datetime.fromisoformat(file["upload_time"])
    return uploaded if uploaded.tzinfo else uploaded.replace(tzinfo=timezone.utc)


def _newest(versions: Iterable[str]) -> str | None:
    best: tuple[Version, str] | None = None
    for version in versions:
        try:
            parsed = Version(version)
        except Exception:
            continue
        if best is None or parsed > best[0]:
            best = (parsed, version)
    return best[1] if best else None


def _older(a: str, b: str) -> bool:
    try:
        return bool(Version(a) < Version(b))
    except Exception:
        return False


def _pins(name: str, files: Files, locks: Mapping[str, LockIndex]) -> list[Pin]:
    by_basename = {file.get("basename"): file for file in files if file.get("upload_time")}
    pins = []
    for env, lock in locks.items():
        for platform, locked in lock.get(name, {}).items():
            file = by_basename.get("/".join(locked.url.split("/")[-2:]))
            pins.append(Pin(env, platform, locked.version, _uploaded(file) if file else None))
    return pins


def _newest_available(files: Files, platform: str, cutoff: datetime) -> str | None:
    """Newest stable version installable on *platform* that existed by *cutoff*.

    To the minute, not the day: the solver's cooldown cutoff is a moment, and
    a release uploaded later that same day was not there for it to pick.
    """
    return _newest(
        file["version"]
        for file in files
        if file.get("upload_time")
        and file["attrs"]["subdir"] in (platform, "noarch")
        and "main" in (file.get("labels") or ["main"])
        and _uploaded(file) <= cutoff
        and not PRERELEASE.search(file["version"])
    )


def _where(hits: Mapping[str, set[str]], pinned_on: Mapping[str, set[str]]) -> str:
    """Where a finding applies: ``py311, py312``, ``every environment``, or — when
    only some of the platforms a package is pinned on are affected —
    ``system on osx-64/osx-arm64``."""
    by_platforms: dict[tuple[str, ...], list[str]] = {}
    for env in sorted(hits):
        partial = () if hits[env] == pinned_on[env] else tuple(sorted(hits[env]))
        by_platforms.setdefault(partial, []).append(env)
    parts = []
    for platforms, envs in by_platforms.items():
        everywhere = len(pinned_on) > 1 and len(envs) == len(pinned_on)
        part = "every environment" if everywhere else ", ".join(envs)
        parts.append(f"{part} on {'/'.join(platforms)}" if platforms else part)
    return "; ".join(parts)


def audit_group(
    group: str,
    packages: Mapping[str, Files],
    locks: Mapping[str, LockIndex],
    *,
    pythons: Mapping[str, int],
    today: date,
) -> list[Finding]:
    """Audit the environments generated from one CSV.

    *packages* maps each active (not ignored) package to its anaconda.org
    files; *locks* maps environment name to its lock; *pythons* gives the
    Python minor version of the environments that pin one.
    """
    findings: list[Finding] = []
    pins = {name: _pins(name, files, locks) for name, files in packages.items()}

    # The solver takes the newest builds it is allowed to see, so the newest
    # pinned build dates the lock — no git history or timestamp file needed.
    newest_build = max((pin.built for group_pins in pins.values() for pin in group_pins if pin.built), default=None)
    lock_age = (today - newest_build.date()).days if newest_build is not None else 0
    if newest_build is not None and lock_age > STALE_LOCK_DAYS:
        findings.append(
            Finding(
                "stale-lock",
                f"conda/{group}",
                f"newest pinned build is from {newest_build.date()} ({lock_age} days ago; "
                f"limit {STALE_LOCK_DAYS}): the weekly regeneration is not landing",
            )
        )

    for name, files in packages.items():
        subject = f"{group}/{name}"
        if not pins[name]:
            findings.append(
                Finding(
                    "no-env",
                    subject,
                    f"active in {group}.csv but pinned in none of its environments "
                    f"({', '.join(sorted(locks))}): the generator found no supported platform and dropped it",
                )
            )
            continue

        pinned_on: dict[str, set[str]] = {}
        for pin in pins[name]:
            pinned_on.setdefault(pin.env, set()).add(pin.platform)

        # Missing from the environments of a Python that has been out a while,
        # though present for an older one: upstream stopped keeping up.
        present = {pythons[env]: env for env in pinned_on if env in pythons}
        if present:
            last = max(present)
            gap = sorted(
                (minor, env)
                for env, minor in pythons.items()
                if env not in pinned_on and minor > last and (today - python_release(minor)).days >= PYTHON_GRACE_DAYS
            )
            if gap:
                findings.append(
                    Finding(
                        "python-gap",
                        subject,
                        f"no build for Python {', '.join(f'3.{minor}' for minor, _ in gap)} "
                        f"(3.{gap[0][0]} came out {python_release(gap[0][0]):%Y-%m}); newest with one is 3.{last}",
                    )
                )

        # Pinned below a version the solver could have used: another pin, or
        # the package's own stale dependency bounds, is holding it back.
        if newest_build is not None:
            held: dict[tuple[str, str], dict[str, set[str]]] = {}
            for pin in pins[name]:
                available = _newest_available(files, pin.platform, newest_build)
                if available and _older(pin.version, available):
                    held.setdefault((pin.version, available), {}).setdefault(pin.env, set()).add(pin.platform)
            if held:
                findings.append(
                    Finding(
                        "held-back",
                        subject,
                        "; ".join(
                            f"{locked} pinned though {available} was available ({_where(hits, pinned_on)})"
                            for (locked, available), hits in sorted(held.items())
                        ),
                        action=False,
                    )
                )

        old: dict[tuple[str, date], dict[str, set[str]]] = {}
        for pin in pins[name]:
            if pin.built and (today - pin.built.date()).days > OLD_BUILD_DAYS:
                old.setdefault((pin.version, pin.built.date()), {}).setdefault(pin.env, set()).add(pin.platform)
        if old:
            findings.append(
                Finding(
                    "old-build",
                    subject,
                    "; ".join(
                        f"{version} built {built} ({_where(hits, pinned_on)})"
                        for (version, built), hits in sorted(old.items())
                    ),
                    action=False,
                )
            )
    return findings


def audit(conda_dir: Path, today: date) -> list[Finding]:
    """Audit every ``conda/<stem>.csv`` against the environments generated from it."""
    findings: list[Finding] = []
    for stem, table in load_tables(conda_dir).items():
        manifest = conda_dir / stem / "pixi.toml"
        if not manifest.is_file():
            raise FileNotFoundError(f"{manifest} not found; run `pixi run conda-generate` first")
        doc: dict[str, Any] = tomlkit.parse(manifest.read_text(encoding="utf-8")).unwrap()
        pythons: dict[str, int] = {}
        locks: dict[str, LockIndex] = {}
        for env in doc["environments"]:
            locks[env] = load_lock(conda_dir / f"{env}-lock.yml")
            spec = doc["feature"][env]["dependencies"].get("python")
            match = re.match(r"3\.(\d+)", spec) if isinstance(spec, str) else None
            if match:
                pythons[env] = int(match.group(1))
        packages = {package.name: package.data.get("files", []) for package in table.packages if not package.ignored}
        findings += audit_group(stem, packages, locks, pythons=pythons, today=today)
    return findings

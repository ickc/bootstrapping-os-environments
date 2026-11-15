"""Checks on the macOS lists under ``nix/``: Homebrew, the Mac App Store, and the flake lock.

Homebrew and Apple both curate abandonment themselves — a cask is deprecated
or disabled with a stated reason, an app is delisted — so these checks just
ask them.
"""

from __future__ import annotations

import asyncio
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from bsos.audit.report import Finding
from bsos.util.http import gather_limited, get_with_retry

_BREW_API = "https://formulae.brew.sh/api/{kind}/{name}.json"
_ITUNES_LOOKUP = "https://itunes.apple.com/lookup"
#: Storefronts searched before an app counts as unlisted. An app sold only
#: elsewhere, or delisted but still wanted (a purchased app stays downloadable
#: from the purchase history), shows up as a finding once; acknowledge it.
MAS_COUNTRIES = ("us", "gb")
#: nixpkgs security fixes arrive through the flake lock; the weekly flake-update
#: workflow bumps it, so an older pin means that has stopped landing.
STALE_FLAKE_DAYS = 60

_QUOTED = re.compile(r'^\s*"([^"]+)"\s*$', re.MULTILINE)
_MAS_APP = re.compile(r'^\s*"([^"]+)"\s*=\s*(\d+)\s*;', re.MULTILINE)


def quoted_names(path: Path) -> list[str]:
    """The entries of a nix list of strings (``brews.nix``, ``casks.nix``), skipping commented ones."""
    return _QUOTED.findall(path.read_text(encoding="utf-8"))


def mas_apps(path: Path) -> dict[str, int]:
    """``{app name: App Store id}`` from ``masApps.nix``."""
    return {name: int(app_id) for name, app_id in _MAS_APP.findall(path.read_text(encoding="utf-8"))}


def brew_finding(kind: str, name: str, info: dict[str, Any] | None) -> Finding | None:
    """Judge one cask/formula from its formulae.brew.sh record (``None``: not found)."""
    subject = f"{kind}/{name}"
    if info is None:
        return Finding("brew", subject, "no longer exists in Homebrew (removed or renamed)")
    for state, when, why in (
        ("disabled", "disable_date", "disable_reason"),
        ("deprecated", "deprecation_date", "deprecation_reason"),
    ):
        if info.get(state) or info.get(when):
            replacement = next((v for k, v in info.items() if "replacement" in k and v), None)
            return Finding(
                "brew",
                subject,
                f"{state} by Homebrew"
                + (f" as of {info[when]}" if info.get(when) else "")
                + (f": {info[why]}" if info.get(why) else "")
                + (f"; replacement: {replacement}" if replacement else ""),
            )
    return None


async def _audit_brew(client: httpx.AsyncClient, entries: list[tuple[str, str]]) -> list[Finding]:
    async def fetch(entry: tuple[str, str]) -> Finding | None:
        kind, name = entry
        response = await get_with_retry(client, _BREW_API.format(kind=kind, name=name))
        if response.status_code == 404:
            return brew_finding(kind, name, None)
        response.raise_for_status()
        return brew_finding(kind, name, response.json())

    return [finding for finding in await gather_limited(entries, fetch, concurrency=8) if finding]


async def _audit_mas(client: httpx.AsyncClient, apps: dict[str, int]) -> list[Finding]:
    missing = set(apps.values())
    for country in MAS_COUNTRIES:
        if not missing:
            break
        url = f"{_ITUNES_LOOKUP}?id={','.join(str(i) for i in sorted(missing))}&country={country}"
        response = await get_with_retry(client, url)
        response.raise_for_status()
        missing -= {result.get("trackId") for result in response.json().get("results", [])}
    return [
        Finding(
            "mas-unlisted",
            name,
            f"App Store id {app_id} is not listed in the {'/'.join(MAS_COUNTRIES).upper()} stores "
            "(delisted, or sold only elsewhere): no more updates, and it installs only while it "
            "stays in your purchase history",
        )
        for name, app_id in apps.items()
        if app_id in missing
    ]


def flake_finding(lock: Path, today: date) -> Finding | None:
    """Age of the nixpkgs revision pinned in ``flake.lock``."""
    nodes = json.loads(lock.read_text(encoding="utf-8"))["nodes"]
    node = nodes[nodes["root"]["inputs"]["nixpkgs"]]
    pinned = datetime.fromtimestamp(node["locked"]["lastModified"], timezone.utc).date()
    age = (today - pinned).days
    if age <= STALE_FLAKE_DAYS:
        return None
    return Finding(
        "stale-lock",
        "nix/flake.lock",
        f"nixpkgs is pinned at {pinned} ({age} days ago; limit {STALE_FLAKE_DAYS}): the weekly flake-update is not landing",
    )


async def _audit_online(nix_dir: Path) -> list[Finding]:
    darwin = nix_dir / "modules" / "darwin"
    entries = [("cask", name) for name in quoted_names(darwin / "casks.nix")]
    entries += [("formula", name) for name in quoted_names(darwin / "brews.nix")]
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        return await _audit_brew(client, entries) + await _audit_mas(client, mas_apps(darwin / "masApps.nix"))


def audit(nix_dir: Path, today: date) -> list[Finding]:
    findings = asyncio.run(_audit_online(nix_dir))
    flake = flake_finding(nix_dir / "flake.lock", today)
    return findings + ([flake] if flake else [])

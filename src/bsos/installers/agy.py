"""Antigravity CLI (``agy``) installer.

Replicates the official ``curl -fsSL https://antigravity.google/cli/install.sh | bash``
flow without GitHub releases.  That bootstrapper queries a per-platform JSON
manifest for the latest version and download URL, then places a single binary
named ``agy``:

    manifest : GET {BASE}/manifests/{platform}.json
               → {"version": "1.1.27", "url": "...cli_linux_x64.tar.gz", "sha512": "..."}
    binary   : the manifest ``url`` — a ``.tar.gz`` holding one ``antigravity`` member

The upstream script installs to ``~/.local/bin/agy`` and then runs ``agy install``
for native shell setup; here the binary lands in ``$__OPT_ROOT/bin/agy`` (already
on PATH via envoy's env) and the shell handoff is skipped.  The manifest sha512
check the upstream script performs is skipped too — we just download and place.

Linux musl has no published manifest (upstream 404s there as well), so only the
glibc Linux and macOS builds are targeted.

Usage::

    python -m bsos.installers.agy install
    python -m bsos.installers.agy uninstall
    python -m bsos.installers.agy test
"""

from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from bsos.installers._download import fetch_text
from bsos.installers._env import platform_key
from bsos.installers._recipe import TAR, Artifact, Dest, Recipe, VersionSpec, run_cli

_BASE = "https://antigravity-cli-auto-updater-974169037036.us-central1.run.app"

# platform_key (uname -sm) -> upstream manifest platform token
_TARGETS = {
    "Linux-x86_64": "linux_amd64",
    "Linux-aarch64": "linux_arm64",
    "Darwin-x86_64": "darwin_amd64",
    "Darwin-arm64": "darwin_arm64",
}


class ManifestVersion(VersionSpec):
    """Resolve the download URL and version from the per-platform JSON manifest.

    ``{tag}`` resolves to the full download URL from the manifest (used directly
    as the ``url_template``); ``{version}`` resolves to the manifest's version
    string.  The lookup is memoized so a single install follows it once.
    ``--version`` is not supported (the manifest only serves latest).
    """

    def __init__(self) -> None:
        self._cache: Optional[Tuple[str, str]] = None

    def resolve_both(self, override: Optional[str] = None) -> "Tuple[str, str]":
        if override is not None:
            raise RuntimeError("agy: --version is not supported (manifest serves latest only)")
        if self._cache is not None:
            return self._cache
        key = platform_key()
        token = _TARGETS.get(key)
        if token is None:
            raise RuntimeError(f"Unsupported platform: {key}")
        manifest: Dict[str, str] = json.loads(fetch_text(f"{_BASE}/manifests/{token}.json"))
        self._cache = (manifest["url"], manifest["version"])
        return self._cache


RECIPE = Recipe(
    name="agy",
    artifacts=[
        Artifact(
            url_template="{tag}",
            dest=Dest.bin("agy"),
            targets=_TARGETS,
            version=ManifestVersion(),
            archive=TAR,
            member="antigravity",
        )
    ],
)

if __name__ == "__main__":
    run_cli(RECIPE)

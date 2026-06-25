"""Clifton HPC workflow tool installer.

Clifton is an HPC workflow tool for the Isambard cluster — a single binary
downloaded from GitHub releases.

Usage::

    python -m bsos.installers.clifton install
    python -m bsos.installers.clifton uninstall
    python -m bsos.installers.clifton test
"""

from bsos.installers._recipe import Verify, github_binary, run_cli

# clifton tags have no leading `v` (e.g. "0.3.0") — github_binary uses {tag}
# in the URL path, so this works without any special-casing.
# `clifton --version` exits 64 (EX_USAGE), so verify by substring match only.
RECIPE = github_binary(
    name="clifton",
    repo="isambard-sc/clifton",
    asset="{target}",
    targets={
        "Darwin-arm64": "clifton-macos-aarch64",
        "Darwin-x86_64": "clifton-macos-x86_64",
        "Linux-x86_64": "clifton-linux-musl-x86_64",
        "Linux-aarch64": "clifton-linux-musl-aarch64",
    },
    verify=Verify(contains="clifton"),
)

if __name__ == "__main__":
    run_cli(RECIPE)

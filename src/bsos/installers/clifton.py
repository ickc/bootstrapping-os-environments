"""Clifton HPC workflow tool installer.

Clifton is an HPC workflow tool for the Isambard cluster — a single binary
downloaded from GitHub releases.

Usage::

    python -m bsos.installers.clifton install
    python -m bsos.installers.clifton uninstall
    python -m bsos.installers.clifton test
"""

from bsos.installers._recipe import Latest, Verify, github_binary, run_cli

# `clifton --version` prints its version but exits 64 (EX_USAGE) rather than 0,
# so verify that the binary runs and identifies itself (substring match) rather
# than gating on its idiosyncratic exit code.
RECIPE = github_binary(
    name="clifton",
    repo="isambard-sc/clifton",
    version=Latest(),
    asset="{target}",  # no version in the filename — /releases/latest/download/ works directly
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

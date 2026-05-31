"""Clifton HPC workflow tool installer.

Clifton is an HPC workflow tool for the Isambard cluster — a single binary
downloaded from GitHub releases.

Usage::

    python -m bsos.installers.clifton install
    python -m bsos.installers.clifton uninstall
    python -m bsos.installers.clifton test
"""

from bsos.installers._recipe import Artifact, Dest, GitHubRedirect, RAW, Recipe, Verify, run_cli

# clifton tags have no leading `v` (e.g. "0.3.0"), so we use Recipe/Artifact
# directly with strip_v=False and no `v` in the URL template.
# `clifton --version` exits 64 (EX_USAGE), so verify by substring match only.
RECIPE = Recipe(
    name="clifton",
    artifacts=[
        Artifact(
            url_template="https://github.com/isambard-sc/clifton/releases/download/{version}/{target}",
            dest=Dest.bin("clifton"),
            targets={
                "Darwin-arm64": "clifton-macos-aarch64",
                "Darwin-x86_64": "clifton-macos-x86_64",
                "Linux-x86_64": "clifton-linux-musl-x86_64",
                "Linux-aarch64": "clifton-linux-musl-aarch64",
            },
            version=GitHubRedirect("isambard-sc", "clifton", strip_v=False),
            archive=RAW,
        ),
    ],
    verify=Verify(contains="clifton"),
)

if __name__ == "__main__":
    run_cli(RECIPE)

"""Claude Code CLI installer.

Replicates the official ``curl -fsSL https://claude.ai/install.sh | bash`` flow
without GitHub releases.  That bootstrap script resolves the latest version from
a plain-text endpoint and then downloads a single ``claude`` binary:

    version : GET https://downloads.claude.ai/claude-code-releases/latest  → "2.1.190"
    binary  : https://downloads.claude.ai/claude-code-releases/{version}/{platform}/claude

The binary is a self-contained executable (no archive), so we only download it
and place it in ``$__OPT_ROOT/bin`` — the manifest.json SHA256 check the script
also performs is skipped (we just download and place, as requested).

Note: the upstream platform string has glibc and musl variants
(``linux-x64`` vs ``linux-x64-musl``); the official script sniffs libc to pick.
The recipe's static platform table can't detect libc, so we target the glibc
build, which is correct for typical Linux/HPC (glibc) systems.

Usage::

    python -m bsos.installers.claude install
    python -m bsos.installers.claude uninstall
    python -m bsos.installers.claude test
"""

from bsos.installers._recipe import Artifact, Dest, HttpVersion, Recipe, run_cli

_BASE = "https://downloads.claude.ai/claude-code-releases"

RECIPE = Recipe(
    name="claude",
    artifacts=[
        Artifact(
            url_template=f"{_BASE}/{{version}}/{{target}}/claude",
            dest=Dest.bin("claude"),
            targets={
                "Linux-x86_64": "linux-x64",
                "Linux-aarch64": "linux-arm64",
                "Darwin-x86_64": "darwin-x64",
                "Darwin-arm64": "darwin-arm64",
            },
            version=HttpVersion(f"{_BASE}/latest"),
        )
    ],
)

if __name__ == "__main__":
    run_cli(RECIPE)

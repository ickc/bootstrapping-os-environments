"""Claude Science installer.

``claude-science`` ships a single self-contained ELF binary at a stable
``latest`` URL — no archive, no version-templated path, no plain-text version
endpoint (``manifest.json`` exists alongside it but is JSON, not the bare-text
format ``HttpVersion`` expects), so we omit ``version=`` entirely and let
``--version`` error out at the ``run_cli`` level, same as ``code.py``:

    binary : https://downloads.claude.ai/claude-science/latest/{target}

Only ``linux-x64`` is confirmed to exist at this path; ``manifest.json``
lists sha256 hashes for ``darwin-x64``/``darwin-arm64`` too, but the darwin
downloads live under a different (unconfirmed) URL scheme, so only Linux is
wired up here.

Usage::

    python -m bsos.installers.claude_science install
    python -m bsos.installers.claude_science uninstall
    python -m bsos.installers.claude_science test
"""

from bsos.installers._recipe import Artifact, Dest, Recipe, run_cli

RECIPE = Recipe(
    name="claude-science",
    artifacts=[
        Artifact(
            url_template="https://downloads.claude.ai/claude-science/latest/{target}",
            dest=Dest.bin("claude-science"),
            targets={
                "Linux-x86_64": "linux-x64",
            },
        )
    ],
)

if __name__ == "__main__":
    run_cli(RECIPE)

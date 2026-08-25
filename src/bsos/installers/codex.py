"""OpenAI Codex CLI installer.

Downloads the latest codex binaries from GitHub releases without calling the
GitHub API (rate-limited at 60 req/hour unauthenticated); the release tag is
resolved by following the /releases/latest redirect.

Two binaries are placed, matching what the official installer
(``https://chatgpt.com/codex/install.sh``) now ships in its
``codex-package-<target>.tar.gz`` bundle:

- ``codex`` — the CLI itself
- ``codex-code-mode-host`` — the code-mode host, which codex execs as a sibling

The official script unpacks the bundle into ``~/.codex/packages/standalone``
and symlinks into ``~/.local/bin``; here each binary comes from its own
standalone release asset and lands directly in ``$__OPT_ROOT/bin``, which
keeps the two siblings on PATH just the same.  The bundle's vendored ``rg``
and (Linux) ``bwrap`` are deliberately not vendored — envoy installs ripgrep
via conda and codex falls back to PATH.

Usage::

    python -m bsos.installers.codex install
    python -m bsos.installers.codex uninstall
    python -m bsos.installers.codex test
"""

from bsos.installers._recipe import TAR, Artifact, Dest, GitHubRedirect, Recipe, run_cli

_TARGETS = {
    "Linux-x86_64": "x86_64-unknown-linux-musl",
    "Linux-aarch64": "aarch64-unknown-linux-musl",
    "Darwin-x86_64": "x86_64-apple-darwin",
    "Darwin-arm64": "aarch64-apple-darwin",
}

# openai/codex tags use a "rust-v" prefix (e.g. "rust-v0.149.1") — {tag} in the
# URL path resolves to the tag verbatim, so no special-casing is needed.  One
# shared VersionSpec instance means the redirect is followed once and both
# binaries are guaranteed to come from the same release.
_VERSION = GitHubRedirect("openai", "codex")


def _standalone_binary(name: str) -> Artifact:
    """A ``<name>-<target>.tar.gz`` asset holding a single ``<name>-<target>`` binary."""
    return Artifact(
        url_template=f"https://github.com/openai/codex/releases/download/{{tag}}/{name}-{{target}}.tar.gz",
        dest=Dest.bin(name),
        targets=_TARGETS,
        version=_VERSION,
        archive=TAR,
        member=f"{name}-{{target}}",
    )


RECIPE = Recipe(
    name="codex",
    artifacts=[
        _standalone_binary("codex"),
        _standalone_binary("codex-code-mode-host"),
    ],
)

if __name__ == "__main__":
    run_cli(RECIPE)

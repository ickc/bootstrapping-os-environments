"""OpenAI Codex CLI installer.

Downloads the latest codex binary from GitHub releases without calling the
GitHub API (rate-limited at 60 req/hour unauthenticated); the release tag is
resolved by following the /releases/latest redirect.

Usage::

    python -m bsos.installers.codex install
    python -m bsos.installers.codex uninstall
    python -m bsos.installers.codex test
"""

from bsos.installers._recipe import github_binary, run_cli

# openai/codex tags use a "rust-v" prefix (e.g. "rust-v0.135.0") — github_binary
# uses {tag} in the URL path, so this works without any special-casing.
RECIPE = github_binary(
    name="codex",
    repo="openai/codex",
    asset="codex-{target}.tar.gz",
    member="codex-{target}",
    targets={
        "Linux-x86_64": "x86_64-unknown-linux-musl",
        "Linux-aarch64": "aarch64-unknown-linux-musl",
        "Darwin-x86_64": "x86_64-apple-darwin",
        "Darwin-arm64": "aarch64-apple-darwin",
    },
)

if __name__ == "__main__":
    run_cli(RECIPE)

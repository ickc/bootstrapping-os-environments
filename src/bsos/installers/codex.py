"""OpenAI Codex CLI installer.

Downloads the latest codex binary from GitHub releases without calling the
GitHub API (rate-limited at 60 req/hour unauthenticated); the release tag is
resolved by following the /releases/latest redirect.

Usage::

    python -m bsos.installers.codex install
    python -m bsos.installers.codex uninstall
    python -m bsos.installers.codex test
"""

from bsos.installers._recipe import Artifact, Dest, GitHubRedirect, TAR, Recipe, Verify, run_cli

# openai/codex tags have a "rust-v" prefix (e.g. "rust-v0.135.0"), not the
# conventional "v" prefix, so github_binary's default URL template would
# produce "vrust-v0.135.0" → 404.  Use Recipe/Artifact directly with
# strip_v=False and no leading "v" in the URL template.
RECIPE = Recipe(
    name="codex",
    artifacts=[
        Artifact(
            url_template="https://github.com/openai/codex/releases/download/{version}/codex-{target}.tar.gz",
            dest=Dest.bin("codex"),
            targets={
                "Linux-x86_64": "x86_64-unknown-linux-musl",
                "Linux-aarch64": "aarch64-unknown-linux-musl",
                "Darwin-x86_64": "x86_64-apple-darwin",
                "Darwin-arm64": "aarch64-apple-darwin",
            },
            version=GitHubRedirect("openai", "codex", strip_v=False),
            archive=TAR,
            member="codex-{target}",
        ),
    ],
    verify=Verify(),
)

if __name__ == "__main__":
    run_cli(RECIPE)

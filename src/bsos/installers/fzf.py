"""fzf fuzzy finder installer.

Downloads the latest fzf binary from GitHub releases without calling the GitHub
API (rate-limited at 60 req/hour unauthenticated); the version is resolved by
following the /releases/latest redirect.

Usage::

    python -m bsos.installers.fzf install
    python -m bsos.installers.fzf uninstall
    python -m bsos.installers.fzf test"""

from bsos.installers._recipe import github_binary, run_cli

RECIPE = github_binary(
    name="fzf",
    repo="junegunn/fzf",
    asset="fzf-{version}-{target}.tar.gz",
    member="fzf",
    targets={
        "Linux-x86_64": "linux_amd64",
        "Linux-aarch64": "linux_arm64",
        "Darwin-x86_64": "darwin_amd64",
        "Darwin-arm64": "darwin_arm64",
    },
)

if __name__ == "__main__":
    run_cli(RECIPE)

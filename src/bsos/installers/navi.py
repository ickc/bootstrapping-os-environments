"""navi interactive cheatsheet tool installer.

Downloads the latest navi binary from GitHub releases without calling the GitHub
API (rate-limited at 60 req/hour unauthenticated); the version is resolved by
following the /releases/latest redirect.

Usage::

    python -m bsos.installers.navi install
    python -m bsos.installers.navi uninstall
    python -m bsos.installers.navi test"""

from bsos.installers._recipe import github_binary, run_cli

RECIPE = github_binary(
    name="navi",
    repo="denisidoro/navi",
    asset="navi-v{version}-{target}.tar.gz",
    member="navi",
    targets={
        "Linux-x86_64": "x86_64-unknown-linux-musl",
        "Linux-aarch64": "aarch64-unknown-linux-gnu",
    },
)

if __name__ == "__main__":
    run_cli(RECIPE)

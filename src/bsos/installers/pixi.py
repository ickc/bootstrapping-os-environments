"""Pixi installer.

Downloads the latest pixi binary from GitHub releases and installs it to
``$PIXI_HOME/bin/pixi``.
"""

from bsos.installers._recipe import Dest, Latest, github_binary, run_cli

# Use the /releases/latest/download/ redirect — no GitHub API call, no rate limit.
RECIPE = github_binary(
    name="pixi",
    repo="prefix-dev/pixi",
    version=Latest(),
    asset="pixi-{target}.tar.gz",
    member="pixi",
    targets={
        "Linux-x86_64": "x86_64-unknown-linux-musl",
        "Linux-aarch64": "aarch64-unknown-linux-musl",
        "Darwin-x86_64": "x86_64-apple-darwin",
        "Darwin-arm64": "aarch64-apple-darwin",
    },
    dest=Dest("pixi_home", "bin/pixi"),
)

if __name__ == "__main__":
    run_cli(RECIPE)

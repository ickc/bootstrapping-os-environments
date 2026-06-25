"""chezmoi dotfile manager installer.

Downloads the latest chezmoi binary from GitHub releases and installs it to
``$__OPT_ROOT/bin/chezmoi``.

Usage::

    python -m bsos.installers.chezmoi install
    python -m bsos.installers.chezmoi uninstall
    python -m bsos.installers.chezmoi test
"""

from bsos.installers._recipe import github_binary, run_cli

RECIPE = github_binary(
    name="chezmoi",
    repo="twpayne/chezmoi",
    asset="chezmoi_{version}_{target}.tar.gz",
    member="chezmoi",
    targets={
        "Linux-x86_64": "linux_amd64",
        "Linux-aarch64": "linux_arm64",
        "Darwin-x86_64": "darwin_amd64",
        "Darwin-arm64": "darwin_arm64",
    },
)

if __name__ == "__main__":
    run_cli(RECIPE)

"""micromamba installer.

Downloads the latest micromamba static binary from GitHub releases and installs
it to ``$__OPT_ROOT/bin/micromamba``.

micromamba is a single self-contained executable: unlike Miniforge3 (which the
:mod:`mamba` installer unpacks into ``$MAMBA_ROOT_PREFIX``), it ships no base
environment and no ``condabin``/``etc`` tree. It still honours
``$MAMBA_ROOT_PREFIX`` for its package cache and named environments.
"""

from bsos.installers._recipe import GitHubRedirect, github_binary, run_cli

RECIPE = github_binary(
    name="micromamba",
    repo="mamba-org/micromamba-releases",
    # Release assets are the bare static binary per platform — no archive,
    # no version in the filename. dest defaults to $__OPT_ROOT/bin/micromamba.
    asset="micromamba-{target}",
    # Tags carry no leading 'v' (e.g. 2.8.1-0); {tag} resolves to the raw tag.
    version=GitHubRedirect("mamba-org", "micromamba-releases", strip_v=False),
    targets={
        "Darwin-arm64": "osx-arm64",
        "Darwin-x86_64": "osx-64",
        "Linux-x86_64": "linux-64",
        "Linux-aarch64": "linux-aarch64",
        "Linux-ppc64le": "linux-ppc64le",
    },
)

if __name__ == "__main__":
    run_cli(RECIPE)

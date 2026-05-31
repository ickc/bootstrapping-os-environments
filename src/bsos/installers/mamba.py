"""Miniforge3 (mamba) installer.

Downloads and runs the official Miniforge3 shell installer for the current
platform — a fresh install, or an in-place update when ``$MAMBA_ROOT_PREFIX``
already exists.
"""

from bsos.installers._recipe import (
    RAW,
    Artifact,
    Dest,
    GitHubRedirect,
    Recipe,
    Remove,
    RunScript,
    Verify,
    run_cli,
)

_PREFIX = Dest("mamba_root_prefix")

RECIPE = Recipe(
    name="mamba",
    artifacts=[
        Artifact(
            # Miniforge tags have no leading 'v' (e.g. 26.3.2-2), so strip_v=False.
            url_template="https://github.com/conda-forge/miniforge/releases/download/{version}/Miniforge3-{target}.sh",
            version=GitHubRedirect("conda-forge", "miniforge", strip_v=False),
            targets={
                "Darwin-arm64": "Darwin-arm64",
                "Darwin-x86_64": "Darwin-x86_64",
                "Linux-x86_64": "Linux-x86_64",
                "Linux-aarch64": "Linux-aarch64",
                "Linux-ppc64le": "Linux-ppc64le",
            },
            archive=RAW,
            dest=_PREFIX,
            # -b batch, -s skip running init, -p prefix; -f fresh, -u update.
            action=RunScript(
                fresh_args=["{script}", "-fbsp", "{dest}"],
                update_args=["{script}", "-ubsp", "{dest}"],
                update_marker="etc/profile.d/conda.sh",
            ),
        )
    ],
    verify=Verify(path=Dest("mamba_root_prefix", "bin/mamba")),
    remove=Remove(tree=_PREFIX),
)

if __name__ == "__main__":
    run_cli(RECIPE)

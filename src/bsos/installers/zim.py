"""Zim (zsh plugin manager) installer.

Downloads ``zimfw.zsh`` from the latest GitHub release into ``$ZIM_HOME``.
Platform-independent: a single sourced script, not an executable.
"""

from bsos.installers._recipe import RAW, Artifact, Dest, Recipe, Remove, Verify, run_cli

RECIPE = Recipe(
    name="zim",
    artifacts=[
        Artifact(
            url_template="https://github.com/zimfw/zimfw/releases/latest/download/zimfw.zsh",
            archive=RAW,
            dest=Dest("zim_home", "zimfw.zsh"),
            executable=False,
        )
    ],
    verify=Verify(args=None),  # sourced file, not runnable — existence check only
    remove=Remove(tree=Dest("zim_home")),
)

if __name__ == "__main__":
    run_cli(RECIPE)

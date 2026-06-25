"""VS Code CLI installer.

Entry point convention shared by all installers (so CI can drive them
generically): ``install`` / ``uninstall`` / ``test`` actions, where ``test``
validates an install on the current platform.
"""

from bsos.installers._recipe import TAR, ZIP, Artifact, Dest, Recipe, run_cli

RECIPE = Recipe(
    name="code",
    artifacts=[
        Artifact(
            url_template="https://code.visualstudio.com/sha/download?build=stable&os={target}",
            targets={
                "Linux-x86_64": "cli-alpine-x64",
                "Linux-armv7l": "cli-linux-armhf",
                "Linux-aarch64": "cli-alpine-arm64",
                "Darwin-x86_64": "cli-darwin-x64",
                "Darwin-arm64": "cli-darwin-arm64",
            },
            archive={
                "Linux-x86_64": TAR,
                "Linux-armv7l": TAR,
                "Linux-aarch64": TAR,
                "Darwin-x86_64": ZIP,
                "Darwin-arm64": ZIP,
            },
            member="code",
            dest=Dest.bin("code"),
        )
    ],
)

if __name__ == "__main__":
    run_cli(RECIPE)

"""sman snippet manager installer.

Installs the ``sman`` binary and its shell-integration file ``sman.rc``.  The
sman-snippets repository is managed separately (clone it to
``$XDG_DATA_HOME/sman/snippets`` via git).
"""

from bsos.installers._recipe import (
    RAW,
    TAR,
    Artifact,
    Dest,
    Pinned,
    Recipe,
    Verify,
    run_cli,
)

_VERSION = Pinned("1.0.4")

RECIPE = Recipe(
    name="sman",
    artifacts=[
        Artifact(
            url_template="https://github.com/ickc/sman/releases/download/v{version}/sman-{target}-v{version}.tgz",
            version=_VERSION,
            archive=TAR,
            targets={
                "Darwin-arm64": "darwin-arm64",
                "Darwin-x86_64": "darwin-amd64",
                "Linux-x86_64": "linux-amd64",
                "Linux-aarch64": "linux-arm64",
                "Linux-ppc64le": "linux-ppc64le",
                "FreeBSD-amd64": "freebsd-amd64",
            },
            member="sman-{target}-v{version}",
            dest=Dest.bin("sman"),
        ),
        Artifact(
            url_template="https://raw.githubusercontent.com/ickc/sman/refs/heads/main/sman.rc",
            archive=RAW,
            dest=Dest("xdg_data_home", "sman/sman.rc"),
            executable=False,
        ),
    ],
    verify=Verify(args=["-h"]),
)

if __name__ == "__main__":
    run_cli(RECIPE)

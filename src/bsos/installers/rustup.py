"""rustup (Rust toolchain manager) installer.

Downloads and runs the official ``rustup-init`` binary for the current
platform — a fresh install, or ``rustup update`` in place when
``$CARGO_HOME/bin/rustup`` already exists.

Unlike the upstream ``sh.rustup.rs`` script (which defaults to
``$HOME/.rustup``/``$HOME/.cargo`` and offers to edit shell rc files),
``RUSTUP_HOME``/``CARGO_HOME`` are redirected under ``$__OPT_ROOT`` (see
``_env.py``) and ``--no-modify-path`` is always passed — envoy manages
``PATH``/env vars itself via ``env.sh``/``env.fish``, not the tool's own
installer.
"""

from bsos.installers._recipe import (
    RAW,
    Artifact,
    Dest,
    Latest,
    Recipe,
    Remove,
    RunScript,
    Verify,
    run_cli,
)

_CARGO_HOME = Dest("cargo_home")

RECIPE = Recipe(
    name="rustup",
    artifacts=[
        Artifact(
            # No {version}/{tag} in this URL — it always resolves to the
            # current rustup-init, so there is nothing for --version to pin.
            url_template="https://static.rust-lang.org/rustup/dist/{target}/rustup-init",
            version=Latest(),
            targets={
                "Darwin-arm64": "aarch64-apple-darwin",
                "Darwin-x86_64": "x86_64-apple-darwin",
                "Linux-x86_64": "x86_64-unknown-linux-gnu",
                "Linux-aarch64": "aarch64-unknown-linux-gnu",
            },
            archive=RAW,
            dest=_CARGO_HOME,
            action=RunScript(
                fresh_args=[
                    "{script}",
                    "-y",
                    "--no-modify-path",
                    "--default-toolchain",
                    "stable",
                    "--profile",
                    "default",
                ],
                # Already installed: update rustup itself and the default
                # toolchain via the installed binary, not a re-run of
                # rustup-init.
                update_args=["{dest}/bin/rustup", "update"],
                update_marker="bin/rustup",
            ),
        )
    ],
    verify=Verify(path=Dest("cargo_home", "bin/rustup")),
    # rustup owns two independent roots (CARGO_HOME for bin/registry,
    # RUSTUP_HOME for toolchains) — remove both on uninstall.
    remove=Remove(trees=[_CARGO_HOME, Dest("rustup_home")]),
)

if __name__ == "__main__":
    run_cli(RECIPE)

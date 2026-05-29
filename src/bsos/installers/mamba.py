"""Miniforge3 (mamba) installer.

Downloads and runs the official Miniforge3 shell installer for the current
platform.  Performs a fresh install or an in-place update depending on
whether ``$MAMBA_ROOT_PREFIX`` already exists.
"""

import argparse
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Optional

from bsos.installers._download import download_file
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

_URLS = {
    "Darwin-arm64": "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Darwin-arm64.sh",
    "Darwin-x86_64": "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Darwin-x86_64.sh",
    "Linux-x86_64": "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh",
    "Linux-aarch64": "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh",
    "Linux-ppc64le": "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-ppc64le.sh",
}


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    key = platform_key()
    url = _URLS.get(key)
    if url is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)

    tmp = Path(tempfile.mkdtemp(prefix="bsos-mamba-"))
    try:
        installer = tmp / "Miniforge3.sh"
        download_file(url, installer)
        installer.chmod(installer.stat().st_mode | stat.S_IEXEC)

        update = (env.mamba_root_prefix / "etc" / "profile.d" / "conda.sh").exists()
        flag = "-ubsp" if update else "-fbsp"
        action = "Updating" if update else "Installing"
        print(f"{action} mamba to {env.mamba_root_prefix} ...")
        run([str(installer), flag, str(env.mamba_root_prefix)], env=env.subprocess_env())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"Installed mamba to {env.mamba_root_prefix}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    if env.mamba_root_prefix.exists():
        shutil.rmtree(env.mamba_root_prefix)
        print(f"Removed {env.mamba_root_prefix}")
    else:
        print(f"{env.mamba_root_prefix} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate the mamba install on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _URLS:
        print(f"Platform {key} unsupported by mamba installer; skipping", file=sys.stderr)
        return 0
    mamba_bin = env.mamba_root_prefix / "bin" / "mamba"
    if not mamba_bin.exists():
        print(f"{mamba_bin} not found; run install first", file=sys.stderr)
        return 1
    result = run([str(mamba_bin), "--version"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help="install/uninstall Miniforge3, or test validates an install "
        "(skips cleanly if the platform is unsupported)",
    )
    args = parser.parse_args()
    env = EnvConfig()
    if args.action == "install":
        install(env)
    elif args.action == "uninstall":
        uninstall(env)
    else:
        sys.exit(test_install(env))


if __name__ == "__main__":
    main()

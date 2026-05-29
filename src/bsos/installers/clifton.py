"""Clifton HPC workflow tool installer.

Clifton is an HPC workflow tool for the Isambard cluster.
Downloads a single binary from GitHub releases.

Usage::

    python -m bsos.installers.clifton install
    python -m bsos.installers.clifton uninstall
    python -m bsos.installers.clifton test
"""

import argparse
import shutil
import sys
from typing import Optional

from bsos.installers._download import download_file
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

# Filename suffix per platform; no version in filename — /releases/latest/download/ works directly.
_TARGETS = {
    "Darwin-arm64": "clifton-macos-aarch64",
    "Darwin-x86_64": "clifton-macos-x86_64",
    "Linux-x86_64": "clifton-linux-musl-x86_64",
    "Linux-aarch64": "clifton-linux-musl-aarch64",
}

_URL_TEMPLATE = "https://github.com/isambard-sc/clifton/releases/latest/download/{filename}"


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    key = platform_key()
    filename = _TARGETS.get(key)
    if filename is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)

    url = _URL_TEMPLATE.format(filename=filename)
    env.bin_dir.mkdir(parents=True, exist_ok=True)
    dest = env.bin_dir / "clifton"
    download_file(url, dest)
    dest.chmod(0o755)
    print(f"Installed clifton (latest) to {dest}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    clifton_bin = env.bin_dir / "clifton"
    if clifton_bin.exists():
        clifton_bin.unlink()
        print(f"Removed {clifton_bin}")
    else:
        print(f"{clifton_bin} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate the clifton install on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _TARGETS:
        print(f"Platform {key} unsupported by clifton installer; skipping", file=sys.stderr)
        return 0
    clifton_bin = env.bin_dir / "clifton"
    if not clifton_bin.exists():
        print(f"{clifton_bin} not found; run install first", file=sys.stderr)
        return 1
    result = run([str(clifton_bin), "--version"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help="install/uninstall clifton, or test validates an install "
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

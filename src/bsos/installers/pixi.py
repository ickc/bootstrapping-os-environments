"""Pixi installer.

Downloads the latest pixi binary from GitHub releases and installs it to
``$PIXI_HOME/bin/pixi``.
"""

import argparse
import json
import shutil
import sys
import urllib.request
from typing import Optional

from bsos.installers._download import download_to_tempdir
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

_TARGETS = {
    "Linux-x86_64": "x86_64-unknown-linux-musl",
    "Linux-aarch64": "aarch64-unknown-linux-musl",
    "Darwin-x86_64": "x86_64-apple-darwin",
    "Darwin-arm64": "aarch64-apple-darwin",
}

_RELEASES_API = "https://api.github.com/repos/prefix-dev/pixi/releases/latest"


def _latest_version() -> str:
    req = urllib.request.Request(
        _RELEASES_API,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        data = json.loads(resp.read())
    return data["tag_name"].lstrip("v")


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    key = platform_key()
    target = _TARGETS.get(key)
    if target is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)

    version = _latest_version()
    url = f"https://github.com/prefix-dev/pixi/releases/download/v{version}/pixi-{target}.tar.gz"
    tmp = download_to_tempdir(url, extract="tar")
    try:
        src = tmp / "pixi"
        if not src.exists():
            print("Expected 'pixi' binary not found in archive", file=sys.stderr)
            sys.exit(1)
        pixi_bin_dir = env.pixi_home / "bin"
        pixi_bin_dir.mkdir(parents=True, exist_ok=True)
        dest = pixi_bin_dir / "pixi"
        shutil.move(str(src), str(dest))
        dest.chmod(0o755)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"Installed pixi {version} to {dest}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    target = env.pixi_home / "bin" / "pixi"
    if target.exists():
        target.unlink()
        print(f"Removed {target}")
    else:
        print(f"{target} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate the pixi install on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _TARGETS:
        print(f"Platform {key} unsupported by pixi installer; skipping", file=sys.stderr)
        return 0
    pixi_bin = env.pixi_home / "bin" / "pixi"
    if not pixi_bin.exists():
        print(f"{pixi_bin} not found; run install first", file=sys.stderr)
        return 1
    result = run([str(pixi_bin), "--version"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help="install/uninstall pixi, or test validates an install "
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

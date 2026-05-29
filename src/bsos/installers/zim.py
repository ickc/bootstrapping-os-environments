"""Zim (zsh plugin manager) installer.

Downloads ``zimfw.zsh`` from the latest GitHub release into ``$ZIM_HOME``.
"""

import argparse
import shutil
import sys
from typing import Optional

from bsos.installers._download import download_file
from bsos.installers._env import EnvConfig

_ZIMFW_URL = "https://github.com/zimfw/zimfw/releases/latest/download/zimfw.zsh"


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    env.zim_home.mkdir(parents=True, exist_ok=True)
    dest = env.zim_home / "zimfw.zsh"
    download_file(_ZIMFW_URL, dest)
    print(f"Installed zimfw to {dest}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    if env.zim_home.exists():
        shutil.rmtree(env.zim_home)
        print(f"Removed {env.zim_home}")
    else:
        print(f"{env.zim_home} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate that zimfw.zsh was installed."""
    env = env or EnvConfig()
    zimfw = env.zim_home / "zimfw.zsh"
    if not zimfw.exists():
        print(f"{zimfw} not found; run install first", file=sys.stderr)
        return 1
    print(f"zimfw.zsh found at {zimfw}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "uninstall", "test"])
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

"""VS Code CLI installer.

Entry point convention shared by all installers (so CI can drive them
generically): ``install`` / ``uninstall`` / ``test`` actions, where
``test`` validates an install on the current platform.
"""

import argparse
import shutil
import sys
from typing import Optional

from bsos.installers._download import download_to_tempdir
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

# key: (url, archive_format)
_URLS = {
    "Linux-x86_64": (
        "https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64",
        "tar",
    ),
    "Linux-armv7l": (
        "https://code.visualstudio.com/sha/download?build=stable&os=cli-linux-armhf",
        "tar",
    ),
    "Linux-aarch64": (
        "https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-arm64",
        "tar",
    ),
    "Darwin-x86_64": (
        "https://code.visualstudio.com/sha/download?build=stable&os=cli-darwin-x64",
        "zip",
    ),
    "Darwin-arm64": (
        "https://code.visualstudio.com/sha/download?build=stable&os=cli-darwin-arm64",
        "zip",
    ),
}


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()

    key = platform_key()
    entry = _URLS.get(key)
    if entry is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)

    url, fmt = entry
    tmp = download_to_tempdir(url, extract=fmt)
    try:
        src = tmp / "code"
        if not src.exists():
            print("Expected 'code' binary not found in archive", file=sys.stderr)
            sys.exit(1)
        env.bin_dir.mkdir(parents=True, exist_ok=True)
        dest = env.bin_dir / "code"
        shutil.move(str(src), str(dest))
        dest.chmod(0o755)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"Installed VS Code CLI to {dest}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    target = env.bin_dir / "code"
    if target.exists():
        target.unlink()
        print(f"Removed {target}")
    else:
        print(f"{target} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate the install on the current platform.

    On an unsupported platform: print to stderr and return 0 (a clean
    skip, so CI can run this on any runner).  On a supported platform:
    run the installed ``code --version`` and return its exit code.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _URLS:
        print(f"Platform {key} unsupported by code installer; skipping", file=sys.stderr)
        return 0
    code_bin = env.bin_dir / "code"
    if not code_bin.exists():
        print(f"{code_bin} not found; run install first", file=sys.stderr)
        return 1
    result = run([str(code_bin), "--version"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help="install/uninstall the VS Code CLI, or test validates an install "
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

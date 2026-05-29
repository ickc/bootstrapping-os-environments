"""sman snippet manager installer.

Installs the ``sman`` binary and its shell-integration file ``sman.rc``.
The sman-snippets repository is managed separately (clone it to
``$XDG_DATA_HOME/sman/snippets`` via git).
"""

import argparse
import shutil
import sys
from typing import Optional

from bsos.installers._download import download_file, download_to_tempdir
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

_VERSION = "1.0.4"

_TARGETS = {
    "Darwin-arm64": "darwin-arm64",
    "Darwin-x86_64": "darwin-amd64",
    "Linux-x86_64": "linux-amd64",
    "Linux-aarch64": "linux-arm64",
    "Linux-ppc64le": "linux-ppc64le",
    "FreeBSD-amd64": "freebsd-amd64",
}

_SMAN_RC_URL = "https://raw.githubusercontent.com/ickc/sman/refs/heads/main/sman.rc"


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    key = platform_key()
    target = _TARGETS.get(key)
    if target is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)

    filename = f"sman-{target}-v{_VERSION}"
    url = f"https://github.com/ickc/sman/releases/download/v{_VERSION}/{filename}.tgz"
    tmp = download_to_tempdir(url, extract="tar")
    try:
        src = tmp / filename
        if not src.exists():
            print(f"Expected binary {filename!r} not found in archive", file=sys.stderr)
            sys.exit(1)
        env.bin_dir.mkdir(parents=True, exist_ok=True)
        dest = env.bin_dir / "sman"
        shutil.move(str(src), str(dest))
        dest.chmod(0o755)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    sman_dir = env.xdg_data_home / "sman"
    sman_dir.mkdir(parents=True, exist_ok=True)
    rc_dest = sman_dir / "sman.rc"
    download_file(_SMAN_RC_URL, rc_dest)

    print(f"Installed sman {_VERSION} to {dest}")
    print(f"sman.rc written to {rc_dest}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    sman_bin = env.bin_dir / "sman"
    sman_rc = env.xdg_data_home / "sman" / "sman.rc"
    for path in (sman_bin, sman_rc):
        if path.exists():
            path.unlink()
            print(f"Removed {path}")
        else:
            print(f"{path} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate the sman install on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _TARGETS:
        print(f"Platform {key} unsupported by sman installer; skipping", file=sys.stderr)
        return 0
    sman_bin = env.bin_dir / "sman"
    if not sman_bin.exists():
        print(f"{sman_bin} not found; run install first", file=sys.stderr)
        return 1
    result = run([str(sman_bin), "--version"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help="install/uninstall sman, or test validates an install "
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

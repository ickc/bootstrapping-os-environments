"""GitHub CLI (gh) installer.

Downloads the latest gh binary from GitHub releases without calling
the GitHub API (rate-limited at 60 req/hour unauthenticated). The
version is resolved by following the /releases/latest redirect URL.

Usage::

    python -m bsos.installers.gh install
    python -m bsos.installers.gh uninstall
    python -m bsos.installers.gh test
"""

import argparse
import shutil
import sys
from typing import Optional, Tuple

from bsos.installers._download import download_to_tempdir, resolve_latest_github_tag
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

# (filename_template, archive_format)
# {version} is replaced with the resolved release version (no leading 'v').
_TARGETS: dict = {
    "Linux-x86_64":  ("gh_{version}_linux_amd64.tar.gz",  "tar"),
    "Linux-aarch64": ("gh_{version}_linux_arm64.tar.gz",   "tar"),
    "Darwin-x86_64": ("gh_{version}_macOS_amd64.zip",      "zip"),
    "Darwin-arm64":  ("gh_{version}_macOS_arm64.zip",      "zip"),
}

_OWNER = "cli"
_REPO = "cli"


def _resolve(key: str) -> Tuple[str, str, str]:
    """Return (version, filename, archive_format) for the current platform."""
    entry = _TARGETS.get(key)
    if entry is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)
    tag = resolve_latest_github_tag(_OWNER, _REPO)
    version = tag.lstrip("v")
    filename_tmpl, fmt = entry
    filename = filename_tmpl.format(version=version)
    return version, filename, fmt


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    key = platform_key()
    version, filename, fmt = _resolve(key)

    url = f"https://github.com/{_OWNER}/{_REPO}/releases/download/v{version}/{filename}"
    tmp = download_to_tempdir(url, extract=fmt)
    try:
        # Archive unpacks to a directory named after the archive (minus extension).
        dirname = filename.replace(".tar.gz", "").replace(".zip", "")
        gh_binary = tmp / dirname / "bin" / "gh"
        if not gh_binary.exists():
            print(f"Expected binary not found at {gh_binary}", file=sys.stderr)
            sys.exit(1)
        env.bin_dir.mkdir(parents=True, exist_ok=True)
        dest = env.bin_dir / "gh"
        shutil.move(str(gh_binary), str(dest))
        dest.chmod(0o755)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"Installed gh {version} to {dest}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    gh_bin = env.bin_dir / "gh"
    if gh_bin.exists():
        gh_bin.unlink()
        print(f"Removed {gh_bin}")
    else:
        print(f"{gh_bin} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate the gh install on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _TARGETS:
        print(f"Platform {key} unsupported by gh installer; skipping", file=sys.stderr)
        return 0
    gh_bin = env.bin_dir / "gh"
    if not gh_bin.exists():
        print(f"{gh_bin} not found; run install first", file=sys.stderr)
        return 1
    result = run([str(gh_bin), "--version"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help="install/uninstall gh, or test validates an install "
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

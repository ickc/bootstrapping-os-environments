"""OpenAI Codex CLI installer.

Downloads the latest codex binary from GitHub releases without calling
the GitHub API (rate-limited at 60 req/hour unauthenticated). The
release tag is resolved by following the /releases/latest redirect URL.

Usage::

    python -m bsos.installers.codex install
    python -m bsos.installers.codex uninstall
    python -m bsos.installers.codex test
"""

import argparse
import shutil
import sys
from typing import Optional, Tuple

from bsos.installers._download import download_to_tempdir, resolve_latest_github_tag
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

# (filename, binary_name_in_archive)
# The binary is unpacked directly at the root of the tar (no subdirectory).
_TARGETS: dict = {
    "Linux-x86_64":  ("codex-x86_64-unknown-linux-musl.tar.gz",  "codex-x86_64-unknown-linux-musl"),
    "Linux-aarch64": ("codex-aarch64-unknown-linux-musl.tar.gz", "codex-aarch64-unknown-linux-musl"),
    "Darwin-x86_64": ("codex-x86_64-apple-darwin.tar.gz",        "codex-x86_64-apple-darwin"),
    "Darwin-arm64":  ("codex-aarch64-apple-darwin.tar.gz",       "codex-aarch64-apple-darwin"),
}

_OWNER = "openai"
_REPO = "codex"


def _resolve(key: str) -> Tuple[str, str, str]:
    """Return (tag, filename, binary_name) for the current platform."""
    entry = _TARGETS.get(key)
    if entry is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)
    tag = resolve_latest_github_tag(_OWNER, _REPO)
    filename, binary_name = entry
    return tag, filename, binary_name


def install(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    key = platform_key()
    tag, filename, binary_name = _resolve(key)

    url = f"https://github.com/{_OWNER}/{_REPO}/releases/download/{tag}/{filename}"
    tmp = download_to_tempdir(url, extract="tar")
    try:
        src = tmp / binary_name
        if not src.exists():
            print(f"Expected binary {binary_name!r} not found in archive", file=sys.stderr)
            sys.exit(1)
        env.bin_dir.mkdir(parents=True, exist_ok=True)
        dest = env.bin_dir / "codex"
        shutil.move(str(src), str(dest))
        dest.chmod(0o755)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"Installed codex ({tag}) to {dest}")


def uninstall(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    codex_bin = env.bin_dir / "codex"
    if codex_bin.exists():
        codex_bin.unlink()
        print(f"Removed {codex_bin}")
    else:
        print(f"{codex_bin} not found", file=sys.stderr)


def test_install(env: Optional[EnvConfig] = None) -> int:
    """Validate the codex install on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _TARGETS:
        print(f"Platform {key} unsupported by codex installer; skipping", file=sys.stderr)
        return 0
    codex_bin = env.bin_dir / "codex"
    if not codex_bin.exists():
        print(f"{codex_bin} not found; run install first", file=sys.stderr)
        return 1
    result = run([str(codex_bin), "--version"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help="install/uninstall codex, or test validates an install "
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

"""Conda environment installer using mamba.

Creates or updates a named conda environment from an environment YAML file.
The environment is installed to ``$__OPT_ROOT/$NAME`` (default: ``system``).

When run from within the envoy repository the bundled ``conda/`` files are
discovered automatically.  Otherwise pass ``--env-file`` with a local path
or a URL::

    # auto-detect bundled file (envoy repo clone):
    python3 install/mamba_env.py install --name system

    # explicit local file:
    python3 install/mamba_env.py install --name system --env-file /path/to/env.yml

    # URL (downloaded to a temp file, then used):
    python3 install/mamba_env.py install --name system \\
        --env-file https://raw.githubusercontent.com/ickc/envoy/main/conda/system_linux-64.yml

    # curl | python3 variant:
    curl -fsSL https://raw.githubusercontent.com/ickc/envoy/main/install/mamba_env.py | \\
        python3 - install --name system \\
        --env-file https://raw.githubusercontent.com/ickc/envoy/main/conda/system_linux-64.yml
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

from bsos.installers._download import download_file
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

_PLATFORM_MAP = {
    "Darwin-arm64": "osx-arm64",
    "Darwin-x86_64": "osx-64",
    "Linux-x86_64": "linux-64",
    "Linux-aarch64": "linux-aarch64",
    "Linux-ppc64le": "linux-ppc64le",
}


def _find_bundled_env_file(name: str) -> Optional[Path]:
    """Search for ``conda/${name}_${platform}.yml`` near the script.

    Works both when running as a source module (``src/bsos/installers/``) and
    as a compiled standalone script (``install/mamba_env.py`` — the repo root
    is one level up).
    """
    key = platform_key()
    conda_arch = _PLATFORM_MAP.get(key)
    if conda_arch is None:
        return None
    filename = f"{name}_{conda_arch}.yml"
    script_dir = Path(__file__).resolve().parent
    for search_root in [script_dir, *list(script_dir.parents)[:4]]:
        candidate = search_root / "conda" / filename
        if candidate.is_file():
            return candidate
    return None


def install(
    name: str = "system",
    env_file: Optional[str] = None,
    env: Optional[EnvConfig] = None,
) -> None:
    """Install or update a named conda environment.

    *env_file* may be a local path or an ``http(s)://`` URL; if omitted the
    bundled ``conda/`` file for the current platform is used.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _PLATFORM_MAP:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)

    mamba_bin = env.mamba_root_prefix / "bin" / "mamba"
    if not mamba_bin.exists():
        print(
            f"mamba not found at {mamba_bin}; install mamba first (run install/mamba.py install)",
            file=sys.stderr,
        )
        sys.exit(1)

    tmp_path: Optional[Path] = None
    try:
        if env_file is not None and env_file.startswith(("http://", "https://")):
            fd, tmp_str = tempfile.mkstemp(suffix=".yml", prefix="bsos-env-")
            import os; os.close(fd)
            tmp_path = Path(tmp_str)
            download_file(env_file, tmp_path)
            resolved = tmp_path
        elif env_file is not None:
            resolved = Path(env_file)
        else:
            resolved = _find_bundled_env_file(name)
            if resolved is None:
                print(
                    f"No env file found for name={name!r} on {key}. "
                    "Pass --env-file <path-or-url>.",
                    file=sys.stderr,
                )
                sys.exit(1)

        prefix = env.opt_root / name
        if prefix.exists():
            print(f"Updating conda env {name!r} at {prefix} ...")
            run(
                [str(mamba_bin), "env", "update", "-f", str(resolved), "-p", str(prefix), "-y", "--prune"],
                env=env.subprocess_env(),
            )
        else:
            print(f"Creating conda env {name!r} at {prefix} ...")
            run(
                [str(mamba_bin), "env", "create", "-f", str(resolved), "-p", str(prefix), "-y"],
                env=env.subprocess_env(),
            )
        print(f"Conda env {name!r} ready at {prefix}")
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def uninstall(name: str = "system", env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    prefix = env.opt_root / name
    if prefix.exists():
        shutil.rmtree(prefix)
        print(f"Removed conda env at {prefix}")
    else:
        print(f"{prefix} not found", file=sys.stderr)


def test_install(name: str = "system", env: Optional[EnvConfig] = None) -> int:
    """Validate that the named conda env exists on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.  Fails (exit 1) if mamba
    is absent — that is a missing prerequisite, not a platform limitation.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _PLATFORM_MAP:
        print(f"Platform {key} unsupported by mamba_env installer; skipping", file=sys.stderr)
        return 0
    mamba_bin = env.mamba_root_prefix / "bin" / "mamba"
    if not mamba_bin.exists():
        print(
            f"mamba not found at {mamba_bin}; install mamba first (run install/mamba.py install)",
            file=sys.stderr,
        )
        return 1
    prefix = env.opt_root / name
    if not prefix.exists():
        print(f"Conda env {name!r} not found at {prefix}; run install first", file=sys.stderr)
        return 1
    result = run([str(mamba_bin), "env", "list"], env=env.subprocess_env(), check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "uninstall", "test"])
    parser.add_argument(
        "--name",
        default="system",
        help="Conda env name and prefix subdirectory (default: system)",
    )
    parser.add_argument(
        "--env-file",
        default=None,
        metavar="PATH_OR_URL",
        help="Path or URL to conda env YAML (auto-detected from repo when omitted)",
    )
    args = parser.parse_args()
    env = EnvConfig()
    if args.action == "install":
        install(args.name, args.env_file, env)
    elif args.action == "uninstall":
        uninstall(args.name, env)
    else:
        sys.exit(test_install(args.name, env))


if __name__ == "__main__":
    main()

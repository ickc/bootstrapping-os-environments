"""Conda environment installer using mamba.

Creates or updates a named conda environment from an environment YAML file,
installed to ``$__OPT_ROOT/$NAME`` (default: ``system``).

The YAML file is selected by *name* + detected platform —
``<env-dir>/<name>_<conda-arch>.yml`` (e.g. ``system_linux-64.yml``) — so only
the directory (or base URL) is given; the filename is derived.  ``--env-dir``
defaults to the bundled ``conda/`` directory when running from a repo clone,
and to the canonical remote base otherwise (e.g. piped through ``curl``)::

    # bundled conda/ (repo clone), current platform:
    python3 install/mamba_env.py install --name system

    # explicit local directory:
    python3 install/mamba_env.py install --name py312 --env-dir /path/to/conda

    # explicit remote base (curl | python3 variant):
    curl -fsSL https://raw.githubusercontent.com/ickc/envoy/main/install/mamba_env.py | \\
        python3 - install --name system \\
        --env-dir https://raw.githubusercontent.com/ickc/envoy/main/conda
"""

import argparse
import contextlib
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterator, Optional

from bsos.installers._download import download_file
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

# platform_key() -> conda subdir token (this installer's analog of Artifact.targets).
_CONDA_ARCH = {
    "Darwin-arm64": "osx-arm64",
    "Darwin-x86_64": "osx-64",
    "Linux-x86_64": "linux-64",
    "Linux-aarch64": "linux-aarch64",
    "Linux-ppc64le": "linux-ppc64le",
}

# Canonical remote base, used when no bundled conda/ dir is found (e.g. curl | python3).
_REMOTE_ENV_DIR = "https://raw.githubusercontent.com/ickc/envoy/main/conda"


def _conda_arch() -> str:
    """Return the conda arch token for this platform, exiting 1 if unsupported."""
    key = platform_key()
    arch = _CONDA_ARCH.get(key)
    if arch is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)
    return arch


def _find_bundled_conda_dir() -> Optional[Path]:
    """Locate the bundled ``conda/`` directory near this script.

    Works both as a source module (``src/bsos/installers/``) and as a compiled
    standalone script (``install/mamba_env.py`` — the repo root is one level up).
    """
    script_dir = Path(__file__).resolve().parent
    for root in [script_dir, *list(script_dir.parents)[:4]]:
        candidate = root / "conda"
        if candidate.is_dir():
            return candidate
    return None


def _default_env_dir() -> str:
    """Bundled ``conda/`` dir when running from a clone, else the remote base."""
    local = _find_bundled_conda_dir()
    return str(local) if local is not None else _REMOTE_ENV_DIR


@contextlib.contextmanager
def _env_yaml(base: str, filename: str) -> Iterator[Path]:
    """Yield a local path to ``<base>/<filename>``.

    *base* is a local directory or an ``http(s)://`` base URL; a remote file is
    downloaded into a temp directory that is removed on exit.
    """
    if base.startswith(("http://", "https://")):
        tmp = Path(tempfile.mkdtemp(prefix="bsos-env-"))
        try:
            dest = tmp / filename
            download_file(f"{base.rstrip('/')}/{filename}", dest)
            yield dest
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        path = Path(base) / filename
        if not path.is_file():
            print(f"Env file not found: {path}", file=sys.stderr)
            sys.exit(1)
        yield path


def install(
    name: str = "system",
    env_dir: Optional[str] = None,
    env: Optional[EnvConfig] = None,
    force: bool = False,
) -> None:
    """Create a named conda environment, or skip if it already exists.

    With *force=True* (the ``update`` action), an existing env is updated via
    ``mamba env update --prune``; a missing env is created as normal.

    The env YAML is ``<env_dir>/<name>_<conda-arch>.yml``; *env_dir* may be a
    local directory or an ``http(s)://`` base URL (default: the bundled
    ``conda/`` dir, else the canonical remote base).
    """
    env = env or EnvConfig()

    mamba_bin = env.mamba_root_prefix / "bin" / "mamba"
    if not mamba_bin.exists():
        print(
            f"mamba not found at {mamba_bin}; install mamba first (run install/mamba.py install)",
            file=sys.stderr,
        )
        sys.exit(1)

    prefix = env.opt_root / name
    if not force and prefix.exists():
        print(f"Conda env {name!r} already exists at {prefix}; run 'update' to refresh")
        return

    filename = f"{name}_{_conda_arch()}.yml"
    base = env_dir if env_dir is not None else _default_env_dir()
    with _env_yaml(base, filename) as spec:
        if prefix.exists():
            print(f"Updating conda env {name!r} at {prefix} ...")
            argv = [str(mamba_bin), "env", "update", "-f", str(spec), "-p", str(prefix), "-y", "--prune"]
        else:
            print(f"Creating conda env {name!r} at {prefix} ...")
            argv = [str(mamba_bin), "env", "create", "-f", str(spec), "-p", str(prefix), "-y"]
        run(argv, env=env.subprocess_env())
    print(f"Conda env {name!r} ready at {prefix}")


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
    if key not in _CONDA_ARCH:
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
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "action",
        choices=["install", "update", "reinstall", "uninstall", "test"],
        help="install: create env if absent, skip if already present; "
        "update: force mamba env update even if env exists; "
        "reinstall: remove env then create fresh; "
        "uninstall: remove env; test: validate",
    )
    parser.add_argument(
        "--name",
        default="system",
        help="conda env name and prefix subdirectory (default: system)",
    )
    parser.add_argument(
        "--env-dir",
        default=None,
        metavar="PATH_OR_URL",
        help="directory or base URL holding <name>_<arch>.yml "
        "(default: bundled conda/, else the canonical remote base)",
    )
    args = parser.parse_args()
    env = EnvConfig()
    if args.action == "install":
        install(args.name, args.env_dir, env)
    elif args.action == "update":
        install(args.name, args.env_dir, env, force=True)
    elif args.action == "reinstall":
        uninstall(args.name, env)
        install(args.name, args.env_dir, env)
    elif args.action == "uninstall":
        uninstall(args.name, env)
    else:
        sys.exit(test_install(args.name, env))


if __name__ == "__main__":
    main()

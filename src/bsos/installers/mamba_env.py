"""Conda environment installer (micromamba or mamba backend).

Creates or updates a named conda environment from an environment spec file,
installed to ``$__OPT_ROOT/$NAME`` (default: ``system``).

``--backend`` selects the package manager (default ``micromamba``):
``micromamba`` is the standalone binary at ``$__OPT_ROOT/bin/micromamba``;
``mamba`` is the Miniforge build at ``$MAMBA_ROOT_PREFIX/bin/mamba``.
On update, a lockfile-based env is removed and recreated (``env update``
cannot consume conda-lock files; the pinned lockfile makes recreation exactly
reproduce the target state), while a YAML-based env uses ``env update
--prune`` so the spec stays authoritative.

The spec file is derived from *name*: the version-pinned multi-platform
conda-lock file ``<env-dir>/<name>-lock.yml`` (e.g. ``system-lock.yml``) is
preferred; environments not yet migrated to lockfiles fall back to the
per-platform ``<env-dir>/<name>_<conda-arch>.yml`` (e.g.
``system_linux-64.yml``). Both backends consume conda-lock files directly,
recognized by the ``-lock.yml`` suffix.  ``--env-dir``
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
import urllib.error
from pathlib import Path
from typing import Iterator, List, Optional

from bsos.installers._download import download_file
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run

# platform_key() -> conda subdir token (this installer's analog of Artifact.targets).
_CONDA_ARCH = {
    "Darwin-arm64": "osx-arm64",
    "Darwin-x86_64": "osx-64",
    "Linux-x86_64": "linux-64",
    "Linux-aarch64": "linux-aarch64",
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
    if "__file__" not in globals():
        return None
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


_BACKENDS = ("micromamba", "mamba")
_DEFAULT_BACKEND = "micromamba"


def _backend_bin(backend: str, env: EnvConfig) -> Path:
    """Path to the package-manager binary for *backend*.

    micromamba is a standalone binary under ``$__OPT_ROOT/bin``; mamba lives in
    the Miniforge tree at ``$MAMBA_ROOT_PREFIX/bin``.
    """
    if backend == "micromamba":
        return env.bin_dir / "micromamba"
    return env.mamba_root_prefix / "bin" / "mamba"


def _require_backend(backend: str, env: EnvConfig) -> Optional[Path]:
    """Return the backend binary path, or print an error and return ``None``."""
    tool = _backend_bin(backend, env)
    if not tool.exists():
        print(
            f"{backend} not found at {tool}; install it first (run install/{backend}.py install)",
            file=sys.stderr,
        )
        return None
    return tool


def _env_filenames(name: str) -> List[str]:
    """Candidate spec filenames for *name*, most preferred first.

    The unified conda-lock file pins versions for all platforms; the
    per-platform YAML is the fallback for envs not yet migrated to lockfiles.
    """
    return [f"{name}-lock.yml", f"{name}_{_conda_arch()}.yml"]


@contextlib.contextmanager
def _env_spec(base: str, filenames: List[str]) -> Iterator[Path]:
    """Yield a local path to the first of ``<base>/<filename>`` that exists.

    *base* is a local directory or an ``http(s)://`` base URL; a remote file is
    downloaded into a temp directory that is removed on exit.  The local
    filename is preserved so the backends still see the ``-lock.yml`` suffix
    that marks a conda-lock file.
    """
    if base.startswith(("http://", "https://")):
        tmp = Path(tempfile.mkdtemp(prefix="bsos-env-"))
        try:
            for i, filename in enumerate(filenames):
                dest = tmp / filename
                try:
                    download_file(f"{base.rstrip('/')}/{filename}", dest)
                except urllib.error.HTTPError as exc:
                    if exc.code == 404 and i < len(filenames) - 1:
                        continue
                    raise
                yield dest
                return
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        for filename in filenames:
            path = Path(base) / filename
            if path.is_file():
                yield path
                return
        tried = ", ".join(str(Path(base) / filename) for filename in filenames)
        print(f"Env spec not found: tried {tried}", file=sys.stderr)
        sys.exit(1)


def install(
    name: str = "system",
    env_dir: Optional[str] = None,
    env: Optional[EnvConfig] = None,
    force: bool = False,
    backend: str = _DEFAULT_BACKEND,
) -> None:
    """Create a named conda environment, or skip if it already exists.

    With *force=True* (the ``update`` action), an existing env is updated via
    ``env update --prune`` (YAML spec) or removed and recreated (lockfile
    spec); a missing env is created as normal. *backend* selects the package
    manager (``micromamba`` or ``mamba``).

    The env spec is ``<env_dir>/<name>-lock.yml`` (preferred, version-pinned)
    or ``<env_dir>/<name>_<conda-arch>.yml`` (fallback); *env_dir* may be a
    local directory or an ``http(s)://`` base URL (default: the bundled
    ``conda/`` dir, else the canonical remote base).
    """
    env = env or EnvConfig()

    tool = _require_backend(backend, env)
    if tool is None:
        sys.exit(1)

    prefix = env.opt_root / name
    if not force and prefix.exists():
        print(f"Conda env {name!r} already exists at {prefix}; run 'update' to refresh")
        return

    base = env_dir if env_dir is not None else _default_env_dir()
    with _env_spec(base, _env_filenames(name)) as spec:
        if prefix.exists() and spec.name.endswith("-lock.yml"):
            # `env update` cannot consume conda-lock files (libmamba fails to
            # parse the pinned entries). The lockfile pins every package, so
            # removing and recreating reproduces exactly the state that
            # `env update --prune` would converge to.
            print(f"Recreating conda env {name!r} at {prefix} from lockfile via {backend} ...")
            shutil.rmtree(prefix)
        if prefix.exists():
            print(f"Updating conda env {name!r} at {prefix} via {backend} ...")
            argv = [str(tool), "env", "update", "-y", "-p", str(prefix), "-f", str(spec), "--prune"]
        elif backend == "micromamba":
            print(f"Creating conda env {name!r} at {prefix} via micromamba ...")
            argv = [str(tool), "create", "-y", "-p", str(prefix), "-f", str(spec)]
        else:
            print(f"Creating conda env {name!r} at {prefix} via mamba ...")
            argv = [str(tool), "env", "create", "-y", "-p", str(prefix), "-f", str(spec)]
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


def test_install(name: str = "system", env: Optional[EnvConfig] = None, backend: str = _DEFAULT_BACKEND) -> int:
    """Validate that the named conda env exists on the current platform.

    Skips cleanly (exit 0) on unsupported platforms.  Fails (exit 1) if the
    chosen *backend* is absent — a missing prerequisite, not a platform limit.
    """
    env = env or EnvConfig()
    key = platform_key()
    if key not in _CONDA_ARCH:
        print(f"Platform {key} unsupported by mamba_env installer; skipping", file=sys.stderr)
        return 0
    tool = _require_backend(backend, env)
    if tool is None:
        return 1
    prefix = env.opt_root / name
    if not prefix.exists():
        print(f"Conda env {name!r} not found at {prefix}; run install first", file=sys.stderr)
        return 1
    result = run([str(tool), "env", "list"], env=env.subprocess_env(), check=False)
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
        "update: force env update even if env exists; "
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
        help="directory or base URL holding <name>-lock.yml (or the <name>_<arch>.yml fallback) "
        "(default: bundled conda/, else the canonical remote base)",
    )
    parser.add_argument(
        "--backend",
        choices=_BACKENDS,
        default=_DEFAULT_BACKEND,
        help=f"package manager driving env create/update (default: {_DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--skip-unsupported",
        action="store_true",
        default=False,
        help="no-op flag for CI compatibility; mamba_env is always platform-supported",
    )
    args = parser.parse_args()
    env = EnvConfig()
    if args.action == "install":
        install(args.name, args.env_dir, env, backend=args.backend)
    elif args.action == "update":
        install(args.name, args.env_dir, env, force=True, backend=args.backend)
    elif args.action == "reinstall":
        uninstall(args.name, env)
        install(args.name, args.env_dir, env, backend=args.backend)
    elif args.action == "uninstall":
        uninstall(args.name, env)
    else:
        sys.exit(test_install(args.name, env, backend=args.backend))


if __name__ == "__main__":
    main()

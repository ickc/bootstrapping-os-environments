"""Conda environment installer (micromamba or mamba backend).

Creates or updates a named conda environment from an environment spec file,
installed to ``$__OPT_ROOT/$NAME`` (default: ``system``).

``--backend`` selects the package manager (default ``micromamba``):
``micromamba`` is the standalone binary at ``$__OPT_ROOT/bin/micromamba``;
``mamba`` is the Miniforge build at ``$MAMBA_ROOT_PREFIX/bin/mamba``.

The spec file is derived from *name*: by default the version-pinned
multi-platform conda-lock file ``<name>-lock.yml`` (e.g. ``system-lock.yml``),
which both backends consume directly (recognized by the ``-lock.yml``
suffix); with ``--no-lock``, the per-platform ``<name>_<conda-arch>.yml``
(e.g. ``system_linux-64.yml``) instead.

The conda-lock files are not in git: they are assets of a dated GitHub
Release, and git keeps ``conda/locks.sha256``, which names that release and
the sha256 of each lock.  Without ``--env-dir`` the lock is resolved in this
order:

1. from a repo clone, a local ``conda/<name>-lock.yml`` if present (what
   ``pixi run conda-generate`` just wrote), with a warning when it is not the
   lock the pointer pins;
2. otherwise the release the pointer names — the clone's
   ``conda/locks.sha256``, or main's when piped through ``curl`` — downloaded
   and verified against the pointer's sha256; a mismatch is fatal.

On update, an env whose stamped lockfile sha256 already equals the pointer's
entry is converged, and nothing is downloaded.  Otherwise
``env update --prune`` is tried first; if it fails on a lockfile spec
(current libmamba cannot re-solve against conda-lock files), the env is
either left as-is when its stamped lockfile sha256 already matches (nothing
to do) or removed and recreated (the pinned lockfile makes recreation exactly
reproduce the target state).  ``--env-dir`` (a directory or base URL) skips
the pointer and takes ``<env-dir>/<name>-lock.yml`` as is, unverified::

    # pinned release (repo clone: its pointer; curl | python3: main's):
    python3 install/mamba_env.py install --name system

    # explicit local directory:
    python3 install/mamba_env.py install --name py312 --env-dir /path/to/conda

    # explicit remote base, e.g. one particular release:
    curl -fsSL https://raw.githubusercontent.com/ickc/bootstrapping-os-environments/main/install/mamba_env.py | \\
        python3 - install --name system \\
        --env-dir https://github.com/ickc/bootstrapping-os-environments/releases/download/conda-2026.11.16
"""

import argparse
import contextlib
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterator, List, Optional, Set

from bsos.installers._download import download_file, fetch_text
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._locks import (
    POINTER_NAME,
    REMOTE_POINTER_URL,
    LockChecksumError,
    LockPointer,
    LockPointerError,
    fetch_lock,
    parse_pointer,
    read_pointer,
    sha256_file,
)
from bsos.installers._subprocess import find_command, run

# platform_key() -> conda subdir token (this installer's analog of Artifact.targets).
_CONDA_ARCH = {
    "Darwin-arm64": "osx-arm64",
    "Darwin-x86_64": "osx-64",
    "Linux-x86_64": "linux-64",
    "Linux-aarch64": "linux-aarch64",
}

# Canonical remote base for the --no-lock specs, used when no bundled conda/ dir
# is found (e.g. curl | python3). The conda-lock files come from the release the
# lock pointer names instead (see _pinned_lock).
_REMOTE_ENV_DIR = "https://raw.githubusercontent.com/ickc/bootstrapping-os-environments/main/conda"


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
    """Bundled ``conda/`` dir when running from a clone, else the remote base (``--no-lock``)."""
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


# Records the sha256 of the lockfile an env was created from, so a forced
# update can skip the recreate when the lockfile is unchanged (the lockfile
# fully determines the env, so an equal hash means the env is already
# converged). Lives in conda-meta/ so it travels with the env.
_LOCK_STAMP = ".bsos-lock-sha256"


def _lock_stamp_path(prefix: Path) -> Path:
    return prefix / "conda-meta" / _LOCK_STAMP


def _env_filename(name: str, lock: bool) -> str:
    """Spec filename for *name*: the unified conda-lock file, or with
    *lock=False* the per-platform YAML."""
    return f"{name}-lock.yml" if lock else f"{name}_{_conda_arch()}.yml"


@contextlib.contextmanager
def _env_spec(base: str, filename: str) -> Iterator[Path]:
    """Yield a local path to ``<base>/<filename>``.

    *base* is a local directory or an ``http(s)://`` base URL; a remote file is
    downloaded into a temp directory that is removed on exit.  The local
    filename is preserved so the backends still see the ``-lock.yml`` suffix
    that marks a conda-lock file.
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
            print(f"Env spec not found: {path}", file=sys.stderr)
            sys.exit(1)
        yield path


def _load_pointer(conda_dir: Optional[Path]) -> LockPointer:
    """The lock pointer of the clone's *conda_dir*, or main's without a clone; exit 1 if unreadable."""
    try:
        if conda_dir is not None:
            return read_pointer(conda_dir / POINTER_NAME)
        return parse_pointer(fetch_text(REMOTE_POINTER_URL), REMOTE_POINTER_URL)
    except (OSError, LockPointerError) as exc:
        print(f"Cannot read the conda lock pointer: {exc}", file=sys.stderr)
        sys.exit(1)


def _warn_if_unpinned(local: Path, conda_dir: Path) -> None:
    """Say so on stderr when *local* is not the lock the pointer pins.

    A local lock wins over the pinned release — it is what
    ``pixi run conda-generate`` just wrote — so a forgotten one would
    otherwise shadow the release silently.
    """
    try:
        expected: Optional[str] = read_pointer(conda_dir / POINTER_NAME).expected(local.name)
    except (OSError, LockPointerError):
        expected = None
    actual = sha256_file(local)
    if actual == expected:
        return
    pinned = f"pins {expected}" if expected else "has no usable entry for it"
    print(
        f"WARNING: using the local {local} (sha256 {actual}), not the pinned lock: "
        f"{conda_dir / POINTER_NAME} {pinned}. Delete the local file to install the pinned release.",
        file=sys.stderr,
    )


@contextlib.contextmanager
def _pinned_lock(name: str, stamp: Optional[Path]) -> Iterator[Optional[Path]]:
    """Yield a local path to the conda-lock file for *name* (default ``--env-dir``).

    A local ``conda/<name>-lock.yml`` in the clone wins (see
    :func:`_warn_if_unpinned`); otherwise the lock is downloaded from the
    release the pointer names and verified against its sha256 — a mismatch
    exits 1.  When *stamp* (an existing env's lock stamp) already records the
    pointer's sha256, the env is converged: yield ``None``, download nothing.
    """
    filename = _env_filename(name, lock=True)
    conda_dir = _find_bundled_conda_dir()
    if conda_dir is not None and (conda_dir / filename).is_file():
        local = conda_dir / filename
        _warn_if_unpinned(local, conda_dir)
        yield local
        return
    pointer = _load_pointer(conda_dir)
    try:
        expected = pointer.expected(filename)
    except LockPointerError as exc:
        print(f"Cannot install {name!r}: {exc}", file=sys.stderr)
        sys.exit(1)
    if stamp is not None and stamp.is_file() and stamp.read_text().strip() == expected:
        yield None
        return
    tmp = Path(tempfile.mkdtemp(prefix="bsos-env-"))
    try:
        print(f"Fetching {filename} from release {pointer.tag} ...")
        try:
            spec = fetch_lock(pointer, filename, tmp)
        except (OSError, LockChecksumError) as exc:
            print(f"Cannot fetch the pinned {filename}: {exc}", file=sys.stderr)
            sys.exit(1)
        yield spec
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _write_lock_stamp(prefix: Path, spec: Path) -> None:
    stamp = _lock_stamp_path(prefix)
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(sha256_file(spec) + "\n")


def _create_env(tool: Path, backend: str, name: str, prefix: Path, spec: Path, env: EnvConfig, lock: bool) -> None:
    """Create *prefix* from *spec*, stamping the lockfile hash on success.

    Always uses ``env create`` (not the bare ``create`` subcommand): mamba
    (conda-based) only parses the full environment.yml/conda-lock schema
    through its ``env`` module — plain ``create -f`` there expects an
    explicit spec list instead. micromamba's ``env create`` is a documented
    alias of its ``create``, so this is a no-op change for that backend.
    """
    print(f"Creating conda env {name!r} at {prefix} via {backend} ...")
    argv = [str(tool), "env", "create", "-y", "-p", str(prefix), "-f", str(spec)]
    run(argv, env=env.subprocess_env())
    if lock:
        _write_lock_stamp(prefix, spec)


def _update_env(tool: Path, backend: str, name: str, prefix: Path, spec: Path, env: EnvConfig, lock: bool) -> None:
    """Converge an existing *prefix* onto *spec*.

    ``env update --prune`` is tried first — it keeps the spec authoritative
    and is the cheap in-place path whenever the backend can handle the spec.
    Current libmamba cannot re-solve against a conda-lock file (it fails
    re-parsing exact-pin specs), so on failure with a lockfile spec: if the
    stamped lockfile sha256 already matches, the env is converged and there
    is nothing to do; otherwise recreate from scratch — the lockfile pins
    every package, so recreation reproduces the target state exactly.
    """
    print(f"Updating conda env {name!r} at {prefix} via {backend} ...")
    argv = [str(tool), "env", "update", "-y", "-p", str(prefix), "-f", str(spec), "--prune"]
    result = run(argv, env=env.subprocess_env(), check=False)
    if result.returncode == 0:
        if lock:
            _write_lock_stamp(prefix, spec)
        return
    if not lock:
        sys.exit(result.returncode)
    stamp = _lock_stamp_path(prefix)
    if stamp.is_file() and stamp.read_text().strip() == sha256_file(spec):
        print(f"Conda env {name!r} at {prefix} already matches {spec.name}; nothing to do")
        return
    print(
        f"env update failed (exit {result.returncode}); recreating {prefix} from {spec.name}",
        file=sys.stderr,
    )
    shutil.rmtree(prefix)
    _create_env(tool, backend, name, prefix, spec, env, lock)


def install(
    name: str = "system",
    env_dir: Optional[str] = None,
    env: Optional[EnvConfig] = None,
    force: bool = False,
    backend: str = _DEFAULT_BACKEND,
    lock: bool = True,
) -> None:
    """Create a named conda environment, or skip if it already exists.

    With *force=True* (the ``update`` action), an existing env is converged
    onto the spec (see ``_update_env``); a missing env is created as normal.
    *backend* selects the package manager (``micromamba`` or ``mamba``).

    The env spec is ``<name>-lock.yml`` (version-pinned, default) or, with
    *lock=False*, ``<name>_<conda-arch>.yml``.  An explicit *env_dir* (a
    local directory or an ``http(s)://`` base URL) is used as is.  Without
    one, a lock comes from the release the lock pointer names, unless the
    clone has a local copy (see :func:`_pinned_lock`), and a ``--no-lock``
    spec from the bundled ``conda/`` dir, else the canonical remote base.
    """
    env = env or EnvConfig()

    tool = _require_backend(backend, env)
    if tool is None:
        sys.exit(1)

    prefix = env.opt_root / name
    if not force and prefix.exists():
        print(f"Conda env {name!r} already exists at {prefix}; run 'update' to refresh")
        return

    spec_source: "contextlib.AbstractContextManager[Optional[Path]]"
    if env_dir is None and lock:
        spec_source = _pinned_lock(name, _lock_stamp_path(prefix) if prefix.exists() else None)
    else:
        base = env_dir if env_dir is not None else _default_env_dir()
        spec_source = _env_spec(base, _env_filename(name, lock))
    with spec_source as spec:
        if spec is None:
            print(f"Conda env {name!r} at {prefix} already matches the pinned {name}-lock.yml; nothing to do")
        elif prefix.exists():
            _update_env(tool, backend, name, prefix, spec, env, lock)
        else:
            _create_env(tool, backend, name, prefix, spec, env, lock)
    print(f"Conda env {name!r} ready at {prefix}")


def uninstall(name: str = "system", env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    prefix = env.opt_root / name
    if prefix.exists():
        shutil.rmtree(prefix)
        print(f"Removed conda env at {prefix}")
    else:
        print(f"{prefix} not found", file=sys.stderr)


def _unresolved_libraries(prefix: Path, env: EnvConfig) -> List[str]:
    """ELF executables in ``<prefix>/bin`` with a shared library that fails to resolve.

    An env can solve and install cleanly and still ship a binary that cannot
    start: when a feedstock stops being rebuilt, the solver falls back to an
    old build linked against libraries the env no longer provides (w3m's 2017
    build wanting ``libssl.so.1.0.0``).  Neither the lockfile nor ``env list``
    shows that; asking the dynamic loader does.

    Linux only, via ``ldd``.  Returns one ``"<name>: <lib>, <lib>"`` entry per
    broken executable — empty when everything loads, and also when the check
    does not apply (another OS, or no ``ldd`` on PATH).
    """
    if env.ostype != "Linux":
        return []
    ldd = find_command("ldd")
    bin_dir = prefix / "bin"
    if ldd is None or not bin_dir.is_dir():
        return []
    broken: List[str] = []
    seen: Set[Path] = set()
    for entry in sorted(bin_dir.iterdir()):
        try:
            real = entry.resolve()
            if real in seen or not real.is_file():
                continue
            seen.add(real)
            with real.open("rb") as f:
                if f.read(4) != b"\x7fELF":
                    continue
        except OSError:
            continue
        # ldd exits non-zero for static binaries; only its report matters here.
        result = run([ldd, str(real)], env=env.subprocess_env(), check=False, capture_output=True, text=True)
        missing = [line.split("=>")[0].strip() for line in (result.stdout or "").splitlines() if "not found" in line]
        if missing:
            broken.append(f"{entry.name}: {', '.join(missing)}")
    return broken


def test_install(name: str = "system", env: Optional[EnvConfig] = None, backend: str = _DEFAULT_BACKEND) -> int:
    """Validate that the named conda env exists and its executables can load.

    Skips cleanly (exit 0) on unsupported platforms.  Fails (exit 1) if the
    chosen *backend* is absent — a missing prerequisite, not a platform limit —
    or if an executable in the env has unresolved shared libraries (Linux).
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
    if result.returncode != 0:
        return int(result.returncode)
    broken = _unresolved_libraries(prefix, env)
    if broken:
        print(f"Conda env {name!r} at {prefix} has executables that cannot load:", file=sys.stderr)
        for line in broken:
            print(f"  {line}", file=sys.stderr)
        return 1
    return 0


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
        help="directory or base URL holding <name>-lock.yml (or <name>_<arch>.yml with --no-lock), used "
        "unverified (default: a local conda/<name>-lock.yml in the clone, else the release named by "
        "conda/locks.sha256, verified)",
    )
    parser.add_argument(
        "--no-lock",
        action="store_true",
        default=False,
        help="use the per-platform <name>_<arch>.yml spec instead of the pinned <name>-lock.yml",
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
    lock = not args.no_lock
    if args.action == "install":
        install(args.name, args.env_dir, env, backend=args.backend, lock=lock)
    elif args.action == "update":
        install(args.name, args.env_dir, env, force=True, backend=args.backend, lock=lock)
    elif args.action == "reinstall":
        uninstall(args.name, env)
        install(args.name, args.env_dir, env, backend=args.backend, lock=lock)
    elif args.action == "uninstall":
        uninstall(args.name, env)
    else:
        sys.exit(test_install(args.name, env, backend=args.backend))


if __name__ == "__main__":
    main()

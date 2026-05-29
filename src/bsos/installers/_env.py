"""Envoy environment configuration — single source of truth.

Defines all envoy-managed environment variables and their derivation logic,
and generates the shell ``env.sh`` script from the same definitions.

stdlib only; targets Python 3.10+.
"""

import os
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple

# Inherited env vars that are safe/useful to pass to installer subprocesses.
_INHERIT_KEYS = (
    "HOME",
    "USER",
    "LOGNAME",
    "TERM",
    "PATH",
    "LANG",
    "LC_ALL",
    "TMPDIR",
    "SHELL",
    "SSH_AUTH_SOCK",
)


def detect_platform() -> Tuple[str, str]:
    """Detect OS and architecture, matching ``uname -sm`` output."""
    return platform.system(), platform.machine()


def platform_key() -> str:
    """Return ``<ostype>-<arch>`` for use in URL/archive dispatch tables."""
    ostype, arch = detect_platform()
    return f"{ostype}-{arch}"


class EnvConfig:
    """Compute envoy-managed paths, respecting pre-existing env vars.

    Path-like attributes are :class:`pathlib.Path`; the env-var mapping
    (:meth:`as_dict`) stringifies them.  An empty pre-existing value is
    treated as unset, matching the shell ``${VAR:-default}`` semantics.
    """

    def __init__(self, environ: Optional[Dict[str, str]] = None) -> None:
        env = dict(environ) if environ is not None else dict(os.environ)

        self.ostype, self.arch = detect_platform()
        self.home = Path(env.get("HOME") or Path.home())

        appdir = env.get("__APPDIR", "")
        self.local_root = Path(
            env.get("__LOCAL_ROOT")
            or (f"{appdir}/local" if appdir else self.home / ".local")
        )
        self.opt_root = Path(
            env.get("__OPT_ROOT") or self.local_root / "opt" / f"{self.ostype}-{self.arch}"
        )

        self.mamba_root_prefix = Path(env.get("MAMBA_ROOT_PREFIX") or self.opt_root / "miniforge3")
        self.pixi_home = Path(env.get("PIXI_HOME") or self.opt_root / "pixi")
        self.zim_home = Path(env.get("ZIM_HOME") or self.home / ".zim")

        self.xdg_config_home = Path(env.get("XDG_CONFIG_HOME") or self.home / ".config")
        self.xdg_data_home = Path(env.get("XDG_DATA_HOME") or self.local_root / "share")
        self.xdg_state_home = Path(env.get("XDG_STATE_HOME") or self.local_root / "state")
        self.xdg_cache_home = Path(env.get("XDG_CACHE_HOME") or self.home / ".cache")

        self.bin_dir = self.opt_root / "bin"

    def as_dict(self) -> Dict[str, str]:
        """All envoy-managed vars as a flat ``str``-valued dict."""
        return {
            "__OSTYPE": self.ostype,
            "__ARCH": self.arch,
            "__LOCAL_ROOT": str(self.local_root),
            "__OPT_ROOT": str(self.opt_root),
            "MAMBA_ROOT_PREFIX": str(self.mamba_root_prefix),
            "PIXI_HOME": str(self.pixi_home),
            "ZIM_HOME": str(self.zim_home),
            "XDG_CONFIG_HOME": str(self.xdg_config_home),
            "XDG_DATA_HOME": str(self.xdg_data_home),
            "XDG_STATE_HOME": str(self.xdg_state_home),
            "XDG_CACHE_HOME": str(self.xdg_cache_home),
        }

    def subprocess_env(self) -> Dict[str, str]:
        """Controlled environment for installer subprocesses.

        A minimal base of inherited vars plus all envoy-managed vars, so
        child processes don't inherit unrelated env state.
        """
        env = {key: os.environ[key] for key in _INHERIT_KEYS if key in os.environ}
        env.update(self.as_dict())
        return env


def generate_env_sh() -> str:
    """Generate the shell ``env.sh`` script from the Python definitions.

    Functionally equivalent to the env derivation above: same variable
    names, same ``${VAR:-default}`` fallback semantics.  This function is
    the single generator — ``env.sh`` is a derived artifact, so other
    shells can keep sourcing it while ``_env.py`` is the source of truth.
    """
    return """\
# Shell library: envoy installer path detection.
# Source from shell startup to set envoy-managed paths.
# Respects pre-existing values — dotfiles may set __APPDIR, XDG vars, etc. first.
#
# GENERATED from bsos.installers._env — do not edit. Regenerate with:
#   pixi run generate-env-sh

# Platform detection (always re-detected — pure platform facts)
# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"
export __OSTYPE __ARCH

# Path derivation (respects __APPDIR if pre-set by dotfiles)
export __LOCAL_ROOT="${__LOCAL_ROOT:-${__APPDIR:+${__APPDIR}/local}}"
export __LOCAL_ROOT="${__LOCAL_ROOT:-${HOME}/.local}"
export __OPT_ROOT="${__OPT_ROOT:-${__LOCAL_ROOT}/opt/${__OSTYPE}-${__ARCH}}"

# Tool paths
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-${__OPT_ROOT}/miniforge3}"
export PIXI_HOME="${PIXI_HOME:-${__OPT_ROOT}/pixi}"
export ZIM_HOME="${ZIM_HOME:-${HOME}/.zim}"

# XDG base dirs
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-${__LOCAL_ROOT}/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-${__LOCAL_ROOT}/state}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"
"""


if __name__ == "__main__":
    print(generate_env_sh(), end="")

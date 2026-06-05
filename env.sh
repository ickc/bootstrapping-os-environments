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

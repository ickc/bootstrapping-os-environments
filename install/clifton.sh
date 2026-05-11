#!/usr/bin/env bash

set -euo pipefail

# Minimal env for envoy installer scripts. Inlined by compile.sh.
# __OSTYPE/__ARCH always re-detected (pure platform facts).
# All derived vars respect pre-existing values via ${VAR:-default},
# so dotfiles-set values (e.g. __APPDIR) propagate correctly.
# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"
export __OSTYPE __ARCH
export __LOCAL_ROOT="${__LOCAL_ROOT:-${__APPDIR:+${__APPDIR}/local}}"
export __LOCAL_ROOT="${__LOCAL_ROOT:-${HOME}/.local}"
export __OPT_ROOT="${__OPT_ROOT:-${__LOCAL_ROOT}/opt/${__OSTYPE}-${__ARCH}}"
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-${__OPT_ROOT}/miniforge3}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-${__LOCAL_ROOT}/share}"
export ZIM_HOME="${ZIM_HOME:-${HOME}/.zim}"
BINDIR="${__OPT_ROOT}/bin"

# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"

clifton_install() {
    case "${__OSTYPE}-${__ARCH}" in
        Darwin-arm64) filename="clifton-macos-aarch64" ;;
        Darwin-x86_64) filename="clifton-macos-x86_64" ;;
        Linux-x86_64) filename="clifton-linux-musl-x86_64" ;;
        Linux-aarch64) filename="clifton-linux-musl-aarch64" ;;
        *) exit 1 ;;
    esac
    url="https://github.com/isambard-sc/clifton/releases/latest/download/${filename}"

    mkdir -p "${BINDIR}"
    if command -v curl > /dev/null; then
        curl -fL "${url}" -o "${BINDIR}/clifton"
    elif command -v wget > /dev/null; then
        wget "${url}" -O "${BINDIR}/clifton"
    fi
    chmod +x "${BINDIR}/clifton"
}

clifton_uninstall() {
    rm -f "${BINDIR}/clifton"
}

case "${1:-}" in
    install)
        clifton_install
        ;;
    uninstall)
        clifton_uninstall
        ;;
    *)
        echo "Usage: __OPT_ROOT=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

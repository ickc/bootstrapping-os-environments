#!/usr/bin/env bash

set -euo pipefail

# Shell library: envoy installer path detection.
# Source from shell startup to set envoy-managed paths.
# Respects pre-existing values — dotfiles may set __APPDIR, XDG vars, etc. first.

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
BINDIR="${__OPT_ROOT}/bin"

# https://unix.stackexchange.com/a/84980/192799
DOWNLOADDIR="$(mktemp -d 2> /dev/null || mktemp -d -t 'codex')"

# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"

codex_latest_tag() {
    local release_json
    local tag

    if command -v curl > /dev/null; then
        release_json="$(curl -fsSL https://api.github.com/repos/openai/codex/releases/latest)"
    elif command -v wget > /dev/null; then
        release_json="$(wget -qO- https://api.github.com/repos/openai/codex/releases/latest)"
    else
        echo "curl or wget is required"
        exit 1
    fi

    tag="$(printf '%s\n' "${release_json}" | sed -n 's/.*"tag_name":[[:space:]]*"\([^\"]*\)".*/\1/p' | head -n1)"

    if [[ -z ${tag} ]]; then
        echo "Unable to determine the latest Codex version"
        exit 1
    fi

    printf '%s\n' "${tag}"
}

codex_install() {
    local tag
    local filename
    local binary
    local url
    tag="$(codex_latest_tag)"

    case "${__OSTYPE}-${__ARCH}" in
        "Linux-x86_64")
            filename="codex-x86_64-unknown-linux-musl.tar.gz"
            binary="codex-x86_64-unknown-linux-musl"
            ;;
        "Linux-aarch64")
            filename="codex-aarch64-unknown-linux-musl.tar.gz"
            binary="codex-aarch64-unknown-linux-musl"
            ;;
        "Darwin-x86_64")
            filename="codex-x86_64-apple-darwin.tar.gz"
            binary="codex-x86_64-apple-darwin"
            ;;
        "Darwin-arm64")
            filename="codex-aarch64-apple-darwin.tar.gz"
            binary="codex-aarch64-apple-darwin"
            ;;
        *)
            echo "Unsupported OS or architecture"
            exit 1
            ;;
    esac

    url="https://github.com/openai/codex/releases/download/${tag}/${filename}"

    cd "${DOWNLOADDIR}"

    if command -v curl > /dev/null; then
        curl -fL "${url}" -o "${filename}"
    elif command -v wget > /dev/null; then
        wget "${url}" -O "${filename}"
    fi

    tar -xzf "${filename}"

    mkdir -p "${BINDIR}"
    mv "${binary}" "${BINDIR}/codex"
    chmod +x "${BINDIR}/codex"

    cd - > /dev/null || exit 1
    rm -rf "${DOWNLOADDIR}"
}

codex_uninstall() {
    rm -rf "${BINDIR}/codex"
}

case "${1:-}" in
    install)
        codex_install
        ;;
    uninstall)
        codex_uninstall
        ;;
    *)
        echo "Usage: __OPT_ROOT=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

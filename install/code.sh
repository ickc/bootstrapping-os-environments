#!/usr/bin/env bash

set -euo pipefail

__OPT_ROOT="${__OPT_ROOT:-"${HOME}/.local/opt/${__OSTYPE}-${__ARCH}"}"
MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-"${__OPT_ROOT}/miniforge3"}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-"${HOME}/.config"}"
ZDOTDIR="${ZDOTDIR:-"${HOME}"}"
BINDIR="${__OPT_ROOT}/bin"

# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"

code_install() {
    case "${__OSTYPE}-${__ARCH}" in
        "Linux-x86_64")
            url="https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64"
            ;;
        "Linux-armv7l")
            url="https://code.visualstudio.com/sha/download?build=stable&os=cli-linux-armhf"
            ;;
        "Linux-aarch64")
            url="https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-arm64"
            ;;
        "Darwin-x86_64")
            url="https://code.visualstudio.com/sha/download?build=stable&os=cli-darwin-x64"
            ;;
        "Darwin-arm64")
            url="https://code.visualstudio.com/sha/download?build=stable&os=cli-darwin-arm64"
            ;;
        *)
            echo "Unsupported OS or architecture"
            exit 1
            ;;
    esac

    case "${__OSTYPE}" in
        Darwin)
            if command -v curl > /dev/null; then
                curl -L "${url}" -o vscode_cli.zip
            elif command -v wget > /dev/null; then
                wget "${url}" -O vscode_cli.zip
            fi
            unzip vscode_cli.zip
            rm vscode_cli.zip
            ;;
        Linux)
            if command -v curl > /dev/null; then
                # shellcheck disable=SC2312
                curl -fL "${url}" | tar -xz
            elif command -v wget > /dev/null; then
                # shellcheck disable=SC2312
                wget -O - "${url}" | tar -xz
            fi
            ;;
        *) ;;
    esac

    mkdir -p "${BINDIR}"
    mv code "${BINDIR}"
}

code_uninstall() {
    rm -rf "${BINDIR}/code"
}

case "${1:-}" in
    install)
        code_install
        ;;
    uninstall)
        code_uninstall
        ;;
    *)
        echo "Usage: __OPT_ROOT=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

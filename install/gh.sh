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
export PIXI_HOME="${PIXI_HOME:-${__OPT_ROOT}/pixi}"
export ZIM_HOME="${ZIM_HOME:-${HOME}/.zim}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-${__LOCAL_ROOT}/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-${__LOCAL_ROOT}/state}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"
BINDIR="${__OPT_ROOT}/bin"

# https://unix.stackexchange.com/a/84980/192799
DOWNLOADDIR="$(mktemp -d 2> /dev/null || mktemp -d -t 'gh')"

# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"

gh_latest_version() {
    local release_json
    local version

    if command -v curl > /dev/null; then
        release_json="$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest)"
    elif command -v wget > /dev/null; then
        release_json="$(wget -qO- https://api.github.com/repos/cli/cli/releases/latest)"
    else
        echo "curl or wget is required"
        exit 1
    fi

    version="$(printf '%s\n' "${release_json}" | sed -n 's/.*"tag_name":[[:space:]]*"v\([^\"]*\)".*/\1/p' | head -n1)"

    if [[ -z ${version} ]]; then
        echo "Unable to determine the latest GitHub CLI version"
        exit 1
    fi

    printf '%s\n' "${version}"
}

gh_install() {
    local version
    local filename
    local dirname
    local url
    version="$(gh_latest_version)"

    case "${__OSTYPE}-${__ARCH}" in
        "Linux-x86_64")
            filename="gh_${version}_linux_amd64.tar.gz"
            ;;
        "Linux-aarch64")
            filename="gh_${version}_linux_arm64.tar.gz"
            ;;
        "Darwin-x86_64")
            filename="gh_${version}_macOS_amd64.zip"
            ;;
        "Darwin-arm64")
            filename="gh_${version}_macOS_arm64.zip"
            ;;
        *)
            echo "Unsupported OS or architecture"
            exit 1
            ;;
    esac

    dirname="${filename%.tar.gz}"
    dirname="${dirname%.zip}"
    url="https://github.com/cli/cli/releases/download/v${version}/${filename}"

    cd "${DOWNLOADDIR}"

    if command -v curl > /dev/null; then
        curl -fL "${url}" -o "${filename}"
    elif command -v wget > /dev/null; then
        wget "${url}" -O "${filename}"
    fi

    case "${filename}" in
        *.zip)
            unzip "${filename}"
            ;;
        *.tar.gz)
            tar -xzf "${filename}"
            ;;
        *)
            echo "Unsupported archive format"
            exit 1
            ;;
    esac

    mkdir -p "${BINDIR}"
    mv "${dirname}/bin/gh" "${BINDIR}"

    cd - > /dev/null || exit 1
    rm -rf "${DOWNLOADDIR}"
}

gh_uninstall() {
    rm -rf "${BINDIR}/gh"
}

case "${1:-}" in
    install)
        gh_install
        ;;
    uninstall)
        gh_uninstall
        ;;
    *)
        echo "Usage: __OPT_ROOT=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

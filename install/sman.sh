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
# git 2.3.0 or later is required
export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

github_clone_git() {
    user="${1}"
    repo="${2}"
    git clone "git@github.com:${user}/${repo}.git"
}

github_clone_https() {
    user="${1}"
    repo="${2}"
    git clone "https://github.com/${user}/${repo}.git"
}

github_download_file_to() {
    user="${1}"
    repo="${2}"
    branch="${3}"
    file="${4}"
    dest="${5}"
    mkdir -p "${dest%/*}"
    curl -fSL "https://raw.githubusercontent.com/${user}/${repo}/refs/heads/${branch}/${file}" -o "${dest}"
}
VERSION=1.0.4
BINDIR="${__OPT_ROOT}/bin"

# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"

sman_install_bin() {
    case "${__OSTYPE}-${__ARCH}" in
        Darwin-arm64) GO_UNAME=darwin-arm64 ;;
        Darwin-x86_64) GO_UNAME=darwin-amd64 ;;
        Linux-x86_64) GO_UNAME=linux-amd64 ;;
        Linux-aarch64) GO_UNAME=linux-arm64 ;;
        Linux-ppc64le) GO_UNAME=linux-ppc64le ;;
        FreeBSD-amd64) GO_UNAME=freebsd-amd64 ;;
        *) exit 1 ;;
    esac
    filename="sman-${GO_UNAME}-v${VERSION}"
    url="https://github.com/ickc/sman/releases/download/v${VERSION}/${filename}.tgz"

    if command -v curl > /dev/null; then
        # shellcheck disable=SC2312
        curl -fL "${url}" | tar -xz
    elif command -v wget > /dev/null; then
        # shellcheck disable=SC2312
        wget -O - "${url}" | tar -xz
    fi
    mkdir -p "${BINDIR}"
    mv "${filename}" "${BINDIR}/sman"
}

sman_install_rc() {
    mkdir -p "${XDG_DATA_HOME}/sman"
    github_download_file_to ickc sman main sman.rc "${XDG_DATA_HOME}/sman/sman.rc"
}

sman_install_snippets() {
    local snippets_dir="${XDG_DATA_HOME}/sman/snippets"
    if [[ -d ${snippets_dir} ]]; then
        cd "${snippets_dir}"
        git pull
    else
        mkdir -p "${XDG_DATA_HOME}/sman"
        cd "${XDG_DATA_HOME}/sman"
        github_clone_git ickc sman-snippets
        mv sman-snippets snippets
    fi
}

sman_install() {
    sman_install_bin
    sman_install_rc
    sman_install_snippets
}

sman_uninstall() {
    rm -f "${BINDIR}/sman" "${XDG_DATA_HOME}/sman/sman.rc"
    rm -rf "${XDG_DATA_HOME}/sman/snippets"
}

case "${1:-}" in
    install)
        sman_install
        ;;
    uninstall)
        sman_uninstall
        ;;
    *)
        echo "Usage: __OPT_ROOT=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

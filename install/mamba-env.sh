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
print_double_line() {
    echo '================================================================================'
}

print_line() {
    echo '--------------------------------------------------------------------------------'
}
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
NAME="${NAME:-system}"

PREFIX="${__OPT_ROOT}/${NAME}"

# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"

get_conda_env_file() {
    case "${__OSTYPE}-${__ARCH}" in
        Darwin-arm64) CONDA_UNAME=osx-arm64 ;;
        Darwin-x86_64) CONDA_UNAME=osx-64 ;;
        Linux-x86_64) CONDA_UNAME=linux-64 ;;
        Linux-aarch64) CONDA_UNAME=linux-aarch64 ;;
        Linux-ppc64le) CONDA_UNAME=linux-ppc64le ;;
        *) exit 1 ;;
    esac
    local filename
    filename="${NAME}_${CONDA_UNAME}.yml"
    if [[ -z ${__MAMBA_ENV_DOWNLOAD+x} ]]; then
        # use local file
        # shellcheck disable=SC2312
        __MAMBA_ENV_FILE="conda/${filename}"
    else
        __MAMBA_ENV_FILE="${HOME}/${filename}"
        github_download_file_to ickc envoy main "conda/${filename}" "${__MAMBA_ENV_FILE}"
    fi
}

mamba_env_install() {
    get_conda_env_file
    if [[ -d ${PREFIX} ]]; then
        "${MAMBA_ROOT_PREFIX}/bin/mamba" env update -f "${__MAMBA_ENV_FILE}" -p "${PREFIX}" -y --prune
    else
        "${MAMBA_ROOT_PREFIX}/bin/mamba" env create -f "${__MAMBA_ENV_FILE}" -p "${PREFIX}" -y
    fi
    if [[ -n ${__MAMBA_ENV_DOWNLOAD+x} ]]; then
        rm -f "${__MAMBA_ENV_FILE}"
    fi
}

mamba_env_uninstall() {
    rm -rf "${PREFIX}"
}

case "${1:-}" in
    install)
        mamba_env_install
        ;;
    uninstall)
        mamba_env_uninstall
        ;;
    *)
        echo "Usage: MAMBA_ROOT_PREFIX=... __OPT_ROOT=... NAME=(system|py313|...) ${0} [install|uninstall]"
        exit 1
        ;;
esac

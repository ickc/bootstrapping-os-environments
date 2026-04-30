#!/usr/bin/env bash

set -euo pipefail

dotfiles_install() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local dotfiles_dir="${script_dir}/../dotfiles"
    local target_dir="${HOME}"
    local src dest

    for src in "${dotfiles_dir}"/.*; do
        [[ "$(basename "${src}")" == "." ]] && continue
        [[ "$(basename "${src}")" == ".." ]] && continue

        dest="${target_dir}/$(basename "${src}")"

        if [[ -L ${dest} ]]; then
            echo "already a symlink, skipping: ${dest}"
            continue
        fi

        if [[ -e ${dest} ]]; then
            echo "backing up existing file: ${dest} -> ${dest}.bak"
            mv "${dest}" "${dest}.bak"
        fi

        ln -s "${src}" "${dest}"
        echo "linked: ${dest} -> ${src}"
    done
}

dotfiles_uninstall() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local dotfiles_dir="${script_dir}/../dotfiles"
    local target_dir="${HOME}"
    local src dest

    for src in "${dotfiles_dir}"/.*; do
        [[ "$(basename "${src}")" == "." ]] && continue
        [[ "$(basename "${src}")" == ".." ]] && continue

        dest="${target_dir}/$(basename "${src}")"

        if [[ -L ${dest} ]]; then
            rm "${dest}"
            echo "removed symlink: ${dest}"
        fi
    done
}

case "${1:-}" in
    install)
        dotfiles_install
        ;;
    uninstall)
        dotfiles_uninstall
        ;;
    *)
        echo "Usage: ${0} [install|uninstall]"
        exit 1
        ;;
esac

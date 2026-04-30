#!/usr/bin/env bash

set -euo pipefail

source ../lib/dotfiles.sh

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

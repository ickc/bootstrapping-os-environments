#!/usr/bin/env bash

set -e

zim_install() {
    curl -fsSL --create-dirs -o "${ZIM_HOME}/zimfw.zsh" https://github.com/zimfw/zimfw/releases/latest/download/zimfw.zsh
}

zim_uninstall() {
    rm -rf "${ZIM_HOME}"
}

case "${1:-}" in
    install)
        zim_install
        ;;
    uninstall)
        zim_uninstall
        ;;
    *)
        echo "Usage: ZIM_HOME=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

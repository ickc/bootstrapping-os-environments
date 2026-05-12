#!/usr/bin/env bash

set -euo pipefail

source ../../../env.sh
source ../lib/codex.sh

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

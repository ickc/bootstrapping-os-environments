#!/usr/bin/env bash

set -euo pipefail

source ../../../env.sh
source ../lib/code.sh

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

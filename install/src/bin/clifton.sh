#!/usr/bin/env bash

set -euo pipefail

source ../../../env.sh
source ../lib/clifton.sh

case "${1:-}" in
    install)
        clifton_install
        ;;
    uninstall)
        clifton_uninstall
        ;;
    *)
        echo "Usage: __OPT_ROOT=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

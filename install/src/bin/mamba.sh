#!/usr/bin/env bash

set -euo pipefail

source ../../../env.sh
source ../lib/util/helpers.sh
source ../lib/mamba.sh

case "${1:-}" in
    install)
        mamba_install
        ;;
    uninstall)
        mamba_uninstall
        ;;
    *)
        echo "Usage: MAMBA_ROOT_PREFIX=... ${0} [install|uninstall]"
        exit 1
        ;;
esac

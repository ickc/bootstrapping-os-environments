#!/usr/bin/env bash

set -euo pipefail

source ../../../env.sh
source ../lib/util/helpers.sh
source ../lib/util/git.sh
source ../lib/mamba-env.sh

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

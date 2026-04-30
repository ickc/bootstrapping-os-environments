if [[ -z ${__BASHRC_SOURCED} ]]; then
    export __BASHRC_SOURCED=1
    # shellcheck disable=SC1090
    . ~/.bashrc
fi

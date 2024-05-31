#!/usr/bin/env bash

set -e

# install reload-browser for entr
PREFIX="${PREFIX:-"${HOME}/.local"}"

# https://unix.stackexchange.com/a/84980/192799
DOWNLOADDIR="$(mktemp -d 2> /dev/null || mktemp -d -t 'zsh')"

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

install() {
    print_double_line
    echo Downloading to temp dir "${DOWNLOADDIR}"
    cd "${DOWNLOADDIR}"
    curl -L -O https://eradman.com/entrproject/scripts/reload-browser
    chmod +x reload-browser

    print_line
    echo Installing to "${PREFIX}/bin"
    mkdir -p "${PREFIX}/bin"
    mv reload-browser "${PREFIX}/bin"

    print_line
    echo Removing temp dir "${DOWNLOADDIR}"
    rm -rf "${DOWNLOADDIR}"
}

install

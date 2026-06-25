#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-${HOME}/.local}"
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
    # shellcheck disable=SC2312
    SYSTEM="$(uname -s)-$(uname -m)"

    # Determine the appropriate file based on the system information
    case "${SYSTEM}" in
        Darwin-aarch64)
            filename="difft-aarch64-apple-darwin.tar.gz"
            ;;
        Linux-aarch64)
            filename="difft-aarch64-unknown-linux-gnu.tar.gz"
            ;;
        Darwin-x86_64)
            filename="difft-x86_64-apple-darwin.tar.gz"
            ;;
        Linux-x86_64)
            filename="difft-x86_64-unknown-linux-gnu.tar.gz"
            ;;
        *)
            echo "Unsupported system: ${SYSTEM}"
            exit 1
            ;;
    esac
    downloadUrl="https://github.com/Wilfred/difftastic/releases/latest/download/${filename}"

    print_double_line
    echo Downloading to temp dir "${DOWNLOADDIR}"
    cd "${DOWNLOADDIR}"
    wget "${downloadUrl}"
    tar -xf "${filename}"
    ls -R

    print_double_line
    echo Installing to ${PREFIX}/bin...
    mkdir -p "${PREFIX}/bin"
    mv difft "${PREFIX}/bin"

    print_line
    echo Removing temp dir "${DOWNLOADDIR}"
    rm -rf "${DOWNLOADDIR}"
}

install

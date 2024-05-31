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

downloadUrl=https://github.com/aristocratos/btop/releases/latest/download/btop-x86_64-linux-musl.tbz
filename="${downloadUrl##*/}"

print_double_line
echo Downloading to temp dir "${DOWNLOADDIR}"
cd "${DOWNLOADDIR}"
wget "${downloadUrl}"
tar -xf "${filename}"

print_double_line
echo Installing...
cd btop
export PREFIX
make install

print_line
echo Removing temp dir "${DOWNLOADDIR}"
rm -rf "${DOWNLOADDIR}"

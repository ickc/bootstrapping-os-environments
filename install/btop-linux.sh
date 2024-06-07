#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-${HOME}/.local}"
CC="${CC:-CC}"
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

print_double_line
echo Downloading to temp dir "${DOWNLOADDIR}"
cd "${DOWNLOADDIR}"
git clone https://github.com/aristocratos/btop.git
cd btop
LATEST_TAG="$(git describe --tags "$(git rev-list --tags --max-count=1)")"
git checkout "${LATEST_TAG}"

print_double_line
echo "Compiling ${LATEST_TAG}..."
make CXX="${CC}" ADDFLAGS='-march=native -mtune=native'
print_line
echo "Installing to ${PREFIX}..."
export PREFIX
make install

print_line
echo Removing temp dir "${DOWNLOADDIR}"
rm -rf "${DOWNLOADDIR}"

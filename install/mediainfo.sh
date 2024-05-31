#!/usr/bin/env bash

set -e

VERSION=20.09
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
downloadUrl="https://mediaarea.net/download/binary/mediainfo/${VERSION}/mediainfo-${VERSION}.glibc2.3-x86_64.AppImage"
filename="${downloadUrl##*/}"

print_double_line
echo Downloading to temp dir "${DOWNLOADDIR}"
cd "${DOWNLOADDIR}"
wget "${downloadUrl}"

print_double_line
echo Installing to ${PREFIX}/bin...
mv "${filename}" "${PREFIX}/bin/mediainfo"
chmod +x "${PREFIX}/bin/mediainfo"

print_line
echo Removing temp dir "${DOWNLOADDIR}"
rm -rf "${DOWNLOADDIR}"

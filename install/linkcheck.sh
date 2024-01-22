#!/usr/bin/env bash

set -e

VERSION=3.0.0
PREFIX="${PREFIX:-$HOME/.local}"
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
downloadUrl="https://github.com/filiph/linkcheck/releases/download/$VERSION/linkcheck-$VERSION-linux-x64.tar.gz"
filename="${downloadUrl##*/}"

print_double_line
echo Downloading to temp dir "$DOWNLOADDIR"
cd "$DOWNLOADDIR"
wget "$downloadUrl"
tar -xf "$filename"
ls -R

print_double_line
echo Installing to $PREFIX/bin...
mkdir -p "$PREFIX/bin"
mv linkcheck/linkcheck "$PREFIX/bin"

print_line
echo Removing temp dir "$DOWNLOADDIR"
rm -rf "$DOWNLOADDIR"

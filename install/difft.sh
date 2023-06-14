#!/usr/bin/env bash

set -e

PREFIX=${PREFIX:-~/.local}
# https://unix.stackexchange.com/a/84980/192799
DOWNLOADDIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'zsh')"

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

downloadUrl=https://github.com/Wilfred/difftastic/releases/latest/download/difft-x86_64-unknown-linux-gnu.tar.gz
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
mv difft "$PREFIX/bin"

print_line
echo Removing temp dir "$DOWNLOADDIR"
rm -rf "$DOWNLOADDIR"

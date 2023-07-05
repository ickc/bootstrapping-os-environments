#!/usr/bin/env bash

set -e
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

# https://github.com/conda-forge/miniforge
downloadUrl='https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64'

download () {
print_double_line
echo Downloading to temp dir "$DOWNLOADDIR"
cd "$DOWNLOADDIR"
curl -L "$downloadUrl" -o vscode_cli.tar.gz
tar -xf vscode_cli.tar.gz
mkdir -p ~/.local/bin
mv code ~/.local/bin

print_line
echo Removing temp dir "$DOWNLOADDIR"
rm -rf "$DOWNLOADDIR"
}

download

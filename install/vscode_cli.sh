#!/usr/bin/env bash

set -e
# https://unix.stackexchange.com/a/84980/192799
DOWNLOADDIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'zsh')"
PREFIX="${PREFIX:-"$HOME/.local"}"

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

# Determine OS and architecture
os=$(uname -s) # Operating System
arch=$(uname -m) # Architecture
# Set downloadUrl based on OS and architecture
case "${os}-${arch}" in
    "Linux-x86_64")
        downloadUrl="https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64"
        ;;
    "Linux-armv7l")
        downloadUrl="https://code.visualstudio.com/sha/download?build=stable&os=cli-linux-armhf"
        ;;
    "Linux-aarch64")
        downloadUrl="https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-arm64"
        ;;
    "Darwin-x86_64")
        downloadUrl="https://code.visualstudio.com/sha/download?build=stable&os=cli-darwin-x64"
        ;;
    "Darwin-arm64")
        downloadUrl="https://code.visualstudio.com/sha/download?build=stable&os=cli-darwin-arm64"
        ;;
    *)
        echo "Unsupported OS or architecture"
        exit 1
        ;;
esac

echo "Download URL: $downloadUrl"


download () {
print_double_line
echo Downloading to temp dir "$DOWNLOADDIR"
cd "$DOWNLOADDIR"
curl -L "$downloadUrl" -o vscode_cli.tar.gz
tar -xf vscode_cli.tar.gz
mkdir -p "$PREFIX/bin"
mv -f code "$PREFIX/bin"

print_line
echo Removing temp dir "$DOWNLOADDIR"
rm -rf "$DOWNLOADDIR"
}

download

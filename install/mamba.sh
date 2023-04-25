#!/usr/bin/env bash

set -e

CONDA_PREFIX="${CONDA_PREFIX:-"$HOME/.mambaforge"}"
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
downloadUrl="https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"

print_double_line
echo Downloading to temp dir "$DOWNLOADDIR"
cd "$DOWNLOADDIR"
curl -L "$downloadUrl" --location --output Mambaforge.sh

print_double_line
echo Installing mamba...
chmod +x Mambaforge.sh
./Mambaforge.sh -b -s -p "$CONDA_PREFIX"

print_line
echo Removing temp dir "$DOWNLOADDIR"
rm -rf "$DOWNLOADDIR"

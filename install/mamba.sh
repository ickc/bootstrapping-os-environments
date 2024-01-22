#!/usr/bin/env bash

set -e

CONDA_PREFIX="${CONDA_PREFIX:-"$HOME/.miniforge3"}"
# https://unix.stackexchange.com/a/84980/192799
DOWNLOADDIR="$(mktemp -d 2> /dev/null || mktemp -d -t 'miniforge3')"

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

install() {
    # https://github.com/conda-forge/miniforge
    downloadUrl="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"

    print_double_line
    echo Downloading to temp dir "$DOWNLOADDIR"
    cd "$DOWNLOADDIR"
    curl -L "$downloadUrl" -o Miniforge3.sh

    print_double_line
    echo Installing mamba...
    chmod +x Miniforge3.sh
    ./Miniforge3.sh -b -s -p "$CONDA_PREFIX"

    print_line
    echo Removing temp dir "$DOWNLOADDIR"
    rm -rf "$DOWNLOADDIR"
}

install

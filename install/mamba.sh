#!/usr/bin/env bash

set -e

CONDA_PREFIX="${CONDA_PREFIX:-"$HOME/.mambaforge"}"

# https://github.com/conda-forge/miniforge
downloadUrl="https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"

curl -L "$downloadUrl" --location --output Mambaforge.sh

chmod +x Mambaforge.sh

./Mambaforge.sh -b -s -p "$CONDA_PREFIX"

rm -f Mambaforge.sh

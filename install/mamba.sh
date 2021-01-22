#!/usr/bin/env bash

set -e

CONDA_PREFIX="${CONDA_PREFIX:-"$HOME/.mambaforge"}"

# https://github.com/conda-forge/miniforge
case "$(uname -sm)" in
  Darwin\ x86_64)
    downloadUrl=https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-x86_64.sh
    ;;
  Linux\ x86_64)
    downloadUrl=https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
    ;;
  Linux\ aarch64)
    downloadUrl=https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-aarch64.sh
    ;;
esac

curl "$downloadUrl" --location --output Mambaforge.sh

chmod +x Mambaforge.sh

./Mambaforge.sh -b -s -p "$CONDA_PREFIX"

rm -f Mambaforge.sh

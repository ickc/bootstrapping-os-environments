#!/usr/bin/env bash

set -e

# * Define PREFIX if you want to install in a conda prefix instead
# PREFIX=
BINDIR=${BINDIR:-~/.local/bin}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

./../../src/bsos/conda_env.py -o temp.yml -n system -C conda-system.txt -v 3.9 -c conda-forge
if [[ -z ${PREFIX+x} ]]; then
    ENV_NAME=system39-conda-forge
    mamba env create -f temp.yml -n "$ENV_NAME"
    . activate "$ENV_NAME"
    PREFIX="$CONDA_PREFIX"
else
    mamba env create -f temp.yml -p "$PREFIX"
fi
rm -f temp.yml

mkdir -p "$BINDIR"
while read line; do
    ln -sf "$PREFIX/bin/$line" "$BINDIR"
done < conda-system-link.txt

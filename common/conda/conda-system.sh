#!/usr/bin/env bash

set -e

# * use UPDATE=1 to update the environment instead

# * Define PREFIX if you want to install in a conda prefix instead
# PREFIX=
BINDIR=${BINDIR:-~/.local/bin}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

./../../src/bsos/conda_env.py -o temp.yml -n system -C conda-system.txt -v 3.11 -c conda-forge
if [[ -z ${PREFIX+x} ]]; then
    ENV_NAME=system311-conda-forge
    if [[ -z "$UPDATE" ]]; then
        mamba env create -f temp.yml -n "$ENV_NAME"
    else
        mamba env update -f temp.yml -n "$ENV_NAME" --prune
    fi
    . activate "$ENV_NAME"
    PREFIX="$CONDA_PREFIX"
else
    if [[ -z "$UPDATE" ]]; then
        mamba env create -f temp.yml -p "$PREFIX"
    else
        mamba env update -f temp.yml -p "$PREFIX" --prune
    fi
fi
rm -f temp.yml

mkdir -p "$BINDIR"
while read line; do
    ln -sf "$PREFIX/bin/$line" "$BINDIR"
done < conda-system-link.txt

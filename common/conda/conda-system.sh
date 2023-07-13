#!/usr/bin/env bash

set -e

# * use UPDATE=1 to update the environment instead

# * Define PREFIX if you want to install in a conda prefix instead
# PREFIX=
BINDIR="${BINDIR:-$HOME/.local/bin}"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [[ "$(uname -m)" == ppc64le ]]; then
    TXT=conda-system-ppc64le.txt
else
    TXT=conda-system.txt
fi
./../../src/bsos/conda_env.py -o temp.yml -n system -C "$TXT" -v 3.11 -c conda-forge
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
    [[ -e "$PREFIX/bin/$line" ]] && ln -sf "$PREFIX/bin/$line" "$BINDIR"
done < conda-system-link.txt

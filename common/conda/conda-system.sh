#!/usr/bin/env bash

set -e

PREFIX=${PREFIX:-/global/common/software/polar/.conda/envs/system39-conda-forge}
BINDIR=${BINDIR:-/global/common/software/polar/local/bin}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

./conda_env.py -o temp.yml -n system -C conda-system.txt -v 3.9 -c conda-forge
mamba env create -f temp.yml -p "$PREFIX"
rm -f temp.yml

while read line; do
    ln -s "$PREFIX/bin/$line" "$BINDIR"
done < conda-system-link.txt

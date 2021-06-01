#!/usr/bin/env bash

set -e

# * Define PREFIX if you want to install in a conda prefix instead
# PREFIX=
BINDIR=${BINDIR:-~/.local/bin}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

./conda_env.py -o temp.yml -n system -C conda-system.txt -v 3.9 -c conda-forge
if [[ -z ${PREFIX+x} ]]; then
    mamba env create -f temp.yml -n system39-conda-forge
else
    mamba env create -f temp.yml -p "$PREFIX"
fi
rm -f temp.yml

mkdir -p "$BINDIR"
while read line; do
    ln -s "$PREFIX/bin/$line" "$BINDIR"
done < conda-system-link.txt

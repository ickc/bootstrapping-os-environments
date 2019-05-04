#!/usr/bin/env bash

set -e

url="git@github.com:lesgourg/class_public.git"

# set install directory
if [[ -n $NERSC_HOST ]]; then
    defaultDir=/global/common/software/polar/git
else
    defaultDir="$HOME/git/fork"
fi
INSTALLDIR="${INSTALLDIR:-$defaultDir}"
mkdir -p "$INSTALLDIR"
cd "$INSTALLDIR"

# obtain class
git clone "$url" class
cd class
make clean

# compile
if [[ $(uname) == Darwin ]]; then
    make -j$(nproc) OPTFLAG='-Ofast -ffast-math -march=native' CC=gcc-8
else
    make -j$(nproc) OPTFLAG='-Ofast -ffast-math -march=native'
fi
cd python
python setup.py install --user

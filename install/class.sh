#!/usr/bin/env bash

# install class on all *-(defaults|intel) conda environments
# can be invoked repeatedly to update

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

# obtain class
cd "$INSTALLDIR"
git clone "$url" class || (cd class && git pull)

# compile
cd class
make clean
if [[ $(uname) == Darwin ]]; then
    make -j$(nproc) OPTFLAG='-Ofast -ffast-math -march=native' CC=gcc-8
else
    make -j$(nproc) OPTFLAG='-Ofast -ffast-math -march=native'
fi

# install in all conda environments that ends in -defaults or -intel
cd python
for i in $(grep -E -- '-(defaults|intel)' ~/.conda/environments.txt); do
    . activate $i
    python setup.py install
done

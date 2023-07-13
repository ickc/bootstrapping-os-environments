#!/usr/bin/env bash

# install class on all *-(defaults|intel) conda environments
# set INSTALLDIR to customize where the git repo is located
# can be invoked repeatedly to update
# before running this script, an environment with Cython is needed
# to be loaded first

set -e

url="git@github.com:lesgourg/class_public.git"

print_log(){
	eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
	printf "$@\n"
}

# set install directory
if [[ -n $NERSC_HOST ]]; then
    defaultDir=/global/common/software/polar/git
	module swap gcc/8.2.0
else
    defaultDir="$HOME/git/fork"
fi
INSTALLDIR="${INSTALLDIR:-$defaultDir}"
NPROC="${NPROC:-$(nproc)}"
mkdir -p "$INSTALLDIR"

# obtain class
print_log "installing in $INSTALLDIR"
cd "$INSTALLDIR"
git clone "$url" class || (cd class && git reset --hard && git clean -d -f && git pull)

# compile
print_log "Compiling with $NPROC processors"
cd class
make clean

if [[ $(uname) == Darwin ]]; then
    make -j$NPROC OPTFLAG='-Ofast -ffast-math -march=native' CC=gcc-8
else
    make -j$NPROC OPTFLAG='-Ofast -ffast-math -march=native'
fi

# install in all conda environments that ends in -defaults or -intel
cd python
for i in $(grep -E -- '-(defaults|intel)' "$HOME/.conda/environments.txt"); do
	print_log "Install in Python at $i"
    . activate "$i"
	# allow this to fail in some environments
	python setup.py install || true
done

#!/usr/bin/env bash

set -e

url="git@github.com:andreimesinger/21cmFAST.git"

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$HOME/21cmfast"}"
VERSION=${VERSION-latest}
PREFIX="${PREFIX-"$HOME/21cmfast/local"}"

# c.f. https://stackoverflow.com/a/23378780/5769446
P="${P-$(if [[ "$(uname)" == Darwin ]]; then sysctl -n hw.physicalcpu_max; else lscpu -p | grep -E -v '^#' | sort -u -t, -k 2,4 | wc -l; fi)}"
echo "Using $P processes..."

print_log(){
	eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
	printf "$@\n"
}

print_log "clone 21cmfast to $TEMPDIR"

mkdir -p "$TEMPDIR"
cd "$TEMPDIR"
git clone "$url" || (cd 21cmFAST && git reset --hard && git clean -d -f && git pull)

# compile
print_log "Compiling with $NPROC processors"
cd 21cmFAST/Programs
make clean || true

if [[ $(uname) == Darwin ]]; then
    make -j$NPROC CC='gcc-8 -fopenmp -Ofast -ffast-math -march=native' CPPFLAGS="-I $PREFIX/include"
else
    make -j$NPROC CC='gcc -fopenmp -Ofast -ffast-math -march=native' CPPFLAGS="-I $PREFIX/include"
fi

#!/usr/bin/env bash

set -e

url="git@github.com:andreimesinger/21cmFAST.git"

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$HOME/21cmfast"}"
P=${P-$(getconf _NPROCESSORS_ONLN)}
VERSION=${VERSION-latest}
PREFIX="${PREFIX-"$HOME/21cmfast/local"}"

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

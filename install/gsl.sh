#!/usr/bin/env bash

set -e

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$HOME/21cmfast/gsl"}"
P=${P-$(getconf _NPROCESSORS_ONLN)}
VERSION=${VERSION-latest}
PREFIX="${PREFIX-"$HOME/21cmfast/local"}"

print_log(){
	eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
	printf "$@\n"
}

print_log "download gsl to $TEMPDIR"

mkdir -p "$TEMPDIR"
cd "$TEMPDIR"
wget -qO- http://reflection.oss.ou.edu/gnu/gsl/gsl-$VERSION.tar.gz | tar -xzf -

print_log configure

cd gsl-*
CFLAGS='-Ofast -ffast-math -march=native' ./configure --prefix=$PREFIX

# print_log make

make -j $P
make install

print_log cleanup

rm -rf "$TEMPDIR"

echo '# export these PATH'
# echo export PATH="$PREFIX/bin:\$PATH"
echo export LD_LIBRARY_PATH=$PREFIX/lib:\$LD_LIBRARY_PATH"
# echo export MANPATH="$PREFIX/share/man:\$MANPATH

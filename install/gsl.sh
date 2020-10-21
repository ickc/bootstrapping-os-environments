#!/usr/bin/env bash

set -e

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$HOME/21cmfast/gsl"}"
VERSION=${VERSION-latest}
PREFIX="${PREFIX-"$HOME/21cmfast/local"}"

# c.f. https://stackoverflow.com/a/23378780/5769446
P="${P-$([ $(uname) = 'Darwin' ] && sysctl -n hw.physicalcpu_max || lscpu -p | grep -E -v '^#' | sort -u -t, -k 2,4 | wc -l)}"
echo "Using $P processes..."

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

#!/usr/bin/env bash

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$SCRATCH/.libarchive"}"
# check newest at http://www.libarchive.org/
VERSION=${VERSION-3.6.1}
# assume using a conda environment
PREFIX="${PREFIX-"$CONDA_PREFIX"}"
CFLAGS="-O3 -fPIC"

# c.f. https://stackoverflow.com/a/23378780/5769446
P="${P-$(if [[ "$(uname)" == Darwin ]]; then sysctl -n hw.physicalcpu_max; else lscpu -p | grep -E -v '^#' | sort -u -t, -k 2,4 | wc -l; fi)}"
echo "Using $P processes..."

mkdir -p "$TEMPDIR" &&
cd "$TEMPDIR" &&
wget -qO- http://www.libarchive.org/downloads/libarchive-$VERSION.tar.gz | tar -xzf - &&
cd libarchive-$VERSION &&
CFLAGS="$CFLAGS" ./configure --prefix=$PREFIX &&

make -j $P &&
make install -j $P

rm -rf "$TEMPDIR" &&

echo '# export these PATH'
echo export PATH="$PREFIX/bin:\$PATH"
echo export LD_LIBRARY_PATH="$PREFIX/lib:\$LD_LIBRARY_PATH"
echo export MANPATH="$PREFIX/share/man:\$MANPATH"

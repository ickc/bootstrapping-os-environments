#!/usr/bin/env bash

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$SCRATCH/.libarchive"}"
VERSION=${VERSION-3.3.2}
PREFIX="${PREFIX-"$PBCOMMON/local"}"

# c.f. https://stackoverflow.com/a/23378780/5769446
P="${P-$([ $(uname) = 'Darwin' ] && sysctl -n hw.physicalcpu_max || lscpu -p | grep -E -v '^#' | sort -u -t, -k 2,4 | wc -l)}"
echo "Using $P processes..."

mkdir -p "$TEMPDIR" &&
cd "$TEMPDIR" &&
wget -qO- http://www.libarchive.org/downloads/libarchive-$VERSION.tar.gz | tar -xzf - &&
cd libarchive-$VERSION &&
./configure --prefix=$PREFIX &&

make -j $P &&
make install -j $P

rm -rf "$TEMPDIR" &&

echo '# export these PATH'
echo export PATH="$PREFIX/bin:\$PATH"
echo export LD_LIBRARY_PATH=$PREFIX/lib:\$LD_LIBRARY_PATH"
echo export MANPATH="$PREFIX/share/man:\$MANPATH"

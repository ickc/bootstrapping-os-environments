#!/usr/bin/env bash

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$SCRATCH/.libarchive"}"
P=${P-$(getconf _NPROCESSORS_ONLN)}
VERSION=${VERSION-3.3.2}
PREFIX="${PREFIX-"$PBCOMMON/local"}"

mkdir -p "$TEMPDIR" &&
cd "$TEMPDIR" &&
wget -qO- http://www.libarchive.org/downloads/libarchive-$VERSION.tar.gz | tar -xzf - &&
cd libarchive-$VERSION &&
./configure --prefix=$PREFIX &&

make -j $P &&
make install -j $P

rm -rf "$TEMPDIR"

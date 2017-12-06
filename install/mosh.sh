#!/usr/bin/env bash

# install mosh

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$HOME/.mosh"}"
P=${P-$(getconf _NPROCESSORS_ONLN)}
VERSION=${VERSION-1.3.2}
PREFIX="${PREFIX-"$HOME/.local"}"

mkdir -p "$TEMPDIR" &&
cd "$TEMPDIR" &&
wget -qO- https://mosh.org/mosh-$VERSION.tar.gz | tar -xzf - &&
cd mosh-$VERSION &&
if [[ -n $NERSC_HOST ]]; then
	# module load gcc/7.1.0 &&
	module load intel &&
	module load protobuf/3.0.0 &&
	protobuf_CFLAGS="-I$C_INCLUDE_PATH" protobuf_LIBS="-L$LD_LIBRARY_PATH" CC=icc CXX=icpc ./configure --prefix="$PREFIX" --disable-client || exit 1
else
	./configure --prefix="$PREFIX" || exit 1
fi

make V=1 -j $P &&
make V=1 install -j $P

rm -rf "$TEMPDIR" &&

echo '# export these PATH'
echo export PATH="$PREFIX/bin:\$PATH"
echo export MANPATH="$PREFIX/share/man:\$MANPATH"

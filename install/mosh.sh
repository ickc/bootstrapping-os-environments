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
	module swap PrgEnv-intel PrgEnv-gnu &&
	module load protobuf/2.6.1 &&
	protobuf_CFLAGS="-I$C_INCLUDE_PATH" protobuf_LIBS="-L$LD_LIBRARY_PATH" CC=cc CXX=CC ./configure --prefix="$PREFIX" || exit 1
else
	./configure --prefix="$PREFIX" || exit 1
fi

make -j $P &&
make install -j $P

rm -rf "$TEMPDIR" &&

echo '# export these PATH'
echo export PATH="$PREFIX/bin:\$PATH"
echo export MANPATH="$PREFIX/share/man:\$MANPATH"

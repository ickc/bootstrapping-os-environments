#!/usr/bin/env bash

# install mosh

# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$HOME/.mosh"}"
VERSION=${VERSION-1.3.2}
PREFIX="${PREFIX-"$HOME/.local"}"

# c.f. https://stackoverflow.com/a/23378780/5769446
P="${P-$([ $(uname) = 'Darwin' ] && sysctl -n hw.physicalcpu_max || lscpu -p | grep -E -v '^#' | sort -u -t, -k 2,4 | wc -l)}"
echo "Using $P processes..."

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

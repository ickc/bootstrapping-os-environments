#!/usr/bin/env bash

version=1.3.2

mkdir -p $HOME/.mosh &&
cd $HOME/.mosh &&
wget -qO- https://mosh.org/mosh-$version.tar.gz | tar -xzf - &&
cd mosh-$version &&
if [[ -n $NERSC_HOST ]]; then
	module swap PrgEnv-intel PrgEnv-gnu
	module load protobuf/2.6.1 &&
	protobuf_CFLAGS="-I$C_INCLUDE_PATH" protobuf_LIBS="-L$LD_LIBRARY_PATH" CC=cc CXX=CC ./configure
else
	./configure
fi &&
make &&
make install --prefix="$HOME/.mosh"

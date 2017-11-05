#!/usr/bin/env bash

version=1.3.2

mkdir -p $HOME/.mosh &&
cd $HOME.mosh &&
wget -O - https://mosh.org/mosh-$version.tar.gz | tar -xvzf - &&
cd mosh-$version &&
./configure &&
make &&
make install

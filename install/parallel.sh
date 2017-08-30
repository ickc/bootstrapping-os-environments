#!/usr/bin/env bash

mkdir -p $HOME/.parallel &&
cd $HOME/.parallel &&
wget -O - https://ftp.gnu.org/gnu/parallel/parallel-latest.tar.bz2 | tar -xvjf - &&
cd parallel-* &&
./configure &&
make &&
sudo make install

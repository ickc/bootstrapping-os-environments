#!/usr/bin/env bash

set -e

PREFIX=${PREFIX:-/global/common/software/polar/local}

GH_SHORT=ClementTsang/bottom

url="https://github.com/$GH_SHORT/releases/latest"
downloadUrl="https://github.com$(curl -L $url | grep -o "/$GH_SHORT/releases/download/.*/bottom_x86_64-unknown-linux-gnu\.tar\.gz")"
# downloadUrl="https://github.com$(curl -L $url | grep -o "/$GH_SHORT/archive/.*\.tar.gz")"
filename="${downloadUrl##*/}"

mkdir temp-bottom
cd temp-bottom

wget -qO- "$downloadUrl" | tar -xzf -

mv btm "$PREFIX/bin"

cd ..
rm -rf temp-bottom

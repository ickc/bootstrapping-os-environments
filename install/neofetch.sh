#!/usr/bin/env bash

PREFIX=${PREFIX:-/global/common/software/polar/local}

GH_SHORT=dylanaraps/neofetch

url="https://github.com/$GH_SHORT/releases/latest"
# downloadUrl="https://github.com$(curl -L $url | grep -o "/$GH_SHORT/releases/download/FILENAMEPATTERN")"
downloadUrl="https://github.com$(curl -L $url | grep -o "/$GH_SHORT/archive/.*\.tar.gz")"
filename="${downloadUrl##*/}"

wget "$downloadUrl"

tar -xf "$filename"

cd neofetch-*

export PREFIX
make install

cd ..
rm -rf neofetch-* "$filename"

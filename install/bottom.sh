#!/usr/bin/env bash

GH_SHORT=ClementTsang/bottom

url="https://github.com/$GH_SHORT/releases/latest"
downloadUrl="https://github.com$(curl -L $url | grep -o "/$GH_SHORT/releases/download/bottom_.*_amd64\.deb")"
# downloadUrl="https://github.com$(curl -L $url | grep -o "/$GH_SHORT/archive/.*\.tar.gz")"
filename="${downloadUrl##*/}"

wget "$downloadUrl"

sudo dpkg -i "$filename"

#!/usr/bin/env bash

set -e

case "$(uname -sm)" in
   Linux\ x86_64)  downloadUrl=https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64 ;;
   Linux\ arm*)    downloadUrl=https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-armhf ;;
   Linux\ aarch64) downloadUrl=https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-arm64 ;;
esac

wget "$downloadUrl" -O vscode.deb

sudo apt install ./vscode.deb -y

rm -f vscode.deb

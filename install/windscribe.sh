#!/usr/bin/env bash

set -e

case "$(uname -sm)" in
    Linux\ x86_64) downloadUrl=https://windscribe.com/install/desktop/linux_deb_x64 ;;
    Linux\ i*86) downloadUrl=https://windscribe.com/install/desktop/linux_deb_x86 ;;
    Linux\ arm*) downloadUrl=https://windscribe.com/install/desktop/linux_deb_arm ;;
    Linux\ aarch64) downloadUrl=https://windscribe.com/install/desktop/linux_deb_arm ;;
esac

wget "$downloadUrl" -O windscribe.deb

sudo apt install ./windscribe.deb -y

rm -f windscribe.deb

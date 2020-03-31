#!/usr/bin/env bash

set -e

mkdir -p deb

# windscribe
wget https://windscribe.com/install/desktop/linux_deb_x64 -O deb/windscribe_linux_deb_x64.deb
sudo apt install ./deb/windscribe_linux_deb_x64.deb -y

# zero-tier
curl -s https://install.zerotier.com/ | sudo bash

# pandoc
downloadUrl="https://github.com$(curl -L https://github.com/jgm/pandoc/releases/latest | grep -o '/jgm/pandoc/releases/download/.*-amd64\.deb')"

wget "$downloadUrl" -O deb/pandoc.deb
sudo apt install ./deb/pandoc.deb -y

# vscode
downloadUrl="$(curl -L https://update.code.visualstudio.com/api/update/linux-deb-x64/insider/VERSION | grep -o '[^"]*.deb')"

wget "$downloadUrl" -O deb/vscode.deb
sudo apt install ./deb/vscode.deb -y

tree deb
echo Cleaning up...
rm -rf deb

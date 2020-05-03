#!/usr/bin/env bash

set -e

mkdir -p deb

# windscribe
case "$(uname -sm)" in
   Linux\ x86_64)  downloadUrl=https://windscribe.com/install/desktop/linux_deb_x64 ;;
   Linux\ i*86)    downloadUrl=https://windscribe.com/install/desktop/linux_deb_x86 ;;
   Linux\ arm*)    downloadUrl=https://windscribe.com/install/desktop/linux_deb_arm ;;
   Linux\ aarch64) downloadUrl=https://windscribe.com/install/desktop/linux_deb_arm ;;
esac

wget "$downloadUrl" -O deb/windscribe.deb
sudo apt install ./deb/windscribe.deb -y

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

# miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O deb/Miniconda3-latest-Linux-x86_64.sh
chmod +x deb/Miniconda3-latest-Linux-x86_64.sh
bash deb/Miniconda3-latest-Linux-x86_64.sh -b

tree deb
echo Cleaning up...
rm -rf deb

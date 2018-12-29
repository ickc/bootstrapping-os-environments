#!/usr/bin/env bash

set -e

# assume on Ubuntu

sudo add-apt-repository ppa:morphis/anbox-support -y
sudo apt update
sudo apt install linux-headers-generic anbox-modules-dkms -y

sudo modprobe ashmem_linux
sudo modprobe binder_linux

# debug
ls -1 /dev/{ashmem,binder}

sudo snap install --devmode --beta anbox

# debug
snap info anbox

# Add Google Play and ARM support
mkdir -p ~/git/geeks-r-us && cd ~/git/geeks-r-us
git clone git@github.com:geeks-r-us/anbox-playstore-installer.git
cd anbox-playstore-installer

sudo apt install wget lzip unzip squashfs-tools -y
sed -i 's/^OPENGAPPS_RELEASEDATE.*$/OPENGAPPS_RELEASEDATE="20181229"/' install-playstore.sh
sudo ./install-playstore.sh

anbox.appmgr

echo 'Enable all: Settings > Apps > Google Play Services/Store > Permissions'

#!/bin/sh​

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

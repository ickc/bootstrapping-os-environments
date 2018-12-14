#!/usr/bin/env bash

set -e

# assume on Ubuntu

sudo apt install git curl wget sed -y

git clone https://github.com/ickc/linux-surface.git ~/linux-surface

cd ~/linux-surface

sudo sh setup.sh

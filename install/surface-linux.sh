#!/usr/bin/env bash

set -e

# assume on Ubuntu

sudo apt install git curl wget sed -y

git clone https://github.com/ickc/linux-surface.git "$HOME/linux-surface"

cd "$HOME/linux-surface"

sudo sh setup.sh

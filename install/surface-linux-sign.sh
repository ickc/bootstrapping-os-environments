#!/usr/bin/env bash

set -e

# assume on Ubuntu

# debug
sudo mokutil --list-enrolled

cd "$HOME"

find /boot -maxdepth 1 -name 'vmlinuz-*-surface+' -exec bash -c 'sudo sbsign --key MOK.priv --cert MOK.pem "$0" --output "$0.signed"' {} \;
find /boot -maxdepth 1 -name 'initrd.img-*-surface+' -exec bash -c 'sudo cp "$0" "$0.signed"' {} \;

sudo update-grub

#!/bin/sh​

set -e

# assume on Ubuntu

# debug
sudo mokutil --list-enrolled

cd ~

find /boot -maxdepth 1 -name 'vmlinuz-*-surface+' -exec bash -c 'sudo sbsign --key MOK.priv --cert MOK.pem "$0" --output "$0.signed" && sudo rm -f "$0"' {} \;
find /boot -maxdepth 1 -name 'initrd.img-*-surface+' -exec bash -c 'sudo mv "$0" "$0.signed"' {} \;

sudo update-grub

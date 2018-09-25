#!/usr/bin/env bash

# example
# ./macOS-to-usb.sh /Applications/Install\ macOS\ Mojave.app /Volumes/USB

sudo "$1/Contents/Resources/createinstallmedia" \
    --volume "$2" \
    --nointeraction \
    --downloadassets

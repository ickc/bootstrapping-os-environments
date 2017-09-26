#!/usr/bin/env bash

# example
# ./macOS-to-usb.sh /Applications/Install\ macOS\ High\ Sierra.app /Volumes/Install\ macOS\ High\ Sierra 

sudo "$1/Contents/Resources/createinstallmedia" --volume "$2" --applicationpath "$1"

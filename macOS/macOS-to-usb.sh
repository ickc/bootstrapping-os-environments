#!/usr/bin/env bash

# examples
# ./macOS-to-usb.sh /Applications/Install\ macOS\ Mojave.app USB
# ./macOS-to-usb.sh '/Applications/Install macOS Big Sur.app' USB

# get disk#
diskutil list
while true; do
    read -p "What's the disk number?" dkno
    if [[ "$dkno" =~ ^[0-9]+$ ]]; then
        break
    else
        echo "Disk number should be integers only."
    fi
done

diskutil partitionDisk "/dev/disk$dkno" GPT JHFS+ "$2" 100%

sudo "$1/Contents/Resources/createinstallmedia" \
    --volume "/Volumes/$2" \
    --nointeraction \
    --downloadassets

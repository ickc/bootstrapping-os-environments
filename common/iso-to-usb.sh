#!/usr/bin/env bash

# This script burns the iso to the usb disk, supports macOS and Linux.
# usage: ./iso-to-usb.sh /path/to.iso

set -e
UNAME="$(uname)"

# show the disks
# for Linux
if [[ $UNAME == Darwin ]]; then
    diskutil list
else
    lsblk
fi

# read the disk name from user
while true; do
    read -rp "What's the disk name? " diskname
    if [[ -b "/dev/$diskname" ]]; then
        break
    else
        echo "Disk name is not valid."
    fi
done

# confirm to burn the iso to the disk, else exit
while true; do
    read -rp "Do you wish to burn the iso to $diskname? (Y/n) " yn
    case $yn in
    [Yy]*) break ;;
    [Nn]*) exit ;;
    *) echo "Please answer yes or no." ;;
    esac
done

echo unmounting the disk "/dev/$diskname"
if [[ $UNAME == Darwin ]]; then
    diskutil unmountDisk "/dev/$diskname"
else
    sudo umount "/dev/$diskname" || true
fi

if [[ $UNAME == Darwin ]]; then
    if [[ $(command -v dd) == /bin/dd ]]; then
        # use macOS dd
        sudo dd if="$1" of="/dev/r$diskname" bs=4m
    else
        # use gnu dd
        sudo dd if="$1" of="/dev/$diskname" bs=4M conv=fsync status=progress
    fi
else
    sudo dd if="$1" of="/dev/$diskname" bs=4M conv=fsync oflag=direct status=progress
fi
sync

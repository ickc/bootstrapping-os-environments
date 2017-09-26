#!/usr/bin/env bash

# get paths and extension
PATHNAME="$@"
PATHNAMEWOEXT=${PATHNAME%.*}
EXT=${PATHNAME##*.}
# ext="${EXT,,}" #This does not work on Mac's default, old version of, bash.

# Convert iso to dmg
if [[ $EXT != "dmg" ]]
then
	hdiutil convert "$PATHNAME" -format UDRW -o "$PATHNAMEWOEXT.dmg"
fi

# get disk#
diskutil list

read -p "What's the disk number?" dkno
if ! [[ "$dkno" =~ ^[0-9]+$ ]]
then
    echo "Disk number should be integers only."
	exit 1
fi

# clone
while true; do
    read -p "Do you wish to burn the iso to disk$dkno? (Y/n)" yn
    case $yn in
        [Yy]* ) diskutil unmountDisk /dev/disk$dkno && sudo dd if="$PATHNAMEWOEXT.dmg" of=/dev/rdisk$dkno bs=1M; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
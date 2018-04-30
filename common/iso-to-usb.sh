#!/usr/bin/env bash

# get paths and extension
PATHNAME="$@"
PATHNAMEWOEXT=${PATHNAME%.*}
EXT=${PATHNAME##*.}

# Convert iso to dmg
if [[ $EXT != "dmg" && $(uname) == Darwin ]]; then
	filename="$PATHNAMEWOEXT.dmg"
	hdiutil convert "$PATHNAME" -format UDRW -o "$filename"
else
	filename="$PATHNAME"
fi

# get disk#
if [[ $(uname) == Darwin ]]; then
	diskutil list
	while true; do
		read -p "What's the disk number?" dkno
		if [[ "$dkno" =~ ^[0-9]+$ ]]; then
			break
		else
			echo "Disk number should be integers only."
		fi
	done
	diskname=disk$dkno
else
	lsblk
	while true; do
		read -p "What's the disk label?" dklb
		if [[ "$dklb" =~ ^[a-z]$ ]]; then
			break
		else
			echo "Disk number should be alphabets only."
		fi
	done
	diskname=sd$dklb
fi

# clone
while true; do
	read -p "Do you wish to burn the iso to $diskname? (Y/n)" yn
	if [[ $(uname) == Darwin ]]; then
		case $yn in
			[Yy]* ) diskutil unmountDisk /dev/$diskname && sudo dd if="$filename" of=/dev/r$diskname status=progress bs=1M && sync; break;;
			[Nn]* ) exit;;
			* ) echo "Please answer yes or no.";;
		esac
	else
		case $yn in
			[Yy]* ) sudo dd if="$filename" of=/dev/$diskname status=progress bs=1M && sync; break;;
			[Nn]* ) exit;;
			* ) echo "Please answer yes or no.";;
		esac
	fi
done

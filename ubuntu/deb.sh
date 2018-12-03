#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

# Gitkraken
wget https://release.gitkraken.com/linux/gitkraken-amd64.deb &&
	sudo apt install ./gitkraken-amd64.deb
# dropbox
wget 'https://www.dropbox.com/download?dl=packages/ubuntu/dropbox_2018.11.28_amd64.deb' -O dropbox_amd64.deb &&
	sudo apt install ./dropbox_amd64.deb
# windscribe
wget https://windscribe.com/install/desktop/linux_deb_x64 -O windscribe_linux_deb_x64.deb &&
	sudo apt install ./windscribe_linux_deb_x64.deb

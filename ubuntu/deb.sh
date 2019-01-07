#!/usr/bin/env bash

# dropbox
wget 'https://www.dropbox.com/download?dl=packages/ubuntu/dropbox_2018.11.28_amd64.deb' -O dropbox_amd64.deb &&
	sudo apt install ./dropbox_amd64.deb -y
# windscribe
wget https://windscribe.com/install/desktop/linux_deb_x64 -O windscribe_linux_deb_x64.deb &&
	sudo apt install ./windscribe_linux_deb_x64.deb -y

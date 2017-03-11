#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Gitkraken
wget https://release.gitkraken.com/linux/gitkraken-amd64.deb && \
	sudo dpkg -i gitkraken-amd64.deb
# dropbox
wget https://linux.dropbox.com/packages/ubuntu/dropbox_2015.10.28_amd64.deb && \
	sudo dpkg -i dropbox_2015.10.28_amd64.deb

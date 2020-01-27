#!/usr/bin/env bash

# windscribe
wget https://windscribe.com/install/desktop/linux_deb_x64 -O windscribe_linux_deb_x64.deb &&
	sudo apt install ./windscribe_linux_deb_x64.deb -y

# zero-tier
curl -s https://install.zerotier.com/ | sudo bash

# pandoc
wget https://github.com/jgm/pandoc/releases/download/2.9.1.1/pandoc-2.9.1.1-1-amd64.deb -O pandoc.deb &&
	sudo apt install ./pandoc.deb -y

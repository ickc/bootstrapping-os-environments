#!/usr/bin/env zsh

set -e

MACPORTS_VERSION=2.10.5
MACPORTS_OS_VERSION=15-Sequoia

# helpers ##############################################################

startsudo() {
    sudo -v
    (while true; do
        sudo -v
        sleep 50
    done) &
    SUDO_PID="$!"
    trap stopsudo SIGINT SIGTERM
}
stopsudo() {
    kill "${SUDO_PID}"
    trap - SIGINT SIGTERM
    sudo -k
}

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

startsudo

print_double_line
echo "install macports..."
# port: update from https://www.macports.org/install.php
# prebuild binaries
curl -L "https://github.com/macports/macports-base/releases/download/v${MACPORTS_VERSION}/MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" --output "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
sudo installer -pkg "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" -target /
rm -f "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
# build from source
# curl https://distfiles.macports.org/MacPorts/MacPorts-${MACPORTS_VERSION}.tar.bz2 --output MacPorts-${MACPORTS_VERSION}.tar.bz2
# tar xjvf MacPorts-${MACPORTS_VERSION}.tar.bz2
# cd MacPorts-${MACPORTS_VERSION}
# build from master
# git clone https://github.com/macports/macports-base.git
# cd macports-base
# ./configure && make && sudo make install
# cd ..
# rm -rf MacPorts-${MACPORTS_VERSION}*
# rm -rf macports-base
sudo /opt/local/bin/port -v selfupdate

stopsudo

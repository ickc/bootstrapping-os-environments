#!/usr/bin/env bash

# helpers ##############################################################

startsudo() {
    sudo -v
    ( while true; do sudo -v; sleep 50; done; ) &
    SUDO_PID="$!"
    trap stopsudo SIGINT SIGTERM
}
stopsudo() {
    kill "$SUDO_PID"
    trap - SIGINT SIGTERM
    sudo -k
}

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

startsudo

# setup compilers first
sudo port -N install gcc13 mpich-default
# port select --list gcc
sudo port -N select --set gcc mp-gcc13
# port select --list mpi
sudo port -N select --set mpi mpich-mp-fortran

# https://serverfault.com/a/915814
grep -v '#' port.txt | awk NF | xargs -n1 sudo port -N install

# configure git after macports's git is installed
git config --global pull.rebase false

sudo port -N load smartmontools
# sudo port -N load openssh
sudo port -N load rsync

stopsudo

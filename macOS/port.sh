#!/usr/bin/env bash

# sudo loop
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# setup compilers first
sudo port -N install gcc12 mpich-default
# port select --list gcc
sudo port -N select --set gcc mp-gcc12
# port select --list mpi
sudo port -N select --set mpi mpich-mp-fortran

# https://serverfault.com/a/915814
grep -v '#' port.txt | awk NF | xargs -n1 sudo port -N install

# configure git after macports's git is installed
git config --global pull.rebase false

sudo port -N load smartmontools
# sudo port -N load openssh
sudo port -N load rsync

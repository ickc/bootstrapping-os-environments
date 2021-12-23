#!/usr/bin/env bash

# sudo loop
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# setup compilers first
sudo port install gcc10 mpich mpich-gcc10
sudo port select --set gcc mp-gcc10
sudo port select --set mpi mpich-gcc10

grep -v '#' port.txt | xargs sudo port install

# configure git after macports's git is installed
git config --global pull.rebase false

sudo port load smartmontools
sudo port load openssh
sudo port load rsync

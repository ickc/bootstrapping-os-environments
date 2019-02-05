#!/usr/bin/env bash

# prepare sudo for pkg
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

brew tap homebrew/cask-versions
brew tap homebrew/cask-drivers

# run once a time because it is not uncommon for some casks to be failed to install
# for example just because it occassionally cannot download something
# make sure to check the output log to see if needed by run again
grep -v '#' brew-cask.txt | xargs -n1 brew cask install

# overriding Mac App Store's version
brew cask install --force atext

cat << EOF >> $HOME/.bash_profile

# CUDA
export PATH=":\$PATH:$(echo /Developer/NVIDIA/CUDA-*.*/bin)"
EOF

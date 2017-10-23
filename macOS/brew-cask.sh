#!/usr/bin/env bash

# prepare sudo for pkg
sudo -v &&

# this can be done after gnuize.sh, but I put it here because it requires sudo
sudo sh -c 'echo "/usr/local/bin/bash" >> /etc/shells' && chsh -s /usr/local/bin/bash

brew tap caskroom/versions &&
brew tap caskroom/drivers &&

grep -v '#' brew-cask.txt | xargs brew cask install &&

# overriding Mac App Store's version
brew cask install --force atext &&

cat << EOF >> $HOME/.bash_profile

# CUDA
export PATH=":\$PATH:$(echo /Developer/NVIDIA/CUDA-*.*/bin)"

# Textmate
export EDITOR="/usr/local/bin/mate -w"
EOF

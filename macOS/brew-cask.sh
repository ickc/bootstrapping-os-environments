#!/usr/bin/env bash

# prepare sudo for pkg
sudo -v &&

brew tap caskroom/versions &&
brew tap caskroom/drivers &&

grep -v '#' brew-cask.txt | xargs brew cask install &&

# overriding Mac App Store's version
brew cask install --force atext &&

# CUDA PATH
printf "%s\n" "" "# CUDA" 'export PATH="'$(echo /Developer/NVIDIA/CUDA-*.*/bin)':$PATH"' >> $HOME/.bash_profile

## Set Textmate as default text editor in Terminal
printf "%s\n" "" '# Textmate' 'export EDITOR="/usr/local/bin/mate -w"' >> $HOME/.bash_profile

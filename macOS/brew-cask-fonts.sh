#!/usr/bin/env bash

# the later for Microsoft Fonts
brew tap homebrew/cask-fonts  &&
brew tap niksy/pljoska &&

grep -v '#' brew-cask-fonts.txt | xargs -n1 brew cask install

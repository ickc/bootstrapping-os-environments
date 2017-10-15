#!/usr/bin/env bash

# the later for Microsoft Fonts
brew tap caskroom/fonts &&
brew tap niksy/pljoska &&

grep -v '#' brew-cask-fonts.txt | xargs brew cask install

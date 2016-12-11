#!/bin/bash

brew tap caskroom/fonts
# Microsoft Fonts
brew tap niksy/pljoska

# grep -v invert the search. i.e. all lines including # are considered as "comments"
grep -v '#' brew-cask-fonts.txt | xargs brew cask install

#!/bin/bash

# prepare sudo for pkg
sudo -v

brew tap caskroom/versions

# grep -v invert the search. i.e. all lines including # are considered as "comments"
grep -v '#' brew-cask.txt | xargs brew cask install

# overriding Mac App Store's version
brew cask install --force atext multimarkdown-composer-beta

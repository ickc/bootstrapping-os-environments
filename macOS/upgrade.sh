#!/usr/bin/env bash

# upgrade npm & npm packages
npm install npm -g && npm update -g

# upgrade brew packages (not including brew-cask)
brew update && brew upgrade && brew cleanup && brew doctor

# upgrade Mac App Store apps
mas upgrade

# upgrade gems
update_rubygems && gem update --system

# update cabal
# cabal update

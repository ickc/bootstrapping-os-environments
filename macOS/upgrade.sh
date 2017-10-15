#!/usr/bin/env bash

# upgrade npm
npm install npm -g
# upgrade npm packages
npm update -g

# upgrade pip
pip install -U pip setuptools # setuptools should be installed by default
pip3 install -U pip setuptools # setuptools wheel should be installed by default
# upgrade pip packages
pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
pip3 freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

# upgrade brew packages (not including brew-cask)
brew update
brew upgrade
brew cleanup
brew doctor

# cleanup downloaded files (cask do not support upgrade yet)
brew cask cleanup

# upgrade Mac App Store apps
mas upgrade

# upgrade gems
update_rubygems
gem update --system

# update cabal
cabal update

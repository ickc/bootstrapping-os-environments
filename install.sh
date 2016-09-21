#!/bin/bash

# install xcode
xcode-select --install
sudo xcodebuild -license

# install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# install node & npm
brew install node

# install mas cli
brew install mas
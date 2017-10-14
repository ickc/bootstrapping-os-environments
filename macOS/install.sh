#!/usr/bin/env bash

# install xcode
xcode-select --install &&
sudo xcodebuild -license accept &&

# install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" &&

# GNU-ize
../submodule/gnuize.sh &&

# install node, npm, mas cli
brew install node mas

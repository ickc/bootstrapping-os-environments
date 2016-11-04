#!/bin/bash

# install xcode
xcode-select --install
sudo xcodebuild -license accept

# install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# [GNU-ize Mac OS X El Capitan](https://gist.github.com/ickc/3a9600fabb9fc9cef7d1ae981afc6810)
./gnuize.sh

# install node & npm
brew install node

# install mas cli
brew install mas

# install cabal for haskell
brew install ghc cabal-install && printf "%s\n" "" "# cabal PATH" "export PATH=\"$HOME/.cabal/bin:\$PATH\"" >> $HOME/.bash_profile

# install anaconda
brew cask install anaconda && printf "%s\n" "" "# anaconda PATH" "export PATH=\"$HOME/anaconda3/bin:\$PATH\"" >> $HOME/.bash_profile

# alternative way of getting gem
# brew install brew-gem

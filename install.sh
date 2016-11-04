#!/bin/bash

# install xcode
xcode-select --install
sudo xcodebuild -license accept

# install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# [GNU-ize Mac OS X El Capitan](https://gist.github.com/clayfreeman/2a5e54577bcc033e2f00): it will override your bash profile!
./gnuize.sh && brew linkapps python

# install node & npm
brew install node

# install mas cli
brew install mas

# install cabal for haskell
brew install ghc cabal-install && printf "%s\n" "" "# cabal PATH" "export PATH=\"/Users/kolen/.cabal/bin:\$PATH\"" >> $HOME/.bash_profile

# alternative way of getting gem
# brew install brew-gem

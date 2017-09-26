#!/usr/bin/env bash

# install xcode
xcode-select --install
sudo xcodebuild -license accept

# install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# GNU-ize: it will override your bash profile!
../submodule/gnuize.sh

# install node & npm
brew install node

# install mas cli
brew install mas

# install cabal for haskell
brew install ghc cabal-install && printf "%s\n" "" "# cabal" 'export PATH="/Users/kolen/.cabal/bin:$PATH"' >> $HOME/.bash_profile

# alternative way of getting gem
# brew install brew-gem

#!/usr/bin/env bash

# install xcode
# the first time it runs, the process ends here
# the second time it runs, this command fails and proceed to next
xcode-select --install ||

# install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" &&

# GNU-ize
../submodule/gnuize.sh

# install node, npm, mas cli
brew install node mas ruby

# first 2 needed by closure-compiler, sshfs respectively
brew cask install java osxfuse anaconda

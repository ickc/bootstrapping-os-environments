#!/usr/bin/env bash

# prepare sudo for pkg
sudo -v
while true; do
    sudo -n true
    sleep 50
    kill -0 "$$" || exit
done 2> /dev/null &

brew tap homebrew/cask-versions
brew tap homebrew/cask-drivers
brew tap homebrew/cask-fonts

# run once a time because it is not uncommon for some casks to be failed to install
# for example just because it occassionally cannot download something
# make sure to check the output log to see if needed by run again
cat brew-cask.txt brew-cask-fonts.txt | grep -v '#' | xargs -n1 brew install --cask

# mas uninstall 488566438
# brew cask install atext

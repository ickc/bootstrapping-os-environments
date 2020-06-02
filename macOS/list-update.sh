#!/usr/bin/env bash

printline() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

printline

echo Consider add the following to mas.txt:
mas list | xargs -i -n1 bash -c 'cat install.sh mas.txt | if ! grep -q ${0%% *} -; then echo $0; fi' {}

printline

echo Consider add the following to port.txt:
port installed requested | grep -oP '^  ([^@]*)' | xargs -i -n1 bash -c 'cat port.txt | if ! grep -q ${0%% *} -; then echo $0; fi' {}

printline

echo Consider add the following to brew.txt:
brew leaves | xargs -i -n1 bash -c 'cat gnuize.sh install.sh brew.sh brew.txt | if ! grep -q $0 -; then echo $0; fi' {}

printline

echo Consider add the following to brew-cask.txt:
brew cask list | xargs -i -n1 bash -c 'cat install.sh brew-cask.sh brew-cask.txt brew-cask-fonts.txt | if ! grep -q $0 -; then echo $0; fi' {}

printline

echo Consider add the following to npm.txt:
ls $(npm root -g) | xargs -i -n1 bash -c 'cat ../common/npm.txt | if ! grep -q $0 -; then echo $0; fi' {}

printline

echo Consider add the following to code.txt:
code --list-extensions 2>/dev/null | xargs -i -n1 bash -c 'cat ../common/code.txt | if ! grep -q $0 -; then echo $0; fi' {}

#!/usr/bin/env bash

printf '=%.0s' {1..72} && echo

echo Consider add the following to mas.txt:
mas list | xargs -i -n1 bash -c 'if ! grep -q ${0%% *} mas.txt; then echo $0; fi' {}

printf '=%.0s' {1..72} && echo

echo Consider add the following to brew.txt:
brew leaves | xargs -i -n1 bash -c 'cat gnuize.sh install.sh brew.sh brew.txt | if ! grep -q $0 -; then echo $0; fi' {}

printf '=%.0s' {1..72} && echo

echo Consider add the following to brew-cask.txt:
brew cask list | xargs -i -n1 bash -c 'cat install.sh brew-cask.sh brew-cask.txt brew-cask-fonts.txt | if ! grep -q $0 -; then echo $0; fi' {}

printf '=%.0s' {1..72} && echo

echo Consider add the following to npm.txt:
ls $(npm root -g) | xargs -i -n1 bash -c 'cat ../common/npm.txt | if ! grep -q $0 -; then echo $0; fi' {}

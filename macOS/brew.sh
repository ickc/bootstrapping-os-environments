#!/usr/bin/env bash

# only when build from source, it will uses homebrew's compiler (chosen as gcc from gnuize)
brew install mpich --build-from-source &&

grep -v '#' brew.txt | xargs brew install &&

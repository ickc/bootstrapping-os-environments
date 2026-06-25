#!/usr/bin/env bash

cabal update

grep -v '#' cabal.txt | xargs -i cabal install --force-reinstalls {}

#!/usr/bin/env bash

grep -v '#' npm.txt | xargs npm install -g

printf "%s\n" "" '# MathJax-node' 'export PATH=$(dirname $(readlink -f $(which npm)))/../../mathjax-node/bin:$PATH' >> $HOME/.bash_profile

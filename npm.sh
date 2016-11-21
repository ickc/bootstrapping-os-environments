#!/bin/bash

npm install -g imageoptim-cli
npm install -g mathjax-node && printf "%s\n" "" '# MathJax-node' 'export PATH=/usr/local/lib/node_modules/mathjax-node/bin:$PATH' >> $HOME/.bash_profile
 
npm install -g uglify-js
npm install -g cssnano-cli
npm install -g csso
npm install -g html-minifier

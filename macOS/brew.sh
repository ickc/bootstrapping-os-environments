#!/bin/bash

grep -v '#' brew.txt | xargs brew install

brew linkapps python3
printf "%s\n" "" '# homebrew's Ruby'' 'export PATH=$(brew --prefix ruby)/bin:$PATH' >> $HOME/.bash_profile #[Small but very useful tip on using jekyll on macosx when you use hoembrew · Issue #1504 · jekyll/jekyll](https://github.com/jekyll/jekyll/issues/1504)

#!/usr/bin/env bash

# only when build from source, it will uses homebrew's compiler (chosen as gcc from gnuize)
brew install mpich --build-from-source

grep -v '#' brew.txt | xargs brew install

printf "%s\n" "" '# Ruby from homebrew'' 'export PATH=$(brew --prefix ruby)/bin:$PATH' >> $HOME/.bash_profile #[Small but very useful tip on using jekyll on macosx when you use hoembrew · Issue #1504 · jekyll/jekyll](https://github.com/jekyll/jekyll/issues/1504)

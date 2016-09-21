#!/bin/bash

# brew
brew install python3
brew install ruby
echo 'export PATH=$(brew --prefix ruby)/bin:$PATH' >> ~/.bash_profile #[Small but very useful tip on using jekyll on macosx when you use hoembrew · Issue #1504 · jekyll/jekyll](https://github.com/jekyll/jekyll/issues/1504)
# brew install rbenv && rbenv init
brew install multimarkdown
brew install pandoc
brew install pandoc-citeproc
brew install openconnect # Open client for Cisco AnyConnect VPN
brew install enca
brew install smartmontools
brew install gdrive
brew install imagemagick
brew install mas
brew install mp4v2
brew install pdf2svg
brew install potrace
brew install tree

# homebrew/dupes
brew tap homebrew/dupes

# install GNU-ize
2a5e54577bcc033e2f00/gnuize.sh

# alternative way of getting gem
# brew install brew-gem
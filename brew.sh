#!/bin/bash

# brew
brew install python3 && brew linkapps python3
brew install ruby && echo 'export PATH=$(brew --prefix ruby)/bin:$PATH' >> $HOME/.bash_profile #[Small but very useful tip on using jekyll on macosx when you use hoembrew · Issue #1504 · jekyll/jekyll](https://github.com/jekyll/jekyll/issues/1504)
# brew install rbenv && rbenv init
brew install parallel
brew install multimarkdown
brew install openconnect # Open client for Cisco AnyConnect VPN
brew install enca
brew install smartmontools
brew install gdrive
brew install imagemagick
brew install mp4v2
brew install pdf2svg
brew install potrace
brew install tree
brew install exiftool
brew install wget
brew install doxygen # brew doctor will complain it is missing. I wonder why it wasn't installed if it is needed, and if it is really needed

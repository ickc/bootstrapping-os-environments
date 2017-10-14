#!/usr/bin/env bash

mkdir -p "$@" && cd "$@"

# Mac App Stores Only
mas list > mas.txt

# Applications (including Mac App Stores')
ls /Applications > applicatio-ls.txt
tree -L 2 /Applications > applications-tree.txt

# Safari extensions
find $HOME/Library/Safari/Extensions/ -iname '*.safariextz' -print | sed -e s=/.*/==g -e s=.safariextz==g > safari.txt

# local bin
ls /usr/local/bin/ > local-bin-ls.txt
tree /usr/local/bin/ > local-bin-tree.txt


# local bin in home
ls $HOME/.local/bin > home-local-bin-ls.txt
tree $HOME/.local/bin > home-local-bin-tree.txt

# brew
brew leaves > brew.txt

# gem
gem list --no-version > gem.txt

#npm
npm list --depth=0 > npm-project-tree.txt
npm list -g --depth=0 > npm-global-tree.txt
ls `npm root -g` > npm-global-ls.txt

# pip
pip list | sed 's/ (.*)//' > pip.txt

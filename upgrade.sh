#!/bin/bash

npm install npm -g

pip install -U pip setuptools

brew update && brew upgrade && brew cleanup && brew doctor

mas upgrade

gem install rubygems-update
update_rubygems
gem update --system

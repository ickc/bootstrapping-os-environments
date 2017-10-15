#!/usr/bin/env bash

# prepare sudo for pkg
sudo -v &&

brew tap caskroom/versions &&
brew tap caskroom/drivers &&

grep -v '#' brew-cask.txt | xargs brew cask install

# overriding Mac App Store's version
brew cask install --force atext

# CUDA PATH
printf "%s\n" "" "# CUDA" 'export PATH="'$(echo /Developer/NVIDIA/CUDA-*.*/bin)':$PATH"' >> $HOME/.bash_profile
# conda PATH
# this is a better approach since you can always deactivate it and uses defaults bin for example
printf "%s\n" "" "# conda" '. /usr/local/anaconda3/bin/activate root' >> $HOME/.bash_profile

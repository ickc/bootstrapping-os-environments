#!/bin/bash

# post brew-cask.sh
## open Adobe CC installer downloaded by brew cask
open -a '/usr/local/Caskroom/adobe-creative-cloud/latest/Creative Cloud Installer.app'
## Set Textmate as default text editor in Terminal
echo 'export EDITOR="/usr/local/bin/mate -w"' >> ~/.bash_profile

# create temp folder for downloads
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir -p temp
cd temp

# Solarized Terminal
git clone git://github.com/tomislav/osx-terminal.app-colors-solarized.git
open 'osx-terminal.app-colors-solarized/Solarized Light.terminal'
open 'osx-terminal.app-colors-solarized/Solarized Dark.terminal'

# Solarized Textmate
git clone git://github.com/deplorableword/textmate-solarized.git
mv 'textmate-solarized/Solarized (dark).tmTheme' ~/Library/Application\ Support/TextMate/Managed/Bundles/Themes.tmbundle/Themes/
mv 'textmate-solarized/Solarized (light).tmTheme' ~/Library/Application\ Support/TextMate/Managed/Bundles/Themes.tmbundle/Themes/

# download [GNU-ize Mac OS X El Capitan](https://gist.github.com/clayfreeman/2a5e54577bcc033e2f00)
git clone git@github.com:2a5e54577bcc033e2f00.git
2a5e54577bcc033e2f00/gnuize.sh && brew linkapps python

cd ..
rm -rf temp

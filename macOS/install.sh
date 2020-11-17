#!/usr/bin/env zsh

set -e

MACPORTS_VERSION=2.6.4
MACPORTS_OS_VERSION=11.0-BigSur

# sudo loop
sudo xcodebuild -license accept
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
echo "install homebrew..."
# install brew
mkdir ~/.homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C ~/.homebrew

print_double_line
echo "install macports..."
# port: update from https://www.macports.org/install.php
# prebuild binaries
curl "https://distfiles.macports.org/MacPorts/MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" --output "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
sudo installer -pkg "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" -target /
rm -f "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
# build from source
# curl https://distfiles.macports.org/MacPorts/MacPorts-${MACPORTS_VERSION}.tar.bz2 --output MacPorts-${MACPORTS_VERSION}.tar.bz2
# tar xjvf MacPorts-${MACPORTS_VERSION}.tar.bz2
# cd MacPorts-${MACPORTS_VERSION}
# build from master
# git clone https://github.com/macports/macports-base.git
# cd macports-base
# ./configure && make && sudo make install
# cd ..
# rm -rf MacPorts-${MACPORTS_VERSION}*
# rm -rf macports-base
sudo /opt/local/bin/port -v selfupdate

export PATH="$HOME/.homebrew/bin:$HOME/.homebrew/opt/ruby/bin:$PATH"
print_double_line
echo "install mas..."
# mas
brew install mas

print_double_line
echo "install node and ruby..."
# install node, npm
brew install node ruby

print_line
echo 'update gem...'
gem install rubygems-update

print_double_line
echo 'install anaconda and oracle-jdk...'
brew cask install anaconda oracle-jdk

#!/usr/bin/env zsh

# TODO: use heredoc to define bash functions ml_brew, ml_port

# sudo loop
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# install xcode command line tools
xcode-select --install

# install brew
mkdir ~/.homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C ~/.homebrew &&
export PATH="$HOME/.homebrew/bin:$PATH"

# port: update from https://www.macports.org/install.php
MACPORTS_VERSION=2.6.3
MACPORTS_OS_VERSION=10.15-Catalina
curl "https://distfiles.macports.org/MacPorts/MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" --output "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
sudo installer -pkg "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" -target /
rm -f "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"

# mas
brew install mas
# macport needs xcode
mas install 497799835
sudo xcodebuild -license accept

# install node, npm
brew install node ruby
export PATH="~/.homebrew/opt/ruby/bin:$PATH"

gem install rubygems-update

brew cask install anaconda oracle-jdk

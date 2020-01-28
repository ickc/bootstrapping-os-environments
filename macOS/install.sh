#!/usr/bin/env zsh

# TODO: use heredoc to define bash functions ml_brew, ml_port

# sudo loop
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# install xcode
xcode-select --install

sudo xcodebuild -license accept

# Prezto
git clone --recursive https://github.com/sorin-ionescu/prezto.git "${ZDOTDIR:-$HOME}/.zprezto"
setopt EXTENDED_GLOB
for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
  ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
done

# sman
mkdir -p ~/.local/bin
bash -c "$(curl https://raw.githubusercontent.com/ickc/sman/master/install.sh)"

# install brew
mkdir ~/.homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C ~/.homebrew &&

export PATH="$HOME/.homebrew/bin:$PATH"
printf "%s\n" "" '# homebrew' 'export PATH="$HOME/.homebrew/bin:$PATH"' >> $HOME/.bash_profile

# port
MACPORTS_VERSION=2.6.2
MACPORTS_OS_VERSION=10.15-Catalina
curl "https://distfiles.macports.org/MacPorts/MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" --output "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
sudo installer -pkg "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" -target /
rm -f "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
printf "%s\n" "" '# port' 'export PATH="/opt/local/bin:$PATH"' >> $HOME/.bash_profile

# mas
brew install mas
# install Xcode before gnuize, because aescrypt-packetizer requires Xcode
mas install 497799835

# may be needed again after Xcode is installed?
sudo xcodebuild -license accept

# GNU-ize
# TODO ../submodule/gnuize.sh
../../GNU-ize/gnuize.sh -p ~/.homebrew

# install node, npm
brew install node ruby

export PATH="~/.homebrew/opt/ruby/bin:$PATH"
printf "%s\n" "" '# Ruby from homebrew' 'export PATH="~/.homebrew/opt/ruby/bin:$PATH"' >> $HOME/.bash_profile #[Small but very useful tip on using jekyll on macosx when you use hoembrew · Issue #1504 · jekyll/jekyll](https://github.com/jekyll/jekyll/issues/1504)

gem install rubygems-update

# first 2 needed by closure-compiler, sshfs respectively
brew cask install java osxfuse anaconda

# conda
~/.homebrew/anaconda3/bin/conda init zsh

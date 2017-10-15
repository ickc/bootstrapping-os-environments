#!/usr/bin/env bash

# install xcode
# the first time it runs, the process ends here
# the second time it runs, this command fails and proceed to next
xcode-select --install ||

# install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" &&

# GNU-ize
../submodule/gnuize.sh

# install node, npm, mas cli
brew install node mas ruby

printf "%s\n" "" '# Ruby from homebrew' 'export PATH=$(brew --prefix ruby)/bin:$PATH' >> $HOME/.bash_profile #[Small but very useful tip on using jekyll on macosx when you use hoembrew · Issue #1504 · jekyll/jekyll](https://github.com/jekyll/jekyll/issues/1504)

gem install rubygems-update

# first 2 needed by closure-compiler, sshfs respectively
brew cask install java osxfuse anaconda

# conda PATH
# this is a better approach since you can always deactivate it and uses defaults bin for example
printf "%s\n" "" "# conda" '. /usr/local/anaconda3/bin/activate root' >> $HOME/.bash_profile

#!/bin/bash

# prepare sudo for pkg
sudo -v

# runtime
brew cask install xquartz
brew cask install java
brew cask install flash
# brew cask install silverlight
# brew cask install playonmac

# license required
brew cask install microsoft-office
brew cask install adobe-creative-cloud
brew cask install vmware-fusion
brew cask install atext
brew cask install textmate
brew cask install papers

# services
brew cask install dropbox
brew cask install google-drive
brew cask install github-desktop
brew cask install duet
# brew cask install sophos-anti-virus-home-edition # no public link available by the developer, so this is removed
# brew cask install skype
# brew cask install steam

# text
brew cask install mactex
brew cask install atom
# brew cask install manuscripts
# brew cask install marked
# brew cask install macdown

# browser
brew cask install google-chrome
brew cask install firefox

# media
brew cask install keka
brew cask install inkscape
brew cask install adobe-dng-converter
brew cask install imageoptim
brew cask install imagealpha
brew cask install handbrake
brew cask install vlc
brew cask install makemkv
brew cask install kodi
# brew cask install mplayerx

# small utilities
brew cask install desktoputility
brew cask install disk-inventory-x
brew cask install dupeguru
brew cask install filezilla
brew cask install sdformatter
brew cask install appcleaner
brew cask install namechanger
brew cask install itsycal
brew cask install calibre
# brew cask install google-earth
# brew cask install stellarium
# brew cask install nimble
# brew cask install blue-jeans-launcher
# brew cask install superduper

# hardware related
brew cask install openzfs
brew cask install cuda
brew cask install cuda-z
brew cask install intel-power-gadget
brew cask install gfxcardstatus
brew cask install logitech-options
brew cask install logitech-gaming-software
brew cask install wacom-intuos-tablet # check if it is this or `brew cask install wacom-intuos-pro-tablet`
brew cask install switchresx
# brew cask install paragon-ntfs # Seagate version??
# brew cask install karabiner # equals to Keyremap4Macbook

# QuickLook
brew cask install ttscoff-mmd-quicklook
brew cask install invisorql # display video metadata instead of playing it
brew cask install epubquicklook

# Others
brew cask install markdown-service-tools # mac Services for markdown editing
brew cask install spectacle # windows manager

# homebrew-cask-versions
brew tap caskroom/versions
brew cask install safari-technology-preview
brew cask install google-chrome-canary

# run installer
open -a '/usr/local/Caskroom/adobe-creative-cloud/latest/Creative Cloud Installer.app'
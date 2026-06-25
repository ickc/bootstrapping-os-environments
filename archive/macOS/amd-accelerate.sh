#!/usr/bin/env bash

# force AMD accelerate
# https://github.com/acidanthera/WhateverGreen/blob/master/Manual/FAQ.Chart.md

defaults write com.apple.AppleGVA gvaForceAMDKE -boolean yes
defaults write com.apple.AppleGVA gvaForceAMDAVCDecode -boolean yes
defaults write com.apple.AppleGVA gvaForceAMDAVCEncode -boolean yes
defaults write com.apple.AppleGVA gvaForceAMDHEVCDecode -boolean yes
defaults write com.apple.AppleGVA disableGVAEncryption -string YES
defaults write com.apple.coremedia hardwareVideoDecoder -string force

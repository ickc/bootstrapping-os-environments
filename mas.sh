#!/bin/bash

mas signin

grep -v '#' mas.txt | xargs mas install

# open applications to transfer license to non-mas version
open -a /Applications/aText.app
open -a /Applications/MultiMarkdown\ Composer.app

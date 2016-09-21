#!/bin/bash

brew update && brew upgrade && brew cleanup && brew doctor

pip install -U pip setuptools
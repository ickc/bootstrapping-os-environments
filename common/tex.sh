#!/usr/bin/env bash

sudo tlmgr update --self
grep -v '#' tex.txt | xargs sudo tlmgr install

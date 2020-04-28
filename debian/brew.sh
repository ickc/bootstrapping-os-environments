#!/usr/bin/env bash

grep -v '#' brew.txt | xargs -n1 brew install

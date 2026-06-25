#!/usr/bin/env bash

grep -v '#' npm.txt | xargs npm install -g

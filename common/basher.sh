#!/usr/bin/env bash

grep -v '#' basher.txt | xargs -n1 basher install

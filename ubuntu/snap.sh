#!/usr/bin/env bash

xargs -a <(sed -E 's/^([^# ]*).*$/\1/g' snap.txt) -r -- sudo snap install

#!/usr/bin/env bash

grep -v '#' port.txt | xargs sudo port install

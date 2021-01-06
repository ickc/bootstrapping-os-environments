#!/usr/bin/env bash

grep -v '#' mas.txt | xargs mas install

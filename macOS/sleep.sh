#!/usr/bin/env bash

sudo rm -rf /var/vm/sleepimage
sudo pmset hibernatemode 0
pmset -g | grep hibernatemode
echo "hibernatemode 0 = suspend to RAM only (default on desktops)"

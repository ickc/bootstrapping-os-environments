#!/usr/bin/env bash

sudo pmset hibernatemode 0 &&
    sudo rm -rf /var/vm/sleepimage &&
    pmset -g | grep hibernatemode &&
    echo "hibernatemode 0 = suspend to RAM only (default on desktops)"

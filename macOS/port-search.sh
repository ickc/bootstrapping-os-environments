#!/usr/bin/env bash

# usage ./port-search.sh brew-cask.txt

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

while IFS="" read -r p || [ -n "$p" ]; do
    print_double_line
    echo port search $p
    port search $p
done < <(grep -v '#' $@)

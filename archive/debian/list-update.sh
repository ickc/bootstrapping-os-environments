#!/usr/bin/env bash

printline() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

printline

echo Consider add the following to apt.txt:
comm -23 <(apt-mark showmanual | sort -u) <(gzip -dc /var/log/installer/initial-status.gz | sed -n 's/^Package: //p' | sort -u) | xargs -i -n1 bash -c 'cat apt.txt | if ! grep -q ${0%% *} -; then echo $0; fi' {}

#!/usr/bin/env bash

set -e

echo 'Consider using Settings Sync extension instead.'

path2txt="$(dirname "${BASH_SOURCE[0]}")/code.txt"

temp=$(grep -v '#' "${path2txt}")
echo ${temp} | xargs -n1 code-insiders --install-extension

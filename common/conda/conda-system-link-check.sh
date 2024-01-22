#!/bin/bash

while IFS= read -r command; do
    # Check if the command is available in the PATH
    command -v "$command" > /dev/null 2>&1 || echo "$command"
done < conda-system-link.txt

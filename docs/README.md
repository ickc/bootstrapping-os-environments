---
title:	bsos—bootstraping OS environments
...

``` {.table}
---
header: false
markdown: true
include: badges.csv
...
```

# Description

Disclaimer: this is written for me, and at best served as a starting point for you. It is not documented. Good starting point would be to tailor the `*.txt` files to packages you want to install on your machines. A better design probably would be to separate install scripts and config files (`*.txt`) in different repo.

Setup macOS or Ubuntu in scripts so that it is repeatable and automatic.

Scripts to automate installations of softwares after a freshly installed OS — macOS or Ubuntu.

The goal is to automate as much as possible on setting up a new machine, an often tedious task when you want to erase the drive and reinstall everything. Tools like Time Machine could be an alternative, but often time you want to start fresh without all the legacy stuffs like applications and settings, etc.

These scripts provided an automated way to repeat what you did to the OSes. Whenever you install a new software, update the scripts accordingly to reflect what you did. So that in the future you can run the scripts and recover the "current status" of your machine.

For example, even something like editing a bash profile, rather than editing it directly (or backing it up), scripts are written to edit the bash profile instead so it is also automated.

# `conda.py`

See [`common/conda/README.md`](common/conda/README.md).

# Todo

- seperate the boilerplate and the custom `.txt` files for personalisation. This should be easier for forks.

# Intro

This is a minimal and isolated setup.

Follow `macOS/README.md`, except:

- don't install Xcode.
- don't register ssh to GitHub
- don't symlink to iCloud
- don't run mas.sh
- don't run brew.sh
- don't run conda-install.sh

# Maintaining

- some are symlink to parent dir
- whenever name are the same between this dir and parent dir, diff them to propagate the changes. Those inside current dir should have commented unused lines in `*.sh`, and all unused lines deleted in `*.txt`.

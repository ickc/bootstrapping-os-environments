# The Scripts

On the old computer:

- Use `list-update.sh` to print out packages you're using but not included in the scripts here.
- Optionally, use `list-installed-packages.sh </FOLDER/>`: to export lists of installed things into `FOLDER` for future references

On the freshly installed computer:

- `sudo apt install openssh-server zsh && chsh -s /bin/zsh`
- Generate SSH key and add it to GitHub.
- Install [dotfiles](https://github.com/ickc/dotfiles).
- Install ssh-dir.
- Install this repo: `mkdir -p ~/git/source; cd ~/git/source; git clone git@github.com:ickc/reproducible-os-environments.git || git clone https://github.com/ickc/reproducible-os-environments.git; cd reproducible-os-environments/macOS`
	- `apt.sh` / `raspbian.sh`
	- `brew.sh` (optional)
	- `deb.sh`

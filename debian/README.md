# The Scripts

On the old computer:

- Use `list-update.sh` to print out packages you're using but not included in the scripts here.
- Optionally, use `list-installed-packages.sh </FOLDER/>`: to export lists of installed things into `FOLDER` for future references

On the freshly installed computer:

- `sudo apt install openssh-server zsh tmux curl -y && chsh -s /bin/zsh`
- Generate SSH key and add it to GitHub.
- Install [dotfiles](https://github.com/ickc/dotfiles).
- Install ssh-dir.
- Install this repo: `mkdir -p ~/git/source; cd ~/git/source; git clone git@github.com:ickc/bootstrapping-os-environments.git || git clone https://github.com/ickc/bootstrapping-os-environments.git; cd bootstrapping-os-environments/debian`
	- `brew.sh` (optional)
	- `apt.sh` / `raspbian.sh`
		- `deb.sh`
			- `conda activate`
				- `conda-install.sh`
					- `jupyterlab.sh`
						- `jupyterlab-chrome.sh`

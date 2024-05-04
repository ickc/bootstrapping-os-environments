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

# Raspberry Pi 4

## UEFI

- update the EEPROM
	- to check: `sudo rpi-eeprom-update`
	- to update: `sudo rpi-update` and then reboot
- prepare SD card: [pftf/RPi4: Raspberry Pi 4 UEFI Firmware Images](https://github.com/pftf/RPi4). In order for the UEFI config to persist, as of writing, these conditions must be met:
	- use micro SD card rather than USB
	- format it with ESP flag
	- some micro SD card might not work, e.g. a 2GB micro SD card I have, but 4GB or 128GB are fine.
- Turn off 3GB limit: Device Manager → Raspberry Pi Configuration → Advanced Configuration

## memtest86

[memtest86](https://www.memtest86.com) can be run together with UEFI setup above. As of UEFI firmware v1.37, only single CPU mode would work.

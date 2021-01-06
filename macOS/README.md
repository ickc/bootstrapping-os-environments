# The Scripts

On the old Mac:

- Use `list-update.sh` to print out packages you're using but not included in the scripts here.
- Optionally, use `list-installed-packages.sh </FOLDER/>`: to export lists of installed things into `FOLDER` for future references

On the freshly installed Mac:

- open App Store, sign in and install Xcode.
- In command line, run e.g. `make` to trigger CLT install.
- In System Preferences, Sharing, activate remote ssh.
- Generate SSH key and add it to GitHub.
- Install [dotfiles](https://github.com/ickc/dotfiles), which requires the CLT.
- Install ssh-dir.
- Install this repo: `mkdir -p ~/git/source; cd ~/git/source; git clone git@github.com:ickc/reproducible-os-environments.git; cd reproducible-os-environments/macOS`
- remove sleep image (may already be the default): `sleep.sh`
- symlink iCloud Documents to have a simpler path: `ln -s "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Documents" "$HOME/iCloud"`
- Install Cocoa emacs emulation `install-cocoa-emacs-emulation.sh`
- Install package managers: `install.sh`
- restart shell for the new PATH to take effect
- Install packages (sub-level indicates depending on higher levels executed first)
	- `mas.sh`
		- `brew-cask.sh`
	- `brew.sh`
	- `port.sh`
	- `conda activate`
		- `conda-install.sh`
		- `jupyterlab.sh`
			- `jupyterlab-chrome.sh`
- upgrade package installers
	- `upgrade.sh`

# No Cli Install

Manual Settings:

- Terminal:
	- default solarized
	- change font to Consolas
	- change cursor to `|` and blink
- TextMate:  
	- install Solarized bundle
	- choose theme
	- set font to Consolas
- Safari extension:
	- Manually install
		- Tablinks: `%w. [%t](%u)%b`

Manual install these:

- [Sophos Antivirus](https://home.sophos.com/install/25032820d057eecb3e35f151a371114d/b82de6901f33736f4e43e37d013e0795) @manual(behindRegistrationWall) @cancel
- System Center EndPoint Protection from Berkeley Software Central?
- Davinci Resolve @manual(behindRegistrationWall) @cancel
- mathematica @manual(behindRegistrationWall)
- iOS Font Maker @cancel
- tsmuxerGUI @cancel
- Brother ControlCenter (DCP-7065 DN)
- hdapm @cancel
- BT747 @cancel
- [OS-X-SAT-SMART-Driver](https://binaryfruit.com/drivedx/usb-drive-support)
- Remote Camera Control @cancel
- MurGaa Auto Clicker @cancel
- ti connect @cancel
- WD Drive Utility @cancel
- Cisco AnyConnect - @replacedby(openconnect)
- Markdown quicklook @replacedby(ttscoff-mmd-quicklook)

## Fonts

- CYBERBIT FONT
- MathJax-TeX-fonts-otf
- SetoFont
- HanWang Zhuyin ruby fonts

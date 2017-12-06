# The Scripts

On the old Mac:

- `list-installed-packages.sh </FOLDER/>`: Export lists of installed things into `FOLDER`[^listPackages]
- Alternatively, `list-update.sh` will print out packages you're using but not included in the scripts here.

On the freshly installed Mac:

- remove sleep image: `sleep.sh`
- Install package managers: `install.sh` (make sure iCloud is signed in for `mas`, wait for Xcode installation finished before Return on command line)
- Install packages
	- `mas.sh`
		- `brew-cask.sh`
    		- `brew-cask-fonts.sh`
			- `download.sh`
	- `brew.sh`
		- `upgrade.sh`
			- `npm.sh`
			- `gem.sh`
			- `conda-install.sh`
			- `cabal.sh`
- upgrade package installers
	- `upgrade.sh`

[^listPackages]: This is for future reference only. The scripts below does not use this information. The idea is to use these files to keep track of what was installed before and update the scripts manually if needed.

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

- [Sophos Antivirus](https://home.sophos.com/install/25032820d057eecb3e35f151a371114d/b82de6901f33736f4e43e37d013e0795) @manual(behindRegistrationWall)
- Davinci Resolve @manual(behindRegistrationWall)
- mathematica @manual(behindRegistrationWall)
- iOS Font Maker
- SMARTReporter
- tsmuxerGUI
- Brother ControlCenter (DCP-7065 DN)
- hdapm
- BT747
- OS-X-SAT-SMART-Driver @unsign
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

# The Scripts

On the old Mac:

- `list-installed-packages.sh </FOLDER/>`: Export lists of installed things into `FOLDER` [^listPackages]
- `download.sh`: download `gnuize`

On the freshly installed Mac:

- remove sleep image: `sleep.sh`
- Install brew and npm: `install.sh`
- Install packages
	- `mas.sh`
		- `brew-cask.sh`
	- `brew.sh`
		- `upgrade.sh`
			- `npm.sh`
			- `gem.sh`
			- `pip.sh`
- upgrade package installers
	- `upgrade.sh`

[^listPackages]: This is for future reference only. The scripts below does not use this information. The idea is to use these files to keep track of what was installed before and update the scripts manually if needed.

# No Cli Install

Manual install these:

- Nvidia Driver Manager @waiting(cask)
- iOS Font Maker
- ColorMunki Photo @waiting(cask)
- Logos @waiting(cask)
- SMARTReporter
- Cisco AnyConnect - openconnect installed: Open client for Cisco AnyConnect VPN
- Davinci Resolve @manual(behindRegistrationWall)
- mathematica @manual(behindRegistrationWall)
- tsmuxerGUI
- Brother ControlCenter (DCP-7065 DN)
- ti connect @cancel
- Remoate Camera Control
- MurGaa Auto Clicker
- MultiMarkdown Composer @manual(requireMAS)
- Window Tidy @replaceby(spectacle)
- OS-X-SAT-SMART-Driver @unsign
- hdapm
- BT747
- WD Drive Utility: check cask
- Markdown quicklook @cask(ttscoff-mmd-quicklook)
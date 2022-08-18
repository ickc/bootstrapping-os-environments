# The Scripts

On the old Mac:

- Use `list-update.sh` to print out packages you're using but not included in the scripts here.
- Optionally, use `list-installed-packages.sh </FOLDER/>`: to export lists of installed things into `FOLDER` for future references
- Optionally, backup the wall papers. See [macOS Wallpaper Locations].

On the freshly installed Mac:

- open App Store, sign in and install Xcode, and run the followings meanwhile.
- In command line, run `xcode-select --install` or e.g. `make` to trigger CLT install.
	- `sudo xcodebuild -license accept`.
- In System Preferences, Sharing, activate remote ssh, select `Allow full disk access for remote users` if available, which probably is equivalent to the `Full Disk Access` setting below.
- `softwareupdate --install-rosetta --agree-to-license` to install rosetta for Apple Silicon.
- In System Preferences, `Security & Privacy -> Privacy -> Full Disk Access`, add `/usr/libexec/sshd-keygen-wrapper`[^sshd-keygen]. (This may be done automatically in later versions of macOS/mac.)
- Generate SSH key and add it to GitHub.
- Install [dotfiles](https://github.com/ickc/dotfiles), which requires the CLT.
- Install ssh-dir.
- Install this repo: `mkdir -p ~/git/source; cd ~/git/source; git clone git@github.com:ickc/bootstrapping-os-environments.git || git clone https://github.com/ickc/bootstrapping-os-environments.git; cd bootstrapping-os-environments/macOS`
- remove sleep image (may already be the default): `sleep.sh`
- symlink iCloud Documents to have a simpler path: `rm -f "$HOME/iCloud"; ln -s "$HOME/Library/Mobile Documents/com~apple~CloudDocs/iCloud" "$HOME/iCloud"`
- Install Cocoa emacs emulation `install-cocoa-emacs-emulation.sh`
- Install package managers: `install.sh`
- restart shell for the new PATH to take effect
- Install packages (sub-level indicates depending on higher levels executed first)
	- `../common/basher.sh`
	- `mas.sh`
		- `brew-cask.sh` (run after Xcode is installed)
	- `brew.sh` (you may need to run `softwareupdate --all --install --force` first to update the Command Line Tools (CLT))
	- `port.sh` (run after Xcode is installed)
	- `conda activate`
		- `conda-install.sh`
			- `jupyterlab.sh`
				- `jupyterlab-config.sh`
- upgrade package installers
	- `upgrade.sh`
- In System Preferences, `Security & Privacy -> Privacy -> Full Disk Access`, add `kitty`.

[^sshd-keygen]: [bash - Getting an “Operation not permitted” error when running commands after to SSHing from another machine to macOS - Super User](https://superuser.com/questions/1615072/getting-an-operation-not-permitted-error-when-running-commands-after-to-sshing)

# List of unsupported softwares in Apple Silicon

- `brew/imageoptim-cli`: [Unable to install on M1 / Apple Silicon · Issue #191 · JamieMason/ImageOptim-CLI](https://github.com/JamieMason/ImageOptim-CLI/issues/191)
- port:
	- testdisk
- conda:
	- mkl
	- pandoc-crossref
	- acor
	- toast
	- libsharp
	- intel-openmp
	- pickle5
	- pyslalib
	- make_arq

# List of softwares relying on Rosetta 2



- port:
	- stack
		- pandoc
		- shellcheck

# macOS Wallpaper Locations

Different versions of macOS may have wall papers in the following paths,

```bash
/Library/Desktop Pictures
/System/Library/Desktop Pictures
$HOME/Library/Application Support/com.apple.mobileAssetDesktop
/System/Library/AssetsV2/com_apple_MobileAsset_DesktopPicture
```

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

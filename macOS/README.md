# The Scripts

On the old Mac:

- Use `list-update.sh` to print out packages you're using but not included in the scripts here.
- Optionally, use `list-installed-packages.sh </FOLDER/>`: to export lists of installed things into `FOLDER` for future references
- Optionally, backup the wall papers. See [macOS Wallpaper Locations].

On the freshly installed Mac:

> [!TIP]
> 
> Use the following to check what is changed after customizing settings to make it reproducible next time.
>
> ```bash
> defaults read > defaults.pre.txt
> 
> # *make a change in Settings*
> 
> defaults read > defaults.post.txt
> 
> diff defaults.pre.txt defaults.post.txt
> ```
> 
> C.f. [sickcodes/osx-optimizer: OSX Optimizer: Optimize MacOS - Shell scripts to speed up your mac boot time, accelerate loading, and prevent unnecessary throttling.](https://github.com/sickcodes/osx-optimizer)

- ~~open App Store, sign in and install Xcode, and run the followings meanwhile.~~
	- ~~You may need to open Xcode explicitly for all components to be installed^[See [ios - Xcode build fails and repetitive requires command line developer tools install - Stack Overflow](https://stackoverflow.com/questions/72583801/xcode-build-fails-and-repetitive-requires-command-line-developer-tools-install/73703946#73703946).].~~
- In System Preferences, Sharing, activate remote ssh,
	- select `Allow full disk access for remote users` if available, which probably is equivalent to the `Full Disk Access` setting below.
	- In System Preferences, `Security & Privacy -> Privacy -> Full Disk Access`, add `/usr/libexec/sshd-keygen-wrapper`[^sshd-keygen]. (This may be done automatically in later versions of macOS/mac.)
- In command line, run `xcode-select --install` or e.g. `make` to trigger CLT install.
	- `sudo xcodebuild -license accept`.
- `softwareupdate --install-rosetta --agree-to-license` to install rosetta for Apple Silicon.
- Follow <../unix-minimal/README.md> to setup a minimal environment, which requires the CLT.
- `cd ~/git/source/bootstrapping-os-environments/macOS`
- remove sleep image (may already be the default): `sleep.sh`
- symlink iCloud Documents to have a simpler path: `rm -f "$HOME/iCloud"; ln -s "$HOME/Library/Mobile Documents/com~apple~CloudDocs/iCloud" "$HOME/iCloud"`
- Install Cocoa emacs emulation `install-cocoa-emacs-emulation.sh`
- Remap keys at launch: `key-remapping-hidutil.sh`
- Install package managers: `install.sh`
- restart shell for the new PATH to take effect
- Install packages (sub-level indicates depending on higher levels executed first)
	- `mas.sh`
	- `brew.sh` (you may need to run `softwareupdate --all --install --force` first to update the Command Line Tools (CLT))
		- `brew-cask.sh`
			- `tex.sh`
	- `port.sh` (run after Xcode is installed)
	- `conda activate`
		- `conda-install.sh`
			- `jupyterlab.sh`
				- `jupyterlab-config.sh`
- upgrade package installers
	- `upgrade.sh`
- In System Preferences, `Security & Privacy -> Privacy -> Full Disk Access`, add `kitty`.

[^sshd-keygen]: [bash - Getting an “Operation not permitted” error when running commands after to SSHing from another machine to macOS - Super User](https://superuser.com/questions/1615072/getting-an-operation-not-permitted-error-when-running-commands-after-to-sshing)

# After OS upgrade

Macports requires migration after an OS upgrade:

> A MacPorts installation is designed to work with a particular operating system and a particular hardware architecture.^[[Migration – MacPorts](https://trac.macports.org/wiki/Migration)]

Install the latest Xcode, Xcode Command Line Tools, then run

```bash
./port-uninstall.sh
./port-install.sh
./port.sh
```

to uninstall and reinstall macports, as well as all packages.

# sudo with Touch ID

Redo this after every major OS upgrade.

```bash
sudo nano /etc/pam.d/sudo
# add these
auth       optional       /opt/local/lib/pam/pam_reattach.so ignore_ssh
auth       sufficient     pam_tid.so
```

See <https://github.com/fabianishere/pam_reattach>.

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

- port: (These are moved to homebrew for now. c.f. <https://trac.macports.org/ticket/64063>.)
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

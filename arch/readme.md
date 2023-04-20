This is currently alpha stage—untested, and is just notes for now. So they aren't executables.

# Installation

Format the drive following [Advanced Format - ArchWiki](https://wiki.archlinux.org/title/Advanced_Format#Check_supported_sector_sizes_of_NVMe_drives):

- Setting native sector size
- blkdiscard once first
- when making FS, follow [Advanced Format - ArchWiki](https://wiki.archlinux.org/title/Advanced_Format#File_systems) to format at the right sector size.

Follow [Installation guide - ArchWiki](https://wiki.archlinux.org/title/Installation_guide#Post-installation).

Remember to setup the network (see [Network configuration - ArchWiki](https://wiki.archlinux.org/title/Network_configuration#Network_managers)), e.g. by

```sh
pacman -Syu
pacman -S grub efibootmgr tmux dhcpcd iotop mosh zsh which dhcpcd sudo inetutils neofetch ntp firewalld smartmontools nvme-cli exa # intel-ucode / amd-ucode
grub-mkconfig -o /boot/grub/grub.cfg
systemctl enable --now dhcpcd
systemctl enable --now ntpd.service
```

Follow [General recommendations - ArchWiki](https://wiki.archlinux.org/title/General_recommendations).

```sh
useradd -m -G wheel -s /usr/bin/zsh USERNAME
passwd USERNAME
visudo
# uncomment the line allowing group wheel to use sudo
```

Install yay: [Jguer/yay: Yet another Yogurt - An AUR Helper written in Go](https://github.com/Jguer/yay#source)

```sh
yay -S linux-headers zfs-dkms
```

- btop
- exa

## Nameserver

```sh
nano /etc/resolv.conf
```

E.g., add

```
nameserver 1.1.1.1
nameserver 1.0.0.1
```

Setup continuous TRIM following [Solid state drive - ArchWiki](https://wiki.archlinux.org/title/Solid_state_drive#Continuous_TRIM).

# Personalize

See [the README for debian](../debian/README.md).

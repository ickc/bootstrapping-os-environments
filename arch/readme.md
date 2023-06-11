Assume installation media is created from [Arch Linux - Downloads](https://archlinux.org/download/).

Below follows [Installation guide - ArchWiki](https://wiki.archlinux.org/title/Installation_guide#Post-installation) unless stated otherwise.

# ssh (optional)

This section follows [Install Arch Linux via SSH - ArchWiki](https://wiki.archlinux.org/title/Install_Arch_Linux_via_SSH) to setup ssh before installing.

On server where Arch Linux is to be installed,

```bash
# set root password for SSH
passwd
```

On local machine,

```bash
ssh -o StrictHostKeyChecking=no -o "UserKnownHostsFile /dev/null" root@archiso.local
```

# Basic checks

```bash
# verify internet is working
ip link
ping archlinux.org
# verify booting into UEFI if ls without problems
ls /sys/firmware/efi/efivars
# verify system clock is accurate
timedatectl
```

# Preparing the drive

## Advanced format

This section follows [Advanced Format - ArchWiki](https://wiki.archlinux.org/title/Advanced_Format#Check_supported_sector_sizes_of_NVMe_drives)

For NVMe device, check if the best format is used already:

```bash
for i in /dev/nvme*n1; do echo $i; bash -c "nvme id-ns -H $i | grep 'Relative Performance'"; done
# set to the best format shown above
nvme format --lbaf=I /dev/nvmeXn1
```

Optionally, perform `blkdiscard` like so

```bash
# set the list of nvme devices to blkdiscard
for i in ...; do blkdiscard /dev/nvme${i}n1; done
```

## Partition and format

```bash
device=nvme1n1
parted /dev/$device mklabel gpt
parted /dev/$device mkpart fat32 1MiB 301MiB
parted /dev/$device set 1 esp on
parted /dev/$device mkpart XFS 301MiB 100%
# assuming 4k sectors
mkfs.fat -S 4096 -F 32 /dev/${device}p1
mkfs.xfs -s size=4096 /dev/${device}p2
# mount
mount /dev/${device}p2 /mnt
mount --mkdir /dev/${device}p1 /mnt/boot
```

If encryption is needed,

```bash
device=nvme1n1
parted /dev/$device mklabel gpt
parted /dev/$device mkpart fat32 1MiB 301MiB
parted /dev/$device set 1 esp on
parted /dev/$device mkpart XFS 301MiB 100%
# encrypt
cryptsetup -y -v luksFormat /dev/${device}p2
cryptsetup open /dev/${device}p2 root
# assuming 4k sectors
mkfs.fat -S 4096 -F 32 /dev/${device}p1
mkfs.xfs -s size=4096 /dev/mapper/root
# mount
mount /dev/mapper/root /mnt
mount --mkdir /dev/${device}p1 /mnt/boot
```



# Installation

```bash
pacstrap -K /mnt base linux linux-firmware grub efibootmgr git base-devel nano tmux dhcpcd iotop mosh zsh which dhcpcd sudo inetutils neofetch ntp firewalld smartmontools nvme-cli exa btop lm_sensors # intel-ucode / amd-ucode
```

# Post-installation

## Fstab

```bash
genfstab -U /mnt >> /mnt/etc/fstab
```

## chroot

```bash
arch-chroot /mnt
```

## Timezone

```bash
ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime
hwclock --systohc
# verify
date
```

## locale

```bash
cat <<EOF > /etc/locale.gen
en_US.UTF-8 UTF-8
en_GB.UTF-8 UTF-8
en_HK.UTF-8 UTF-8
zh_HK.UTF-8 UTF-8
yue_HK UTF-8
EOF
locale-gen
echo 'LANG=en_US.UTF-8' > /etc/locale.conf
```

## hostname

```bash
HOSTNAME=...
echo $HOSTNAME > /etc/hostname
```

## Install firmwares

## initramfs

This section follows [dm-crypt/Encrypting an entire system - ArchWiki](https://wiki.archlinux.org/title/Dm-crypt/Encrypting_an_entire_system#Configuring_mkinitcpio).

Do this only if encryption is used in [Partition and format](#partition-and-format).

```bash
nano /etc/mkinitcpio.conf
# Following the guide using systemd-based initramfs
# edit the HOOK line to this
# HOOKS=(base systemd autodetect modconf kms keyboard sd-vconsole block sd-encrypt filesystems fsck)
# verify correct
grep -v '^#' /etc/mkinitcpio.conf
mkinitcpio -P
```

Record the stderr warnings for later.

## Kernel parameters

If encryption is used, first use `blkid` to find the device-UUID of e.g. `/dev/nvme1n1p2`.

```bash
nano /etc/default/grub
# edit this line with device-UUID replaced with the UUID found above
GRUB_CMDLINE_LINUX_DEFAULT="... quiet mitigations=off acpi_enforce_resources=lax rootflags=discard rd.luks.name=device-UUID=root root=/dev/mapper/root"
...
GRUB_ENABLE_CRYPTODISK=y
```

## Boot loader

```bash
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

Then reboot.

# Post-installation after reboot

This section follows [General recommendations - ArchWiki](https://wiki.archlinux.org/title/General_recommendations) unless stated otherwise.

## User

On server,

```sh
useradd -m -G wheel -s /usr/bin/zsh USERNAME
passwd USERNAME
EDITOR=nano visudo
# then uncomment the line allowing group wheel to use sudo
systemctl enable --now sshd
```

Now ssh into the system and continue.

## Network

This section follows [Network configuration - ArchWiki](https://wiki.archlinux.org/title/Network_configuration#Network_managers).

```sh
sudo systemctl enable --now dhcpcd
sudo systemctl enable --now ntpd.service
```

## AUR

Install yay: [Jguer/yay: Yet another Yogurt - An AUR Helper written in Go](https://github.com/Jguer/yay#source)

```sh
mkdir -p ~/git/read-only
cd ~/git/read-only
git clone https://aur.archlinux.org/yay.git
cd ~/git/read-only/yay
makepkg -si
rm -rf ~/git/read-only/yay
```

## Rate mirrors

```bash
yay -S rate-mirrors-bin
command -v rate-mirrors >/dev/null 2>&1 && bash -c 'rate-mirrors arch | sudo tee /etc/pacman.d/mirrorlist'
```

## initramfs again

From the warnings in stderr saved in [initramfs](#initramfs), follow this table to install missing packages: [mkinitcpio - ArchWiki](https://wiki.archlinux.org/title/Mkinitcpio#Possibly_missing_firmware_for_module_XXXX)

E.g. for lpc,

```bash
yay -S upd72020x-fw ast-firmware aic94xx-firmware linux-firmware-qlogic wd719x-firmware
```

## Sensors

```bash
# If SATA devices are present
sudo modprobe drivetemp
sudo lm-sensors
```

## Nameserver

```sh
sudo nano /etc/resolv.conf
```

E.g., add

```
nameserver 1.1.1.1
nameserver 1.0.0.1
```

## TRIM

Setup continuous TRIM following [Solid state drive - ArchWiki](https://wiki.archlinux.org/title/Solid_state_drive#Continuous_TRIM).

## Personalize

See [the README for debian](../debian/README.md).

# chroot maintenance

1. Boot to archiso
2. Optionally, [access remotely via ssh](#ssh-optional)
3. then

```bash
device=nvme1n1
cryptsetup open /dev/${device}p2 root
mount /dev/mapper/root /mnt
mount --mkdir /dev/${device}p1 /mnt/boot
arch-chroot /mnt
```

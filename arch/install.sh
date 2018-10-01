#!/usr/bin/env bash

# Note: this isn't executable yet as it hasn't been tested

DISK=${DISK:-sda}
PART=${PART:-sda}

# set up ssh
passwd

systemctl start sshd

# update system clock
timedatectl set-ntp true

parted /dev/$DISK
mkfs.fat /dev/${PART}1
mkfs.ext4 /dev/${PART}2

mount /dev/${PART}2 /mnt
mkdir /mnt/boot && mount /dev/${PART}1 /mnt/boot

pacstrap /mnt base base-devel

genfstab -U /mnt >> /mnt/etc/fstab

# chroot
arch-chroot /mnt

INSTALLHOSTNAME=${INSTALLHOSTNAME:-placeholder}

ln -sf /usr/share/zoneinfo/US/Pacific /etc/localtime

hwclock --systohc

echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen
echo 'LANG=en_US.UTF-8' > /etc/locale.conf

echo "$INSTALLHOSTNAME" > /etc/hostname

cat << EOF > /etc/hosts
127.0.0.1    localhost
::1    localhost
127.0.1.1    $INSTALLHOSTNAME.localdomain    $INSTALLHOSTNAME
EOF

pacman -S iw wpa_supplicant dialog intel-ucode grub efibootmgr openssh

grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=arch_grub

grub-mkconfig -o /boot/grub/grub.cfg

# root passwd
passwd

# setup
systemctl enable sshd
useradd -m -s /bin/zsh kolen
passwd kolen

# finalize
exit
umount -R /mnt

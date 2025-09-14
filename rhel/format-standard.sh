#!/usr/bin/env bash
#
# Automated drive partitioning for RHEL installation:
# - Single device (e.g., sdi, nvme0n1, etc.)
# - GPT partitioning:
#   p1: 512MiB  (EFI System Partition, FAT32)
#   p2: 1GiB    (XFS /boot)
#   p3: remainder (XFS /)
# - All partitions aligned to 1MiB and ending at 100%
#
set -euo pipefail

#############################################
# Configuration
#############################################
DEFAULT_DEV="/dev/sdi"

# Filesystem labels
EFI_LABEL="EFI"
BOOT_LABEL="BOOT"
ROOT_LABEL="ROOT"

# Flags / options
ASSUME_YES=0

#############################################
usage() {
  cat <<EOF
Usage: $0 [options] [DEVICE]

Options:
  --yes              Non-interactive (assume yes).
  --help             Show this help.

Arguments:
  DEVICE            Block device to partition (default: $DEFAULT_DEV)
                    Examples: sdi, nvme0n1, sda, etc.
                    Will be prefixed with /dev/ if not already present.

Example:
  $0 --yes sdi
  $0 --yes /dev/nvme0n1
  $0 sda
EOF
}

#############################################
# Parse arguments
#############################################
TARGET_DEV="$DEFAULT_DEV"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) ASSUME_YES=1 ;;
    --help) usage; exit 0 ;;
    *)
      # Treat as device name
      if [[ "$1" =~ ^/dev/ ]]; then
        TARGET_DEV="$1"
      else
        TARGET_DEV="/dev/$1"
      fi
      ;;
  esac
  shift
done

#############################################
# Root check
#############################################
if [[ $EUID -ne 0 ]]; then
  echo "Must run as root." >&2
  exit 1
fi

#############################################
# Validate block device
#############################################
if [[ ! -b "$TARGET_DEV" ]]; then
  echo "Device $TARGET_DEV not found or not a block device." >&2
  exit 1
fi

# Get device size for display
device_size=$(blockdev --getsize64 "$TARGET_DEV")
echo "Target device: $TARGET_DEV ($(numfmt --to=iec "$device_size"))"

#############################################
# Check if device is mounted and unmount
#############################################
echo "Checking for mounted partitions on $TARGET_DEV..."
mounted_parts=$(mount | grep "^$TARGET_DEV" | awk '{print $1}' || true)
if [[ -n "$mounted_parts" ]]; then
  echo "Found mounted partitions, unmounting..."
  echo "$mounted_parts" | while read -r partition; do
    echo "Unmounting $partition"
    umount "$partition" || {
      echo "Failed to unmount $partition, attempting lazy unmount..."
      umount -l "$partition" || {
        echo "Failed to unmount $partition even with lazy unmount" >&2
        exit 1
      }
    }
  done
fi

#############################################
# Confirm destructive action
#############################################
if [[ $ASSUME_YES -ne 1 ]]; then
  read -rp "About to DESTROY ALL DATA on $TARGET_DEV. Continue? [yes/NO] " ans
  if [[ "$ans" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

#############################################
# Wipe existing filesystem signatures
#############################################
echo "Wiping filesystem signatures from $TARGET_DEV..."
wipefs -af "$TARGET_DEV" || true

#############################################
# Partitioning with parted
#############################################
echo "Creating GPT partition table on $TARGET_DEV..."
parted -s "$TARGET_DEV" mklabel gpt

echo "Creating partitions..."
# Partition 1: EFI System Partition (512MiB)
# Start at 1MiB for proper alignment, end at 513MiB
parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary fat32 1 513
parted -s "$TARGET_DEV" set 1 esp on
parted -s "$TARGET_DEV" set 1 boot on

# Partition 2: /boot (1GiB)
# Start at 513MiB, end at 1537MiB (513 + 1024)
parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary xfs 513 1537

# Partition 3: / (remainder)
# Start at 1537MiB, use percentage for end to avoid alignment issues
parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary xfs 1537 100%

echo "Partition table created:"
parted "$TARGET_DEV" unit MiB print

#############################################
# Wait for kernel to recognize new partitions
#############################################
echo "Waiting for kernel to recognize new partitions..."
udevadm settle
partprobe "$TARGET_DEV"
sleep 2

#############################################
# Determine partition naming scheme
#############################################
# Handle different device naming schemes (sda1 vs nvme0n1p1)
if [[ "$TARGET_DEV" =~ nvme|mmcblk ]]; then
  P1="${TARGET_DEV}p1"
  P2="${TARGET_DEV}p2"
  P3="${TARGET_DEV}p3"
else
  P1="${TARGET_DEV}1"
  P2="${TARGET_DEV}2"
  P3="${TARGET_DEV}3"
fi

#############################################
# Format filesystems
#############################################
echo "Formatting EFI partition ($P1) as FAT32..."
mkfs.vfat -F32 -n "$EFI_LABEL" "$P1"

echo "Formatting boot partition ($P2) as XFS..."
mkfs.xfs -f -L "$BOOT_LABEL" "$P2"

echo "Formatting root partition ($P3) as XFS..."
mkfs.xfs -f -L "$ROOT_LABEL" "$P3"

#############################################
# Display results
#############################################
echo
echo "Partitioning and formatting completed successfully!"
echo
echo "Partition layout:"
lsblk "$TARGET_DEV"
echo
echo "Filesystem information:"
blkid | grep "$TARGET_DEV"
echo
echo "The device is now ready for RHEL installation."
echo
echo "Partition assignments:"
echo "  $P1 -> EFI System Partition (FAT32)"
echo "  $P2 -> /boot (XFS)"
echo "  $P3 -> / (XFS)"

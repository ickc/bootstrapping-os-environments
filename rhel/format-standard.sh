#!/usr/bin/env bash
#
# Automated drive partitioning for RHEL installation:
# - Single device (e.g., sdi, nvme0n1, etc.)
# - GPT or MBR partitioning (user choice):
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
DEFAULT_PARTITION_TYPE="gpt"

# Filesystem labels
EFI_LABEL="EFI"
BOOT_LABEL="BOOT"
ROOT_LABEL="ROOT"

# Flags / options
ASSUME_YES=0
PARTITION_TYPE="$DEFAULT_PARTITION_TYPE"

#############################################
usage() {
  cat <<EOF
Usage: $0 [options] [DEVICE]

Options:
  --yes              Non-interactive (assume yes).
  --gpt              Use GPT partition table (default).
  --mbr              Use MBR partition table (keeps UEFI partition).
  --help             Show this help.

Arguments:
  DEVICE            Block device to partition (default: $DEFAULT_DEV)
                    Examples: sdi, nvme0n1, sda, etc.
                    Will be prefixed with /dev/ if not already present.

Notes:
  - Both GPT and MBR modes create a UEFI ESP partition
  - MBR mode uses primary partitions with protective MBR for UEFI compatibility
  - GPT is recommended for modern systems and drives >2TB

Examples:
  $0 --yes --gpt sdi
  $0 --yes --mbr /dev/nvme0n1
  $0 --mbr sda
EOF
}

#############################################
# Parse arguments
#############################################
TARGET_DEV="$DEFAULT_DEV"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) ASSUME_YES=1 ;;
    --gpt) PARTITION_TYPE="gpt" ;;
    --mbr) PARTITION_TYPE="msdos" ;;
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

# Get device size for display and validation
device_size=$(blockdev --getsize64 "$TARGET_DEV")
device_size_gb=$((device_size / 1024 / 1024 / 1024))

echo "Target device: $TARGET_DEV ($(numfmt --to=iec "$device_size"))"
echo "Partition type: ${PARTITION_TYPE^^}"

# Warn about MBR limitations
if [[ "$PARTITION_TYPE" == "msdos" && $device_size_gb -gt 2048 ]]; then
  echo "WARNING: Device is larger than 2TB. MBR partition table may not support full capacity."
  echo "Consider using --gpt for drives larger than 2TB."
  if [[ $ASSUME_YES -ne 1 ]]; then
    read -rp "Continue with MBR anyway? [yes/NO] " ans
    if [[ "$ans" != "yes" ]]; then
      echo "Aborted. Use --gpt for large drives."
      exit 1
    fi
  fi
fi

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
  echo
  echo "About to DESTROY ALL DATA on $TARGET_DEV"
  echo "Partition type: ${PARTITION_TYPE^^}"
  echo "Device size: $(numfmt --to=iec "$device_size")"
  echo
  read -rp "Continue? [yes/NO] " ans
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
echo "Creating $PARTITION_TYPE partition table on $TARGET_DEV..."
parted -s "$TARGET_DEV" mklabel "$PARTITION_TYPE"

echo "Creating partitions..."

if [[ "$PARTITION_TYPE" == "gpt" ]]; then
  # GPT partitioning
  echo "Using GPT partitioning scheme..."
  
  # Partition 1: EFI System Partition (512MiB)
  parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary fat32 1 513
  parted -s "$TARGET_DEV" set 1 esp on
  parted -s "$TARGET_DEV" set 1 boot on

  # Partition 2: /boot (1GiB)
  parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary xfs 513 1537

  # Partition 3: / (remainder)
  parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary xfs 1537 100%

else
  # MBR partitioning (keeping UEFI support)
  echo "Using MBR partitioning scheme with UEFI compatibility..."
  
  # Partition 1: EFI System Partition (512MiB) - marked as FAT32 and bootable
  parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary fat32 1 513
  parted -s "$TARGET_DEV" set 1 boot on

  # Partition 2: /boot (1GiB)
  parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary xfs 513 1537

  # Partition 3: / (remainder)
  parted -s -a optimal "$TARGET_DEV" unit MiB mkpart primary xfs 1537 100%
  
  # Note: In MBR mode, we can't set the ESP flag, but the boot flag on partition 1
  # combined with FAT32 formatting will make it work for UEFI systems
fi

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
# Verify partitions exist
#############################################
echo "Verifying partitions exist..."
for partition in "$P1" "$P2" "$P3"; do
  if [[ ! -b "$partition" ]]; then
    echo "ERROR: Partition $partition not found after creation." >&2
    echo "Available partitions:"
    ls -la "${TARGET_DEV}"* || true
    exit 1
  fi
done

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
echo "Configuration used:"
echo "  Partition table: ${PARTITION_TYPE^^}"
echo "  Device: $TARGET_DEV ($(numfmt --to=iec "$device_size"))"
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
echo "  $P1 -> EFI System Partition (FAT32) - UEFI bootable"
echo "  $P2 -> /boot (XFS)"
echo "  $P3 -> / (XFS)"
echo
if [[ "$PARTITION_TYPE" == "msdos" ]]; then
  echo "Note: Using MBR with UEFI ESP. Modern UEFI systems should boot correctly."
  echo "The first partition is formatted as FAT32 and marked bootable for UEFI compatibility."
fi

#!/usr/bin/env bash
#
# Automated provisioning for the "ark" layout:
# - Two NVMe devices: one slightly smaller (mirror baseline), one slightly larger (extra cache partition)
# - GPT partitioning:
#   p1: 512MiB  (EFI System Partition, FAT32)            (both disks for redundancy; you may later only mount one)
#   p2: 1GiB    (RAID1 /boot, md0, metadata=1.0, XFS)
#   p3: ~183.1G (RAID1 root LUKS container, md1 -> LUKS -> XFS /)
#   p4: Remainder up to end of smaller disk (intended mirror member for ZFS or future use)
#   p5: (only on larger disk) remaining tail (cache, XFS, e.g. /var/cache)
#
# After arrays:
#   /dev/md0 -> mkfs.xfs -> /boot
#   /dev/md1 -> LUKS -> XFS -> /
#   LargerDisk p5 -> XFS -> /var/cache (optional)
#
# Optional: Create ZFS mirror: zpool create tank mirror <small>p4 <large>p4
#
set -euo pipefail

#############################################
# Configuration (adjust as needed)
#############################################
SMALL_DEV_DEFAULT="/dev/nvme0n1"
LARGE_DEV_DEFAULT="/dev/nvme1n1"

# Names for md arrays
MD_BOOT="/dev/md0"
MD_ROOT="/dev/md1"

# LUKS name
LUKS_NAME="cryptroot"

# Filesystem labels
EFI_LABEL="EFI"
BOOT_LABEL="BOOT"
ROOT_LABEL="ROOT"
CACHE_LABEL="CACHE"
ZFS_POOL="tank"

# Flags / options
DO_ZFS=0
DO_MOUNT=0
ASSUME_YES=0
CACHE_MOUNTPOINT="/var/cache"
TARGET_PREFIX="/mnt/target"   # Where to mount if DO_MOUNT=1
CREATE_CACHE=1                # Set to 0 to skip formatting/mounting p5
EFI_ON_BOTH=1                 # If 1, format EFI on BOTH disks. If 0, only on larger disk.

#############################################
usage() {
  cat <<EOF
Usage: $0 [options] [SMALL_DEV LARGE_DEV]

Options:
  --yes              Non-interactive (assume yes).
  --zfs              Create ZFS mirror on p4 partitions (requires zpool).
  --no-cache         Skip formatting/mounting p5 as cache.
  --mount            Mount created filesystems under \$TARGET_PREFIX.
  --efi-one          Only format EFI partition on larger disk (still creates on small, just not formatted).
  --help             Show this help.

Defaults:
  Smaller device: $SMALL_DEV_DEFAULT
  Larger  device: $LARGE_DEV_DEFAULT

Example:
  $0 --yes --zfs --mount
EOF
}

#############################################
# Parse arguments
#############################################
SMALL_DEV="$SMALL_DEV_DEFAULT"
LARGE_DEV="$LARGE_DEV_DEFAULT"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) ASSUME_YES=1 ;;
    --zfs) DO_ZFS=1 ;;
    --no-cache) CREATE_CACHE=0 ;;
    --mount) DO_MOUNT=1 ;;
    --efi-one) EFI_ON_BOTH=0 ;;
    --help) usage; exit 0 ;;
    /dev/*)
      if [[ "$SMALL_DEV" == "$SMALL_DEV_DEFAULT" && "$LARGE_DEV" == "$LARGE_DEV_DEFAULT" ]]; then
        SMALL_DEV="$1"
      elif [[ "$SMALL_DEV" != "$1" && "$LARGE_DEV" == "$LARGE_DEV_DEFAULT" ]]; then
        LARGE_DEV="$1"
      else
        echo "Unexpected extra device argument: $1" >&2
        exit 1
      fi
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
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
# Validate block devices
#############################################
for d in "$SMALL_DEV" "$LARGE_DEV"; do
  if [[ ! -b "$d" ]]; then
    echo "Device $d not found or not a block device." >&2
    exit 1
  fi
done

#############################################
# Auto-detect actual smaller / larger ordering
#############################################
size_small=$(blockdev --getsize64 "$SMALL_DEV")
size_large=$(blockdev --getsize64 "$LARGE_DEV")

if (( size_small > size_large )); then
  echo "Swapping devices: provided 'small' is actually larger."
  tmp="$SMALL_DEV"
  SMALL_DEV="$LARGE_DEV"
  LARGE_DEV="$tmp"
  size_small=$(blockdev --getsize64 "$SMALL_DEV")
  size_large=$(blockdev --getsize64 "$LARGE_DEV")
fi

echo "Detected smaller device: $SMALL_DEV ($(numfmt --to=iec "$size_small"))"
echo "Detected larger  device: $LARGE_DEV ($(numfmt --to=iec "$size_large"))"

#############################################
# Confirm destructive action
#############################################
if [[ $ASSUME_YES -ne 1 ]]; then
  read -rp "About to DESTROY ALL DATA on $SMALL_DEV and $LARGE_DEV. Continue? [yes/NO] " ans
  if [[ "$ans" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

#############################################
# Stop any pre-existing arrays referencing these disks
#############################################
echo "Stopping existing md arrays referencing the target devices (if any)..."
mdadm --detail --scan | awk '/ARRAY/ {print $2}' | while read -r arr; do
  if grep -qE "$(basename "$SMALL_DEV")|$(basename "$LARGE_DEV")" "/proc/mdstat" 2>/dev/null || mdadm --detail "$arr" 2>/dev/null | grep -qE "$(basename "$SMALL_DEV")|$(basename "$LARGE_DEV")"; then
    echo "Stopping array $arr"
    mdadm --stop "$arr" || true
  fi
done

# Wipe superblocks (whole disk)
echo "Zeroing possible old RAID superblocks..."
mdadm --zero-superblock "${SMALL_DEV}" || true
mdadm --zero-superblock "${LARGE_DEV}" || true

# Also wipe partition-level superblocks (if partitions exist from prior runs)
for p in {1..6}; do
  mdadm --zero-superblock "${SMALL_DEV}p$p" 2>/dev/null || true
  mdadm --zero-superblock "${LARGE_DEV}p$p" 2>/dev/null || true
done

#############################################
# Partitioning
#############################################
# Layout (MiB):
# small:
#   1    - 513      : 512MiB (p1 EFI)
#   513  - 1537     : 1024MiB (p2 /boot RAID)
#   1537 - 184642   : 183105MiB (p3 root RAID/LUKS)
#   184642 - 100%   : remainder (p4 ZFS mirror member)
#
# large:
#   same p1..p3
#   184642 - 953869 : p4 (match small disk end-of-disk size to allow ZFS mirror of same size)
#   953869 - 100%   : p5 (cache)
#

echo "Creating GPT and partitions on $SMALL_DEV ..."
parted -s -a optimal "$SMALL_DEV" mklabel gpt
parted -s -a optimal "$SMALL_DEV" unit MiB mkpart primary 1 513
parted -s -a optimal "$SMALL_DEV" unit MiB mkpart primary 513 1537
parted -s -a optimal "$SMALL_DEV" unit MiB mkpart primary 1537 184642
parted -s -a optimal "$SMALL_DEV" unit MiB mkpart primary 184642 100%
parted -s "$SMALL_DEV" set 1 esp on
parted -s "$SMALL_DEV" set 1 boot on
parted -s "$SMALL_DEV" set 2 raid on
parted -s "$SMALL_DEV" set 3 raid on

echo "Creating GPT and partitions on $LARGE_DEV ..."
parted -s -a optimal "$LARGE_DEV" mklabel gpt
parted -s -a optimal "$LARGE_DEV" unit MiB mkpart primary 1 513
parted -s -a optimal "$LARGE_DEV" unit MiB mkpart primary 513 1537
parted -s -a optimal "$LARGE_DEV" unit MiB mkpart primary 1537 184642
parted -s -a optimal "$LARGE_DEV" unit MiB mkpart primary 184642 953869
parted -s -a optimal "$LARGE_DEV" unit MiB mkpart primary 953869 100%
parted -s "$LARGE_DEV" set 1 esp on
parted -s "$LARGE_DEV" set 1 boot on
parted -s "$LARGE_DEV" set 2 raid on
parted -s "$LARGE_DEV" set 3 raid on

echo "Partition tables created:"
parted "$SMALL_DEV" unit MiB print
parted "$LARGE_DEV" unit MiB print

#############################################
# Create MD arrays
#############################################
echo "Creating RAID1 for /boot ($MD_BOOT)..."
mdadm --create "$MD_BOOT" --metadata=1.0 --level=1 --raid-devices=2 \
  "${SMALL_DEV}p2" "${LARGE_DEV}p2"

echo "Creating RAID1 for root ($MD_ROOT)..."
mdadm --create "$MD_ROOT" --level=1 --raid-devices=2 \
  "${SMALL_DEV}p3" "${LARGE_DEV}p3"

# Wait for arrays to become active
udevadm settle
cat /proc/mdstat

#############################################
# LUKS on root array
#############################################
echo "Setting up LUKS on $MD_ROOT ..."
if [[ $ASSUME_YES -eq 1 ]]; then
  echo "Using --batch-mode for cryptsetup."
  cryptsetup luksFormat --batch-mode "$MD_ROOT"
else
  cryptsetup luksFormat "$MD_ROOT"
fi

cryptsetup open "$MD_ROOT" "$LUKS_NAME"

#############################################
# Filesystems
#############################################
SMALL_P1="${SMALL_DEV}p1"
LARGE_P1="${LARGE_DEV}p1"
CACHE_PART="${LARGE_DEV}p5"
BOOT_MD="$MD_BOOT"
ROOT_MAPPER="/dev/mapper/$LUKS_NAME"

# EFI: Format on one or both
if [[ $EFI_ON_BOTH -eq 1 ]]; then
  echo "Formatting BOTH EFI partitions as FAT32."
  mkfs.vfat -F32 -n "${EFI_LABEL}A" "$SMALL_P1"
  mkfs.vfat -F32 -n "${EFI_LABEL}B" "$LARGE_P1"
else
  echo "Formatting ONLY large disk EFI partition."
  mkfs.vfat -F32 -n "$EFI_LABEL" "$LARGE_P1"
fi

echo "Formatting /boot (XFS)..."
mkfs.xfs -f -L "$BOOT_LABEL" "$BOOT_MD"

echo "Formatting root (XFS inside LUKS)..."
mkfs.xfs -f -L "$ROOT_LABEL" "$ROOT_MAPPER"

if [[ $CREATE_CACHE -eq 1 ]]; then
  echo "Formatting cache partition (XFS)..."
  mkfs.xfs -f -L "$CACHE_LABEL" "$CACHE_PART"
fi

#############################################
# Optional ZFS
#############################################
if [[ $DO_ZFS -eq 1 ]]; then
  if ! command -v zpool >/dev/null 2>&1; then
    echo "zpool command not found. Install ZFS tools first." >&2
    exit 1
  fi
  echo "Creating ZFS mirror pool ($ZFS_POOL) on p4 partitions..."
  zpool create -f -o ashift=12 "$ZFS_POOL" mirror "${SMALL_DEV}p4" "${LARGE_DEV}p4"
  zpool status "$ZFS_POOL"
fi

#############################################
# Mount (optional)
#############################################
if [[ $DO_MOUNT -eq 1 ]]; then
  echo "Mounting filesystems under $TARGET_PREFIX ..."
  mkdir -p "$TARGET_PREFIX"
  mount "$ROOT_MAPPER" "$TARGET_PREFIX"
  mkdir -p "$TARGET_PREFIX/boot"
  mount "$BOOT_MD" "$TARGET_PREFIX/boot"

  # Decide which EFI to mount (choose larger)
  mkdir -p "$TARGET_PREFIX/boot/efi"
  if [[ $EFI_ON_BOTH -eq 1 ]]; then
    mount "$LARGE_P1" "$TARGET_PREFIX/boot/efi"
  else
    mount "$LARGE_P1" "$TARGET_PREFIX/boot/efi"
  fi

  if [[ $CREATE_CACHE -eq 1 ]]; then
    mkdir -p "$TARGET_PREFIX/$CACHE_MOUNTPOINT"
    mount "$CACHE_PART" "$TARGET_PREFIX/$CACHE_MOUNTPOINT"
  fi

  echo "Mount layout:"
  findmnt -R "$TARGET_PREFIX"
fi

#############################################
# mdadm.conf suggestion
#############################################
echo
echo "You can record array metadata for the installed system with:"
echo "  mdadm --detail --scan >> /etc/mdadm.conf"
echo
echo "Then inside chroot or installer environment, ensure /etc/crypttab is updated:"
echo "  echo '$LUKS_NAME UUID=\$(blkid -s UUID -o value $MD_ROOT) none luks' >> /etc/crypttab"
echo
echo "Finished provisioning steps."

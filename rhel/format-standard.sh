#!/bin/bash

# RHEL Drive Partitioning Script
# Usage: ./partition_drive.sh <device>
# Example: ./partition_drive.sh sdi

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to validate device argument
validate_device() {
    local device=$1
    
    # Check if device starts with /dev/
    if [[ ! "$device" =~ ^/dev/ ]]; then
        device="/dev/$device"
    fi
    
    # Check if device exists
    if [[ ! -b "$device" ]]; then
        print_error "Device $device does not exist or is not a block device"
        exit 1
    fi
    
    echo "$device"
}

# Function to unmount all partitions on the device
unmount_device() {
    local device=$1
    print_info "Unmounting all partitions on $device..."
    
    # Find all mounted partitions for this device
    local mounted_partitions=$(mount | grep "^$device" | awk '{print $1}' || true)
    
    if [[ -n "$mounted_partitions" ]]; then
        while IFS= read -r partition; do
            if [[ -n "$partition" ]]; then
                print_info "Unmounting $partition"
                umount "$partition" || print_warning "Failed to unmount $partition (may not be mounted)"
            fi
        done <<< "$mounted_partitions"
    else
        print_info "No mounted partitions found on $device"
    fi
}

# Function to destroy existing partition table
destroy_partition_table() {
    local device=$1
    print_info "Destroying existing partition table on $device..."
    
    # Use parted to create a new GPT label (this destroys existing partitions)
    parted -s "$device" mklabel gpt
    print_success "Partition table destroyed and GPT label created"
}

# Function to create partitions
create_partitions() {
    local device=$1
    print_info "Creating partitions on $device..."
    
    # Create EFI partition (1st partition): 1MiB to 513MiB
    print_info "Creating EFI partition (512MiB)..."
    parted -s "$device" mkpart primary fat32 1MiB 513MiB
    parted -s "$device" set 1 esp on
    
    # Create /boot partition (2nd partition): 513MiB to 1537MiB (513 + 1024)
    print_info "Creating /boot partition (1GiB)..."
    parted -s "$device" mkpart primary ext4 513MiB 1537MiB
    
    # Create root partition (3rd partition): 1537MiB to 100%
    print_info "Creating root partition (remaining space)..."
    parted -s "$device" mkpart primary xfs 1537MiB 100%
    
    # Ensure all changes are written
    parted -s "$device" align-check optimal 1
    parted -s "$device" align-check optimal 2
    parted -s "$device" align-check optimal 3
    
    print_success "All partitions created successfully"
}

# Function to format partitions
format_partitions() {
    local device=$1
    print_info "Formatting partitions..."
    
    # Wait a moment for the kernel to recognize the new partitions
    sleep 2
    partprobe "$device"
    sleep 2
    
    # Format EFI partition as FAT32
    print_info "Formatting EFI partition (${device}1) as FAT32..."
    mkfs.fat -F32 "${device}1"
    
    # Format /boot partition as ext4
    print_info "Formatting /boot partition (${device}2) as ext4..."
    mkfs.ext4 -F "${device}2"
    
    # Format root partition as XFS
    print_info "Formatting root partition (${device}3) as XFS..."
    mkfs.xfs -f "${device}3"
    
    print_success "All partitions formatted successfully"
}

# Function to display partition information
show_partition_info() {
    local device=$1
    print_info "Partition layout for $device:"
    parted -s "$device" print
    
    print_info "Filesystem information:"
    lsblk -f "$device"
}

# Main function
main() {
    # Check if device argument is provided
    if [[ $# -ne 1 ]]; then
        print_error "Usage: $0 <device>"
        print_error "Example: $0 sdi"
        print_error "Example: $0 /dev/sdi"
        exit 1
    fi
    
    # Check if running as root
    check_root
    
    # Validate and normalize device path
    local device=$(validate_device "$1")
    
    print_warning "WARNING: This will DESTROY ALL DATA on $device!"
    print_warning "The following operations will be performed:"
    echo "  1. Unmount all partitions on $device"
    echo "  2. Destroy existing partition table"
    echo "  3. Create new GPT partition table"
    echo "  4. Create EFI partition (512MiB, FAT32)"
    echo "  5. Create /boot partition (1GiB, ext4)"
    echo "  6. Create root partition (remaining space, XFS)"
    echo "  7. Format all partitions"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Operation cancelled by user"
        exit 0
    fi
    
    print_info "Starting partitioning process for $device..."
    
    # Execute partitioning steps
    unmount_device "$device"
    destroy_partition_table "$device"
    create_partitions "$device"
    format_partitions "$device"
    
    print_success "Drive partitioning completed successfully!"
    show_partition_info "$device"
    
    print_info "Your drive is now ready for RHEL installation with:"
    echo "  ${device}1 - EFI System Partition (512MiB, FAT32)"
    echo "  ${device}2 - Boot Partition (1GiB, ext4)"
    echo "  ${device}3 - Root Partition (remaining space, XFS)"
}

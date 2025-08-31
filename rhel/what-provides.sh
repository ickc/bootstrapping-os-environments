#!/bin/bash

# Script to find packages providing executables on RHEL 10
# Usage: ./find_packages.sh <input_file>

# Check if input file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_file>"
    echo "Example: $0 executables.txt"
    exit 1
fi

INPUT_FILE="$1"
DNF_FILE="dnf.txt"
MISSING_FILE="missing.txt"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found!"
    exit 1
fi

# Clear output files
> "$DNF_FILE"
> "$MISSING_FILE"

echo "Processing executables from '$INPUT_FILE'..."
echo "Found packages will be written to '$DNF_FILE'"
echo "Missing executables will be written to '$MISSING_FILE'"
echo

# Counter for progress
total_lines=$(wc -l < "$INPUT_FILE")
current_line=0

# Read file line by line
while IFS= read -r executable || [ -n "$executable" ]; do
    # Skip empty lines
    if [ -z "$executable" ]; then
        continue
    fi
    
    ((current_line++))
    echo "Processing ($current_line/$total_lines): $executable"
    
    # Try to find package providing the executable
    # We'll check both direct executable name and full path variants
    package_info=""
    
    # Try different path patterns where the executable might be found
    for path_pattern in "$executable" "*/$executable" "/usr/bin/$executable" "/bin/$executable" "/usr/sbin/$executable" "/sbin/$executable"; do
        # Use dnf provides to find the package
        result=$(dnf provides "$path_pattern" 2>/dev/null | grep -E "^[^[:space:]]+\s+:" | head -n1)
        
        if [ -n "$result" ]; then
            # Extract package name (everything before the first colon and space)
            package_name=$(echo "$result" | cut -d':' -f1 | awk '{print $1}')
            if [ -n "$package_name" ]; then
                package_info="$package_name"
                break
            fi
        fi
    done
    
    # Write result to appropriate file
    if [ -n "$package_info" ]; then
        # Extract just the package name without version/arch info
        # Remove everything after the first dash-digit pattern or .el pattern
        clean_package_name=$(echo "$package_info" | sed 's/-[0-9].*$//' | sed 's/\.el.*$//')
        echo "$clean_package_name" >> "$DNF_FILE"
        echo "  → Found: $clean_package_name (from $package_info)"
    else
        echo "$executable" >> "$MISSING_FILE"
        echo "  → Not found"
    fi
    
done < "$INPUT_FILE"

echo
echo "Processing complete!"
echo "Found packages: $(wc -l < "$DNF_FILE") (saved to $DNF_FILE)"
echo "Missing executables: $(wc -l < "$MISSING_FILE") (saved to $MISSING_FILE)"

# Show summary
if [ -s "$DNF_FILE" ]; then
    echo
    echo "=== Found Packages ==="
    cat "$DNF_FILE"
fi

if [ -s "$MISSING_FILE" ]; then
    echo
    echo "=== Missing Executables ==="
    cat "$MISSING_FILE"
fi

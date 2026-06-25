#!/usr/bin/env python3

"""
Script to find packages providing executables on RHEL 10
Usage: python3 find_packages.py <input_file>

Input format supports:
- ## comment lines (ignored)
- # commented package lines (ignored) 
- package_name # inline comment (extracts package_name)
- package_name (regular package)
"""

import sys
import subprocess
import re
import os

def extract_package_name(package_info):
    """
    Extract clean package name from dnf output.
    E.g., 'bash-5.2.26-6.el10.x86_64' -> 'bash'
    """
    if not package_info:
        return None
    
    # Remove everything after first dash followed by digit, or .el pattern
    clean_name = re.sub(r'-\d.*$', '', package_info)
    clean_name = re.sub(r'\.el.*$', '', clean_name)
    
    return clean_name

def parse_input_line(line):
    """
    Parse input line and extract package name if it's not a comment.
    
    Returns:
        tuple: (package_name, is_valid)
        - package_name: extracted package name or None
        - is_valid: True if this line should be processed
    """
    # Strip whitespace
    line = line.strip()
    
    # Skip empty lines
    if not line:
        return None, False
    
    # Skip comment lines starting with ##
    if line.startswith('##'):
        return None, False
    
    # Skip commented package lines starting with #
    if line.startswith('#'):
        return None, False
    
    # Handle lines with inline comments (package_name # comment)
    if '#' in line:
        package_name = line.split('#')[0].strip()
    else:
        package_name = line.strip()
    
    # Validate package name (should not be empty after processing)
    if not package_name:
        return None, False
    
    # Basic validation - package name should be reasonable
    if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\-\._+]*$', package_name):
        return package_name, True
    
    return None, False

def find_package_for_executable(executable):
    """
    Use dnf provides to find which package provides the executable.
    Try different path patterns where the executable might be found.
    """
    path_patterns = [
        executable,
        f"*/{executable}",
        f"/usr/bin/{executable}",
        f"/bin/{executable}",
        f"/usr/sbin/{executable}",
        f"/sbin/{executable}"
    ]
    
    for pattern in path_patterns:
        try:
            # Run dnf provides command
            result = subprocess.run(
                ['dnf', 'provides', pattern],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                # Look for lines that match package format (package : description)
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    # Skip metadata messages and other non-package lines
                    if ('metadata expiration' in line.lower() or 
                        'repo' in line.lower() or
                        line.startswith('Last') or
                        not line or
                        not ':' in line):
                        continue
                    
                    # Look for actual package lines (should not start with whitespace)
                    if ':' in line and not line.startswith(' '):
                        # Extract package name (everything before the first colon)
                        package_name = line.split(':')[0].strip()
                        # Verify it looks like a package name (contains alphanumeric and allowed chars)
                        if package_name and re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\-\._+]*', package_name):
                            return package_name
                            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            continue
    
    return None

def process_executables_file(input_file):
    """
    Process the input file containing executables and find their packages.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return False
    
    dnf_file = 'dnf.txt'
    missing_file = 'missing.txt'
    
    # Clear output files
    open(dnf_file, 'w').close()
    open(missing_file, 'w').close()
    
    print(f"Processing executables from '{input_file}'...")
    print(f"Found packages will be written to '{dnf_file}'")
    print(f"Missing executables will be written to '{missing_file}'")
    print()
    
    # Read input file and parse lines
    try:
        with open(input_file, 'r') as f:
            all_lines = f.readlines()
        
        # Parse lines to extract valid package names
        executables = []
        skipped_lines = 0
        
        for line_num, line in enumerate(all_lines, 1):
            package_name, is_valid = parse_input_line(line)
            if is_valid and package_name:
                executables.append(package_name)
            else:
                skipped_lines += 1
                if line.strip() and not line.strip().startswith('#'):
                    print(f"Line {line_num}: Skipped invalid line: '{line.strip()}'")
        
        total_lines = len(executables)
        print(f"Found {total_lines} valid package names to process (skipped {skipped_lines} comment/empty lines)")
        print()
        
        found_packages = []
        missing_executables = []
        
        # Process each executable
        for i, executable in enumerate(executables, 1):
            print(f"Processing ({i}/{total_lines}): {executable}")
            
            # Find package for this executable
            package_info = find_package_for_executable(executable)
            
            if package_info:
                # Extract clean package name
                clean_name = extract_package_name(package_info)
                if clean_name:
                    found_packages.append(clean_name)
                    print(f"  → Found: {clean_name} (from {package_info})")
                else:
                    missing_executables.append(executable)
                    print("  → Not found")
            else:
                missing_executables.append(executable)
                print("  → Not found")
        
        # Write results to files
        if found_packages:
            with open(dnf_file, 'w') as f:
                for package in found_packages:
                    f.write(f"{package}\n")
        
        if missing_executables:
            with open(missing_file, 'w') as f:
                for executable in missing_executables:
                    f.write(f"{executable}\n")
        
        # Print summary
        print()
        print("Processing complete!")
        print(f"Found packages: {len(found_packages)} (saved to {dnf_file})")
        print(f"Missing executables: {len(missing_executables)} (saved to {missing_file})")
        
        # Show summary
        if found_packages:
            print()
            print("=== Found Packages ===")
            for package in found_packages:
                print(package)
        
        if missing_executables:
            print()
            print("=== Missing Executables ===")
            for executable in missing_executables:
                print(executable)
        
        return True
        
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python3 find_packages.py <input_file>")
        print("Example: python3 find_packages.py executables.txt")
        print()
        print("Input format supports:")
        print("  ## comment lines (ignored)")
        print("  # commented package lines (ignored)")
        print("  package_name # inline comment (extracts package_name)")
        print("  package_name (regular package)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not process_executables_file(input_file):
        sys.exit(1)

if __name__ == "__main__":
    main()

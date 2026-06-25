#!/usr/bin/env python3
"""
RHEL Package Information Extractor

This script reads a list of package names from a text file and extracts:
- Short description of each package
- List of executables provided by each package

Usage: python3 package_info.py <input_file.txt> <output_file.yaml>
"""

import subprocess
import sys
import yaml
import re
from pathlib import Path


def run_command(cmd):
    """Run a shell command and return stdout, stderr, and return code."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", f"Error running command: {e}", 1


def get_package_description(package_name):
    """Get package description using dnf info."""
    cmd = f"dnf info {package_name} 2>/dev/null"
    stdout, stderr, returncode = run_command(cmd)
    
    if returncode != 0:
        # Try with yum as fallback
        cmd = f"yum info {package_name} 2>/dev/null"
        stdout, stderr, returncode = run_command(cmd)
    
    if returncode == 0:
        # Parse the output to extract description
        lines = stdout.split('\n')
        description_started = False
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Description'):
                description_started = True
                # Get the part after the colon
                desc_part = line.split(':', 1)
                if len(desc_part) > 1:
                    desc_text = desc_part[1].strip()
                    if desc_text:
                        description_lines.append(desc_text)
                continue
            elif description_started:
                if line and not line.startswith(('Name', 'Version', 'Release', 'Architecture', 
                                               'Size', 'Source', 'Repository', 'Summary',
                                               'URL', 'License', 'Provides', 'Requires')):
                    description_lines.append(line)
                elif line.startswith(('Name', 'Version', 'Release')):
                    break
        
        if description_lines:
            return ' '.join(description_lines)
        
        # Fallback to summary if description not found
        for line in lines:
            if line.startswith('Summary'):
                summary_part = line.split(':', 1)
                if len(summary_part) > 1:
                    return summary_part[1].strip()
    
    return "Description not available"


def get_package_executables(package_name):
    """Get list of executables provided by the package."""
    executables = []
    
    # First, try to get the list of files from the package
    cmd = f"rpm -ql {package_name} 2>/dev/null"
    stdout, stderr, returncode = run_command(cmd)
    
    if returncode != 0:
        # If package is not installed, try to get file list from repository
        cmd = f"dnf repoquery --list {package_name} 2>/dev/null"
        stdout, stderr, returncode = run_command(cmd)
        
        if returncode != 0:
            # Try with yum
            cmd = f"yum repoquery --list {package_name} 2>/dev/null"
            stdout, stderr, returncode = run_command(cmd)
    
    if returncode == 0:
        lines = stdout.split('\n')
        bin_dirs = ['/usr/bin/', '/bin/', '/usr/sbin/', '/sbin/', '/usr/local/bin/']
        
        for line in lines:
            line = line.strip()
            if line:
                for bin_dir in bin_dirs:
                    if line.startswith(bin_dir) and '/' not in line[len(bin_dir):]:
                        # Extract executable name
                        executable = line[len(bin_dir):]
                        if executable and executable not in executables:
                            executables.append(executable)
    
    return sorted(executables) if executables else []


def process_packages(input_file, output_file):
    """Process the list of packages and generate YAML output."""
    try:
        with open(input_file, 'r') as f:
            package_names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False
    
    if not package_names:
        print("Error: No package names found in input file.")
        return False
    
    print(f"Processing {len(package_names)} packages...")
    
    package_info = {}
    
    for i, package_name in enumerate(package_names, 1):
        print(f"Processing {i}/{len(package_names)}: {package_name}")
        
        # Get package description
        description = get_package_description(package_name)
        
        # Get executables
        executables = get_package_executables(package_name)
        
        package_info[package_name] = {
            'description': description,
            'executables': executables
        }
    
    # Write YAML output
    try:
        with open(output_file, 'w') as f:
            yaml.dump(package_info, f, default_flow_style=False, sort_keys=True, indent=2)
        
        print(f"Successfully wrote package information to '{output_file}'")
        return True
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 package_info.py <input_file.txt> <output_file.yaml>")
        print("\nExample:")
        print("  python3 package_info.py packages.txt package_info.yaml")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Validate input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Check if we're running on a RHEL-compatible system
    cmd = "which dnf || which yum"
    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        print("Warning: Neither 'dnf' nor 'yum' found. This script is designed for RHEL-compatible systems.")
    
    success = process_packages(input_file, output_file)
    
    if success:
        print("\nPackage information extraction completed successfully!")
        sys.exit(0)
    else:
        print("\nPackage information extraction failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

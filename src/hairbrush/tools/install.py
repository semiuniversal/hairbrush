#!/usr/bin/env python3
"""
Installation helper script for the Dual Airbrush Export extension.
This script will copy the necessary files to the Inkscape extensions directory.
"""

import os
import sys
import shutil
import platform
import argparse
from pathlib import Path

def get_inkscape_extensions_dir():
    """
    Get the Inkscape extensions directory based on the operating system.
    """
    home = Path.home()
    
    if platform.system() == "Windows":
        return home / "AppData" / "Roaming" / "inkscape" / "extensions"
    elif platform.system() == "Darwin":  # macOS
        return home / "Library" / "Application Support" / "org.inkscape.Inkscape" / "config" / "inkscape" / "extensions"
    else:  # Linux and others
        return home / ".config" / "inkscape" / "extensions"

def find_extension_files():
    """
    Find the extension files in the package.
    """
    # Try to find the extension files in the package
    package_dir = Path(__file__).parent.parent.parent.parent  # Go up to the project root
    
    # Look in common locations
    locations = [
        package_dir / "inkscape_extension",
        package_dir / "extensions",
        package_dir / "inkscape",
    ]
    
    for location in locations:
        inx_file = location / "dual_airbrush_export.inx"
        py_file = location / "dual_airbrush_export.py"
        
        if inx_file.exists() and py_file.exists():
            return location, inx_file, py_file
    
    return None, None, None

def install_extension(dest_dir=None, force=False):
    """
    Install the Dual Airbrush Export extension to the Inkscape extensions directory.
    
    Args:
        dest_dir: Destination directory (if None, use default Inkscape extensions dir)
        force: Whether to overwrite existing files
    """
    if dest_dir is None:
        dest_dir = get_inkscape_extensions_dir()
    
    # Create destination directory if it doesn't exist
    dest_dir = Path(dest_dir)
    if not dest_dir.exists():
        print(f"Creating directory: {dest_dir}")
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Find extension files
    source_dir, inx_file, py_file = find_extension_files()
    
    if inx_file is None or py_file is None:
        print("Error: Could not find extension files.")
        print("Make sure you have the inkscape_extension directory in your project.")
        return False
    
    # Copy extension files
    print(f"Copying {inx_file} to {dest_dir}")
    shutil.copy2(inx_file, dest_dir)
    
    print(f"Copying {py_file} to {dest_dir}")
    shutil.copy2(py_file, dest_dir)
    
    # Create hairbrush directory in extensions folder
    hairbrush_dest = dest_dir / "hairbrush"
    if hairbrush_dest.exists() and not force:
        print(f"Warning: {hairbrush_dest} already exists. Use --force to overwrite.")
    else:
        if hairbrush_dest.exists():
            print(f"Removing existing {hairbrush_dest}")
            shutil.rmtree(hairbrush_dest)
        
        # Find hairbrush source directory
        hairbrush_src = Path(__file__).parent.parent  # src/hairbrush
        
        print(f"Copying hairbrush package to {hairbrush_dest}")
        shutil.copytree(hairbrush_src, hairbrush_dest)
    
    print("\nInstallation complete!")
    print(f"Extension installed to: {dest_dir}")
    print("Please restart Inkscape to use the extension.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Install Dual Airbrush Export extension for Inkscape")
    parser.add_argument("--dest", help="Custom destination directory")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing files")
    args = parser.parse_args()
    
    success = install_extension(args.dest, args.force)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 
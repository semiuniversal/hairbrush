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

def install_extension(source_dir, dest_dir=None, force=False):
    """
    Install the Dual Airbrush Export extension to the Inkscape extensions directory.
    
    Args:
        source_dir: Directory containing the extension files
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
    
    # Copy INX and PY files
    source_dir = Path(source_dir)
    inx_file = source_dir / "dual_airbrush_export.inx"
    py_file = source_dir / "dual_airbrush_export.py"
    
    if not inx_file.exists() or not py_file.exists():
        print("Error: Could not find extension files. Make sure you're running this script from the correct directory.")
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
        hairbrush_src = source_dir.parent / "src" / "hairbrush"
        if not hairbrush_src.exists():
            print(f"Error: Could not find hairbrush package at {hairbrush_src}")
            return False
        
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
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    success = install_extension(script_dir, args.dest, args.force)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 
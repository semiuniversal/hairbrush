#!/usr/bin/env python3
"""
Installation helper script for the Hairbrush extension.
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
    Install the Hairbrush extension to the Inkscape extensions directory.
    
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
    
    # List of extension files to copy
    extension_files = [
        ("hairbrush_export.inx", "hairbrush_export.py"),
        ("hairbrush_export_effect.inx", "hairbrush_export_effect.py"),
        ("dual_airbrush_export.inx", "dual_airbrush_export.py"),
        ("check_extension.inx", "check_extension.py")
    ]
    
    # Copy all extension files
    source_dir = Path(source_dir)
    for inx_file, py_file in extension_files:
        inx_path = source_dir / inx_file
        py_path = source_dir / py_file
        
        if inx_path.exists() and py_path.exists():
            print(f"Copying {inx_path} to {dest_dir}")
            shutil.copy2(inx_path, dest_dir)
            
            print(f"Copying {py_path} to {dest_dir}")
            shutil.copy2(py_path, dest_dir)
        else:
            print(f"Warning: Could not find {inx_file} or {py_file}")
    
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
            # Try alternative location
            hairbrush_src = source_dir.parent.parent / "src" / "hairbrush"
            if not hairbrush_src.exists():
                print(f"Error: Could not find hairbrush package at {hairbrush_src}")
                return False
        
        print(f"Copying hairbrush package to {hairbrush_dest}")
        shutil.copytree(hairbrush_src, hairbrush_dest)
    
    # Create hairbrush_lib directory in extensions folder if it exists
    hairbrush_lib_src = source_dir / "hairbrush_lib"
    if hairbrush_lib_src.exists():
        hairbrush_lib_dest = dest_dir / "hairbrush_lib"
        if hairbrush_lib_dest.exists() and not force:
            print(f"Warning: {hairbrush_lib_dest} already exists. Use --force to overwrite.")
        else:
            if hairbrush_lib_dest.exists():
                print(f"Removing existing {hairbrush_lib_dest}")
                shutil.rmtree(hairbrush_lib_dest)
            
            print(f"Copying hairbrush_lib package to {hairbrush_lib_dest}")
            shutil.copytree(hairbrush_lib_src, hairbrush_lib_dest)
    
    print("\nInstallation complete!")
    print(f"Extension installed to: {dest_dir}")
    print("Please restart Inkscape to use the extension.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Install Hairbrush extension for Inkscape")
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
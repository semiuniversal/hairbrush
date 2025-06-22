#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H.Airbrush Extension Installer

This script installs the H.Airbrush Inkscape extension to the user's Inkscape extensions directory.
It also installs the required Python dependencies.
"""

import os
import sys
import shutil
import platform
import subprocess
import argparse
from pathlib import Path

def get_inkscape_extensions_dir():
    """
    Find the Inkscape extensions directory based on the platform
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows: Check common locations
        possible_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'inkscape', 'extensions'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Inkscape', 'share', 'inkscape', 'extensions'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Inkscape', 'share', 'inkscape', 'extensions'),
            os.path.join(os.environ.get('PROGRAMW6432', ''), 'Inkscape', 'share', 'inkscape', 'extensions'),
        ]
        
        for path in possible_paths:
            if os.path.isdir(path):
                return path
        
        # If not found, try to find using registry
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Inkscape") as key:
                inkscape_path = winreg.QueryValueEx(key, "InstallDir")[0]
                extensions_path = os.path.join(inkscape_path, 'share', 'inkscape', 'extensions')
                if os.path.isdir(extensions_path):
                    return extensions_path
        except:
            pass
    
    elif system == "Darwin":
        # macOS: Check common locations
        possible_paths = [
            os.path.expanduser('~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions'),
            '/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions',
        ]
        
        for path in possible_paths:
            if os.path.isdir(path):
                return path
    
    else:
        # Linux: Check common locations
        possible_paths = [
            os.path.expanduser('~/.config/inkscape/extensions'),
            '/usr/share/inkscape/extensions',
            '/usr/local/share/inkscape/extensions',
        ]
        
        for path in possible_paths:
            if os.path.isdir(path):
                return path
    
    # If we get here, we couldn't find the extensions directory
    return None

def find_inkscape_command():
    """Find the Inkscape command"""
    system = platform.system()
    
    if system == "Windows":
        # Try common locations
        possible_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Inkscape', 'bin', 'inkscape.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Inkscape', 'bin', 'inkscape.exe'),
            os.path.join(os.environ.get('PROGRAMW6432', ''), 'Inkscape', 'bin', 'inkscape.exe'),
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
        
        # Try to find using registry
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Inkscape") as key:
                inkscape_path = winreg.QueryValueEx(key, "InstallDir")[0]
                inkscape_exe = os.path.join(inkscape_path, 'bin', 'inkscape.exe')
                if os.path.isfile(inkscape_exe):
                    return inkscape_exe
        except:
            pass
    
    # For all platforms, try to find in PATH
    try:
        if system == "Windows":
            result = subprocess.run(['where', 'inkscape'], capture_output=True, text=True)
        else:
            result = subprocess.run(['which', 'inkscape'], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

def install_python_dependencies(source_dir):
    """
    Install required Python dependencies
    """
    requirements_file = os.path.join(source_dir, 'requirements.txt')
    
    if not os.path.isfile(requirements_file):
        print("Warning: requirements.txt not found, skipping dependency installation")
        return
    
    print("Installing Python dependencies...")
    
    # Try to install using pip
    try:
        # First try using the system's pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], check=True)
        print("Dependencies installed successfully using pip")
        return
    except Exception as e:
        print(f"Warning: Could not install dependencies using pip: {str(e)}")
    
    # If pip fails, try to install dependencies manually
    try:
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print("Attempting to install dependencies manually...")
        
        for req in requirements:
            print(f"Installing {req}...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', req], check=True)
                print(f"Installed {req}")
            except Exception as e:
                print(f"Warning: Could not install {req}: {str(e)}")
    except Exception as e:
        print(f"Warning: Could not install dependencies manually: {str(e)}")
        print("You may need to install the following dependencies manually:")
        print("  - lxml>=4.9.0")
        print("  - pyyaml>=6.0")
        print("  - numpy>=1.22.0")

def install_extension(source_dir, extensions_dir):
    """
    Install the extension files to the Inkscape extensions directory
    """
    if not os.path.isdir(extensions_dir):
        print(f"Creating extensions directory: {extensions_dir}")
        os.makedirs(extensions_dir, exist_ok=True)
    
    # Files to install
    files_to_install = [
        'hairbrush.inx',
        'hairbrush_control.py',
        'hairbrush.py',
        'hairbrush_export_effect.inx',
        'hairbrush_export_effect.py',
        'check_installation.inx',
        'check_installation.py',
        'README.md',
        'INSTALL.md',
        'requirements.txt'
    ]
    
    # Directories to install
    dirs_to_install = [
        'hairbrush_lib',
        'hairbrush_deps',
        'vendor'  # Include the vendor directory with bundled dependencies
    ]
    
    # Install files
    for filename in files_to_install:
        source_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(extensions_dir, filename)
        
        if os.path.isfile(source_file):
            print(f"Installing {filename}...")
            shutil.copy2(source_file, dest_file)
        else:
            print(f"Warning: {filename} not found in source directory")
    
    # Install directories
    for dirname in dirs_to_install:
        source_dir_path = os.path.join(source_dir, dirname)
        dest_dir_path = os.path.join(extensions_dir, dirname)
        
        if os.path.isdir(source_dir_path):
            print(f"Installing {dirname}...")
            
            # Remove existing directory if it exists
            if os.path.isdir(dest_dir_path):
                shutil.rmtree(dest_dir_path)
            
            # Copy directory
            shutil.copytree(source_dir_path, dest_dir_path)
        else:
            print(f"Warning: {dirname} directory not found in source directory")
    
    # Install gcode_backend directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gcode_backend_src = os.path.join(project_root, 'gcode_backend')
    gcode_backend_dst = os.path.join(extensions_dir, 'gcode_backend')
    
    if os.path.isdir(gcode_backend_src):
        print("Installing gcode_backend directory...")
        
        # Remove existing directory if it exists
        if os.path.isdir(gcode_backend_dst):
            shutil.rmtree(gcode_backend_dst)
        
        # Copy directory
        shutil.copytree(gcode_backend_src, gcode_backend_dst)
    else:
        print("Warning: gcode_backend directory not found in project root")
        
        # Create gcode_backend directory with default templates
        print("Creating default gcode_backend directory...")
        os.makedirs(gcode_backend_dst, exist_ok=True)
        
        # Create default command_templates.yaml
        default_template = {
            "brush_a": {
                "offset": [0, 0],
                "air_on": "M42 P0 S1",
                "air_off": "M42 P0 S0",
                "paint_on": "M280 P0 S90",
                "paint_off": "M280 P0 S0"
            },
            "brush_b": {
                "offset": [50, 50],
                "air_on": "M42 P1 S1",
                "air_off": "M42 P1 S0",
                "paint_on": "M280 P1 S90",
                "paint_off": "M280 P1 S0"
            }
        }
        
        import yaml
        with open(os.path.join(gcode_backend_dst, 'command_templates.yaml'), 'w') as f:
            yaml.dump(default_template, f, default_flow_style=False)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Install H.Airbrush Inkscape extension')
    parser.add_argument('--extensions-dir', help='Inkscape extensions directory')
    args = parser.parse_args()
    
    # Get the source directory (where this script is located)
    source_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Source directory: {source_dir}")
    
    # Get the Inkscape extensions directory
    extensions_dir = args.extensions_dir
    if not extensions_dir:
        extensions_dir = get_inkscape_extensions_dir()
    
    if not extensions_dir:
        print("Error: Could not find Inkscape extensions directory")
        print("Please specify the directory using --extensions-dir")
        return 1
    
    print(f"Inkscape extensions directory: {extensions_dir}")
    
    # Install the extension
    install_extension(source_dir, extensions_dir)
    
    print("\nInstallation complete!")
    print("Please restart Inkscape to use the H.Airbrush extension.")
    print("\nNote: All dependencies are bundled with the extension.")
    
    # Find Inkscape command
    inkscape_cmd = find_inkscape_command()
    if inkscape_cmd:
        print(f"\nYou can start Inkscape using: {inkscape_cmd}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 
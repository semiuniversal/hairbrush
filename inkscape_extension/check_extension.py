#!/usr/bin/env python3
"""
Check if Inkscape can find and load our extensions.
This script should be run from within Inkscape's Python environment.
"""

import os
import sys
import importlib
import subprocess

def check_extension():
    """Check if Inkscape can find and load our extensions."""
    print("Checking Inkscape extensions...")
    
    # Print Python version and path
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    # Check if we can import inkex
    try:
        import inkex
        print(f"inkex version: {inkex.__version__ if hasattr(inkex, '__version__') else 'unknown'}")
        print(f"inkex path: {inkex.__file__}")
    except ImportError:
        print("Error: Could not import inkex module")
        return False
    
    # Check Inkscape extensions directory
    try:
        # Try to find the Inkscape extensions directory
        extensions_dir = None
        for path in sys.path:
            if "inkscape" in path.lower() and "extensions" in path.lower():
                extensions_dir = path
                break
        
        if extensions_dir:
            print(f"Inkscape extensions directory: {extensions_dir}")
            
            # Check if our extension files exist
            extension_files = [
                "hairbrush_export.inx",
                "hairbrush_export.py",
                "hairbrush_export_effect.inx",
                "hairbrush_export_effect.py",
                "dual_airbrush_export.inx",
                "dual_airbrush_export.py"
            ]
            
            for file in extension_files:
                file_path = os.path.join(extensions_dir, file)
                if os.path.exists(file_path):
                    print(f"✓ Found {file}")
                else:
                    print(f"✗ Missing {file}")
            
            # Check if hairbrush package exists
            hairbrush_dir = os.path.join(extensions_dir, "hairbrush")
            if os.path.exists(hairbrush_dir) and os.path.isdir(hairbrush_dir):
                print(f"✓ Found hairbrush package at {hairbrush_dir}")
                # Check for key modules
                for module in ["svg_parser.py", "gcode_generator.py", "path_processor.py"]:
                    module_path = os.path.join(hairbrush_dir, module)
                    if os.path.exists(module_path):
                        print(f"  ✓ Found {module}")
                    else:
                        print(f"  ✗ Missing {module}")
            else:
                print(f"✗ Missing hairbrush package at {hairbrush_dir}")
            
            # Check if hairbrush_lib package exists
            hairbrush_lib_dir = os.path.join(extensions_dir, "hairbrush_lib")
            if os.path.exists(hairbrush_lib_dir) and os.path.isdir(hairbrush_lib_dir):
                print(f"✓ Found hairbrush_lib package at {hairbrush_lib_dir}")
                # Check for key modules
                for module in ["svg_parser.py", "gcode_generator.py", "path_processor.py"]:
                    module_path = os.path.join(hairbrush_lib_dir, module)
                    if os.path.exists(module_path):
                        print(f"  ✓ Found {module}")
                    else:
                        print(f"  ✗ Missing {module}")
            else:
                print(f"✗ Missing hairbrush_lib package at {hairbrush_lib_dir}")
        else:
            print("Could not find Inkscape extensions directory in sys.path")
    except Exception as e:
        print(f"Error checking extensions: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Try to import our modules
    print("\nTrying to import extension modules:")
    try:
        # Try to import hairbrush_export
        spec = importlib.util.find_spec("hairbrush_export")
        if spec:
            print(f"✓ Found hairbrush_export module at {spec.origin}")
        else:
            print("✗ Could not find hairbrush_export module")
        
        # Try to import dual_airbrush_export
        spec = importlib.util.find_spec("dual_airbrush_export")
        if spec:
            print(f"✓ Found dual_airbrush_export module at {spec.origin}")
        else:
            print("✗ Could not find dual_airbrush_export module")
        
        # Try to import hairbrush package
        try:
            import hairbrush
            print(f"✓ Successfully imported hairbrush package from {hairbrush.__file__}")
        except ImportError:
            print("✗ Could not import hairbrush package")
        
        # Try to import hairbrush_lib package
        try:
            import hairbrush_lib
            print(f"✓ Successfully imported hairbrush_lib package from {hairbrush_lib.__file__}")
        except ImportError:
            print("✗ Could not import hairbrush_lib package")
        
    except Exception as e:
        print(f"Error importing modules: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nExtension check complete!")
    return True

if __name__ == "__main__":
    check_extension() 
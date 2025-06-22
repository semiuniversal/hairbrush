#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H.Airbrush Extension - Installation Checker

This script checks if the H.Airbrush extension is properly installed and can be loaded by Inkscape.
It also verifies that the required Python dependencies are available.
"""

import os
import sys
import inkex
import importlib.util
import platform
import tempfile
import logging

# Setup logging
log_file = os.path.join(tempfile.gettempdir(), 'hairbrush_check.log')
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file)
logger = logging.getLogger('hairbrush_check')

class CheckInstallationEffect(inkex.Effect):
    """
    Check if the Hairbrush extension is properly installed.
    """
    
    def __init__(self):
        super(CheckInstallationEffect, self).__init__()
    
    def effect(self):
        """
        Run the installation check.
        """
        results = []
        
        # Check Python version
        python_version = sys.version
        results.append(f"Python version: {python_version}")
        
        # Check platform
        system_info = platform.system() + " " + platform.release()
        results.append(f"System: {system_info}")
        
        # Check Inkscape version
        try:
            inkscape_version = inkex.Version
            results.append(f"Inkscape module version: {inkscape_version}")
        except AttributeError:
            results.append("Inkscape module version: Unknown")
        
        # Check extension directory
        extension_dir = os.path.dirname(os.path.abspath(__file__))
        results.append(f"Extension directory: {extension_dir}")
        
        # Check for required files
        required_files = [
            "hairbrush.inx",
            "hairbrush.py",
            "hairbrush_export_effect.inx",
            "hairbrush_export_effect.py",
            os.path.join("hairbrush_lib", "__init__.py"),
            os.path.join("hairbrush_lib", "svg_parser.py"),
            os.path.join("hairbrush_lib", "path_processor.py"),
            os.path.join("hairbrush_lib", "gcode_generator.py"),
            os.path.join("hairbrush_lib", "config.py"),
            os.path.join("hairbrush_lib", "templates", "default.yaml"),
            os.path.join("vendor", "yaml", "__init__.py")  # Check for bundled PyYAML
        ]
        
        for file_path in required_files:
            full_path = os.path.join(extension_dir, file_path)
            if os.path.exists(full_path):
                results.append(f"✓ Found: {file_path}")
            else:
                results.append(f"✗ Missing: {file_path}")
        
        # Check for required dependencies
        results.append("\nChecking bundled dependencies:")
        
        # Check for PyYAML in vendor directory
        yaml_path = os.path.join(extension_dir, "vendor", "yaml")
        if os.path.exists(yaml_path) and os.path.isdir(yaml_path):
            results.append(f"✓ PyYAML is bundled in vendor directory")
        else:
            results.append(f"✗ PyYAML is NOT bundled in vendor directory")
        
        # Try to import hairbrush modules
        try:
            # Add the extensions directory to sys.path
            if extension_dir not in sys.path:
                sys.path.append(extension_dir)
            
            # Add vendor directory to sys.path
            vendor_dir = os.path.join(extension_dir, "vendor")
            if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
                sys.path.insert(0, vendor_dir)
            
            # Try to import the main module
            spec = importlib.util.find_spec("hairbrush")
            if spec:
                results.append("✓ hairbrush module can be imported")
            else:
                results.append("✗ hairbrush module cannot be imported")
            
            # Try to import the library
            spec = importlib.util.find_spec("hairbrush_lib")
            if spec:
                results.append("✓ hairbrush_lib package can be imported")
                
                # Try to import specific modules
                for module_name in ["svg_parser", "path_processor", "gcode_generator", "config"]:
                    try:
                        module = importlib.import_module(f"hairbrush_lib.{module_name}")
                        results.append(f"✓ hairbrush_lib.{module_name} can be imported")
                    except ImportError as e:
                        results.append(f"✗ hairbrush_lib.{module_name} cannot be imported: {str(e)}")
            else:
                results.append("✗ hairbrush_lib package cannot be imported")
        
        except Exception as e:
            results.append(f"Error checking imports: {str(e)}")
        
        # Display results
        self._show_results(results)
        
        # Log results
        for result in results:
            logger.info(result)
        
        logger.info(f"Log file: {log_file}")
    
    def _show_results(self, results):
        """
        Display the results to the user.
        """
        # Create a dialog with the results
        dialog_text = "H.Airbrush Extension Installation Check\n\n"
        dialog_text += "\n".join(results)
        dialog_text += f"\n\nDetailed log saved to: {log_file}"
        
        # Show the results
        inkex.utils.debug(dialog_text)

if __name__ == '__main__':
    CheckInstallationEffect().affect() 
#!/usr/bin/env python3
"""
Clear Flask cache files

This script removes any __pycache__ directories and .pyc files
to ensure Flask loads the latest versions of all files.
"""

import os
import shutil
import sys

def clear_cache(directory):
    """Clear all __pycache__ directories and .pyc files in the given directory."""
    print(f"Clearing cache in {directory}...")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            print(f"Removing {pycache_dir}")
            shutil.rmtree(pycache_dir)
    
    # Remove .pyc files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                print(f"Removing {pyc_file}")
                os.remove(pyc_file)
    
    print("Cache clearing complete!")

if __name__ == "__main__":
    # Get the directory to clear cache from
    directory = os.path.dirname(os.path.abspath(__file__))
    
    # If a directory is provided as an argument, use that instead
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    
    clear_cache(directory)
    print("\nTo run the application with no caching, use:")
    print("DEBUG=true TEMPLATES_AUTO_RELOAD=true PORT=5001 python app.py") 
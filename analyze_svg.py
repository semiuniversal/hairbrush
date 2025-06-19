#!/usr/bin/env python3
"""
Simple script to analyze an SVG file.
"""

import sys
import os
import json
from pathlib import Path

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

try:
    from hairbrush.svg_parser import SVGParser
except ImportError:
    print("Error: Could not import hairbrush.svg_parser.")
    print(f"Python path: {sys.path}")
    sys.exit(1)


def analyze_svg(svg_path):
    """Analyze an SVG file and print information about it."""
    try:
        parser = SVGParser(svg_path)
        
        # Get basic document info
        doc_info = parser.get_document_info()
        print("SVG Document Information:")
        print(f"  Width: {doc_info['width']}")
        print(f"  Height: {doc_info['height']}")
        print(f"  ViewBox: {doc_info['viewBox']}")
        print()
        
        # Get layers
        layers = parser.get_layers()
        print(f"Layers: {len(layers)}")
        for i, (layer, label) in enumerate(layers):
            print(f"  {i+1}. {label}")
        print()
        
        # Get paths
        all_paths = parser.get_all_paths()
        print(f"Total paths: {len(all_paths)}")
        
        # Analyze paths
        for i, path in enumerate(all_paths):
            if i >= 10:  # Limit to first 10 paths
                print(f"  ... and {len(all_paths) - 10} more paths")
                break
                
            path_id = path.get("id", "")
            path_data = parser.get_path_data(path)
            path_style = parser.get_path_style(path)
            
            print(f"  Path {i+1}" + (f" (id: {path_id})" if path_id else ""))
            
            # Show style information
            fill = path_style.get('fill', 'none')
            stroke = path_style.get('stroke', 'none')
            print(f"    Fill: {fill}, Stroke: {stroke}")
            
            # Show path bounds
            bounds = parser.get_path_bounds(path)
            min_x, min_y, max_x, max_y = bounds
            print(f"    Bounds: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})")
            print(f"    Size: {max_x - min_x:.1f} x {max_y - min_y:.1f}")
            
            # Show a snippet of the path data
            if path_data:
                preview = path_data[:50] + "..." if len(path_data) > 50 else path_data
                print(f"    Data: {preview}")
            
            print()
            
    except Exception as e:
        print(f"Error analyzing SVG: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <svg_file>")
        sys.exit(1)
        
    svg_path = sys.argv[1]
    if not os.path.exists(svg_path):
        print(f"Error: File '{svg_path}' not found.")
        sys.exit(1)
        
    analyze_svg(svg_path) 
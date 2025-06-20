#!/usr/bin/env python3
"""
Test script for the improved path processing.

This script tests the path processing improvements with the test SVG file.
"""

import sys
import os
import argparse

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, src_dir)

try:
    from hairbrush.svg_parser import SVGParser
    from hairbrush.path_processor import PathProcessor
except ImportError as e:
    print(f"Error importing hairbrush modules: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

def test_path_processing(svg_file, layer_name=None, curve_resolution=10):
    """
    Test path processing on the given SVG file.
    
    Args:
        svg_file: Path to the SVG file
        layer_name: Name of the layer to process (None for all paths)
        curve_resolution: Number of segments to use for curve approximation
    """
    try:
        # Parse the SVG file
        parser = SVGParser(svg_file)
        
        # Print document properties
        viewbox = parser.get_viewbox()
        width = parser.get_width()
        height = parser.get_height()
        
        print(f"SVG Document Properties:")
        print(f"  viewBox: {viewbox}")
        print(f"  width: {width}")
        print(f"  height: {height}")
        print()
        
        # Get layers
        layers = parser.get_layers()
        print(f"Layers in the SVG file:")
        for layer_id, layer_label in layers:
            print(f"  - {layer_label} (id: {layer_id})")
        print()
        
        # Get paths from the specified layer or all paths
        if layer_name:
            paths = parser.get_paths_by_layer(layer_name)
            if not paths:
                print(f"No paths found in layer '{layer_name}'")
                return
            print(f"Processing paths in layer '{layer_name}':")
        else:
            paths = parser.get_all_paths()
            if not paths:
                print("No paths found in the SVG file")
                return
            print(f"Processing all paths:")
        
        # Process each path
        for i, path in enumerate(paths):
            path_id = parser.get_path_id(path)
            path_data = parser.get_path_data(path)
            
            if not path_data:
                continue
                
            print(f"\nPath {i+1}/{len(paths)}" + (f" (id: {path_id})" if path_id else ""))
            print(f"  Path data: {path_data[:60]}..." if len(path_data) > 60 else path_data)
            
            # Parse path data to segments
            segments = PathProcessor.parse_path(path_data)
            print(f"  Segments: {len(segments)}")
            
            # Print segment types
            segment_types = {}
            for segment in segments:
                cmd_type = segment.command.name
                if cmd_type in segment_types:
                    segment_types[cmd_type] += 1
                else:
                    segment_types[cmd_type] = 1
            
            print(f"  Segment types: {segment_types}")
            
            # Convert segments to polyline with specified curve resolution
            polyline = PathProcessor.path_to_polyline(segments, curve_resolution)
            print(f"  Polyline points: {len(polyline)}")
            print(f"  First 3 points: {polyline[:3]}")
            print(f"  Last 3 points: {polyline[-3:]}")
            
            # Calculate bounding box
            min_x = min(p[0] for p in polyline)
            max_x = max(p[0] for p in polyline)
            min_y = min(p[1] for p in polyline)
            max_y = max(p[1] for p in polyline)
            
            print(f"  Bounding box: ({min_x:.2f}, {min_y:.2f}) - ({max_x:.2f}, {max_y:.2f})")
            print(f"  Width: {max_x - min_x:.2f}, Height: {max_y - min_y:.2f}")
            
    except Exception as e:
        print(f"Error processing SVG file: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Test path processing")
    parser.add_argument("svg_file", help="Path to the SVG file")
    parser.add_argument("--layer", help="Name of the layer to process (default: all layers)")
    parser.add_argument("--curve-resolution", type=int, default=10,
                        help="Number of segments for curve approximation (default: 10)")
    args = parser.parse_args()
    
    # Check if the SVG file exists
    if not os.path.exists(args.svg_file):
        print(f"Error: File '{args.svg_file}' not found.")
        sys.exit(1)
    
    # Test path processing
    test_path_processing(args.svg_file, args.layer, args.curve_resolution)

if __name__ == "__main__":
    main() 
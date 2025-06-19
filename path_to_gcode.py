#!/usr/bin/env python3
"""
Convert SVG paths to G-code for the dual-airbrush plotter.

This script extracts paths from an SVG file and converts them to G-code
using the hairbrush package.

Usage:
    python path_to_gcode.py <svg_file> [--layer <layer_name>] [--output <output_file>]
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

try:
    from hairbrush.svg_parser import SVGParser
    from hairbrush.gcode_generator import GCodeGenerator
    from hairbrush.path_processor import PathProcessor
except ImportError as e:
    print(f"Error importing hairbrush modules: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)


def convert_svg_to_gcode(svg_path, layer_name=None, simplify=False, tolerance=0.5, 
                        z_height=2.0, feedrate=1500, brush="brush_a"):
    """
    Convert SVG paths to G-code.
    
    Args:
        svg_path: Path to the SVG file
        layer_name: Name of the layer to process (None for all paths)
        simplify: Whether to simplify paths
        tolerance: Tolerance for path simplification
        z_height: Z height for the brush
        feedrate: Feedrate for movements
        brush: Brush identifier
        
    Returns:
        G-code as a string
    """
    try:
        # Parse the SVG file
        parser = SVGParser(svg_path)
        
        # Get paths from the specified layer or all paths
        if layer_name:
            paths = parser.get_paths_by_layer(layer_name)
            if not paths:
                print(f"Warning: No paths found in layer '{layer_name}'")
                print("Available layers:")
                for _, label in parser.get_layers():
                    print(f"  - {label}")
                return None
        else:
            paths = parser.get_all_paths()
            if not paths:
                print("Warning: No paths found in the SVG file")
                return None
        
        # Initialize G-code generator
        gcode_gen = GCodeGenerator()
        gcode_gen.add_header()
        
        # Add information about the source file
        gcode_gen.output_lines.extend([
            f"; SVG file: {os.path.basename(svg_path)}",
            f"; Layer: {layer_name if layer_name else 'All layers'}",
            f"; Paths: {len(paths)}",
            f"; Z height: {z_height}mm",
            f"; Feedrate: {feedrate}mm/min",
            f"; Simplification: {'Yes' if simplify else 'No'}",
            ""
        ])
        
        # Process each path
        for i, path in enumerate(paths):
            path_id = parser.get_path_id(path)
            path_data = parser.get_path_data(path)
            
            if not path_data:
                continue
                
            # Simplify path if requested
            if simplify:
                path_data = PathProcessor.simplify_path(path_data, tolerance)
            
            # Add comment for the path
            gcode_gen.output_lines.append(f"; Path {i+1}" + (f" (id: {path_id})" if path_id else ""))
            
            # Add the path to the G-code
            gcode_gen.add_path(path_data, brush, z_height, feedrate)
            
            # Add a separator
            gcode_gen.output_lines.append("")
        
        # Add footer
        gcode_gen.add_footer()
        
        # Return the G-code
        return gcode_gen.get_output()
        
    except Exception as e:
        print(f"Error converting SVG to G-code: {str(e)}")
        return None


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Convert SVG paths to G-code")
    parser.add_argument("svg_file", help="Path to the SVG file")
    parser.add_argument("--layer", help="Name of the layer to process (default: all layers)")
    parser.add_argument("--output", "-o", help="Output G-code file (default: <svg_name>.gcode)")
    parser.add_argument("--simplify", action="store_true", help="Simplify paths")
    parser.add_argument("--tolerance", type=float, default=0.5, 
                        help="Tolerance for path simplification (default: 0.5)")
    parser.add_argument("--z-height", type=float, default=2.0, 
                        help="Z height for the brush (default: 2.0)")
    parser.add_argument("--feedrate", type=int, default=1500, 
                        help="Feedrate for movements (default: 1500)")
    parser.add_argument("--brush", choices=["brush_a", "brush_b"], default="brush_a",
                        help="Brush to use (default: brush_a)")
    args = parser.parse_args()
    
    # Check if the SVG file exists
    if not os.path.exists(args.svg_file):
        print(f"Error: File '{args.svg_file}' not found.")
        sys.exit(1)
    
    # Generate G-code
    gcode = convert_svg_to_gcode(
        args.svg_file,
        args.layer,
        args.simplify,
        args.tolerance,
        args.z_height,
        args.feedrate,
        args.brush
    )
    
    if not gcode:
        print("Error: Failed to generate G-code.")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        svg_name = os.path.splitext(os.path.basename(args.svg_file))[0]
        output_file = f"{svg_name}.gcode"
    
    # Write G-code to file
    try:
        with open(output_file, "w") as f:
            f.write(gcode)
        print(f"G-code written to {output_file}")
    except Exception as e:
        print(f"Error writing G-code to file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
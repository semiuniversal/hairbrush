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
                        z_height=2.0, feedrate=1500, brush="brush_a", curve_resolution=10,
                        debug_markers=False, scale_factor=1.0, offset_x=0.0, offset_y=0.0):
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
        curve_resolution: Number of segments to use for curve approximation
        debug_markers: Whether to add debug markers to the G-code
        scale_factor: Additional scaling factor to apply
        offset_x: X offset to apply after all transformations
        offset_y: Y offset to apply after all transformations
        
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
        
        # Set SVG document properties
        viewbox = parser.get_viewbox()
        width = parser.get_width()
        height = parser.get_height()
        gcode_gen.set_svg_document_properties(viewbox, width, height)
        
        # Set user-defined transformations
        gcode_gen.set_user_transform(scale_factor, offset_x, offset_y)
        
        # Enable debug markers if requested
        if debug_markers:
            gcode_gen.enable_debug_markers(True)
        
        # Configure brush
        gcode_gen.configure_brush(brush, {
            "offset": (0, 0),  # Default offset
            "z_height": z_height
        })
        
        gcode_gen.add_header()
        
        # Add information about the source file
        gcode_gen.output_lines.extend([
            f"; SVG file: {os.path.basename(svg_path)}",
            f"; Layer: {layer_name if layer_name else 'All layers'}",
            f"; Paths: {len(paths)}",
            f"; Base Z height: {z_height}mm",
            f"; Base feedrate: {feedrate}mm/min",
            f"; Simplification: {'Yes' if simplify else 'No'}",
            f"; Curve resolution: {curve_resolution}",
            f"; Debug markers: {'Yes' if debug_markers else 'No'}",
            ""
        ])
        
        # Process each path
        total_paths = len(paths)
        for i, path in enumerate(paths):
            path_id = parser.get_path_id(path)
            path_data = parser.get_path_data(path)
            
            if not path_data:
                continue
                
            # Simplify path if requested
            if simplify:
                path_data = PathProcessor.simplify_path(path_data, tolerance)
            
            # Add comment for the path
            gcode_gen.output_lines.append(f"; Path {i+1}/{total_paths}" + (f" (id: {path_id})" if path_id else ""))
            
            # Extract stroke attributes
            path_style = parser.get_path_style(path)
            
            # Get stroke color
            stroke_color = path_style.get("stroke", "#000000")  # Default to black
            if stroke_color == "none":
                # If stroke is none, try to use fill color
                stroke_color = path_style.get("fill", "#000000")
                if stroke_color == "none":
                    stroke_color = "#000000"  # Default to black if no stroke or fill
            
            # Get stroke width
            stroke_width_str = path_style.get("stroke-width", "1")
            try:
                stroke_width = float(stroke_width_str)
            except ValueError:
                stroke_width = 1.0  # Default width
            
            # Get stroke opacity
            stroke_opacity_str = path_style.get("stroke-opacity", "1")
            try:
                stroke_opacity = float(stroke_opacity_str)
            except ValueError:
                stroke_opacity = 1.0  # Default opacity
                
            # If we're using fill instead of stroke, get fill opacity
            if stroke_color == path_style.get("fill", ""):
                fill_opacity_str = path_style.get("fill-opacity", "1")
                try:
                    fill_opacity = float(fill_opacity_str)
                    stroke_opacity = fill_opacity  # Use fill opacity
                except ValueError:
                    pass  # Keep stroke opacity
            
            # Parse path data to segments for validation
            try:
                # Add the path to the G-code using the improved path processor with stroke attributes
                gcode_gen.add_path_with_attributes(
                    path_data, 
                    stroke_color, 
                    stroke_width, 
                    stroke_opacity, 
                    feedrate
                )
                
                # Report progress for large files
                if total_paths > 10 and (i+1) % 5 == 0:
                    print(f"Processing path {i+1}/{total_paths} ({(i+1)/total_paths*100:.1f}%)")
                
            except Exception as e:
                print(f"Warning: Error processing path {i+1} (id: {path_id}): {str(e)}")
                print("Skipping this path and continuing...")
                continue
            
            # Add a separator
            gcode_gen.output_lines.append("")
        
        # Add footer
        gcode_gen.add_footer()
        
        # Return the G-code
        return gcode_gen.get_output()
        
    except Exception as e:
        print(f"Error converting SVG to G-code: {str(e)}")
        import traceback
        traceback.print_exc()
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
    parser.add_argument("--curve-resolution", type=int, default=10,
                        help="Number of segments for curve approximation (default: 10)")
    parser.add_argument("--debug-markers", action="store_true",
                        help="Add debug markers to the G-code")
    parser.add_argument("--scale-factor", type=float, default=1.0,
                        help="Additional scaling factor to apply")
    parser.add_argument("--offset-x", type=float, default=0.0,
                        help="X offset to apply after all transformations")
    parser.add_argument("--offset-y", type=float, default=0.0,
                        help="Y offset to apply after all transformations")
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
        args.brush,
        args.curve_resolution,
        args.debug_markers,
        args.scale_factor,
        args.offset_x,
        args.offset_y
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
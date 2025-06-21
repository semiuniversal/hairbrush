#!/usr/bin/env python3
"""
Test script for G-code generation.

This script generates G-code from the test SVG file and creates a simple
visualization of the G-code paths.
"""

import sys
import os
import argparse
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, src_dir)

try:
    from hairbrush.svg_parser import SVGParser
    from hairbrush.gcode_generator import GCodeGenerator
    from hairbrush.path_processor import PathProcessor
except ImportError as e:
    print(f"Error importing hairbrush modules: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

def parse_gcode_for_visualization(gcode):
    """
    Parse G-code to extract movement paths for visualization.
    
    Args:
        gcode: G-code string
        
    Returns:
        List of path segments, each containing a list of (x, y) points
    """
    paths = []
    current_path = []
    current_x, current_y = 0, 0
    
    for line in gcode.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith(';'):
            continue
        
        # Parse G0/G1 commands
        if line.startswith('G0 ') or line.startswith('G1 '):
            parts = line.split(' ')
            
            x = None
            y = None
            
            for part in parts:
                if part.startswith('X'):
                    try:
                        x = float(part[1:])
                    except ValueError:
                        pass
                elif part.startswith('Y'):
                    try:
                        y = float(part[1:])
                    except ValueError:
                        pass
            
            # Update position
            if x is not None:
                current_x = x
            if y is not None:
                current_y = y
                
            # If G0 (rapid move), start a new path
            if line.startswith('G0 '):
                if current_path:
                    paths.append(current_path)
                current_path = [(current_x, current_y)]
            else:
                # G1 (linear move), add to current path
                current_path.append((current_x, current_y))
    
    # Add the last path
    if current_path:
        paths.append(current_path)
    
    return paths

def visualize_gcode(gcode, output_file=None):
    """
    Visualize G-code paths.
    
    Args:
        gcode: G-code string
        output_file: Path to save the visualization image (None to display)
    """
    # Parse G-code for visualization
    paths = parse_gcode_for_visualization(gcode)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot each path
    for i, path in enumerate(paths):
        if len(path) > 1:
            x = [p[0] for p in path]
            y = [p[1] for p in path]
            ax.plot(x, y, 'b-', linewidth=0.5)
            
            # Mark start and end points
            ax.plot(path[0][0], path[0][1], 'go', markersize=3)  # Start point
            ax.plot(path[-1][0], path[-1][1], 'ro', markersize=3)  # End point
    
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add title
    ax.set_title('G-code Visualization')
    
    # Add labels
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    
    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_file}")
    else:
        plt.show()

def generate_and_visualize_gcode(svg_file, layer_name=None, curve_resolution=10, 
                                debug_markers=False, output_file=None, 
                                visualize=True, viz_output=None):
    """
    Generate G-code from SVG and visualize the result.
    
    Args:
        svg_file: Path to the SVG file
        layer_name: Name of the layer to process (None for all paths)
        curve_resolution: Number of segments to use for curve approximation
        debug_markers: Whether to add debug markers to the G-code
        output_file: Path to save the G-code (None to print to console)
        visualize: Whether to visualize the G-code
        viz_output: Path to save the visualization image (None to display)
    """
    try:
        # Parse the SVG file
        parser = SVGParser(svg_file)
        
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
        
        # Enable debug markers if requested
        if debug_markers:
            gcode_gen.enable_debug_markers(True)
        
        gcode_gen.add_header()
        
        # Add information about the source file
        gcode_gen.output_lines.extend([
            f"; SVG file: {os.path.basename(svg_file)}",
            f"; Layer: {layer_name if layer_name else 'All layers'}",
            f"; Paths: {len(paths)}",
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
                
            # Add comment for the path
            gcode_gen.output_lines.append(f"; Path {i+1}/{total_paths}" + (f" (id: {path_id})" if path_id else ""))
            
            # Parse path data to segments for validation
            try:
                segments = PathProcessor.parse_path(path_data)
                
                # Convert segments to polyline with specified curve resolution
                polyline = PathProcessor.path_to_polyline(segments, curve_resolution)
                
                # Add the path to the G-code
                gcode_gen.add_path(path_data, "brush_a", 2.0, 1500)
                
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
        
        # Get the G-code
        gcode = gcode_gen.get_output()
        
        # Output the G-code
        if output_file:
            with open(output_file, 'w') as f:
                f.write(gcode)
            print(f"G-code written to {output_file}")
        else:
            print("\nG-code output:")
            print("=" * 40)
            print(gcode[:500] + "..." if len(gcode) > 500 else gcode)
            print("=" * 40)
        
        # Visualize the G-code if requested
        if visualize:
            visualize_gcode(gcode, viz_output)
        
        return gcode
        
    except Exception as e:
        print(f"Error generating G-code: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Test G-code generation")
    parser.add_argument("svg_file", help="Path to the SVG file")
    parser.add_argument("--layer", help="Name of the layer to process (default: all layers)")
    parser.add_argument("--curve-resolution", type=int, default=10,
                        help="Number of segments for curve approximation (default: 10)")
    parser.add_argument("--debug-markers", action="store_true",
                        help="Add debug markers to the G-code")
    parser.add_argument("--output", "-o", help="Output G-code file (default: print to console)")
    parser.add_argument("--no-visualize", action="store_true",
                        help="Skip G-code visualization")
    parser.add_argument("--viz-output", help="Output visualization image file (default: display)")
    args = parser.parse_args()
    
    # Check if the SVG file exists
    if not os.path.exists(args.svg_file):
        print(f"Error: File '{args.svg_file}' not found.")
        sys.exit(1)
    
    # Generate and visualize G-code
    generate_and_visualize_gcode(
        args.svg_file,
        args.layer,
        args.curve_resolution,
        args.debug_markers,
        args.output,
        not args.no_visualize,
        args.viz_output
    )

if __name__ == "__main__":
    main() 
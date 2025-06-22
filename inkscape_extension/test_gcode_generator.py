#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the GCodeGenerator class.
This script doesn't require Inkscape or the inkex module.
"""

import os
import sys
import logging
import tempfile

# Setup logging
log_file = os.path.join(tempfile.gettempdir(), 'hairbrush_test.log')
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file)
logger = logging.getLogger('test_gcode_generator')

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
try:
    from hairbrush_lib.gcode_generator import GCodeGenerator
    from hairbrush_lib.path_processor import PathProcessor
    logger.info("Successfully imported hairbrush_lib modules")
except ImportError as e:
    logger.error(f"Failed to import hairbrush_lib modules: {e}")
    sys.stderr.write(f"Error: Could not import hairbrush_lib modules: {e}\n")
    sys.exit(1)

def test_gcode_generation():
    """Test the GCodeGenerator class with some sample paths."""
    try:
        # Create a GCodeGenerator instance
        gcode_gen = GCodeGenerator()
        
        # Configure Z behavior
        gcode_gen.configure_z_behavior(min_height=1.0, max_height=15.0, travel_height=10.0, spray_cone_angle=15.0)
        
        # Configure the brushes
        gcode_gen.configure_brush("brush_a", {"offset": (0, 0)})
        gcode_gen.configure_brush("brush_b", {"offset": (0, 0)})
        
        # Set SVG document properties
        gcode_gen.set_svg_document_properties(viewbox=(0, 0, 100, 100), width=100, height=100)
        
        # Enable debug markers
        gcode_gen.enable_debug_markers(True)
        
        # Add header information
        gcode_gen.output_lines.extend([
            "; Test G-code generation",
            "; Simple shapes",
            ""
        ])
        
        # Sample paths
        paths = [
            # Square (black)
            {
                "d": "M 10,10 L 30,10 L 30,30 L 10,30 Z",
                "stroke": "#000000",
                "stroke-width": 1.0,
                "stroke-opacity": 1.0,
                "id": "square1"
            },
            # Circle (black)
            {
                "d": "M 60,20 C 65.52,20 70,24.48 70,30 C 70,35.52 65.52,40 60,40 C 54.48,40 50,35.52 50,30 C 50,24.48 54.48,20 60,20 Z",
                "stroke": "#000000",
                "stroke-width": 1.5,
                "stroke-opacity": 0.8,
                "id": "circle1"
            },
            # Square (white)
            {
                "d": "M 10,50 L 30,50 L 30,70 L 10,70 Z",
                "stroke": "#ffffff",
                "stroke-width": 2.0,
                "stroke-opacity": 0.7,
                "id": "square2"
            },
            # Circle (white)
            {
                "d": "M 60,60 C 65.52,60 70,64.48 70,70 C 70,75.52 65.52,80 60,80 C 54.48,80 50,75.52 50,70 C 50,64.48 54.48,60 60,60 Z",
                "stroke": "#ffffff",
                "stroke-width": 2.5,
                "stroke-opacity": 0.9,
                "id": "circle2"
            },
            # Wavy path (black)
            {
                "d": "M 20,80 C 30,90 40,70 50,80 C 60,90 70,70 80,80",
                "stroke": "#000000",
                "stroke-width": 1.0,
                "stroke-opacity": 1.0,
                "id": "path1"
            }
        ]
        
        # Process each path
        for i, path in enumerate(paths):
            # Extract path attributes
            path_data = path["d"]
            stroke_color = path["stroke"]
            stroke_width = float(path["stroke-width"])
            stroke_opacity = float(path["stroke-opacity"])
            path_id = path["id"]
            
            # Add comment for the path
            gcode_gen.output_lines.append(f"; Path {i+1}/{len(paths)} (id: {path_id})")
            
            # Add the path to the G-code generator
            gcode_gen.add_path_with_attributes(
                path_data, 
                stroke_color, 
                stroke_width, 
                stroke_opacity, 
                base_feedrate=100,  # Slow for testing
                curve_resolution=20
            )
        
        # Generate the G-code
        gcode = gcode_gen.generate_gcode(include_test_pattern=False)
        
        # Save the G-code to a file
        output_file = os.path.abspath("../assets/test/test_output.gcode")
        with open(output_file, "w") as f:
            f.write(gcode)
        
        print(f"G-code generated and saved to {output_file}")
        
        # Print the first 10 lines of the G-code
        print("\nFirst 10 lines of G-code:")
        for i, line in enumerate(gcode.split("\n")[:10]):
            print(f"{i+1}: {line}")
        
        return True
    except Exception as e:
        logger.error(f"Error in test_gcode_generation: {e}", exc_info=True)
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing G-code generation...")
    success = test_gcode_generation()
    print(f"Test {'succeeded' if success else 'failed'}")
    sys.exit(0 if success else 1) 
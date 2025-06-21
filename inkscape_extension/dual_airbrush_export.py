#!/usr/bin/env python3
# Dual Airbrush Export - Inkscape extension for exporting SVG layers to G-code
# for a dual-airbrush plotter with a Duet 2 WiFi board
#
# Copyright (C) 2024 Your Name
# Released under MIT License

import os
import sys
import logging
from lxml import etree

# Set up logging
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the hairbrush package
# when installed as an Inkscape extension
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import inkex - this will work when run from within Inkscape
try:
    import inkex
except ImportError:
    sys.stderr.write("Error: This extension requires the inkex module from Inkscape.\n")
    sys.stderr.write("This extension is meant to be run from within Inkscape.\n")
    sys.exit(1)

# Try to import from hairbrush_lib first (extension directory)
try:
    from hairbrush_lib.svg_parser import SVGParser
    from hairbrush_lib.gcode_generator import GCodeGenerator
    from hairbrush_lib.path_processor import PathProcessor
except ImportError:
    # If that fails, try to import from hairbrush package (installed in extensions dir)
    try:
        from hairbrush.svg_parser import SVGParser
        from hairbrush.gcode_generator import GCodeGenerator
        from hairbrush.path_processor import PathProcessor
    except ImportError:
        inkex.utils.debug("Error: Could not import hairbrush modules. Make sure they're installed correctly.")
        sys.exit(1)

class DualAirbrushExport(inkex.EffectExtension):
    """
    Inkscape extension for exporting SVG layers to G-code for a dual-airbrush plotter.
    """
    
    def add_arguments(self, pars):
        # Layers tab
        pars.add_argument("--tab", type=str, default="layers")
        pars.add_argument("--black_layer", type=str, default="black")
        pars.add_argument("--white_layer", type=str, default="white")
        pars.add_argument("--process_order", type=str, default="black_first")
        
        # Machine Settings tab
        pars.add_argument("--z_height", type=float, default=2.0)
        pars.add_argument("--feedrate", type=int, default=1500)
        pars.add_argument("--travel_feedrate", type=int, default=3000)
        pars.add_argument("--brush_offset_x", type=float, default=50.0)
        pars.add_argument("--brush_offset_y", type=float, default=0.0)
        
        # Output tab
        pars.add_argument("--output_path", type=str, default="dual_airbrush_output.gcode")
        pars.add_argument("--add_comments", type=inkex.Boolean, default=True)
        pars.add_argument("--preview_gcode", type=inkex.Boolean, default=False)

    def effect(self):
        """
        Main entry point for the extension.
        """
        # Create a temporary SVG file to process
        tmp_svg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp_output.svg")
        self.document.write(tmp_svg)
        
        try:
            # Parse the SVG using our parser
            parser = SVGParser(tmp_svg)
            
            # Initialize G-code generator
            gcode_gen = GCodeGenerator()
            gcode_gen.add_header()
            
            # Add custom configuration information
            if self.options.add_comments:
                gcode_gen.output_lines.append("; Dual Airbrush Export Configuration:")
                gcode_gen.output_lines.append(f"; Black Layer: {self.options.black_layer}")
                gcode_gen.output_lines.append(f"; White Layer: {self.options.white_layer}")
                gcode_gen.output_lines.append(f"; Z Height: {self.options.z_height}mm")
                gcode_gen.output_lines.append(f"; Feedrate: {self.options.feedrate}mm/min")
                gcode_gen.output_lines.append(f"; Travel Feedrate: {self.options.travel_feedrate}mm/min")
                gcode_gen.output_lines.append(f"; Brush Offset: X={self.options.brush_offset_x}mm, Y={self.options.brush_offset_y}mm")
                gcode_gen.output_lines.append(";")
            
            # Configure brush offsets
            brush_config = {
                "brush_a": {
                    "offset": [0, 0],
                },
                "brush_b": {
                    "offset": [self.options.brush_offset_x, self.options.brush_offset_y],
                }
            }
            
            # Process layers based on selected order
            layers_to_process = []
            if self.options.process_order == "black_first":
                layers_to_process = [
                    (self.options.black_layer, "brush_a"),
                    (self.options.white_layer, "brush_b")
                ]
            else:
                layers_to_process = [
                    (self.options.white_layer, "brush_b"),
                    (self.options.black_layer, "brush_a")
                ]
            
            # Process each layer
            for layer_name, brush_id in layers_to_process:
                paths = parser.get_paths_by_layer(layer_name)
                if paths:
                    if self.options.add_comments:
                        gcode_gen.output_lines.append(f"; Processing {layer_name} layer with {brush_id}")
                    
                    for path in paths:
                        path_data = parser.get_path_data(path)
                        if path_data:
                            gcode_gen.add_path(
                                path_data, 
                                brush_id, 
                                self.options.z_height, 
                                self.options.feedrate
                            )
                elif self.options.add_comments:
                    gcode_gen.output_lines.append(f"; No paths found in {layer_name} layer")
            
            # Add footer and save to file
            gcode_gen.add_footer()
            
            # Get absolute path for output if not already absolute
            output_path = self.options.output_path
            if not os.path.isabs(output_path):
                # Try to save relative to the input file location
                svg_dir = os.path.dirname(self.options.input_file) if hasattr(self.options, 'input_file') and self.options.input_file else os.getcwd()
                output_path = os.path.join(svg_dir, output_path)
            
            gcode_gen.save_to_file(output_path)
            
            # Show success message
            success_msg = f"G-code saved to {output_path}"
            inkex.utils.debug(success_msg)
            
            # Preview G-code if requested
            if self.options.preview_gcode:
                try:
                    with open(output_path, 'r') as f:
                        preview_content = f.read()
                    inkex.utils.debug("\nG-code Preview (first 20 lines):\n" + "\n".join(preview_content.split("\n")[:20]))
                except Exception as e:
                    inkex.utils.debug(f"Could not preview G-code: {str(e)}")
            
        except Exception as e:
            inkex.utils.debug(f"Error processing SVG: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_svg):
                os.remove(tmp_svg)

if __name__ == '__main__':
    DualAirbrushExport().run()

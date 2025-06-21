#!/usr/bin/env python3
"""
Hairbrush G-code Export - Inkscape Effect Extension

This extension exports SVG paths to G-code for a dual-airbrush plotter.
"""

import sys
import os
import inkex
from inkex import PathElement
import tempfile
import re
import math
import xml.etree.ElementTree as ET

# Add the parent directory to the path to find the hairbrush package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from hairbrush.svg_parser import SVGParser
    from hairbrush.gcode_generator import GCodeGenerator
    from hairbrush.path_processor import PathProcessor
except ImportError:
    inkex.utils.debug("Error importing hairbrush modules. Using bundled modules.")
    # If import fails, try to use bundled modules
    try:
        from . import svg_parser_bundled as SVGParser
        from . import gcode_generator_bundled as GCodeGenerator
        from . import path_processor_bundled as PathProcessor
    except ImportError:
        inkex.utils.debug("Error importing bundled modules.")
        sys.exit(1)


class HairbrushGcodeExportEffect(inkex.EffectExtension):
    """Inkscape effect extension for exporting SVG paths to G-code for dual-airbrush plotter."""
    
    def add_arguments(self, pars):
        """Add command line arguments."""
        # Options tab
        pars.add_argument("--tab", type=str, dest="tab", default="options")
        pars.add_argument("--brush", type=str, dest="brush", default="brush_a")
        pars.add_argument("--z_height", type=float, dest="z_height", default=2.0)
        pars.add_argument("--feedrate", type=int, dest="feedrate", default=1500)
        pars.add_argument("--curve_resolution", type=int, dest="curve_resolution", default=20)
        pars.add_argument("--simplify", type=inkex.Boolean, dest="simplify", default=False)
        pars.add_argument("--tolerance", type=float, dest="tolerance", default=0.5)
        pars.add_argument("--debug_markers", type=inkex.Boolean, dest="debug_markers", default=False)
        pars.add_argument("--output_path", type=str, dest="output_path", default="")
        
        # Transform tab
        pars.add_argument("--scale_factor", type=float, dest="scale_factor", default=1.0)
        pars.add_argument("--offset_x", type=float, dest="offset_x", default=0.0)
        pars.add_argument("--offset_y", type=float, dest="offset_y", default=0.0)
    
    def effect(self):
        """Generate G-code and save it to the specified file."""
        try:
            # Get the current SVG file path
            svg_file = self.document_path()
            inkex.utils.debug(f"Current SVG file: {svg_file}")
            
            # Determine output path based on SVG file
            output_path = self.options.output_path
            if not output_path:
                if svg_file and svg_file != 'memory':
                    # Use the same directory and base name as the SVG file
                    svg_dir = os.path.dirname(svg_file)
                    svg_name = os.path.splitext(os.path.basename(svg_file))[0]
                    output_path = os.path.join(svg_dir, f"{svg_name}.gcode")
                else:
                    # Fallback if no SVG file is available
                    output_path = os.path.expanduser("~/Desktop/output.gcode")
            
            # Get the absolute path
            output_path = os.path.abspath(os.path.expanduser(output_path))
            
            # Debug: Show the path
            inkex.utils.debug(f"Attempting to save to: {output_path}")
            
            # Create a temporary SVG file
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_file:
                tmp_svg = tmp_file.name
            
            # Save the current document to the temporary file
            self.document.write(tmp_svg)
            
            try:
                # Process the SVG and generate G-code
                gcode = self.process_svg_to_gcode(tmp_svg)
                
                # Ensure output directory exists
                output_dir = os.path.dirname(output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                # Save to file
                with open(output_path, 'w') as f:
                    f.write(gcode)
                
                # Verify file was created
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    inkex.utils.debug(f"File successfully saved: {output_path} (Size: {file_size} bytes)")
                    self.msg(f"G-code exported to: {output_path}")
                else:
                    inkex.utils.debug(f"File was not created: {output_path}")
                    self.msg(f"Failed to create file: {output_path}")
                
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(tmp_svg)
                except:
                    pass
            
        except Exception as e:
            inkex.utils.debug(f"Error exporting G-code: {str(e)}")
            import traceback
            inkex.utils.debug(traceback.format_exc())
            self.msg(f"Error: {str(e)}")
    
    def process_svg_to_gcode(self, svg_file):
        """Process SVG file and generate G-code."""
        try:
            # Parse the SVG file
            parser = SVGParser(svg_file)
            
            # Get all paths
            paths = parser.get_all_paths()
            if not paths:
                inkex.utils.debug("Warning: No paths found in the SVG file")
                return "; No paths found in the SVG file"
            
            # Initialize G-code generator
            gcode_gen = GCodeGenerator()
            
            # Set SVG document properties
            viewbox = parser.get_viewbox()
            width = parser.get_width()
            height = parser.get_height()
            gcode_gen.set_svg_document_properties(viewbox, width, height)
            
            # Set user-defined transformations
            gcode_gen.set_user_transform(
                self.options.scale_factor,
                self.options.offset_x,
                self.options.offset_y
            )
            
            # Enable debug markers if requested
            if self.options.debug_markers:
                gcode_gen.enable_debug_markers(True)
            
            # Configure brush
            gcode_gen.configure_brush(self.options.brush, {
                "offset": (0, 0),  # Default offset
                "z_height": self.options.z_height
            })
            
            gcode_gen.add_header()
            
            # Add information about the source file
            svg_name = os.path.basename(svg_file)
            gcode_gen.output_lines.extend([
                f"; Source SVG: {svg_name}",
                f"; Paths: {len(paths)}",
                f"; Base Z height: {self.options.z_height}mm",
                f"; Base feedrate: {self.options.feedrate}mm/min",
                f"; Simplification: {'Yes' if self.options.simplify else 'No'}",
                f"; Curve resolution: {self.options.curve_resolution}",
                f"; Debug markers: {'Yes' if self.options.debug_markers else 'No'}",
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
                if self.options.simplify:
                    path_data = PathProcessor.simplify_path(path_data, self.options.tolerance)
                
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
                
                try:
                    # Add the path to the G-code using the improved path processor with stroke attributes
                    gcode_gen.add_path_with_attributes(
                        path_data, 
                        stroke_color, 
                        stroke_width, 
                        stroke_opacity, 
                        self.options.feedrate
                    )
                    
                except Exception as e:
                    inkex.utils.debug(f"Warning: Error processing path {i+1} (id: {path_id}): {str(e)}")
                    continue
                
                # Add a separator
                gcode_gen.output_lines.append("")
            
            # Add footer
            gcode_gen.add_footer()
            
            # Return the G-code
            return gcode_gen.get_output()
            
        except Exception as e:
            inkex.utils.debug(f"Error in process_svg_to_gcode: {str(e)}")
            import traceback
            inkex.utils.debug(traceback.format_exc())
            return f"; Error processing SVG: {str(e)}"


if __name__ == '__main__':
    HairbrushGcodeExportEffect().run() 
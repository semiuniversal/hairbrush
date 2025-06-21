#!/usr/bin/env python3
"""
Hairbrush G-code Export - Inkscape Extension

This extension exports SVG paths to G-code for a dual-airbrush plotter.
It uses bundled modules for path processing and G-code generation.
"""

import sys
import os
import inkex
from inkex import PathElement
from inkex.command import inkscape
import tempfile
import re
import math
import xml.etree.ElementTree as ET

# Add the parent directory to the path so we can import the hairbrush package
# when installed as an Inkscape extension
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


class HairbrushGcodeExport(inkex.OutputExtension):
    """Inkscape extension for exporting SVG paths to G-code for dual-airbrush plotter."""
    
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
        
        # Transform tab
        pars.add_argument("--scale_factor", type=float, dest="scale_factor", default=1.0)
        pars.add_argument("--offset_x", type=float, dest="offset_x", default=0.0)
        pars.add_argument("--offset_y", type=float, dest="offset_y", default=0.0)
    
    def save(self, stream):
        """Save the G-code to the output stream."""
        # Create a temporary SVG file
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_file:
            tmp_svg = tmp_file.name
        
        # Save the current document to the temporary file
        self.document.write(tmp_svg)
        
        try:
            # Parse the SVG file
            parser = SVGParser(tmp_svg)
            
            # Get all paths
            paths = parser.get_all_paths()
            if not paths:
                inkex.utils.debug("Warning: No paths found in the SVG file")
                return
            
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
            gcode_gen.output_lines.extend([
                f"; SVG file: {os.path.basename(self.options.input_file)}",
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
            
            # Write G-code to output stream
            stream.write(gcode_gen.get_output().encode('utf-8'))
            
        except Exception as e:
            inkex.utils.debug(f"Error converting SVG to G-code: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up the temporary file
            try:
                os.unlink(tmp_svg)
            except:
                pass


if __name__ == '__main__':
    HairbrushGcodeExport().run() 
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
    # Try to import from local hairbrush_lib first
    from hairbrush_lib.svg_parser import SVGParser
    from hairbrush_lib.gcode_generator import GCodeGenerator
    from hairbrush_lib.path_processor import PathProcessor
    inkex.utils.debug("Successfully imported local hairbrush_lib modules")
except ImportError:
    inkex.utils.debug("Error importing local modules. Trying package imports.")
    try:
        from hairbrush.svg_parser import SVGParser
        from hairbrush.gcode_generator import GCodeGenerator
        from hairbrush.path_processor import PathProcessor
        inkex.utils.debug("Successfully imported hairbrush package modules")
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
            # Debug the SVG file path
            inkex.utils.debug(f"SVG file path: {svg_file}")
            
            # Initialize G-code generator
            gcode_gen = GCodeGenerator()
            
            # Instead of using our SVGParser, let's use inkex directly to get paths
            inkex.utils.debug("Using inkex to extract paths directly from the document")
            
            # If we're working with a temporary file, load the document from it
            if os.path.exists(svg_file):
                doc = inkex.load_svg(svg_file)
                root = doc.getroot()
            else:
                # We're already working with the document from Inkscape
                doc = self.document
                root = doc.getroot()
            
            # Extract paths using inkex
            paths = []
            for element in doc.xpath('//svg:path', namespaces=inkex.NSS):
                paths.append(element)
            
            # Also get other shape elements that can be converted to paths
            for element in doc.xpath('//svg:rect', namespaces=inkex.NSS):
                paths.append(element)
            
            for element in doc.xpath('//svg:circle', namespaces=inkex.NSS):
                paths.append(element)
                
            for element in doc.xpath('//svg:ellipse', namespaces=inkex.NSS):
                paths.append(element)
                
            for element in doc.xpath('//svg:line', namespaces=inkex.NSS):
                paths.append(element)
            
            inkex.utils.debug(f"Found {len(paths)} path elements")
            
            if not paths:
                inkex.utils.debug("Warning: No paths found in the SVG file")
                return "; No paths found in the SVG file"
            
            # Get document dimensions
            svg = doc.getroot()
            width_str = svg.get('width', '100')
            height_str = svg.get('height', '100')
            
            # Parse dimensions
            width = self._parse_dimension(width_str)
            height = self._parse_dimension(height_str)
            
            # Get viewBox
            viewbox_str = svg.get('viewBox')
            viewbox = None
            if viewbox_str:
                try:
                    vb_parts = viewbox_str.strip().split()
                    if len(vb_parts) == 4:
                        viewbox = (float(vb_parts[0]), float(vb_parts[1]), 
                                  float(vb_parts[2]), float(vb_parts[3]))
                except Exception as e:
                    inkex.utils.debug(f"Error parsing viewBox: {str(e)}")
            
            inkex.utils.debug(f"Document dimensions - Width: {width}, Height: {height}, ViewBox: {viewbox}")
            
            # Set document properties in G-code generator
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
            svg_name = os.path.basename(svg_file) if isinstance(svg_file, str) else "document"
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
            for i, element in enumerate(paths):
                # Get the path data
                if element.tag.endswith('path'):
                    path_data = element.get('d')
                else:
                    # Convert other shapes to path data
                    path_data = self._shape_to_path_data(element)
                
                if not path_data:
                    continue
                
                # Get element ID
                path_id = element.get('id', f"path_{i}")
                
                # Simplify path if requested
                if self.options.simplify:
                    # Instead of using PathProcessor.simplify_path, we'll just use the path as is
                    # A proper implementation would simplify the path here
                    inkex.utils.debug(f"Path simplification requested but not implemented")
                
                # Add comment for the path
                gcode_gen.output_lines.append(f"; Path {i+1}/{total_paths}" + (f" (id: {path_id})" if path_id else ""))
                
                # Extract style attributes
                style_str = element.get('style', '')
                style_dict = self._parse_style(style_str)
                
                # Get stroke color
                stroke_color = style_dict.get("stroke", element.get('stroke', "#000000"))
                if stroke_color == "none":
                    # If stroke is none, try to use fill color
                    stroke_color = style_dict.get("fill", element.get('fill', "#000000"))
                    if stroke_color == "none":
                        stroke_color = "#000000"  # Default to black if no stroke or fill
                
                # Get stroke width
                stroke_width_str = style_dict.get("stroke-width", element.get('stroke-width', "1"))
                try:
                    stroke_width = float(stroke_width_str)
                except ValueError:
                    stroke_width = 1.0  # Default width
                
                # Get stroke opacity
                stroke_opacity_str = style_dict.get("stroke-opacity", element.get('stroke-opacity', "1"))
                try:
                    stroke_opacity = float(stroke_opacity_str)
                except ValueError:
                    stroke_opacity = 1.0  # Default opacity
                
                try:
                    # Add the path to the G-code using path data directly
                    gcode_gen.add_path_with_attributes(
                        path_data, 
                        stroke_color, 
                        stroke_width, 
                        stroke_opacity, 
                        self.options.feedrate,
                        self.options.curve_resolution
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
    
    def _parse_style(self, style_str):
        """Parse an SVG style string into a dictionary"""
        style_dict = {}
        if not style_str:
            return style_dict
            
        # Split the style string by semicolons and process each property
        for item in style_str.split(';'):
            if ':' in item:
                key, value = item.split(':', 1)
                style_dict[key.strip()] = value.strip()
                
        return style_dict
    
    def _parse_dimension(self, value):
        """Parse an SVG dimension value, removing units"""
        if not value:
            return 0
            
        # Remove units (px, mm, cm, etc.)
        value = str(value)
        value = re.sub(r'[a-zA-Z%]+$', '', value)
        try:
            return float(value)
        except ValueError:
            return 0
    
    def _shape_to_path_data(self, element):
        """Convert SVG shape elements to path data"""
        tag = element.tag.split('}')[-1]  # Get tag name without namespace
        
        if tag == 'rect':
            # Get rectangle attributes
            x = float(element.get('x', 0))
            y = float(element.get('y', 0))
            width = float(element.get('width', 0))
            height = float(element.get('height', 0))
            
            # Create path data for rectangle
            return f"M {x},{y} h {width} v {height} h {-width} Z"
            
        elif tag == 'circle':
            # Get circle attributes
            cx = float(element.get('cx', 0))
            cy = float(element.get('cy', 0))
            r = float(element.get('r', 0))
            
            # Create path data for circle (approximation with cubic bezier curves)
            c = 0.551915024494 * r  # Magic number for circular bezier approximation
            return f"M {cx-r},{cy} C {cx-r},{cy-c} {cx-c},{cy-r} {cx},{cy-r} C {cx+c},{cy-r} {cx+r},{cy-c} {cx+r},{cy} C {cx+r},{cy+c} {cx+c},{cy+r} {cx},{cy+r} C {cx-c},{cy+r} {cx-r},{cy+c} {cx-r},{cy} Z"
            
        elif tag == 'ellipse':
            # Get ellipse attributes
            cx = float(element.get('cx', 0))
            cy = float(element.get('cy', 0))
            rx = float(element.get('rx', 0))
            ry = float(element.get('ry', 0))
            
            # Create path data for ellipse (approximation with cubic bezier curves)
            c_x = 0.551915024494 * rx
            c_y = 0.551915024494 * ry
            return f"M {cx-rx},{cy} C {cx-rx},{cy-c_y} {cx-c_x},{cy-ry} {cx},{cy-ry} C {cx+c_x},{cy-ry} {cx+rx},{cy-c_y} {cx+rx},{cy} C {cx+rx},{cy+c_y} {cx+c_x},{cy+ry} {cx},{cy+ry} C {cx-c_x},{cy+ry} {cx-rx},{cy+c_y} {cx-rx},{cy} Z"
            
        elif tag == 'line':
            # Get line attributes
            x1 = float(element.get('x1', 0))
            y1 = float(element.get('y1', 0))
            x2 = float(element.get('x2', 0))
            y2 = float(element.get('y2', 0))
            
            # Create path data for line
            return f"M {x1},{y1} L {x2},{y2}"
            
        return None


if __name__ == '__main__':
    HairbrushGcodeExportEffect().run() 
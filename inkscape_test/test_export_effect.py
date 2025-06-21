#!/usr/bin/env python
"""
Test G-code Export - Effect extension

This is a simplified effect extension for testing Inkscape extension functionality.
It appears in the Extensions > Export menu.
"""

import sys
import os
import inkex

class TestGcodeExportEffect(inkex.EffectExtension):
    """Effect extension for exporting G-code."""
    
    def add_arguments(self, pars):
        """Add command line arguments."""
        pars.add_argument("--tab", type=str, dest="tab", default="options")
        pars.add_argument("--feedrate", type=int, dest="feedrate", default=1500)
        pars.add_argument("--z_height", type=float, dest="z_height", default=2.0)
        pars.add_argument("--add_comments", type=inkex.Boolean, dest="add_comments", default=True)
        pars.add_argument("--output_path", type=str, dest="output_path", default="")
    
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
            
            # Create G-code content
            gcode = self.generate_gcode()
            
            # Debug: Show current working directory
            inkex.utils.debug(f"Current working directory: {os.getcwd()}")
            
            # Debug: Check if directory exists
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                inkex.utils.debug(f"Directory does not exist: {output_dir}")
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    inkex.utils.debug(f"Created directory: {output_dir}")
                except Exception as e:
                    inkex.utils.debug(f"Failed to create directory: {str(e)}")
            
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
            
        except Exception as e:
            inkex.utils.debug(f"Error exporting G-code: {str(e)}")
            import traceback
            inkex.utils.debug(traceback.format_exc())
            self.msg(f"Error: {str(e)}")
    
    def generate_gcode(self):
        """Generate G-code content."""
        # Get SVG document information
        svg_name = "Unknown"
        try:
            svg_file = self.document_path()
            if svg_file and svg_file != 'memory':
                svg_name = os.path.basename(svg_file)
        except:
            pass
            
        # Add a header comment
        header = "; Test G-code Export (Effect Extension)\n"
        header += f"; Source SVG: {svg_name}\n"
        header += f"; Feedrate: {self.options.feedrate} mm/min\n"
        header += f"; Z Height: {self.options.z_height} mm\n\n"
        
        # Add some simple G-code
        gcode = "G21 ; Set units to mm\n"
        gcode += "G90 ; Set absolute positioning\n"
        gcode += f"G0 X0 Y0 Z{self.options.z_height + 3} ; Move to origin\n"
        
        # Add comments if requested
        comment = " ; Draw a line" if self.options.add_comments else ""
        gcode += f"G0 X10 Y10 Z{self.options.z_height}{comment}\n"
        gcode += f"G1 X20 Y10 F{self.options.feedrate}{comment}\n"
        
        comment = " ; Draw another line" if self.options.add_comments else ""
        gcode += f"G1 X20 Y20 F{self.options.feedrate}{comment}\n"
        gcode += f"G1 X10 Y20 F{self.options.feedrate}{comment}\n"
        
        comment = " ; Close the square" if self.options.add_comments else ""
        gcode += f"G1 X10 Y10 F{self.options.feedrate}{comment}\n"
        
        comment = " ; Lift the tool" if self.options.add_comments else ""
        gcode += f"G0 Z{self.options.z_height + 3}{comment}\n"
        
        comment = " ; Return to origin" if self.options.add_comments else ""
        gcode += f"G0 X0 Y0{comment}\n"
        
        return header + gcode


if __name__ == '__main__':
    TestGcodeExportEffect().run() 
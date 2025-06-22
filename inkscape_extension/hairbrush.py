#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H.Airbrush - Main module for the H.Airbrush Inkscape extension

This module implements the core functionality for the H.Airbrush dual-airbrush plotter system.
It is called by hairbrush_control.py which handles the Inkscape UI integration.
"""

import os
import sys
import time
import math
import logging
import tempfile
from lxml import etree
import inkex
import simplestyle

# Setup logging
log_file = os.path.join(tempfile.gettempdir(), 'hairbrush_debug.log')
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file)
logger = logging.getLogger('hairbrush')

# Add the extensions directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import our modules
try:
    from hairbrush_lib import svg_parser, path_processor
    logger.info("Successfully imported hairbrush_lib modules")
except ImportError:
    logger.error("Failed to import hairbrush_lib modules")
    sys.stderr.write("Error: Could not import hairbrush_lib modules. Make sure they are installed correctly.\n")

# Constants
VERSION = "1.0.0"

class HairbrushPlotter:
    """
    Main class for the H.Airbrush plotter
    """
    
    def __init__(self, document, options):
        """Initialize the plotter with document and options"""
        self.document = document
        self.options = options
        self.svg_parser = None
        self.path_processor = None
        self.gcode_generator = None
        self.preview_renderer = None
        
        # Initialize the components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize the SVG parser, path processor, and G-code generator"""
        try:
            # Import here to avoid errors if modules are missing
            from hairbrush_lib.svg_parser import SVGParser
            from hairbrush_lib.path_processor import PathProcessor
            
            # Create instances
            self.svg_parser = SVGParser(self.document)
            self.path_processor = PathProcessor(
                curve_tolerance=1.0,  # Default value, can be overridden
                path_handling=1       # Default value, can be overridden
            )
            
            logger.info("Components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}", exc_info=True)
            raise
    
    def plot(self):
        """Execute the plotting operation"""
        logger.info("Starting plot operation")
        
        # Extract paths from SVG
        paths = self._extract_paths()
        if not paths:
            logger.warning("No paths found to plot")
            return False
        
        # Process paths
        processed_paths = self._process_paths(paths)
        
        # Generate G-code
        gcode = self._generate_gcode(processed_paths)
        
        # Output G-code
        self._output_gcode(gcode)
        
        # If multiple copies requested, handle them
        copies = int(self.options.get('copies', 1))
        if copies > 1:
            page_delay = int(self.options.get('page_delay', 15))
            for i in range(1, copies):
                logger.info(f"Plotting copy {i+1} of {copies}")
                time.sleep(page_delay)
                self._output_gcode(gcode)
        
        return True
    
    def _extract_paths(self):
        """Extract paths from the SVG document"""
        try:
            logger.info("Extracting paths from SVG")
            
            # Extract paths
            paths = self.svg_parser.extract_paths()
            logger.info(f"Extracted {len(paths)} paths")
            
            return paths
        except Exception as e:
            logger.error(f"Error extracting paths: {str(e)}", exc_info=True)
            return []
    
    def _process_paths(self, paths):
        """Process the extracted paths"""
        try:
            logger.info("Processing paths")
            
            # Process paths
            processed_paths = self.path_processor.process_paths(paths)
            logger.info(f"Processed {len(processed_paths)} paths")
            
            return processed_paths
        except Exception as e:
            logger.error(f"Error processing paths: {str(e)}", exc_info=True)
            return []
    
    def _generate_gcode(self, paths):
        """Generate G-code from the processed paths"""
        try:
            logger.info("Generating G-code")
            
            # Import the GCodeGenerator
            from hairbrush_lib.gcode_generator import GCodeGenerator
            
            # Create a GCodeGenerator instance
            gcode_gen = GCodeGenerator()
            
            # Configure Z behavior based on user options
            min_z = float(self.options.get('min_z', 1.0))
            max_z = float(self.options.get('max_z', 15.0))
            travel_z = float(self.options.get('travel_z', 10.0))
            spray_angle = float(self.options.get('spray_angle', 15.0))
            gcode_gen.configure_z_behavior(min_z, max_z, travel_z, spray_angle)
            
            # Configure Z transformation parameters
            z_scale = float(self.options.get('z_scale', 1.0))
            z_offset = float(self.options.get('z_offset', 0.0))
            gcode_gen.set_z_transformation(z_scale, z_offset)
            
            # Configure the default brush
            default_brush = self.options.get('brush', 'brush_a')
            z_height = float(self.options.get('z_height', 2.0))
            feedrate = int(self.options.get('feedrate', 1500))
            
            gcode_gen.configure_brush(default_brush, {
                "offset": (0, 0),  # Default offset
                "z_height": z_height
            })
            
            # Get SVG document properties
            svg_width, svg_height, viewbox = self.svg_parser.get_document_dimensions()
            if svg_width and svg_height:
                # Set document properties for proper scaling
                gcode_gen.set_svg_document_properties(viewbox, svg_width, svg_height)
                
                # Set machine origin to ensure proper alignment
                gcode_gen.set_machine_origin(0, 0, 0)
                
                # Apply user-defined transformations if provided
                scale_factor = float(self.options.get('scale_factor', 1.0))
                offset_x = float(self.options.get('offset_x', 0.0))
                offset_y = float(self.options.get('offset_y', 0.0))
                gcode_gen.set_user_transform(scale_factor, offset_x, offset_y)
            
            # Enable debug markers if in debug mode
            if self.options.get('debug', False):
                gcode_gen.enable_debug_markers(True)
                
            # Skip homing if requested
            if self.options.get('skip_homing', False):
                gcode_gen.set_skip_homing(True)
            
            # Add header information about the source file
            source_file = self.options.get('input_file', 'unknown.svg')
            source_file = os.path.basename(source_file)
            gcode_gen.output_lines.extend([
                f"; Source SVG: {source_file}",
                f"; Paths: {len(paths)}",
                f"; Base Z height: {z_height}mm",
                f"; Base feedrate: {feedrate}mm/min",
                f"; Simplification: {self.options.get('simplify', 'No')}",
                f"; Curve resolution: {self.options.get('curve_resolution', 20)}",
                f"; Debug markers: {self.options.get('debug', 'No')}",
                ""
            ])
            
            # Process each path
            for i, path in enumerate(paths):
                # Extract path data and attributes
                path_data = path.get('d', '')
                stroke_color = path.get('stroke', '#000000')
                stroke_width = float(path.get('stroke-width', 1.0))
                stroke_opacity = float(path.get('stroke-opacity', 1.0))
                path_id = path.get('id', f'path{i+1}')
                
                # Add comment for the path
                gcode_gen.output_lines.append(f"; Path {i+1}/{len(paths)} (id: {path_id})")
                
                # Add the path to the G-code generator using the path batching system
                curve_resolution = int(self.options.get('curve_resolution', 20))
                gcode_gen.add_path_with_attributes(
                    path_data, 
                    stroke_color, 
                    stroke_width, 
                    stroke_opacity, 
                    feedrate,
                    curve_resolution=curve_resolution
                )
            
            # Check if test pattern is requested
            include_test_pattern = self.options.get('test_pattern', False)
            
            # Generate the complete G-code
            # This will process all pending paths and generate the actual G-code
            gcode = gcode_gen.generate_gcode(include_test_pattern=include_test_pattern)
            
            return gcode
        except Exception as e:
            logger.error(f"Error generating G-code: {str(e)}", exc_info=True)
            return ""
    
    def _output_gcode(self, gcode):
        """Output the generated G-code"""
        try:
            logger.info("Outputting G-code")
            
            # Determine output filename
            output_file = self.options.get('output_file', '')
            if not output_file:
                # Try to get the input file name
                input_file = self.options.get('input_file', '')
                if input_file:
                    output_file = os.path.splitext(input_file)[0] + '.gcode'
                else:
                    # Fallback to a default name
                    output_file = os.path.expanduser("~/Desktop/hairbrush_output.gcode")
            
            # Ensure the directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Write the G-code to the file
            with open(output_file, 'w') as f:
                f.write(gcode)
            
            logger.info(f"G-code saved to {output_file}")
            print(f"G-code saved to {output_file}")
            
            return True
        except Exception as e:
            logger.error(f"Error outputting G-code: {str(e)}", exc_info=True)
            print(f"Error saving G-code: {str(e)}")
            return False
    
    def setup(self):
        """Execute the setup operation"""
        logger.info("Starting setup operation")
        
        setup_type = self.options.get('setup_type', 'home')
        logger.info(f"Setup type: {setup_type}")
        
        if setup_type == "home":
            print("Homing the machine...")
            # Code to home the machine would go here
        elif setup_type == "align":
            print("Disabling motors for manual alignment...")
            # Code to disable motors would go here
        elif setup_type == "test":
            print("Running test pattern...")
            # Code to run test pattern would go here
        else:
            logger.warning(f"Unknown setup type: {setup_type}")
            print(f"Unknown setup type: {setup_type}")
        
        return True
    
    def manual(self):
        """Execute the manual operation"""
        logger.info("Starting manual operation")
        
        cmd = self.options.get('manual_cmd', 'none')
        logger.info(f"Manual command: {cmd}")
        
        if cmd == "none":
            print("No command selected")
            return True
        
        if cmd == "walk_home":
            print("Moving to home position...")
            # Code to move to home position would go here
        elif cmd in ["walk_x", "walk_y", "walk_mmx", "walk_mmy"]:
            dist = self.options.get('dist', 1.0)
            print(f"Moving {dist} units in {cmd[5:]} direction...")
            # Code to move the carriage would go here
        elif cmd == "activate_a":
            print("Activating Brush A...")
            # Code to activate brush A would go here
        elif cmd == "activate_b":
            print("Activating Brush B...")
            # Code to activate brush B would go here
        elif cmd == "deactivate":
            print("Deactivating brushes...")
            # Code to deactivate brushes would go here
        elif cmd == "enable_xy":
            print("Enabling XY motors...")
            # Code to enable motors would go here
        elif cmd == "disable_xy":
            print("Disabling XY motors...")
            # Code to disable motors would go here
        elif cmd == "strip_data":
            print("Stripping plotter data from file...")
            # Code to strip plotter data would go here
        else:
            logger.warning(f"Unknown manual command: {cmd}")
            print(f"Unknown manual command: {cmd}")
        
        return True
    
    def layers(self):
        """Execute the layers operation"""
        logger.info("Starting layers operation")
        
        layer_number = self.options.get('layer', 1)
        logger.info(f"Layer number: {layer_number}")
        
        # Extract paths from the specified layer
        paths = self._extract_paths_from_layer(layer_number)
        if not paths:
            logger.warning(f"No paths found in layer {layer_number}")
            print(f"No paths found in layer {layer_number}")
            return False
        
        # Process paths
        processed_paths = self._process_paths(paths)
        
        # Generate G-code
        gcode = self._generate_gcode(processed_paths)
        
        # Output G-code
        self._output_gcode(gcode)
        
        return True
    
    def _extract_paths_from_layer(self, layer_number):
        """Extract paths from the specified layer"""
        try:
            logger.info(f"Extracting paths from layer {layer_number}")
            
            # Extract paths from the specified layer
            paths = self.svg_parser.extract_paths_from_layer(layer_number)
            logger.info(f"Extracted {len(paths)} paths from layer {layer_number}")
            
            return paths
        except Exception as e:
            logger.error(f"Error extracting paths from layer: {str(e)}", exc_info=True)
            return []
    
    def resume(self):
        """Execute the resume operation"""
        logger.info("Starting resume operation")
        
        resume_type = self.options.get('resume_type', 'ResumeNow')
        logger.info(f"Resume type: {resume_type}")
        
        if resume_type == "ResumeNow":
            print("Resuming plot...")
            # Code to resume plotting would go here
        elif resume_type == "home":
            print("Returning to home corner...")
            # Code to return to home corner would go here
        else:
            logger.warning(f"Unknown resume type: {resume_type}")
            print(f"Unknown resume type: {resume_type}")
        
        return True
    
    def options(self):
        """Execute the options operation"""
        logger.info("Starting options operation")
        
        submode = self.options.get('submode', 'Speed')
        logger.info(f"Options submode: {submode}")
        
        if submode == "sysinfo":
            print("Checking for updates...")
            # Code to check for updates would go here
        
        return True
    
    def preview(self):
        """Execute the preview operation"""
        logger.info("Starting preview operation")
        
        # Extract paths from SVG
        paths = self._extract_paths()
        if not paths:
            logger.warning("No paths found to preview")
            return False
        
        # Process paths
        processed_paths = self._process_paths(paths)
        
        # Generate preview
        self._generate_preview(processed_paths)
        
        return True
    
    def _generate_preview(self, paths):
        """Generate a preview of the plotting operation"""
        try:
            logger.info("Generating preview")
            
            # For now, just print a message
            print("Preview generated")
            print(f"Number of paths: {len(paths)}")
            
            # In a real implementation, we would generate a visual preview
            
            logger.info("Preview complete")
            return True
        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}", exc_info=True)
            return False

    def generate_gcode(self):
        """Generate G-code for the selected paths."""
        # Initialize G-code generator with template and configuration
        generator = GCodeGenerator(template=self.get_template())
        
        # Configure generator settings
        generator.z_travel = self.options.z_travel
        generator.skip_homing = self.options.skip_homing
        generator.scale_factor = self.options.scale_factor
        
        # Configure brush offsets
        brush_config = {
            'brush_a': {'offset': (self.options.brush_a_offset_x, self.options.brush_a_offset_y)},
            'brush_b': {'offset': (self.options.brush_b_offset_x, self.options.brush_b_offset_y)}
        }
        generator.brush_config = brush_config
        
        # Process each selected path
        for node in self.svg.selected.values():
            if node.tag == inkex.addNS('path', 'svg'):
                # Get path data
                path_data = node.get('d')
                if not path_data:
                    continue
                
                # Get style attributes
                style = simplestyle.parseStyle(node.get('style', ''))
                
                # Get stroke color, width, and opacity with defaults
                stroke_color = style.get('stroke', '#000000')
                stroke_opacity = float(style.get('stroke-opacity', '1.0'))
                stroke_width = self.svg.unittouu(style.get('stroke-width', '1px'))
                
                # Select brush based on color
                brush = "brush_a"  # Default to brush_a (black)
                if stroke_color.lower() in ["#ffffff", "white"]:
                    brush = "brush_b"  # Use brush_b for white
                
                # Calculate parameters for airbrush based on stroke attributes
                z_height, paint_flow, speed_factor = generator.calculate_airbrush_parameters(
                    stroke_width, stroke_opacity
                )
                feedrate = self.options.base_feedrate * speed_factor
                
                # Add path to generator
                generator.add_path(
                    path_data, 
                    brush, 
                    z_height, 
                    feedrate, 
                    curve_resolution=self.options.curve_resolution,
                    paint_flow=paint_flow
                )
                
        # Generate G-code with optional test pattern
        gcode = generator.generate_gcode(include_test_pattern=self.options.include_test_pattern)
        
        return gcode

# Module-level functions that are called by hairbrush_control.py

def plot(document, options):
    """Plot the document with the specified options"""
    plotter = HairbrushPlotter(document, options)
    return plotter.plot()

def setup(document, options):
    """Execute the setup operation"""
    plotter = HairbrushPlotter(document, options)
    return plotter.setup()

def manual(document, options):
    """Execute the manual operation"""
    plotter = HairbrushPlotter(document, options)
    return plotter.manual()

def layers(document, options):
    """Execute the layers operation"""
    plotter = HairbrushPlotter(document, options)
    return plotter.layers()

def resume(document, options):
    """Execute the resume operation"""
    plotter = HairbrushPlotter(document, options)
    return plotter.resume()

def options(document, options):
    """Execute the options operation"""
    plotter = HairbrushPlotter(document, options)
    return plotter.options()

def preview(document, options):
    """Execute the preview operation"""
    plotter = HairbrushPlotter(document, options)
    return plotter.preview() 
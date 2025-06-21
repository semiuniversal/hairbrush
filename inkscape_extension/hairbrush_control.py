#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H.Airbrush Control - Inkscape extension for dual-airbrush plotter control

This script serves as the main entry point for the H.Airbrush Inkscape extension.
It processes the parameters from the Inkscape UI and delegates to the main hairbrush.py module.
"""

import os
import sys
import inkex
import tempfile
import logging
from lxml import etree

# Setup logging
log_file = os.path.join(tempfile.gettempdir(), 'hairbrush_debug.log')
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file)
logger = logging.getLogger('hairbrush_control')

# Add the extensions directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import our modules
try:
    import hairbrush
    logger.info("Successfully imported hairbrush module")
except ImportError:
    logger.error("Failed to import hairbrush module")
    sys.stderr.write("Error: Could not import hairbrush module. Make sure it is installed correctly.\n")

class HairbrushControl(inkex.EffectExtension):
    """
    Control script for the H.Airbrush extension
    """
    
    def __init__(self):
        """Initialize the extension with parameters from the UI"""
        super(HairbrushControl, self).__init__()
        
        # Main tab parameters
        self.arg_parser.add_argument("--mode", type=str, default="plot")
        self.arg_parser.add_argument("--preview", type=inkex.Boolean, default=False)
        
        # Plot tab parameters
        self.arg_parser.add_argument("--copies", type=int, default=1)
        self.arg_parser.add_argument("--page_delay", type=int, default=15)
        
        # Setup tab parameters
        self.arg_parser.add_argument("--brush_a_height", type=int, default=60)
        self.arg_parser.add_argument("--brush_b_height", type=int, default=60)
        self.arg_parser.add_argument("--setup_type", type=str, default="home")
        
        # Options tab - Speed page
        self.arg_parser.add_argument("--submode", type=str, default="Speed")
        self.arg_parser.add_argument("--speed_drawing", type=int, default=25)
        self.arg_parser.add_argument("--speed_travel", type=int, default=75)
        self.arg_parser.add_argument("--accel", type=str, default="50")
        self.arg_parser.add_argument("--const_speed", type=inkex.Boolean, default=False)
        
        # Options tab - Brush timing page
        self.arg_parser.add_argument("--brush_switch_rate", type=str, default="50")
        self.arg_parser.add_argument("--brush_activate_rate", type=str, default="50")
        self.arg_parser.add_argument("--brush_delay_switch", type=int, default=500)
        self.arg_parser.add_argument("--brush_delay_activate", type=int, default=250)
        
        # Options tab - Notifications page
        self.arg_parser.add_argument("--report_time", type=inkex.Boolean, default=False)
        self.arg_parser.add_argument("--rendering", type=str, default="3")
        
        # Options tab - Advanced page
        self.arg_parser.add_argument("--auto_rotate", type=inkex.Boolean, default=True)
        self.arg_parser.add_argument("--random_start", type=inkex.Boolean, default=False)
        self.arg_parser.add_argument("--reordering", type=str, default="1")
        self.arg_parser.add_argument("--resolution", type=str, default="1")
        
        # Options tab - Config page
        self.arg_parser.add_argument("--model", type=str, default="1")
        self.arg_parser.add_argument("--port_config", type=str, default="1")
        self.arg_parser.add_argument("--port", type=str, default="")
        
        # Manual tab parameters
        self.arg_parser.add_argument("--manual_cmd", type=str, default="none")
        self.arg_parser.add_argument("--dist", type=float, default=1.0)
        
        # Layers tab parameters
        self.arg_parser.add_argument("--layer", type=int, default=1)
        
        # Resume tab parameters
        self.arg_parser.add_argument("--resume_type", type=str, default="ResumeNow")
    
    def effect(self):
        """Main entry point for the extension"""
        try:
            # Log the start of execution and parameters
            logger.info("H.Airbrush Control extension started")
            logger.info(f"Mode: {self.options.mode}")
            logger.info(f"Preview: {self.options.preview}")
            
            # Create options dictionary to pass to the main module
            options_dict = vars(self.options)
            
            # If we're in preview mode, handle it specially
            if self.options.preview:
                logger.info("Preview mode enabled")
                self._handle_preview_mode(options_dict)
                return
            
            # Handle the selected mode
            if self.options.mode == "plot":
                self._handle_plot_mode(options_dict)
            elif self.options.mode == "setup":
                self._handle_setup_mode(options_dict)
            elif self.options.mode == "options":
                self._handle_options_mode(options_dict)
            elif self.options.mode == "manual":
                self._handle_manual_mode(options_dict)
            elif self.options.mode == "layers":
                self._handle_layers_mode(options_dict)
            elif self.options.mode == "resume":
                self._handle_resume_mode(options_dict)
            else:
                logger.warning(f"Unknown mode: {self.options.mode}")
                inkex.errormsg(f"Unknown mode: {self.options.mode}")
        
        except Exception as e:
            logger.error(f"Error in effect(): {str(e)}", exc_info=True)
            inkex.errormsg(f"H.Airbrush extension error: {str(e)}")
    
    def _handle_preview_mode(self, options):
        """Handle preview mode"""
        try:
            # Import the main module
            import hairbrush
            
            # Call the preview function
            hairbrush.preview(self.document, options)
            
            logger.info("Preview completed")
        except Exception as e:
            logger.error(f"Error in preview mode: {str(e)}", exc_info=True)
            inkex.errormsg(f"Error in preview mode: {str(e)}")
    
    def _handle_plot_mode(self, options):
        """Handle plot mode"""
        try:
            # Import the main module
            import hairbrush
            
            # Call the plot function
            hairbrush.plot(self.document, options)
            
            logger.info("Plot completed")
        except Exception as e:
            logger.error(f"Error in plot mode: {str(e)}", exc_info=True)
            inkex.errormsg(f"Error in plot mode: {str(e)}")
    
    def _handle_setup_mode(self, options):
        """Handle setup mode"""
        try:
            # Import the main module
            import hairbrush
            
            # Call the setup function
            hairbrush.setup(self.document, options)
            
            logger.info("Setup completed")
        except Exception as e:
            logger.error(f"Error in setup mode: {str(e)}", exc_info=True)
            inkex.errormsg(f"Error in setup mode: {str(e)}")
    
    def _handle_options_mode(self, options):
        """Handle options mode"""
        try:
            # Import the main module
            import hairbrush
            
            # Call the options function
            hairbrush.options(self.document, options)
            
            logger.info("Options completed")
        except Exception as e:
            logger.error(f"Error in options mode: {str(e)}", exc_info=True)
            inkex.errormsg(f"Error in options mode: {str(e)}")
    
    def _handle_manual_mode(self, options):
        """Handle manual mode"""
        try:
            # Import the main module
            import hairbrush
            
            # Call the manual function
            hairbrush.manual(self.document, options)
            
            logger.info("Manual command completed")
        except Exception as e:
            logger.error(f"Error in manual mode: {str(e)}", exc_info=True)
            inkex.errormsg(f"Error in manual mode: {str(e)}")
    
    def _handle_layers_mode(self, options):
        """Handle layers mode"""
        try:
            # Import the main module
            import hairbrush
            
            # Call the layers function
            hairbrush.layers(self.document, options)
            
            logger.info("Layers plot completed")
        except Exception as e:
            logger.error(f"Error in layers mode: {str(e)}", exc_info=True)
            inkex.errormsg(f"Error in layers mode: {str(e)}")
    
    def _handle_resume_mode(self, options):
        """Handle resume mode"""
        try:
            # Import the main module
            import hairbrush
            
            # Call the resume function
            hairbrush.resume(self.document, options)
            
            logger.info("Resume completed")
        except Exception as e:
            logger.error(f"Error in resume mode: {str(e)}", exc_info=True)
            inkex.errormsg(f"Error in resume mode: {str(e)}")

if __name__ == '__main__':
    HairbrushControl().run() 
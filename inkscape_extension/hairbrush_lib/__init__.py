#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hairbrush Library - Core modules for the H.Airbrush Inkscape extension.

This package contains the core functionality for SVG parsing, path processing,
and G-code generation for the H.Airbrush dual-airbrush plotter system.
"""

import os
import sys

# Add the vendor directory to the Python path
vendor_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'vendor')
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

__version__ = '1.0.0'

# Import modules for easier access
from . import svg_parser
from . import path_processor
from . import gcode_generator
from . import config

# Expose main classes
from .svg_parser import SVGParser
from .path_processor import PathProcessor
from .gcode_generator import GCodeGenerator

__author__ = 'H.Airbrush Team' 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG Parser for the H.Airbrush extension

This module handles parsing SVG files and extracting paths for the H.Airbrush extension.
"""

import os
import sys
import math
import logging
import tempfile
from lxml import etree
import re
import inkex
from inkex import bezier

# Setup logging
log_file = os.path.join(tempfile.gettempdir(), 'hairbrush_debug.log')
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file)
logger = logging.getLogger('hairbrush_svg_parser')

class SVGPath:
    """
    Class representing an SVG path with its properties
    """
    
    def __init__(self, path_id=None, d=None, style=None, transform=None, layer=None):
        """Initialize the SVG path"""
        self.id = path_id
        self.d = d
        self.style = style or {}
        self.transform = transform
        self.layer = layer
        self.commands = []
        self.bounds = None
        
        # Parse the path commands if d is provided
        if d:
            self._parse_commands()
    
    def _parse_commands(self):
        """Parse the path commands from the d attribute"""
        try:
            # Use inkex's built-in path parser
            path = inkex.Path(self.d)
            self.commands = path
            
            # Calculate bounds
            self._calculate_bounds()
            
            logger.debug(f"Parsed path with {len(self.commands)} commands")
        except Exception as e:
            logger.error(f"Error parsing path commands: {str(e)}", exc_info=True)
    
    def _calculate_bounds(self):
        """Calculate the bounding box of the path"""
        try:
            if not self.commands:
                return
            
            # Use inkex's built-in bounding box calculation
            bounds = inkex.Path(self.commands).bounding_box()
            if bounds:
                self.bounds = {
                    'x': bounds.left,
                    'y': bounds.top,
                    'width': bounds.width,
                    'height': bounds.height
                }
                
                logger.debug(f"Path bounds: {self.bounds}")
        except Exception as e:
            logger.error(f"Error calculating path bounds: {str(e)}", exc_info=True)

class SVGParser:
    """
    Class for parsing SVG files and extracting paths
    """
    
    # SVG namespace
    SVG_NS = "{http://www.w3.org/2000/svg}"
    INKSCAPE_NS = "{http://www.inkscape.org/namespaces/inkscape}"
    SODIPODI_NS = "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}"
    XLINK_NS = "{http://www.w3.org/1999/xlink}"
    
    def __init__(self, document):
        """Initialize the SVG parser with the document"""
        self.document = document
        self.root = None
        self.viewbox = None
        self.width = None
        self.height = None
        self.layers = {}
        
        # Debug information
        logger.info(f"Initializing SVGParser with document type: {type(document)}")
        
        # Parse the document
        self._parse_document()
    
    def _parse_document(self):
        """Parse the SVG document"""
        try:
            # Check if document is a string (file path)
            if isinstance(self.document, str):
                logger.info(f"Parsing document from file path: {self.document}")
                try:
                    from lxml import etree
                    tree = etree.parse(self.document)
                    self.root = tree.getroot()
                    logger.info(f"Parsed XML document with root tag: {self.root.tag}")
                except Exception as e:
                    logger.error(f"Error parsing XML from file: {str(e)}", exc_info=True)
                    return
            else:
                # Assume it's already an XML element or document
                logger.info("Document is not a string, assuming it's an XML element or document")
                self.root = self.document.getroot() if hasattr(self.document, 'getroot') else self.document
            
            # Get the viewBox attribute
            if self.root is not None and 'viewBox' in self.root.attrib:
                viewbox = self.root.attrib['viewBox'].split()
                self.viewbox = {
                    'x': float(viewbox[0]),
                    'y': float(viewbox[1]),
                    'width': float(viewbox[2]),
                    'height': float(viewbox[3])
                }
                logger.info(f"Found viewBox: {self.viewbox}")
            else:
                logger.warning("No viewBox attribute found in SVG root")
            
            # Get the width and height
            if self.root is not None:
                if 'width' in self.root.attrib:
                    self.width = self._parse_dimension(self.root.attrib['width'])
                    logger.info(f"Found width: {self.width}")
                if 'height' in self.root.attrib:
                    self.height = self._parse_dimension(self.root.attrib['height'])
                    logger.info(f"Found height: {self.height}")
            
            # Find all layers
            self._find_layers()
            
            logger.info("Document parsed successfully")
            logger.info(f"Viewbox: {self.viewbox}")
            logger.info(f"Width: {self.width}, Height: {self.height}")
            logger.info(f"Found {len(self.layers)} layers")
        except Exception as e:
            logger.error(f"Error parsing document: {str(e)}", exc_info=True)
    
    def _parse_dimension(self, value):
        """Parse a dimension value from the SVG"""
        try:
            # Remove any units
            value = re.sub(r'[a-zA-Z]+$', '', value)
            return float(value)
        except Exception as e:
            logger.error(f"Error parsing dimension: {str(e)}", exc_info=True)
            return None
    
    def _find_layers(self):
        """Find all layers in the document"""
        try:
            # Find all groups that are layers
            for element in self.root.findall(f".//{self.SVG_NS}g"):
                # Check if it's a layer
                if f"{self.INKSCAPE_NS}groupmode" in element.attrib and element.attrib[f"{self.INKSCAPE_NS}groupmode"] == "layer":
                    # Get the layer ID and label
                    layer_id = element.attrib.get('id', '')
                    layer_label = element.attrib.get(f"{self.INKSCAPE_NS}label", layer_id)
                    
                    # Store the layer
                    self.layers[layer_id] = {
                        'id': layer_id,
                        'label': layer_label,
                        'element': element
                    }
                    
                    logger.debug(f"Found layer: {layer_label} (ID: {layer_id})")
        except Exception as e:
            logger.error(f"Error finding layers: {str(e)}", exc_info=True)
    
    def extract_paths(self):
        """Extract all paths from the document"""
        try:
            paths = []
            
            if self.root is None:
                logger.error("Cannot extract paths: root element is None")
                return paths
            
            logger.info("Extracting paths from SVG document")
            
            # Find all path elements
            logger.info("Looking for path elements...")
            path_elements = self.root.findall(f".//{self.SVG_NS}path")
            logger.info(f"Found {len(path_elements)} path elements")
            
            for element in path_elements:
                path = self._extract_path_from_element(element)
                if path:
                    paths.append(path)
            
            # Find all rectangles and convert to paths
            logger.info("Looking for rectangle elements...")
            rect_elements = self.root.findall(f".//{self.SVG_NS}rect")
            logger.info(f"Found {len(rect_elements)} rectangle elements")
            
            for element in rect_elements:
                path = self._extract_rect_as_path(element)
                if path:
                    paths.append(path)
            
            # Find all circles and convert to paths
            logger.info("Looking for circle elements...")
            circle_elements = self.root.findall(f".//{self.SVG_NS}circle")
            logger.info(f"Found {len(circle_elements)} circle elements")
            
            for element in circle_elements:
                path = self._extract_circle_as_path(element)
                if path:
                    paths.append(path)
            
            # Find all ellipses and convert to paths
            logger.info("Looking for ellipse elements...")
            ellipse_elements = self.root.findall(f".//{self.SVG_NS}ellipse")
            logger.info(f"Found {len(ellipse_elements)} ellipse elements")
            
            for element in ellipse_elements:
                path = self._extract_ellipse_as_path(element)
                if path:
                    paths.append(path)
            
            # Find all lines and convert to paths
            logger.info("Looking for line elements...")
            line_elements = self.root.findall(f".//{self.SVG_NS}line")
            logger.info(f"Found {len(line_elements)} line elements")
            
            for element in line_elements:
                path = self._extract_line_as_path(element)
                if path:
                    paths.append(path)
            
            logger.info(f"Total paths extracted: {len(paths)}")
            return paths
        except Exception as e:
            logger.error(f"Error extracting paths: {str(e)}", exc_info=True)
            return []
    
    def extract_paths_from_layer(self, layer_number):
        """Extract paths from a specific layer"""
        try:
            paths = []
            
            # Find layers that start with the specified number
            layer_prefix = str(layer_number)
            matching_layers = []
            
            for layer_id, layer in self.layers.items():
                if layer['label'].startswith(layer_prefix):
                    matching_layers.append(layer)
            
            if not matching_layers:
                logger.warning(f"No layers found with prefix '{layer_prefix}'")
                return []
            
            # Extract paths from matching layers
            for layer in matching_layers:
                layer_element = layer['element']
                
                # Find all path elements in this layer
                for element in layer_element.findall(f".//{self.SVG_NS}path"):
                    path = self._extract_path_from_element(element, layer['label'])
                    if path:
                        paths.append(path)
                
                # Find all other shape elements and convert to paths
                for shape_type in ['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon']:
                    for element in layer_element.findall(f".//{self.SVG_NS}{shape_type}"):
                        path = getattr(self, f"_extract_{shape_type}_as_path")(element, layer['label'])
                        if path:
                            paths.append(path)
            
            logger.info(f"Extracted {len(paths)} paths from layer(s) with prefix '{layer_prefix}'")
            return paths
        except Exception as e:
            logger.error(f"Error extracting paths from layer: {str(e)}", exc_info=True)
            return []
    
    def _extract_path_from_element(self, element, layer=None):
        """Extract an SVG path from a path element"""
        try:
            # Get the path attributes
            path_id = element.attrib.get('id', '')
            d = element.attrib.get('d', '')
            
            if not d:
                logger.warning(f"Path element with ID '{path_id}' has no 'd' attribute")
                return None
            
            # Get the style attributes
            style = self._extract_style(element)
            
            # Get the transform
            transform = element.attrib.get('transform', None)
            
            # Create and return the SVG path
            return SVGPath(path_id=path_id, d=d, style=style, transform=transform, layer=layer)
        except Exception as e:
            logger.error(f"Error extracting path from element: {str(e)}", exc_info=True)
            return None
    
    def _extract_rect_as_path(self, element, layer=None):
        """Extract an SVG path from a rectangle element"""
        try:
            # Get the rectangle attributes
            rect_id = element.attrib.get('id', '')
            x = float(element.attrib.get('x', '0'))
            y = float(element.attrib.get('y', '0'))
            width = float(element.attrib.get('width', '0'))
            height = float(element.attrib.get('height', '0'))
            rx = float(element.attrib.get('rx', '0'))
            ry = float(element.attrib.get('ry', '0'))
            
            # If only one of rx or ry is specified, use it for both
            if rx > 0 and ry == 0:
                ry = rx
            elif ry > 0 and rx == 0:
                rx = ry
            
            # Create the path data
            if rx == 0 and ry == 0:
                # Simple rectangle
                d = f"M {x},{y} h {width} v {height} h {-width} Z"
            else:
                # Rounded rectangle
                d = f"M {x+rx},{y} h {width-2*rx} a {rx},{ry} 0 0 1 {rx},{ry} v {height-2*ry} a {rx},{ry} 0 0 1 {-rx},{ry} h {-width+2*rx} a {rx},{ry} 0 0 1 {-rx},{-ry} v {-height+2*ry} a {rx},{ry} 0 0 1 {rx},{-ry} Z"
            
            # Get the style attributes
            style = self._extract_style(element)
            
            # Get the transform
            transform = element.attrib.get('transform', None)
            
            # Create and return the SVG path
            return SVGPath(path_id=rect_id, d=d, style=style, transform=transform, layer=layer)
        except Exception as e:
            logger.error(f"Error extracting rectangle as path: {str(e)}", exc_info=True)
            return None
    
    def _extract_circle_as_path(self, element, layer=None):
        """Extract an SVG path from a circle element"""
        try:
            # Get the circle attributes
            circle_id = element.attrib.get('id', '')
            cx = float(element.attrib.get('cx', '0'))
            cy = float(element.attrib.get('cy', '0'))
            r = float(element.attrib.get('r', '0'))
            
            # Create the path data (approximation of a circle using cubic Bezier curves)
            # Using the 4-curve approximation
            k = 0.5522847498 # Magic number for approximating a circle with 4 Bezier curves
            d = f"M {cx-r},{cy} C {cx-r},{cy-k*r} {cx-k*r},{cy-r} {cx},{cy-r} C {cx+k*r},{cy-r} {cx+r},{cy-k*r} {cx+r},{cy} C {cx+r},{cy+k*r} {cx+k*r},{cy+r} {cx},{cy+r} C {cx-k*r},{cy+r} {cx-r},{cy+k*r} {cx-r},{cy} Z"
            
            # Get the style attributes
            style = self._extract_style(element)
            
            # Get the transform
            transform = element.attrib.get('transform', None)
            
            # Create and return the SVG path
            return SVGPath(path_id=circle_id, d=d, style=style, transform=transform, layer=layer)
        except Exception as e:
            logger.error(f"Error extracting circle as path: {str(e)}", exc_info=True)
            return None
    
    def _extract_ellipse_as_path(self, element, layer=None):
        """Extract an SVG path from an ellipse element"""
        try:
            # Get the ellipse attributes
            ellipse_id = element.attrib.get('id', '')
            cx = float(element.attrib.get('cx', '0'))
            cy = float(element.attrib.get('cy', '0'))
            rx = float(element.attrib.get('rx', '0'))
            ry = float(element.attrib.get('ry', '0'))
            
            # Create the path data (approximation of an ellipse using cubic Bezier curves)
            # Using the 4-curve approximation
            k = 0.5522847498 # Magic number for approximating an ellipse with 4 Bezier curves
            d = f"M {cx-rx},{cy} C {cx-rx},{cy-k*ry} {cx-k*rx},{cy-ry} {cx},{cy-ry} C {cx+k*rx},{cy-ry} {cx+rx},{cy-k*ry} {cx+rx},{cy} C {cx+rx},{cy+k*ry} {cx+k*rx},{cy+ry} {cx},{cy+ry} C {cx-k*rx},{cy+ry} {cx-rx},{cy+k*ry} {cx-rx},{cy} Z"
            
            # Get the style attributes
            style = self._extract_style(element)
            
            # Get the transform
            transform = element.attrib.get('transform', None)
            
            # Create and return the SVG path
            return SVGPath(path_id=ellipse_id, d=d, style=style, transform=transform, layer=layer)
        except Exception as e:
            logger.error(f"Error extracting ellipse as path: {str(e)}", exc_info=True)
            return None
    
    def _extract_line_as_path(self, element, layer=None):
        """Extract an SVG path from a line element"""
        try:
            # Get the line attributes
            line_id = element.attrib.get('id', '')
            x1 = float(element.attrib.get('x1', '0'))
            y1 = float(element.attrib.get('y1', '0'))
            x2 = float(element.attrib.get('x2', '0'))
            y2 = float(element.attrib.get('y2', '0'))
            
            # Create the path data
            d = f"M {x1},{y1} L {x2},{y2}"
            
            # Get the style attributes
            style = self._extract_style(element)
            
            # Get the transform
            transform = element.attrib.get('transform', None)
            
            # Create and return the SVG path
            return SVGPath(path_id=line_id, d=d, style=style, transform=transform, layer=layer)
        except Exception as e:
            logger.error(f"Error extracting line as path: {str(e)}", exc_info=True)
            return None
    
    def _extract_polyline_as_path(self, element, layer=None):
        """Extract an SVG path from a polyline element"""
        try:
            # Get the polyline attributes
            polyline_id = element.attrib.get('id', '')
            points = element.attrib.get('points', '')
            
            if not points:
                logger.warning(f"Polyline element with ID '{polyline_id}' has no 'points' attribute")
                return None
            
            # Parse the points
            point_list = re.findall(r'(-?[\d.]+)[,\s](-?[\d.]+)', points)
            if not point_list:
                logger.warning(f"Polyline element with ID '{polyline_id}' has invalid 'points' attribute")
                return None
            
            # Create the path data
            d = f"M {point_list[0][0]},{point_list[0][1]}"
            for point in point_list[1:]:
                d += f" L {point[0]},{point[1]}"
            
            # Get the style attributes
            style = self._extract_style(element)
            
            # Get the transform
            transform = element.attrib.get('transform', None)
            
            # Create and return the SVG path
            return SVGPath(path_id=polyline_id, d=d, style=style, transform=transform, layer=layer)
        except Exception as e:
            logger.error(f"Error extracting polyline as path: {str(e)}", exc_info=True)
            return None
    
    def _extract_polygon_as_path(self, element, layer=None):
        """Extract an SVG path from a polygon element"""
        try:
            # Get the polygon attributes
            polygon_id = element.attrib.get('id', '')
            points = element.attrib.get('points', '')
            
            if not points:
                logger.warning(f"Polygon element with ID '{polygon_id}' has no 'points' attribute")
                return None
            
            # Parse the points
            point_list = re.findall(r'(-?[\d.]+)[,\s](-?[\d.]+)', points)
            if not point_list:
                logger.warning(f"Polygon element with ID '{polygon_id}' has invalid 'points' attribute")
                return None
            
            # Create the path data
            d = f"M {point_list[0][0]},{point_list[0][1]}"
            for point in point_list[1:]:
                d += f" L {point[0]},{point[1]}"
            d += " Z"
            
            # Get the style attributes
            style = self._extract_style(element)
            
            # Get the transform
            transform = element.attrib.get('transform', None)
            
            # Create and return the SVG path
            return SVGPath(path_id=polygon_id, d=d, style=style, transform=transform, layer=layer)
        except Exception as e:
            logger.error(f"Error extracting polygon as path: {str(e)}", exc_info=True)
            return None
    
    def _extract_style(self, element):
        """Extract style attributes from an element"""
        try:
            style = {}
            
            # Check for inline style attribute
            if 'style' in element.attrib:
                # Parse the style attribute
                style_str = element.attrib['style']
                style_items = re.findall(r'([^:;]+):([^:;]+)(?:;|$)', style_str)
                for name, value in style_items:
                    style[name.strip()] = value.strip()
            
            # Check for individual style attributes
            for attr in ['fill', 'stroke', 'stroke-width', 'stroke-opacity', 'fill-opacity', 'opacity']:
                if attr in element.attrib:
                    style[attr] = element.attrib[attr]
            
            return style
        except Exception as e:
            logger.error(f"Error extracting style: {str(e)}", exc_info=True)
            return {}
    
    def get_document_dimensions(self):
        """
        Get the dimensions of the SVG document.
        
        Returns:
            tuple: (width, height, viewbox) where viewbox is a tuple (min_x, min_y, width, height)
                  or (None, None, None) if dimensions are not available
        """
        try:
            # Convert viewbox to the format expected by GCodeGenerator
            viewbox_tuple = None
            if self.viewbox:
                viewbox_tuple = (
                    self.viewbox['x'],
                    self.viewbox['y'],
                    self.viewbox['width'],
                    self.viewbox['height']
                )
            
            logger.info(f"Document dimensions: width={self.width}, height={self.height}, viewbox={viewbox_tuple}")
            
            return self.width, self.height, viewbox_tuple
        except Exception as e:
            logger.error(f"Error getting document dimensions: {str(e)}", exc_info=True)
            return None, None, None 
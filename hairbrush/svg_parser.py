"""
SVG Parser for Hairbrush

This module provides functionality to parse SVG files and extract paths and their attributes.
"""

import os
import re
import xml.etree.ElementTree as ET
import inkex
from inkex import bezier

# Register SVG namespace
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("svg", "http://www.w3.org/2000/svg")
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
ET.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")

# SVG namespace
SVG_NS = "{http://www.w3.org/2000/svg}"
INKSCAPE_NS = "{http://www.inkscape.org/namespaces/inkscape}"


class SVGParser:
    """Parser for SVG files to extract paths and their attributes."""
    
    def __init__(self, svg_file):
        """Initialize the parser with an SVG file path."""
        self.svg_file = svg_file
        self.tree = ET.parse(svg_file)
        self.root = self.tree.getroot()
        self.viewbox = None
        self.width = None
        self.height = None
        self._parse_document_properties()
    
    def _parse_document_properties(self):
        """Parse the document properties like viewBox, width, and height."""
        if self.root is None:
            return
        
        # Get viewBox
        viewbox_str = self.root.get('viewBox')
        if viewbox_str:
            try:
                self.viewbox = [float(x) for x in viewbox_str.split()]
            except (ValueError, TypeError):
                self.viewbox = [0, 0, 100, 100]  # Default viewBox
        else:
            self.viewbox = [0, 0, 100, 100]  # Default viewBox
        
        # Get width and height
        width_str = self.root.get('width')
        height_str = self.root.get('height')
        
        # Parse width
        if width_str:
            match = re.match(r'(\d+\.?\d*)([a-z]*)', width_str)
            if match:
                value, unit = match.groups()
                self.width = float(value)
                # Convert to pixels if needed
                if unit == 'mm':
                    self.width *= 3.7795275591  # 96 DPI / 25.4 mm per inch
                elif unit == 'cm':
                    self.width *= 37.795275591  # 96 DPI / 2.54 cm per inch
                elif unit == 'in':
                    self.width *= 96  # 96 DPI
        else:
            self.width = self.viewbox[2]  # Use viewBox width
        
        # Parse height
        if height_str:
            match = re.match(r'(\d+\.?\d*)([a-z]*)', height_str)
            if match:
                value, unit = match.groups()
                self.height = float(value)
                # Convert to pixels if needed
                if unit == 'mm':
                    self.height *= 3.7795275591  # 96 DPI / 25.4 mm per inch
                elif unit == 'cm':
                    self.height *= 37.795275591  # 96 DPI / 2.54 cm per inch
                elif unit == 'in':
                    self.height *= 96  # 96 DPI
        else:
            self.height = self.viewbox[3]  # Use viewBox height
    
    def get_viewbox(self):
        """Get the viewBox of the SVG document."""
        return self.viewbox
    
    def get_width(self):
        """Get the width of the SVG document."""
        return self.width
    
    def get_height(self):
        """Get the height of the SVG document."""
        return self.height
    
    def get_all_paths(self):
        """Get all path elements in the SVG document."""
        if self.root is None:
            return []
        
        # Find all path elements
        paths = self.root.findall(f".//{SVG_NS}path")
        
        # Also find all rectangles, circles, ellipses, lines, polylines, and polygons
        # and convert them to paths
        rects = self.root.findall(f".//{SVG_NS}rect")
        circles = self.root.findall(f".//{SVG_NS}circle")
        ellipses = self.root.findall(f".//{SVG_NS}ellipse")
        lines = self.root.findall(f".//{SVG_NS}line")
        polylines = self.root.findall(f".//{SVG_NS}polyline")
        polygons = self.root.findall(f".//{SVG_NS}polygon")
        
        # Convert shapes to paths
        for rect in rects:
            paths.append(self._rect_to_path(rect))
        
        for circle in circles:
            paths.append(self._circle_to_path(circle))
        
        for ellipse in ellipses:
            paths.append(self._ellipse_to_path(ellipse))
        
        for line in lines:
            paths.append(self._line_to_path(line))
        
        for polyline in polylines:
            paths.append(self._polyline_to_path(polyline))
        
        for polygon in polygons:
            paths.append(self._polygon_to_path(polygon))
        
        return paths
    
    def get_path_id(self, path):
        """Get the ID of a path element."""
        return path.get('id', '')
    
    def get_path_data(self, path):
        """Get the path data (d attribute) of a path element."""
        return path.get('d', '')
    
    def get_path_style(self, path):
        """Get the style attributes of a path element."""
        style_dict = {}
        
        # Get style attribute
        style_attr = path.get('style', '')
        if style_attr:
            # Parse style attribute
            style_items = style_attr.split(';')
            for item in style_items:
                if ':' in item:
                    key, value = item.split(':', 1)
                    style_dict[key.strip()] = value.strip()
        
        # Get individual style attributes
        for attr in ['stroke', 'stroke-width', 'stroke-opacity', 'fill', 'fill-opacity']:
            value = path.get(attr)
            if value is not None:
                style_dict[attr] = value
        
        return style_dict
    
    def _rect_to_path(self, rect):
        """Convert a rectangle element to a path element."""
        # Get rectangle attributes
        x = float(rect.get('x', 0))
        y = float(rect.get('y', 0))
        width = float(rect.get('width', 0))
        height = float(rect.get('height', 0))
        
        # Create path data
        d = f"M {x},{y} L {x+width},{y} L {x+width},{y+height} L {x},{y+height} Z"
        
        # Create path element
        path = ET.Element(f"{SVG_NS}path")
        path.set('d', d)
        
        # Copy attributes
        for attr, value in rect.attrib.items():
            if attr not in ['x', 'y', 'width', 'height']:
                path.set(attr, value)
        
        return path
    
    def _circle_to_path(self, circle):
        """Convert a circle element to a path element."""
        # Get circle attributes
        cx = float(circle.get('cx', 0))
        cy = float(circle.get('cy', 0))
        r = float(circle.get('r', 0))
        
        # Create path data using Bezier curves to approximate a circle
        # A circle can be approximated by 4 cubic Bezier curves
        # The control points are at a distance of r*kappa from the center
        kappa = 0.5522848  # 4*(sqrt(2)-1)/3
        
        d = (
            f"M {cx},{cy-r} "
            f"C {cx+r*kappa},{cy-r} {cx+r},{cy-r*kappa} {cx+r},{cy} "
            f"C {cx+r},{cy+r*kappa} {cx+r*kappa},{cy+r} {cx},{cy+r} "
            f"C {cx-r*kappa},{cy+r} {cx-r},{cy+r*kappa} {cx-r},{cy} "
            f"C {cx-r},{cy-r*kappa} {cx-r*kappa},{cy-r} {cx},{cy-r} Z"
        )
        
        # Create path element
        path = ET.Element(f"{SVG_NS}path")
        path.set('d', d)
        
        # Copy attributes
        for attr, value in circle.attrib.items():
            if attr not in ['cx', 'cy', 'r']:
                path.set(attr, value)
        
        return path
    
    def _ellipse_to_path(self, ellipse):
        """Convert an ellipse element to a path element."""
        # Get ellipse attributes
        cx = float(ellipse.get('cx', 0))
        cy = float(ellipse.get('cy', 0))
        rx = float(ellipse.get('rx', 0))
        ry = float(ellipse.get('ry', 0))
        
        # Create path data using Bezier curves to approximate an ellipse
        kappa = 0.5522848  # 4*(sqrt(2)-1)/3
        
        d = (
            f"M {cx},{cy-ry} "
            f"C {cx+rx*kappa},{cy-ry} {cx+rx},{cy-ry*kappa} {cx+rx},{cy} "
            f"C {cx+rx},{cy+ry*kappa} {cx+rx*kappa},{cy+ry} {cx},{cy+ry} "
            f"C {cx-rx*kappa},{cy+ry} {cx-rx},{cy+ry*kappa} {cx-rx},{cy} "
            f"C {cx-rx},{cy-ry*kappa} {cx-rx*kappa},{cy-ry} {cx},{cy-ry} Z"
        )
        
        # Create path element
        path = ET.Element(f"{SVG_NS}path")
        path.set('d', d)
        
        # Copy attributes
        for attr, value in ellipse.attrib.items():
            if attr not in ['cx', 'cy', 'rx', 'ry']:
                path.set(attr, value)
        
        return path
    
    def _line_to_path(self, line):
        """Convert a line element to a path element."""
        # Get line attributes
        x1 = float(line.get('x1', 0))
        y1 = float(line.get('y1', 0))
        x2 = float(line.get('x2', 0))
        y2 = float(line.get('y2', 0))
        
        # Create path data
        d = f"M {x1},{y1} L {x2},{y2}"
        
        # Create path element
        path = ET.Element(f"{SVG_NS}path")
        path.set('d', d)
        
        # Copy attributes
        for attr, value in line.attrib.items():
            if attr not in ['x1', 'y1', 'x2', 'y2']:
                path.set(attr, value)
        
        return path
    
    def _polyline_to_path(self, polyline):
        """Convert a polyline element to a path element."""
        # Get points
        points_str = polyline.get('points', '')
        if not points_str:
            return ET.Element(f"{SVG_NS}path")
        
        # Parse points
        points = []
        for point in points_str.split():
            if ',' in point:
                x, y = point.split(',')
                points.append((float(x), float(y)))
        
        if not points:
            return ET.Element(f"{SVG_NS}path")
        
        # Create path data
        d = f"M {points[0][0]},{points[0][1]}"
        for x, y in points[1:]:
            d += f" L {x},{y}"
        
        # Create path element
        path = ET.Element(f"{SVG_NS}path")
        path.set('d', d)
        
        # Copy attributes
        for attr, value in polyline.attrib.items():
            if attr != 'points':
                path.set(attr, value)
        
        return path
    
    def _polygon_to_path(self, polygon):
        """Convert a polygon element to a path element."""
        # Get points
        points_str = polygon.get('points', '')
        if not points_str:
            return ET.Element(f"{SVG_NS}path")
        
        # Parse points
        points = []
        for point in points_str.split():
            if ',' in point:
                x, y = point.split(',')
                points.append((float(x), float(y)))
        
        if not points:
            return ET.Element(f"{SVG_NS}path")
        
        # Create path data
        d = f"M {points[0][0]},{points[0][1]}"
        for x, y in points[1:]:
            d += f" L {x},{y}"
        d += " Z"  # Close the path
        
        # Create path element
        path = ET.Element(f"{SVG_NS}path")
        path.set('d', d)
        
        # Copy attributes
        for attr, value in polygon.attrib.items():
            if attr != 'points':
                path.set(attr, value)
        
        return path 
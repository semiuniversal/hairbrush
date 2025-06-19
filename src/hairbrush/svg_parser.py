"""
SVG parsing utilities for the hairbrush package.
"""

from lxml import etree
import re
import math
from typing import Dict, List, Tuple, Optional, Any, Union


class SVGParser:
    """Parser for SVG files that extracts paths by layer."""
    
    def __init__(self, svg_path):
        """
        Initialize the SVG parser.
        
        Args:
            svg_path (str): Path to the SVG file
        """
        self.svg_path = svg_path
        self.tree = None
        self.root = None
        self.namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
            'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'
        }
        self._load()
        self._parse_document_properties()
    
    def _load(self):
        """Load the SVG file."""
        self.tree = etree.parse(self.svg_path)
        self.root = self.tree.getroot()
    
    def _parse_document_properties(self):
        """Parse SVG document properties like width, height, and viewBox."""
        self.width = self.root.get('width')
        self.height = self.root.get('height')
        self.viewbox = self.root.get('viewBox')
        
        # Parse units from width and height
        self.width_value, self.width_unit = self._parse_dimension(self.width)
        self.height_value, self.height_unit = self._parse_dimension(self.height)
        
        # Parse viewBox
        if self.viewbox:
            parts = self.viewbox.split()
            if len(parts) == 4:
                self.min_x = float(parts[0])
                self.min_y = float(parts[1])
                self.vb_width = float(parts[2])
                self.vb_height = float(parts[3])
    
    def _parse_dimension(self, value: str) -> Tuple[float, str]:
        """
        Parse a dimension string into value and unit.
        
        Args:
            value: Dimension string like "210mm" or "100px"
            
        Returns:
            Tuple of (numeric_value, unit)
        """
        if not value:
            return 0, ""
            
        match = re.match(r'([0-9.]+)([a-z%]+)?', value)
        if match:
            number = float(match.group(1))
            unit = match.group(2) if match.group(2) else ""
            return number, unit
        return 0, ""
    
    def get_document_info(self) -> Dict[str, Any]:
        """
        Get SVG document information.
        
        Returns:
            Dictionary with document properties
        """
        return {
            'width': self.width,
            'height': self.height,
            'viewBox': self.viewbox,
            'width_value': self.width_value,
            'width_unit': self.width_unit,
            'height_value': self.height_value,
            'height_unit': self.height_unit
        }
    
    def get_layers(self):
        """
        Get all layers in the SVG.
        
        Returns:
            list: List of layer elements
        """
        # Find all group elements that might be layers
        groups = self.root.findall(".//svg:g", namespaces=self.namespaces)
        
        # Filter for those that have a label attribute or inkscape:label
        layers = []
        for group in groups:
            label = group.get("label") or group.get("{{{0}}}label".format(self.namespaces['inkscape']))
            if label:
                layers.append((group, label))
        
        return layers
    
    def get_paths_by_layer(self, layer_name):
        """
        Get all paths in a specific layer.
        
        Args:
            layer_name (str): Name of the layer
            
        Returns:
            list: List of path elements
        """
        layers = self.get_layers()
        
        for layer, label in layers:
            if label == layer_name:
                return layer.findall(".//svg:path", namespaces=self.namespaces)
        
        return []
    
    def get_all_paths(self):
        """
        Get all paths in the SVG regardless of layer.
        
        Returns:
            list: List of path elements
        """
        return self.root.findall(".//svg:path", namespaces=self.namespaces)
    
    def get_path_data(self, path_element):
        """
        Get the path data from a path element.
        
        Args:
            path_element: The path element
            
        Returns:
            str: The path data
        """
        return path_element.get("d")
    
    def get_path_style(self, path_element):
        """
        Get the style attributes from a path element.
        
        Args:
            path_element: The path element
            
        Returns:
            dict: Dictionary of style attributes
        """
        style_str = path_element.get("style", "")
        style_dict = {}
        
        if style_str:
            style_items = style_str.split(";")
            for item in style_items:
                if ":" in item:
                    key, value = item.split(":", 1)
                    style_dict[key.strip()] = value.strip()
        
        # Also check for direct attributes
        for attr in ['fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin', 'stroke-opacity']:
            if path_element.get(attr):
                style_dict[attr] = path_element.get(attr)
        
        return style_dict
    
    def get_path_id(self, path_element) -> str:
        """
        Get the ID of a path element.
        
        Args:
            path_element: The path element
            
        Returns:
            str: The path ID or empty string if not found
        """
        return path_element.get("id", "")
    
    def get_path_bounds(self, path_element) -> Tuple[float, float, float, float]:
        """
        Calculate the bounding box of a path.
        This is a simple implementation that works for basic paths.
        For complex paths with curves, a more sophisticated algorithm would be needed.
        
        Args:
            path_element: The path element
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        path_data = self.get_path_data(path_element)
        if not path_data:
            return (0, 0, 0, 0)
            
        # Extract all numeric values from the path data
        numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', path_data)
        if not numbers:
            return (0, 0, 0, 0)
            
        # Convert to floats
        numbers = [float(n) for n in numbers]
        
        # Group into x,y pairs (this is a simplification)
        points = []
        for i in range(0, len(numbers) - 1, 2):
            if i + 1 < len(numbers):
                points.append((numbers[i], numbers[i + 1]))
        
        if not points:
            return (0, 0, 0, 0)
            
        # Find min/max
        min_x = min(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)
        
        return (min_x, min_y, max_x, max_y)
    
    def analyze_svg(self) -> Dict[str, Any]:
        """
        Analyze the SVG file and return information about its structure.
        
        Returns:
            Dictionary with SVG analysis information
        """
        layers = self.get_layers()
        all_paths = self.get_all_paths()
        
        layer_info = []
        for layer, label in layers:
            paths = layer.findall(".//svg:path", namespaces=self.namespaces)
            layer_info.append({
                'name': label,
                'path_count': len(paths)
            })
        
        # Get overall bounds
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        
        for path in all_paths:
            path_min_x, path_min_y, path_max_x, path_max_y = self.get_path_bounds(path)
            min_x = min(min_x, path_min_x)
            min_y = min(min_y, path_min_y)
            max_x = max(max_x, path_max_x)
            max_y = max(max_y, path_max_y)
        
        # If no paths were found, use default values
        if min_x == float('inf'):
            min_x, min_y = 0, 0
            max_x, max_y = 0, 0
        
        return {
            'document_info': self.get_document_info(),
            'layer_count': len(layers),
            'layers': layer_info,
            'total_paths': len(all_paths),
            'bounds': {
                'min_x': min_x,
                'min_y': min_y,
                'max_x': max_x,
                'max_y': max_y,
                'width': max_x - min_x,
                'height': max_y - min_y
            }
        } 
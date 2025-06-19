"""
SVG parsing utilities for the hairbrush package.
"""

from lxml import etree


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
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
        }
        self._load()
    
    def _load(self):
        """Load the SVG file."""
        self.tree = etree.parse(self.svg_path)
        self.root = self.tree.getroot()
    
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
        
        return style_dict 
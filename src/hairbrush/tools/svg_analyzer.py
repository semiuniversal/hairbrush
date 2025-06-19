#!/usr/bin/env python3
"""
SVG Analyzer Tool - Analyzes SVG files for use with the hairbrush package.

This tool provides detailed information about an SVG file, including:
- Document properties (width, height, viewBox)
- Layer structure
- Path information
- Color usage
- Bounding boxes

Usage:
    python -m hairbrush.tools.svg_analyzer path/to/file.svg
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for direct script execution
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from hairbrush.svg_parser import SVGParser
except ImportError:
    print("Error: Could not import hairbrush.svg_parser. Make sure the hairbrush package is installed or in your Python path.")
    sys.exit(1)


def analyze_svg(svg_path: str, output_format: str = "text") -> Dict[str, Any]:
    """
    Analyze an SVG file and return information about its structure.
    
    Args:
        svg_path: Path to the SVG file
        output_format: Format for output ("text", "json")
        
    Returns:
        Dictionary with analysis information
    """
    try:
        parser = SVGParser(svg_path)
        analysis = parser.analyze_svg()
        
        # Add additional path information
        paths_info = []
        all_paths = parser.get_all_paths()
        
        for i, path in enumerate(all_paths):
            path_id = parser.get_path_id(path)
            path_style = parser.get_path_style(path)
            path_bounds = parser.get_path_bounds(path)
            
            # Extract color information
            fill = path_style.get('fill', 'none')
            stroke = path_style.get('stroke', 'none')
            stroke_width = path_style.get('stroke-width', '0')
            
            paths_info.append({
                'index': i,
                'id': path_id,
                'fill': fill,
                'stroke': stroke,
                'stroke_width': stroke_width,
                'bounds': {
                    'min_x': path_bounds[0],
                    'min_y': path_bounds[1],
                    'max_x': path_bounds[2],
                    'max_y': path_bounds[3],
                    'width': path_bounds[2] - path_bounds[0],
                    'height': path_bounds[3] - path_bounds[1]
                }
            })
        
        analysis['paths'] = paths_info
        return analysis
    except Exception as e:
        print(f"Error analyzing SVG: {str(e)}")
        return {
            "error": str(e),
            "document_info": {},
            "layer_count": 0,
            "layers": [],
            "total_paths": 0,
            "bounds": {"min_x": 0, "min_y": 0, "max_x": 0, "max_y": 0, "width": 0, "height": 0},
            "paths": []
        }


def format_output(analysis: Dict[str, Any], output_format: str) -> str:
    """
    Format the analysis output.
    
    Args:
        analysis: Analysis dictionary
        output_format: Format for output ("text", "json")
        
    Returns:
        Formatted output string
    """
    if output_format == "json":
        return json.dumps(analysis, indent=2)
    
    # Text format
    output = []
    output.append("SVG Analysis Report")
    output.append("=================")
    output.append("")
    
    # Check for error
    if "error" in analysis and analysis["error"]:
        output.append(f"Error: {analysis['error']}")
        return "\n".join(output)
    
    # Document info
    doc_info = analysis['document_info']
    output.append(f"Document Properties:")
    output.append(f"  Width: {doc_info['width']}")
    output.append(f"  Height: {doc_info['height']}")
    output.append(f"  ViewBox: {doc_info['viewBox']}")
    output.append("")
    
    # Layers
    output.append(f"Layers: {analysis['layer_count']}")
    for i, layer in enumerate(analysis['layers']):
        output.append(f"  {i+1}. {layer['name']} - {layer['path_count']} paths")
    output.append("")
    
    # Bounds
    bounds = analysis['bounds']
    output.append(f"Document Bounds:")
    output.append(f"  Min X: {bounds['min_x']:.2f}, Min Y: {bounds['min_y']:.2f}")
    output.append(f"  Max X: {bounds['max_x']:.2f}, Max Y: {bounds['max_y']:.2f}")
    output.append(f"  Width: {bounds['width']:.2f}, Height: {bounds['height']:.2f}")
    output.append("")
    
    # Paths
    output.append(f"Paths: {analysis['total_paths']}")
    for i, path in enumerate(analysis['paths']):
        if i < 10:  # Limit to first 10 paths to avoid excessive output
            output.append(f"  Path {i+1}" + (f" (id: {path['id']})" if path['id'] else ""))
            output.append(f"    Fill: {path['fill']}, Stroke: {path['stroke']}, Width: {path['stroke_width']}")
            b = path['bounds']
            output.append(f"    Bounds: ({b['min_x']:.1f}, {b['min_y']:.1f}) to ({b['max_x']:.1f}, {b['max_y']:.1f})")
        elif i == 10:
            output.append(f"  ... and {analysis['total_paths'] - 10} more paths")
            break
    
    return "\n".join(output)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Analyze SVG files for use with the hairbrush package")
    parser.add_argument("svg_file", help="Path to the SVG file to analyze")
    parser.add_argument("--format", choices=["text", "json"], default="text", 
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()
    
    try:
        analysis = analyze_svg(args.svg_file, args.format)
        output = format_output(analysis, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Analysis written to {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error analyzing SVG: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 
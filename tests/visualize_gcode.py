#!/usr/bin/env python3
"""
Visualize G-code output for debugging.

This script reads a G-code file and generates an SVG visualization of the tool path.
It helps to debug the SVG to G-code conversion process.

Usage:
    python visualize_gcode.py <gcode_file> [--output <output_file>]
"""

import sys
import os
import argparse
import re
from pathlib import Path
import math
import xml.etree.ElementTree as ET


def parse_gcode(gcode_file):
    """
    Parse G-code file and extract movement commands.
    
    Args:
        gcode_file: Path to the G-code file
        
    Returns:
        list: List of (x, y, z, command_type, tool, paint_flow) tuples
    """
    movements = []
    current_x, current_y, current_z = 0, 0, 0
    current_tool = 0  # Default to tool 0 (black)
    current_paint_flow = 1.0  # Default to full flow
    
    try:
        with open(gcode_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check for tool change
                if line.startswith('T'):
                    tool_match = re.search(r'T(\d+)', line)
                    if tool_match:
                        current_tool = int(tool_match.group(1))
                    continue
                
                # Check for paint flow comment
                if '; PAINT_FLOW:' in line:
                    flow_match = re.search(r'; PAINT_FLOW:([\d.]+)', line)
                    if flow_match:
                        current_paint_flow = float(flow_match.group(1))
                    continue
                
                # Skip other comments
                if line.startswith(';'):
                    continue
                
                # Parse G0/G1 movement commands
                if line.startswith('G0') or line.startswith('G1'):
                    command_type = 'rapid' if line.startswith('G0') else 'linear'
                    
                    # Extract X, Y, Z coordinates
                    x_match = re.search(r'X([-+]?\d*\.?\d+)', line)
                    y_match = re.search(r'Y([-+]?\d*\.?\d+)', line)
                    z_match = re.search(r'Z([-+]?\d*\.?\d+)', line)
                    
                    if x_match:
                        current_x = float(x_match.group(1))
                    if y_match:
                        current_y = float(y_match.group(1))
                    if z_match:
                        current_z = float(z_match.group(1))
                    
                    movements.append((current_x, current_y, current_z, command_type, current_tool, current_paint_flow))
    
    except Exception as e:
        print(f"Error parsing G-code file: {str(e)}")
        return []
    
    return movements


def create_svg_visualization(movements, output_file, width=800, height=600, margin=20):
    """
    Create an SVG visualization of the G-code movements.
    
    Args:
        movements: List of (x, y, z, command_type, tool, paint_flow) tuples
        output_file: Path to the output SVG file
        width: Width of the SVG
        height: Height of the SVG
        margin: Margin around the visualization
    """
    if not movements:
        print("No movements to visualize")
        return False
    
    # Find bounds of the movements
    min_x = min(m[0] for m in movements)
    max_x = max(m[0] for m in movements)
    min_y = min(m[1] for m in movements)
    max_y = max(m[1] for m in movements)
    min_z = min(m[2] for m in movements)
    max_z = max(m[2] for m in movements)
    
    # Calculate scaling factors
    data_width = max_x - min_x
    data_height = max_y - min_y
    
    if data_width == 0 or data_height == 0:
        print("Warning: Zero width or height in data")
        data_width = data_width or 1
        data_height = data_height or 1
    
    scale_x = (width - 2 * margin) / data_width
    scale_y = (height - 2 * margin) / data_height
    scale = min(scale_x, scale_y)
    
    # Create SVG root element
    svg = ET.Element('svg', {
        'width': str(width),
        'height': str(height),
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f"0 0 {width} {height}"
    })
    
    # Add a white background
    ET.SubElement(svg, 'rect', {
        'width': str(width),
        'height': str(height),
        'fill': 'white'
    })
    
    # Add a grid
    grid_group = ET.SubElement(svg, 'g', {
        'stroke': '#ddd',
        'stroke-width': '0.5'
    })
    
    grid_size = 10
    for i in range(0, width, grid_size):
        ET.SubElement(grid_group, 'line', {
            'x1': str(i),
            'y1': '0',
            'x2': str(i),
            'y2': str(height)
        })
    
    for i in range(0, height, grid_size):
        ET.SubElement(grid_group, 'line', {
            'x1': '0',
            'y1': str(i),
            'x2': str(width),
            'y2': str(i)
        })
    
    # Create a group for the tool paths
    paths_group = ET.SubElement(svg, 'g', {
        'transform': f"translate({margin}, {margin}) scale({scale})"
    })
    
    # Add a transform to adjust for the data bounds and flip Y axis (SVG Y is down)
    transform = f"translate({-min_x}, {-min_y}) scale(1, -1) translate(0, {-data_height})"
    paths_group.set('transform', f"translate({margin}, {margin}) scale({scale}) {transform}")
    
    # Group movements by tool, command type, and Z height
    path_groups = {}
    
    for i, (x, y, z, cmd_type, tool, paint_flow) in enumerate(movements):
        # Create a key for this type of movement
        key = (cmd_type, tool, round(z, 1))
        
        if key not in path_groups:
            path_groups[key] = []
        
        # Add this point to the appropriate group
        path_groups[key].append((x, y, z, paint_flow))
    
    # Create paths for each group
    for (cmd_type, tool, z), points in path_groups.items():
        # Skip if no points
        if not points:
            continue
        
        # Determine color based on tool and Z height
        if cmd_type == 'rapid':
            # Rapid movements are always dashed blue
            stroke = 'blue'
            stroke_dasharray = '2,1'
            stroke_width = '0.5'
            stroke_opacity = '0.7'
        else:
            # Linear movements color based on tool
            if tool == 0:  # Tool 0 (black)
                stroke = '#000000'  # Black
            else:  # Tool 1 (white)
                stroke = '#888888'  # Gray (to represent white on white background)
            
            # Adjust opacity based on Z height
            z_range = max_z - min_z
            if z_range > 0:
                # Higher Z = more transparent
                z_factor = 1 - ((z - min_z) / z_range) * 0.7
            else:
                z_factor = 1
            
            stroke_opacity = str(max(0.3, z_factor))
            stroke_width = str(1 + (z - min_z) * 0.3)  # Thicker lines for higher Z
            stroke_dasharray = 'none'
        
        # Create path data
        path_data = ""
        current_segment = []
        
        for x, y, z, paint_flow in points:
            if not current_segment:
                # Start a new segment
                current_segment.append((x, y))
                path_data += f"M {x} {y} "
            else:
                # Continue the segment
                current_segment.append((x, y))
                path_data += f"L {x} {y} "
        
        # Add the path
        ET.SubElement(paths_group, 'path', {
            'd': path_data,
            'fill': 'none',
            'stroke': stroke,
            'stroke-width': stroke_width,
            'stroke-dasharray': stroke_dasharray,
            'stroke-opacity': stroke_opacity
        })
    
    # Add markers for the start and end points
    if movements:
        start_x, start_y = movements[0][0], movements[0][1]
        end_x, end_y = movements[-1][0], movements[-1][1]
        
        # Start point (green circle)
        ET.SubElement(paths_group, 'circle', {
            'cx': str(start_x),
            'cy': str(start_y),
            'r': '1',
            'fill': 'green'
        })
        
        # End point (red circle)
        ET.SubElement(paths_group, 'circle', {
            'cx': str(end_x),
            'cy': str(end_y),
            'r': '1',
            'fill': 'red'
        })
    
    # Add a legend
    legend_group = ET.SubElement(svg, 'g', {
        'transform': f"translate({width - 180}, 20)"
    })
    
    # Title
    ET.SubElement(legend_group, 'text', {
        'x': '0',
        'y': '15',
        'font-size': '14',
        'font-weight': 'bold'
    }).text = 'Legend'
    
    # Rapid movement
    ET.SubElement(legend_group, 'line', {
        'x1': '0',
        'y1': '30',
        'x2': '30',
        'y2': '30',
        'stroke': 'blue',
        'stroke-width': '1',
        'stroke-dasharray': '2,1'
    })
    ET.SubElement(legend_group, 'text', {
        'x': '35',
        'y': '35',
        'font-size': '12'
    }).text = 'Rapid (G0)'
    
    # Tool 0 (Black)
    ET.SubElement(legend_group, 'line', {
        'x1': '0',
        'y1': '50',
        'x2': '30',
        'y2': '50',
        'stroke': '#000000',
        'stroke-width': '1'
    })
    ET.SubElement(legend_group, 'text', {
        'x': '35',
        'y': '55',
        'font-size': '12'
    }).text = 'Tool 0 (Black)'
    
    # Tool 1 (White)
    ET.SubElement(legend_group, 'line', {
        'x1': '0',
        'y1': '70',
        'x2': '30',
        'y2': '70',
        'stroke': '#888888',
        'stroke-width': '1'
    })
    ET.SubElement(legend_group, 'text', {
        'x': '35',
        'y': '75',
        'font-size': '12'
    }).text = 'Tool 1 (White)'
    
    # Z-Height
    ET.SubElement(legend_group, 'text', {
        'x': '0',
        'y': '95',
        'font-size': '12'
    }).text = 'Z-Height:'
    
    # Z-Height indicators
    z_levels = 3
    for i in range(z_levels):
        z_factor = i / (z_levels - 1)
        z_value = min_z + z_factor * (max_z - min_z)
        opacity = max(0.3, 1 - z_factor * 0.7)
        width = 1 + z_factor * 0.3
        
        ET.SubElement(legend_group, 'line', {
            'x1': '0',
            'y1': str(110 + i * 20),
            'x2': '30',
            'y2': str(110 + i * 20),
            'stroke': '#000000',
            'stroke-width': str(width),
            'stroke-opacity': str(opacity)
        })
        ET.SubElement(legend_group, 'text', {
            'x': '35',
            'y': str(115 + i * 20),
            'font-size': '12'
        }).text = f'Z = {z_value:.1f}mm'
    
    # Start point
    ET.SubElement(legend_group, 'circle', {
        'cx': '15',
        'cy': '170',
        'r': '3',
        'fill': 'green'
    })
    ET.SubElement(legend_group, 'text', {
        'x': '35',
        'y': '175',
        'font-size': '12'
    }).text = 'Start'
    
    # End point
    ET.SubElement(legend_group, 'circle', {
        'cx': '15',
        'cy': '190',
        'r': '3',
        'fill': 'red'
    })
    ET.SubElement(legend_group, 'text', {
        'x': '35',
        'y': '195',
        'font-size': '12'
    }).text = 'End'
    
    # Write the SVG to file
    tree = ET.ElementTree(svg)
    try:
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"SVG visualization written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing SVG file: {str(e)}")
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Visualize G-code as SVG")
    parser.add_argument("gcode_file", help="Path to the G-code file")
    parser.add_argument("--output", "-o", help="Output SVG file (default: <gcode_name>.svg)")
    parser.add_argument("--width", type=int, default=800, help="Width of the SVG (default: 800)")
    parser.add_argument("--height", type=int, default=600, help="Height of the SVG (default: 600)")
    parser.add_argument("--margin", type=int, default=20, help="Margin around the visualization (default: 20)")
    args = parser.parse_args()
    
    # Check if the G-code file exists
    if not os.path.exists(args.gcode_file):
        print(f"Error: File '{args.gcode_file}' not found.")
        sys.exit(1)
    
    # Parse the G-code file
    movements = parse_gcode(args.gcode_file)
    if not movements:
        print("No movements found in the G-code file.")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        gcode_name = os.path.splitext(os.path.basename(args.gcode_file))[0]
        output_file = f"{gcode_name}.svg"
    
    # Create the SVG visualization
    if not create_svg_visualization(movements, output_file, args.width, args.height, args.margin):
        print("Error: Failed to create SVG visualization.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
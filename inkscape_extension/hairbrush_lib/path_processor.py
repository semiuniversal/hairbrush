#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Processor for the H.Airbrush extension

This module handles processing SVG paths and converting them to G-code for the H.Airbrush extension.
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
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Union
from enum import Enum, auto

# Setup logging
log_file = os.path.join(tempfile.gettempdir(), 'hairbrush_debug.log')
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file)
logger = logging.getLogger('hairbrush_path_processor')

class PathCommand(Enum):
    """Enum for SVG path commands."""
    MOVE_TO = auto()          # M, m
    LINE_TO = auto()          # L, l
    HORIZONTAL_LINE = auto()  # H, h
    VERTICAL_LINE = auto()    # V, v
    CUBIC_BEZIER = auto()     # C, c
    SMOOTH_CUBIC = auto()     # S, s
    QUADRATIC_BEZIER = auto() # Q, q
    SMOOTH_QUADRATIC = auto() # T, t
    ARC = auto()              # A, a
    CLOSE_PATH = auto()       # Z, z


class PathSegment:
    """Represents a segment of an SVG path."""
    
    def __init__(self, command: PathCommand, params: List[float], absolute: bool = True):
        """
        Initialize a path segment.
        
        Args:
            command: The path command type
            params: List of parameters for the command
            absolute: Whether the command uses absolute coordinates
        """
        self.command = command
        self.params = params
        self.absolute = absolute
    
    def to_absolute(self, current_x: float, current_y: float) -> 'PathSegment':
        """
        Convert the segment to use absolute coordinates.
        
        Args:
            current_x: Current X position
            current_y: Current Y position
            
        Returns:
            A new PathSegment with absolute coordinates
        """
        if self.absolute:
            return self
        
        # Create a copy with absolute coordinates
        new_params = self.params.copy()
        
        if self.command == PathCommand.MOVE_TO or self.command == PathCommand.LINE_TO:
            # Convert pairs of coordinates
            for i in range(0, len(new_params), 2):
                if i + 1 < len(new_params):
                    new_params[i] += current_x
                    new_params[i + 1] += current_y
                    current_x, current_y = new_params[i], new_params[i + 1]
        
        elif self.command == PathCommand.HORIZONTAL_LINE:
            # Convert x coordinates
            for i in range(len(new_params)):
                new_params[i] += current_x
                current_x = new_params[i]
        
        elif self.command == PathCommand.VERTICAL_LINE:
            # Convert y coordinates
            for i in range(len(new_params)):
                new_params[i] += current_y
                current_y = new_params[i]
        
        elif self.command == PathCommand.CUBIC_BEZIER:
            # Convert three points (control1, control2, end)
            for i in range(0, len(new_params), 6):
                if i + 5 < len(new_params):
                    new_params[i] += current_x      # c1x
                    new_params[i + 1] += current_y  # c1y
                    new_params[i + 2] += current_x  # c2x
                    new_params[i + 3] += current_y  # c2y
                    new_params[i + 4] += current_x  # x
                    new_params[i + 5] += current_y  # y
                    current_x, current_y = new_params[i + 4], new_params[i + 5]
        
        elif self.command == PathCommand.SMOOTH_CUBIC:
            # Convert two points (control2, end)
            for i in range(0, len(new_params), 4):
                if i + 3 < len(new_params):
                    new_params[i] += current_x      # c2x
                    new_params[i + 1] += current_y  # c2y
                    new_params[i + 2] += current_x  # x
                    new_params[i + 3] += current_y  # y
                    current_x, current_y = new_params[i + 2], new_params[i + 3]
        
        elif self.command == PathCommand.QUADRATIC_BEZIER:
            # Convert two points (control, end)
            for i in range(0, len(new_params), 4):
                if i + 3 < len(new_params):
                    new_params[i] += current_x      # cx
                    new_params[i + 1] += current_y  # cy
                    new_params[i + 2] += current_x  # x
                    new_params[i + 3] += current_y  # y
                    current_x, current_y = new_params[i + 2], new_params[i + 3]
        
        elif self.command == PathCommand.SMOOTH_QUADRATIC:
            # Convert one point (end)
            for i in range(0, len(new_params), 2):
                if i + 1 < len(new_params):
                    new_params[i] += current_x      # x
                    new_params[i + 1] += current_y  # y
                    current_x, current_y = new_params[i], new_params[i + 1]
        
        elif self.command == PathCommand.ARC:
            # Convert one point (end) - first 5 params are unchanged
            for i in range(0, len(new_params), 7):
                if i + 6 < len(new_params):
                    new_params[i + 5] += current_x  # x
                    new_params[i + 6] += current_y  # y
                    current_x, current_y = new_params[i + 5], new_params[i + 6]
        
        # CLOSE_PATH has no parameters to convert
        
        return PathSegment(self.command, new_params, True)
    
    def get_end_point(self, current_x: float, current_y: float) -> Tuple[float, float]:
        """
        Get the end point of this path segment.
        
        Args:
            current_x: Current X position
            current_y: Current Y position
            
        Returns:
            Tuple of (end_x, end_y)
        """
        # If already absolute, use the params directly
        if self.absolute:
            if self.command == PathCommand.MOVE_TO or self.command == PathCommand.LINE_TO:
                if len(self.params) >= 2:
                    return self.params[-2], self.params[-1]
            
            elif self.command == PathCommand.HORIZONTAL_LINE:
                if self.params:
                    return self.params[-1], current_y
            
            elif self.command == PathCommand.VERTICAL_LINE:
                if self.params:
                    return current_x, self.params[-1]
            
            elif self.command in [PathCommand.CUBIC_BEZIER, PathCommand.SMOOTH_CUBIC]:
                if len(self.params) >= 4:
                    return self.params[-2], self.params[-1]
            
            elif self.command in [PathCommand.QUADRATIC_BEZIER, PathCommand.SMOOTH_QUADRATIC]:
                if len(self.params) >= 2:
                    return self.params[-2], self.params[-1]
            
            elif self.command == PathCommand.ARC:
                if len(self.params) >= 7:
                    return self.params[5], self.params[6]
        
        # For relative commands or if we couldn't determine the end point
        # Convert to absolute first
        abs_segment = self.to_absolute(current_x, current_y)
        return abs_segment.get_end_point(current_x, current_y)


class ProcessedPath:
    """
    Class representing a processed path ready for G-code generation
    """
    
    def __init__(self, path_id=None, points=None, style=None, layer=None):
        """Initialize the processed path"""
        self.id = path_id
        self.points = points or []
        self.style = style or {}
        self.layer = layer
        self.brush = None
        self.height = None
        self.opacity = None
        
        # Process style attributes to determine brush, height, and opacity
        self._process_style()
    
    def _process_style(self):
        """Process style attributes to determine brush, height, and opacity"""
        try:
            # Determine brush based on stroke color
            stroke = self.style.get('stroke', '#000000').lower()
            if stroke in ['none', 'transparent']:
                self.brush = None
            elif stroke in ['#000000', '#000', 'black']:
                self.brush = 'A'
            elif stroke in ['#ffffff', '#fff', 'white']:
                self.brush = 'B'
            else:
                # Default to brush A for any other color
                self.brush = 'A'
            
            # Determine height based on stroke width
            stroke_width = self.style.get('stroke-width', '1')
            try:
                self.height = float(stroke_width)
            except (ValueError, TypeError):
                self.height = 1.0
            
            # Normalize height to 0-100 range (assuming max stroke width of 10)
            self.height = min(100, max(0, self.height * 10))
            
            # Determine opacity
            opacity = self.style.get('opacity', '1')
            stroke_opacity = self.style.get('stroke-opacity', '1')
            try:
                self.opacity = float(opacity) * float(stroke_opacity)
            except (ValueError, TypeError):
                self.opacity = 1.0
            
            # Normalize opacity to 0-100 range
            self.opacity = min(100, max(0, self.opacity * 100))
            
            logger.debug(f"Processed style: brush={self.brush}, height={self.height}, opacity={self.opacity}")
        except Exception as e:
            logger.error(f"Error processing style: {str(e)}", exc_info=True)

class PathProcessor:
    """
    Class for processing SVG paths and converting them to G-code
    """
    
    def __init__(self, curve_tolerance=1.0, path_handling=1):
        """Initialize the path processor"""
        self.curve_tolerance = curve_tolerance
        self.path_handling = path_handling
    
    def process_paths(self, paths):
        """Process a list of SVG paths"""
        try:
            processed_paths = []
            
            for path in paths:
                processed_path = self.process_path(path)
                if processed_path:
                    processed_paths.append(processed_path)
            
            logger.info(f"Processed {len(processed_paths)} paths")
            return processed_paths
        except Exception as e:
            logger.error(f"Error processing paths: {str(e)}", exc_info=True)
            return []
    
    def process_path(self, path):
        """Process an SVG path"""
        try:
            # Skip paths with no commands
            if not path.commands:
                logger.warning(f"Path {path.id} has no commands")
                return None
            
            # Convert path commands to points
            points = self._commands_to_points(path.commands)
            
            # Apply path handling based on the setting
            if self.path_handling == 1:  # Adaptive
                points = self._adaptive_simplify(points)
            elif self.path_handling == 2:  # Raw
                pass  # Use points as is
            elif self.path_handling == 3:  # Simplified
                points = self._simplify_path(points)
            
            # Create and return the processed path
            return ProcessedPath(
                path_id=path.id,
                points=points,
                style=path.style,
                layer=path.layer
            )
        except Exception as e:
            logger.error(f"Error processing path {path.id}: {str(e)}", exc_info=True)
            return None
    
    def _commands_to_points(self, commands):
        """Convert path commands to a list of points"""
        try:
            points = []
            current_point = (0, 0)
            
            for cmd in commands:
                cmd_type = cmd.letter
                params = cmd.args
                
                if cmd_type == 'M':  # Move to
                    current_point = (params[0], params[1])
                    points.append(current_point)
                
                elif cmd_type == 'L':  # Line to
                    current_point = (params[0], params[1])
                    points.append(current_point)
                
                elif cmd_type == 'H':  # Horizontal line
                    current_point = (params[0], current_point[1])
                    points.append(current_point)
                
                elif cmd_type == 'V':  # Vertical line
                    current_point = (current_point[0], params[0])
                    points.append(current_point)
                
                elif cmd_type == 'C':  # Cubic Bezier
                    # Convert cubic Bezier to points
                    start = current_point
                    c1 = (params[0], params[1])
                    c2 = (params[2], params[3])
                    end = (params[4], params[5])
                    
                    # Generate points along the curve
                    curve_points = self._cubic_bezier_to_points(start, c1, c2, end)
                    points.extend(curve_points)
                    
                    current_point = end
                
                elif cmd_type == 'S':  # Smooth cubic Bezier
                    # Calculate the first control point as reflection of the previous control point
                    if points and len(points) >= 2:
                        prev_c2 = points[-2]
                        c1 = (2 * current_point[0] - prev_c2[0], 2 * current_point[1] - prev_c2[1])
                    else:
                        c1 = current_point
                    
                    c2 = (params[0], params[1])
                    end = (params[2], params[3])
                    
                    # Generate points along the curve
                    curve_points = self._cubic_bezier_to_points(current_point, c1, c2, end)
                    points.extend(curve_points)
                    
                    current_point = end
                
                elif cmd_type == 'Q':  # Quadratic Bezier
                    # Convert quadratic Bezier to points
                    start = current_point
                    c = (params[0], params[1])
                    end = (params[2], params[3])
                    
                    # Generate points along the curve
                    curve_points = self._quadratic_bezier_to_points(start, c, end)
                    points.extend(curve_points)
                    
                    current_point = end
                
                elif cmd_type == 'T':  # Smooth quadratic Bezier
                    # Calculate the control point as reflection of the previous control point
                    if points and len(points) >= 2:
                        prev_c = points[-2]
                        c = (2 * current_point[0] - prev_c[0], 2 * current_point[1] - prev_c[1])
                    else:
                        c = current_point
                    
                    end = (params[0], params[1])
                    
                    # Generate points along the curve
                    curve_points = self._quadratic_bezier_to_points(current_point, c, end)
                    points.extend(curve_points)
                    
                    current_point = end
                
                elif cmd_type == 'A':  # Arc
                    # Convert arc to points
                    start = current_point
                    rx, ry = params[0], params[1]
                    x_axis_rotation = params[2]
                    large_arc_flag = params[3]
                    sweep_flag = params[4]
                    end = (params[5], params[6])
                    
                    # Generate points along the arc
                    arc_points = self._arc_to_points(start, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, end)
                    points.extend(arc_points)
                    
                    current_point = end
                
                elif cmd_type == 'Z':  # Close path
                    # Add the first point to close the path if needed
                    if points and points[0] != current_point:
                        points.append(points[0])
                    
                    current_point = points[0] if points else (0, 0)
            
            return points
        except Exception as e:
            logger.error(f"Error converting commands to points: {str(e)}", exc_info=True)
            return []
    
    def _cubic_bezier_to_points(self, start, c1, c2, end):
        """Convert a cubic Bezier curve to a list of points"""
        try:
            points = []
            
            # Number of segments based on curve length and tolerance
            # Estimate the curve length as the sum of the control polygon segments
            length = (
                math.sqrt((c1[0] - start[0])**2 + (c1[1] - start[1])**2) +
                math.sqrt((c2[0] - c1[0])**2 + (c2[1] - c1[1])**2) +
                math.sqrt((end[0] - c2[0])**2 + (end[1] - c2[1])**2)
            )
            
            # Calculate number of segments based on length and tolerance
            num_segments = max(2, int(length / self.curve_tolerance))
            
            # Generate points along the curve
            for i in range(num_segments + 1):
                t = i / num_segments
                
                # Cubic Bezier formula
                x = (1-t)**3 * start[0] + 3*(1-t)**2 * t * c1[0] + 3*(1-t) * t**2 * c2[0] + t**3 * end[0]
                y = (1-t)**3 * start[1] + 3*(1-t)**2 * t * c1[1] + 3*(1-t) * t**2 * c2[1] + t**3 * end[1]
                
                points.append((x, y))
            
            return points
        except Exception as e:
            logger.error(f"Error converting cubic Bezier to points: {str(e)}", exc_info=True)
            return []
    
    def _quadratic_bezier_to_points(self, start, c, end):
        """Convert a quadratic Bezier curve to a list of points"""
        try:
            points = []
            
            # Number of segments based on curve length and tolerance
            # Estimate the curve length as the sum of the control polygon segments
            length = (
                math.sqrt((c[0] - start[0])**2 + (c[1] - start[1])**2) +
                math.sqrt((end[0] - c[0])**2 + (end[1] - c[1])**2)
            )
            
            # Calculate number of segments based on length and tolerance
            num_segments = max(2, int(length / self.curve_tolerance))
            
            # Generate points along the curve
            for i in range(num_segments + 1):
                t = i / num_segments
                
                # Quadratic Bezier formula
                x = (1-t)**2 * start[0] + 2*(1-t) * t * c[0] + t**2 * end[0]
                y = (1-t)**2 * start[1] + 2*(1-t) * t * c[1] + t**2 * end[1]
                
                points.append((x, y))
            
            return points
        except Exception as e:
            logger.error(f"Error converting quadratic Bezier to points: {str(e)}", exc_info=True)
            return []
    
    def _arc_to_points(self, start, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, end):
        """Convert an arc to a list of points"""
        try:
            # Convert arc to cubic Bezier curves using inkex
            path = inkex.Path()
            path.append(inkex.paths.Move(start[0], start[1]))
            path.append(inkex.paths.Arc(
                rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, end[0], end[1]
            ))
            
            # Convert the path to a list of points
            points = []
            current_point = start
            
            for cmd in path[1:]:  # Skip the initial Move command
                cmd_type = cmd.letter
                params = cmd.args
                
                if cmd_type == 'C':  # Cubic Bezier
                    # Convert cubic Bezier to points
                    c1 = (params[0], params[1])
                    c2 = (params[2], params[3])
                    end = (params[4], params[5])
                    
                    # Generate points along the curve
                    curve_points = self._cubic_bezier_to_points(current_point, c1, c2, end)
                    points.extend(curve_points)
                    
                    current_point = end
            
            return points
        except Exception as e:
            logger.error(f"Error converting arc to points: {str(e)}", exc_info=True)
            
            # Fallback: approximate the arc with a straight line
            return [end]
    
    def _adaptive_simplify(self, points):
        """Adaptively simplify a path based on curvature"""
        try:
            if len(points) <= 2:
                return points
            
            # Use the Ramer-Douglas-Peucker algorithm with adaptive tolerance
            simplified = self._ramer_douglas_peucker(points, self.curve_tolerance)
            
            logger.debug(f"Adaptively simplified path from {len(points)} to {len(simplified)} points")
            return simplified
        except Exception as e:
            logger.error(f"Error in adaptive simplification: {str(e)}", exc_info=True)
            return points
    
    def _simplify_path(self, points):
        """Simplify a path using the Ramer-Douglas-Peucker algorithm"""
        try:
            if len(points) <= 2:
                return points
            
            # Use a fixed tolerance for simplification
            simplified = self._ramer_douglas_peucker(points, self.curve_tolerance * 2)
            
            logger.debug(f"Simplified path from {len(points)} to {len(simplified)} points")
            return simplified
        except Exception as e:
            logger.error(f"Error in path simplification: {str(e)}", exc_info=True)
            return points
    
    def _ramer_douglas_peucker(self, points, epsilon):
        """
        Ramer-Douglas-Peucker algorithm for curve simplification
        
        Args:
            points: List of points [(x1, y1), (x2, y2), ...]
            epsilon: Distance threshold
            
        Returns:
            Simplified list of points
        """
        try:
            if len(points) <= 2:
                return points
            
            # Find the point with the maximum distance
            dmax = 0
            index = 0
            end = len(points) - 1
            
            for i in range(1, end):
                d = self._point_line_distance(points[i], points[0], points[end])
                if d > dmax:
                    index = i
                    dmax = d
            
            # If max distance is greater than epsilon, recursively simplify
            if dmax > epsilon:
                # Recursive call
                rec_results1 = self._ramer_douglas_peucker(points[:index + 1], epsilon)
                rec_results2 = self._ramer_douglas_peucker(points[index:], epsilon)
                
                # Build the result list
                return rec_results1[:-1] + rec_results2
            else:
                return [points[0], points[end]]
        except Exception as e:
            logger.error(f"Error in Ramer-Douglas-Peucker algorithm: {str(e)}", exc_info=True)
            return points
    
    def _point_line_distance(self, point, line_start, line_end):
        """
        Calculate the distance between a point and a line segment
        
        Args:
            point: The point (x, y)
            line_start: Start point of the line (x1, y1)
            line_end: End point of the line (x2, y2)
            
        Returns:
            Distance from the point to the line
        """
        try:
            if line_start == line_end:
                return math.sqrt((point[0] - line_start[0])**2 + (point[1] - line_start[1])**2)
            
            # Calculate the distance using the formula:
            # d = |cross_product(end - start, point - start)| / |end - start|
            
            # Vector from start to end
            dx = line_end[0] - line_start[0]
            dy = line_end[1] - line_start[1]
            
            # Length of the line segment
            length = math.sqrt(dx**2 + dy**2)
            
            # Cross product
            cross = abs((dy * (point[0] - line_start[0])) - (dx * (point[1] - line_start[1])))
            
            # Distance
            return cross / length
        except Exception as e:
            logger.error(f"Error calculating point-line distance: {str(e)}", exc_info=True)
            return 0
    
    def generate_gcode(self, processed_paths, options=None):
        """Generate G-code from processed paths"""
        try:
            options = options or {}
            
            # Initialize G-code
            gcode = []
            
            # Add header
            gcode.append("; H.Airbrush G-code")
            gcode.append("; Generated by H.Airbrush Extension")
            gcode.append("")
            gcode.append("G21 ; Set units to millimeters")
            gcode.append("G90 ; Absolute positioning")
            gcode.append("G28 ; Home all axes")
            gcode.append("")
            
            # Set speeds
            drawing_speed = options.get('speed_drawing', 25)
            travel_speed = options.get('speed_travel', 75)
            
            # Convert speeds to mm/min (assuming 100% = 3000 mm/min)
            drawing_speed_mm = drawing_speed * 30
            travel_speed_mm = travel_speed * 30
            
            # Process each path
            for i, path in enumerate(processed_paths):
                gcode.append(f"; Path {i+1}: {path.id}")
                
                # Skip paths with no points
                if not path.points:
                    gcode.append("; Empty path, skipping")
                    gcode.append("")
                    continue
                
                # Skip paths with no brush assigned
                if not path.brush:
                    gcode.append("; No brush assigned, skipping")
                    gcode.append("")
                    continue
                
                # Move to the start point with brush up
                start_point = path.points[0]
                gcode.append(f"G0 X{start_point[0]:.3f} Y{start_point[1]:.3f} F{travel_speed_mm}")
                
                # Activate the appropriate brush
                if path.brush == 'A':
                    gcode.append(f"M280 P0 S{path.height:.0f} ; Set brush A height")
                    gcode.append("M400 ; Wait for moves to finish")
                    gcode.append("M42 P10 S255 ; Activate brush A")
                else:
                    gcode.append(f"M280 P1 S{path.height:.0f} ; Set brush B height")
                    gcode.append("M400 ; Wait for moves to finish")
                    gcode.append("M42 P11 S255 ; Activate brush B")
                
                # Wait for brush activation
                gcode.append("G4 P500 ; Wait for brush activation")
                
                # Draw the path
                for point in path.points[1:]:
                    gcode.append(f"G1 X{point[0]:.3f} Y{point[1]:.3f} F{drawing_speed_mm}")
                
                # Deactivate the brush
                if path.brush == 'A':
                    gcode.append("M42 P10 S0 ; Deactivate brush A")
                else:
                    gcode.append("M42 P11 S0 ; Deactivate brush B")
                
                gcode.append("")
            
            # Add footer
            gcode.append("; End of G-code")
            gcode.append("G28 ; Return to home position")
            
            return "\n".join(gcode)
        except Exception as e:
            logger.error(f"Error generating G-code: {str(e)}", exc_info=True)
            return "; Error generating G-code"

    @staticmethod
    def parse_path(path_data: str) -> List[PathSegment]:
        """
        Parse SVG path data into a list of PathSegment objects.
        
        Args:
            path_data: SVG path data string
            
        Returns:
            List of PathSegment objects
        """
        # Regular expression to match path commands and parameters
        command_regex = r"([MLHVCSQTAZmlhvcsqtaz])([^MLHVCSQTAZmlhvcsqtaz]*)"
        
        # Find all commands and their parameters
        segments = []
        for match in re.finditer(command_regex, path_data):
            cmd = match.group(1)
            params_str = match.group(2).strip()
            
            # Parse parameters
            params = []
            if params_str:
                # Split by either commas or spaces
                params_parts = re.split(r"[\s,]+", params_str)
                # Convert to float
                params = [float(p) for p in params_parts if p]
            
            # Determine command type and whether it's absolute
            command_type = None
            is_absolute = cmd.isupper()
            
            if cmd.upper() == 'M':
                command_type = PathCommand.MOVE_TO
            elif cmd.upper() == 'L':
                command_type = PathCommand.LINE_TO
            elif cmd.upper() == 'H':
                command_type = PathCommand.HORIZONTAL_LINE
            elif cmd.upper() == 'V':
                command_type = PathCommand.VERTICAL_LINE
            elif cmd.upper() == 'C':
                command_type = PathCommand.CUBIC_BEZIER
            elif cmd.upper() == 'S':
                command_type = PathCommand.SMOOTH_CUBIC
            elif cmd.upper() == 'Q':
                command_type = PathCommand.QUADRATIC_BEZIER
            elif cmd.upper() == 'T':
                command_type = PathCommand.SMOOTH_QUADRATIC
            elif cmd.upper() == 'A':
                command_type = PathCommand.ARC
            elif cmd.upper() == 'Z':
                command_type = PathCommand.CLOSE_PATH
            
            if command_type:
                segments.append(PathSegment(command_type, params, is_absolute))
        
        return segments

    @staticmethod
    def path_to_polyline(path_segments: List[PathSegment], curve_resolution: int = 10) -> List[Tuple[float, float]]:
        """
        Convert a path to a polyline (a series of straight line segments).
        
        This implementation handles all SVG path commands and uses adaptive segmentation
        for curves based on their complexity.
        
        Args:
            path_segments: List of PathSegment objects
            curve_resolution: Base resolution for curve approximation
                (higher values result in smoother curves)
            
        Returns:
            List of (x, y) points representing the polyline
        """
        if not path_segments:
            return []
            
        polyline = []
        current_x, current_y = 0, 0
        start_x, start_y = 0, 0  # For closing paths
        prev_control_point = None  # For smooth curves
        
        for segment in path_segments:
            # Convert to absolute coordinates if needed
            if not segment.absolute:
                segment = segment.to_absolute(current_x, current_y)
                
            if segment.command == PathCommand.MOVE_TO:
                # Move to a new position
                for i in range(0, len(segment.params), 2):
                    if i + 1 < len(segment.params):
                        current_x, current_y = segment.params[i], segment.params[i + 1]
                        if not polyline:  # First point in the path
                            polyline.append((current_x, current_y))
                        else:
                            # If we're moving after drawing, add the move as a separate point
                            polyline.append((current_x, current_y))
                        start_x, start_y = current_x, current_y  # Update start point for Z command
                        
            elif segment.command == PathCommand.LINE_TO:
                # Draw lines to specified points
                for i in range(0, len(segment.params), 2):
                    if i + 1 < len(segment.params):
                        current_x, current_y = segment.params[i], segment.params[i + 1]
                        polyline.append((current_x, current_y))
                        
            elif segment.command == PathCommand.HORIZONTAL_LINE:
                # Draw horizontal lines
                for x in segment.params:
                    current_x = x
                    polyline.append((current_x, current_y))
                    
            elif segment.command == PathCommand.VERTICAL_LINE:
                # Draw vertical lines
                for y in segment.params:
                    current_y = y
                    polyline.append((current_x, current_y))
                    
            elif segment.command == PathCommand.CUBIC_BEZIER:
                # Draw cubic Bezier curves
                for i in range(0, len(segment.params), 6):
                    if i + 5 < len(segment.params):
                        # Extract control points and end point
                        c1x, c1y = segment.params[i], segment.params[i + 1]
                        c2x, c2y = segment.params[i + 2], segment.params[i + 3]
                        x, y = segment.params[i + 4], segment.params[i + 5]
                        
                        # Store the last control point for smooth curves
                        prev_control_point = (c2x, c2y)
                        
                        # Generate points along the curve
                        for t in range(1, curve_resolution + 1):
                            t_normalized = t / curve_resolution
                            # Cubic Bezier formula
                            bx = (1 - t_normalized)**3 * current_x + \
                                3 * (1 - t_normalized)**2 * t_normalized * c1x + \
                                3 * (1 - t_normalized) * t_normalized**2 * c2x + \
                                t_normalized**3 * x
                            by = (1 - t_normalized)**3 * current_y + \
                                3 * (1 - t_normalized)**2 * t_normalized * c1y + \
                                3 * (1 - t_normalized) * t_normalized**2 * c2y + \
                                t_normalized**3 * y
                            polyline.append((bx, by))
                        
                        current_x, current_y = x, y
                        
            elif segment.command == PathCommand.SMOOTH_CUBIC:
                # Draw smooth cubic Bezier curves
                for i in range(0, len(segment.params), 4):
                    if i + 3 < len(segment.params):
                        # Calculate the first control point as a reflection of the previous one
                        if prev_control_point is not None:
                            c1x = 2 * current_x - prev_control_point[0]
                            c1y = 2 * current_y - prev_control_point[1]
                        else:
                            # If no previous control point, use current point
                            c1x, c1y = current_x, current_y
                            
                        # Extract second control point and end point
                        c2x, c2y = segment.params[i], segment.params[i + 1]
                        x, y = segment.params[i + 2], segment.params[i + 3]
                        
                        # Store the last control point for next smooth curve
                        prev_control_point = (c2x, c2y)
                        
                        # Generate points along the curve
                        for t in range(1, curve_resolution + 1):
                            t_normalized = t / curve_resolution
                            # Cubic Bezier formula
                            bx = (1 - t_normalized)**3 * current_x + \
                                3 * (1 - t_normalized)**2 * t_normalized * c1x + \
                                3 * (1 - t_normalized) * t_normalized**2 * c2x + \
                                t_normalized**3 * x
                            by = (1 - t_normalized)**3 * current_y + \
                                3 * (1 - t_normalized)**2 * t_normalized * c1y + \
                                3 * (1 - t_normalized) * t_normalized**2 * c2y + \
                                t_normalized**3 * y
                            polyline.append((bx, by))
                        
                        current_x, current_y = x, y
                        
            elif segment.command == PathCommand.QUADRATIC_BEZIER:
                # Draw quadratic Bezier curves
                for i in range(0, len(segment.params), 4):
                    if i + 3 < len(segment.params):
                        # Extract control point and end point
                        cx, cy = segment.params[i], segment.params[i + 1]
                        x, y = segment.params[i + 2], segment.params[i + 3]
                        
                        # Store control point for smooth quadratic curves
                        prev_control_point = (cx, cy)
                        
                        # Generate points along the curve
                        for t in range(1, curve_resolution + 1):
                            t_normalized = t / curve_resolution
                            # Quadratic Bezier formula
                            bx = (1 - t_normalized)**2 * current_x + \
                                2 * (1 - t_normalized) * t_normalized * cx + \
                                t_normalized**2 * x
                            by = (1 - t_normalized)**2 * current_y + \
                                2 * (1 - t_normalized) * t_normalized * cy + \
                                t_normalized**2 * y
                            polyline.append((bx, by))
                        
                        current_x, current_y = x, y
                        
            elif segment.command == PathCommand.SMOOTH_QUADRATIC:
                # Draw smooth quadratic Bezier curves
                for i in range(0, len(segment.params), 2):
                    if i + 1 < len(segment.params):
                        # Calculate control point as reflection of previous control point
                        if prev_control_point is not None:
                            cx = 2 * current_x - prev_control_point[0]
                            cy = 2 * current_y - prev_control_point[1]
                        else:
                            # If no previous control point, use current point
                            cx, cy = current_x, current_y
                            
                        # Extract end point
                        x, y = segment.params[i], segment.params[i + 1]
                        
                        # Store control point for next smooth curve
                        prev_control_point = (cx, cy)
                        
                        # Generate points along the curve
                        for t in range(1, curve_resolution + 1):
                            t_normalized = t / curve_resolution
                            # Quadratic Bezier formula
                            bx = (1 - t_normalized)**2 * current_x + \
                                2 * (1 - t_normalized) * t_normalized * cx + \
                                t_normalized**2 * x
                            by = (1 - t_normalized)**2 * current_y + \
                                2 * (1 - t_normalized) * t_normalized * cy + \
                                t_normalized**2 * y
                            polyline.append((bx, by))
                        
                        current_x, current_y = x, y
                        
            elif segment.command == PathCommand.ARC:
                # Draw elliptical arcs
                for i in range(0, len(segment.params), 7):
                    if i + 6 < len(segment.params):
                        # Extract arc parameters
                        rx, ry = segment.params[i], segment.params[i + 1]
                        x_axis_rotation = segment.params[i + 2]
                        large_arc_flag = int(segment.params[i + 3])
                        sweep_flag = int(segment.params[i + 4])
                        x, y = segment.params[i + 5], segment.params[i + 6]
                        
                        # Generate points along the arc
                        # This is a simplified approximation
                        arc_points = []
                        for t in range(1, curve_resolution + 1):
                            t_normalized = t / curve_resolution
                            # Linear interpolation for now
                            ax = current_x + (x - current_x) * t_normalized
                            ay = current_y + (y - current_y) * t_normalized
                            arc_points.append((ax, ay))
                        
                        polyline.extend(arc_points)
                        current_x, current_y = x, y
                        
            elif segment.command == PathCommand.CLOSE_PATH:
                # Close the path by returning to the start point
                if start_x != current_x or start_y != current_y:
                    polyline.append((start_x, start_y))
                current_x, current_y = start_x, start_y
        
        return polyline 
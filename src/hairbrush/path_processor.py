"""
Path processing utilities for the hairbrush package.

This module provides advanced SVG path processing functionality,
including path simplification, smoothing, and conversion between
different path formats.
"""

import re
import math
from typing import List, Tuple, Dict, Any, Optional, Union
import numpy as np
from enum import Enum, auto


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
    
    def to_svg_command(self) -> str:
        """
        Convert the segment to an SVG path command string.
        
        Returns:
            SVG path command string
        """
        cmd_char = ""
        
        if self.command == PathCommand.MOVE_TO:
            cmd_char = "M" if self.absolute else "m"
        elif self.command == PathCommand.LINE_TO:
            cmd_char = "L" if self.absolute else "l"
        elif self.command == PathCommand.HORIZONTAL_LINE:
            cmd_char = "H" if self.absolute else "h"
        elif self.command == PathCommand.VERTICAL_LINE:
            cmd_char = "V" if self.absolute else "v"
        elif self.command == PathCommand.CUBIC_BEZIER:
            cmd_char = "C" if self.absolute else "c"
        elif self.command == PathCommand.SMOOTH_CUBIC:
            cmd_char = "S" if self.absolute else "s"
        elif self.command == PathCommand.QUADRATIC_BEZIER:
            cmd_char = "Q" if self.absolute else "q"
        elif self.command == PathCommand.SMOOTH_QUADRATIC:
            cmd_char = "T" if self.absolute else "t"
        elif self.command == PathCommand.ARC:
            cmd_char = "A" if self.absolute else "a"
        elif self.command == PathCommand.CLOSE_PATH:
            cmd_char = "Z" if self.absolute else "z"
        
        # Format parameters
        params_str = " ".join(f"{p:.3f}" if isinstance(p, float) else str(p) for p in self.params)
        
        return f"{cmd_char} {params_str}".strip()
    
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
                    return self.params[-2], self.params[-1]
        
        # For relative commands or CLOSE_PATH, convert to absolute first
        abs_segment = self.to_absolute(current_x, current_y)
        
        if self.command == PathCommand.CLOSE_PATH:
            # CLOSE_PATH returns to the start of the path, which we don't track here
            # In this case, just return the current point
            return current_x, current_y
        
        return abs_segment.get_end_point(current_x, current_y)


class PathProcessor:
    """Processor for SVG paths with advanced operations."""
    
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
    def path_to_absolute(path_segments: List[PathSegment]) -> List[PathSegment]:
        """
        Convert all path segments to use absolute coordinates.
        
        Args:
            path_segments: List of path segments
            
        Returns:
            List of path segments with absolute coordinates
        """
        absolute_segments = []
        current_x, current_y = 0, 0
        
        for segment in path_segments:
            abs_segment = segment.to_absolute(current_x, current_y)
            absolute_segments.append(abs_segment)
            
            # Update current position
            if segment.command != PathCommand.CLOSE_PATH and segment.params:
                current_x, current_y = abs_segment.get_end_point(current_x, current_y)
        
        return absolute_segments
    
    @staticmethod
    def _adaptive_bezier_segmentation(start_point, control_points, end_point, max_error=0.1, min_segments=5, max_segments=100):
        """
        Determine the appropriate number of segments for a Bezier curve based on curvature.
        
        This method uses an adaptive approach that analyzes the curve's complexity
        to determine how many line segments are needed for accurate approximation.
        
        Args:
            start_point (tuple): Starting point (x, y)
            control_points (list): List of control points [(x1, y1), (x2, y2), ...]
            end_point (tuple): End point (x, y)
            max_error (float): Maximum allowed error
            min_segments (int): Minimum number of segments
            max_segments (int): Maximum number of segments
            
        Returns:
            int: Number of segments to use
        """
        # For cubic bezier (with 2 control points)
        if len(control_points) == 2:
            # Calculate the "complexity" of the curve by examining control points
            # Calculate distances between control points and the line from start to end
            x0, y0 = start_point
            x3, y3 = end_point
            x1, y1 = control_points[0]
            x2, y2 = control_points[1]
            
            # Calculate the straight-line distance from start to end
            chord_length = math.sqrt((x3 - x0) ** 2 + (y3 - y0) ** 2)
            
            # If the chord length is very small, use minimum segments
            if chord_length < 0.001:
                return min_segments
                
            # Calculate control point distances from the chord line
            # First, calculate parameters for the line equation ax + by + c = 0
            a = y3 - y0
            b = x0 - x3
            c = x3 * y0 - x0 * y3
            norm = math.sqrt(a * a + b * b)
            
            if norm < 0.001:  # Avoid division by zero
                return min_segments
                
            # Calculate perpendicular distances from control points to the chord line
            d1 = abs(a * x1 + b * y1 + c) / norm
            d2 = abs(a * x2 + b * y2 + c) / norm
            
            # Calculate the "curve complexity" based on these distances and chord length
            curve_complexity = max(d1, d2) / chord_length
            
            # Calculate the arc length approximation
            arc_length = (
                math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) +
                math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) +
                math.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)
            )
            
            # Adjust by the ratio of arc length to chord length
            arc_chord_ratio = arc_length / chord_length if chord_length > 0 else 1
            
            # Calculate the number of segments based on curve complexity and arc/chord ratio
            # The magic numbers here are derived from empirical testing
            segments = min(
                max_segments,
                max(
                    min_segments,
                    int(min(
                        max_segments,
                        curve_complexity * 100,  # Scale based on curve complexity
                        arc_chord_ratio * 20     # Scale based on arc/chord ratio
                    ))
                )
            )
            
            return segments
            
        # For quadratic bezier (with 1 control point)
        elif len(control_points) == 1:
            x0, y0 = start_point
            x2, y2 = end_point
            x1, y1 = control_points[0]
            
            # Calculate the straight-line distance from start to end
            chord_length = math.sqrt((x2 - x0) ** 2 + (y2 - y0) ** 2)
            
            # If the chord length is very small, use minimum segments
            if chord_length < 0.001:
                return min_segments
                
            # Calculate control point distance from the chord line
            a = y2 - y0
            b = x0 - x2
            c = x2 * y0 - x0 * y2
            norm = math.sqrt(a * a + b * b)
            
            if norm < 0.001:  # Avoid division by zero
                return min_segments
                
            d1 = abs(a * x1 + b * y1 + c) / norm
            
            # Calculate curve complexity
            curve_complexity = d1 / chord_length
            
            # Calculate the arc length approximation
            arc_length = (
                math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) +
                math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            )
            
            # Adjust by the ratio of arc length to chord length
            arc_chord_ratio = arc_length / chord_length if chord_length > 0 else 1
            
            # Calculate the number of segments
            segments = min(
                max_segments,
                max(
                    min_segments,
                    int(min(
                        max_segments,
                        curve_complexity * 80,   # Scale based on curve complexity
                        arc_chord_ratio * 15     # Scale based on arc/chord ratio
                    ))
                )
            )
            
            return segments
            
        # Default case
        return min_segments
    
    @staticmethod
    def _calculate_smooth_control_point(current_point, prev_control_point):
        """
        Calculate the control point for smooth curve commands (S, T).
        
        Args:
            current_point (tuple): Current point (x, y)
            prev_control_point (tuple): Previous control point (x, y)
            
        Returns:
            tuple: Calculated control point (x, y)
        """
        # Reflect the previous control point around the current point
        if prev_control_point is None:
            return current_point
            
        return (
            2 * current_point[0] - prev_control_point[0],
            2 * current_point[1] - prev_control_point[1]
        )
    
    @staticmethod
    def _approximate_arc(start_point, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, end_point, segments=20):
        """
        Approximate an elliptical arc with line segments.
        
        This is a more accurate implementation of the SVG arc command (A/a).
        Based on the SVG 1.1 specification and the approach used in the AxiDraw extension.
        
        Args:
            start_point (tuple): Starting point (x, y)
            rx (float): X-axis radius
            ry (float): Y-axis radius
            x_axis_rotation (float): Rotation of the ellipse's x-axis, in degrees
            large_arc_flag (int): 1 for large arc, 0 for small arc
            sweep_flag (int): 1 for positive angle, 0 for negative angle
            end_point (tuple): End point (x, y)
            segments (int): Number of line segments to use
            
        Returns:
            list: List of points [(x, y), ...] approximating the arc
        """
        # Handle degenerate cases
        if start_point == end_point:
            return [start_point]
            
        if rx == 0 or ry == 0:
            return [start_point, end_point]
            
        # Make sure rx and ry are positive
        rx = abs(rx)
        ry = abs(ry)
        
        # Convert rotation from degrees to radians
        phi = math.radians(x_axis_rotation)
        
        # Extract start and end points
        x1, y1 = start_point
        x2, y2 = end_point
        
        # Step 1: Transform to origin
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)
        
        # Compute transformed point (x1', y1')
        x1_prime = cos_phi * (x1 - x2) / 2 + sin_phi * (y1 - y2) / 2
        y1_prime = -sin_phi * (x1 - x2) / 2 + cos_phi * (y1 - y2) / 2
        
        # Ensure radii are large enough
        lambda_value = (x1_prime * x1_prime) / (rx * rx) + (y1_prime * y1_prime) / (ry * ry)
        if lambda_value > 1:
            # Scale up rx and ry
            rx *= math.sqrt(lambda_value)
            ry *= math.sqrt(lambda_value)
        
        # Step 2: Compute center parameters
        sign = -1 if large_arc_flag == sweep_flag else 1
        
        # Calculate the discriminant
        disc = max(0, (rx * rx * ry * ry - rx * rx * y1_prime * y1_prime - ry * ry * x1_prime * x1_prime) / 
                      (rx * rx * y1_prime * y1_prime + ry * ry * x1_prime * x1_prime))
        
        # Calculate center point (cx', cy')
        factor = sign * math.sqrt(disc)
        cx_prime = factor * rx * y1_prime / ry
        cy_prime = -factor * ry * x1_prime / rx
        
        if math.isnan(cx_prime) or math.isnan(cy_prime):
            # Fallback for numerical issues
            cx_prime = 0
            cy_prime = 0
        
        # Step 3: Transform back to original coordinate system
        cx = cos_phi * cx_prime - sin_phi * cy_prime + (x1 + x2) / 2
        cy = sin_phi * cx_prime + cos_phi * cy_prime + (y1 + y2) / 2
        
        # Step 4: Calculate the start and end angles
        ux = (x1_prime - cx_prime) / rx
        uy = (y1_prime - cy_prime) / ry
        vx = (-x1_prime - cx_prime) / rx
        vy = (-y1_prime - cy_prime) / ry
        
        # Calculate start angle
        start_angle = math.atan2(uy, ux)
        
        # Calculate angle delta
        n = math.sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
        p = ux * vx + uy * vy
        d = p / n
        
        # Clamp d to avoid numerical issues
        d = max(min(d, 1.0), -1.0)
        
        delta = math.acos(d)
        if (ux * vy - uy * vx) < 0:
            delta = -delta
            
        # Adjust delta based on sweep flag
        if sweep_flag == 0 and delta > 0:
            delta -= 2 * math.pi
        elif sweep_flag == 1 and delta < 0:
            delta += 2 * math.pi
            
        # Step 5: Generate points along the arc
        points = []
        for i in range(segments + 1):
            t = start_angle + delta * i / segments
            
            # Calculate point on the ellipse
            ellipse_x = rx * math.cos(t)
            ellipse_y = ry * math.sin(t)
            
            # Transform back to original coordinate system
            x = cos_phi * ellipse_x - sin_phi * ellipse_y + cx
            y = sin_phi * ellipse_x + cos_phi * ellipse_y + cy
            
            points.append((x, y))
            
        # Ensure the end point is exactly as specified
        points[-1] = end_point
            
        return points

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
                        
                        # Determine the appropriate number of segments based on curve complexity
                        control_points = [(c1x, c1y), (c2x, c2y)]
                        segments = PathProcessor._adaptive_bezier_segmentation(
                            (current_x, current_y), 
                            control_points, 
                            (x, y), 
                            max_error=0.1, 
                            min_segments=curve_resolution,
                            max_segments=curve_resolution * 5
                        )
                        
                        # Generate points along the curve
                        for t in range(1, segments + 1):
                            t_normalized = t / segments
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
                            c1x, c1y = PathProcessor._calculate_smooth_control_point(
                                (current_x, current_y), 
                                prev_control_point
                            )
                        else:
                            # If no previous control point, use current point
                            c1x, c1y = current_x, current_y
                            
                        # Extract second control point and end point
                        c2x, c2y = segment.params[i], segment.params[i + 1]
                        x, y = segment.params[i + 2], segment.params[i + 3]
                        
                        # Store the last control point for next smooth curve
                        prev_control_point = (c2x, c2y)
                        
                        # Determine the appropriate number of segments
                        control_points = [(c1x, c1y), (c2x, c2y)]
                        segments = PathProcessor._adaptive_bezier_segmentation(
                            (current_x, current_y), 
                            control_points, 
                            (x, y), 
                            max_error=0.1, 
                            min_segments=curve_resolution,
                            max_segments=curve_resolution * 5
                        )
                        
                        # Generate points along the curve
                        for t in range(1, segments + 1):
                            t_normalized = t / segments
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
                        
                        # Determine the appropriate number of segments
                        control_points = [(cx, cy)]
                        segments = PathProcessor._adaptive_bezier_segmentation(
                            (current_x, current_y), 
                            control_points, 
                            (x, y), 
                            max_error=0.1, 
                            min_segments=curve_resolution,
                            max_segments=curve_resolution * 3
                        )
                        
                        # Generate points along the curve
                        for t in range(1, segments + 1):
                            t_normalized = t / segments
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
                        # Calculate the control point as a reflection of the previous one
                        if prev_control_point is not None:
                            cx, cy = PathProcessor._calculate_smooth_control_point(
                                (current_x, current_y), 
                                prev_control_point
                            )
                        else:
                            # If no previous control point, use current point
                            cx, cy = current_x, current_y
                            
                        # Extract end point
                        x, y = segment.params[i], segment.params[i + 1]
                        
                        # Store control point for next smooth curve
                        prev_control_point = (cx, cy)
                        
                        # Determine the appropriate number of segments
                        control_points = [(cx, cy)]
                        segments = PathProcessor._adaptive_bezier_segmentation(
                            (current_x, current_y), 
                            control_points, 
                            (x, y), 
                            max_error=0.1, 
                            min_segments=curve_resolution,
                            max_segments=curve_resolution * 3
                        )
                        
                        # Generate points along the curve
                        for t in range(1, segments + 1):
                            t_normalized = t / segments
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
                        rx = segment.params[i]
                        ry = segment.params[i + 1]
                        x_axis_rotation = segment.params[i + 2]
                        large_arc_flag = int(segment.params[i + 3])
                        sweep_flag = int(segment.params[i + 4])
                        x = segment.params[i + 5]
                        y = segment.params[i + 6]
                        
                        # Clear previous control point as arc doesn't affect smooth curves
                        prev_control_point = None
                        
                        # Calculate adaptive segment count based on arc size and complexity
                        arc_length_estimate = math.sqrt((x - current_x)**2 + (y - current_y)**2)
                        arc_segments = max(curve_resolution, min(curve_resolution * 4, int(arc_length_estimate * 0.5)))
                        
                        # Approximate the arc with line segments
                        arc_points = PathProcessor._approximate_arc(
                            (current_x, current_y),
                            rx, ry,
                            x_axis_rotation,
                            large_arc_flag,
                            sweep_flag,
                            (x, y),
                            arc_segments
                        )
                        
                        # Add all points except the first (which is the current point)
                        polyline.extend(arc_points)
                        
                        current_x, current_y = x, y
                        
            elif segment.command == PathCommand.CLOSE_PATH:
                # Close the path by drawing a line to the start point
                if polyline and (start_x, start_y) != (current_x, current_y):
                    polyline.append((start_x, start_y))
                    current_x, current_y = start_x, start_y
                    
        return polyline
    
    @staticmethod
    def simplify_path(path_data: str, tolerance: float = 0.5) -> str:
        """
        Simplify a path by reducing the number of points while preserving shape.
        Uses the Ramer-Douglas-Peucker algorithm.
        
        Args:
            path_data: SVG path data string
            tolerance: Tolerance for simplification (higher = more simplification)
            
        Returns:
            Simplified SVG path data string
        """
        # Parse the path
        segments = PathProcessor.parse_path(path_data)
        
        # Convert to a polyline
        points = PathProcessor.path_to_polyline(segments)
        
        # Apply Ramer-Douglas-Peucker algorithm
        simplified_points = PathProcessor._rdp_simplify(points, tolerance)
        
        # Convert back to SVG path data
        path = f"M {simplified_points[0][0]:.3f},{simplified_points[0][1]:.3f}"
        for i in range(1, len(simplified_points)):
            path += f" L {simplified_points[i][0]:.3f},{simplified_points[i][1]:.3f}"
        
        return path
    
    @staticmethod
    def _rdp_simplify(points: List[Tuple[float, float]], epsilon: float) -> List[Tuple[float, float]]:
        """
        Ramer-Douglas-Peucker algorithm for line simplification.
        
        Args:
            points: List of (x, y) points
            epsilon: Tolerance value
            
        Returns:
            Simplified list of points
        """
        if len(points) < 3:
            return points
        
        # Find the point with the maximum distance
        dmax = 0
        index = 0
        for i in range(1, len(points) - 1):
            d = PathProcessor._perpendicular_distance(points[i], points[0], points[-1])
            if d > dmax:
                index = i
                dmax = d
        
        # If max distance is greater than epsilon, recursively simplify
        if dmax > epsilon:
            # Recursive call
            rec_results1 = PathProcessor._rdp_simplify(points[:index + 1], epsilon)
            rec_results2 = PathProcessor._rdp_simplify(points[index:], epsilon)
            
            # Build the result list
            return rec_results1[:-1] + rec_results2
        else:
            return [points[0], points[-1]]
    
    @staticmethod
    def _perpendicular_distance(point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> float:
        """
        Calculate the perpendicular distance from a point to a line.
        
        Args:
            point: The point (x, y)
            line_start: Start point of the line (x, y)
            line_end: End point of the line (x, y)
            
        Returns:
            The perpendicular distance
        """
        if line_start == line_end:
            # If the line is actually a point, return the distance to that point
            return math.sqrt((point[0] - line_start[0])**2 + (point[1] - line_start[1])**2)
        
        # Calculate the perpendicular distance
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Line length
        line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Perpendicular distance
        return abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / line_length 
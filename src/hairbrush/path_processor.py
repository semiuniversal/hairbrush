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
    def path_to_polyline(path_segments: List[PathSegment], curve_resolution: int = 10) -> List[Tuple[float, float]]:
        """
        Convert a path to a polyline (series of points).
        Curves are approximated with straight line segments.
        
        Args:
            path_segments: List of path segments
            curve_resolution: Number of points to use when approximating curves
            
        Returns:
            List of (x, y) points
        """
        # First convert all segments to absolute coordinates
        abs_segments = PathProcessor.path_to_absolute(path_segments)
        
        points = []
        current_x, current_y = 0, 0
        path_start_x, path_start_y = 0, 0
        
        for segment in abs_segments:
            if segment.command == PathCommand.MOVE_TO:
                # Move to a new position
                for i in range(0, len(segment.params), 2):
                    if i + 1 < len(segment.params):
                        current_x, current_y = segment.params[i], segment.params[i+1]
                        points.append((current_x, current_y))
                        
                        # Record start of path for CLOSE_PATH
                        path_start_x, path_start_y = current_x, current_y
            
            elif segment.command == PathCommand.LINE_TO:
                # Draw lines
                for i in range(0, len(segment.params), 2):
                    if i + 1 < len(segment.params):
                        current_x, current_y = segment.params[i], segment.params[i+1]
                        points.append((current_x, current_y))
            
            elif segment.command == PathCommand.HORIZONTAL_LINE:
                # Draw horizontal lines
                for x in segment.params:
                    current_x = x
                    points.append((current_x, current_y))
            
            elif segment.command == PathCommand.VERTICAL_LINE:
                # Draw vertical lines
                for y in segment.params:
                    current_y = y
                    points.append((current_x, current_y))
            
            elif segment.command == PathCommand.CLOSE_PATH:
                # Close the path by returning to the start point
                if (current_x, current_y) != (path_start_x, path_start_y):
                    current_x, current_y = path_start_x, path_start_y
                    points.append((current_x, current_y))
            
            elif segment.command == PathCommand.CUBIC_BEZIER:
                # Approximate cubic Bezier curves with line segments
                for i in range(0, len(segment.params), 6):
                    if i + 5 < len(segment.params):
                        start_x, start_y = current_x, current_y
                        c1x, c1y = segment.params[i], segment.params[i+1]
                        c2x, c2y = segment.params[i+2], segment.params[i+3]
                        end_x, end_y = segment.params[i+4], segment.params[i+5]
                        
                        # Approximate the curve with line segments
                        for t in range(1, curve_resolution + 1):
                            t_normalized = t / curve_resolution
                            
                            # Cubic Bezier formula
                            x = (1 - t_normalized)**3 * start_x + \
                                3 * (1 - t_normalized)**2 * t_normalized * c1x + \
                                3 * (1 - t_normalized) * t_normalized**2 * c2x + \
                                t_normalized**3 * end_x
                            
                            y = (1 - t_normalized)**3 * start_y + \
                                3 * (1 - t_normalized)**2 * t_normalized * c1y + \
                                3 * (1 - t_normalized) * t_normalized**2 * c2y + \
                                t_normalized**3 * end_y
                            
                            points.append((x, y))
                        
                        current_x, current_y = end_x, end_y
            
            # For simplicity, we'll approximate other curve types as straight lines
            # to their endpoints. A more accurate implementation would use proper
            # curve interpolation for each type.
            else:
                end_x, end_y = segment.get_end_point(current_x, current_y)
                if (end_x, end_y) != (current_x, current_y):
                    current_x, current_y = end_x, end_y
                    points.append((current_x, current_y))
        
        return points
    
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
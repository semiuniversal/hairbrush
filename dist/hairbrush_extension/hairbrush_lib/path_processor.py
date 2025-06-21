"""
Path Processor for Hairbrush

This module provides functionality to process SVG paths and convert them to a format
suitable for G-code generation.
"""

import re
import math
from collections import namedtuple

# Named tuple for a point
Point = namedtuple('Point', ['x', 'y'])

class PathProcessor:
    """Process SVG paths for G-code generation."""
    
    @staticmethod
    def parse_path(path_data):
        """Parse SVG path data into a list of commands and coordinates."""
        # Regular expression to match path commands and coordinates
        command_regex = r'([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)'
        
        # Find all commands and coordinates
        commands = []
        for match in re.finditer(command_regex, path_data):
            command = match.group(1)
            params = match.group(2).strip()
            
            # Parse parameters
            if params:
                # Split parameters by comma or space
                params = re.split(r'[\s,]+', params)
                # Convert to float
                params = [float(p) for p in params if p]
            else:
                params = []
            
            commands.append((command, params))
        
        return commands
    
    @staticmethod
    def process_path(path_data, curve_resolution=20):
        """Process SVG path data into a list of points."""
        commands = PathProcessor.parse_path(path_data)
        points = []
        
        # Current position
        current_x = 0
        current_y = 0
        
        # Start position (for closepath)
        start_x = 0
        start_y = 0
        
        # Previous control point (for smooth curves)
        prev_control_x = 0
        prev_control_y = 0
        
        for command, params in commands:
            if command == 'M':  # Move to (absolute)
                for i in range(0, len(params), 2):
                    current_x = params[i]
                    current_y = params[i+1]
                    points.append(Point(current_x, current_y))
                    start_x = current_x
                    start_y = current_y
            
            elif command == 'm':  # Move to (relative)
                for i in range(0, len(params), 2):
                    current_x += params[i]
                    current_y += params[i+1]
                    points.append(Point(current_x, current_y))
                    start_x = current_x
                    start_y = current_y
            
            elif command == 'L':  # Line to (absolute)
                for i in range(0, len(params), 2):
                    current_x = params[i]
                    current_y = params[i+1]
                    points.append(Point(current_x, current_y))
            
            elif command == 'l':  # Line to (relative)
                for i in range(0, len(params), 2):
                    current_x += params[i]
                    current_y += params[i+1]
                    points.append(Point(current_x, current_y))
            
            elif command == 'H':  # Horizontal line to (absolute)
                for i in range(len(params)):
                    current_x = params[i]
                    points.append(Point(current_x, current_y))
            
            elif command == 'h':  # Horizontal line to (relative)
                for i in range(len(params)):
                    current_x += params[i]
                    points.append(Point(current_x, current_y))
            
            elif command == 'V':  # Vertical line to (absolute)
                for i in range(len(params)):
                    current_y = params[i]
                    points.append(Point(current_x, current_y))
            
            elif command == 'v':  # Vertical line to (relative)
                for i in range(len(params)):
                    current_y += params[i]
                    points.append(Point(current_x, current_y))
            
            elif command == 'C':  # Cubic Bezier curve (absolute)
                for i in range(0, len(params), 6):
                    x1, y1 = params[i], params[i+1]
                    x2, y2 = params[i+2], params[i+3]
                    x, y = params[i+4], params[i+5]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.cubic_bezier(
                        current_x, current_y, x1, y1, x2, y2, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x2
                    prev_control_y = y2
            
            elif command == 'c':  # Cubic Bezier curve (relative)
                for i in range(0, len(params), 6):
                    x1 = current_x + params[i]
                    y1 = current_y + params[i+1]
                    x2 = current_x + params[i+2]
                    y2 = current_y + params[i+3]
                    x = current_x + params[i+4]
                    y = current_y + params[i+5]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.cubic_bezier(
                        current_x, current_y, x1, y1, x2, y2, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x2
                    prev_control_y = y2
            
            elif command == 'S':  # Smooth cubic Bezier curve (absolute)
                for i in range(0, len(params), 4):
                    # Reflect the previous control point
                    x1 = 2 * current_x - prev_control_x
                    y1 = 2 * current_y - prev_control_y
                    
                    x2, y2 = params[i], params[i+1]
                    x, y = params[i+2], params[i+3]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.cubic_bezier(
                        current_x, current_y, x1, y1, x2, y2, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x2
                    prev_control_y = y2
            
            elif command == 's':  # Smooth cubic Bezier curve (relative)
                for i in range(0, len(params), 4):
                    # Reflect the previous control point
                    x1 = 2 * current_x - prev_control_x
                    y1 = 2 * current_y - prev_control_y
                    
                    x2 = current_x + params[i]
                    y2 = current_y + params[i+1]
                    x = current_x + params[i+2]
                    y = current_y + params[i+3]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.cubic_bezier(
                        current_x, current_y, x1, y1, x2, y2, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x2
                    prev_control_y = y2
            
            elif command == 'Q':  # Quadratic Bezier curve (absolute)
                for i in range(0, len(params), 4):
                    x1, y1 = params[i], params[i+1]
                    x, y = params[i+2], params[i+3]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.quadratic_bezier(
                        current_x, current_y, x1, y1, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x1
                    prev_control_y = y1
            
            elif command == 'q':  # Quadratic Bezier curve (relative)
                for i in range(0, len(params), 4):
                    x1 = current_x + params[i]
                    y1 = current_y + params[i+1]
                    x = current_x + params[i+2]
                    y = current_y + params[i+3]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.quadratic_bezier(
                        current_x, current_y, x1, y1, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x1
                    prev_control_y = y1
            
            elif command == 'T':  # Smooth quadratic Bezier curve (absolute)
                for i in range(0, len(params), 2):
                    # Reflect the previous control point
                    x1 = 2 * current_x - prev_control_x
                    y1 = 2 * current_y - prev_control_y
                    
                    x, y = params[i], params[i+1]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.quadratic_bezier(
                        current_x, current_y, x1, y1, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x1
                    prev_control_y = y1
            
            elif command == 't':  # Smooth quadratic Bezier curve (relative)
                for i in range(0, len(params), 2):
                    # Reflect the previous control point
                    x1 = 2 * current_x - prev_control_x
                    y1 = 2 * current_y - prev_control_y
                    
                    x = current_x + params[i]
                    y = current_y + params[i+1]
                    
                    # Calculate points along the curve
                    curve_points = PathProcessor.quadratic_bezier(
                        current_x, current_y, x1, y1, x, y, curve_resolution
                    )
                    points.extend(curve_points)
                    
                    current_x = x
                    current_y = y
                    prev_control_x = x1
                    prev_control_y = y1
            
            elif command == 'A':  # Elliptical arc (absolute)
                for i in range(0, len(params), 7):
                    rx, ry = params[i], params[i+1]
                    x_axis_rotation = params[i+2]
                    large_arc_flag = int(params[i+3])
                    sweep_flag = int(params[i+4])
                    x, y = params[i+5], params[i+6]
                    
                    # Calculate points along the arc
                    arc_points = PathProcessor.elliptical_arc(
                        current_x, current_y, rx, ry, x_axis_rotation,
                        large_arc_flag, sweep_flag, x, y, curve_resolution
                    )
                    points.extend(arc_points)
                    
                    current_x = x
                    current_y = y
            
            elif command == 'a':  # Elliptical arc (relative)
                for i in range(0, len(params), 7):
                    rx, ry = params[i], params[i+1]
                    x_axis_rotation = params[i+2]
                    large_arc_flag = int(params[i+3])
                    sweep_flag = int(params[i+4])
                    x = current_x + params[i+5]
                    y = current_y + params[i+6]
                    
                    # Calculate points along the arc
                    arc_points = PathProcessor.elliptical_arc(
                        current_x, current_y, rx, ry, x_axis_rotation,
                        large_arc_flag, sweep_flag, x, y, curve_resolution
                    )
                    points.extend(arc_points)
                    
                    current_x = x
                    current_y = y
            
            elif command == 'Z' or command == 'z':  # Close path
                if points and (current_x != start_x or current_y != start_y):
                    points.append(Point(start_x, start_y))
                    current_x = start_x
                    current_y = start_y
        
        return points
    
    @staticmethod
    def cubic_bezier(x0, y0, x1, y1, x2, y2, x3, y3, num_segments):
        """Calculate points along a cubic Bezier curve."""
        points = []
        
        # Use adaptive segmentation based on curve complexity
        # Calculate the "complexity" of the curve by measuring control point distances
        chord_length = math.sqrt((x3 - x0) ** 2 + (y3 - y0) ** 2)
        control_distance = (
            math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) +
            math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) +
            math.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)
        )
        
        # If the control points are far from the chord, use more segments
        complexity_ratio = control_distance / (chord_length + 0.0001)  # Avoid division by zero
        adaptive_segments = min(100, max(5, int(num_segments * complexity_ratio)))
        
        for i in range(1, adaptive_segments + 1):
            t = i / adaptive_segments
            
            # Cubic Bezier formula
            x = (1-t)**3 * x0 + 3*(1-t)**2 * t * x1 + 3*(1-t) * t**2 * x2 + t**3 * x3
            y = (1-t)**3 * y0 + 3*(1-t)**2 * t * y1 + 3*(1-t) * t**2 * y2 + t**3 * y3
            
            points.append(Point(x, y))
        
        return points
    
    @staticmethod
    def quadratic_bezier(x0, y0, x1, y1, x2, y2, num_segments):
        """Calculate points along a quadratic Bezier curve."""
        points = []
        
        # Use adaptive segmentation based on curve complexity
        chord_length = math.sqrt((x2 - x0) ** 2 + (y2 - y0) ** 2)
        control_distance = (
            math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) +
            math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        )
        
        # If the control point is far from the chord, use more segments
        complexity_ratio = control_distance / (chord_length + 0.0001)  # Avoid division by zero
        adaptive_segments = min(50, max(5, int(num_segments * complexity_ratio / 2)))
        
        for i in range(1, adaptive_segments + 1):
            t = i / adaptive_segments
            
            # Quadratic Bezier formula
            x = (1-t)**2 * x0 + 2*(1-t) * t * x1 + t**2 * x2
            y = (1-t)**2 * y0 + 2*(1-t) * t * y1 + t**2 * y2
            
            points.append(Point(x, y))
        
        return points
    
    @staticmethod
    def elliptical_arc(x1, y1, rx, ry, phi, large_arc, sweep, x2, y2, num_segments):
        """Calculate points along an elliptical arc."""
        # Implementation based on the SVG specification
        # See: https://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        
        # If the endpoints are identical, return a single point
        if x1 == x2 and y1 == y2:
            return [Point(x1, y1)]
        
        # If rx or ry is 0, treat as a straight line
        if rx == 0 or ry == 0:
            return [Point(x2, y2)]
        
        # Convert angle from degrees to radians
        phi_rad = phi * math.pi / 180.0
        
        # Step 1: Compute the transformed endpoint
        cos_phi = math.cos(phi_rad)
        sin_phi = math.sin(phi_rad)
        
        dx = (x1 - x2) / 2
        dy = (y1 - y2) / 2
        
        x1p = cos_phi * dx + sin_phi * dy
        y1p = -sin_phi * dx + cos_phi * dy
        
        # Ensure radii are large enough
        rx = abs(rx)
        ry = abs(ry)
        
        lambda_value = (x1p / rx) ** 2 + (y1p / ry) ** 2
        if lambda_value > 1:
            rx *= math.sqrt(lambda_value)
            ry *= math.sqrt(lambda_value)
        
        # Step 2: Compute the center
        sign = -1 if large_arc == sweep else 1
        sq = ((rx*ry)**2 - (rx*y1p)**2 - (ry*x1p)**2) / ((rx*y1p)**2 + (ry*x1p)**2)
        sq = max(0, sq)  # Ensure non-negative
        coef = sign * math.sqrt(sq)
        
        cxp = coef * rx * y1p / ry
        cyp = coef * -ry * x1p / rx
        
        # Step 3: Transform the center back
        cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2
        cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2
        
        # Step 4: Compute the start and sweep angles
        ux = (x1p - cxp) / rx
        uy = (y1p - cyp) / ry
        vx = (-x1p - cxp) / rx
        vy = (-y1p - cyp) / ry
        
        # Start angle
        n = math.sqrt(ux*ux + uy*uy)
        p = ux  # cos(theta)
        theta = math.acos(p/n) if uy >= 0 else -math.acos(p/n)
        theta_deg = theta * 180 / math.pi
        
        # Sweep angle
        n = math.sqrt((ux*ux + uy*uy) * (vx*vx + vy*vy))
        p = ux * vx + uy * vy
        d = p/n
        d = max(-1, min(1, d))  # Clamp to [-1, 1]
        delta = math.acos(d)
        
        if ux * vy - uy * vx < 0:
            delta = -delta
        
        delta_deg = delta * 180 / math.pi
        
        if sweep == 0 and delta > 0:
            delta -= 360
        elif sweep == 1 and delta < 0:
            delta += 360
        
        # Generate points along the arc
        points = []
        num_steps = max(int(abs(delta_deg) / 5), num_segments)
        
        for i in range(1, num_steps + 1):
            angle = theta + delta * i / num_steps
            
            # Point on the ellipse
            x = rx * math.cos(angle)
            y = ry * math.sin(angle)
            
            # Rotate and translate
            px = cos_phi * x - sin_phi * y + cx
            py = sin_phi * x + cos_phi * y + cy
            
            points.append(Point(px, py))
        
        return points
    
    @staticmethod
    def simplify_path(path_data, tolerance=0.5):
        """Simplify a path using the Ramer-Douglas-Peucker algorithm."""
        # First convert the path to points
        points = PathProcessor.process_path(path_data)
        
        if len(points) <= 2:
            return path_data  # Can't simplify further
        
        # Apply the Ramer-Douglas-Peucker algorithm
        simplified_points = PathProcessor.rdp_simplify(points, tolerance)
        
        # Convert back to path data
        if simplified_points:
            path = f"M {simplified_points[0].x},{simplified_points[0].y}"
            for point in simplified_points[1:]:
                path += f" L {point.x},{point.y}"
            
            # Check if the original path was closed
            if path_data.strip().upper().endswith('Z'):
                path += " Z"
            
            return path
        
        return path_data
    
    @staticmethod
    def rdp_simplify(points, epsilon):
        """Ramer-Douglas-Peucker algorithm for path simplification."""
        if len(points) <= 2:
            return points
        
        # Find the point with the maximum distance
        dmax = 0
        index = 0
        
        for i in range(1, len(points) - 1):
            d = PathProcessor.perpendicular_distance(points[i], points[0], points[-1])
            if d > dmax:
                index = i
                dmax = d
        
        # If max distance is greater than epsilon, recursively simplify
        if dmax > epsilon:
            # Recursive call
            rec_results1 = PathProcessor.rdp_simplify(points[:index + 1], epsilon)
            rec_results2 = PathProcessor.rdp_simplify(points[index:], epsilon)
            
            # Build the result list
            result = rec_results1[:-1] + rec_results2
        else:
            result = [points[0], points[-1]]
        
        return result
    
    @staticmethod
    def perpendicular_distance(point, line_start, line_end):
        """Calculate the perpendicular distance from a point to a line."""
        if line_start == line_end:
            return math.sqrt((point.x - line_start.x) ** 2 + (point.y - line_start.y) ** 2)
        
        # Calculate the perpendicular distance
        numerator = abs((line_end.y - line_start.y) * point.x - 
                        (line_end.x - line_start.x) * point.y + 
                        line_end.x * line_start.y - 
                        line_end.y * line_start.x)
        
        denominator = math.sqrt((line_end.y - line_start.y) ** 2 + 
                               (line_end.x - line_start.x) ** 2)
        
        return numerator / denominator 
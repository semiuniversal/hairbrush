#!/usr/bin/env python3
"""
Test the improved path processing implementation.

This script tests the improved path processing implementation with various SVG paths.
"""

import sys
import os
import math
from pathlib import Path

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, src_dir)

try:
    from hairbrush.path_processor import PathProcessor, PathSegment, PathCommand
except ImportError as e:
    print(f"Error importing hairbrush modules: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)


def test_adaptive_bezier_segmentation():
    """Test the adaptive Bezier segmentation algorithm."""
    print("\n=== Testing Adaptive Bezier Segmentation ===")
    
    # Test cases with different curve complexities
    test_cases = [
        # Simple curve (almost straight)
        {
            'start': (0, 0),
            'control_points': [(10, 1), (20, -1)],
            'end': (30, 0)
        },
        # Medium curve
        {
            'start': (0, 0),
            'control_points': [(10, 20), (20, 20)],
            'end': (30, 0)
        },
        # Complex curve (sharp turn)
        {
            'start': (0, 0),
            'control_points': [(0, 30), (30, 30)],
            'end': (30, 0)
        },
        # Quadratic curve
        {
            'start': (0, 0),
            'control_points': [(15, 30)],
            'end': (30, 0)
        }
    ]
    
    for i, case in enumerate(test_cases):
        segments = PathProcessor._adaptive_bezier_segmentation(
            case['start'], 
            case['control_points'], 
            case['end'],
            max_error=0.1,
            min_segments=5,
            max_segments=100
        )
        
        print(f"Case {i+1}: {len(case['control_points'])} control points - {segments} segments")


def test_arc_approximation():
    """Test the elliptical arc approximation algorithm."""
    print("\n=== Testing Arc Approximation ===")
    
    # Test cases with different arc parameters
    test_cases = [
        # Simple 90-degree arc
        {
            'start': (0, 0),
            'rx': 10,
            'ry': 10,
            'x_axis_rotation': 0,
            'large_arc_flag': 0,
            'sweep_flag': 1,
            'end': (10, 10)
        },
        # Elliptical arc
        {
            'start': (0, 0),
            'rx': 20,
            'ry': 10,
            'x_axis_rotation': 45,
            'large_arc_flag': 0,
            'sweep_flag': 1,
            'end': (20, 10)
        },
        # Large arc flag
        {
            'start': (0, 0),
            'rx': 10,
            'ry': 10,
            'x_axis_rotation': 0,
            'large_arc_flag': 1,
            'sweep_flag': 1,
            'end': (10, 10)
        }
    ]
    
    for i, case in enumerate(test_cases):
        points = PathProcessor._approximate_arc(
            case['start'],
            case['rx'],
            case['ry'],
            case['x_axis_rotation'],
            case['large_arc_flag'],
            case['sweep_flag'],
            case['end'],
            segments=20
        )
        
        print(f"Case {i+1}: {len(points)} points generated")
        print(f"  First point: {points[0]}")
        print(f"  Last point: {points[-1]}")


def test_path_to_polyline():
    """Test the path_to_polyline method with various SVG paths."""
    print("\n=== Testing Path to Polyline Conversion ===")
    
    # Test cases with different SVG path commands
    test_cases = [
        # Simple path with lines
        "M 10,10 L 20,20 H 30 V 10 Z",
        # Path with cubic Bezier curves
        "M 10,10 C 20,20 30,20 40,10",
        # Path with quadratic Bezier curves
        "M 10,10 Q 25,25 40,10",
        # Path with arcs
        "M 10,10 A 10,10 0 0 1 20,20",
        # Path with mixed commands
        "M 10,10 L 20,10 C 30,10 30,20 20,20 Z"
    ]
    
    for i, path_data in enumerate(test_cases):
        segments = PathProcessor.parse_path(path_data)
        polyline = PathProcessor.path_to_polyline(segments, curve_resolution=10)
        
        print(f"Case {i+1}: {path_data}")
        print(f"  Segments: {len(segments)}")
        print(f"  Polyline points: {len(polyline)}")
        print(f"  First point: {polyline[0]}")
        print(f"  Last point: {polyline[-1]}")


def test_coordinate_transformation():
    """Test coordinate transformation between SVG and G-code space."""
    print("\n=== Testing Coordinate Transformation ===")
    
    # Import the GCodeGenerator
    try:
        from hairbrush.gcode_generator import GCodeGenerator
    except ImportError as e:
        print(f"Error importing GCodeGenerator: {e}")
        return
    
    # Test cases with different SVG document properties
    test_cases = [
        # Simple case: viewBox only
        {
            'viewbox': (0, 0, 100, 100),
            'width': None,
            'height': None,
            'points': [(0, 0), (50, 50), (100, 100)]
        },
        # With document dimensions
        {
            'viewbox': (0, 0, 100, 100),
            'width': 200,
            'height': 200,
            'points': [(0, 0), (50, 50), (100, 100)]
        },
        # With offset viewBox
        {
            'viewbox': (10, 10, 80, 80),
            'width': 160,
            'height': 160,
            'points': [(10, 10), (50, 50), (90, 90)]
        },
        # With user scaling and offset
        {
            'viewbox': (0, 0, 100, 100),
            'width': 100,
            'height': 100,
            'user_scale': 2.0,
            'user_offset_x': 10,
            'user_offset_y': 20,
            'points': [(0, 0), (50, 50), (100, 100)]
        }
    ]
    
    for i, case in enumerate(test_cases):
        gcode_gen = GCodeGenerator()
        gcode_gen.set_svg_document_properties(case['viewbox'], case['width'], case['height'])
        
        if 'user_scale' in case:
            gcode_gen.set_user_transform(case['user_scale'], 
                                         case.get('user_offset_x', 0), 
                                         case.get('user_offset_y', 0))
        
        print(f"Case {i+1}:")
        print(f"  viewBox: {case['viewbox']}")
        print(f"  width: {case['width']}, height: {case['height']}")
        
        if 'user_scale' in case:
            print(f"  user_scale: {case['user_scale']}")
            print(f"  user_offset: ({case.get('user_offset_x', 0)}, {case.get('user_offset_y', 0)})")
        
        for point in case['points']:
            transformed = gcode_gen.transform_coordinates(point[0], point[1])
            print(f"  {point} -> {transformed}")


def main():
    """Main entry point for the script."""
    print("Testing Improved Path Processing Implementation")
    print("=============================================")
    
    test_adaptive_bezier_segmentation()
    test_arc_approximation()
    test_path_to_polyline()
    test_coordinate_transformation()


if __name__ == "__main__":
    main() 
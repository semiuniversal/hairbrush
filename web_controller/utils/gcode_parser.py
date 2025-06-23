#!/usr/bin/env python3
"""
G-code Parser Utility Module

Provides functions for parsing and analyzing G-code files.
"""

import re
import os
import logging
from typing import Dict, List, Optional, Any, Tuple, Iterator

logger = logging.getLogger(__name__)

# Regular expressions for G-code parsing
MOVE_REGEX = re.compile(r'G[0-1]\s+(?:[XYZ][-+]?\d*\.?\d+\s*)+(?:F\d+)?')
COMMENT_REGEX = re.compile(r';.*')
BRUSH_REGEX = re.compile(r'M4[23]\s+P\d+\s+S\d+')
SERVO_REGEX = re.compile(r'M280\s+P\d+\s+S\d+')

class GCodeAnalyzer:
    """Analyzes G-code files to extract information and statistics."""
    
    def __init__(self, file_path: str):
        """
        Initialize the analyzer with a G-code file.
        
        Args:
            file_path: Path to the G-code file
        """
        self.file_path = file_path
        self.stats: Dict[str, Any] = {}
        self.bounds: Dict[str, Tuple[float, float]] = {
            'X': (float('inf'), float('-inf')),
            'Y': (float('inf'), float('-inf')),
            'Z': (float('inf'), float('-inf'))
        }
        self.current_pos: Dict[str, float] = {'X': 0, 'Y': 0, 'Z': 0}
        self.total_travel = 0.0
        self.move_count = 0
        self.brush_changes = 0
        self.estimated_time = 0.0
        self.layer_count = 0
        
        # Analyze the file
        self._analyze()
    
    def _analyze(self) -> None:
        """Analyze the G-code file to extract statistics."""
        try:
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
                
                prev_z = None
                prev_pos = {'X': 0, 'Y': 0, 'Z': 0}
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith(';'):
                        continue
                    
                    # Extract position from move commands
                    if re.match(r'G[0-1]', line):
                        # Extract X, Y, Z coordinates
                        for axis in ['X', 'Y', 'Z']:
                            match = re.search(f'{axis}([-+]?\d*\.?\d+)', line)
                            if match:
                                pos = float(match.group(1))
                                self.current_pos[axis] = pos
                                
                                # Update bounds
                                self.bounds[axis] = (
                                    min(self.bounds[axis][0], pos),
                                    max(self.bounds[axis][1], pos)
                                )
                        
                        # Count layer changes
                        if prev_z is not None and self.current_pos['Z'] != prev_z:
                            self.layer_count += 1
                        
                        prev_z = self.current_pos['Z']
                        
                        # Calculate travel distance
                        distance = sum((self.current_pos[axis] - prev_pos[axis]) ** 2 
                                      for axis in ['X', 'Y', 'Z']) ** 0.5
                        self.total_travel += distance
                        
                        # Update previous position
                        prev_pos = self.current_pos.copy()
                        
                        self.move_count += 1
                    
                    # Count brush changes
                    if BRUSH_REGEX.match(line) or SERVO_REGEX.match(line):
                        self.brush_changes += 1
            
            # Calculate estimated time (very rough estimate)
            # Assuming average speed of 1000 mm/min
            self.estimated_time = self.total_travel / 1000 * 60  # seconds
            
            # Compile statistics
            self.stats = {
                'filename': os.path.basename(self.file_path),
                'file_size': os.path.getsize(self.file_path),
                'bounds': self.bounds,
                'dimensions': {
                    'X': self.bounds['X'][1] - self.bounds['X'][0],
                    'Y': self.bounds['Y'][1] - self.bounds['Y'][0],
                    'Z': self.bounds['Z'][1] - self.bounds['Z'][0]
                },
                'total_travel': self.total_travel,
                'move_count': self.move_count,
                'brush_changes': self.brush_changes,
                'estimated_time': self.estimated_time,
                'layer_count': self.layer_count
            }
            
            logger.info(f"Analyzed G-code file: {self.file_path}")
            
        except Exception as e:
            logger.error(f"Error analyzing G-code file: {e}")
            self.stats = {'error': str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the G-code file.
        
        Returns:
            dict: Statistics about the G-code file
        """
        return self.stats
    
    def get_preview_points(self, max_points: int = 1000) -> List[Dict[str, float]]:
        """
        Get a list of points for preview visualization.
        
        Args:
            max_points: Maximum number of points to return
            
        Returns:
            list: List of points as dictionaries with X, Y, Z coordinates
        """
        points = []
        
        try:
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
                
                # Calculate sampling rate to stay under max_points
                move_lines = [line for line in lines if re.match(r'G[0-1]', line.strip())]
                sample_rate = max(1, len(move_lines) // max_points)
                
                current_pos = {'X': 0, 'Y': 0, 'Z': 0}
                
                for i, line in enumerate(move_lines):
                    if i % sample_rate != 0:
                        continue
                    
                    # Extract X, Y, Z coordinates
                    for axis in ['X', 'Y', 'Z']:
                        match = re.search(f'{axis}([-+]?\d*\.?\d+)', line)
                        if match:
                            current_pos[axis] = float(match.group(1))
                    
                    points.append(current_pos.copy())
            
            return points
        
        except Exception as e:
            logger.error(f"Error extracting preview points: {e}")
            return []

def parse_gcode(file_path: str) -> Iterator[Dict[str, Any]]:
    """
    Parse a G-code file and yield commands.
    
    Args:
        file_path: Path to the G-code file
        
    Yields:
        dict: Parsed command with type, parameters, and original line
    """
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Extract comment
                comment_match = COMMENT_REGEX.search(line)
                comment = comment_match.group(0)[1:].strip() if comment_match else None
                
                # Remove comment from line
                if comment_match:
                    line = line[:comment_match.start()].strip()
                
                # Skip lines that are only comments
                if not line:
                    yield {
                        'type': 'comment',
                        'comment': comment,
                        'line': line_num,
                        'original': f";{comment}" if comment else ""
                    }
                    continue
                
                # Parse command
                cmd_parts = line.split()
                if not cmd_parts:
                    continue
                
                cmd_type = cmd_parts[0]
                params = {}
                
                # Extract parameters
                for part in cmd_parts[1:]:
                    if len(part) >= 2 and part[0].isalpha():
                        try:
                            params[part[0]] = float(part[1:])
                        except ValueError:
                            params[part[0]] = part[1:]
                
                yield {
                    'type': cmd_type,
                    'params': params,
                    'comment': comment,
                    'line': line_num,
                    'original': line + (f" ;{comment}" if comment else "")
                }
    
    except Exception as e:
        logger.error(f"Error parsing G-code file: {e}")
        yield {'type': 'error', 'error': str(e)}

def estimate_print_time(file_path: str) -> float:
    """
    Estimate print time for a G-code file.
    
    Args:
        file_path: Path to the G-code file
        
    Returns:
        float: Estimated print time in seconds
    """
    analyzer = GCodeAnalyzer(file_path)
    return analyzer.estimated_time 
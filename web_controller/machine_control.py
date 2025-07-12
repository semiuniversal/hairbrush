#!/usr/bin/env python3
"""
Machine Control Module

Provides high-level machine control functions for the H.Airbrush machine.
"""

import logging
import time
import yaml
import os
from typing import Dict, List, Optional, Any, Tuple

# Import the config module directly
import config

logger = logging.getLogger(__name__)

class MachineControl:
    """
    High-level machine control for the H.Airbrush machine.
    
    Provides functions for:
    - Manual jog control
    - Brush control (air on/off, paint on/off)
    - Maintenance routines (parking, cleaning, calibration)
    - Emergency stop
    """
    
    def __init__(self, duet_client):
        """
        Initialize the machine control.
        
        Args:
            duet_client: Duet client instance
        """
        self.duet_client = duet_client
        self.config = config.config
        
        # Machine state
        self.is_homed = False
        self.position = {"X": 0, "Y": 0, "Z": 0}
        self.brush_state = {
            "a": {"air": False, "paint": False},
            "b": {"air": False, "paint": False}
        }
    
    def update_status(self) -> Dict[str, Any]:
        """
        Update machine status from Duet.
        
        Returns:
            dict: Current machine status
        """
        # Get position using M114
        position_result = self.duet_client.get_position()
        if position_result["status"] == "success":
            self.position = position_result["position"]
        
        # Get general status via HTTP API
        status = self.duet_client.get_status()
        
        # Update homing status
        if "axesHomed" in status:
            self.is_homed = all(status["axesHomed"])
        
        return {
            "position": self.position,
            "is_homed": self.is_homed,
            "brush_state": self.brush_state
        }
    
    def home(self) -> Dict[str, Any]:
        """
        Home all axes.
        
        Returns:
            dict: Response with status and message
        """
        result = self.duet_client.send_command_and_wait("G28")
        
        if result.get("status") == "success":
            self.is_homed = True
            logger.info("Machine homed")
            return {"status": "success", "message": "Machine homed"}
        else:
            logger.error(f"Failed to home machine: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def jog(self, axis: str, distance: float, speed: float = 1000) -> Dict[str, Any]:
        """
        Jog an axis by a specific distance.
        
        Args:
            axis: Axis to jog (X, Y, Z)
            distance: Distance to jog in mm
            speed: Movement speed in mm/min
            
        Returns:
            dict: Response with status and message
        """
        if axis not in ["X", "Y", "Z"]:
            return {"status": "error", "message": f"Invalid axis: {axis}"}
        
        # Check if machine is homed
        if not self.is_homed:
            return {"status": "error", "message": "Machine not homed"}
        
        # Send jog command and wait for completion
        command = f"G1 {axis}{distance} F{speed}"
        result = self.duet_client.send_command_and_wait(command)
        
        if result.get("status") == "success":
            # Update position
            position_result = self.duet_client.get_position()
            if position_result["status"] == "success":
                self.position = position_result["position"]
            else:
                # Estimate position if we can't get it
                self.position[axis] += distance
                
            logger.info(f"Jogged {axis} by {distance} mm at {speed} mm/min")
            return {
                "status": "success", 
                "message": f"Jogged {axis} by {distance} mm",
                "position": self.position
            }
        else:
            logger.error(f"Failed to jog {axis}: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def move_to(self, x: Optional[float] = None, y: Optional[float] = None, 
                z: Optional[float] = None, speed: float = 1000) -> Dict[str, Any]:
        """
        Move to a specific position.
        
        Args:
            x: X position in mm (None to keep current)
            y: Y position in mm (None to keep current)
            z: Z position in mm (None to keep current)
            speed: Movement speed in mm/min
            
        Returns:
            dict: Response with status and message
        """
        # Check if machine is homed
        if not self.is_homed:
            return {"status": "error", "message": "Machine not homed"}
        
        # Build command
        command_parts = ["G1"]
        if x is not None:
            command_parts.append(f"X{x}")
        if y is not None:
            command_parts.append(f"Y{y}")
        if z is not None:
            command_parts.append(f"Z{z}")
        
        command_parts.append(f"F{speed}")
        command = " ".join(command_parts)
        
        # Send command and wait for completion
        result = self.duet_client.send_command_and_wait(command)
        
        if result.get("status") == "success":
            # Update position from machine
            position_result = self.duet_client.get_position()
            if position_result["status"] == "success":
                self.position = position_result["position"]
            else:
                # Estimate position if we can't get it
                if x is not None:
                    self.position["X"] = x
                if y is not None:
                    self.position["Y"] = y
                if z is not None:
                    self.position["Z"] = z
            
            logger.info(f"Moved to position {self.position}")
            return {
                "status": "success", 
                "message": "Moved to position",
                "position": self.position
            }
        else:
            logger.error(f"Failed to move: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def set_brush_air(self, brush: str, state: bool) -> Dict[str, Any]:
        """
        Turn brush air on or off.
        
        Args:
            brush: Brush ID ('a' or 'b')
            state: True to turn on, False to turn off
            
        Returns:
            dict: Response with status and message
        """
        if brush not in ["a", "b"]:
            return {"status": "error", "message": f"Invalid brush: {brush}"}
        
        brush_config = self.config.get(f"brush_{brush}")
        if not brush_config:
            return {"status": "error", "message": f"Brush {brush} not configured"}
        
        command = brush_config["air_on"] if state else brush_config["air_off"]
        result = self.duet_client.send_command_and_wait(command)
        
        if result.get("status") == "success":
            self.brush_state[brush]["air"] = state
            action = "on" if state else "off"
            logger.info(f"Turned brush {brush} air {action}")
            return {"status": "success", "message": f"Brush {brush} air turned {action}"}
        else:
            logger.error(f"Failed to set brush {brush} air: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def set_brush_paint(self, brush: str, state: bool) -> Dict[str, Any]:
        """
        Turn brush paint on or off.
        
        Args:
            brush: Brush ID ('a' or 'b')
            state: True to turn on, False to turn off
            
        Returns:
            dict: Response with status and message
        """
        if brush not in ["a", "b"]:
            return {"status": "error", "message": f"Invalid brush: {brush}"}
        
        brush_config = self.config.get(f"brush_{brush}")
        if not brush_config:
            return {"status": "error", "message": f"Brush {brush} not configured"}
        
        command = brush_config["paint_on"] if state else brush_config["paint_off"]
        result = self.duet_client.send_command_and_wait(command)
        
        if result.get("status") == "success":
            self.brush_state[brush]["paint"] = state
            action = "on" if state else "off"
            logger.info(f"Turned brush {brush} paint {action}")
            return {"status": "success", "message": f"Brush {brush} paint turned {action}"}
        else:
            logger.error(f"Failed to set brush {brush} paint: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def set_brush_paint_flow(self, brush: str, percentage: float) -> Dict[str, Any]:
        """
        Set the paint flow for a brush as a percentage.
        
        Args:
            brush: Brush ID ('a' or 'b')
            percentage: Flow percentage (0-100)
            
        Returns:
            dict: Response with status and message
        """
        if brush not in ["a", "b"]:
            return {"status": "error", "message": f"Invalid brush: {brush}"}
        
        # Clamp percentage to 0-100 range
        percentage = max(0, min(100, percentage))
        
        # Get min and max servo angles from config
        paint_min = self.config["brushes"][brush]["paint_min"]
        paint_max = self.config["brushes"][brush]["paint_max"]
        
        # Calculate servo angle based on percentage, handling reversed limits
        if paint_max > paint_min:
            # Normal case: min to max
            servo_angle = paint_min + (percentage / 100) * (paint_max - paint_min)
        else:
            # Reversed case: max is lower than min
            servo_angle = paint_min - (percentage / 100) * (paint_min - paint_max)
        
        servo_angle = round(servo_angle)  # Round to nearest integer
        
        # Determine servo pin based on brush
        servo_pin = 0 if brush == "a" else 1
        
        # Send command to set servo angle
        command = f"M280 P{servo_pin} S{servo_angle}"
        result = self.duet_client.send_command_and_wait(command)
        
        if result.get("status") == "success":
            # Update brush state - paint is on if percentage > 0
            self.brush_state[brush]["paint"] = percentage > 0
            
            logger.info(f"Set brush {brush} paint flow to {percentage}% (servo angle: {servo_angle})")
            return {
                "status": "success", 
                "message": f"Brush {brush} paint flow set to {percentage}%",
                "servo_angle": servo_angle
            }
        else:
            logger.error(f"Failed to set brush {brush} paint flow: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def park(self) -> Dict[str, Any]:
        """
        Park the machine (move to a safe position).
        
        Returns:
            dict: Response with status and message
        """
        # Check if machine is homed
        if not self.is_homed:
            return {"status": "error", "message": "Machine not homed"}
        
        # First, raise Z axis to a safe height
        z_result = self.move_to(z=10, speed=500)
        if z_result["status"] == "error":
            return z_result
        
        # Then move to park position
        result = self.move_to(x=0, y=0, speed=3000)
        
        if result["status"] == "success":
            logger.info("Machine parked")
            return {"status": "success", "message": "Machine parked"}
        else:
            logger.error(f"Failed to park machine: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def clean_brush(self, brush: str) -> Dict[str, Any]:
        """
        Run the cleaning routine for a brush.
        
        Args:
            brush: Brush ID ('a' or 'b')
            
        Returns:
            dict: Response with status and message
        """
        if brush not in ["a", "b"]:
            return {"status": "error", "message": f"Invalid brush: {brush}"}
        
        # Check if machine is homed
        if not self.is_homed:
            return {"status": "error", "message": "Machine not homed"}
        
        # First, raise Z axis to a safe height
        z_result = self.move_to(z=10, speed=500)
        if z_result["status"] == "error":
            return z_result
        
        # Move to cleaning position
        move_result = self.move_to(x=250, y=250, speed=3000)
        if move_result["status"] == "error":
            return move_result
        
        # Lower Z axis to cleaning position
        z_result = self.move_to(z=5, speed=500)
        if z_result["status"] == "error":
            return z_result
        
        # Turn on air
        air_result = self.set_brush_air(brush, True)
        if air_result["status"] == "error":
            return air_result
        
        # Wait for 2 seconds
        time.sleep(2)
        
        # Turn off air
        air_result = self.set_brush_air(brush, False)
        if air_result["status"] == "error":
            return air_result
        
        # Raise Z axis to safe height
        z_result = self.move_to(z=10, speed=500)
        if z_result["status"] == "error":
            return z_result
        
        logger.info(f"Cleaned brush {brush}")
        return {"status": "success", "message": f"Brush {brush} cleaned"}
    
    def emergency_stop(self) -> Dict[str, Any]:
        """
        Emergency stop the machine.
        
        Returns:
            dict: Response with status and message
        """
        # Send M112 emergency stop command
        result = self.duet_client.send_command("M112")
        
        # Reset machine state
        self.is_homed = False
        
        # Turn off all brushes
        for brush in ["a", "b"]:
            self.brush_state[brush]["air"] = False
            self.brush_state[brush]["paint"] = False
        
        logger.warning("Emergency stop triggered")
        return {"status": "success", "message": "Emergency stop triggered"}
    
    def calibrate(self) -> Dict[str, Any]:
        """
        Run the calibration routine.
        
        Returns:
            dict: Response with status and message
        """
        # Home all axes
        home_result = self.home()
        if home_result["status"] == "error":
            return home_result
        
        # Move to center position
        move_result = self.move_to(x=150, y=150, z=10, speed=3000)
        if move_result["status"] == "error":
            return move_result
        
        # Test brush A
        brush_a_result = self._test_brush("a")
        if brush_a_result["status"] == "error":
            return brush_a_result
        
        # Test brush B
        brush_b_result = self._test_brush("b")
        if brush_b_result["status"] == "error":
            return brush_b_result
        
        # Return to safe position
        park_result = self.park()
        if park_result["status"] == "error":
            return park_result
        
        logger.info("Calibration completed")
        return {"status": "success", "message": "Calibration completed"}
    
    def _test_brush(self, brush: str) -> Dict[str, Any]:
        """
        Test a brush by cycling air and paint.
        
        Args:
            brush: Brush ID ('a' or 'b')
            
        Returns:
            dict: Response with status and message
        """
        # Turn on air
        air_result = self.set_brush_air(brush, True)
        if air_result["status"] == "error":
            return air_result
        
        # Wait for 1 second
        time.sleep(1)
        
        # Turn on paint
        paint_result = self.set_brush_paint(brush, True)
        if paint_result["status"] == "error":
            return paint_result
        
        # Wait for 1 second
        time.sleep(1)
        
        # Turn off paint
        paint_result = self.set_brush_paint(brush, False)
        if paint_result["status"] == "error":
            return paint_result
        
        # Wait for 1 second
        time.sleep(1)
        
        # Turn off air
        air_result = self.set_brush_air(brush, False)
        if air_result["status"] == "error":
            return air_result
        
        return {"status": "success", "message": f"Brush {brush} tested"}
    
    def process_gcode_file(self, filename: str) -> Dict[str, Any]:
        """
        Process a G-code file with awareness of synchronization points (M400).
        
        This method reads a G-code file and executes it line by line,
        properly handling M400 commands as synchronization points.
        
        Args:
            filename: Path to the G-code file
            
        Returns:
            dict: Response with status and message
        """
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                
            total_lines = len(lines)
            processed_lines = 0
            
            logger.info(f"Processing G-code file: {filename} ({total_lines} lines)")
            
            for line in lines:
                # Strip comments and whitespace
                command = line.split(';')[0].strip()
                
                if not command:
                    # Skip empty lines or comment-only lines
                    processed_lines += 1
                    continue
                
                # Check if this is a synchronization command (M400)
                if command.upper().startswith("M400"):
                    # Wait for all previous commands to complete
                    result = self.duet_client.wait_for_motion_complete()
                    if result.get("status") != "success":
                        logger.error(f"Error waiting for motion to complete: {result.get('message')}")
                        return {"status": "error", "message": f"Error at line {processed_lines}: {result.get('message')}"}
                else:
                    # Send the command without waiting (the M400 commands in the file will handle synchronization)
                    result = self.duet_client.send_command(command)
                    if result.get("status") != "success":
                        logger.error(f"Error executing command '{command}': {result.get('message')}")
                        return {"status": "error", "message": f"Error at line {processed_lines}: {result.get('message')}"}
                
                processed_lines += 1
                
                # Update progress periodically
                if processed_lines % 10 == 0:
                    progress = (processed_lines / total_lines) * 100
                    logger.debug(f"G-code progress: {progress:.1f}% ({processed_lines}/{total_lines})")
            
            # Ensure all commands are completed at the end
            final_result = self.duet_client.wait_for_motion_complete()
            
            logger.info(f"G-code file processing complete: {filename}")
            return {"status": "success", "message": f"G-code file processed successfully ({total_lines} lines)"}
            
        except Exception as e:
            logger.error(f"Error processing G-code file: {e}")
            return {"status": "error", "message": f"Failed to process G-code file: {e}"} 
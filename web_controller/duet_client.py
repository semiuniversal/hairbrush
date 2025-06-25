#!/usr/bin/env python3
"""
Duet Client Module

Handles communication with the Duet 2 WiFi board via HTTP API.
"""

import time
import json
import logging
import requests
import urllib.parse
from typing import Dict, List, Optional, Union, Any, Tuple

logger = logging.getLogger(__name__)

class DuetClient:
    """
    Client for communicating with Duet 2 WiFi board using HTTP API.
    
    Supports:
    - HTTP API for G-code commands and status monitoring
    - Session management for RRF 3.x firmware
    """
    
    def __init__(self, host: str = '192.168.1.1', 
                 http_port: int = 80, connect_timeout: int = 5, 
                 password: str = "", auto_connect: bool = True):
        """
        Initialize the Duet client.
        
        Args:
            host: Duet IP address or hostname
            http_port: HTTP port (default: 80)
            connect_timeout: Connection timeout in seconds
            password: Duet web password (if set)
            auto_connect: Whether to connect automatically on initialization
        """
        self.host = host
        self.http_port = http_port
        self.connect_timeout = connect_timeout
        self.password = password
        
        self.connected = False
        self.last_status: Dict[str, Any] = {}
        
        # Create a session for persistent cookies
        self.session = requests.Session()
        
        # Try to connect if auto_connect is True
        if auto_connect:
            self.connect()
    
    def connect(self) -> bool:
        """
        Connect to the Duet board via HTTP and establish a session.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Attempting to connect to Duet at {self.host}:{self.http_port}")
            
            # Establish connection and get session cookie (if any)
            connect_url = f"http://{self.host}:{self.http_port}/rr_connect?password={self.password}"
            logger.debug(f"Sending request to: {connect_url}")
            
            response = self.session.get(connect_url, timeout=self.connect_timeout)
            logger.debug(f"rr_connect response status: {response.status_code}")
            logger.debug(f"rr_connect response text: {response.text}")
            logger.debug(f"rr_connect response headers: {response.headers}")
            logger.debug(f"Session cookies: {self.session.cookies.get_dict()}")
            
            response.raise_for_status()
            
            # Check if connection was successful
            try:
                response_json = response.json()
                if response_json.get("err", 0) != 0:
                    logger.error(f"Failed to connect: {response.text}")
                    self.connected = False
                    return False
                
                # Log board info if available
                if "boardType" in response_json:
                    logger.info(f"Connected to board type: {response_json['boardType']}")
                if "apiLevel" in response_json:
                    logger.info(f"API level: {response_json['apiLevel']}")
                
            except ValueError:
                # Not JSON or invalid JSON
                if "err" in response.text.lower():
                    logger.error(f"Failed to connect: {response.text}")
                    self.connected = False
                    return False
            
            # Verify connection by getting status
            status_url = f"http://{self.host}:{self.http_port}/rr_status?type=1"
            logger.debug(f"Getting status from: {status_url}")
            
            status_response = self.session.get(status_url, timeout=self.connect_timeout)
            logger.debug(f"rr_status response status: {status_response.status_code}")
            logger.debug(f"rr_status response text: {status_response.text[:100]}...")  # Truncate long response
            
            status_response.raise_for_status()
            
            # If we get here, HTTP connection is successful
            logger.info(f"Successfully connected to H.Airbrush Plotter at {self.host}:{self.http_port}")
            self.connected = True
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to connect to H.Airbrush Plotter: {e}")
            logger.exception("Connection error details:")
            self.connected = False
            return False
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to the Duet board without establishing a session.
        
        Returns:
            tuple: (success, message)
        """
        try:
            logger.info(f"Testing connection to Duet at {self.host}:{self.http_port}")
            
            # Create a temporary session for testing
            test_session = requests.Session()
            
            # Try to connect
            connect_url = f"http://{self.host}:{self.http_port}/rr_connect?password={self.password}"
            response = test_session.get(connect_url, timeout=self.connect_timeout)
            
            # Check response status
            if response.status_code != 200:
                return False, f"Connection failed with status code: {response.status_code}"
            
            # Try to parse response as JSON
            try:
                response_json = response.json()
                
                # Check for error in response
                if response_json.get("err", 0) != 0:
                    return False, f"Connection error: {response.text}"
                
                # Get board info if available
                board_info = ""
                if "boardType" in response_json:
                    board_info += f"Board: {response_json['boardType']}, "
                if "apiLevel" in response_json:
                    board_info += f"API: {response_json['apiLevel']}"
                
                # Try to get status as well
                try:
                    status_url = f"http://{self.host}:{self.http_port}/rr_status?type=1"
                    status_response = test_session.get(status_url, timeout=self.connect_timeout)
                    status_response.raise_for_status()
                    
                    # Successfully got status
                    return True, f"Connected successfully. {board_info}"
                    
                except requests.RequestException:
                    # Status request failed but connect succeeded
                    return True, f"Connected, but status request failed. {board_info}"
                
            except ValueError:
                # Not JSON or invalid JSON
                if "err" in response.text.lower():
                    return False, f"Connection error: {response.text}"
                else:
                    # Non-JSON response but might still be valid
                    return True, "Connected, but received unexpected response format"
            
        except requests.RequestException as e:
            logger.error(f"Connection test failed: {e}")
            return False, f"Connection failed: {str(e)}"
    
    def is_connected(self) -> bool:
        """
        Check if the client is connected to the Duet board.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.connected:
            return False
            
        # Try to get status to verify connection is still active
        try:
            status_url = f"http://{self.host}:{self.http_port}/rr_status?type=1"
            response = self.session.get(status_url, timeout=self.connect_timeout)
            response.raise_for_status()
            return True
        except:
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Duet board."""
        if self.connected:
            try:
                # Send disconnect request
                disconnect_url = f"http://{self.host}:{self.http_port}/rr_disconnect"
                self.session.get(disconnect_url, timeout=self.connect_timeout)
            except requests.RequestException as e:
                logger.error(f"Error during disconnect: {e}")
            
            # Clear session
            self.session = requests.Session()
        
        self.connected = False
        logger.info(f"Disconnected from H.Airbrush Plotter at {self.host}")
    
    def send_gcode(self, gcode):
        """Send a G-code command to the Duet board."""
        logger.info(f"Sending G-code: {gcode}")
        
        # Special handling for certain commands
        if gcode.strip().startswith(('M114', 'M119')):
            return self._handle_special_command(gcode)
            
        try:
            # URL encode the G-code command
            encoded_gcode = urllib.parse.quote(gcode)
            url = f"http://{self.host}:{self.http_port}/rr_gcode?gcode={encoded_gcode}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            # Get the response from the command
            reply_response = self.session.get(f"http://{self.host}:{self.http_port}/rr_reply")
            reply_response.raise_for_status()
            
            reply_text = reply_response.text.strip()
            logger.debug(f"Command response: {reply_text}")
            
            return {'status': 'success', 'response': reply_text}
            
        except requests.RequestException as e:
            logger.error(f"Error sending G-code: {e}")
            return {'status': 'error', 'message': str(e)}

    def _handle_special_command(self, gcode):
        """Handle special commands that need specific processing."""
        try:
            # URL encode the G-code command
            encoded_gcode = urllib.parse.quote(gcode)
            url = f"http://{self.host}:{self.http_port}/rr_gcode?gcode={encoded_gcode}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            # Get the response from the command
            reply_response = self.session.get(f"http://{self.host}:{self.http_port}/rr_reply")
            reply_response.raise_for_status()
            
            reply_text = reply_response.text.strip()
            logger.debug(f"Special command response: {reply_text}")
            
            if gcode.strip().startswith('M114'):
                # Process position response
                return self._process_position_response(reply_text)
            elif gcode.strip().startswith('M119'):
                # Process endstop status response
                return self._process_endstop_response(reply_text)
            else:
                return {'status': 'success', 'response': reply_text}
            
        except requests.RequestException as e:
            logger.error(f"Error handling special command: {e}")
            return {'status': 'error', 'message': str(e)}

    def _process_position_response(self, response):
        """Process the position response from M114 command."""
        logger.debug(f"Processing position response: {response}")
        
        # Example: X:0.00 Y:0.00 Z:0.00 E:0.00 Count X:0 Y:0 Z:0
        position = {}
        
        try:
            # Extract X, Y, Z positions
            parts = response.split()
            for part in parts:
                if part.startswith(('X:', 'Y:', 'Z:')):
                    axis, value = part.split(':', 1)
                    position[axis.lower()] = float(value)
            
            return {
                'status': 'success',
                'position': position
            }
        except Exception as e:
            logger.error(f"Error parsing position: {e}")
            return {
                'status': 'error',
                'message': f"Failed to parse position: {e}",
                'response': response
            }

    def _process_endstop_response(self, response):
        """Process the endstop status response from M119 command."""
        logger.debug(f"Processing endstop response: {response}")
        
        # Simply return the raw response for now, client-side will parse it
        return {
            'status': 'success',
            'response': response
        }
    
    def send_command(self, command: str) -> Dict[str, Any]:
        """
        Send a G-code command to the Duet board via HTTP API.
        
        Args:
            command: G-code command to send
            
        Returns:
            dict: Response with status and message
        """
        if not self.connected:
            logger.debug(f"Not connected, attempting to connect before sending command: {command}")
            if not self.connect():
                return {"status": "error", "message": "Not connected to H.Airbrush Plotter"}
        
        try:
            # URL encode the command
            encoded_command = urllib.parse.quote(command)
            logger.debug(f"Sending command: {command} (encoded: {encoded_command})")
            
            # Send command via HTTP API
            url = f"http://{self.host}:{self.http_port}/rr_gcode?gcode={encoded_command}"
            logger.debug(f"Command URL: {url}")
            
            response = self.session.get(url, timeout=5)
            logger.debug(f"Command response status: {response.status_code}")
            logger.debug(f"Command response text: {response.text}")
            
            response.raise_for_status()
            
            # Get the reply from the command
            reply_url = f"http://{self.host}:{self.http_port}/rr_reply"
            logger.debug(f"Getting reply from: {reply_url}")
            
            reply_response = self.session.get(reply_url, timeout=5)
            logger.debug(f"Reply response status: {reply_response.status_code}")
            logger.debug(f"Reply response text: {reply_response.text}")
            
            reply_response.raise_for_status()
            
            return {"status": "success", "response": reply_response.text.strip()}
        
        except requests.RequestException as e:
            logger.error(f"Error sending command '{command}': {e}")
            logger.exception("Command error details:")
            return {"status": "error", "message": str(e)}
    
    def send_command_and_wait(self, command: str) -> Dict[str, Any]:
        """
        Send a G-code command and wait for it to complete execution.
        This adds an M400 after the command to ensure motion completion.
        
        Args:
            command: G-code command to send
            
        Returns:
            dict: Response with status and message
        """
        result = self.send_command(command)
        if result["status"] == "error":
            return result
        
        # Send M400 to wait for motion completion
        return self.wait_for_motion_complete()
    
    def wait_for_motion_complete(self) -> Dict[str, Any]:
        """
        Send M400 to wait for all buffered moves to complete.
        
        Returns:
            dict: Response with status and message
        """
        return self.send_command("M400")
    
    def get_position(self) -> Dict[str, Any]:
        """
        Get the current position of the machine using HTTP API.
        
        Returns:
            dict: Position information with X, Y, Z coordinates
        """
        if not self.connected:
            if not self.connect():
                return {"status": "error", "message": "Not connected to H.Airbrush Plotter"}
        
        try:
            url = f"http://{self.host}:{self.http_port}/rr_status?type=2"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            status = response.json()
            if 'coords' in status and 'xyz' in status['coords']:
                xyz = status['coords']['xyz']
                if len(xyz) >= 3:
                    position = {
                        'X': xyz[0],
                        'Y': xyz[1],
                        'Z': xyz[2]
                    }
                    return {"status": "success", "position": position}
            
            return {"status": "error", "message": "Could not parse position from response"}
        
        except requests.RequestException as e:
            logger.error(f"Error getting position: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Duet board via HTTP API.
        
        Returns:
            dict: Status information
        """
        if not self.connected:
            if not self.connect():
                return self.last_status or {"status": "error", "message": "Not connected to H.Airbrush Plotter"}
            
        try:
            url = f"http://{self.host}:{self.http_port}/rr_status?type=3"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            status = response.json()
            self.last_status = status
            return status
        
        except requests.RequestException as e:
            logger.error(f"Error getting status: {e}")
            return self.last_status or {"status": "error", "message": str(e)}
    
    def is_homed(self) -> bool:
        """
        Check if all axes are homed.
        
        Returns:
            bool: True if all axes are homed, False otherwise
        """
        try:
            status = self.get_status()
            if isinstance(status, dict) and "axesHomed" in status:
                return all(status["axesHomed"])
            return False
        except Exception as e:
            logger.error(f"Error checking homed status: {e}")
            return False
    
    def are_motors_enabled(self) -> bool:
        """
        Check if motors are enabled.
        
        Returns:
            bool: True if motors are enabled, False otherwise
        """
        try:
            status = self.get_status()
            if isinstance(status, dict) and "status" in status:
                # Different firmware versions use different fields
                if "motors" in status:
                    return status["motors"] == 1
                elif "drive" in status:
                    return status["drive"] == 1
            return False
        except Exception as e:
            logger.error(f"Error checking motor status: {e}")
            return False
    
    def get_file_list(self) -> List[Dict[str, Any]]:
        """
        Get the list of files on the Duet board.
        
        Returns:
            list: List of files with metadata
        """
        if not self.connected:
            if not self.connect():
                return []
            
        try:
            url = f"http://{self.host}:{self.http_port}/rr_filelist"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            files = response.json()
            return files.get('files', [])
        
        except requests.RequestException as e:
            logger.error(f"Error getting file list: {e}")
            return []
    
    def upload_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        """
        Upload a file to the Duet board.
        
        Args:
            filename: Name of the file to upload
            content: File content as bytes
            
        Returns:
            dict: Response with status and message
        """
        if not self.connected:
            if not self.connect():
                return {"status": "error", "message": "Not connected to H.Airbrush Plotter"}
            
        try:
            url = f"http://{self.host}:{self.http_port}/rr_upload?name=0:/gcodes/{filename}"
            response = self.session.post(url, data=content, timeout=30)
            response.raise_for_status()
            
            return {"status": "success", "message": f"File {filename} uploaded"}
        
        except requests.RequestException as e:
            logger.error(f"Error uploading file: {e}")
            return {"status": "error", "message": str(e)}
    
    def __del__(self) -> None:
        """Clean up resources on deletion."""
        if hasattr(self, 'connected') and self.connected:
            self.disconnect() 
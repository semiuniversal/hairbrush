#!/usr/bin/env python3
"""
Serial Communication Service for H.Airbrush Web Controller

Handles serial port communication with the Duet board for initial setup.
"""

import logging
import re
import time
import threading
import os
import platform
import subprocess
from typing import Dict, List, Optional, Any, Callable, Tuple

import serial
import serial.tools.list_ports

logger = logging.getLogger(__name__)

class SerialService:
    """
    Handles serial communication with the Duet board.
    
    Provides functions for:
    - Listing available serial ports
    - Connecting to a port
    - Sending commands
    - Reading responses
    - Parsing IP address from responses
    """
    
    def __init__(self):
        """Initialize the serial service."""
        self.serial_port = None
        self.is_connected = False
        self.port_name = None
        self.baud_rate = 115200
        self.read_thread = None
        self.stop_thread = threading.Event()
        self.data_callback = None
        self.last_found_ip = None  # Store any IP address found in the background thread
        self.ip_found_time = None  # When the IP was found
        
    def _is_wsl(self) -> bool:
        """
        Check if running in WSL environment.
        Only called when needed, not during initialization.
        
        Returns:
            bool: True if running in WSL, False otherwise
        """
        try:
            # Check for WSL-specific indicators without being intrusive
            # Look for WSL-specific patterns in release string (more precise than just "microsoft")
            if "microsoft-standard-wsl" in platform.uname().release.lower():
                return True
                
            # Check for WSL interop file - definitive indicator of WSL
            if os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
                return True
                
            # Check for /proc/version mentioning Microsoft
            try:
                with open("/proc/version", "r") as f:
                    if "microsoft" in f.read().lower():
                        return True
            except:
                pass
                
            return False
        except:
            # If any error occurs, assume not WSL
            return False
        
    def list_ports(self) -> List[Dict[str, Any]]:
        """
        List available serial ports.
        
        Returns:
            list: List of dictionaries with port information
        """
        ports = []
        
        # Standard approach - works on all platforms
        try:
            for port in serial.tools.list_ports.comports():
                ports.append({
                    'device': port.device,
                    'description': port.description,
                    'hwid': port.hwid,
                    'manufacturer': port.manufacturer if hasattr(port, 'manufacturer') else None,
                    'product': port.product if hasattr(port, 'product') else None,
                })
            
            logger.info(f"Found {len(ports)} serial ports using pyserial")
        except Exception as e:
            logger.error(f"Error listing serial ports with pyserial: {e}")
        
        # If no ports found and running in WSL, try Windows COM ports as fallback
        if len(ports) == 0 and self._is_wsl():
            logger.info("No ports found with standard method and running in WSL, checking for Windows COM ports")
            try:
                # Use PowerShell to list COM ports
                cmd = ["powershell.exe", "-Command", "[System.IO.Ports.SerialPort]::GetPortNames()"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    com_ports = result.stdout.strip().split('\n')
                    for port in com_ports:
                        if port.strip():
                            ports.append({
                                'device': port.strip(),
                                'description': f"Windows {port.strip()}",
                                'hwid': 'WSL-Windows',
                                'manufacturer': 'Unknown',
                                'product': 'Windows COM Port',
                            })
                    logger.info(f"Found {len(ports)} Windows COM ports")
                else:
                    logger.error(f"Error running PowerShell command: {result.stderr}")
            except Exception as e:
                logger.error(f"Error listing Windows COM ports: {e}")
        
        return ports
    
    def connect(self, port_name: str, baud_rate: int = 115200, 
                data_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Connect to a serial port.
        
        Args:
            port_name: Serial port name
            baud_rate: Baud rate
            data_callback: Callback function for received data
            
        Returns:
            dict: Response with status and message
        """
        if self.is_connected:
            return {"status": "error", "message": "Already connected to a port"}
        
        original_port_name = port_name
        
        try:
            # Handle Windows COM ports in WSL
            if port_name.startswith("COM") and self._is_wsl():
                logger.info(f"WSL environment detected with Windows COM port: {port_name}")
                # In WSL, COM ports need to be accessed via /dev/ttyS + (N-1)
                # For example, COM1 is /dev/ttyS0, COM2 is /dev/ttyS1, etc.
                try:
                    com_number = int(port_name[3:])
                    wsl_port = f"/dev/ttyS{com_number - 1}"
                    
                    # Check if the device exists and is accessible
                    if os.path.exists(wsl_port):
                        if os.access(wsl_port, os.R_OK | os.W_OK):
                            logger.info(f"Mapping Windows {port_name} to WSL {wsl_port}")
                            port_name = wsl_port
                        else:
                            logger.warning(f"WSL device {wsl_port} exists but is not accessible (permission denied)")
                            return {"status": "error", "message": f"Permission denied for {wsl_port}. Try running with sudo or add your user to the dialout group."}
                    else:
                        logger.warning(f"WSL device {wsl_port} does not exist")
                        # Try direct access as fallback (might work with usbipd-win setup)
                        logger.info(f"Trying direct access to {original_port_name} as fallback")
                        port_name = original_port_name
                except ValueError:
                    logger.warning(f"Could not parse COM port number from {port_name}")
            
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            
            self.is_connected = True
            self.port_name = port_name
            self.baud_rate = baud_rate
            self.data_callback = data_callback
            
            # Start read thread
            self.stop_thread.clear()
            self.read_thread = threading.Thread(target=self._read_thread)
            self.read_thread.daemon = True
            self.read_thread.start()
            
            logger.info(f"Connected to {port_name} at {baud_rate} baud")
            return {"status": "success", "message": f"Connected to {port_name}"}
            
        except serial.SerialException as e:
            logger.error(f"Error connecting to {port_name}: {e}")
            
            # Add helpful message for WSL users
            if self._is_wsl() and "Permission denied" in str(e):
                return {"status": "error", "message": f"Permission denied: {str(e)}. In WSL, you may need to run with sudo or use usbipd-win to attach USB devices."}
            
            return {"status": "error", "message": str(e)}
    
    def disconnect(self) -> Dict[str, Any]:
        """
        Disconnect from the serial port.
        
        Returns:
            dict: Response with status and message
        """
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to any port"}
        
        try:
            # Stop read thread
            self.stop_thread.set()
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=1)
            
            # Close port
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.is_connected = False
            port_name = self.port_name
            self.port_name = None
            self.data_callback = None
            
            logger.info(f"Disconnected from {port_name}")
            return {"status": "success", "message": f"Disconnected from {port_name}"}
            
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_command(self, command: str) -> Dict[str, Any]:
        """
        Send a command to the serial port.
        
        Args:
            command: Command to send
            
        Returns:
            dict: Response with status and message
        """
        if not self.is_connected or not self.serial_port:
            return {"status": "error", "message": "Not connected to any port"}
        
        try:
            # Ensure command ends with newline
            if not command.endswith('\n'):
                command += '\n'
            
            # Send command
            self.serial_port.write(command.encode('utf-8'))
            logger.debug(f"Sent command: {command.strip()}")
            
            return {"status": "success", "message": "Command sent"}
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_ip_address(self) -> Dict[str, Any]:
        """
        Send M552 command to get IP address.
        
        Returns:
            dict: Response with status, message, and IP address if found
        """
        if not self.is_connected or not self.serial_port:
            return {"status": "error", "message": "Not connected to any port"}
        
        try:
            # Temporarily pause the read thread
            original_callback = self.data_callback
            self.data_callback = None
            
            # Clear any pending data
            self.serial_port.reset_input_buffer()
            
            # Send M552 command
            result = self.send_command("M552")
            if result["status"] != "success":
                # Restore the callback
                self.data_callback = original_callback
                return result
            
            # Wait for response
            time.sleep(0.5)
            
            # Collect all available data
            all_data = ""
            start_time = time.time()
            
            # Keep reading data for up to 3 seconds
            while time.time() - start_time < 3 and self.serial_port and self.serial_port.is_open:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='replace')
                    all_data += data
                time.sleep(0.1)
            
            # Restore the callback
            self.data_callback = original_callback
            
            # Look for IP address in the response
            match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', all_data)
            if match:
                ip_address = match.group()
                
                # Store this IP address for future use
                self.last_found_ip = ip_address
                self.ip_found_time = time.time()
                
                return {
                    "status": "success", 
                    "message": "IP address found",
                    "ip_address": ip_address,
                    "response": all_data
                }
            else:
                # Check if we have an IP address from the background thread as a fallback
                if self.last_found_ip:
                    return {
                        "status": "success", 
                        "message": "IP address found from background thread",
                        "ip_address": self.last_found_ip,
                        "response": all_data
                    }
                
                return {
                    "status": "warning",
                    "message": "No IP address found in response",
                    "response": all_data
                }
            
        except Exception as e:
            logger.error(f"Error getting IP address: {e}")
            # Make sure to restore the callback in case of error
            if 'original_callback' in locals():
                self.data_callback = original_callback
            return {"status": "error", "message": str(e)}
    
    def _read_thread(self) -> None:
        """Read thread that continuously reads from the serial port."""
        try:
            while not self.stop_thread.is_set() and self.serial_port and self.serial_port.is_open:
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='replace')
                    if data:
                        # Look for IP addresses in the incoming data
                        match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', data)
                        if match:
                            ip_address = match.group()
                            logger.info(f"IP address found in background thread: {ip_address}")
                            
                            # Store the IP address and timestamp
                            self.last_found_ip = ip_address
                            self.ip_found_time = time.time()
                        
                        # Pass data to callback if registered
                        if self.data_callback:
                            self.data_callback(data)
                else:
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in read thread: {e}")
            if self.is_connected:
                self.disconnect() 
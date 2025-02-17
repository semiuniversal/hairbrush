# tinyg_tester/controller.py
from dataclasses import dataclass
import json
import logging
from queue import Queue
import threading
from typing import Dict, Any, Optional

import serial
import yaml

@dataclass
class TinyGConfig:
    port: str
    baud_rate: int
    config: Dict[str, Any]

class TinyGController:
    def __init__(self, config: TinyGConfig):
        self.config = config
        self.serial = None
        self.status_queue = Queue()
        self.running = False
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TinyG')

    def connect(self) -> bool:
        try:
            self.serial = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baud_rate,
                timeout=1
            )
            self.logger.info(f"Connected to {self.config.port}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self) -> None:
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("Disconnected from TinyG")

    def get_current_config(self) -> dict:
        """Query TinyG for current configuration"""
        current_config = {}
        for key in self.config.config.keys():
            command = f"{{{key}}}\n"
            self.serial.write(command.encode())
            response = self.serial.readline()
            try:
                resp_data = json.loads(response.decode().strip())
                # TinyG returns config values in a nested structure
                if 'r' in resp_data and key in resp_data['r']:
                    current_config[key] = resp_data['r'][key]
            except (json.JSONDecodeError, KeyError):
                self.logger.warning(f"Could not parse configuration response for {key}")
        return current_config

    def safe_servo_init(self) -> None:
        """Initialize servos to a safe state"""
        # First disable both servos
        self.send_command("M5")  # Spindle off command disables PWM
        self.logger.info("Servos disabled for safe initialization")
        
        # Set minimum position for both servos
        self.send_command("M3 S0")  # Set servo 1 to minimum
        self.send_command("M4 S0")  # Set servo 2 to minimum
        self.logger.info("Servos initialized to minimum position")

    def apply_config(self) -> None:
        """Apply configuration from YAML to TinyG with verification"""
        self.logger.info("Starting configuration process...")
        
        # Get current configuration
        current_config = self.get_current_config()
        
        # Track changes made
        changes_made = 0
        
        for key, new_value in self.config.config.items():
            current_value = current_config.get(key)
            
            # Special handling for PWM settings
            if key.startswith('p1') and 'sl' in key or 'sh' in key:
                # Ensure servo position values are within safe limits
                if new_value > 1580:  # 15.8 degrees * 100
                    self.logger.warning(f"Limiting {key} to maximum safe value of 1580")
                    new_value = 1580
                elif new_value < 0:
                    self.logger.warning(f"Limiting {key} to minimum safe value of 0")
                    new_value = 0
            
            # Only update if value is different
            if current_value != new_value:
                command = f"{{{key}:{new_value}}}\n"
                self.serial.write(command.encode())
                response = self.serial.readline()
                self.logger.info(f"Updated {key}: {current_value} → {new_value}")
                changes_made += 1
            else:
                self.logger.debug(f"Skipped {key}: already set to {current_value}")
        
        self.logger.info(f"Configuration complete. Made {changes_made} changes.")
        
        # Initialize servos to safe state
        self.safe_servo_init()

    def send_command(self, command: str) -> Optional[str]:
        """Send a command to TinyG and return the response"""
        if not self.serial or not self.serial.is_open:
            self.logger.error("Not connected to TinyG")
            return None
        
        try:
            self.serial.write(f"{command}\n".encode())
            response = self.serial.readline()
            return response.decode().strip()
        except serial.SerialException as e:
            self.logger.error(f"Error sending command: {e}")
            return None

    def start_status_monitor(self) -> None:
        """Start monitoring status updates in a separate thread"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._status_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def _status_monitor(self) -> None:
        """Monitor status updates from TinyG"""
        while self.running:
            if self.serial and self.serial.in_waiting:
                try:
                    line = self.serial.readline().decode().strip()
                    if line:
                        try:
                            status = json.loads(line)
                            self.status_queue.put(status)
                        except json.JSONDecodeError:
                            self.logger.debug(f"Non-JSON response: {line}")
                except:
                    continue

    def stop_status_monitor(self) -> None:
        """Stop the status monitoring thread"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
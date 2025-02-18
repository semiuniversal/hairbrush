# tinyg_tester/controller.py

from dataclasses import dataclass
import json
import logging
from queue import Queue
import threading
import time
from typing import Dict, Any, Optional, Tuple, List

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
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TinyG')

    def read_response(self, timeout: float = 1.0) -> Optional[str]:
        try:
            start_time = time.time()
            response = ""
            brace_count = 0
            in_json = False
            
            while time.time() - start_time < timeout:
                if self.serial.in_waiting:
                    char = self.serial.read().decode()
                    response += char
                    
                    if char == '{':
                        in_json = True
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    
                    if in_json and brace_count == 0 and char == '}':
                        return response.strip()
                    elif not in_json and char == '\n':
                        clean_response = response.strip()
                        if clean_response:
                            return clean_response
                else:
                    time.sleep(0.01)
                    
            if response:
                self.logger.debug(f"Incomplete response: {response}")
            return None
                
        except Exception as e:
            self.logger.error(f"Error reading response: {e}")
            return None

    def read_all_responses(self, timeout: float = 2.0) -> List[str]:
        responses = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = self.read_response(timeout=0.1)
            if response:
                responses.append(response)
                if not self.serial.in_waiting:
                    time.sleep(0.1)
                    if not self.serial.in_waiting:
                        break
            else:
                break
                
        return responses

    def parse_json_response(self, response: str) -> Tuple[bool, Any]:
        try:
            response = response.strip()
            if response.count('{') > response.count('}'):
                response = response + '}'
            
            data = json.loads(response)
            return True, data
        except json.JSONDecodeError as e:
            self.logger.debug(f"JSON parse error: {e} in response: {response}")
            return False, None

    def initialize_port(self) -> bool:
        try:
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            self.logger.info("Clearing communication buffers...")
            self.serial.write(b'\r\n\r\n')
            time.sleep(0.5)
            
            while self.serial.in_waiting:
                self.serial.readline()
                time.sleep(0.1)
            
            self.logger.info("Enabling JSON mode...")
            self.serial.write(b'{"ej":1}\n')
            time.sleep(0.5)
            
            response = self.read_response(timeout=2.0)
            success, data = self.parse_json_response(response) if response else (False, None)
            if not success or not data or 'r' not in data or 'ej' not in data['r']:
                self.logger.error("Failed to enable JSON mode")
                return False
            
            self.logger.info("Configuring verbosity...")
            self.send_command('{"jv":4}')
            time.sleep(0.5)
            self.send_command('{"sv":1}')
            time.sleep(0.5)
            
            return True
        except serial.SerialException as e:
            self.logger.error(f"Port initialization failed: {e}")
            return False

    def connect(self) -> bool:
        try:
            self.serial = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baud_rate,
                timeout=1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.logger.info(f"Connected to {self.config.port}")
            
            time.sleep(2)
            self.logger.info("Waiting for TinyG initialization...")
            
            if not self.initialize_port():
                return False
            
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self) -> None:
        if self.serial and self.serial.is_open:
            self.send_command('{"me":0}')
            time.sleep(0.1)
            self.serial.close()
            self.logger.info("Disconnected from TinyG")

    def get_current_config(self) -> dict:
        current_config = {}
        self.serial.reset_input_buffer()
        
        for key in self.config.config.keys():
            command = f"{{{key}:n}}\n"
            self.logger.debug(f"Querying config: {command.strip()}")
            self.serial.write(command.encode())
            
            response = self.read_response()
            if response:
                success, data = self.parse_json_response(response)
                if success and 'r' in data:
                    if isinstance(data['r'], dict):
                        if key in data['r']:
                            current_config[key] = data['r'][key]
                    else:
                        current_config[key] = data['r']
                else:
                    self.logger.warning(f"Could not parse configuration response for {key}")
                    self.logger.debug(f"Raw response: {response}")
            
            time.sleep(0.1)
        
        return current_config

    def send_command(self, command: str) -> Optional[str]:
        if not self.serial or not self.serial.is_open:
            self.logger.error("Not connected to TinyG")
            return None
        
        try:
            self.logger.debug(f"Sending command: {command}")
            self.serial.write(f"{command}\n".encode())
            
            if command.startswith('M'):
                responses = self.read_all_responses(timeout=2.0)
                return '; '.join(responses) if responses else None
            else:
                response = self.read_response()
                if response:
                    self.logger.debug(f"Received response: {response}")
                    return response
                    
            self.logger.warning(f"No response received for command: {command}")
            return None
        except serial.SerialException as e:
            self.logger.error(f"Error sending command: {e}")
            return None

    def apply_config(self) -> None:
        self.logger.info("Starting configuration process...")
        
        self.send_command('{"ej":1}')
        time.sleep(0.1)
        
        current_config = self.get_current_config()
        self.logger.debug(f"Current config: {current_config}")
        
        changes_made = 0
        for key, new_value in self.config.config.items():
            self.logger.debug(f"Checking config {key}")
            current_value = current_config.get(key)
            
            if key == 'sys' and isinstance(new_value, dict):
                for sys_key, sys_value in new_value.items():
                    command = f"{{\"sys\":{{\"{sys_key}\":{sys_value}}}}}\n"
                    self.logger.debug(f"Sending sys config command: {command.strip()}")
                    self.serial.write(command.encode())
                    response = self.read_response()
                    if response:
                        self.logger.info(f"Updated sys.{sys_key}")
                        changes_made += 1
                    time.sleep(0.1)
                continue
            
            if current_value != new_value:
                command = f"{{{key}:{new_value}}}\n"
                self.logger.debug(f"Sending config command: {command.strip()}")
                self.serial.write(command.encode())
                response = self.read_response()
                if response:
                    success, _ = self.parse_json_response(response)
                    if success:
                        self.logger.info(f"Updated {key}: {current_value} → {new_value}")
                        changes_made += 1
                    else:
                        self.logger.warning(f"Failed to update {key}")
            else:
                self.logger.debug(f"Skipped {key}: already set to {current_value}")
            
            time.sleep(0.1)
        
        if changes_made > 0:
            self.logger.info("Writing configuration to flash...")
            self.send_command('{"sv":1}')
            time.sleep(1.0)
        
        self.logger.info(f"Configuration complete. Made {changes_made} changes.")

    def safe_servo_init(self) -> None:
        self.send_command("M5")
        time.sleep(0.1)
        self.logger.info("Servos disabled for safe initialization")
        
        self.send_command("M3 S0")
        time.sleep(0.1)
        self.send_command("M4 S0")
        time.sleep(0.1)
        self.logger.info("Servos initialized to minimum position")
        
        self.send_command('{"1pm":2}')
        time.sleep(0.1)
        self.send_command('{"2pm":2}')
        time.sleep(0.1)
        self.send_command('{"3pm":2}')
        time.sleep(0.1)
        self.logger.info("Motors set to powered-in-cycle mode")

    def start_status_monitor(self) -> None:
        self.running = True
        self.monitor_thread = threading.Thread(target=self._status_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def _status_monitor(self) -> None:
        while self.running:
            if self.serial and self.serial.in_waiting:
                response = self.read_response(timeout=0.1)
                if response:
                    success, data = self.parse_json_response(response)
                    if success:
                        self.status_queue.put(data)
                    else:
                        self.logger.debug(f"Non-JSON response in monitor: {response}")

    def stop_status_monitor(self) -> None:
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
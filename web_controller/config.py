#!/usr/bin/env python3
"""
Configuration Module

Handles configuration loading and management for the H.Airbrush Web Controller.
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the H.Airbrush Web Controller."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config: Dict[str, Any] = {}
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 'config.yaml')
        
        # Load configuration
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.json'):
                        self.config = json.load(f)
                    else:
                        self.config = yaml.safe_load(f)
                
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file not found at {self.config_path}")
                self._create_default_config()
        
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                if self.config_path.endswith('.json'):
                    json.dump(self.config, f, indent=2)
                else:
                    yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Saved configuration to {self.config_path}")
        
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        if '.' in key:
            parts = key.split('.')
            value = self.config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            value: Value to set
        """
        if '.' in key:
            parts = key.split('.')
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            
            config[parts[-1]] = value
        else:
            self.config[key] = value
    
    def _create_default_config(self) -> None:
        """Create default configuration."""
        self.config = {
            'duet': {
                'host': '192.168.1.1',
                'telnet_port': 23,
                'http_port': 80,
                'connect_timeout': 5
            },
            'connection': {
                'history': []
            },
            'web': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'secret_key': os.urandom(24).hex()
            },
            'machine': {
                'max_x': 841,  # A0 width in mm
                'max_y': 1189, # A0 height in mm
                'max_z': 50,
                'home_x': 0,
                'home_y': 0,
                'home_z': 10,
                'park_x': 0,
                'park_y': 0,
                'park_z': 10,
                'cleaning_x': 750,
                'cleaning_y': 1100,
                'cleaning_z': 5,
                'paper': {
                    'width': 841,  # A0 width in mm
                    'height': 1189, # A0 height in mm
                    'orientation': 'portrait'
                }
            },
            'brushes': {
                'a': {
                    'name': 'Black',
                    'offset_x': 0,
                    'offset_y': 0,
                    'air_on': 'M42 P0 S1',
                    'air_off': 'M42 P0 S0',
                    'paint_on': 'M280 P0 S90',
                    'paint_off': 'M280 P0 S0'
                },
                'b': {
                    'name': 'White',
                    'offset_x': 50,
                    'offset_y': 50,
                    'air_on': 'M42 P1 S1',
                    'air_off': 'M42 P1 S0',
                    'paint_on': 'M280 P1 S90',
                    'paint_off': 'M280 P1 S0'
                }
            }
        }
        
        # Save default configuration
        self.save()
        logger.info("Created default configuration")

# Create global configuration instance
config = Config() 
#!/usr/bin/env python3
"""
Logger Utility Module

Provides logging configuration for the H.Airbrush Web Controller.
"""

import os
import logging
import logging.handlers
from datetime import datetime

def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name (None for root logger)
        level: Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create file handler
    log_file = os.path.join(logs_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5)  # 10MB max, 5 backups
    file_handler.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name (None for root logger)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

# Set up root logger
setup_logger() 
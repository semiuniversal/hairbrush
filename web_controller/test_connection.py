#!/usr/bin/env python3
"""
Test script to directly test the connection to the Duet board.
"""

import sys
import logging
import requests
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection(host, password=""):
    """Test connection to Duet board using HTTP API."""
    logger.info(f"Testing connection to Duet at {host}")
    
    # Create session for cookies
    session = requests.Session()
    
    try:
        # Step 1: Connect and get session cookie
        connect_url = f"http://{host}/rr_connect?password={password}"
        logger.info(f"Connecting to: {connect_url}")
        
        connect_response = session.get(connect_url, timeout=5)
        logger.info(f"Connect response status: {connect_response.status_code}")
        logger.info(f"Connect response: {connect_response.text}")
        logger.info(f"Connect cookies: {session.cookies.get_dict()}")
        
        connect_response.raise_for_status()
        
        # Step 2: Get status
        status_url = f"http://{host}/rr_status?type=1"
        logger.info(f"Getting status from: {status_url}")
        
        status_response = session.get(status_url, timeout=5)
        logger.info(f"Status response status: {status_response.status_code}")
        logger.info(f"Status response (truncated): {status_response.text[:100]}...")
        
        status_response.raise_for_status()
        
        # Step 3: Send a simple G-code command
        command = "M115" # Get firmware info
        encoded_command = urllib.parse.quote(command)
        command_url = f"http://{host}/rr_gcode?gcode={encoded_command}"
        
        logger.info(f"Sending command: {command}")
        logger.info(f"Command URL: {command_url}")
        
        command_response = session.get(command_url, timeout=5)
        logger.info(f"Command response status: {command_response.status_code}")
        logger.info(f"Command response: {command_response.text}")
        
        command_response.raise_for_status()
        
        # Step 4: Get reply
        reply_url = f"http://{host}/rr_reply"
        logger.info(f"Getting reply from: {reply_url}")
        
        reply_response = session.get(reply_url, timeout=5)
        logger.info(f"Reply response status: {reply_response.status_code}")
        logger.info(f"Reply response: {reply_response.text}")
        
        reply_response.raise_for_status()
        
        # Step 5: Disconnect
        disconnect_url = f"http://{host}/rr_disconnect"
        logger.info(f"Disconnecting from: {disconnect_url}")
        
        disconnect_response = session.get(disconnect_url, timeout=5)
        logger.info(f"Disconnect response status: {disconnect_response.status_code}")
        logger.info(f"Disconnect response: {disconnect_response.text}")
        
        logger.info("Connection test completed successfully!")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Connection test failed: {e}")
        logger.exception("Error details:")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <host> [password]")
        sys.exit(1)
    
    host = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else ""
    
    success = test_connection(host, password)
    sys.exit(0 if success else 1) 
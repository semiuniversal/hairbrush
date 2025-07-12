#!/usr/bin/env python3
"""
H.Airbrush Web Controller

A Flask-based web server for controlling the H.Airbrush machine in real-time,
sending G-code commands via HTTP API to the Duet 2 WiFi board running RepRap firmware.
"""

import os
import logging
import datetime
import yaml
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import time
from flask_autoindex import AutoIndex

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'hairbrush_controller.log')

# Set root logger to DEBUG level
logging.getLogger().setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # This will output to console
    ]
)

# Ensure our specific loggers are set to DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set serial_service logger to DEBUG explicitly
serial_logger = logging.getLogger('serial_service')
serial_logger.setLevel(logging.DEBUG)

logger.debug("Logging initialized at DEBUG level")

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Disable template caching
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file caching
# AutoIndex(app, browse_root=os.path.curdir)
# Add datetime.now to Jinja environment
app.jinja_env.globals['now'] = datetime.datetime.now

# Create SocketIO instance
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import controllers after app is created to avoid circular imports
from utils import logger as log_util
from duet_client import DuetClient
from job_manager import JobManager
from machine_control import MachineControl
from serial_service import SerialService
from config import config

# Initialize components
duet_client = None
job_manager = None
machine_control = None
serial_service = None

def initialize_components():
    global duet_client, job_manager, machine_control, serial_service
    
    # Load configuration
    duet_host = config.get('duet.host', '192.168.1.1')
    duet_port = int(config.get('duet.http_port', 80))
    connect_timeout = int(config.get('duet.connect_timeout', 5))
    duet_password = config.get('duet.password', '')
    
    # Initialize components
    duet_client = DuetClient(
        host=duet_host,
        http_port=duet_port,
        connect_timeout=connect_timeout,
        password=duet_password,
        auto_connect=False
    )
    job_manager = JobManager(app.config['UPLOAD_FOLDER'], duet_client)
    machine_control = MachineControl(duet_client)
    serial_service = SerialService()
    
    # Set up job status update callback
    if job_manager:
        job_manager.set_status_callback(emit_job_status_update)
    
    logger.info(f"Initialized components with H.Airbrush Plotter host: {duet_host}:{duet_port}")

# Function to emit job status updates via WebSocket
def emit_job_status_update(job_data):
    """
    Emit job status update via WebSocket.
    
    Args:
        job_data: Job data to emit
    """
    try:
        socketio.emit('job_status', job_data)
        logger.debug(f"Emitted job status update: {job_data.get('status')} - {job_data.get('progress')}%")
    except Exception as e:
        logger.error(f"Error emitting job status update: {e}")

# Function to emit serial data via WebSocket
def emit_serial_data(data):
    """
    Emit serial data via WebSocket.
    
    Args:
        data: Serial data to emit
    """
    try:
        socketio.emit('serial_data', {'data': data})
        logger.debug(f"Emitted serial data: {data.strip()}")
    except Exception as e:
        logger.error(f"Error emitting serial data: {e}")

# Routes
@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/control')
def control():
    """Render the machine control page."""
    return render_template('control.html')

@app.route('/files')
def files():
    """Render the file management page."""
    return render_template('files.html')

@app.route('/files/preview')
def file_preview():
    """Render the file preview page."""
    return render_template('file_preview.html')

@app.route('/test')
def test_page():
    """Render the test page."""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'test.html')

@app.route('/test_command_history')
def test_command_history():
    """Render the command history test page."""
    return render_template('test_command_history.html')

@app.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html')

@app.route('/maintenance')
def maintenance():
    """Render the maintenance page."""
    return render_template('maintenance.html')

@app.route('/setup')
def setup():
    """Render the initial setup page."""
    return render_template('setup.html')

@app.route('/api/status')
def get_status():
    """Get the current machine status."""
    if duet_client:
        try:
            # Get position from Duet
            position_result = duet_client.get_position()
            
            # Get machine state
            state = duet_client.get_status().get('state', 'unknown')
            
            # Get homed state
            is_homed = duet_client.is_homed()
            
            # Get motors state
            motors_state = 'enabled' if duet_client.are_motors_enabled() else 'disabled'
            
            # Create status object
            status = {
                "position": position_result.get('position', {}),
                "state": state,
                "is_homed": is_homed,
                "motors_state": motors_state
            }
            
            # Try to get brush state if the method exists
            if machine_control and hasattr(machine_control, 'get_brush_state'):
                brush_state = machine_control.get_brush_state()
                status["brush_state"] = brush_state
            else:
                # Provide default brush state
                status["brush_state"] = {
                    "a": {"air": False, "paint": False},
                    "b": {"air": False, "paint": False}
                }
            
            return jsonify(status)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Duet client not initialized"}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """List available G-code files."""
    if job_manager:
        files = job_manager.list_files()
        return jsonify(files)
    return jsonify({"error": "Job manager not initialized"}), 500

@app.route('/api/files/<job_id>', methods=['GET'])
def get_file(job_id):
    """Get information about a specific file."""
    if job_manager:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({"error": f"Job {job_id} not found"}), 404
        return jsonify(job.to_dict())
    return jsonify({"error": "Job manager not initialized"}), 500

@app.route('/api/files', methods=['POST'])
def upload_file():
    """Upload a G-code file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if job_manager:
        result = job_manager.upload_file(file)
        return jsonify(result)
    
    return jsonify({"error": "Job manager not initialized"}), 500

@app.route('/api/files/<job_id>/preview', methods=['GET'])
def preview_file(job_id):
    """Preview a G-code file."""
    if job_manager:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({"error": f"Job {job_id} not found"}), 404
        
        try:
            with open(job.file_path, 'r') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading file for preview: {e}")
            return jsonify({"error": f"Error reading file: {str(e)}"}), 500
    
    return jsonify({"error": "Job manager not initialized"}), 500

@app.route('/api/files/<job_id>', methods=['DELETE'])
def delete_file(job_id):
    """Delete a G-code file."""
    if job_manager:
        result = job_manager.delete_job(job_id)
        return jsonify(result)
    return jsonify({"error": "Job manager not initialized"}), 500

@app.route('/api/machine/config', methods=['GET'])
def get_machine_config():
    """Get the machine configuration."""
    machine_config = {
        'machine': config.get('machine', {}),
        'brushes': config.get('brushes', {})
    }
    return jsonify(machine_config)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all settings."""
    try:
        # Return the entire configuration
        return jsonify(config.config)
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings."""
    try:
        settings = request.json
        if not settings:
            return jsonify({"error": "No settings provided"}), 400
        
        # Validate settings before applying them
        for section, values in settings.items():
            if section not in config.config and section not in ['command_timeout', 'status_interval']:
                logger.warning(f"Unknown settings section: {section}")
        
        # Create a backup of the current configuration
        import copy
        config_backup = copy.deepcopy(config.config)
        
        # Update settings
        for section, values in settings.items():
            if isinstance(values, dict):
                # Handle nested sections (e.g., duet, machine, brushes)
                for key, value in values.items():
                    if isinstance(value, dict):
                        # Handle doubly nested sections (e.g., brushes.a)
                        for subkey, subvalue in value.items():
                            config.set(f"{section}.{key}.{subkey}", subvalue)
                    else:
                        config.set(f"{section}.{key}", value)
            else:
                # Handle top-level settings
                config.set(section, values)
        
        # Save configuration to file
        try:
            config.save()
        except Exception as save_error:
            logger.error(f"Failed to save configuration: {save_error}")
            # Restore the backup
            config.config = config_backup
            return jsonify({"error": f"Failed to save configuration: {str(save_error)}"}), 500
        
        # Return updated configuration
        return jsonify({"success": True, "config": config.config})
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/connection/test', methods=['POST'])
def test_connection():
    """Test connection to the Duet board."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No connection data provided"}), 400
        
        host = data.get('host')
        port = data.get('port')
        
        if not host:
            return jsonify({"error": "Host is required"}), 400
        
        if not port:
            port = 80  # Default HTTP port
        
        # Create a temporary client to test connection
        from duet_client import DuetClient
        test_client = DuetClient(
            host=host,
            http_port=port,
            connect_timeout=5,
            auto_connect=False
        )
        
        # Test connection
        success, message = test_client.test_connection()
        
        # Return result
        return jsonify({
            "success": success,
            "message": message,
            "host": host,
            "port": port
        })
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({
            "success": False,
            "message": str(e),
            "host": data.get('host') if data else None,
            "port": data.get('port') if data else None
        })

@app.route('/api/connection', methods=['GET'])
def get_connection_status():
    """Get the current connection status."""
    if duet_client:
        connected = duet_client.is_connected()
        return jsonify({
            "connected": connected,
            "host": duet_client.host,
            "port": duet_client.http_port
        })
    return jsonify({"connected": False})

@app.route('/api/connection/history', methods=['GET'])
def get_connection_history():
    """Get connection history."""
    history = config.get('connection.history', [])
    return jsonify(history)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

@app.route('/api/machine/brush/<brush_id>/air', methods=['POST'])
def set_brush_air(brush_id):
    """Set brush air on/off."""
    if machine_control:
        try:
            data = request.json
            state = data.get('state', False)
            result = machine_control.set_brush_air(brush_id, state)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error setting brush {brush_id} air: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Machine control not initialized"}), 500

@app.route('/api/machine/brush/<brush_id>/paint', methods=['POST'])
def set_brush_paint(brush_id):
    """Set brush paint on/off."""
    if machine_control:
        try:
            data = request.json
            state = data.get('state', False)
            result = machine_control.set_brush_paint(brush_id, state)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error setting brush {brush_id} paint: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Machine control not initialized"}), 500

@app.route('/api/machine/brush/<brush_id>/flow', methods=['POST'])
def set_brush_paint_flow(brush_id):
    """Set brush paint flow percentage."""
    if machine_control:
        try:
            data = request.json
            percentage = float(data.get('percentage', 50))
            result = machine_control.set_brush_paint_flow(brush_id, percentage)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error setting brush {brush_id} paint flow: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Machine control not initialized"}), 500

@app.route('/api/machine/home', methods=['POST'])

# Serial communication API endpoints
@app.route('/api/serial/ports', methods=['GET'])
def list_serial_ports():
    """List available serial ports."""
    if not serial_service:
        return jsonify({"error": "Serial service not initialized"}), 500
    
    ports = serial_service.list_ports()
    return jsonify(ports)

@app.route('/api/serial/connect', methods=['POST'])
def connect_serial():
    """Connect to a serial port."""
    if not serial_service:
        return jsonify({"error": "Serial service not initialized"}), 500
    
    data = request.json
    port = data.get('port')
    baud_rate = data.get('baud_rate', 115200)
    
    if not port:
        return jsonify({"error": "Port is required"}), 400
    
    result = serial_service.connect(port, baud_rate, emit_serial_data)
    
    if result["status"] == "success":
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/serial/disconnect', methods=['POST'])
def disconnect_serial():
    """Disconnect from the serial port."""
    if not serial_service:
        return jsonify({"error": "Serial service not initialized"}), 500
    
    result = serial_service.disconnect()
    
    if result["status"] == "success":
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/serial/command', methods=['POST'])
def send_serial_command():
    """Send a command to the serial port."""
    if not serial_service:
        return jsonify({"error": "Serial service not initialized"}), 500
    
    if not serial_service.is_connected:
        return jsonify({"error": "Not connected to a serial port"}), 400
    
    data = request.json
    command = data.get('command')
    
    if not command:
        return jsonify({"error": "Command is required"}), 400
    
    result = serial_service.send_command(command)
    
    if result["status"] == "success":
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/serial/ip', methods=['GET'])
def get_ip_address():
    """Get IP address from the Duet board."""
    if not serial_service:
        return jsonify({"error": "Serial service not initialized"}), 500
    
    if not serial_service.is_connected:
        return jsonify({"error": "Not connected to a serial port"}), 400
    
    result = serial_service.get_ip_address()
    
    if result["status"] == "success":
        # Add IP to connection history if found
        if "ip_address" in result:
            add_ip_to_history(result["ip_address"])
        
        return jsonify(result)
    else:
        return jsonify(result), 500

def add_ip_to_history(ip_address):
    """
    Add IP address to connection history.
    
    Args:
        ip_address: IP address to add
    """
    try:
        # Get current connection history
        connection_history = config.get('connection.history', [])
        
        # Add IP to history if not already present
        if ip_address not in connection_history:
            connection_history.insert(0, ip_address)
            
            # Keep only the 5 most recent IPs
            if len(connection_history) > 5:
                connection_history = connection_history[:5]
            
            # Update config
            config.set('connection.history', connection_history)
            config.save()
            
            logger.info(f"Added IP {ip_address} to connection history")
    except Exception as e:
        logger.error(f"Error adding IP to history: {e}")

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    
    try:
        # Initialize components if not already initialized
        if duet_client is None:
            initialize_components()
        
        # Send initial status
        if duet_client:
            connected = duet_client.is_connected()
            socketio.emit('connection_status', {"connected": connected}, room=request.sid)
    except Exception as e:
        logger.error(f"Error in handle_connect: {e}")
        socketio.emit('connection_status', {"connected": False, "error": str(e)}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('error')
def handle_error(error):
    """Handle socket.io errors."""
    logger.error(f"SocketIO error for {request.sid}: {error}")

@socketio.on_error()
def error_handler(e):
    """Global error handler for all namespaces."""
    logger.error(f"SocketIO global error: {e}")
    return {"status": "error", "message": str(e)}

@socketio.on_error_default
def default_error_handler(e):
    """Default error handler."""
    logger.error(f"SocketIO default error: {e}")
    return {"status": "error", "message": str(e)}

@socketio.on('connect_device')
def handle_connect_device(data):
    """Handle connect device request."""
    global duet_client, job_manager, machine_control
    
    host = data.get('host', '192.168.1.1')
    port = data.get('port', 80)
    password = data.get('password', '')
    
    logger.info(f"Connecting to device: {host}:{port}")
    
    try:
        # Disconnect existing client if connected
        if duet_client and duet_client.is_connected():
            duet_client.disconnect()
        
        # Create new client
        duet_client = DuetClient(
            host=host,
            http_port=port,
            connect_timeout=5,
            password=password,
            auto_connect=False
        )
        
        # Connect to device
        connected = duet_client.connect()
        
        if connected:
            # Update configuration
            config.set('duet.host', host)
            config.set('duet.http_port', port)
            config.set('duet.password', password)
            config.save()
            
            # Update connection history
            history = config.get('connection.history', [])
            if host not in history:
                history.insert(0, host)
                # Limit history to 10 items
                if len(history) > 10:
                    history = history[:10]
                config.set('connection.history', history)
                config.save()
            
            # Reinitialize components
            job_manager = JobManager(app.config['UPLOAD_FOLDER'], duet_client)
            machine_control = MachineControl(duet_client)
            
            # Send success response
            socketio.emit('connection_status', {
                "connected": True,
                "host": host,
                "port": port
            }, room=request.sid)
            
            return {"status": "success", "connected": True}
        else:
            # Send failure response
            socketio.emit('connection_status', {
                "connected": False,
                "error": "Failed to connect to device"
            }, room=request.sid)
            
            return {"status": "error", "message": "Failed to connect to device"}
    
    except Exception as e:
        logger.error(f"Error connecting to device: {e}")
        
        # Send error response
        socketio.emit('connection_status', {
            "connected": False,
            "error": str(e)
        }, room=request.sid)
        
        return {"status": "error", "message": str(e)}

@socketio.on('disconnect_device')
def handle_disconnect_device(data):
    """Handle disconnect device request."""
    global duet_client
    
    logger.info("Disconnecting from device")
    
    try:
        # Disconnect client
        if duet_client:
            duet_client.disconnect()
            duet_client = None
        
        # Send success response
        socketio.emit('connection_status', {
            "connected": False
        }, room=request.sid)
        
        return {"status": "success", "connected": False}
    
    except Exception as e:
        logger.error(f"Error disconnecting from device: {e}")
        
        # Send error response
        socketio.emit('connection_status', {
            "connected": False,
            "error": str(e)
        }, room=request.sid)
        
        return {"status": "error", "message": str(e)}

@socketio.on('command')
def handle_command(data):
    """Handle G-code command."""
    if not duet_client:
        return {"status": "error", "message": "Not connected to device"}
    
    command = data.get('command')
    if not command:
        return {"status": "error", "message": "No command provided"}
    
    try:
        result = duet_client.send_gcode(command)
        return {"status": "success", "result": result}
    
    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return {"status": "error", "message": str(e)}

@socketio.on('jog')
def handle_jog(data):
    """Handle jog command."""
    if not duet_client:
        return {"status": "error", "message": "Not connected to device"}
    
    axis = data.get('axis')
    distance = data.get('distance')
    speed = data.get('speed')
    
    if not axis or distance is None:
        return {"status": "error", "message": "Axis and distance are required"}
    
    try:
        result = machine_control.jog(axis, distance, speed)
        return {"status": "success", "result": result}
    
    except Exception as e:
        logger.error(f"Error jogging: {e}")
        return {"status": "error", "message": str(e)}

@socketio.on('job_control')
def handle_job_control(data):
    """Handle job control commands."""
    if not job_manager:
        return {"status": "error", "message": "Job manager not initialized"}
    
    action = data.get('action')
    job_id = data.get('job_id')
    
    if not action:
        return {"status": "error", "message": "No action provided"}
    
    try:
        if action == 'start':
            if not job_id:
                return {"status": "error", "message": "Job ID is required"}
            
            result = job_manager.start_job(job_id)
            return {"status": "success", "result": result}
        
        elif action == 'pause':
            result = job_manager.pause_job()
            return {"status": "success", "result": result}
        
        elif action == 'resume':
            result = job_manager.resume_job()
            return {"status": "success", "result": result}
        
        elif action == 'stop':
            result = job_manager.stop_job()
            return {"status": "success", "result": result}
        
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    except Exception as e:
        logger.error(f"Error controlling job: {e}")
        return {"status": "error", "message": str(e)}

@socketio.on('get_status')
def handle_get_status(data):
    """Handle get status request."""
    if not duet_client:
        return {"status": "error", "message": "Not connected to device"}
    
    try:
        # Get position from Duet
        position_result = duet_client.get_position()
        
        # Get machine state
        state = duet_client.get_status().get('state', 'unknown')
        
        # Get homed state
        try:
            is_homed = duet_client.is_homed()
        except Exception as e:
            logger.error(f"Error getting homed state: {e}")
            is_homed = False
        
        # Get motors state
        try:
            motors_state = 'enabled' if duet_client.are_motors_enabled() else 'disabled'
        except Exception as e:
            logger.error(f"Error getting motors state: {e}")
            motors_state = 'unknown'
        
        # Create status object
        status = {
            "position": position_result.get('position', {}),
            "state": state,
            "is_homed": is_homed,
            "motors_state": motors_state
        }
        
        # Try to get brush state if the method exists
        if machine_control and hasattr(machine_control, 'get_brush_state'):
            brush_state = machine_control.get_brush_state()
            status["brush_state"] = brush_state
        else:
            # Provide default brush state
            status["brush_state"] = {
                "a": {"air": False, "paint": False},
                "b": {"air": False, "paint": False}
            }
        
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {"status": "error", "message": str(e)}

@socketio.on('brush_paint')
def handle_brush_paint(data):
    """Handle brush paint on/off."""
    if not machine_control:
        socketio.emit('error', {'message': 'Machine control not initialized'})
        return
    
    try:
        brush_id = data.get('brush', 'a')
        state = data.get('state', False)
        result = machine_control.set_brush_paint(brush_id, state)
        socketio.emit('brush_paint_result', result)
    except Exception as e:
        logger.error(f"Error handling brush paint: {e}")
        socketio.emit('error', {'message': str(e)})

@socketio.on('brush_paint_flow')
def handle_brush_paint_flow(data):
    """Handle brush paint flow percentage."""
    if not machine_control:
        socketio.emit('error', {'message': 'Machine control not initialized'})
        return
    
    try:
        brush_id = data.get('brush', 'a')
        percentage = float(data.get('percentage', 50))
        result = machine_control.set_brush_paint_flow(brush_id, percentage)
        socketio.emit('brush_paint_flow_result', result)
    except Exception as e:
        logger.error(f"Error handling brush paint flow: {e}")
        socketio.emit('error', {'message': str(e)})

@socketio.on('serial_connect')
def handle_serial_connect(data):
    """Handle serial connect request."""
    if not serial_service:
        socketio.emit('serial_status', {
            "connected": False,
            "error": "Serial service not initialized"
        }, room=request.sid)
        return
    
    port = data.get('port')
    baud_rate = data.get('baud_rate', 115200)
    
    if not port:
        socketio.emit('serial_status', {
            "connected": False,
            "error": "Port is required"
        }, room=request.sid)
        return
    
    result = serial_service.connect(port, baud_rate, emit_serial_data)
    
    socketio.emit('serial_status', {
        "connected": result["status"] == "success",
        "port": port if result["status"] == "success" else None,
        "message": result["message"],
        "error": result["message"] if result["status"] != "success" else None
    }, room=request.sid)

@socketio.on('serial_disconnect')
def handle_serial_disconnect():
    """Handle serial disconnect request."""
    if not serial_service:
        socketio.emit('serial_status', {
            "connected": False,
            "error": "Serial service not initialized"
        }, room=request.sid)
        return
    
    result = serial_service.disconnect()
    
    socketio.emit('serial_status', {
        "connected": False,
        "message": result["message"],
        "error": result["message"] if result["status"] != "success" else None
    }, room=request.sid)

@socketio.on('serial_command')
def handle_serial_command(data):
    """Handle serial command request."""
    if not serial_service:
        socketio.emit('error', {
            "message": "Serial service not initialized"
        }, room=request.sid)
        return
    
    command = data.get('command')
    
    if not command:
        socketio.emit('error', {
            "message": "Command is required"
        }, room=request.sid)
        return
    
    result = serial_service.send_command(command)
    
    if result["status"] != "success":
        socketio.emit('error', {
            "message": result["message"]
        }, room=request.sid)

@socketio.on('get_ip_address')
def handle_get_ip_address():
    """Handle get IP address request."""
    if not serial_service:
        socketio.emit('ip_address_result', {
            "status": "error",
            "message": "Serial service not initialized"
        }, room=request.sid)
        return
    
    if not serial_service.is_connected:
        socketio.emit('ip_address_result', {
            "status": "error",
            "message": "Not connected to a serial port"
        }, room=request.sid)
        return
    
    # Get the IP address
    result = serial_service.get_ip_address()
    
    # Add IP to connection history if found
    if result["status"] == "success" and "ip_address" in result:
        add_ip_to_history(result["ip_address"])
    
    socketio.emit('ip_address_result', result, room=request.sid)

@app.route('/api/settings/get', methods=['GET'])
def get_setting():
    """Get a specific setting by key."""
    key = request.args.get('key')
    if not key:
        return jsonify({"error": "Key is required"}), 400
    
    try:
        value = config.get(key, None)
        return jsonify({"key": key, "value": value})
    except Exception as e:
        logger.error(f"Error getting setting {key}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings/set', methods=['POST'])
def set_setting():
    """Set a specific setting."""
    data = request.json
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({"error": "Key and value are required"}), 400
    
    key = data['key']
    value = data['value']
    
    try:
        config.set(key, value)
        config.save()
        return jsonify({"success": True, "key": key, "value": value})
    except Exception as e:
        logger.error(f"Error setting {key}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/connect', methods=['POST'])
def connect_to_duet():
    """Connect to the Duet board."""
    data = request.json
    if not data:
        return jsonify({"error": "No connection data provided"}), 400
    
    host = data.get('host')
    port = data.get('port', 80)
    
    if not host:
        return jsonify({"error": "Host is required"}), 400
    
    try:
        # Update configuration
        config.set('duet.host', host)
        config.set('duet.http_port', port)
        config.save()
        
        # Initialize Duet client with new settings
        global duet_client
        if duet_client:
            duet_client.disconnect()
        
        duet_client = DuetClient(
            host=host,
            http_port=port,
            connect_timeout=int(config.get('duet.connect_timeout', 5)),
            password=config.get('duet.password', ''),
            auto_connect=True
        )
        
        # Test connection
        if duet_client.is_connected():
            # Add to connection history
            add_ip_to_history(host)
            
            return jsonify({"success": True, "message": f"Connected to {host}"})
        else:
            return jsonify({"success": False, "message": "Failed to connect to Duet board"}), 500
    except Exception as e:
        logger.error(f"Error connecting to Duet: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/commands')
def get_commands():
    """Get available Duet commands."""
    try:
        # Path to the YAML file
        commands_file = os.path.join(os.path.dirname(__file__), 'duet_status_commands.yaml')
        
        # Check if file exists
        if not os.path.exists(commands_file):
            return jsonify({"error": "Commands file not found"}), 404
        
        # Load commands from YAML
        with open(commands_file, 'r') as f:
            commands = yaml.safe_load(f)
        
        return jsonify(commands)
    except Exception as e:
        logger.error(f"Error loading commands: {e}")
        return jsonify({"error": str(e)}), 500

# Run the application if executed directly
if __name__ == '__main__':
    # Initialize components
    initialize_components()
    
    # Get web server configuration
    host = config.get('web.host', '0.0.0.0')
    port = int(config.get('web.port', 5000))
    debug = config.get('web.debug', False)
    
    # Run the server
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True) 
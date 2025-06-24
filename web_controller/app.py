#!/usr/bin/env python3
"""
H.Airbrush Web Controller

A Flask-based web server for controlling the H.Airbrush machine in real-time,
sending G-code commands via Telnet to the Duet 2 WiFi board.
"""

import os
import logging
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'hairbrush_controller.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Disable template caching
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file caching

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
from config import config

# Initialize components
duet_client = None
job_manager = None
machine_control = None

def initialize_components():
    global duet_client, job_manager, machine_control
    
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
    
    logger.info(f"Initialized components with H.Airbrush Plotter host: {duet_host}:{duet_port}")

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

@app.route('/api/status')
def get_status():
    """Get the current machine status."""
    if duet_client:
        status = duet_client.get_status()
        return jsonify(status)
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
        config.save()
        
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

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    
    # Initialize components if not already initialized
    if duet_client is None:
        initialize_components()
    
    # Send initial status
    if duet_client:
        connected = duet_client.is_connected()
        socketio.emit('connection_status', {"connected": connected}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")

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
    """Handle status request."""
    if not duet_client:
        return {"status": "error", "message": "Not connected to device"}
    
    try:
        # Get machine status
        status = duet_client.get_status()
        
        # Get machine position
        position = duet_client.get_position()
        
        # Get brush state
        brush_state = machine_control.get_brush_state() if machine_control else None
        
        # Get motors state
        motors_state = machine_control.get_motors_state() if machine_control else None
        
        return {
            "status": "success",
            "data": {
                "machine_status": status,
                "position": position,
                "brush_state": brush_state,
                "motors_state": motors_state
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {"status": "error", "message": str(e)}

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
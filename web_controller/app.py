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

@app.route('/api/connection', methods=['GET'])
def get_connection_status():
    """Get the current connection status."""
    if duet_client:
        return jsonify({
            "connected": duet_client.connected,
            "ip": duet_client.host if duet_client.connected else None
        })
    return jsonify({"error": "Duet client not initialized"}), 500

@app.route('/api/connection/history', methods=['GET'])
def get_connection_history():
    """Get connection history."""
    history = config.get('connection.history', [])
    return jsonify(history)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info(f"Client connected: {request.sid}")
    
    # Send connection status to client
    if duet_client:
        socketio.emit('connection_status', {
            'connected': duet_client.connected,
            'ip': duet_client.host if duet_client.connected else None
        }, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('connect_device')
def handle_connect_device(data):
    """Handle device connection request."""
    ip = data.get('ip')
    password = data.get('password', '')
    
    logger.info(f"Received connection request for device at {ip}")
    
    if not ip:
        logger.error("Connection request missing IP address")
        return {'status': 'error', 'message': 'No IP address provided'}
    
    if duet_client:
        # Update host and password
        logger.debug(f"Updating duet_client host to {ip} and setting password")
        duet_client.host = ip
        duet_client.password = password
        
        # Try to connect
        logger.info(f"Attempting to connect to device at {ip}")
        if duet_client.connect():
            logger.info(f"Successfully connected to device at {ip}")
            
            # Add to connection history
            history = config.get('connection.history', [])
            if ip in history:
                history.remove(ip)
            history.insert(0, ip)
            if len(history) > 5:
                history = history[:5]
            
            # Update configuration
            logger.debug(f"Updating configuration with new connection details")
            config.set('connection.history', history)
            config.set('duet.host', ip)
            
            # Only save password if provided
            if password:
                config.set('duet.password', password)
                
            config.save()
            
            # Notify all clients about connection
            logger.debug(f"Notifying clients about successful connection")
            socketio.emit('connection_status', {
                'connected': True,
                'ip': ip
            })
            
            return {'status': 'success'}
        else:
            logger.error(f"Failed to connect to device at {ip}")
            return {'status': 'error', 'message': 'Failed to connect to device'}
    
    logger.error("Duet client not initialized")
    return {'status': 'error', 'message': 'Duet client not initialized'}

@socketio.on('disconnect_device')
def handle_disconnect_device(data):
    """Handle device disconnection request."""
    if duet_client:
        duet_client.disconnect()
        
        # Notify all clients about disconnection
        socketio.emit('connection_status', {
            'connected': False,
            'ip': None
        })
        
        return {'status': 'success'}
    
    return {'status': 'error', 'message': 'Duet client not initialized'}

@socketio.on('command')
def handle_command(data):
    """Handle G-code command from client."""
    command = data.get('command')
    if command and duet_client:
        if not duet_client.connected:
            return {'status': 'error', 'message': 'Not connected to device'}
        
        result = duet_client.send_command(command)
        return {'status': 'success', 'result': result}
    
    return {'status': 'error', 'message': 'Invalid command or client not initialized'}

@socketio.on('jog')
def handle_jog(data):
    """Handle jog command from client."""
    if machine_control:
        if not duet_client or not duet_client.connected:
            return {'status': 'error', 'message': 'Not connected to device'}
        
        axis = data.get('axis')
        distance = data.get('distance')
        speed = data.get('speed', 1000)
        result = machine_control.jog(axis, distance, speed)
        return {'status': 'success', 'result': result}
    
    return {'status': 'error', 'message': 'Machine control not initialized'}

@socketio.on('job_control')
def handle_job_control(data):
    """Handle job control command from client."""
    if job_manager:
        if not duet_client or not duet_client.connected:
            return {'status': 'error', 'message': 'Not connected to device'}
        
        action = data.get('action')
        job_id = data.get('job_id')
        
        if action == 'start' and job_id:
            result = job_manager.start_job(job_id)
        elif action == 'pause':
            result = job_manager.pause_job()
        elif action == 'resume':
            result = job_manager.resume_job()
        elif action == 'stop':
            result = job_manager.stop_job()
        else:
            return {'status': 'error', 'message': 'Invalid action'}
        
        return {'status': 'success', 'result': result}
    
    return {'status': 'error', 'message': 'Job manager not initialized'}

@socketio.on('get_status')
def handle_get_status(data):
    """Handle status request from client."""
    if duet_client:
        if not duet_client.connected:
            return {'status': 'error', 'message': 'Not connected to device'}
        
        status = duet_client.get_status()
        return {'status': 'success', 'data': status}
    
    return {'status': 'error', 'message': 'Duet client not initialized'}

if __name__ == '__main__':
    # Use eventlet as async server
    initialize_components()
    socketio.run(
        app, 
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('DEBUG', 'False').lower() == 'true'
    ) 
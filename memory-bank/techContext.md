# Technical Context

## Technology Stack
- **Inkscape Extension**: Python with `inkex` for SVG processing and G-code generation
- **Web Controller**: Flask-based web server with Telnet/HTTP client for Duet communication
- **Hardware Control**: Duet 2 WiFi board running RepRapFirmware

## Development Environment
- **Operating System**: WSL2 (Ubuntu) on Windows
- **Python Environment**: uv for virtual environment management
- **Dependency Management**: pyproject.toml
- **Web Server**: Flask with Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Visualization**: HTML5 Canvas
- **Communication**: HTTP API, WebSocket
- **Configuration**: YAML with PyYAML

## Key Technologies

### Python Libraries
- **Flask**: Web framework for the controller application
- **Flask-SocketIO**: Real-time WebSocket communication
- **PyYAML**: YAML configuration file handling
- **Inkscape Extension API**: For the Inkscape plugin

### JavaScript Libraries
- **Bootstrap 5**: UI framework for responsive design
- **Socket.IO Client**: Real-time communication with server
- **HTML5 Canvas API**: For machine visualization
- **Fetch API**: For HTTP requests to server endpoints

### Communication Protocols
- **HTTP API**: For Duet board communication
- **WebSocket**: For real-time updates between server and browser
- **G-code**: For machine control commands

## Duet 2 WiFi Communication

### HTTP API Endpoints
- `/rr_gcode`: Send G-code commands
- `/rr_reply`: Get command responses
- `/rr_status`: Get machine status
- `/rr_upload`: Upload files

### HTTP API Usage
```python
# Send G-code command
encoded_gcode = urllib.parse.quote(gcode)
url = f"http://{host}:{port}/rr_gcode?gcode={encoded_gcode}"
response = session.get(url)

# Get response
reply_response = session.get(f"http://{host}:{port}/rr_reply")
reply_text = reply_response.text.strip()
```

### WebSocket Communication
```javascript
// Client-side
const socket = io();
socket.on('connect', () => {
    console.log('Connected to server');
});
socket.on('status_update', (data) => {
    updateStatus(data);
});
```

```python
# Server-side
@socketio.on('command')
def handle_command(data):
    command = data.get('command')
    result = duet_client.send_command(command)
    return {'status': 'success', 'result': result}
```

## Configuration Management

### YAML Configuration
```yaml
# config.yaml
duet:
  host: 192.168.1.100
  port: 80
  
brushes:
  a:
    offset_x: 0
    offset_y: 0
  b:
    offset_x: 25
    offset_y: 0
```

### Configuration Access
```python
# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access configuration
host = config['duet']['host']
port = config['duet']['port']
brush_b_offset_x = config['brushes']['b']['offset_x']
```

### Settings API
```python
@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all settings."""
    return jsonify(config.config)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings."""
    settings = request.json
    
    # Update settings
    for section, values in settings.items():
        if isinstance(values, dict):
            # Handle nested sections
            for key, value in values.items():
                config.set(f"{section}.{key}", value)
        else:
            # Handle top-level settings
            config.set(section, values)
    
    # Save configuration to file
    config.save()
    
    return jsonify({"success": True, "config": config.config})
```

## Visualization

### Canvas-based Visualization
```javascript
class MachineVisualization {
    constructor(containerId, config = {}) {
        // Initialize canvas
        this.canvas = document.createElement('canvas');
        this.container = document.getElementById(containerId);
        this.container.appendChild(this.canvas);
        
        // Set up high-DPI support
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.ctx = this.canvas.getContext('2d');
        this.ctx.scale(dpr, dpr);
        
        // Calculate scaling to fit paper in visualization
        this.scale = Math.min(scaleX, scaleY);
        
        // Set origin to center of paper
        this.originX = this.paperLeft + (this.paperWidthPx / 2);
        this.originY = this.paperTop + (this.paperHeightPx / 2);
    }
    
    // Draw grid with scale indicators
    drawGrid() {
        const ctx = this.ctx;
        
        // Draw major grid lines with labels
        ctx.strokeStyle = '#888';
        ctx.fillStyle = '#666';
        ctx.font = '10px Arial';
        
        // Draw X grid lines and labels
        for (let x = -100; x <= 100; x += 20) {
            const xPos = this.originX + (x * this.scale);
            
            // Draw line
            ctx.beginPath();
            ctx.moveTo(xPos, 0);
            ctx.lineTo(xPos, this.canvas.height);
            ctx.stroke();
            
            // Draw label
            ctx.fillText(`${x}`, xPos + 2, this.originY - 2);
        }
        
        // Draw Y grid lines and labels
        for (let y = -100; y <= 100; y += 20) {
            const yPos = this.originY - (y * this.scale);
            
            // Draw line
            ctx.beginPath();
            ctx.moveTo(0, yPos);
            ctx.lineTo(this.canvas.width, yPos);
            ctx.stroke();
            
            // Draw label
            ctx.fillText(`${y}`, this.originX + 2, yPos - 2);
        }
    }
    
    // Draw brush position
    drawBrush() {
        const ctx = this.ctx;
        const x = this.originX + (this.position.X * this.scale);
        const y = this.originY - (this.position.Y * this.scale);
        
        // Draw brush position
        ctx.fillStyle = 'red';
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw brush B position (with offset)
        if (this.config.brushBOffsetX || this.config.brushBOffsetY) {
            const offsetX = this.position.X + this.config.brushBOffsetX;
            const offsetY = this.position.Y + this.config.brushBOffsetY;
            const offsetXPx = this.originX + (offsetX * this.scale);
            const offsetYPx = this.originY - (offsetY * this.scale);
            
            ctx.fillStyle = 'blue';
            ctx.beginPath();
            ctx.arc(offsetXPx, offsetYPx, 5, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}
```

## G-code Command Structure

### Basic G-code Commands
- **G0/G1**: Linear move
- **G28**: Home axes
- **M400**: Wait for moves to complete
- **M114**: Get current position
- **M119**: Get endstop status
- **M17**: Enable motors
- **M18/M84**: Disable motors

### Custom G-code Commands
- **M280 P0 S0**: Brush A up
- **M280 P0 S45**: Brush A down
- **M280 P1 S0**: Brush B up
- **M280 P1 S45**: Brush B down

### Example G-code Sequence
```
G28 ; Home all axes
G0 X0 Y0 Z5 ; Move to start position
M400 ; Wait for move to complete
M280 P0 S45 ; Lower brush A
G1 X10 Y10 F1000 ; Draw line
M400 ; Wait for move to complete
M280 P0 S0 ; Raise brush A
```

## Development Requirements

### Critical Requirements
- All command-line operations MUST be executed in WSL, NOT in Windows
- Use uv for virtual environment management
- Use pyproject.toml for dependency management
- Follow minimalist approach to dependencies

### Best Practices
- Implement proper error handling for hardware communication
- Use WebSocket for real-time updates
- Implement proper synchronization with M400 commands
- Follow RESTful API design for HTTP endpoints
- Use modular architecture with clear separation of concerns

## Hardware Specifications

### Duet 2 WiFi Controller
- **Processor**: 32-bit ARM processor
- **Connectivity**: WiFi, Ethernet
- **Stepper Drivers**: 5 TMC2660 drivers
- **I/O Ports**: Multiple configurable I/O ports for accessories

### H.Airbrush Machine
- **Axes**: X, Y, Z (Cartesian)
- **Working Area**: 300mm x 300mm
- **Z-Axis Range**: 50mm
- **Brushes**: Dual airbrushes (A and B)
- **Control**: Separate air and paint control for each brush

### Performance Characteristics
- **Z-axis**: Moves 20x slower than X/Y axes
- **Brush Offsets**: Brushes A and B have different X/Y offsets
- **Air Control**: Digital outputs (M42 P0/P1)
- **Paint Control**: Servo outputs (M280 P0/P1)

## Browser Support
- Chrome 80+
- Firefox 75+
- Edge 80+
- Safari 13+

## Component Architecture

### Inkscape Extension
```
inkscape_extension/
├── hairbrush.inx                # Extension UI definition
├── hairbrush_control.py         # Main entry point
├── hairbrush.py                 # Core functionality
├── hairbrush_lib/               # Core library modules
│   ├── __init__.py
│   ├── svg_parser.py            # SVG parsing functionality
│   ├── path_processor.py        # Path processing functionality
│   ├── gcode_generator.py       # G-code generation with Z-optimization and M400 sync
│   └── config.py                # Configuration management
└── README.md                    # Documentation and usage guide
```

### Web Controller
```
web_controller/
├── web_server.py                # Flask web server
├── duet_client.py               # Duet communication client with M400 handling
├── machine_control.py           # Machine control with M400-aware G-code processing
├── job_manager.py               # G-code job management
├── templates/                   # Web UI templates
└── static/                      # CSS, JavaScript, images
```

## Hardware Constraints
- **Z-axis Performance**: Z-axis moves approximately 20x slower than X/Y axes
- **Dual Airbrush System**: Two independent airbrushes (black and white)
- **SVG Limitations**: Single stroke has constant width/opacity, aligning with Z-height batching

## G-code Optimization Techniques
- **Path Batching**: Group paths by brush type and Z-height to minimize tool changes
- **Movement Sequencing**: Strictly separate Z and XY movements to maintain flat drawings
- **Minimal Z Movements**: Keep Z constant during drawing operations, change only when necessary
- **Physics-based Parameters**: Calculate optimal Z-height, paint flow, and movement speed based on stroke attributes
- **Motion Synchronization**: Strategic placement of M400 commands for reliable operation

## Communication Protocols
- **Extension → Web Controller**: G-code files with embedded M400 synchronization points
- **Web Controller → Duet**: 
  - Telnet (port 23) for G-code streaming with M400 handling
  - HTTP API (port 80) for status and configuration
  - WebSocket for real-time updates

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Use uv for virtual environment management
- Use pyproject.toml for dependency management
- Follow minimalist approach to dependencies 
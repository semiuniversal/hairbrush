# Technical Context

## Technology Stack
- **Inkscape Extension**: Python with `inkex` for SVG processing and G-code generation
- **Web Controller**: Flask-based web server with Telnet/HTTP client for Duet communication
- **Hardware Control**: Duet 2 WiFi board running RepRapFirmware

## Development Environment
- **Operating System**: WSL2 on Windows 10/11
- **Python Version**: 3.8+
- **Package Management**: uv with pyproject.toml
- **IDE**: Visual Studio Code with WSL extension

## Key Technologies

### Inkscape Extension
- **Language**: Python 3.8+
- **Framework**: Inkscape Extension API
- **Dependencies**: 
  - lxml for SVG parsing
  - numpy for mathematical operations
  - inkex for Inkscape extension framework

### Web Controller
- **Language**: Python 3.8+
- **Framework**: Flask with Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Dependencies**:
  - Flask for web server
  - Flask-SocketIO for WebSocket support
  - requests for HTTP API calls
  - socket for Telnet communication

### Duet 2 WiFi Communication
- **Protocols**:
  - Telnet (port 23) for G-code streaming
  - HTTP (port 80) for status monitoring
  - WebSocket for real-time updates
- **G-code Dialect**: RepRap Firmware compatible

## Duet 2 WiFi Integration Details

### Communication Constraints
- Duet **does not push events** - no asynchronous signals when motion completes
- Telnet communication is **stateless** and **line-buffered**
- Must **poll or wait** explicitly using `M400` or `M114` to monitor status

### Critical G-code Commands
- **M400**: Wait for all buffered moves to complete
  - Essential for synchronizing motion completion
  - Duet responds only after all motion has physically finished
- **M114**: Request current position
  - Used for polling machine position for UI updates
  - Returns coordinates in format `X:200.0 Y:200.0 Z:2.0`

### Recommended Protocol Flow
1. Open Telnet connection to Duet on port 23
2. Send G-code commands
3. Send M400 after motion commands to wait for completion
4. Read responses until "ok" or newline is returned
5. Proceed with next command set only after confirmation

### Synchronization Strategy (IMPLEMENTED)
- **Hybrid Approach**:
  - Insert `M400` after each complete stroke or major motion block in G-code generator
  - Recognize and act on `M400` commands as blocking synchronization points in controller
  - Inject additional `M400` when needed for live-streamed operations

### Implementation Pattern (IMPLEMENTED)
```python
# In duet_client.py
def send_command_and_wait(self, command: str) -> Dict[str, Any]:
    """Send command and wait for completion with M400"""
    result = self.send_command(command)
    if result["status"] == "error":
        return result
    
    # Send M400 to wait for motion completion
    return self.wait_for_motion_complete()

def wait_for_motion_complete(self) -> Dict[str, Any]:
    """Send M400 to wait for all buffered moves to complete"""
    return self.send_command("M400")

def get_position(self) -> Dict[str, Any]:
    """Get current position using M114"""
    result = self.send_command("M114")
    # Parse position response
    # ...

# In machine_control.py
def process_gcode_file(self, filename: str) -> Dict[str, Any]:
    """Process G-code with M400 synchronization awareness"""
    # Read file line by line
    for line in lines:
        command = line.split(';')[0].strip()
        
        if command.upper().startswith("M400"):
            # Wait for all previous commands to complete
            result = self.duet_client.wait_for_motion_complete()
        else:
            # Send command without waiting
            result = self.duet_client.send_command(command)
```

### G-code Generation with Synchronization (IMPLEMENTED)
```python
# In gcode_generator.py (Inkscape Extension)
def add_path(self, path_data, brush, z_height, feedrate, curve_resolution=20, paint_flow=1.0):
    # ...
    
    # STEP 1: Raise Z to travel height (G0 for rapid movement)
    self.output_lines.append("G0 Z{:.2f} F3000".format(travel_z))
    self.output_lines.append("M400 ; Wait for Z movement to complete")
    
    # STEP 2: Move XY to start point with Z raised
    self.output_lines.append("G0 X{:.2f} Y{:.2f} F3000".format(x + offset_x, y + offset_y))
    self.output_lines.append("M400 ; Wait for XY movement to complete")
    
    # STEP 3: Lower Z to drawing height
    self.output_lines.append("G1 Z{:.2f} F1500".format(transformed_z))
    self.output_lines.append("M400 ; Wait for Z movement to complete")
    
    # ... Drawing commands ...
    
    # Add M400 after completing the drawing path
    self.output_lines.append("M400 ; Wait for drawing to complete")
```

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
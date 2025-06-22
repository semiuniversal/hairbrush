# Technical Context

## Technology Stack
- **Inkscape Extension**: Python with `inkex` for SVG processing and G-code generation
- **Web Controller**: Flask-based web server with Telnet/HTTP client for Duet communication
- **Hardware Control**: Duet 2 WiFi board running RepRapFirmware

## Development Environment
- **OS**: Development in WSL (Ubuntu) on Windows
- **Tools**: 
  - Python development environment with `uv` for virtual environment management
  - Inkscape for testing extensions
- **Dependencies**: 
  - Python 3.8+
  - `inkex` (Inkscape extension library)
  - Flask (for web controller)
  - Dependencies managed via pyproject.toml

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
│   ├── gcode_generator.py       # G-code generation with Z-optimization
│   └── config.py                # Configuration management
└── README.md                    # Documentation and usage guide
```

### Web Controller
```
web_controller/
├── web_server.py                # Flask web server
├── duet_client.py               # Duet communication client
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

## Communication Protocols
- **Extension → Web Controller**: G-code files
- **Web Controller → Duet**: 
  - Telnet (port 23) for G-code streaming
  - HTTP API (port 80) for status and configuration
  - WebSocket for real-time updates

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Use `uv` for virtual environment management
- Use pyproject.toml for dependency management 
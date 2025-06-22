# System Patterns

## Architecture Overview
The H.Airbrush system consists of three main components:
1. **Inkscape Extension**: SVG processing and G-code generation
2. **H.Airbrush Web Controller**: Machine control and monitoring interface
3. **Duet 2 WiFi Controller**: Hardware control and execution

## Key Components

### Inkscape Extension
- **Key Modules**: `hairbrush.inx` (UI definition), `hairbrush_control.py` (entry point), `hairbrush_lib/` (processing modules)
- **Responsibilities**: SVG parsing, path optimization, G-code generation, export configuration

### Web Controller
- **Key Modules**: `web_server.py`, `duet_client.py`, `job_manager.py`, web UI templates
- **Responsibilities**: Machine control interface, G-code management, status monitoring

### Duet 2 WiFi Controller
- **Responsibilities**: Execute G-code, control hardware (steppers, airbrushes), report status

## Communication Flow
- **Extension → Web Controller**: G-code files
- **Web Controller → Duet**: Telnet (G-code streaming), HTTP API (status/config), WebSocket (updates)
- **User → Web Controller**: Browser-based UI

## Data Models
- **G-code**: Standard format with H.Airbrush extensions for brush control
- **Machine Configuration**: Communication settings, dimensions, brush configurations
- **Job Status**: Position tracking, tool state, progress monitoring

## Technical Decisions
- **Python Implementation**: Cross-platform compatibility with Inkscape
- **Web-based Control Interface**: Accessible from any device on local network
- **Modular Architecture**: Separation of design, control, and hardware layers
- **Z-Movement Optimization**: Path batching to minimize slow Z-axis movements

## Optimization Patterns

### Path Batching
- Group paths by brush type and Z-height to minimize tool changes
- Raise Z only once per batch of similar paths
- Toggle paint flow without changing Z position when possible

### Movement Sequencing
- Strictly separate Z and XY movements to maintain flat drawings
- Always complete Z movements before starting XY movements
- Keep Z constant during all drawing operations

### Hardware Considerations
- Z-axis moves 20x slower than X/Y axes, requiring special optimization
- SVG stroke properties map to Z-height, paint flow, and movement speed
- Constant stroke width/opacity in SVG aligns with Z-height batching

## System Boundaries
- **Inputs**: SVG files from Inkscape
- **Outputs**: G-code files and direct hardware control
- **Security**: Local network operation only with basic authentication 
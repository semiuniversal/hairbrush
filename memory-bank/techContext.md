# Technical Context

## Technology Stack
- **Frontend**: Inkscape Extension (Python with `inkex`)
- **Backend**: Python-based G-code generator
- **Configuration**: YAML-based command templates
- **Hardware Control**: G-code compatible with Duet 2 WiFi board
- **Optional UI**: Python (Tkinter or PyQt) for calibration interface

## Development Environment
- OS: Development in WSL (Windows Subsystem for Linux) on Windows
- Tools: 
  - Python development environment
  - `uv` for Python virtual environment management
  - Inkscape for testing extensions
  - Text editor or IDE with Python support
- Dependencies: 
  - Python 3.x
  - `inkex` (Inkscape extension library)
  - YAML parser
  - `telnetlib` (for optional components)
  - Tkinter or PyQt (for optional GUI components)
  - Dependencies managed via pyproject.toml (not requirements.txt)

## Build & Deployment
- Inkscape extension installation to user's Inkscape extensions directory
- Python package distribution for core components
- Simple installation script to handle dependencies and configuration
- Documentation for manual setup and configuration

## Testing Strategy
- Unit testing for path processing and G-code generation
- Integration testing with sample SVG files
- Dry-run mode for testing without hardware
- Simulation visualization for verifying output before physical plotting
- Hardware testing with actual plotter setup

## Performance Considerations
- Efficient path processing for complex SVG files
- Optimized G-code generation to reduce unnecessary movements
- Proper handling of brush offsets to maintain precision
- Consideration for real-time control latency in optional components

## ⚠️ CORE PROJECT INSTRUCTIONS ⚠️
- **CRITICAL**: All command-line operations MUST be executed in WSL, NOT in Windows
- Agents should ONLY PROPOSE commands for the user to run in WSL
- The user will execute all commands manually
- Use `uv` for virtual environment management instead of venv/virtualenv
- Use pyproject.toml for dependency management instead of requirements.txt 
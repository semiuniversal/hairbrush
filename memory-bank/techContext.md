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

## Inkscape Extension Architecture

The H.Airbrush Inkscape extension follows a modular architecture inspired by the AxiDraw extension:

```
inkscape_extension/
├── hairbrush.inx                # Extension UI definition
├── hairbrush_control.py         # Main entry point
├── hairbrush.py                 # Core functionality
├── install.py                   # Installation script
├── README.md                    # Documentation
├── hairbrush_lib/               # Core library modules
│   ├── __init__.py              # Package initialization
│   ├── svg_parser.py            # SVG parsing functionality
│   └── path_processor.py        # Path processing and G-code generation
└── hairbrush_deps/              # Dependencies and resources
    └── inx_img/                 # UI images
        ├── spacer_10px.svg      # Spacer image
        └── hr.svg               # Horizontal rule image
```

### Extension Components

1. **hairbrush.inx**: Defines the extension UI in Inkscape, including tabs, parameters, and options.

2. **hairbrush_control.py**: Main entry point that handles UI interaction and delegates to the core module.

3. **hairbrush.py**: Core module that implements the main functionality of the extension.

4. **hairbrush_lib/**: Library package containing the core functionality:
   - **svg_parser.py**: Parses SVG files and extracts paths and their attributes.
   - **path_processor.py**: Processes paths and generates G-code.

5. **install.py**: Installation script that copies the extension files to the Inkscape extensions directory.

### Integration with Inkscape

The extension integrates with Inkscape through the following mechanisms:

1. **Extension Registration**: The INX file registers the extension with Inkscape, defining its location in the Extensions menu.

2. **Parameter Handling**: The extension receives parameters from the Inkscape UI and processes them.

3. **SVG Processing**: The extension parses the SVG document provided by Inkscape and extracts paths.

4. **G-code Generation**: The extension generates G-code based on the extracted paths and user settings.

### Brush Selection Logic

The extension uses stroke color to determine which airbrush to use:
- Black stroke: Airbrush A
- White stroke: Airbrush B
- Other colors: Defaults to Airbrush A

Stroke width controls the height of the airbrush (multiplied by 10 to get a percentage).
Stroke opacity controls the paint flow and speed.

## ⚠️ CORE PROJECT INSTRUCTIONS ⚠️
- **CRITICAL**: All command-line operations MUST be executed in WSL, NOT in Windows
- Agents should ONLY PROPOSE commands for the user to run in WSL
- The user will execute all commands manually
- Use `uv` for virtual environment management instead of venv/virtualenv
- Use pyproject.toml for dependency management instead of requirements.txt 
# Dual Airbrush Plotter

This is a prototype Inkscape extension and G-code backend for a custom CoreXY dual-airbrush plotter powered by Duet 2 WiFi.

## Structure
- `inkscape_extension/` - Inkscape export tool
- `gcode_backend/` - Generates G-code from path instructions
- `controller/` - Telnet sender for real-time operation (optional)

## Development Setup

### Prerequisites
- WSL with Ubuntu 22.04 or later
- Python 3.8 or later
- [uv](https://github.com/astral-sh/uv) for virtual environment management
- Inkscape (for extension development and testing)

### Setting up the Development Environment

1. Clone the repository:
   ```bash
   git clone [repository_url]
   cd hairbrush
   ```

2. Create and activate the virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. For development tools:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Project Organization
- `inkscape_extension/`: Inkscape extension files (.inx and .py)
- `gcode_backend/`: G-code generation library and command templates
- `docs/`: Documentation and reference materials
- `tests/`: Test cases and fixtures (to be added)

### Contributing
1. Make sure your code follows the project's style guidelines (using Black and isort)
2. Add appropriate tests for new functionality
3. Update documentation as needed

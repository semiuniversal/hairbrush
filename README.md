# Hairbrush - Dual Airbrush Plotter Controller

A Python package and Inkscape extension for controlling a dual-airbrush plotter with a Duet 2 WiFi board.

## Features

- SVG parsing with layer support
- Path processing and simplification
- G-code generation for dual-airbrush control
- Inkscape extension for direct export

## Installation

### Prerequisites

- Python 3.8 or newer
- Inkscape 1.0 or newer (for the extension)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/hairbrush.git
cd hairbrush

# Create a virtual environment and install dependencies
python -m uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m uv pip install -e .
```

### Install the Inkscape Extension

```bash
python -m hairbrush.tools.install
```

## Usage

### Command Line Tools

#### Analyze SVG Files

```bash
python analyze_svg.py path/to/file.svg
```

#### Convert SVG to G-code

```bash
python path_to_gcode.py path/to/file.svg --output output.gcode
```

Options:
- `--layer LAYER_NAME`: Process only a specific layer
- `--simplify`: Simplify paths for smoother output
- `--tolerance VALUE`: Tolerance for path simplification (default: 0.5)
- `--z-height VALUE`: Z height for the brush (default: 2.0)
- `--feedrate VALUE`: Feedrate for movements (default: 1500)
- `--brush BRUSH_ID`: Brush to use (brush_a or brush_b)

### Inkscape Extension

1. Open your SVG file in Inkscape
2. Go to Extensions → Export → Dual Airbrush Export
3. Configure the settings and click Apply

## Project Structure

```
hairbrush/
├── src/
│   └── hairbrush/
│       ├── __init__.py
│       ├── svg_parser.py      # SVG parsing utilities
│       ├── path_processor.py  # Path processing and simplification
│       ├── gcode_generator.py # G-code generation
│       ├── config.py          # Configuration handling
│       └── tools/             # Command-line tools
├── inkscape_extension/        # Inkscape extension files
├── tests/                     # Test files
├── gcode_backend/             # G-code command templates
└── assets/                    # Example files
```

## Development

### Setup Development Environment

```bash
python -m uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m uv pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

## License

MIT License

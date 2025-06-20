# Hairbrush - Dual Airbrush Plotter Controller

A Python package and Inkscape extension for controlling a dual-airbrush plotter with a Duet 2 WiFi board.

## Features

- SVG parsing with layer support
- Path processing and simplification
- G-code generation for dual-airbrush control
- Inkscape extension for direct export
- Adaptive curve segmentation for improved Bezier curve approximation
- Support for all SVG path commands (M, L, H, V, C, S, Q, T, A, Z)
- SVG viewBox and document dimensions handling for proper scaling
- Debug markers for visualizing path conversion
- Automatic brush selection based on fill color
- User-defined scaling and offset for G-code output
- Robust handling of Inkscape-specific SVG features

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
- `--curve-resolution VALUE`: Number of segments for curve approximation (default: 10)
- `--debug-markers`: Add debug markers to the G-code
- `--scale-factor VALUE`: Additional scaling factor to apply (default: 1.0)
- `--offset-x VALUE`: X offset to apply after all transformations (default: 0.0)
- `--offset-y VALUE`: Y offset to apply after all transformations (default: 0.0)

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
├── tests/                     # Test files and examples
│   ├── svg_samples/           # Sample SVG files for testing
│   ├── test_path_processing.py # Test script for path processing
│   ├── test_improved_path_processing.py # Test script for improved path processing
│   ├── test_gcode_generation.py # Test script for G-code generation
│   └── visualize_gcode.py     # Script to visualize G-code output
├── gcode_backend/             # G-code command templates
└── assets/                    # Example files
```

### Testing Path Processing

```bash
python tests/test_path_processing.py tests/svg_samples/test_curves.svg
```

### Testing Improved Path Processing

```bash
python tests/test_improved_path_processing.py
```

### Testing G-code Generation

```bash
python tests/test_gcode_generation.py tests/svg_samples/test_curves.svg --output test_output.gcode
```

### Visualizing G-code Output

```bash
python tests/visualize_gcode.py test_output.gcode --output test_output.svg
```

## Path Processing Improvements

The path processing system has been enhanced with:

1. **Adaptive Bezier Curve Segmentation**: Automatically adjusts the number of segments based on curve complexity and curvature.
2. **Improved Arc Approximation**: More accurate elliptical arc rendering based on the SVG specification.
3. **Complete SVG Path Command Support**: Properly handles all SVG path commands including smooth curves and arcs.
4. **Robust Coordinate Transformation**: Correctly transforms from SVG coordinate space to G-code coordinate space.

## G-code Generation Improvements

The G-code generator now includes:

1. **Proper Document Scaling**: Handles SVG viewBox, width, and height correctly.
2. **User-defined Transformations**: Allows custom scaling and positioning of the output.
3. **Automatic Brush Selection**: Chooses the appropriate brush based on path fill color.
4. **Enhanced Path Processing**: Uses the improved path processor for more accurate G-code output.

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
# H.Airbrush - Dual Airbrush Plotter Controller

An Inkscape extension for controlling a dual-airbrush plotter with a Duet 2 WiFi board.

## Features

- SVG parsing with layer support
- Path processing and simplification
- G-code generation for dual-airbrush control
- Inkscape extension for direct export
- Adaptive curve segmentation for improved Bezier curve approximation
- Support for all SVG path commands (M, L, H, V, C, S, Q, T, A, Z)
- SVG viewBox and document dimensions handling for proper scaling
- Automatic brush selection based on stroke color
- User-defined scaling and offset for G-code output
- Robust handling of Inkscape-specific SVG features
- Physics-based airbrush parameter calculation for optimal output

## Installation

### Prerequisites

- Python 3.8 or newer
- Inkscape 1.0 or newer
- WSL (Windows Subsystem for Linux) if using Windows

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/hairbrush.git
cd hairbrush

# Create a virtual environment and install dependencies
python -m uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r inkscape_extension/requirements.txt
```

### Install the Inkscape Extension

```bash
python inkscape_extension/install.py
```

This will copy the necessary files to your Inkscape extensions directory.

## Usage

### Inkscape Extension

#### Using the Extension

1. Create or open an SVG file in Inkscape
2. Design your artwork using paths, shapes, or objects converted to paths
3. Use stroke colors to specify which airbrush to use:
   - Black strokes will use Brush A (Black)
   - White strokes will use Brush B (White)
4. Adjust stroke width to control airbrush height (thicker strokes = greater height)
5. Adjust stroke opacity to control paint flow and speed (lower opacity = less paint and faster movement)
6. Go to `Extensions > H.Airbrush > Export G-code`
7. Configure the export options in the dialog that appears
8. Click "Apply" to export the G-code file

#### Export Options

- **Default Brush**: Select the default brush to use (A=Black, B=White)
- **Base Z Height**: Base height for the airbrush (mm)
- **Base Feedrate**: Base movement speed (mm/min)
- **Curve Resolution**: Higher values give smoother curves but larger files
- **Simplify Paths**: Reduce the number of points in paths
- **Simplification Tolerance**: Higher values simplify more aggressively
- **Scale Factor**: Scale the output by this factor
- **X/Y Offset**: Move the output by this amount (mm)
- **Brush Offsets**: Adjust the position of each brush independently
- **Z Travel Height**: Height for travel moves between paths
- **Skip Homing**: Option to skip the homing command in G-code

### Visualizing G-code

You can visualize the generated G-code using online tools like [NC Viewer](https://ncviewer.com/), which provides an interactive 3D visualization of the toolpaths.

## Project Structure

```
hairbrush/
├── inkscape_extension/        # Main Inkscape extension files
│   ├── hairbrush.inx          # Main extension XML definition
│   ├── hairbrush.py           # Core extension implementation
│   ├── hairbrush_control.py   # Extension control interface
│   ├── hairbrush_export_effect.inx # Export effect XML definition
│   ├── hairbrush_export_effect.py  # Export effect implementation
│   ├── check_installation.inx # Installation check XML definition
│   ├── check_installation.py  # Installation check implementation
│   ├── install.py             # Installation script
│   ├── requirements.txt       # Python dependencies
│   ├── hairbrush_lib/         # Core library modules
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration handling
│   │   ├── gcode_generator.py # G-code generation
│   │   ├── path_processor.py  # Path processing and simplification
│   │   ├── svg_parser.py      # SVG parsing utilities
│   │   └── templates/         # Template files
│   └── vendor/                # Vendored dependencies
├── memory-bank/               # Project documentation and planning
└── assets/                    # Example files
```

## Path Processing Features

The path processing system includes:

1. **Adaptive Bezier Curve Segmentation**: Automatically adjusts the number of segments based on curve complexity and curvature.
2. **Improved Arc Approximation**: More accurate elliptical arc rendering based on the SVG specification.
3. **Complete SVG Path Command Support**: Properly handles all SVG path commands including smooth curves and arcs.
4. **Robust Coordinate Transformation**: Correctly transforms from SVG coordinate space to G-code coordinate space.

## G-code Generation Features

The G-code generator includes:

1. **Proper Document Scaling**: Handles SVG viewBox, width, and height correctly.
2. **User-defined Transformations**: Allows custom scaling and positioning of the output.
3. **Automatic Brush Selection**: Chooses the appropriate brush based on path stroke color.
4. **Physics-based Airbrush Parameters**: Calculates optimal Z-height, paint flow, and movement speed based on stroke width and opacity.
5. **Optimized G-code**: Generates clean, efficient G-code with proper separation of Z and XY movements.

## License

MIT License
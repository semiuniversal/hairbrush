# H.Airbrush - Inkscape Extension

This Inkscape extension allows you to export SVG paths to G-code for a dual-airbrush plotter system.

## Features

- Exports SVG paths to G-code for dual-airbrush plotter
- Supports all SVG path commands and basic shapes
- Converts stroke color to airbrush selection (black/white)
- Uses stroke width to control airbrush height
- Uses stroke opacity to control paint flow and speed
- Configurable options for scaling, offsets, and simplification

## Installation

### Windows

1. Download the latest release from the GitHub repository
2. Run the installer script:
   ```
   python install.py
   ```
3. Restart Inkscape

### Manual Installation

1. Copy the following files to your Inkscape extensions directory:
   - `hairbrush.inx`
   - `hairbrush_control.py`
   - `hairbrush.py`
   - `hairbrush_lib/` (directory and all contents)
   - `hairbrush_deps/` (directory and all contents)
2. Restart Inkscape

The Inkscape extensions directory is typically located at:
- Windows: `C:\Program Files\Inkscape\share\inkscape\extensions` or `%APPDATA%\inkscape\extensions`
- macOS: `/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions`
- Linux: `~/.config/inkscape/extensions` or `/usr/share/inkscape/extensions`

## Usage

1. Open Inkscape and load your SVG file
2. Go to Extensions > H.Airbrush > H.Airbrush Control
3. Configure the settings as needed
4. Click "Apply" to generate G-code

### Brush Selection

The extension uses stroke color to determine which airbrush to use:
- Black stroke: Airbrush A
- White stroke: Airbrush B
- Other colors: Defaults to Airbrush A

### Brush Height

Stroke width controls the height of the airbrush:
- Stroke width is multiplied by 10 to get a height value (0-100%)
- Default stroke width of 1 = 10% height

### Opacity

Stroke opacity controls the paint flow and speed:
- 100% opacity = full paint flow
- Lower opacity = reduced paint flow

## G-code Output

The generated G-code includes:
- Proper initialization and homing commands
- Brush selection based on stroke color
- Height control based on stroke width
- Speed control based on settings
- Proper path following with optimized movements

## Troubleshooting

If the extension doesn't appear in Inkscape:
1. Verify the files are in the correct location
2. Check the Inkscape console for error messages
3. Try running the installation script again with admin privileges
4. Check the log file at `%TEMP%\hairbrush_debug.log` (Windows) or `/tmp/hairbrush_debug.log` (Linux/macOS)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
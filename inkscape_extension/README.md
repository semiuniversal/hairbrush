# Dual Airbrush Export Extension for Inkscape

This Inkscape extension allows you to export SVG layers as G-code for a dual-airbrush plotter with a Duet 2 WiFi board.

## Installation

### Prerequisites
- Inkscape 1.0 or newer
- Python 3.8 or newer

### Method 1: Install as a standalone extension (Recommended)

1. Find your Inkscape extensions directory:
   - On Windows: `C:\Users\[USERNAME]\AppData\Roaming\inkscape\extensions`
   - On Linux: `~/.config/inkscape/extensions/`
   - On macOS: `~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/`

2. Create a `hairbrush` directory in the extensions folder

3. Copy the following files:
   - Copy `dual_airbrush_export.inx` and `dual_airbrush_export.py` to the Inkscape extensions directory
   - Copy the entire contents of `src/hairbrush` to the `hairbrush` directory you created in the extensions folder

4. Restart Inkscape

### Method 2: Install with pip (For developers)

1. Install the hairbrush package:
   ```
   pip install -e /path/to/hairbrush
   ```

2. Copy only these files to the Inkscape extensions directory:
   - `dual_airbrush_export.inx`
   - `dual_airbrush_export.py`

3. Restart Inkscape

## Usage

1. Open your SVG file in Inkscape
2. Make sure you have layers named according to your configuration (default: "black" and "white")
3. Go to Extensions → Dual Airbrush → Export to G-code
4. Configure the settings and click Apply
5. The G-code file will be saved to the specified location

## Configuration

The extension provides several configuration options:

### Layers Tab
- **Black Layer Name**: The name of the layer containing paths for the black airbrush
- **White Layer Name**: The name of the layer containing paths for the white airbrush
- **Processing Order**: Which layer to process first (black or white)

### Machine Settings Tab
- **Z Height**: The height of the airbrush nozzle above the surface
- **Feedrate**: The movement speed during drawing
- **Travel Feedrate**: The movement speed during non-drawing moves
- **Brush Offset X/Y**: The offset between the two airbrushes

### Output Tab
- **Output Path**: Where to save the G-code file
- **Add Comments**: Include descriptive comments in the G-code
- **Preview G-code**: Show a preview of the generated G-code

## Troubleshooting

If you encounter issues with the extension:

1. **Extension not appearing in Inkscape**:
   - Make sure the `.inx` and `.py` files are in the correct Inkscape extensions directory
   - Check that you have restarted Inkscape after installation
   - Verify that the files have the correct permissions

2. **ImportError for hairbrush modules**:
   - Make sure the hairbrush package is correctly installed
   - If using Method 1, verify that the hairbrush directory is in the Inkscape extensions directory
   - If using Method 2, verify that the pip installation was successful

3. **Layer processing issues**:
   - Verify that your SVG has properly named layers
   - Check that the layer names in the extension settings match your SVG layers

4. **Output file issues**:
   - Make sure you have write permissions to the output directory
   - Try specifying an absolute path for the output file

For more help, please open an issue on the GitHub repository. 
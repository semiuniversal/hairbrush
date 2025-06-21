# Hairbrush G-code Export - Inkscape Extension

This directory contains the packaged Inkscape extension for the Hairbrush dual-airbrush plotter.

## Installation

To install the extension:

1. Copy the entire `hairbrush_extension` directory to your Inkscape extensions directory:

   **Windows:**
   ```
   C:\Users\<username>\AppData\Roaming\Inkscape\extensions\
   ```

   **Linux:**
   ```
   ~/.config/inkscape/extensions/
   ```

   **macOS:**
   ```
   ~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/
   ```

2. Restart Inkscape.

3. The extension should now be available in the `Extensions > Export > Hairbrush G-code Export` menu.

## Usage

See the README.md file inside the hairbrush_extension directory for detailed usage instructions.

## Files Included

- `hairbrush_extension/hairbrush_export_effect.inx` - Extension definition file
- `hairbrush_extension/hairbrush_export_effect.py` - Main extension script
- `hairbrush_extension/hairbrush_lib/` - Supporting library files:
  - `__init__.py` - Package initialization
  - `path_processor.py` - SVG path processing functions
  - `svg_parser.py` - SVG parsing functions
  - `gcode_generator.py` - G-code generation functions
- `hairbrush_extension/README.md` - Detailed documentation

## Troubleshooting

If the extension doesn't appear in Inkscape:

1. Make sure you've copied the entire directory to the correct location
2. Check Inkscape's extension error log (Edit > Preferences > System > Extensions > Open extension errors log)
3. Verify file permissions (all files should be readable)

## License

This extension is released under the same license as the Hairbrush project. 
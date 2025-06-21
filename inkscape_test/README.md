# Inkscape Test Extensions

This directory contains test extensions to verify that Inkscape can properly load and run our extensions.

## Effect-Type Export Extension (Recommended)

The `test_export_effect.inx` and `test_export_effect.py` files create an extension that appears in the Extensions > Export menu, similar to the "Plot..." option.

### Installation

1. Copy both `test_export_effect.inx` and `test_export_effect.py` to your Inkscape extensions directory:
   - Windows: `C:\Users\<username>\AppData\Roaming\Inkscape\extensions\`
   - Linux: `~/.config/inkscape/extensions/`
   - macOS: `~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/`

2. Restart Inkscape completely

3. Test the extension:
   - Open any SVG file in Inkscape
   - Go to `Extensions > Export > Test G-code Export`
   - Configure the options and specify an output path
   - Click "Apply"
   - Check if the G-code file was created with the expected content

### Expected Output

The generated G-code should be a simple square and should look like this:

```gcode
; Test G-code Export (Effect Extension)
; Feedrate: 1500 mm/min
; Z Height: 2.0 mm

G21 ; Set units to mm
G90 ; Set absolute positioning
G0 X0 Y0 Z5.0 ; Move to origin
G0 X10 Y10 Z2.0 ; Draw a line
G1 X20 Y10 F1500 ; Draw a line
G1 X20 Y20 F1500 ; Draw another line
G1 X10 Y20 F1500 ; Draw another line
G1 X10 Y10 F1500 ; Close the square
G0 Z5.0 ; Lift the tool
G0 X0 Y0 ; Return to origin
```

## Output-Type Extension (Alternative)

The `test_export.inx` and `test_export.py` files create an extension that adds a new file format to the Save As dialog.

### Installation

1. Copy both `test_export.inx` and `test_export.py` to your Inkscape extensions directory.

2. Restart Inkscape completely

3. Test the extension:
   - Open any SVG file in Inkscape
   - Go to `File > Save As...`
   - Look for "Test G-code (*.gcode)" in the file type dropdown
   - Save the file and check if it contains the test G-code

## Troubleshooting

If the extensions don't appear:
1. Check Inkscape's extension error log:
   - In Inkscape: Edit > Preferences > System > Extensions > Open extension errors log
2. Make sure all files have the correct permissions
3. Verify that the Python version used by Inkscape can import the `inkex` module 
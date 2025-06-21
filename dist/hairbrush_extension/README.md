# Hairbrush G-code Export - Inkscape Extension

This Inkscape extension allows you to export SVG paths to G-code for a dual-airbrush plotter system.

## Features

- Exports SVG paths to G-code for dual-airbrush plotter
- Supports all SVG path commands and basic shapes
- Converts stroke color to airbrush selection (black/white)
- Uses stroke width to control airbrush height
- Uses stroke opacity to control paint flow and speed
- Configurable options for scaling, offsets, and simplification

## Installation

1. Copy the following files to your Inkscape extensions directory:
   - `hairbrush_export_effect.inx`
   - `hairbrush_export_effect.py`
   - `hairbrush_lib` directory and its contents

   Inkscape extensions directory locations:
   - Windows: `C:\Users\<username>\AppData\Roaming\Inkscape\extensions\`
   - Linux: `~/.config/inkscape/extensions/`
   - macOS: `~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/`

2. Restart Inkscape.

## Usage

1. Create or open an SVG file in Inkscape
2. Design your artwork using paths, shapes, or objects converted to paths
3. Use stroke colors to specify which airbrush to use:
   - Black strokes will use Brush A (Black)
   - White strokes will use Brush B (White)
4. Adjust stroke width to control airbrush height (thicker strokes = greater height)
5. Adjust stroke opacity to control paint flow and speed (lower opacity = less paint and faster movement)
6. Go to `Extensions > Export > Hairbrush G-code Export`
7. Configure the export options in the dialog
8. Click "Apply" to export the G-code file

## Export Options

### Options Tab
- **Default Brush**: Select the default brush to use (A=Black, B=White)
- **Base Z Height**: Base height for the airbrush (mm)
- **Base Feedrate**: Base movement speed (mm/min)
- **Curve Resolution**: Higher values give smoother curves but larger files
- **Simplify Paths**: Reduce the number of points in paths
- **Simplification Tolerance**: Higher values simplify more aggressively
- **Add Debug Markers**: Add comments in G-code for debugging
- **Output file**: Path where to save the G-code file (leave empty to use SVG filename)

### Transform Tab
- **Scale Factor**: Scale the output by this factor
- **X Offset**: Move the output horizontally by this amount (mm)
- **Y Offset**: Move the output vertically by this amount (mm)

## Troubleshooting

If the extension doesn't appear or doesn't work correctly:

1. Check Inkscape's extension error log:
   - In Inkscape: Edit > Preferences > System > Extensions > Open extension errors log

2. Check file permissions:
   - Make sure the extension files are readable by Inkscape

## G-code Visualization

You can visualize the generated G-code using online tools like [NC Viewer](https://ncviewer.com/).

## License

This extension is released under the same license as the hairbrush project. 
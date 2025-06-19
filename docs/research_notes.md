# Research Notes

## Inkscape Extension Development

### Resources
- [Inkscape Extension Documentation](https://inkscape.org/develop/extensions/)
- [inkex Python Module Documentation](https://inkscape.gitlab.io/extensions/documentation/inkex.html)
- [Inkscape Extensions Repository](https://gitlab.com/inkscape/extensions)
- [Inkscape Extension Tutorial](https://inkscape.gitlab.io/extensions/documentation/tutorial/index.html)
- [AxiDraw Extension GitHub](https://github.com/evil-mad/axidraw)

### Key Concepts
- Extension types: Effect, Output, Input, etc.
- .inx file format for UI definition
- inkex module for SVG manipulation
- Path data representation and transformation
- Layer management and selection

### Extension Structure
- Two main files required:
  - `.inx` file: XML file that defines the UI and extension parameters
  - `.py` file: Python script that implements the extension functionality
- Extensions inherit from classes like `inkex.EffectExtension` or `inkex.OutputExtension`
- Parameters defined in the INX file are passed to the Python script

### INX File Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<inkscape-extension xmlns="http://www.inkscape.org/namespace/inkscape/extension">
  <name>Extension Name</name>
  <id>unique.id.for.extension</id>
  
  <!-- Parameters -->
  <param name="param_name" type="float" _gui-text="Parameter Label">default_value</param>
  
  <!-- Extension type definition -->
  <effect>
    <effects-menu>
      <submenu name="Submenu Name"/>
    </effects-menu>
  </effect>
  
  <!-- Script reference -->
  <script>
    <command reldir="extensions" interpreter="python">script_name.py</command>
  </script>
</inkscape-extension>
```

### Python Extension Implementation
```python
#!/usr/bin/env python3
import inkex

class MyExtension(inkex.EffectExtension):
    def add_arguments(self, pars):
        # Define parameters matching INX file
        pars.add_argument("--param_name", type=float, default=0.0)
    
    def effect(self):
        # Access parameters with self.options.param_name
        # Access selected elements with self.svg.selection
        # Implement extension functionality here
        pass

if __name__ == '__main__':
    MyExtension().run()
```

### AxiDraw Extension Insights
- Uses a main control class that handles different operations (plot, setup, manual control)
- Implements tab-based UI with different parameter sets
- Handles layer-based plotting with options for specific layers
- Manages machine-specific settings through configuration files
- Implements SVG path processing for conversion to plotter movements

### Questions to Explore
- How to extract paths from specific layers?
- How to handle SVG transformations?
- How to implement parameter input in the extension UI?
- How to access stroke properties (width, opacity)?
- How to handle different path types (lines, curves, etc.)?

## Duet 2 WiFi G-code Commands

### Resources
- [Duet G-code Documentation](https://duet3d.dozuki.com/Wiki/Gcode)
- [Duet_Plotter_GCode_Reference.md](../Duet_Plotter_GCode_Reference.md)

### Key Commands
- Movement: G0, G1
- Servo control: M280
- I/O control: M42
- Configuration: G90, G91, G92

### Questions to Explore
- How to control airbrush on/off?
- How to handle Z-height for different surfaces?
- How to implement brush offsets?
- What's the optimal feedrate for airbrush painting?
- How to handle pauses for color/brush changes?

## Command Template System

### Design Considerations
- YAML structure for mapping abstract actions to G-code
- Template variables and substitution
- Validation rules for templates
- Default values and overrides
- Hardware abstraction for different controllers

### Example Template Structure
```yaml
# Example structure to explore
brush_a:
  offset: [0, 0]
  air_on: "M42 P0 S1"
  air_off: "M42 P0 S0"
  paint_on: "M280 P0 S90"
  paint_off: "M280 P0 S0"
```

## SVG Path Processing

### Concepts to Research
- SVG path data format
- Bezier curve representation
- Path flattening algorithms
- Transformation matrices
- Optimizing path traversal for plotting

## Notes from Research

### Inkscape Extension Development
- Inkscape 1.0+ uses Python 3, older versions use Python 2
- Extensions can be installed in the user extensions directory (Edit > Preferences > System: User extensions)
- The `inkex` module provides classes for SVG manipulation and extension development
- Extensions can be invoked from the Inkscape UI or via command line
- Path data can be accessed and modified using `inkex.Path` objects
- Layer information is stored in SVG groups with specific attributes 
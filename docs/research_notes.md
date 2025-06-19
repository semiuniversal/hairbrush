# Research Notes

## Inkscape Extension Development

### Resources
- [Inkscape Extension Documentation](https://inkscape.org/develop/extensions/)
- [inkex Python Module Documentation](https://inkscape.gitlab.io/extensions/documentation/inkex.html)
- [Inkscape Extensions Repository](https://gitlab.com/inkscape/extensions)

### Key Concepts
- Extension types: Effect, Output, Input, etc.
- .inx file format for UI definition
- inkex module for SVG manipulation
- Path data representation and transformation
- Layer management and selection

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

[This section will be populated as research progresses] 
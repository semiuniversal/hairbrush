# Project Brief

## Overview
Software to control a custom-built dual-airbrush CoreXY plotter driven by a Duet 2 WiFi board. The system provides an intuitive workflow for artists who work in vector graphics (e.g., SVGs from Inkscape) to produce high-precision paintings using black and white ink channels.

## Goals
- Create a general-purpose open source painting plotter controller
- Develop a potentially commercially viable, artist-ready creative tool
- Abstract away technical details of G-code and machine control
- Offer both beginner-friendly and power-user modes

## Requirements
### Phase 1 (Core Components)
- Inkscape Extension
  - Export multi-layer SVGs as Duet-compatible G-code with minimal configuration
  - Configure layer names, Z-height, brush offsets, feedrate, and output file path
- G-code Backend Generator
  - Convert parsed paths into Duet-friendly G-code
  - Support command templates for different brush configurations
  - Handle air on/off commands and servo trigger control

### Phase 2 (Optional Components)
- Telnet Controller
  - Send G-code to Duet in real time without Duet Web Control
  - Support manual jog and command input modes
- Calibration & Manual Mode GUI
  - Assist in setup, alignment, and troubleshooting
  - Provide UI for jog control, brush actions, and offset testing

## Constraints
- Must work with Duet 2 WiFi board
- Initial focus on black/white dual-airbrush setup
- Must be accessible to artists without G-code knowledge

## Success Criteria
- Artists can create vector graphics in Inkscape and export directly to plotter
- System handles brush offsets and control transparently
- Modular and readable codebase suitable for open-source release
- Support for hardware abstraction (Duet, Marlin, GRBL) 
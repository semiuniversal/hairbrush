# System Patterns

## Architecture Overview
The system follows a modular architecture with clear separation of concerns. It consists of an Inkscape extension for the user interface, a G-code backend generator for translating vector paths to machine commands, and optional components for direct machine control and calibration.

## Key Components
- **Inkscape Extension**: Front-end GUI that integrates with Inkscape to collect user parameters and initiate the export process.
- **G-code Backend Generator**: Core component that converts SVG paths to machine-specific G-code using configurable command templates.
- **Command Template System**: YAML-based configuration that maps abstract brush actions to specific G-code commands.
- **Telnet Controller** (Phase 2): Optional component for direct machine communication without requiring Duet Web Control.
- **Calibration & Manual Mode GUI** (Phase 2): Optional interface for machine setup, testing, and troubleshooting.

## Design Patterns
- **Template Method**: Used in the G-code generation to support different hardware configurations.
- **Command Pattern**: Abstracts machine-specific commands behind a unified interface.
- **Adapter Pattern**: Translates between SVG path data and G-code commands.
- **Factory Pattern**: Creates appropriate command generators based on machine configuration.

## Data Flow
1. User creates artwork in Inkscape with separate layers for black and white elements
2. Inkscape extension extracts path data from specified layers
3. Backend generator converts paths to G-code using command templates
4. G-code is saved to file or sent directly to the machine
5. Machine executes commands to create the physical artwork

## Technical Decisions
- **Inkscape Extension**: Using Inkscape's extension API (`inkex`) to leverage existing vector editing capabilities.
- **YAML Command Templates**: Allowing for hardware abstraction and easy configuration without code changes.
- **Python Implementation**: Chosen for cross-platform compatibility and ease of integration with Inkscape.
- **Modular Architecture**: Separating UI, path processing, and G-code generation for better maintainability.

## System Boundaries
- **Inputs**: SVG files from Inkscape with specified layer structure
- **Outputs**: G-code files compatible with Duet, Marlin, or GRBL controllers
- **External Interfaces**: 
  - Inkscape Extension API
  - Duet 2 WiFi board (primary target)
  - Optional Telnet/HTTP interfaces for direct control 
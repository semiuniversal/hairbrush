# Active Context

## Current Focus

We have completed a comprehensive redesign of the Inkscape extension for the H.Airbrush project, following the structure and patterns of the AxiDraw extension. The new implementation should resolve the issues with the extension not showing up in Inkscape.

### Key Accomplishments

1. **Complete Extension Structure Redesign**
   - Created a modular architecture following the AxiDraw model
   - Implemented proper error handling and logging
   - Added support for all SVG path commands and shapes

2. **Improved User Interface**
   - Created a detailed INX file with multiple tabs and options
   - Added support for different brush settings
   - Implemented manual control, layer-based plotting, and pause/resume functionality

3. **Enhanced Installation Process**
   - Created a robust installation script for Windows
   - Added automatic detection of Inkscape extensions directory
   - Created detailed installation documentation for all platforms

### Next Steps

1. **Testing**
   - Test installation on Windows Inkscape
   - Verify extension appears in Inkscape UI
   - Test SVG to G-code conversion with different SVG files

2. **Documentation**
   - Create user guide with examples
   - Document G-code commands and parameters
   - Create troubleshooting guide

3. **Additional Features**
   - Implement preview functionality
   - Add custom brush configuration support
   - Create calibration patterns and test files

## Current Issues
- **Namespace Handling**: Current SVG parser doesn't handle Inkscape namespaces properly
- **Path Command Support**: Limited support for all SVG path commands
- **Curve Approximation**: Complex curves aren't being properly approximated
- **Coordinate Transformation**: Incorrect mapping from SVG space to machine space
- **Path Distortion**: G-code visualization shows that SVG paths are being distorted during conversion

## Testing
- Successfully parsed the sample SVG file (`drawing_test.svg`)
- Generated G-code output but identified issues with path accuracy
- Need to improve testing with more complex SVG files

## Dependencies
- Inkscape 1.0+ for testing the extension
- Python 3.8+ with minimal dependencies (lxml, PyYAML)
- WSL environment for development and testing

## Notes
- The current extension implementation is based on the AxiDraw extension architecture
- We are focusing on a layer-based approach where different brushes are assigned to different layers
- The extension currently supports basic path commands (M, L, H, V, Z) with simplified handling of curves
- Future work will include more sophisticated curve handling and optimization
- We're following a "just-in-time" approach to dependencies, adding them only when needed

## Recent Changes
- Initial memory bank setup - [Current date]
- Project brief imported from Project_Brief.md - [Current date]
- Added critical development environment requirements (WSL, uv, pyproject.toml) - [Current date]
- Created implementation plan with 7 stages - [Current date]
- Updated tasks to align with implementation plan - [Current date]
- Reviewed and revised implementation plan - [Current date]
  - Combined template system and SVG processing into a single Core Library Development stage
  - Added research tasks to Stage 1
  - Added user feedback stage before Phase 2 planning
  - Enhanced testing criteria with real-world examples
- Set up development environment - [Current date]
  - Verified WSL installation (Ubuntu 22.04.5 LTS)
  - Created pyproject.toml for dependency management
  - Initialized uv virtual environment
  - Created .gitignore file
- Created test directory structure - [Current date]
  - Added sample SVG for testing
  - Created basic test files for template parser and SVG parser
- Created research_notes.md for documenting findings - [Current date]
- Updated README.md with setup instructions - [Current date]
- Studied AxiDraw extension codebase for best practices - [Current date]
- Created installation tools for the extension - [Current date]
- Optimized dependency management approach - [Current date]
- Implemented path processing improvements - [Current date]
  - Added adaptive curve segmentation for Bezier curves
  - Implemented support for all SVG path commands (C, S, Q, T, A)
  - Added helper methods for calculating control points and approximating arcs
  - Improved curve resolution with curvature-based segmentation
- Enhanced G-code generation - [Current date]
  - Added SVG viewBox and document dimensions handling
  - Implemented coordinate transformation between SVG and G-code space
  - Added debug markers for visualizing path conversion
  - Improved error handling and progress reporting
- Redesigned Inkscape extension structure for better Windows compatibility - [Current date]
- Created simplified hairbrush.inx file with improved UI organization - [Current date]
- Implemented diagnostic check_installation tool for troubleshooting - [Current date]
- Updated README with clear installation instructions - [Current date]

## Open Questions
- What is the current state of the hardware (dual-airbrush CoreXY plotter)?
- Are there any existing G-code examples or templates to reference?
- What are the specific requirements for the Inkscape extension UI?
- Are there any specific performance constraints for the G-code generation?
- What specific Linux distribution is being used in WSL? (Answered: Ubuntu 22.04.5 LTS)
- Are there any preferences for project structure or naming conventions?
- Who will be participating in user testing in Stage 6?

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Agents should ONLY PROPOSE commands for the user to run in WSL
- The user will execute all commands manually
- Use uv for virtual environment management
- Use pyproject.toml for dependency management
- Follow minimalist approach to dependencies 
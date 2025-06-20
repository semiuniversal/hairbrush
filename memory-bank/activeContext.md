# Active Context

## Current Focus
We are currently working on improving the SVG parsing and path processing components of the hairbrush extension for Inkscape, based on our analysis of the AxiDraw extension code. Our goal is to adapt the proven approaches from AxiDraw's SVG processing while changing the output to generate proper G-code for the dual-airbrush plotter.

The main focus areas are:
1. Enhancing SVG parsing to handle all SVG elements and namespaces correctly
2. Implementing sophisticated path processing that accurately handles all SVG path commands
3. Ensuring accurate transformation from SVG coordinate space to machine coordinate space
4. Generating optimized G-code that correctly represents SVG paths and supports dual-airbrush control

## Recent Progress
1. **Enhanced SVG Parser**
   - Added functionality to extract document properties
   - Implemented path analysis and bounding box calculation
   - Added support for extracting style attributes and path IDs
   - Improved layer detection and management

2. **Path Processing**
   - Created a robust `PathProcessor` class for SVG path manipulation
   - Implemented path command parsing and classification
   - Added conversion between relative and absolute coordinates
   - Implemented Bezier curve approximation
   - Added path simplification using Ramer-Douglas-Peucker algorithm

3. **Analysis Tools**
   - Created `analyze_svg.py` for detailed SVG analysis
   - Implemented path bounds calculation
   - Added layer structure analysis

4. **G-code Generation**
   - Created `path_to_gcode.py` for SVG to G-code conversion
   - Added support for layer selection
   - Implemented path simplification options
   - Added Z-height and feedrate control
   - Added brush selection

5. **AxiDraw Code Analysis**
   - Studied AxiDraw extension code structure and approach
   - Identified key differences with our current implementation
   - Created detailed implementation plan based on findings
   - Updated tasks to incorporate lessons from AxiDraw code

## Current Issues
- **Namespace Handling**: Current SVG parser doesn't handle Inkscape namespaces properly
- **Path Command Support**: Limited support for all SVG path commands
- **Curve Approximation**: Complex curves aren't being properly approximated
- **Coordinate Transformation**: Incorrect mapping from SVG space to machine space
- **Path Distortion**: G-code visualization shows that SVG paths are being distorted during conversion

## Next Steps
1. **Improve SVG Parsing**:
   - Enhance namespace handling for Inkscape SVGs
   - Implement fallback mechanisms for undefined namespaces
   - Improve document properties extraction (viewBox, width, height)
   - Add proper unit conversion support

2. **Enhance Path Processing**:
   - Implement all SVG path commands (M, L, H, V, C, S, Q, T, A, Z)
   - Add support for relative and absolute coordinates
   - Implement adaptive segmentation for Bezier curves based on curvature
   - Add proper arc command (A) handling with elliptical arc approximation

3. **Fix Coordinate System Transformation**:
   - Add support for SVG coordinate system (origin at top-left)
   - Implement mapping from SVG space to machine space
   - Handle viewBox transformations correctly
   - Support different unit systems and conversions

4. **Improve G-code Generation**:
   - Research optimal G-code commands for Duet 2 WiFi
   - Implement channel separation based on fill/stroke colors
   - Add support for varying opacity levels to control airbrush pressure
   - Add proper formatting and comments in G-code output

5. **Create Test SVGs and Validation Tools**:
   - Create test SVGs with various path types (lines, curves, arcs)
   - Implement G-code visualization for preview
   - Add debug visualization options to show path approximations

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
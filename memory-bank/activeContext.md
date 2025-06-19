# Active Context

## Current Focus
We are currently working on the SVG handling and G-code generation components of the hairbrush extension for Inkscape. This is part of Stage 1 (Environment Setup and Research) and Stage 4 (Inkscape Extension Development) of our implementation plan.

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

## Current Issues
- **Path Distortion**: G-code visualization shows that SVG paths are being simplified and distorted during conversion
- **Curve Handling**: Complex curves (especially Bezier paths) aren't being properly approximated
- **Segmentation**: Need to break curves into smaller linear segments for better approximation

## Next Steps
1. Improve curve resolution in the `path_to_polyline` method
2. Implement adaptive segmentation for Bezier curves and arcs
3. Ensure proper scaling between SVG and G-code coordinates
4. Add better debugging output to help diagnose conversion issues
5. Integrate improved path processing into the Inkscape extension

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
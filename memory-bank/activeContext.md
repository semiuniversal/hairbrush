# Active Context

## Current Focus
We are currently focused on researching and implementing the Inkscape extension component of the dual-airbrush plotter software. This is part of Stage 1 (Environment Setup and Research) and beginning work on Stage 4 (Inkscape Extension Development) of our implementation plan.

## Recent Progress
- Completed research on Inkscape extension development, with a focus on understanding the extension architecture, INX file structure, and Python implementation patterns
- Updated research_notes.md with detailed information about Inkscape extension development
- Enhanced the existing dual_airbrush_export.inx file with a more sophisticated UI using tabs and additional parameters
- Improved the dual_airbrush_export.py implementation to properly handle the new parameters and integrate with the hairbrush library
- Enhanced the GCodeGenerator class to properly parse and process SVG path data into G-code commands
- Studied the AxiDraw extension as a reference implementation for our project

## Current Challenges
- Need to implement proper SVG path parsing and transformation for complex paths
- Need to test the extension with actual SVG files to verify functionality
- Need to ensure proper integration between the Inkscape extension and the core hairbrush library
- Need to complete research on Duet 2 WiFi G-code command structure

## Next Actions
1. Install required dependencies (PyYAML, lxml) using uv
2. Make initial git commit to preserve current progress
3. Complete research on Duet 2 WiFi G-code command structure
4. Create test SVG files with different layer configurations
5. Test the Inkscape extension with sample SVG files
6. Refine the SVG path parsing logic to handle more complex paths
7. Implement proper error handling and validation in the extension

## Dependencies
- Inkscape 1.0+ for testing the extension
- Python 3.x with lxml and PyYAML packages
- WSL environment for development and testing

## Notes
- The current extension implementation is based on the AxiDraw extension architecture
- We are focusing on a layer-based approach where different brushes are assigned to different layers
- The extension currently supports basic path commands (M, L, H, V, Z) with simplified handling of curves
- Future work will include more sophisticated curve handling and optimization

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

## Open Questions
- What is the current state of the hardware (dual-airbrush CoreXY plotter)?
- Are there any existing G-code examples or templates to reference?
- What are the specific requirements for the Inkscape extension UI?
- Are there any specific performance constraints for the G-code generation?
- What specific Linux distribution is being used in WSL? (Answered: Ubuntu 22.04.5 LTS)
- Are there any preferences for project structure or naming conventions?
- Who will be participating in user testing in Stage 6?

## Current Challenges
- Understanding the specific G-code commands required by the Duet 2 WiFi board
- Determining the best approach for parsing SVG paths and handling transformations
- Planning for future extensibility while keeping the initial implementation focused
- Ensuring the system is intuitive for artists without G-code knowledge

## Next Steps
- Install basic dependencies (PyYAML, lxml) using uv
- Make initial git commit
- Research Inkscape extension development
- Research Duet 2 WiFi G-code command structure
- Update research_notes.md with findings

## Revised Implementation Plan Overview
1. **Stage 1**: Environment Setup and Research (2-3 days) - In Progress
2. **Stage 2**: Core Library Development (3-4 days)
3. **Stage 3**: G-code Generation Engine (3-4 days)
4. **Stage 4**: Inkscape Extension Development (3-4 days)
5. **Stage 5**: Integration and Testing (4-5 days)
6. **Stage 6**: Refinement and User Feedback (3-5 days)
7. **Stage 7**: Phase 2 Planning (2-3 days)

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Agents should ONLY PROPOSE commands for the user to run in WSL
- The user will execute all commands manually
- Use uv for virtual environment management
- Use pyproject.toml for dependency management 
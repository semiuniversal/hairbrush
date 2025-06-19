# Active Context

## Current Focus
Completing Stage 1 (Environment Setup and Research) for the dual-airbrush plotter software. Environment setup is largely complete, now focusing on research and dependency installation.

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
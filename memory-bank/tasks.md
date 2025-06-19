# Tasks

## Active Tasks
### Stage 1: Environment Setup and Research
- [x] Set up WSL development environment
  - [x] Verify WSL installation and Linux distribution
  - [x] Install uv for Python virtual environment management
  - [x] Create project directory structure in WSL
- [x] Configure Python environment
  - [x] Set up Python 3.x in WSL
  - [x] Create pyproject.toml for dependency management
  - [x] Initialize uv virtual environment
  - [ ] Install basic dependencies (PyYAML, etc.)
- [x] Set up version control
  - [x] Initialize git repository
  - [x] Create .gitignore file
  - [ ] Make initial commit
- [ ] Research key technologies
  - [ ] Research Inkscape extension development
  - [ ] Research Duet 2 WiFi G-code command structure
  - [x] Document findings for future reference
- [x] Document environment setup process
  - [x] Create README.md with setup instructions
  - [x] Document WSL-specific considerations

## Next Steps
- [ ] Install basic dependencies (PyYAML, lxml) using uv
- [ ] Make initial git commit
- [ ] Research Inkscape extension development
- [ ] Research Duet 2 WiFi G-code command structure
- [ ] Update research_notes.md with findings

## Backlog
### Stage 2: Core Library Development
- [ ] Design YAML schema for command templates
- [ ] Create command template parser and validator
- [ ] Implement template validation
- [ ] Create sample templates for Duet 2 WiFi board
- [ ] Create utilities for parsing SVG files
- [ ] Implement path extraction from layers
- [ ] Handle path transformations
- [ ] Write unit tests for core libraries
- [ ] Document core library functionality

### Stage 3: G-code Generation Engine
- [ ] Create G-code generator class
- [ ] Implement path to G-code conversion
- [ ] Add brush control command support
- [ ] Implement brush offset handling
- [ ] Create output formatting and file writing
- [ ] Create functions to convert SVG paths to plotter movements
- [ ] Write unit tests for G-code generation
- [ ] Document G-code generation process

### Stage 4: Inkscape Extension Development
- [ ] Create .inx file for extension
- [ ] Implement extension UI with parameter inputs
- [ ] Connect UI to G-code generator
- [ ] Handle parameter validation and errors
- [ ] Implement file output selection
- [ ] Create proof-of-concept with simple SVG files
- [ ] Write extension documentation
- [ ] Create basic user guide

### Stage 5: Integration and Testing
- [ ] Integrate all components
- [ ] Create end-to-end tests
- [ ] Implement error handling and logging
- [ ] Optimize performance for large SVG files
- [ ] Create sample SVG files for testing
- [ ] Test with complex real-world examples
- [ ] Document integrated system
- [ ] Create comprehensive installation instructions

### Stage 6: Refinement and User Feedback
- [ ] Conduct user testing with artists
- [ ] Collect and analyze feedback
- [ ] Implement high-priority improvements
- [ ] Enhance documentation based on user questions
- [ ] Create additional examples and tutorials
- [ ] Optimize performance bottlenecks
- [ ] Implement usability improvements

### Stage 7: Phase 2 Planning (Optional Components)
- [ ] Evaluate Telnet Controller requirements
- [ ] Assess Calibration & Manual Mode GUI needs
- [ ] Create specifications for optional components
- [ ] Prioritize optional features based on user feedback
- [ ] Update implementation plan
- [ ] Create proof-of-concept for highest priority component

## Blocked
- None currently

## Completed
- [x] Set up memory bank structure - Completed: [Current date]
- [x] Create implementation plan - Completed: [Current date]
- [x] Review and revise implementation plan - Completed: [Current date]
- [x] Set up development environment - Completed: [Current date]
- [x] Create test directory structure - Completed: [Current date]
- [x] Create sample SVG for testing - Completed: [Current date]
- [x] Set up basic test files - Completed: [Current date]

## Notes
- Focus on completing Stage 1 before moving to other stages
- Stage 2 consolidates the core library development for both template parsing and SVG processing
- Stage 4 (Inkscape Extension) can begin after Stage 1 research is complete
- User testing in Stage 6 is critical for ensuring the tool meets artist needs
- ⚠️ CRITICAL: All command-line operations MUST be executed in WSL, NOT in Windows
- Agents should ONLY PROPOSE commands for the user to run in WSL
- Use uv for virtual environment management and pyproject.toml for dependencies 
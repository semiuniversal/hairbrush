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
  - [x] Install basic dependencies (PyYAML, etc.)
- [x] Set up version control
  - [x] Initialize git repository
  - [x] Create .gitignore file
  - [ ] Make initial commit
- [x] Research key technologies
  - [x] Research Inkscape extension development
    - [x] Study AxiDraw extension as reference
    - [x] Understand inkex module and dependency handling
    - [x] Document proper extension installation approach
  - [ ] Research Duet 2 WiFi G-code command structure
  - [x] Document findings for future reference
- [x] Document environment setup and project structure
  - [x] Create README.md with setup instructions
  - [x] Document extension installation process

### Stage 2: Core Library Development
- [x] Create basic project structure
  - [x] Set up src/hairbrush package
  - [x] Create module files
- [x] Implement SVG parsing module
  - [x] Create SVG parser class
  - [x] Implement layer extraction
  - [x] Implement path data extraction
- [x] Implement G-code generation module
  - [x] Create G-code generator class
  - [x] Implement template-based commands
  - [x] Add path to G-code conversion
- [x] Create configuration module
  - [x] Implement YAML configuration loading
  - [x] Create default settings

### Stage 3: G-code Generation Engine
- [ ] Implement advanced path processing
  - [ ] Add path simplification
  - [ ] Add path optimization
  - [ ] Implement travel moves
- [ ] Create G-code templates for Duet 2 WiFi
  - [ ] Research specific G-code commands
  - [ ] Create template structure
  - [ ] Implement template substitution

### Stage 4: Inkscape Extension Development
- [x] Create basic extension structure
  - [x] Create .inx file with UI definition
  - [x] Create Python implementation file
- [x] Implement extension functionality
  - [x] Add layer selection
  - [x] Add export options
  - [x] Connect to core library
- [x] Handle extension dependencies
  - [x] Update pyproject.toml for proper dependency management
  - [x] Create installation instructions
  - [x] Document cross-platform compatibility
- [x] Create installation tools
  - [x] Create standalone installation script
  - [x] Create Python package installation script
  - [x] Add CLI command for installation

### Stage 5: Integration and Testing
- [ ] Create test SVG files
  - [ ] Simple shapes
  - [ ] Complex paths
  - [ ] Multi-layer designs
- [ ] Implement testing framework
  - [ ] Unit tests for core modules
  - [ ] Integration tests
  - [ ] Test on different platforms
- [ ] Create user documentation
  - [ ] Installation guide
  - [ ] Usage instructions
  - [ ] Examples

### Stage 6: Refinement and User Feedback
- [ ] Optimize performance
- [ ] Enhance error handling
- [ ] Improve user interface
- [ ] Address user feedback

### Stage 7: Phase 2 Planning
- [ ] Identify advanced features for Phase 2
- [ ] Create roadmap for future development
- [ ] Document API for potential extensions

## Completed Tasks
- [x] Set up development environment with uv and pyproject.toml
- [x] Create basic project structure with src/hairbrush package
- [x] Implement SVG parsing with layer detection
- [x] Create G-code generator with basic path handling
- [x] Implement command templates for brush control
- [x] Enhance SVG parser with document properties extraction
- [x] Implement path analysis and bounding box calculation
- [x] Create path processing with support for different path commands
- [x] Implement path simplification using Ramer-Douglas-Peucker algorithm
- [x] Create SVG analysis tools for examining file structure and paths
- [x] Implement G-code generation from SVG paths with configurable parameters
- [x] Create standalone scripts for SVG analysis and G-code conversion

## Next Steps
1. Research Duet 2 WiFi G-code command structure
2. Create test SVG files for validating the extension functionality
3. Implement advanced path processing features
4. Test the extension installation process on different platforms

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
- [x] Research Inkscape extension development - Completed: [Current date]
- [x] Update research_notes.md with Inkscape extension findings - Completed: [Current date]
- [x] Enhance Inkscape extension structure based on AxiDraw reference - Completed: [Current date]
- [x] Improve SVG path parsing and G-code generation - Completed: [Current date]
- [x] Create implementation plan for fixing extension not showing in Inkscape - Completed: [Current date]
- [x] Create diagnostic tools for extension troubleshooting - Completed: [Current date]
- [x] Update documentation with clear installation instructions - Completed: [Current date]

## Notes
- Focus on completing Stage 1 before moving to other stages
- Stage 2 consolidates the core library development for both template parsing and SVG processing
- Stage 4 (Inkscape Extension) can begin after Stage 1 research is complete
- User testing in Stage 6 is critical for ensuring the tool meets artist needs
- ⚠️ CRITICAL: All command-line operations MUST be executed in WSL, NOT in Windows
- Agents should ONLY PROPOSE commands for the user to run in WSL
- Use uv for virtual environment management and pyproject.toml for dependencies

## Current Tasks

### High Priority
- [x] Redesign Inkscape extension structure:
  - [x] Create simplified extension structure based on AxiDraw model
  - [x] Create comprehensive implementation plan
  - [x] Update documentation with clear installation instructions
  - [x] Implement diagnostic tools for troubleshooting

- [x] Implement improved Inkscape extension:
  - [x] Create main hairbrush_control.py implementation
  - [x] Create core hairbrush.py module
  - [x] Ensure proper module imports and error handling
  - [x] Implement extension UI with multiple tabs and options

- [x] Improve SVG parsing based on AxiDraw analysis:
  - [x] Enhance namespace handling for Inkscape SVGs
  - [x] Implement fallback mechanisms for undefined namespaces
  - [x] Improve document properties extraction (viewBox, width, height)
  - [x] Add support for all SVG path commands

- [x] Implement path processing:
  - [x] Create path processor module with support for all path commands
  - [x] Implement path simplification algorithms
  - [x] Add support for converting paths to points
  - [x] Implement G-code generation for dual-airbrush system

- [x] Create installation script:
  - [x] Implement robust installation script for Windows
  - [x] Add automatic detection of Inkscape extensions directory
  - [x] Add proper error handling and user feedback
  - [x] Support copying all required directories and files

### Medium Priority
- [ ] Test the extension:
  - [ ] Test installation on Windows Inkscape
  - [ ] Verify extension appears in Inkscape UI
  - [ ] Test SVG to G-code conversion
  - [ ] Test with different SVG files and path types

- [ ] Create documentation:
  - [ ] Write comprehensive user guide
  - [ ] Document installation process
  - [ ] Add examples of usage
  - [ ] Create troubleshooting guide

- [ ] Implement additional features:
  - [ ] Add preview functionality
  - [ ] Implement custom brush configurations
  - [ ] Add advanced path optimization
  - [ ] Implement G-code visualization

### Low Priority
- [ ] Create example SVG files:
  - [ ] Create simple test patterns
  - [ ] Create complex artwork examples
  - [ ] Create calibration patterns
  - [ ] Create documentation examples
  - [ ] Optimize performance for large SVG files
  - [ ] Add support for more SVG features (text, images, etc.)
  - [ ] Implement advanced color separation techniques
  - [ ] Add boundary and clipping support 
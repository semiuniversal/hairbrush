# Tasks

## Active Tasks

### Component 1: Inkscape Extension
- [x] Create extension structure based on AxiDraw model
  - [x] Create `hairbrush.inx` file with UI definition
  - [x] Create `hairbrush_control.py` as main entry point
  - [x] Implement `hairbrush.py` core module
  - [x] Create `hairbrush_lib` package with processing modules
- [x] Implement extension functionality
  - [x] Add SVG parsing with layer detection
  - [x] Create path processing with command support
  - [x] Implement G-code generation
  - [x] Add error handling and logging
- [x] Create installation tools
  - [x] Create installation script for Windows
  - [x] Add automatic detection of Inkscape extensions directory
  - [x] Create diagnostic tool for troubleshooting
- [x] Fix G-code generation issues
  - [x] Fix critical issue with G-code output (no movement commands)
  - [x] Simplify G-code output for better readability
  - [x] Fix slanted drawing issues with proper X-Y plane alignment
  - [x] Create documentation for implementation approach
- [ ] GitHub repository setup
  - [ ] Create a new GitHub repository
  - [ ] Push the working code to GitHub
  - [ ] Create README and documentation
  - [ ] Add example SVG files for testing
- [ ] Testing and documentation
  - [ ] Test with real hardware
  - [ ] Create example SVG files for testing
  - [ ] Update user guide with latest changes

### Component 2: Web Controller
- [x] Define architecture and component structure
  - [x] Plan Flask web server implementation
  - [x] Define communication protocols with Duet
  - [x] Design UI templates structure
- [ ] Implement core functionality
  - [ ] Create Flask web server
  - [ ] Implement Duet communication client
  - [ ] Create job management system
  - [ ] Develop basic web UI

### Component 3: Duet 2 WiFi Integration
- [x] Define communication protocols
  - [x] Document Telnet interface for G-code streaming
  - [x] Document HTTP API for status monitoring
  - [x] Plan WebSocket implementation for real-time updates
- [x] Implement G-code command structure
  - [x] Create command templates for brush control
  - [x] Implement brush offset handling
  - [x] Add support for Z-axis performance considerations
- [ ] Hardware testing and calibration
  - [ ] Test with real hardware
  - [ ] Calibrate brush parameters for optimal performance
  - [ ] Measure and document Z vs X/Y performance characteristics

## Next Steps
1. Create a GitHub repository and push the working code
2. Update user guide with latest changes
3. Begin Web Controller implementation
4. Implement G-code streaming via Telnet

## Completed Tasks
- [x] Set up development environment with uv and pyproject.toml
- [x] Create modular architecture following AxiDraw model
- [x] Implement SVG parsing with layer detection
- [x] Create G-code generator with path handling
- [x] Create diagnostic tools for extension troubleshooting
- [x] Define three-component system architecture
- [x] Document communication protocols between components
- [x] Fix critical issue with G-code generation (no movement commands)
- [x] Simplify G-code output for better readability
- [x] Fix slanted drawing issues with proper X-Y plane alignment

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Use uv for virtual environment management
- Use pyproject.toml for dependency management
- Follow minimalist approach to dependencies 
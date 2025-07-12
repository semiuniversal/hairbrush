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
  - [x] Implement hybrid approach with M400 commands for motion synchronization
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
- [x] Set up project structure
  - [x] Create web_controller directory structure
  - [x] Set up Flask application skeleton
  - [x] Configure static and template directories
  - [x] Set up WebSocket support
- [x] Implement Duet communication client
  - [x] Create HTTP client for G-code commands and status monitoring
  - [x] Add WebSocket client for real-time updates
  - [x] Implement error handling and reconnection logic
  - [x] Add send_command_and_wait and wait_for_motion_complete methods
  - [x] Implement get_position method using M114
  - [x] Implement endstop monitoring using M119
- [x] Develop job management system
  - [x] Create G-code file upload and storage
  - [x] Implement job queue management
  - [x] Add job status tracking and reporting
  - [x] Implement job control (start, pause, stop)
- [x] Create machine control interface
  - [x] Implement manual jog controls
  - [x] Add brush control commands
  - [x] Create maintenance routines (parking, cleaning)
  - [x] Implement emergency stop functionality
  - [x] Add G-code file processing with M400 synchronization awareness
  - [x] Add endstop monitoring with real-time status display
  - [x] Optimize machine control layout for better usability
  - [x] Fix JavaScript errors and improve error handling
  - [x] Implement calibrated paint flow control with min/max servo angle settings
- [x] Develop web UI
  - [x] Create responsive dashboard layout
  - [x] Implement G-code visualization
  - [x] Add real-time status display
  - [x] Create file management interface
  - [x] Implement settings and configuration page
  - [x] Add endstop status monitoring section
  - [x] Improve position display and control layout
  - [x] Replace DOM/CSS visualization with Canvas implementation
  - [x] Add scale indicators to visualization
  - [x] Implement settings persistence to config.yaml
  - [x] Connect settings changes to visualization updates
  - [x] Implement global WebSocket manager for persistent connections across tabs
  - [x] Create settings.js to handle loading and saving settings
  - [x] Add API endpoints for getting and setting configuration
  - [x] Implement setup page with IP address discovery
  - [x] Add diagnostic command menu to setup page
- [ ] Testing and optimization
  - [ ] Test with real hardware
  - [x] Optimize performance for real-time control
  - [x] Implement error recovery mechanisms
  - [x] Add comprehensive logging
  - [x] Fix endstop monitoring parsing for Z probe information
  - [x] Fix WebSocket connection reliability issues
  - [x] Improve settings persistence reliability
  - [x] Fix tab-switching disconnection issues
  - [x] Implement JavaScript testing framework with Vitest
  - [ ] Test endstop monitoring and homing procedures
- [ ] Documentation and deployment
  - [x] Create endstop monitoring documentation
  - [ ] Create user guide for web controller
  - [ ] Document API endpoints
  - [ ] Create deployment instructions
  - [ ] Add configuration examples

### Component 3: Duet 2 WiFi Integration
- [x] Define communication protocols
  - [x] Document HTTP API for G-code commands and status monitoring
  - [x] Plan WebSocket implementation for real-time updates
  - [x] Document endstop configuration and monitoring
- [x] Implement G-code command structure
  - [x] Create command templates for brush control
  - [x] Implement brush offset handling
  - [x] Add support for Z-axis performance considerations
  - [x] Implement hybrid approach for motion synchronization
  - [x] Add M119 support for endstop monitoring
- [ ] Hardware testing and calibration
  - [ ] Test with real hardware
  - [ ] Calibrate brush parameters for optimal performance
  - [ ] Measure and document Z vs X/Y performance characteristics
  - [ ] Verify endstop functionality and homing procedures
- [ ] Integration testing
  - [ ] Test end-to-end workflow from Inkscape to hardware
  - [ ] Verify brush control commands
  - [ ] Document hardware-specific considerations
  - [ ] Test endstop monitoring during operation

## Next Steps
1. Integrate refactored JavaScript modules into the main application
2. Remove static HTML test files (completed)
3. Test with real hardware
4. Create comprehensive documentation
5. Prepare for GitHub repository setup and public release

## JavaScript Architecture Refactoring

### Completed
- [x] Create core modules with clear separation of concerns
  - [x] Create machine-state.js for centralized state management
  - [x] Create command-engine.js for hardware command abstraction
  - [x] Create websocket-client.js for standardized communication
  - [x] Create error-handler.js for standardized error handling
- [x] Create UI components
  - [x] Create brush-control.js for brush-specific functionality
  - [x] Create movement-control.js for jog and positioning controls
  - [x] Create visualization.js for machine visualization
- [x] Implement automated testing with Vitest
  - [x] Set up Vitest with JSDOM for browser environment simulation
  - [x] Create tests for core modules (~84% coverage)
  - [x] Create tests for UI components (~100% coverage)
  - [x] Add test coverage reporting

### In Progress
- [ ] Create app.js as main application entry point
- [ ] Integrate refactored modules into main application
- [ ] Create settings-manager.js for configuration management
- [ ] Implement proper dependency injection between modules
- [ ] Replace global state with MachineState module
- [ ] Replace direct WebSocket usage with WebSocketClient

### To Do
- [ ] Implement proper module interfaces
  - [ ] Define clear APIs between modules
  - [ ] Use event-based communication between modules
  - [ ] Implement proper initialization order
  - [ ] Add module lifecycle management (init/destroy)
- [ ] Standardize UI component management
  - [ ] Create component factory for consistent creation
  - [ ] Implement component registration system
  - [ ] Add UI state synchronization with machine state
  - [ ] Create consistent event handling across components
- [ ] Improve error handling and user feedback
  - [ ] Implement error boundaries for components
  - [ ] Create standardized error display system
  - [ ] Implement graceful degradation for failures
- [ ] Optimize performance and resource usage
  - [ ] Implement proper cleanup for event listeners
  - [ ] Use requestAnimationFrame for animations
  - [ ] Batch DOM updates to reduce layout thrashing
  - [ ] Optimize WebSocket message handling
- [ ] Eliminate global variable dependencies
  - [ ] Reduce coupling between components
  - [ ] Consolidate duplicate event listeners and DOM setup
  - [ ] Create consistent initialization sequence

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Use uv for virtual environment management
- Use pyproject.toml for dependency management
- Follow minimalist approach to dependencies 
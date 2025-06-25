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
1. Complete testing and optimization of the web controller
2. Create comprehensive documentation for the web controller
3. Perform integration testing with real hardware
4. Prepare for GitHub repository setup and public release

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
- [x] Implement Flask application structure with WebSocket support
- [x] Create Duet client for HTTP API communication
- [x] Implement job management system for G-code file handling
- [x] Create machine control interface for manual operation
- [x] Develop web UI with dashboard, control, and file management pages
- [x] Implement hybrid approach for motion synchronization with M400 commands
- [x] Add G-code file processing with M400 synchronization awareness
- [x] Enhance Duet client with motion completion and position querying methods
- [x] Migrate from Telnet to HTTP API for Duet communication
- [x] Implement endstop monitoring using M119 command
- [x] Add real-time endstop status display to machine control page
- [x] Create documentation for endstop monitoring feature
- [x] Improve machine control interface layout for better usability
- [x] Fix JavaScript errors related to duplicate socket declaration
- [x] Add missing helper functions for movement control
- [x] Fix Z endstop status parsing to handle RepRapFirmware's Z probe information
- [x] Update endstop monitoring documentation with Z probe information
- [x] Fix endstop status indicator blinking during polling
- [x] Fix "removeChild" error in command history
- [x] Enhance command history with support for 100 entries
- [x] Add command count badge and clear history button
- [x] Fix jog controls to respect selected distance and speed settings
- [x] Add Enable Motors button as toggle counterpart to Disable Motors
- [x] Convert brush control buttons to toggle style for better state indication
- [x] Add paint intensity sliders with percentage control for precise paint flow adjustment
- [x] Improve paint control layout with full-width buttons and sliders below
- [x] Disable jog and home buttons when motors are disabled
- [x] Replace DOM/CSS visualization with Canvas implementation
- [x] Add scale indicators to visualization with proper origin at center
- [x] Add position and brush offset text display to visualization
- [x] Implement settings persistence to config.yaml
- [x] Connect settings changes to visualization updates
- [x] Create settings.js to handle loading and saving settings
- [x] Add API endpoints for getting and setting configuration
- [x] Fix "DuetClient object has no attribute 'is_homed'" error by implementing the missing method
- [x] Add error handling for machine status requests in both client and server code
- [x] Improve JavaScript status notification with safe default values
- [x] Remove Telnet port settings from UI and config.yaml (no longer needed with RepRap firmware)
- [x] Implement calibrated paint flow control with min/max servo angle settings for each brush
- [x] Add test buttons for min/max paint flow settings with real-time feedback
- [x] Implement percentage-to-servo-angle scaling for intuitive user control
- [x] Add safety features to reset servos to minimum position when saving settings
- [x] Fix USB serial connection for device discovery
- [x] Add reliable IP address detection via serial communication
- [x] Implement background thread for capturing IP address from serial data
- [x] Add hierarchical diagnostic command menu with commands from YAML file
- [x] Fix connection history management and persistence
- [x] Add automatic disconnection when leaving or reloading the page
- [x] Improve error handling for serial communication
- [x] Fix "Already connected" errors with proper resource management

## Future Improvements

### JavaScript Architecture Refactoring
- [ ] Eliminate global variable dependencies and improve module structure
  - [ ] Implement proper dependency injection
  - [ ] Create a module pattern for key components
  - [ ] Reduce coupling between components
- [ ] Consolidate duplicate event listeners and DOM setup
  - [ ] Merge overlapping DOMContentLoaded event listeners
  - [ ] Standardize command sending logic
  - [ ] Create consistent initialization sequence
- [ ] Implement proper error boundaries and state management
  - [ ] Centralize state tracking (brush states, motor states)
  - [ ] Implement consistent error handling patterns
  - [ ] Improve UI state synchronization
- [ ] Extract magic numbers and improve configuration management
  - [ ] Create central configuration object for timeouts and intervals
  - [ ] Move grid spacing and visualization parameters to config
  - [ ] Make delay values configurable
- [ ] Optimize DOM manipulation and reduce layout thrashing
  - [ ] Batch DOM style changes
  - [ ] Optimize endstop update logic
  - [ ] Implement requestAnimationFrame for animations

### Connection Handling Improvements
- [ ] Implement proper IP address validation
- [ ] Add cleanup for unmanaged event listeners and timeouts
- [ ] Create a ConnectionManager class with proper dependency injection

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Use uv for virtual environment management
- Use pyproject.toml for dependency management
- Follow minimalist approach to dependencies 
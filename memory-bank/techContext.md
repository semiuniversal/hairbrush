# Technical Context

## Development Environment
- **Operating System**: Windows 11 with WSL (Ubuntu)
- **Python**: 3.10+
- **Package Management**: uv with pyproject.toml
- **Version Control**: Git
- **JavaScript Testing**: Vitest with JSDOM

## Technology Stack

### Inkscape Extension
- **Language**: Python 3.10+
- **Dependencies**: 
  - inkex (Inkscape extension library)
  - lxml (XML processing)
  - numpy (numerical operations)

### Web Controller
- **Backend**: 
  - Flask (web framework)
  - Flask-SocketIO (WebSocket support)
  - PyYAML (configuration management)
  - pyserial (serial communication)
- **Frontend**: 
  - HTML5/CSS3/JavaScript
  - Bootstrap 5 (UI framework)
  - Socket.IO (WebSocket client)
  - HTML5 Canvas (visualization)
- **Testing**:
  - Vitest (JavaScript testing framework)
  - JSDOM (DOM simulation)
  - vi.mock() (mocking utilities)

### Duet 2 WiFi Controller
- **Communication**: HTTP API
- **G-code**: RepRapFirmware compatible
- **Synchronization**: M400 commands

## Core Architecture Components

### Machine State Module
The machine-state.js module provides centralized state management:
- Singleton MachineState class with observable pattern
- Methods for getting and updating machine position, brush states, and motor states
- Validation for all state changes
- Event-based subscription system for state changes
- Support for filtered listeners to monitor specific state changes
- Batch updates for efficient state synchronization
- Comprehensive error handling for state operations

### Command Engine Module
The command-engine.js module abstracts hardware commands:
- CommandEngine class for high-level command abstraction
- Methods for movement, brush control, and motor operations
- Command validation and proper error handling
- Integration with MachineState for state updates after command execution
- Servo angle calculation for paint flow control
- Command queue tracking for pending commands

### WebSocket Client Module
The websocket-client.js module provides standardized communication:
- WebSocketClient class with robust connection management
- Automatic reconnection with configurable retry parameters
- Message queuing for offline scenarios
- Standardized message format and error handling
- Event-based communication system for WebSocket events
- Integration with MachineState for state updates from server
- Support for different message types (commands, events)
- Timeout handling for requests

### Utilities Module
The utils.js module provides common utility functions:
- Debounce function for rate-limiting operations
- Number formatting with configurable precision
- Servo angle calculation for brush control
- Command response parsing
- Range validation and clamping functions
- Unique ID generation

## Testing Framework

### JavaScript Testing
- **Framework**: Vitest with JSDOM for browser environment simulation
- **Test Organization**: Tests located alongside implementation files
- **Coverage**: ~84% for core modules, ~100% for components
- **Mocking**: vi.mock() for dependencies, custom DOM element mocking
- **Test Types**:
  - Unit tests for core modules and components
  - Integration tests for component interactions
  - DOM event simulation and handler testing

### Test Commands
- `npm test` - Run tests in watch mode
- `npm run test:run` - Run tests once
- `npm run test:coverage` - Run tests with coverage reporting
- `npm run test:ui` - Run tests with UI interface

## Communication Protocols

### HTTP API (Duet 2 WiFi)
- **Base URL**: http://{duet_ip}/
- **G-code Endpoint**: /rr_gcode?gcode={command}
- **Status Endpoint**: /rr_status?type=3
- **Response Endpoint**: /rr_reply

### WebSocket (Browser to Server)
- **URL**: ws://{server_ip}:{port}/ws
- **Events**:
  - connect: Connection established
  - disconnect: Connection closed
  - status: Machine status update
  - command: G-code command execution
  - job: Job status update

## G-code Implementation
- **Movement**: G0/G1 commands for positioning
- **Brush Control**: Custom M commands for brush operations
- **Synchronization**: M400 for motion completion
- **Position Query**: M114 for position reporting
- **Endstop Query**: M119 for endstop status

## Development Patterns

### JavaScript Architecture
- **Module Pattern**: Self-contained modules with clear responsibilities
- **Singleton Pattern**: Single instances for state and communication
- **Observer Pattern**: Event-based communication between components
- **Factory Pattern**: Standardized creation of UI components
- **Command Pattern**: Abstraction of hardware commands
- **Promise-based API**: Asynchronous operations with proper error handling

### Python Architecture
- **Class-based Design**: Object-oriented approach with clear responsibilities
- **Dependency Injection**: Explicit dependencies for better testability
- **Configuration Management**: External configuration with YAML
- **Error Handling**: Comprehensive error handling with proper logging

## ⚠️ CRITICAL DEVELOPMENT REQUIREMENTS ⚠️
- All command-line operations MUST be executed in WSL, NOT in Windows
- Use uv for virtual environment management instead of venv/virtualenv
- Use pyproject.toml for dependency management instead of requirements.txt
- Follow minimalist approach to dependencies 
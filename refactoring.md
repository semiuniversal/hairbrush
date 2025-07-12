# H.Airbrush Web Controller Refactoring Plan

## Overview

This document outlines a comprehensive refactoring plan for the H.Airbrush Web Controller application. The goal is to improve modularity, reliability, and maintainability while preserving functionality.

## Current Status (Updated July 15, 2024)

### Completed
- ✅ Core Architecture Implementation
  - Implemented machine-state.js for centralized state management
  - Implemented command-engine.js for hardware command abstraction
  - Implemented websocket-client.js for standardized communication
  - Implemented error-handler.js for standardized error handling
- ✅ UI Component Implementation
  - Implemented brush-control.js for brush-specific functionality
  - Implemented movement-control.js for jog and positioning controls
  - Implemented visualization.js for machine visualization
- ✅ Automated Testing
  - Set up Vitest with JSDOM for browser environment simulation
  - Created tests for core modules (~84% coverage)
  - Created tests for UI components (~100% coverage)
  - Added test coverage reporting

### In Progress
- 🔄 Integration into Main Application
  - Need to create app.js as main application entry point
  - Need to integrate refactored modules into main application
  - Need to replace global state with MachineState module
  - Need to replace direct WebSocket usage with WebSocketClient

### Not Started
- ❌ Command History Component
- ❌ Settings Manager Module
- ❌ Proper Dependency Injection
- ❌ Component Registration System
- ❌ Error Boundaries for Components

### Removed
- 🗑️ Static HTML Test Files
  - Removed standalone test pages (machine-state-test.html, command-engine-test.html, etc.)
  - Decided to rely on automated Vitest tests instead of manual test pages
  - Will use the real application UI for integration testing

## Current Issues

After analyzing the codebase, we've identified several architectural issues:

1. **Excessive Global State and Variable Pollution**
   - Numerous global variables scattered across files
   - Window object pollution with application state
   - Inconsistent state management approaches

2. **Massive Function Complexity**
   - Functions like `setupEventListeners()` (400+ lines) and `onMachineStatusUpdate()` (200+ lines)
   - Monolithic control.js file (2289 lines)
   - Violation of Single Responsibility Principle

3. **Inconsistent Communication Patterns**
   - Mix of direct socket usage and HairbrushWebSocket wrapper
   - Duplicate socket event listeners
   - Inconsistent error handling for communication

4. **Duplicate Code and Logic Repetition**
   - Significant duplication between Brush A and Brush B handling code
   - Repeated patterns for similar operations
   - Multiple implementations of the same functionality

5. **Memory Leaks and Resource Management**
   - Intervals and event listeners without proper cleanup
   - Potential for multiple intervals to be created
   - Inconsistent resource management

## Implemented Architecture

```
web_controller/static/js/
├── core/
│   ├── machine-state.js     # Centralized state management ✅
│   ├── command-engine.js    # Hardware command abstraction ✅
│   ├── websocket-client.js  # Communication layer ✅
│   └── error-handler.js     # Standardized error handling ✅
├── components/
│   ├── brush-control.js     # Brush-specific UI and logic ✅
│   ├── movement-control.js  # Movement and positioning controls ✅
│   ├── visualization.js     # Machine visualization ✅
│   └── command-history.js   # Command history management ❌
├── utils/
│   ├── event-manager.js     # Event handling utilities ✅
│   ├── dom-utils.js         # DOM manipulation helpers ❌
│   └── config-manager.js    # Configuration management ❌
└── app.js                   # Main application entry point ❌
```

## Decision to Remove Static HTML Test Files

After evaluating the static HTML test files (machine-state-test.html, command-engine-test.html, etc.), we decided to remove them for the following reasons:

1. **Redundancy with Automated Tests**: The Vitest automated tests provide better coverage and verification than manual test pages.

2. **Maintenance Burden**: Maintaining separate test pages for each module created additional work without proportional benefit.

3. **Integration Testing Challenges**: The isolated test pages didn't properly test how components work together in the real application.

4. **Issues with Test Implementation**: Some test pages had implementation issues, such as incorrect event filtering in the WebSocketClient test page.

5. **Confusion for Developers**: The presence of both automated tests and manual test pages created confusion about which testing approach to use.

Moving forward, we will rely on:
- Automated unit tests with Vitest for individual modules
- The real application UI for integration testing
- End-to-end testing with real hardware for final validation

## Refactoring Specifications

### 1. Core Architecture

#### User Story 1.1: Machine State Management ✅
**As a** developer  
**I want** a centralized state management system  
**So that** the application has a single source of truth for machine state

**Status**: Implemented

#### User Story 1.2: Command Abstraction ✅
**As a** developer  
**I want** an abstraction layer for hardware commands  
**So that** UI components don't need to know G-code details

**Status**: Implemented

#### User Story 1.3: Communication Layer ✅
**As a** developer  
**I want** a standardized communication layer  
**So that** WebSocket interactions are consistent and reliable

**Status**: Implemented

#### User Story 1.4: Error Handling System ✅
**As a** developer  
**I want** a standardized error handling system  
**So that** errors are handled consistently across the application

**Status**: Implemented

### 2. Component Refactoring

#### User Story 2.1: Brush Control Component ✅
**As a** user  
**I want** reliable brush controls  
**So that** I can control air and paint flow for each brush

**Status**: Implemented

#### User Story 2.2: Movement Control Component ✅
**As a** user  
**I want** reliable movement controls  
**So that** I can position the machine precisely

**Status**: Implemented

#### User Story 2.3: Visualization Component ✅
**As a** user  
**I want** an accurate machine visualization  
**So that** I can see the current position and brush states

**Status**: Implemented

#### User Story 2.4: Command History Component ❌
**As a** user  
**I want** a command history display  
**So that** I can see what commands have been sent and their results

**Status**: Not Started

### 3. Integration and Testing

#### User Story 3.1: Application Initialization ❌
**As a** developer  
**I want** a proper application initialization sequence  
**So that** components are created and connected in the correct order

**Status**: Not Started

#### User Story 3.2: Comprehensive Logging ✅
**As a** developer  
**I want** comprehensive logging throughout the application  
**So that** I can debug issues and monitor performance

**Status**: Implemented

#### User Story 3.3: Component Integration ❌
**As a** user  
**I want** all UI components to work together seamlessly  
**So that** I have a consistent and reliable experience

**Status**: Not Started

## Next Steps

1. **Create app.js Entry Point**
   - Implement proper initialization sequence
   - Set up dependency injection
   - Initialize core modules and UI components

2. **Integrate Modules into Main Application**
   - Replace global state with MachineState
   - Replace direct WebSocket usage with WebSocketClient
   - Replace direct DOM manipulation with components

3. **Test with Real Hardware**
   - Verify functionality with the Duet 2 WiFi board
   - Test endstop monitoring and homing procedures
   - Measure and document performance characteristics

4. **Complete Documentation**
   - Document API endpoints
   - Create user guide
   - Document deployment instructions 
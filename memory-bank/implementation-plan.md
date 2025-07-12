# Implementation Plan: JavaScript Architecture Refactoring

## Three-Component Architecture

Our implementation follows a three-component architecture:

1. **Inkscape Extension** - SVG processing and G-code generation (95% complete)
2. **Web Controller** - Machine control and monitoring interface (95% complete)
3. **Duet 2 WiFi Integration** - Hardware control and execution (20% complete)

## Current Focus: JavaScript Architecture Refactoring

The web controller JavaScript architecture needs refactoring to create a modular, maintainable system with clear separation of concerns.

## Core Principles

1. **Single Responsibility**: Each module has one clear responsibility
2. **Clean Interfaces**: Modules communicate through well-defined APIs
3. **State Centralization**: Machine state is managed in one place
4. **Event-Based Communication**: Components communicate via events
5. **Testability**: Code is structured to enable unit testing
6. **Progressive Implementation**: Refactoring happens incrementally

## Module Structure

### 1. machine-state.js (IMPLEMENTED)

**Responsibility**: State management and synchronization

- Singleton MachineState class with observable pattern
- Methods for getting and updating machine state
- Validation for all state changes
- Event-based subscription system
- Support for filtered listeners
- Batch updates for efficient state synchronization
- Comprehensive error handling

### 2. command-engine.js (IMPLEMENTED)

**Responsibility**: Command abstraction and execution

- CommandEngine class for high-level command abstraction
- Methods for movement, brush control, and motor operations
- Command validation and error handling
- Integration with MachineState for state updates
- Servo angle calculation for paint flow control
- Command queue tracking

### 3. websocket-client.js (IMPLEMENTED)

**Responsibility**: Communication with server

- WebSocketClient class with robust connection management
- Automatic reconnection with configurable retry parameters
- Message queuing for offline scenarios
- Standardized message format and error handling
- Event-based communication system
- Integration with MachineState for state updates

### 4. brush-controls.js (PLANNED)

**Responsibility**: Brush-specific functionality

- UI event listeners for brush controls
- Brush state management
- Paint flow control
- Integration with CommandEngine for execution

### 5. movement-controls.js (PLANNED)

**Responsibility**: Jog and positioning controls

- UI event listeners for movement controls
- Axis movement and homing
- Motor control
- Integration with CommandEngine for execution

### 6. visualization.js (PLANNED)

**Responsibility**: Machine visualization

- Canvas-based position visualization
- Grid and scale indicators
- Brush position display
- Position text display

### 7. settings-manager.js (PLANNED)

**Responsibility**: Configuration management

- Settings loading and saving
- Configuration validation
- UI synchronization with settings
- API communication for settings persistence

## Implementation Sequence

1. **Core Infrastructure** (COMPLETED)
   - ✅ Implement machine-state.js
   - ✅ Implement command-engine.js
   - ✅ Implement websocket-client.js

2. **UI Components** (COMPLETED)
   - ✅ Extract brush-controls.js
   - ✅ Extract movement-controls.js
   - ✅ Extract visualization.js

3. **Settings Management** (NEXT)
   - Create settings-manager.js
   - Migrate settings handling

4. **Integration and Testing** (FUTURE)
   - Connect modules together
   - Test each component in isolation
   - Test integrated system

5. **Cleanup and Optimization** (FUTURE)
   - Remove duplicate code
   - Optimize event listeners
   - Improve error handling

## Testing Strategy

1. **Module Testing**: Test each module in isolation with mock dependencies
2. **Integration Testing**: Test modules working together
3. **UI Testing**: Test UI components with simulated user interactions
4. **Error Handling Testing**: Test system behavior with simulated errors

## Migration Strategy

To minimize disruption, the refactoring follows these steps:

1. Create new modules alongside existing code
2. Gradually migrate functionality to new modules
3. Update references to use new modules
4. Remove old code once migration is complete

This approach allows for incremental testing and reduces the risk of breaking existing functionality. 
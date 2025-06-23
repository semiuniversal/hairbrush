# Implementation Plan

## Three-Component Architecture

Our implementation follows a three-component architecture:

1. **Inkscape Extension** - SVG processing and G-code generation (95% complete)
2. **Web Controller** - Machine control and monitoring interface (85% complete)
3. **Duet 2 WiFi Integration** - Hardware control and execution (15% complete)

## Implementation Priorities

### 1. Web Controller (Current Focus)
- [x] Develop Flask-based web server
- [x] Implement Duet communication client
- [x] Create job management system
- [x] Design responsive web UI
- [ ] Complete testing and optimization
- [ ] Create documentation and deployment guides

### 2. Inkscape Extension (Mostly Complete)
- [x] Fix extension not appearing in Inkscape on Windows
- [x] Implement proper SVG parsing with namespace handling
- [x] Improve path processing for all SVG commands
- [x] Ensure accurate coordinate transformation
- [x] Implement hybrid approach with M400 commands in G-code generation
- [ ] Create GitHub repository and documentation

### 3. Duet 2 WiFi Integration
- [x] Implement Telnet interface for G-code streaming
- [x] Create HTTP API client for status monitoring
- [x] Add WebSocket support for real-time updates
- [x] Develop G-code command templates for brush control
- [x] Implement G-code processing with M400 synchronization points
- [ ] Test with real hardware
- [ ] Calibrate brush parameters for optimal performance

## Web Controller Implementation Status

### Completed Components
- [x] Project structure setup with Flask and WebSocket support
- [x] Duet client with Telnet, HTTP, and WebSocket communication
- [x] Job management system with file handling and job control
- [x] Machine control interface with jog controls and brush commands
- [x] Web UI with dashboard, control panel, and file management
- [x] G-code processing with support for M400 synchronization points

### Remaining Tasks

#### 1. Testing and Optimization
- Hardware testing with Duet 2 WiFi board
- Performance optimization for real-time control
- Error recovery mechanisms implementation
- Comprehensive logging system

#### 2. Documentation and Deployment
- User guide creation
- API documentation
- Deployment instructions for various environments
- Configuration examples

## Duet Communication Strategy

### Motion Synchronization (IMPLEMENTED)
- Use `M400` command to wait for all buffered moves to complete
- Implemented hybrid approach:
  1. Insert `M400` after each complete stroke in G-code generation
  2. Recognize `M400` as blocking synchronization points in controller
  3. Inject additional `M400` for live-streamed operations

### Position Monitoring (IMPLEMENTED)
- Use `M114` to query current position for UI updates
- Implement polling mechanism for real-time position display

### Implementation Pattern (IMPLEMENTED)
```python
# In duet_client.py
def send_command_and_wait(self, command: str) -> Dict[str, Any]:
    """Send command and wait for completion with M400"""
    result = self.send_command(command)
    if result["status"] == "error":
        return result
    
    # Send M400 to wait for motion completion
    return self.wait_for_motion_complete()

def wait_for_motion_complete(self) -> Dict[str, Any]:
    """Send M400 to wait for all buffered moves to complete"""
    return self.send_command("M400")

def get_position(self) -> Dict[str, Any]:
    """Get current position using M114"""
    result = self.send_command("M114")
    # Parse position response
    # ...

# In machine_control.py
def process_gcode_file(self, filename: str) -> Dict[str, Any]:
    """Process G-code with M400 synchronization awareness"""
    # Read file line by line
    for line in lines:
        command = line.split(';')[0].strip()
        
        if command.upper().startswith("M400"):
            # Wait for all previous commands to complete
            result = self.duet_client.wait_for_motion_complete()
        else:
            # Send command without waiting
            result = self.duet_client.send_command(command)
```

## Implementation Timeline

### Week 1: Testing and Optimization
- Day 1-2: Hardware testing setup and verification
- Day 3-4: Performance profiling and optimization
- Day 5-7: Error recovery implementation and testing

### Week 2: Documentation and Integration Testing
- Day 1-3: User guide and API documentation
- Day 4-5: Deployment instructions and configuration examples
- Day 6-7: End-to-end workflow testing and brush control verification

### Week 3: Final Integration and Release Preparation
- Day 1-3: Hardware-specific documentation and testing
- Day 4-5: Final bug fixes and optimizations
- Day 6-7: GitHub repository setup and public release preparation

## Testing Strategy

### Unit Testing
- Duet Client: Connection, commands, error handling
- Job Manager: File upload, job control, error handling
- Machine Control: Jog commands, brush control, maintenance routines
- Configuration: Loading, saving, validation

### Integration Testing
- Component integration tests
- API integration tests
- UI integration tests with real-time updates

### System Testing
- End-to-end workflow from Inkscape to hardware
- Performance testing for UI responsiveness and WebSocket latency
- Security testing for authentication and input validation

### Testing Tools
- pytest for unit and integration testing
- pytest-cov for code coverage analysis
- locust for performance testing
- selenium for UI testing

## Documentation Plan

### User Guide
- Installation and setup instructions
- Web interface usage guide
- Workflow guide from design to execution
- Troubleshooting section

### API Documentation
- REST API endpoints
- WebSocket events and message formats
- Integration examples

### Developer Guide
- Architecture overview
- Code structure explanation
- Extension points
- Development setup instructions

## Key Technical Challenges

1. **Real-time Control** (IMPLEMENTED)
   - Ensuring responsive UI during long operations
   - Handling WebSocket reconnection
   - Managing concurrent operations
   - Implemented proper motion synchronization with `M400`

2. **Error Recovery** (CURRENT FOCUS)
   - Connection loss detection and recovery
   - Job recovery after interruption
   - Robust error handling for hardware communication

3. **Performance Optimization**
   - WebSocket communication for low latency
   - G-code parsing efficiency for large files
   - Status updates throttling to reduce network traffic

## Success Criteria

- [x] Extension appears and functions in Inkscape on Windows
- [x] SVG paths convert accurately to G-code
- [x] Web controller provides intuitive machine interface
- [x] System handles all SVG path types correctly
- [x] Installation process works reliably across platforms
- [x] Motion synchronization implemented with hybrid M400 approach
- [ ] Real-time control and monitoring works smoothly
- [x] G-code visualization accurately represents machine movements
- [ ] Maintenance routines function correctly with real hardware 
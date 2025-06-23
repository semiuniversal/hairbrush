/**
 * Control JavaScript for H.Airbrush Web Controller
 * Handles machine control functionality
 */

// Note: Using socket from websocket.js

// DOM elements
const jogButtons = document.querySelectorAll('.jog-btn');
const distanceInputs = document.querySelectorAll('input[name="distance"]');
const speedInputs = document.querySelectorAll('input[name="speed"]');
const homeAllBtn = document.getElementById('home-all');
const homeXYBtn = document.getElementById('home-xy');
const homeZBtn = document.getElementById('home-z');
const parkMachineBtn = document.getElementById('park-machine');
const disableMotorsBtn = document.getElementById('disable-motors');
const refreshEndstopsBtn = document.getElementById('refresh-endstops');

// Brush control buttons
const brushAAirOnBtn = document.getElementById('brush-a-air-on');
const brushAAirOffBtn = document.getElementById('brush-a-air-off');
const brushAPaintOnBtn = document.getElementById('brush-a-paint-on');
const brushAPaintOffBtn = document.getElementById('brush-a-paint-off');
const brushBAirOnBtn = document.getElementById('brush-b-air-on');
const brushBAirOffBtn = document.getElementById('brush-b-air-off');
const brushBPaintOnBtn = document.getElementById('brush-b-paint-on');
const brushBPaintOffBtn = document.getElementById('brush-b-paint-off');

// Manual command elements
const manualCommandInput = document.getElementById('manual-command');
const sendCommandBtn = document.getElementById('send-command');
const commandHistoryList = document.getElementById('command-history');

// Visualization elements
const visualization = document.querySelector('.visualization-wrapper');
const visualizationContainer = document.querySelector('.visualization-container');
const paperSheet = document.querySelector('.paper-sheet');
const brushA = document.getElementById('brush-a-position');
const brushB = document.getElementById('brush-b-position');
const origin = document.querySelector('.machine-origin');
const axisLabelX = document.getElementById('axis-label-x');
const axisLabelY = document.getElementById('axis-label-y');

// Endstop elements
const xEndstopStatus = document.getElementById('x-endstop');
const yEndstopStatus = document.getElementById('y-endstop');
const zEndstopStatus = document.getElementById('z-endstop');

// Machine configuration
let machineConfig = {
    paper: {
        width: 841,   // A0 width in mm (portrait)
        height: 1189, // A0 height in mm (portrait)
        orientation: 'portrait'
    },
    brushes: {
        a: { offsetX: 0, offsetY: 0 },
        b: { offsetX: 50, offsetY: 0 }
    }
};

// Visualization variables
let scale = 1;
let originX = 0;
let originY = 0;
let paperLeft = 0;
let paperTop = 0;

// Current settings
let currentDistance = 1;
let currentSpeed = 1000;

// Global variables
let endstopPollingInterval;

// Initialize control page
function initControlPage() {
    console.log('Initializing control page');
    
    // Check if socket and hairbrushController are available
    console.log('Socket available:', typeof socket !== 'undefined');
    console.log('hairbrushController available:', typeof window.hairbrushController !== 'undefined');
    
    // Set up socket event listeners (using socket from websocket.js)
    setupSocketListeners();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize visualization
    initVisualization();
    
    // Initial status update
    if (typeof window.hairbrushController !== 'undefined' && 
        typeof window.hairbrushController.requestMachineStatus === 'function') {
        console.log('Requesting initial machine status');
        window.hairbrushController.requestMachineStatus();
    } else {
        console.error('hairbrushController.requestMachineStatus not available');
    }
}

// Set up socket event listeners
function setupSocketListeners() {
    // Check if socket is available from the global scope (set by websocket.js)
    if (typeof socket === 'undefined') {
        console.error('Socket is not defined - make sure websocket.js is loaded');
        return;
    }
    
    console.log('Setting up control-specific socket listeners');
    
    // Listen for status updates - this is handled by websocket.js, 
    // but we'll add our own listener to update the visualization
    socket.on('status_update', function(data) {
        console.log('Control: status update received:', data);
        onMachineStatusUpdate(data);
    });
    
    // Listen for command responses
    socket.on('command_response', function(data) {
        console.log('Control: command response received:', data);
        if (data.command && data.response) {
            addToCommandHistory(data.command, data.response);
        }
    });
}

// Initialize visualization
function initVisualization() {
    if (!visualization || !paperSheet || !brushA || !brushB || !origin) {
        console.error('Visualization elements not found');
        return;
    }
    
    // Get machine configuration from server
    fetch('/api/machine/config')
        .then(response => response.json())
        .then(config => {
            if (config && config.machine && config.machine.paper) {
                machineConfig.paper = config.machine.paper;
            }
            if (config && config.brushes) {
                machineConfig.brushes = config.brushes;
            }
            setupVisualization();
        })
        .catch(error => {
            console.error('Error loading machine configuration:', error);
            setupVisualization();
        });
}

// Set up visualization based on machine configuration
function setupVisualization() {
    if (!visualization || !visualizationContainer || !paperSheet) {
        console.error('Visualization elements not found');
        return;
    }
    
    console.log('Setting up visualization');
    
    // Get paper dimensions
    const paperWidth = machineConfig.paper.width;
    const paperHeight = machineConfig.paper.height;
    
    // Calculate visualization scale
    const visWidth = visualization.clientWidth;
    const visHeight = visualization.clientHeight;
    
    console.log('Visualization dimensions:', visWidth, 'x', visHeight);
    
    // Calculate scaling factor to fit paper in visualization
    // We want to maintain aspect ratio and leave some margin
    const margin = 20; // margin in pixels
    const availableWidth = visWidth - (2 * margin);
    const availableHeight = visHeight - (2 * margin);
    
    // Calculate scale (mm to pixels) based on the limiting dimension
    const scaleX = availableWidth / paperWidth;
    const scaleY = availableHeight / paperHeight;
    scale = Math.min(scaleX, scaleY);
    
    console.log('Scale:', scale, 'pixels per mm');
    
    // Calculate paper dimensions in pixels
    const paperWidthPx = paperWidth * scale;
    const paperHeightPx = paperHeight * scale;
    
    // Position paper in center of visualization
    paperLeft = (visWidth - paperWidthPx) / 2;
    paperTop = (visHeight - paperHeightPx) / 2;
    
    // Set paper dimensions and position
    paperSheet.style.width = paperWidthPx + 'px';
    paperSheet.style.height = paperHeightPx + 'px';
    paperSheet.style.left = paperLeft + 'px';
    paperSheet.style.top = paperTop + 'px';
    
    // Clear any existing grid lines
    const existingGridLines = visualizationContainer.querySelectorAll('.grid-line');
    existingGridLines.forEach(line => line.remove());
    
    // Add grid lines
    const gridSpacing = 50; // mm
    const gridSpacingPx = gridSpacing * scale;
    
    // Add horizontal grid lines
    for (let y = 0; y <= paperHeight; y += gridSpacing) {
        const line = document.createElement('div');
        line.className = 'grid-line grid-line-horizontal';
        line.style.top = (paperTop + y * scale) + 'px';
        line.style.left = paperLeft + 'px';
        line.style.width = paperWidthPx + 'px';
        visualizationContainer.appendChild(line);
    }
    
    // Add vertical grid lines
    for (let x = 0; x <= paperWidth; x += gridSpacing) {
        const line = document.createElement('div');
        line.className = 'grid-line grid-line-vertical';
        line.style.left = (paperLeft + x * scale) + 'px';
        line.style.top = paperTop + 'px';
        line.style.height = paperHeightPx + 'px';
        visualizationContainer.appendChild(line);
    }
    
    // Set origin position (bottom-left of paper)
    originX = paperLeft;
    originY = paperTop + paperHeightPx;
    origin.style.left = originX + 'px';
    origin.style.top = originY + 'px';
    
    // Set axis labels
    if (axisLabelX) {
        axisLabelX.style.position = 'absolute';
        axisLabelX.style.left = (paperLeft + paperWidthPx - 20) + 'px';
        axisLabelX.style.top = (paperTop + paperHeightPx - 20) + 'px';
    }
    
    if (axisLabelY) {
        axisLabelY.style.position = 'absolute';
        axisLabelY.style.left = (paperLeft + 20) + 'px';
        axisLabelY.style.top = (paperTop + 20) + 'px';
    }
    
    // Style brush indicators
    if (brushA) {
        brushA.style.backgroundColor = '#000000';
        brushA.style.color = 'white';
        brushA.style.width = '15px';
        brushA.style.height = '15px';
        brushA.style.borderRadius = '50%';
        brushA.style.zIndex = '10';
        
        const labelA = brushA.querySelector('.machine-head-label');
        if (labelA) {
            labelA.style.color = 'white';
        }
    }
    
    if (brushB) {
        brushB.style.backgroundColor = '#ffffff';
        brushB.style.border = '2px solid #000000';
        brushB.style.color = '#000000';
        brushB.style.width = '15px';
        brushB.style.height = '15px';
        brushB.style.borderRadius = '50%';
        brushB.style.zIndex = '10';
        
        const labelB = brushB.querySelector('.machine-head-label');
        if (labelB) {
            labelB.style.color = '#000000';
        }
    }
    
    // Initial brush positions
    updateBrushPosition(brushA, 0, 0);
    updateBrushPosition(brushB, 
        machineConfig.brushes.b.offsetX || 50, 
        machineConfig.brushes.b.offsetY || 0
    );
    
    console.log('Visualization setup complete');
}

// Update brush position in visualization
function updateBrushPosition(element, x, y) {
    if (!element || !paperSheet) {
        return;
    }
    
    // Get paper dimensions from the element's style
    const paperWidth = parseFloat(paperSheet.style.width) || 0;
    const paperHeight = parseFloat(paperSheet.style.height) || 0;
    const paperLeft = parseFloat(paperSheet.style.left) || 0;
    const paperTop = parseFloat(paperSheet.style.top) || 0;
    
    // Calculate position in pixels
    // Origin is at bottom-left of paper in machine coordinates
    const xPx = paperLeft + (x * scale);
    const yPx = paperTop + paperHeight - (y * scale); // Y is inverted in visualization
    
    // Set position
    element.style.left = xPx + 'px';
    element.style.top = yPx + 'px';
    
    // Make sure the brush position label is visible
    const label = element.querySelector('.machine-head-label');
    if (label) {
        // If we're near the top edge, move label below the brush
        if (yPx < 30) {
            label.style.top = '15px';
        } else {
            label.style.top = '-20px';
        }
    }
    
    // Log position for debugging
    console.log(`Brush position: (${x}, ${y}) mm -> (${xPx}, ${yPx}) px`);
}

// Set up event listeners
function setupEventListeners() {
    // Jog buttons
    jogButtons.forEach(button => {
        button.addEventListener('click', handleJogButtonClick);
    });
    
    // Distance inputs
    distanceInputs.forEach(input => {
        input.addEventListener('change', () => {
            currentDistance = parseFloat(input.value);
        });
    });
    
    // Speed inputs
    speedInputs.forEach(input => {
        input.addEventListener('change', () => {
            currentSpeed = parseInt(input.value);
        });
    });
    
    // Home all button
    if (homeAllBtn) {
        homeAllBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('G28')
                .then(() => {
                    console.log('Machine homed');
                    addToCommandHistory('G28', 'Machine homed');
                })
                .catch(handleError);
        });
    }
    
    // Home XY button
    if (homeXYBtn) {
        homeXYBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('G28 X Y')
                .then(() => {
                    console.log('XY axes homed');
                    addToCommandHistory('G28 X Y', 'XY axes homed');
                })
                .catch(handleError);
        });
    }
    
    // Home Z button
    if (homeZBtn) {
        homeZBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('G28 Z')
                .then(() => {
                    console.log('Z axis homed');
                    addToCommandHistory('G28 Z', 'Z axis homed');
                })
                .catch(handleError);
        });
    }
    
    // Park machine button
    if (parkMachineBtn) {
        parkMachineBtn.addEventListener('click', () => {
            // First move Z to safe height
            hairbrushController.sendCommand('G1 Z10 F500')
                .then(() => {
                    addToCommandHistory('G1 Z10 F500', 'Z raised to safe height');
                    // Then move to park position
                    return hairbrushController.sendCommand('G1 X0 Y0 F3000');
                })
                .then(() => {
                    console.log('Machine parked');
                    addToCommandHistory('G1 X0 Y0 F3000', 'Machine parked');
                })
                .catch(handleError);
        });
    }
    
    // Disable motors button
    if (disableMotorsBtn) {
        disableMotorsBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M18')
                .then(() => {
                    console.log('Motors disabled');
                    addToCommandHistory('M18', 'Motors disabled');
                })
                .catch(handleError);
        });
    }
    
    // Brush A air on button
    if (brushAAirOnBtn) {
        brushAAirOnBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M42 P0 S1')
                .then(() => {
                    console.log('Brush A air on');
                    addToCommandHistory('M42 P0 S1', 'Brush A air on');
                })
                .catch(handleError);
        });
    }
    
    // Brush A air off button
    if (brushAAirOffBtn) {
        brushAAirOffBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M42 P0 S0')
                .then(() => {
                    console.log('Brush A air off');
                    addToCommandHistory('M42 P0 S0', 'Brush A air off');
                })
                .catch(handleError);
        });
    }
    
    // Brush A paint on button
    if (brushAPaintOnBtn) {
        brushAPaintOnBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M280 P0 S90')
                .then(() => {
                    console.log('Brush A paint on');
                    addToCommandHistory('M280 P0 S90', 'Brush A paint on');
                })
                .catch(handleError);
        });
    }
    
    // Brush A paint off button
    if (brushAPaintOffBtn) {
        brushAPaintOffBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M280 P0 S0')
                .then(() => {
                    console.log('Brush A paint off');
                    addToCommandHistory('M280 P0 S0', 'Brush A paint off');
                })
                .catch(handleError);
        });
    }
    
    // Brush B air on button
    if (brushBAirOnBtn) {
        brushBAirOnBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M42 P1 S1')
                .then(() => {
                    console.log('Brush B air on');
                    addToCommandHistory('M42 P1 S1', 'Brush B air on');
                })
                .catch(handleError);
        });
    }
    
    // Brush B air off button
    if (brushBAirOffBtn) {
        brushBAirOffBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M42 P1 S0')
                .then(() => {
                    console.log('Brush B air off');
                    addToCommandHistory('M42 P1 S0', 'Brush B air off');
                })
                .catch(handleError);
        });
    }
    
    // Brush B paint on button
    if (brushBPaintOnBtn) {
        brushBPaintOnBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M280 P1 S90')
                .then(() => {
                    console.log('Brush B paint on');
                    addToCommandHistory('M280 P1 S90', 'Brush B paint on');
                })
                .catch(handleError);
        });
    }
    
    // Brush B paint off button
    if (brushBPaintOffBtn) {
        brushBPaintOffBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M280 P1 S0')
                .then(() => {
                    console.log('Brush B paint off');
                    addToCommandHistory('M280 P1 S0', 'Brush B paint off');
                })
                .catch(handleError);
        });
    }
    
    // Manual command input
    if (manualCommandInput) {
        manualCommandInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                sendManualCommand();
            }
        });
    }
    
    // Send command button
    if (sendCommandBtn) {
        sendCommandBtn.addEventListener('click', sendManualCommand);
    }
    
    // Handle window resize
    window.addEventListener('resize', debounce(() => {
        setupVisualization();
    }, 250));
}

// Handle jog button click
function handleJogButtonClick(event) {
    const button = event.currentTarget;
    const axis = button.getAttribute('data-axis');
    
    if (axis === 'home') {
        // Home all axes
        hairbrushController.sendCommand('G28')
            .then(() => {
                console.log('Machine homed');
                addToCommandHistory('G28', 'Machine homed');
            })
            .catch(handleError);
        return;
    }
    
    // Get distance from button or current setting
    let distance = parseFloat(button.getAttribute('data-distance') || currentDistance);
    
    // Send jog command
    hairbrushController.sendJog(axis, distance, currentSpeed)
        .then(() => {
            console.log(`Jogged ${axis} by ${distance}mm at ${currentSpeed}mm/min`);
            addToCommandHistory(`G1 ${axis}${distance} F${currentSpeed}`, `Jogged ${axis} by ${distance}mm`);
        })
        .catch(handleError);
}

// Send manual command
function sendManualCommand() {
    const command = manualCommandInput.value.trim();
    if (!command) return;
    
    hairbrushController.sendCommand(command)
        .then((result) => {
            console.log(`Command sent: ${command}`);
            addToCommandHistory(command, result || 'Command executed');
            manualCommandInput.value = '';
        })
        .catch((error) => {
            handleError(error);
            addToCommandHistory(command, error.message, true);
        });
}

// Add command to history
function addToCommandHistory(command, result, isError = false) {
    if (!commandHistoryList) return;
    
    // Remove "no commands" message if present
    const noCommandsMsg = commandHistoryList.querySelector('.text-muted');
    if (noCommandsMsg) {
        commandHistoryList.removeChild(noCommandsMsg);
    }
    
    // Create history item
    const item = document.createElement('div');
    item.className = 'command-history-item mb-2 p-2 border-bottom';
    
    const commandEl = document.createElement('div');
    commandEl.className = 'command-text font-monospace small';
    commandEl.textContent = `> ${command}`;
    
    const resultEl = document.createElement('div');
    resultEl.className = `command-result small ${isError ? 'text-danger' : 'text-muted'}`;
    resultEl.textContent = result;
    
    item.appendChild(commandEl);
    item.appendChild(resultEl);
    
    // Add to history list
    commandHistoryList.insertBefore(item, commandHistoryList.firstChild);
    
    // Limit history to 10 items
    while (commandHistoryList.children.length > 10) {
        commandHistoryList.removeChild(commandHistoryList.lastChild);
    }
}

// Handle errors
function handleError(error) {
    console.error('Error:', error);
    alert(`Error: ${error.message || 'Unknown error'}`);
}

// Machine status update handler
function onMachineStatusUpdate(data) {
    console.log('Control: Processing machine status update', data);
    if (!data) {
        console.warn('Control: Empty data received in status update');
        return;
    }
    
    // Update position visualization
    if (data.position && brushA && brushB) {
        // Update position display elements if they exist
        if (document.getElementById('x-position')) {
            document.getElementById('x-position').textContent = data.position.X.toFixed(2);
        }
        if (document.getElementById('y-position')) {
            document.getElementById('y-position').textContent = data.position.Y.toFixed(2);
        }
        if (document.getElementById('z-position')) {
            document.getElementById('z-position').textContent = data.position.Z.toFixed(2);
        }
        
        // Update brush A position
        updateBrushPosition(brushA, data.position.X, data.position.Y);
        
        // Get brush B offsets
        const offsetX = machineConfig.brushes.b.offsetX || 50;
        const offsetY = machineConfig.brushes.b.offsetY || 0;
        
        // Update brush B position
        updateBrushPosition(brushB, data.position.X + offsetX, data.position.Y + offsetY);
        
        // Update brush visibility based on Z height
        if (data.position.Z > 5) { // If Z is high, make brushes semi-transparent
            brushA.style.opacity = '0.5';
            brushB.style.opacity = '0.5';
        } else {
            brushA.style.opacity = '1';
            brushB.style.opacity = '1';
        }
    }
    
    // Update brush state indicators
    if (data.brush_state) {
        // Update brush A status
        const brushAStatus = document.getElementById('brush-a-status');
        const brushAStatusIndicator = document.getElementById('brush-a-status-indicator');
        
        if (brushAStatus && data.brush_state.a) {
            let status = 'Inactive';
            let isActive = false;
            
            if (data.brush_state.a.air && data.brush_state.a.paint) {
                status = 'Active (Air + Paint)';
                isActive = true;
            } else if (data.brush_state.a.air) {
                status = 'Air Only';
                isActive = true;
            } else if (data.brush_state.a.paint) {
                status = 'Paint Only';
                isActive = true;
            }
            
            brushAStatus.textContent = status;
            
            if (brushAStatusIndicator) {
                if (isActive) {
                    brushAStatusIndicator.classList.remove('status-inactive');
                    brushAStatusIndicator.classList.add('status-active');
                } else {
                    brushAStatusIndicator.classList.remove('status-active');
                    brushAStatusIndicator.classList.add('status-inactive');
                }
            }
        }
        
        // Update brush B status
        const brushBStatus = document.getElementById('brush-b-status');
        const brushBStatusIndicator = document.getElementById('brush-b-status-indicator');
        
        if (brushBStatus && data.brush_state.b) {
            let status = 'Inactive';
            let isActive = false;
            
            if (data.brush_state.b.air && data.brush_state.b.paint) {
                status = 'Active (Air + Paint)';
                isActive = true;
            } else if (data.brush_state.b.air) {
                status = 'Air Only';
                isActive = true;
            } else if (data.brush_state.b.paint) {
                status = 'Paint Only';
                isActive = true;
            }
            
            brushBStatus.textContent = status;
            
            if (brushBStatusIndicator) {
                if (isActive) {
                    brushBStatusIndicator.classList.remove('status-inactive');
                    brushBStatusIndicator.classList.add('status-active');
                } else {
                    brushBStatusIndicator.classList.remove('status-active');
                    brushBStatusIndicator.classList.add('status-inactive');
                }
            }
        }
    }
}

// Debounce function for resize events
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', initControlPage);

// Add control-specific functions to the global hairbrushController
// Note: The main hairbrushController object is defined in websocket.js
if (typeof window.hairbrushController !== 'undefined') {
    // Add our control-specific functions
    window.hairbrushController.controlInit = initControlPage;
} else {
    console.error('hairbrushController not found in global scope');
}

// Send command to server
function sendCommand(command) {
    return new Promise((resolve, reject) => {
        // Use the global socket from websocket.js
        if (typeof socket === 'undefined' || !socket.connected) {
            reject(new Error('Not connected to server'));
            return;
        }
        
        socket.emit('command', { command }, (response) => {
            if (response && response.status === 'success') {
                // Request updated status after command completes
                setTimeout(() => {
                    // Call our local requestMachineStatus to avoid recursion
                    requestMachineStatus();
                }, 500); // Small delay to allow machine to update position
                
                resolve(response.result);
            } else {
                reject(new Error(response?.message || 'Command failed'));
            }
        });
    });
}

// Send jog command to server
function sendJog(axis, distance, speed) {
    return new Promise((resolve, reject) => {
        // Use the global socket from websocket.js
        if (typeof socket === 'undefined' || !socket.connected) {
            reject(new Error('Not connected to server'));
            return;
        }
        
        socket.emit('jog', { axis, distance, speed }, (response) => {
            if (response && response.status === 'success') {
                // Request updated status after command completes
                setTimeout(() => {
                    // Call our local requestMachineStatus to avoid recursion
                    requestMachineStatus();
                }, 500);
                
                resolve(response.result);
            } else {
                reject(new Error(response?.message || 'Jog command failed'));
            }
        });
    });
}

// Request machine status from server
function requestMachineStatus() {
    // Use the socket directly to avoid recursion
    if (typeof socket !== 'undefined' && socket.connected) {
        socket.emit('get_status', {}, (response) => {
            if (response && response.status === 'success') {
                onMachineStatusUpdate(response.data);
            }
        });
    }
}

// Query endstop status
function queryEndstopStatus() {
    if (!socket || !socket.connected) {
        console.error('Socket not connected, cannot query endstops');
        return;
    }
    
    // Update UI to show loading state
    if (xEndstopStatus) xEndstopStatus.className = 'endstop-value badge bg-secondary';
    if (yEndstopStatus) yEndstopStatus.className = 'endstop-value badge bg-secondary';
    if (zEndstopStatus) zEndstopStatus.className = 'endstop-value badge bg-secondary';
    
    if (xEndstopStatus) xEndstopStatus.textContent = 'Checking...';
    if (yEndstopStatus) yEndstopStatus.textContent = 'Checking...';
    if (zEndstopStatus) zEndstopStatus.textContent = 'Checking...';
    
    // Send M119 command to query endstops
    socket.emit('command', { command: 'M119' }, (response) => {
        if (response && response.status === 'success' && response.result && response.result.response) {
            updateEndstopUI(response.result.response);
        } else {
            console.error('Failed to query endstops:', response);
            
            // Update UI to show error state
            if (xEndstopStatus) {
                xEndstopStatus.className = 'endstop-value badge bg-danger';
                xEndstopStatus.textContent = 'Error';
            }
            if (yEndstopStatus) {
                yEndstopStatus.className = 'endstop-value badge bg-danger';
                yEndstopStatus.textContent = 'Error';
            }
            if (zEndstopStatus) {
                zEndstopStatus.className = 'endstop-value badge bg-danger';
                zEndstopStatus.textContent = 'Error';
            }
        }
    });
}

// Update endstop UI based on M119 response
function updateEndstopUI(response) {
    console.log('Endstop response:', response);
    
    // Parse the response
    // Example format: "Endstops - X: not stopped, Y: not stopped, Z: not stopped"
    const endstopRegex = /Endstops\s*-\s*X:\s*([^,]+),\s*Y:\s*([^,]+),\s*Z:\s*([^\s]+)/i;
    const match = response.match(endstopRegex);
    
    if (match && match.length >= 4) {
        const xStatus = match[1].trim();
        const yStatus = match[2].trim();
        const zStatus = match[3].trim();
        
        // Update X endstop
        if (xEndstopStatus) {
            if (xStatus.includes('min stop')) {
                xEndstopStatus.className = 'endstop-value badge bg-danger';
                xEndstopStatus.textContent = 'TRIGGERED (min)';
            } else if (xStatus.includes('max stop')) {
                xEndstopStatus.className = 'endstop-value badge bg-danger';
                xEndstopStatus.textContent = 'TRIGGERED (max)';
            } else if (xStatus.includes('not stopped')) {
                xEndstopStatus.className = 'endstop-value badge bg-success';
                xEndstopStatus.textContent = 'Not triggered';
            } else {
                xEndstopStatus.className = 'endstop-value badge bg-warning';
                xEndstopStatus.textContent = xStatus;
            }
        }
        
        // Update Y endstop
        if (yEndstopStatus) {
            if (yStatus.includes('min stop')) {
                yEndstopStatus.className = 'endstop-value badge bg-danger';
                yEndstopStatus.textContent = 'TRIGGERED (min)';
            } else if (yStatus.includes('max stop')) {
                yEndstopStatus.className = 'endstop-value badge bg-danger';
                yEndstopStatus.textContent = 'TRIGGERED (max)';
            } else if (yStatus.includes('not stopped')) {
                yEndstopStatus.className = 'endstop-value badge bg-success';
                yEndstopStatus.textContent = 'Not triggered';
            } else {
                yEndstopStatus.className = 'endstop-value badge bg-warning';
                yEndstopStatus.textContent = yStatus;
            }
        }
        
        // Update Z endstop
        if (zEndstopStatus) {
            if (zStatus.includes('min stop')) {
                zEndstopStatus.className = 'endstop-value badge bg-danger';
                zEndstopStatus.textContent = 'TRIGGERED (min)';
            } else if (zStatus.includes('max stop')) {
                zEndstopStatus.className = 'endstop-value badge bg-danger';
                zEndstopStatus.textContent = 'TRIGGERED (max)';
            } else if (zStatus.includes('not stopped')) {
                zEndstopStatus.className = 'endstop-value badge bg-success';
                zEndstopStatus.textContent = 'Not triggered';
            } else {
                zEndstopStatus.className = 'endstop-value badge bg-warning';
                zEndstopStatus.textContent = zStatus;
            }
        }
    } else {
        console.error('Failed to parse endstop response:', response);
        
        // Update UI to show error state
        if (xEndstopStatus) {
            xEndstopStatus.className = 'endstop-value badge bg-warning';
            xEndstopStatus.textContent = 'Parse error';
        }
        if (yEndstopStatus) {
            yEndstopStatus.className = 'endstop-value badge bg-warning';
            yEndstopStatus.textContent = 'Parse error';
        }
        if (zEndstopStatus) {
            zEndstopStatus.className = 'endstop-value badge bg-warning';
            zEndstopStatus.textContent = 'Parse error';
        }
    }
}

// Socket connection
function connectSocket() {
    if (typeof io === 'undefined') {
        console.error('Socket.IO not loaded');
        return;
    }
    
    // Use the global socket variable without redeclaring it
    if (typeof socket === 'undefined') {
        console.warn('Global socket variable not defined, using window.socket');
        window.socket = io.connect(window.location.protocol + '//' + window.location.host, {
            path: '/socket.io'
        });
        socket = window.socket;
    } else if (!socket.connected) {
        // If socket exists but not connected, reconnect
        socket.connect();
    }

    socket.on('connect', function() {
        console.log('Connected to server');
        // Query position immediately after connection
        sendCommand('M114');
        
        // Query endstops after connection
        setTimeout(() => {
            queryEndstopStatus();
        }, 1000);
        
        // Set up periodic endstop polling (every 5 seconds)
        if (endstopPollingInterval) {
            clearInterval(endstopPollingInterval);
        }
        endstopPollingInterval = setInterval(queryEndstopStatus, 5000);
    });

    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        if (endstopPollingInterval) {
            clearInterval(endstopPollingInterval);
            endstopPollingInterval = null;
        }
    });

    socket.on('position_update', function(data) {
        updatePositionDisplay(data);
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Jog buttons
    jogButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const axis = this.dataset.axis;
            const direction = parseInt(this.dataset.direction);
            const distance = getSelectedDistance();
            const speed = getSelectedSpeed();
            jogAxis(axis, direction, distance, speed);
        });
    });

    // Home buttons
    if (homeAllBtn) {
        homeAllBtn.addEventListener('click', function() {
            sendCommand('G28');
        });
    }
    
    if (homeXYBtn) {
        homeXYBtn.addEventListener('click', function() {
            sendCommand('G28 X Y');
        });
    }
    
    if (homeZBtn) {
        homeZBtn.addEventListener('click', function() {
            sendCommand('G28 Z');
        });
    }

    // Park button
    if (parkMachineBtn) {
        parkMachineBtn.addEventListener('click', function() {
            sendCommand('G1 X0 Y0 F3000');
        });
    }

    // Disable motors
    if (disableMotorsBtn) {
        disableMotorsBtn.addEventListener('click', function() {
            sendCommand('M18');
        });
    }
    
    // Refresh endstops
    if (refreshEndstopsBtn) {
        refreshEndstopsBtn.addEventListener('click', function() {
            queryEndstopStatus();
        });
    }

    // Brush control buttons
    if (brushAAirOnBtn) {
        brushAAirOnBtn.addEventListener('click', function() {
            sendCommand('M42 P0 S1');
        });
    }
    
    if (brushAAirOffBtn) {
        brushAAirOffBtn.addEventListener('click', function() {
            sendCommand('M42 P0 S0');
        });
    }

    if (brushAPaintOnBtn) {
        brushAPaintOnBtn.addEventListener('click', function() {
            sendCommand('M280 P0 S90');
        });
    }
    
    if (brushAPaintOffBtn) {
        brushAPaintOffBtn.addEventListener('click', function() {
            sendCommand('M280 P0 S0');
        });
    }

    if (brushBAirOnBtn) {
        brushBAirOnBtn.addEventListener('click', function() {
            sendCommand('M42 P1 S1');
        });
    }
    
    if (brushBAirOffBtn) {
        brushBAirOffBtn.addEventListener('click', function() {
            sendCommand('M42 P1 S0');
        });
    }

    if (brushBPaintOnBtn) {
        brushBPaintOnBtn.addEventListener('click', function() {
            sendCommand('M280 P1 S90');
        });
    }
    
    if (brushBPaintOffBtn) {
        brushBPaintOffBtn.addEventListener('click', function() {
            sendCommand('M280 P1 S0');
        });
    }

    // Socket connection
    connectSocket();
});

// Update position display
function updatePositionDisplay(data) {
    if (!data || !data.position) {
        console.warn('No position data provided');
        return;
    }
    
    // Update position display elements
    const xPos = document.getElementById('x-position');
    const yPos = document.getElementById('y-position');
    const zPos = document.getElementById('z-position');
    
    if (xPos && data.position.x !== undefined) {
        xPos.textContent = parseFloat(data.position.x).toFixed(2);
    }
    
    if (yPos && data.position.y !== undefined) {
        yPos.textContent = parseFloat(data.position.y).toFixed(2);
    }
    
    if (zPos && data.position.z !== undefined) {
        zPos.textContent = parseFloat(data.position.z).toFixed(2);
    }
    
    // Update brush positions in visualization
    if (brushA && brushB) {
        updateBrushPosition(brushA, data.position.x || 0, data.position.y || 0);
        
        // Get brush B offsets
        const offsetX = machineConfig.brushes.b.offsetX || 50;
        const offsetY = machineConfig.brushes.b.offsetY || 0;
        
        // Update brush B position
        updateBrushPosition(brushB, (data.position.x || 0) + offsetX, (data.position.y || 0) + offsetY);
    }
}

// Get selected distance value
function getSelectedDistance() {
    const selected = document.querySelector('input[name="distance"]:checked');
    return selected ? parseFloat(selected.value) : currentDistance;
}

// Get selected speed value
function getSelectedSpeed() {
    const selected = document.querySelector('input[name="speed"]:checked');
    return selected ? parseInt(selected.value) : currentSpeed;
}

// Update jogAxis function to handle the jog button clicks
function jogAxis(axis, direction, distance, speed) {
    if (!socket || !socket.connected) {
        console.error('Socket not connected, cannot jog');
        return;
    }
    
    // If direction is provided, apply it to the distance
    if (direction !== undefined) {
        distance = distance * direction;
    }
    
    // Emit jog command
    socket.emit('jog', { axis, distance, speed }, (response) => {
        if (response && response.status === 'success') {
            console.log(`Jog successful: ${axis} ${distance}mm at ${speed}mm/min`);
        } else {
            console.error('Jog failed:', response);
        }
    });
} 
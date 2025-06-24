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
const enableMotorsBtn = document.getElementById('enable-motors');
const refreshEndstopsBtn = document.getElementById('refresh-endstops');

// Brush control buttons
const brushAAirToggleBtn = document.getElementById('brush-a-air-toggle');
const brushAAirText = document.getElementById('brush-a-air-text');
const brushAPaintToggleBtn = document.getElementById('brush-a-paint-toggle');
const brushAPaintText = document.getElementById('brush-a-paint-text');
const brushAPaintIcon = document.getElementById('brush-a-paint-icon');
const brushAPaintSliderContainer = document.getElementById('brush-a-paint-slider-container');
const brushAPaintSlider = document.getElementById('brush-a-paint-slider');
const brushAPaintValueElem = document.getElementById('brush-a-paint-value');
const brushBAirToggleBtn = document.getElementById('brush-b-air-toggle');
const brushBAirText = document.getElementById('brush-b-air-text');
const brushBPaintToggleBtn = document.getElementById('brush-b-paint-toggle');
const brushBPaintText = document.getElementById('brush-b-paint-text');
const brushBPaintIcon = document.getElementById('brush-b-paint-icon');
const brushBPaintSliderContainer = document.getElementById('brush-b-paint-slider-container');
const brushBPaintSlider = document.getElementById('brush-b-paint-slider');
const brushBPaintValueElem = document.getElementById('brush-b-paint-value');

// Manual command elements
const manualCommandInput = document.getElementById('manual-command');
const sendCommandBtn = document.getElementById('send-command');
const commandHistoryList = document.getElementById('command-history');
const commandCountBadge = document.getElementById('command-count');
const clearHistoryBtn = document.getElementById('clear-history');

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

// Brush state variables
let brushAPaintState = false;
let brushBPaintState = false;
let brushAPaintValue = 50; // Default to 50%
let brushBPaintValue = 50; // Default to 50%

// Motor state variable
let motorsEnabled = true; // Default to enabled

// Initialize control page
function initControlPage() {
    console.log('Initializing machine control page');
    
    // Get machine configuration
    fetch('/api/machine/config')
        .then(response => response.json())
        .then(config => {
            console.log('Loaded machine configuration:', config);
            
            // Store machine configuration
            if (config && config.machine) {
                machineConfig.machine = config.machine;
            }
            if (config && config.machine && config.machine.paper) {
                machineConfig.paper = config.machine.paper;
            }
            if (config && config.brushes) {
                machineConfig.brushes = config.brushes;
                console.log('Brush configuration:', machineConfig.brushes);
            }
            
            // Initialize visualization after loading config
            initVisualization();
            
            // Set up event listeners
            setupEventListeners();
            
            // Set up socket listeners
            setupSocketListeners();
            
            // Request initial machine status
            requestMachineStatus();
            
            // Query endstop status
            queryEndstopStatus();
        })
        .catch(error => {
            console.error('Error loading machine configuration:', error);
            
            // Continue with default configuration
            initVisualization();
            setupEventListeners();
            setupSocketListeners();
            requestMachineStatus();
            queryEndstopStatus();
        });
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
    const visWidth = visualizationContainer.clientWidth;
    const visHeight = visualizationContainer.clientHeight;
    
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
    const gridSpacing = 100; // mm - more visible spacing
    const gridSpacingPx = gridSpacing * scale;
    
    // Add horizontal grid lines
    for (let y = 0; y <= paperHeight; y += gridSpacing) {
        const line = document.createElement('div');
        line.className = 'grid-line grid-line-horizontal';
        line.style.top = (paperTop + y * scale) + 'px';
        line.style.left = paperLeft + 'px';
        line.style.width = paperWidthPx + 'px';
        line.style.height = '1px';
        line.style.backgroundColor = '#cccccc';
        visualizationContainer.appendChild(line);
    }
    
    // Add vertical grid lines
    for (let x = 0; x <= paperWidth; x += gridSpacing) {
        const line = document.createElement('div');
        line.className = 'grid-line grid-line-vertical';
        line.style.left = (paperLeft + x * scale) + 'px';
        line.style.top = paperTop + 'px';
        line.style.height = paperHeightPx + 'px';
        line.style.width = '1px';
        line.style.backgroundColor = '#cccccc';
        visualizationContainer.appendChild(line);
    }
    
    // Set origin position (center of paper)
    originX = paperLeft + (paperWidthPx / 2);
    originY = paperTop + (paperHeightPx / 2);
    origin.style.left = originX + 'px';
    origin.style.top = originY + 'px';
    
    // Set axis labels
    if (axisLabelX) {
        axisLabelX.style.position = 'absolute';
        axisLabelX.style.left = (originX + 50) + 'px';
        axisLabelX.style.top = originY + 'px';
        axisLabelX.style.transform = 'translateY(-50%)';
    }
    
    if (axisLabelY) {
        axisLabelY.style.position = 'absolute';
        axisLabelY.style.left = originX + 'px';
        axisLabelY.style.top = (originY - 50) + 'px';
        axisLabelY.style.transform = 'translateX(-50%)';
    }
    
    // Style brush indicators
    if (brushA) {
        brushA.style.position = 'absolute';
        brushA.style.backgroundColor = '#000000';
        brushA.style.color = 'white';
        brushA.style.width = '15px';
        brushA.style.height = '15px';
        brushA.style.borderRadius = '50%';
        brushA.style.zIndex = '10';
        brushA.style.transform = 'translate(-50%, -50%)';
        
        const labelA = brushA.querySelector('.machine-head-label');
        if (labelA) {
            labelA.style.position = 'absolute';
            labelA.style.top = '50%';
            labelA.style.left = '50%';
            labelA.style.transform = 'translate(-50%, -50%)';
            labelA.style.color = 'white';
            labelA.style.fontSize = '10px';
            labelA.style.fontWeight = 'bold';
            labelA.style.textAlign = 'center';
            labelA.style.width = '100%';
            labelA.style.height = '100%';
            labelA.style.display = 'flex';
            labelA.style.alignItems = 'center';
            labelA.style.justifyContent = 'center';
        }
    }
    
    if (brushB) {
        brushB.style.position = 'absolute';
        brushB.style.backgroundColor = '#ffffff';
        brushB.style.border = '2px solid #000000';
        brushB.style.color = '#000000';
        brushB.style.width = '15px';
        brushB.style.height = '15px';
        brushB.style.borderRadius = '50%';
        brushB.style.zIndex = '10';
        brushB.style.transform = 'translate(-50%, -50%)';
        
        const labelB = brushB.querySelector('.machine-head-label');
        if (labelB) {
            labelB.style.position = 'absolute';
            labelB.style.top = '50%';
            labelB.style.left = '50%';
            labelB.style.transform = 'translate(-50%, -50%)';
            labelB.style.color = '#000000';
            labelB.style.fontSize = '10px';
            labelB.style.fontWeight = 'bold';
            labelB.style.textAlign = 'center';
            labelB.style.width = '100%';
            labelB.style.height = '100%';
            labelB.style.display = 'flex';
            labelB.style.alignItems = 'center';
            labelB.style.justifyContent = 'center';
        }
    }
    
    // Initial brush positions - start at origin (center of paper)
    updateBrushPosition(brushA, 0, 0);
    
    // Get brush B offsets from configuration
    const offsetX = machineConfig.brushes?.b?.offsetX || 50;
    const offsetY = machineConfig.brushes?.b?.offsetY || 0;
    console.log('Brush B offset:', offsetX, offsetY);
    
    // Update brush B position with offset
    updateBrushPosition(brushB, offsetX, offsetY);
    
    console.log('Visualization setup complete');
}

// Update brush position in visualization
function updateBrushPosition(element, x, y) {
    if (!element || scale === undefined || originX === undefined || originY === undefined) {
        console.error('Cannot update brush position: missing required values');
        return;
    }
    
    try {
        // Calculate position in pixels relative to the origin (center of paper)
        const xPx = originX + (x * scale);
        const yPx = originY - (y * scale); // Y is inverted in visualization
        
        // Set position
        element.style.left = xPx + 'px';
        element.style.top = yPx + 'px';
        
        // Log position for debugging
        console.log(`Brush position: (${x}, ${y}) mm -> (${xPx}, ${yPx}) px`);
    } catch (e) {
        console.error('Error updating brush position:', e);
    }
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
                    
                    // Toggle buttons
                    disableMotorsBtn.style.display = 'none';
                    if (enableMotorsBtn) enableMotorsBtn.style.display = 'inline-block';
                    
                    // Disable jog and home buttons
                    disableMotionControls(true);
                })
                .catch(handleError);
        });
    }
    
    // Enable motors button
    if (enableMotorsBtn) {
        enableMotorsBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('M17')
                .then(() => {
                    console.log('Motors enabled');
                    addToCommandHistory('M17', 'Motors enabled');
                    
                    // Toggle buttons
                    enableMotorsBtn.style.display = 'none';
                    if (disableMotorsBtn) disableMotorsBtn.style.display = 'inline-block';
                    
                    // Enable jog and home buttons
                    disableMotionControls(false);
                })
                .catch(handleError);
        });
    }
    
    // Function to disable/enable motion control buttons
    function disableMotionControls(disable) {
        // Disable/enable jog buttons
        document.querySelectorAll('.jog-btn').forEach(button => {
            button.disabled = disable;
            if (disable) {
                button.classList.add('disabled');
            } else {
                button.classList.remove('disabled');
            }
        });
        
        // Disable/enable home buttons
        [homeAllBtn, homeXYBtn, homeZBtn].forEach(button => {
            if (button) {
                button.disabled = disable;
                if (disable) {
                    button.classList.add('disabled');
                } else {
                    button.classList.remove('disabled');
                }
            }
        });
    }
    
    // Brush A air toggle button
    if (brushAAirToggleBtn) {
        // Track state
        let brushAAirState = false;
        
        brushAAirToggleBtn.addEventListener('click', () => {
            // Toggle state
            brushAAirState = !brushAAirState;
            
            // Send appropriate command based on state
            const command = brushAAirState ? 'M42 P0 S1' : 'M42 P0 S0';
            const statusText = brushAAirState ? 'Brush A air on' : 'Brush A air off';
            
            hairbrushController.sendCommand(command)
                .then(() => {
                    console.log(statusText);
                    addToCommandHistory(command, statusText);
                    
                    // Update button appearance
                    if (brushAAirState) {
                        brushAAirToggleBtn.classList.remove('btn-outline-primary');
                        brushAAirToggleBtn.classList.add('btn-primary');
                        if (brushAAirText) brushAAirText.textContent = 'Air Off';
                    } else {
                        brushAAirToggleBtn.classList.remove('btn-primary');
                        brushAAirToggleBtn.classList.add('btn-outline-primary');
                        if (brushAAirText) brushAAirText.textContent = 'Air On';
                    }
                })
                .catch(handleError);
        });
    }
    
    // Brush A paint toggle button
    if (brushAPaintToggleBtn) {
        brushAPaintToggleBtn.addEventListener('click', () => {
            // Toggle state
            brushAPaintState = !brushAPaintState;
            
            // Calculate servo value based on slider
            const servoValue = brushAPaintState ? brushAPaintValue : 0;
            
            // Send appropriate command based on state
            const command = `M280 P0 S${servoValue}`;
            const statusText = brushAPaintState ? `Brush A paint on (${servoValue}%)` : 'Brush A paint off';
            
            hairbrushController.sendCommand(command)
                .then(() => {
                    console.log(statusText);
                    addToCommandHistory(command, statusText);
                    
                    // Update button appearance
                    if (brushAPaintState) {
                        brushAPaintToggleBtn.classList.remove('btn-outline-primary');
                        brushAPaintToggleBtn.classList.add('btn-primary');
                        if (brushAPaintText) brushAPaintText.textContent = 'Paint Off';
                        if (brushAPaintIcon) {
                            brushAPaintIcon.classList.remove('bi-droplet');
                            brushAPaintIcon.classList.add('bi-droplet-fill');
                        }
                        // Show slider
                        if (brushAPaintSliderContainer) {
                            brushAPaintSliderContainer.style.display = 'flex';
                        }
                    } else {
                        brushAPaintToggleBtn.classList.remove('btn-primary');
                        brushAPaintToggleBtn.classList.add('btn-outline-primary');
                        if (brushAPaintText) brushAPaintText.textContent = 'Paint On';
                        if (brushAPaintIcon) {
                            brushAPaintIcon.classList.remove('bi-droplet-fill');
                            brushAPaintIcon.classList.add('bi-droplet');
                        }
                        // Hide slider
                        if (brushAPaintSliderContainer) {
                            brushAPaintSliderContainer.style.display = 'none';
                        }
                    }
                })
                .catch(handleError);
        });
        
        // Add event listener for slider
        if (brushAPaintSlider) {
            // Update display immediately on input
            brushAPaintSlider.addEventListener('input', () => {
                // Update the value display
                brushAPaintValue = parseInt(brushAPaintSlider.value);
                if (brushAPaintValueElem) {
                    brushAPaintValueElem.textContent = `${brushAPaintValue}%`;
                }
            });
            
            // Debounce the actual command sending on change
            brushAPaintSlider.addEventListener('change', debounce(() => {
                // Only send command if paint is on
                if (brushAPaintState) {
                    const command = `M280 P0 S${brushAPaintValue}`;
                    const statusText = `Brush A paint set to ${brushAPaintValue}%`;
                    
                    hairbrushController.sendCommand(command)
                        .then(() => {
                            console.log(statusText);
                            addToCommandHistory(command, statusText);
                        })
                        .catch(handleError);
                }
            }, 300));
        }
    }
    
    // Brush B air toggle button
    if (brushBAirToggleBtn) {
        // Track state
        let brushBAirState = false;
        
        brushBAirToggleBtn.addEventListener('click', () => {
            // Toggle state
            brushBAirState = !brushBAirState;
            
            // Send appropriate command based on state
            const command = brushBAirState ? 'M42 P1 S1' : 'M42 P1 S0';
            const statusText = brushBAirState ? 'Brush B air on' : 'Brush B air off';
            
            hairbrushController.sendCommand(command)
                .then(() => {
                    console.log(statusText);
                    addToCommandHistory(command, statusText);
                    
                    // Update button appearance
                    if (brushBAirState) {
                        brushBAirToggleBtn.classList.remove('btn-outline-primary');
                        brushBAirToggleBtn.classList.add('btn-primary');
                        if (brushBAirText) brushBAirText.textContent = 'Air Off';
                    } else {
                        brushBAirToggleBtn.classList.remove('btn-primary');
                        brushBAirToggleBtn.classList.add('btn-outline-primary');
                        if (brushBAirText) brushBAirText.textContent = 'Air On';
                    }
                })
                .catch(handleError);
        });
    }
    
    // Brush B paint toggle button
    if (brushBPaintToggleBtn) {
        brushBPaintToggleBtn.addEventListener('click', () => {
            // Toggle state
            brushBPaintState = !brushBPaintState;
            
            // Calculate servo value based on slider
            const servoValue = brushBPaintState ? brushBPaintValue : 0;
            
            // Send appropriate command based on state
            const command = `M280 P1 S${servoValue}`;
            const statusText = brushBPaintState ? `Brush B paint on (${servoValue}%)` : 'Brush B paint off';
            
            hairbrushController.sendCommand(command)
                .then(() => {
                    console.log(statusText);
                    addToCommandHistory(command, statusText);
                    
                    // Update button appearance
                    if (brushBPaintState) {
                        brushBPaintToggleBtn.classList.remove('btn-outline-primary');
                        brushBPaintToggleBtn.classList.add('btn-primary');
                        if (brushBPaintText) brushBPaintText.textContent = 'Paint Off';
                        if (brushBPaintIcon) {
                            brushBPaintIcon.classList.remove('bi-droplet');
                            brushBPaintIcon.classList.add('bi-droplet-fill');
                        }
                        // Show slider
                        if (brushBPaintSliderContainer) {
                            brushBPaintSliderContainer.style.display = 'flex';
                        }
                    } else {
                        brushBPaintToggleBtn.classList.remove('btn-primary');
                        brushBPaintToggleBtn.classList.add('btn-outline-primary');
                        if (brushBPaintText) brushBPaintText.textContent = 'Paint On';
                        if (brushBPaintIcon) {
                            brushBPaintIcon.classList.remove('bi-droplet-fill');
                            brushBPaintIcon.classList.add('bi-droplet');
                        }
                        // Hide slider
                        if (brushBPaintSliderContainer) {
                            brushBPaintSliderContainer.style.display = 'none';
                        }
                    }
                })
                .catch(handleError);
        });
        
        // Add event listener for slider
        if (brushBPaintSlider) {
            // Update display immediately on input
            brushBPaintSlider.addEventListener('input', () => {
                // Update the value display
                brushBPaintValue = parseInt(brushBPaintSlider.value);
                if (brushBPaintValueElem) {
                    brushBPaintValueElem.textContent = `${brushBPaintValue}%`;
                }
            });
            
            // Debounce the actual command sending on change
            brushBPaintSlider.addEventListener('change', debounce(() => {
                // Only send command if paint is on
                if (brushBPaintState) {
                    const command = `M280 P1 S${brushBPaintValue}`;
                    const statusText = `Brush B paint set to ${brushBPaintValue}%`;
                    
                    hairbrushController.sendCommand(command)
                        .then(() => {
                            console.log(statusText);
                            addToCommandHistory(command, statusText);
                        })
                        .catch(handleError);
                }
            }, 300));
        }
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
    
    // Clear history button
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearCommandHistory);
    }
    
    // Handle window resize
    window.addEventListener('resize', debounce(() => {
        setupVisualization();
    }, 250));
}

// Handle jog button click
function handleJogButtonClick(event) {
    const button = event.currentTarget;
    
    // If button is disabled, don't proceed
    if (button.disabled || button.classList.contains('disabled')) {
        console.log('Motion controls are disabled because motors are disabled');
        return;
    }
    
    const axis = button.getAttribute('data-axis');
    
    if (axis === 'home') {
        // Check if specific axis to home
        const homeAxis = button.getAttribute('data-home-axis');
        const command = homeAxis ? `G28 ${homeAxis}` : 'G28';
        
        // Home specified axis or all axes
        hairbrushController.sendCommand(command)
            .then(() => {
                console.log(`Homed ${homeAxis || 'all axes'}`);
                addToCommandHistory(command, `Homed ${homeAxis || 'all axes'}`);
            })
            .catch(handleError);
        return;
    }
    
    // Get selected distance and speed
    const selectedDistance = getSelectedDistance();
    const selectedSpeed = getSelectedSpeed();
    
    // Use the direction from the button but magnitude from the selected distance
    let direction = 1;
    if (button.getAttribute('data-distance')) {
        direction = Math.sign(parseFloat(button.getAttribute('data-distance')));
    }
    
    // Calculate final distance with direction
    const distance = direction * selectedDistance;
    
    // Send jog command
    hairbrushController.sendJog(axis, distance, selectedSpeed)
        .then(() => {
            console.log(`Jogged ${axis} by ${distance}mm at ${selectedSpeed}mm/min`);
            addToCommandHistory(`G1 ${axis}${distance} F${selectedSpeed}`, `Jogged ${axis} by ${distance}mm`);
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
    
    try {
        // Remove "no commands" message if present
        const noCommandsMsg = commandHistoryList.querySelector('.text-muted');
        if (noCommandsMsg && noCommandsMsg.parentNode === commandHistoryList) {
            commandHistoryList.removeChild(noCommandsMsg);
        }
        
        // Create history item
        const item = document.createElement('div');
        item.className = 'command-history-item';
        
        const commandEl = document.createElement('div');
        commandEl.className = 'command-text font-monospace small';
        commandEl.textContent = `> ${command}`;
        
        const resultEl = document.createElement('div');
        resultEl.className = `command-result small ${isError ? 'text-danger' : 'text-muted'}`;
        resultEl.textContent = result;
        
        item.appendChild(commandEl);
        item.appendChild(resultEl);
        
        // With flex-direction: column-reverse, prepending adds to the bottom visually
        // This is counterintuitive but works with our reversed flex container
        commandHistoryList.prepend(item);
        
        // Limit history to 100 items
        const children = Array.from(commandHistoryList.children);
        if (children.length > 100) {
            // Remove oldest items (now at the end due to column-reverse)
            for (let i = children.length - 1; i >= 100; i--) {
                if (children[i] && children[i].parentNode === commandHistoryList) {
                    commandHistoryList.removeChild(children[i]);
                }
            }
        }
        
        // Update command count
        updateCommandCount();
    } catch (e) {
        console.error('Error updating command history:', e);
        // Don't throw the error further to prevent UI disruption
    }
}

// Clear command history
function clearCommandHistory() {
    if (!commandHistoryList) return;
    
    try {
        // Remove all children
        while (commandHistoryList.firstChild) {
            commandHistoryList.removeChild(commandHistoryList.firstChild);
        }
        
        // Add "no commands" message
        const noCommandsMsg = document.createElement('div');
        noCommandsMsg.className = 'text-muted text-center py-2';
        noCommandsMsg.textContent = 'No commands sent yet';
        commandHistoryList.appendChild(noCommandsMsg);
        
        // Update command count
        updateCommandCount();
    } catch (e) {
        console.error('Error clearing command history:', e);
    }
}

// Update command count badge
function updateCommandCount() {
    if (!commandCountBadge || !commandHistoryList) return;
    
    try {
        // Count command items (excluding the "no commands" message)
        const count = commandHistoryList.querySelectorAll('.command-history-item').length;
        commandCountBadge.textContent = count;
        
        // Update badge color based on count
        if (count > 0) {
            commandCountBadge.className = 'badge bg-primary';
        } else {
            commandCountBadge.className = 'badge bg-secondary';
        }
    } catch (e) {
        console.error('Error updating command count:', e);
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
    
    // Check motor state
    if (data.motors_state !== undefined) {
        const newMotorsState = data.motors_state === 'enabled';
        
        // Only update if state has changed
        if (motorsEnabled !== newMotorsState) {
            motorsEnabled = newMotorsState;
            
            // Update button visibility
            if (disableMotorsBtn && enableMotorsBtn) {
                if (motorsEnabled) {
                    disableMotorsBtn.style.display = 'inline-block';
                    enableMotorsBtn.style.display = 'none';
                } else {
                    disableMotorsBtn.style.display = 'none';
                    enableMotorsBtn.style.display = 'inline-block';
                }
            }
            
            // Update motion control buttons
            disableMotionControls(!motorsEnabled);
        }
    }
    
    // Update position visualization
    if (data.position) {
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
        
        // Update canvas visualization if available
        if (window.machineVisualization && typeof window.machineVisualization.updatePosition === 'function') {
            window.machineVisualization.updatePosition(data.position);
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
            
            // Update toggle buttons to match machine state
            if (brushAAirToggleBtn) {
                if (data.brush_state.a.air) {
                    brushAAirToggleBtn.classList.remove('btn-outline-primary');
                    brushAAirToggleBtn.classList.add('btn-primary');
                    if (brushAAirText) brushAAirText.textContent = 'Air Off';
                } else {
                    brushAAirToggleBtn.classList.remove('btn-primary');
                    brushAAirToggleBtn.classList.add('btn-outline-primary');
                    if (brushAAirText) brushAAirText.textContent = 'Air On';
                }
            }
            
            if (brushAPaintToggleBtn) {
                // Update paint state
                brushAPaintState = data.brush_state.a.paint;
                
                if (brushAPaintState) {
                    brushAPaintToggleBtn.classList.remove('btn-outline-primary');
                    brushAPaintToggleBtn.classList.add('btn-primary');
                    if (brushAPaintText) brushAPaintText.textContent = 'Paint Off';
                    if (brushAPaintIcon) {
                        brushAPaintIcon.classList.remove('bi-droplet');
                        brushAPaintIcon.classList.add('bi-droplet-fill');
                    }
                    // Show slider
                    if (brushAPaintSliderContainer) {
                        brushAPaintSliderContainer.style.display = 'flex';
                    }
                } else {
                    brushAPaintToggleBtn.classList.remove('btn-primary');
                    brushAPaintToggleBtn.classList.add('btn-outline-primary');
                    if (brushAPaintText) brushAPaintText.textContent = 'Paint On';
                    if (brushAPaintIcon) {
                        brushAPaintIcon.classList.remove('bi-droplet-fill');
                        brushAPaintIcon.classList.add('bi-droplet');
                    }
                    // Hide slider
                    if (brushAPaintSliderContainer) {
                        brushAPaintSliderContainer.style.display = 'none';
                    }
                }
                
                // Update slider value display
                if (brushAPaintValueElem) {
                    brushAPaintValueElem.textContent = `${brushAPaintValue}%`;
                }
                if (brushAPaintSlider) {
                    brushAPaintSlider.value = brushAPaintValue;
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
            
            // Update toggle buttons to match machine state
            if (brushBAirToggleBtn) {
                if (data.brush_state.b.air) {
                    brushBAirToggleBtn.classList.remove('btn-outline-primary');
                    brushBAirToggleBtn.classList.add('btn-primary');
                    if (brushBAirText) brushBAirText.textContent = 'Air Off';
                } else {
                    brushBAirToggleBtn.classList.remove('btn-primary');
                    brushBAirToggleBtn.classList.add('btn-outline-primary');
                    if (brushBAirText) brushBAirText.textContent = 'Air On';
                }
            }
            
            if (brushBPaintToggleBtn) {
                // Update paint state
                brushBPaintState = data.brush_state.b.paint;
                
                if (brushBPaintState) {
                    brushBPaintToggleBtn.classList.remove('btn-outline-primary');
                    brushBPaintToggleBtn.classList.add('btn-primary');
                    if (brushBPaintText) brushBPaintText.textContent = 'Paint Off';
                    if (brushBPaintIcon) {
                        brushBPaintIcon.classList.remove('bi-droplet');
                        brushBPaintIcon.classList.add('bi-droplet-fill');
                    }
                    // Show slider
                    if (brushBPaintSliderContainer) {
                        brushBPaintSliderContainer.style.display = 'flex';
                    }
                } else {
                    brushBPaintToggleBtn.classList.remove('btn-primary');
                    brushBPaintToggleBtn.classList.add('btn-outline-primary');
                    if (brushBPaintText) brushBPaintText.textContent = 'Paint On';
                    if (brushBPaintIcon) {
                        brushBPaintIcon.classList.remove('bi-droplet-fill');
                        brushBPaintIcon.classList.add('bi-droplet');
                    }
                    // Hide slider
                    if (brushBPaintSliderContainer) {
                        brushBPaintSliderContainer.style.display = 'none';
                    }
                }
                
                // Update slider value display
                if (brushBPaintValueElem) {
                    brushBPaintValueElem.textContent = `${brushBPaintValue}%`;
                }
                if (brushBPaintSlider) {
                    brushBPaintSlider.value = brushBPaintValue;
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

// Store previous endstop states to prevent unnecessary UI updates
let previousEndstopStates = {
    x: { className: '', textContent: '' },
    y: { className: '', textContent: '' },
    z: { className: '', textContent: '' }
};

// Query endstop status
function queryEndstopStatus() {
    if (!socket || !socket.connected) {
        console.error('Socket not connected, cannot query endstops');
        return;
    }
    
    // Only show loading state on first load when elements are empty
    if (xEndstopStatus && !xEndstopStatus.textContent) {
        xEndstopStatus.className = 'endstop-value badge bg-secondary';
        xEndstopStatus.textContent = 'Checking...';
    }
    if (yEndstopStatus && !yEndstopStatus.textContent) {
        yEndstopStatus.className = 'endstop-value badge bg-secondary';
        yEndstopStatus.textContent = 'Checking...';
    }
    if (zEndstopStatus && !zEndstopStatus.textContent) {
        zEndstopStatus.className = 'endstop-value badge bg-secondary';
        zEndstopStatus.textContent = 'Checking...';
    }
    
    // Send M119 command to query endstops
    socket.emit('command', { command: 'M119' }, (response) => {
        if (response && response.status === 'success' && response.result && response.result.response) {
            updateEndstopUI(response.result.response);
        } else {
            console.error('Failed to query endstops:', response);
            
            // Only update UI to show error state if it's different from current state
            const errorClass = 'endstop-value badge bg-danger';
            const errorText = 'Error';
            
            if (xEndstopStatus && (xEndstopStatus.className !== errorClass || xEndstopStatus.textContent !== errorText)) {
                xEndstopStatus.className = errorClass;
                xEndstopStatus.textContent = errorText;
                previousEndstopStates.x = { className: errorClass, textContent: errorText };
            }
            if (yEndstopStatus && (yEndstopStatus.className !== errorClass || yEndstopStatus.textContent !== errorText)) {
                yEndstopStatus.className = errorClass;
                yEndstopStatus.textContent = errorText;
                previousEndstopStates.y = { className: errorClass, textContent: errorText };
            }
            if (zEndstopStatus && (zEndstopStatus.className !== errorClass || zEndstopStatus.textContent !== errorText)) {
                zEndstopStatus.className = errorClass;
                zEndstopStatus.textContent = errorText;
                previousEndstopStates.z = { className: errorClass, textContent: errorText };
            }
        }
    });
}

// Update endstop UI based on M119 response
function updateEndstopUI(response) {
    console.log('Endstop response:', response);
    
    // Parse the response
    // Example format: "Endstops - X: not stopped, Y: not stopped, Z: not stopped, Z probe: at min stop"
    // Use a more robust regex that handles the Z probe information
    const endstopRegex = /Endstops\s*-\s*X:\s*([^,]+),\s*Y:\s*([^,]+),\s*Z:\s*([^,]+)/i;
    const match = response.match(endstopRegex);
    
    if (match && match.length >= 4) {
        const xStatus = match[1].trim();
        const yStatus = match[2].trim();
        // Fix Z status parsing by removing anything after a comma if present
        let zStatus = match[3].trim();
        if (zStatus.includes(',')) {
            zStatus = zStatus.split(',')[0].trim();
        }
        
        // Update X endstop
        if (xEndstopStatus) {
            let newClass = '';
            let newText = '';
            
            if (xStatus.includes('min stop')) {
                newClass = 'endstop-value badge bg-danger';
                newText = 'TRIGGERED (min)';
            } else if (xStatus.includes('max stop')) {
                newClass = 'endstop-value badge bg-danger';
                newText = 'TRIGGERED (max)';
            } else if (xStatus.includes('not stopped')) {
                newClass = 'endstop-value badge bg-success';
                newText = 'Not triggered';
            } else {
                newClass = 'endstop-value badge bg-warning';
                newText = xStatus;
            }
            
            // Only update if there's a change
            if (previousEndstopStates.x.className !== newClass || previousEndstopStates.x.textContent !== newText) {
                xEndstopStatus.className = newClass;
                xEndstopStatus.textContent = newText;
                previousEndstopStates.x = { className: newClass, textContent: newText };
            }
        }
        
        // Update Y endstop
        if (yEndstopStatus) {
            let newClass = '';
            let newText = '';
            
            if (yStatus.includes('min stop')) {
                newClass = 'endstop-value badge bg-danger';
                newText = 'TRIGGERED (min)';
            } else if (yStatus.includes('max stop')) {
                newClass = 'endstop-value badge bg-danger';
                newText = 'TRIGGERED (max)';
            } else if (yStatus.includes('not stopped')) {
                newClass = 'endstop-value badge bg-success';
                newText = 'Not triggered';
            } else {
                newClass = 'endstop-value badge bg-warning';
                newText = yStatus;
            }
            
            // Only update if there's a change
            if (previousEndstopStates.y.className !== newClass || previousEndstopStates.y.textContent !== newText) {
                yEndstopStatus.className = newClass;
                yEndstopStatus.textContent = newText;
                previousEndstopStates.y = { className: newClass, textContent: newText };
            }
        }
        
        // Update Z endstop
        if (zEndstopStatus) {
            let newClass = '';
            let newText = '';
            
            if (zStatus.includes('min stop')) {
                newClass = 'endstop-value badge bg-danger';
                newText = 'TRIGGERED (min)';
            } else if (zStatus.includes('max stop')) {
                newClass = 'endstop-value badge bg-danger';
                newText = 'TRIGGERED (max)';
            } else if (zStatus.includes('not stopped')) {
                newClass = 'endstop-value badge bg-success';
                newText = 'Not triggered';
            } else {
                newClass = 'endstop-value badge bg-warning';
                newText = zStatus;
            }
            
            // Only update if there's a change
            if (previousEndstopStates.z.className !== newClass || previousEndstopStates.z.textContent !== newText) {
                zEndstopStatus.className = newClass;
                zEndstopStatus.textContent = newText;
                previousEndstopStates.z = { className: newClass, textContent: newText };
            }
        }
    } else {
        console.error('Failed to parse endstop response with primary regex:', response);
        
        // Try a fallback approach for more complex responses
        try {
            // Look for individual endstop patterns
            const xMatch = response.match(/X:\s*([^,]+)/i);
            const yMatch = response.match(/Y:\s*([^,]+)/i);
            const zMatch = response.match(/Z:\s*([^,]+)/i);
            
            // Update X endstop if found
            if (xMatch && xEndstopStatus) {
                const xStatus = xMatch[1].trim();
                let newClass = '';
                let newText = '';
                
                if (xStatus.includes('min stop')) {
                    newClass = 'endstop-value badge bg-danger';
                    newText = 'TRIGGERED (min)';
                } else if (xStatus.includes('max stop')) {
                    newClass = 'endstop-value badge bg-danger';
                    newText = 'TRIGGERED (max)';
                } else if (xStatus.includes('not stopped')) {
                    newClass = 'endstop-value badge bg-success';
                    newText = 'Not triggered';
                } else {
                    newClass = 'endstop-value badge bg-warning';
                    newText = xStatus;
                }
                
                // Only update if there's a change
                if (previousEndstopStates.x.className !== newClass || previousEndstopStates.x.textContent !== newText) {
                    xEndstopStatus.className = newClass;
                    xEndstopStatus.textContent = newText;
                    previousEndstopStates.x = { className: newClass, textContent: newText };
                }
            } else if (xEndstopStatus) {
                const newClass = 'endstop-value badge bg-warning';
                const newText = 'Parse error';
                
                // Only update if there's a change
                if (previousEndstopStates.x.className !== newClass || previousEndstopStates.x.textContent !== newText) {
                    xEndstopStatus.className = newClass;
                    xEndstopStatus.textContent = newText;
                    previousEndstopStates.x = { className: newClass, textContent: newText };
                }
            }
            
            // Update Y endstop if found
            if (yMatch && yEndstopStatus) {
                const yStatus = yMatch[1].trim();
                let newClass = '';
                let newText = '';
                
                if (yStatus.includes('min stop')) {
                    newClass = 'endstop-value badge bg-danger';
                    newText = 'TRIGGERED (min)';
                } else if (yStatus.includes('max stop')) {
                    newClass = 'endstop-value badge bg-danger';
                    newText = 'TRIGGERED (max)';
                } else if (yStatus.includes('not stopped')) {
                    newClass = 'endstop-value badge bg-success';
                    newText = 'Not triggered';
                } else {
                    newClass = 'endstop-value badge bg-warning';
                    newText = yStatus;
                }
                
                // Only update if there's a change
                if (previousEndstopStates.y.className !== newClass || previousEndstopStates.y.textContent !== newText) {
                    yEndstopStatus.className = newClass;
                    yEndstopStatus.textContent = newText;
                    previousEndstopStates.y = { className: newClass, textContent: newText };
                }
            } else if (yEndstopStatus) {
                const newClass = 'endstop-value badge bg-warning';
                const newText = 'Parse error';
                
                // Only update if there's a change
                if (previousEndstopStates.y.className !== newClass || previousEndstopStates.y.textContent !== newText) {
                    yEndstopStatus.className = newClass;
                    yEndstopStatus.textContent = newText;
                    previousEndstopStates.y = { className: newClass, textContent: newText };
                }
            }
            
            // Update Z endstop if found
            if (zMatch && zEndstopStatus) {
                let zStatus = zMatch[1].trim();
                // Remove anything after a comma if present
                if (zStatus.includes(',')) {
                    zStatus = zStatus.split(',')[0].trim();
                }
                
                let newClass = '';
                let newText = '';
                
                if (zStatus.includes('min stop')) {
                    newClass = 'endstop-value badge bg-danger';
                    newText = 'TRIGGERED (min)';
                } else if (zStatus.includes('max stop')) {
                    newClass = 'endstop-value badge bg-danger';
                    newText = 'TRIGGERED (max)';
                } else if (zStatus.includes('not stopped')) {
                    newClass = 'endstop-value badge bg-success';
                    newText = 'Not triggered';
                } else {
                    newClass = 'endstop-value badge bg-warning';
                    newText = zStatus;
                }
                
                // Only update if there's a change
                if (previousEndstopStates.z.className !== newClass || previousEndstopStates.z.textContent !== newText) {
                    zEndstopStatus.className = newClass;
                    zEndstopStatus.textContent = newText;
                    previousEndstopStates.z = { className: newClass, textContent: newText };
                }
            } else if (zEndstopStatus) {
                const newClass = 'endstop-value badge bg-warning';
                const newText = 'Parse error';
                
                // Only update if there's a change
                if (previousEndstopStates.z.className !== newClass || previousEndstopStates.z.textContent !== newText) {
                    zEndstopStatus.className = newClass;
                    zEndstopStatus.textContent = newText;
                    previousEndstopStates.z = { className: newClass, textContent: newText };
                }
            }
        } catch (e) {
            console.error('Failed to parse endstop response with fallback approach:', e);
            
            // Update UI to show error state, but only if there's a change
            const newClass = 'endstop-value badge bg-warning';
            const newText = 'Parse error';
            
            if (xEndstopStatus && (previousEndstopStates.x.className !== newClass || previousEndstopStates.x.textContent !== newText)) {
                xEndstopStatus.className = newClass;
                xEndstopStatus.textContent = newText;
                previousEndstopStates.x = { className: newClass, textContent: newText };
            }
            if (yEndstopStatus && (previousEndstopStates.y.className !== newClass || previousEndstopStates.y.textContent !== newText)) {
                yEndstopStatus.className = newClass;
                yEndstopStatus.textContent = newText;
                previousEndstopStates.y = { className: newClass, textContent: newText };
            }
            if (zEndstopStatus && (previousEndstopStates.z.className !== newClass || previousEndstopStates.z.textContent !== newText)) {
                zEndstopStatus.className = newClass;
                zEndstopStatus.textContent = newText;
                previousEndstopStates.z = { className: newClass, textContent: newText };
            }
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
    if (brushAAirToggleBtn) {
        brushAAirToggleBtn.addEventListener('click', function() {
            sendCommand('M42 P0 S1');
        });
    }
    
    if (brushAPaintToggleBtn) {
        brushAPaintToggleBtn.addEventListener('click', function() {
            sendCommand('M280 P0 S90');
        });
    }

    if (brushBAirToggleBtn) {
        brushBAirToggleBtn.addEventListener('click', function() {
            sendCommand('M42 P1 S1');
        });
    }
    
    if (brushBPaintToggleBtn) {
        brushBPaintToggleBtn.addEventListener('click', function() {
            sendCommand('M280 P1 S90');
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
/**
 * Settings JavaScript for H.Airbrush Web Controller
 * Handles loading, displaying, and saving settings to the server
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load settings from server
    loadSettings();
    
    // Set up form submissions
    document.getElementById('connection-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveConnectionSettings();
    });
    
    document.getElementById('machine-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveMachineSettings();
    });
    
    document.getElementById('brush-a-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveBrushSettings('a');
    });
    
    document.getElementById('brush-b-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveBrushSettings('b');
    });
    
    document.getElementById('advanced-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveAdvancedSettings();
    });
    
    // Test connection button
    document.getElementById('test-connection').addEventListener('click', testConnection);
    
    // Duet Web Control button
    const openDwcBtn = document.getElementById('open-dwc');
    if (openDwcBtn) {
        openDwcBtn.addEventListener('click', openDWC);
    }
    
    // Set up brush test buttons
    setupBrushTestButtons('a');
    setupBrushTestButtons('b');
});

/**
 * Open Duet Web Control in a new window
 */
function openDWC() {
    // Get the current Duet host from the input field
    const duetHost = document.getElementById('duet-host').value;
    
    // Ensure we have a valid host
    if (!duetHost) {
        showToast('Please enter a valid Duet host address', 'error');
        return;
    }
    
    // Construct the URL (using protocol-relative URL if the host doesn't include http/https)
    let url = duetHost;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'http://' + url;
    }
    
    // Open in a new window/tab
    window.open(url, '_blank');
}

/**
 * Set up brush test buttons for a specific brush
 * @param {string} brush - Brush identifier ('a' or 'b')
 */
function setupBrushTestButtons(brush) {
    const testMinBtn = document.getElementById(`brush-${brush}-test-min`);
    const testMaxBtn = document.getElementById(`brush-${brush}-test-max`);
    const servoPin = brush === 'a' ? 0 : 1;
    const airPin = brush === 'a' ? 0 : 1;
    
    if (testMinBtn) {
        // Test Min button - mousedown activates, mouseup/mouseleave deactivates
        testMinBtn.addEventListener('mousedown', function() {
            const minValue = parseInt(document.getElementById(`brush-${brush}-paint-min`).value);
            testPaintFlow(servoPin, airPin, minValue, true);
        });
        
        testMinBtn.addEventListener('mouseup', function() {
            testPaintFlow(servoPin, airPin, null, false);
        });
        
        testMinBtn.addEventListener('mouseleave', function() {
            testPaintFlow(servoPin, airPin, null, false);
        });
    }
    
    if (testMaxBtn) {
        // Test Max button - mousedown activates, mouseup/mouseleave deactivates
        testMaxBtn.addEventListener('mousedown', function() {
            const maxValue = parseInt(document.getElementById(`brush-${brush}-paint-max`).value);
            testPaintFlow(servoPin, airPin, maxValue, true);
        });
        
        testMaxBtn.addEventListener('mouseup', function() {
            testPaintFlow(servoPin, airPin, null, false);
        });
        
        testMaxBtn.addEventListener('mouseleave', function() {
            testPaintFlow(servoPin, airPin, null, false);
        });
    }
}

/**
 * Test paint flow by controlling servo and air
 * @param {number} servoPin - Servo pin number
 * @param {number} airPin - Air pin number
 * @param {number|null} servoValue - Servo angle value (null to keep current)
 * @param {boolean} airOn - Whether to turn air on or off
 */
function testPaintFlow(servoPin, airPin, servoValue, airOn) {
    // Use global WebSocket manager if available
    if (window.HairbrushWebSocket) {
        // Send servo command if a value is provided
        if (servoValue !== null) {
            window.HairbrushWebSocket.sendCommand(`M280 P${servoPin} S${servoValue}`)
                .catch(error => {
                    console.error('Error sending servo command:', error);
                    showToast('Error sending servo command', 'error');
                });
        }
        
        // Send air command
        const airCommand = airOn ? `M42 P${airPin} S1` : `M42 P${airPin} S0`;
        window.HairbrushWebSocket.sendCommand(airCommand)
            .catch(error => {
                console.error('Error sending air command:', error);
                showToast('Error sending air command', 'error');
            });
    } else {
        // Fallback to direct fetch API
        fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                commands: [
                    servoValue !== null ? `M280 P${servoPin} S${servoValue}` : null,
                    airOn ? `M42 P${airPin} S1` : `M42 P${airPin} S0`
                ].filter(Boolean)
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to send test command');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error testing paint flow:', error);
            showToast('Error testing paint flow', 'error');
        });
    }
}

/**
 * Load settings from the server
 */
function loadSettings() {
    console.log('Loading settings from server...');
    
    // Get all settings from the server
    fetch('/api/settings')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load settings');
            }
            return response.json();
        })
        .then(settings => {
            console.log('Settings loaded:', settings);
            
            // Populate connection settings
            if (settings.duet) {
                document.getElementById('duet-host').value = settings.duet.host || '';
                document.getElementById('duet-http-port').value = settings.duet.http_port || 80;
                document.getElementById('connection-timeout').value = settings.duet.connect_timeout || 5;
            }
            
            // Populate machine settings
            if (settings.machine) {
                document.getElementById('max-x').value = settings.machine.max_x || 841;
                document.getElementById('max-y').value = settings.machine.max_y || 1189;
                document.getElementById('max-z').value = settings.machine.max_z || 50;
                document.getElementById('default-feedrate').value = settings.machine.default_feedrate || 1000;
                document.getElementById('z-feedrate').value = settings.machine.z_feedrate || 500;
                document.getElementById('travel-height').value = settings.machine.travel_height || 10;
            }
            
            // Populate brush A settings
            if (settings.brushes && settings.brushes.a) {
                document.getElementById('brush-a-offset-x').value = settings.brushes.a.offset_x || 0;
                document.getElementById('brush-a-offset-y').value = settings.brushes.a.offset_y || 0;
                document.getElementById('brush-a-air-pin').value = 0; // Always 0 for brush A
                document.getElementById('brush-a-paint-servo').value = 0; // Always 0 for brush A
                
                // Set paint servo limits
                document.getElementById('brush-a-paint-min').value = settings.brushes.a.paint_min || 0;
                document.getElementById('brush-a-paint-max').value = settings.brushes.a.paint_max || 90;
            }
            
            // Populate brush B settings
            if (settings.brushes && settings.brushes.b) {
                document.getElementById('brush-b-offset-x').value = settings.brushes.b.offset_x || 50;
                document.getElementById('brush-b-offset-y').value = settings.brushes.b.offset_y || 50;
                document.getElementById('brush-b-air-pin').value = 1; // Always 1 for brush B
                document.getElementById('brush-b-paint-servo').value = 1; // Always 1 for brush B
                
                // Set paint servo limits
                document.getElementById('brush-b-paint-min').value = settings.brushes.b.paint_min || 0;
                document.getElementById('brush-b-paint-max').value = settings.brushes.b.paint_max || 90;
            }
            
            // Populate advanced settings
            if (settings.web) {
                document.getElementById('debug-mode').checked = settings.web.debug || false;
            }
            
            // These are not in the config but might be added later
            document.getElementById('command-timeout').value = settings.command_timeout || 10;
            document.getElementById('status-interval').value = settings.status_interval || 500;
            
            showToast('Settings loaded successfully');
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showToast('Error loading settings', 'error');
        });
}

/**
 * Save connection settings to the server
 */
function saveConnectionSettings() {
    const settings = {
        duet: {
            host: document.getElementById('duet-host').value,
            http_port: parseInt(document.getElementById('duet-http-port').value),
            connect_timeout: parseInt(document.getElementById('connection-timeout').value)
        }
    };
    
    console.log('Saving connection settings:', settings);
    
    saveSettings(settings, 'Connection settings saved successfully');
}

/**
 * Save machine settings to the server
 */
function saveMachineSettings() {
    const settings = {
        machine: {
            max_x: parseFloat(document.getElementById('max-x').value),
            max_y: parseFloat(document.getElementById('max-y').value),
            max_z: parseFloat(document.getElementById('max-z').value),
            default_feedrate: parseFloat(document.getElementById('default-feedrate').value),
            z_feedrate: parseFloat(document.getElementById('z-feedrate').value),
            travel_height: parseFloat(document.getElementById('travel-height').value)
        }
    };
    
    console.log('Saving machine settings:', settings);
    
    saveSettings(settings, 'Machine settings saved successfully');
}

/**
 * Save brush settings to the server
 * @param {string} brush - Brush identifier ('a' or 'b')
 */
function saveBrushSettings(brush) {
    const prefix = `brush-${brush}`;
    const servoPin = brush === 'a' ? 0 : 1;
    
    // Create settings object with the brush key
    const settings = {
        brushes: {}
    };
    
    // Add the specific brush settings
    settings.brushes[brush] = {
        offset_x: parseFloat(document.getElementById(`${prefix}-offset-x`).value),
        offset_y: parseFloat(document.getElementById(`${prefix}-offset-y`).value),
        paint_min: parseInt(document.getElementById(`${prefix}-paint-min`).value),
        paint_max: parseInt(document.getElementById(`${prefix}-paint-max`).value)
    };
    
    console.log(`Saving brush ${brush} settings:`, settings);
    
    // Save settings and reset servo to minimum position when done
    saveSettings(settings, `Brush ${brush.toUpperCase()} settings saved successfully`)
        .then(() => {
            // Reset servo to minimum position and ensure air is off
            const minValue = parseInt(document.getElementById(`${prefix}-paint-min`).value);
            const airPin = brush === 'a' ? 0 : 1;
            
            // Send commands to reset servo and turn off air
            if (window.HairbrushWebSocket) {
                window.HairbrushWebSocket.sendCommand(`M280 P${servoPin} S${minValue}`)
                    .then(() => window.HairbrushWebSocket.sendCommand(`M42 P${airPin} S0`))
                    .catch(error => {
                        console.error('Error resetting servo position:', error);
                    });
            }
        });
}

/**
 * Save advanced settings to the server
 */
function saveAdvancedSettings() {
    const settings = {
        web: {
            debug: document.getElementById('debug-mode').checked
        },
        command_timeout: parseInt(document.getElementById('command-timeout').value),
        status_interval: parseInt(document.getElementById('status-interval').value)
    };
    
    console.log('Saving advanced settings:', settings);
    
    saveSettings(settings, 'Advanced settings saved successfully');
}

/**
 * Generic function to save settings to the server
 * @param {Object} settings - Settings object to save
 * @param {string} successMessage - Message to show on success
 * @returns {Promise} Promise that resolves when settings are saved
 */
function saveSettings(settings, successMessage) {
    return fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to save settings');
        }
        return response.json();
    })
    .then(data => {
        console.log('Settings saved:', data);
        showToast(successMessage);
        
        // If we updated brush offsets, update the visualization if available
        if (settings.brushes && window.machineVisualization) {
            const config = {};
            
            if (settings.brushes.b) {
                config.brushBOffsetX = settings.brushes.b.offset_x;
                config.brushBOffsetY = settings.brushes.b.offset_y;
            }
            
            window.machineVisualization.updateConfig(config);
        }
        
        return data; // Return data for chaining
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showToast('Error saving settings: ' + error.message, 'error');
        throw error; // Re-throw for promise chaining
    });
}

/**
 * Test connection to the Duet board
 */
function testConnection() {
    const host = document.getElementById('duet-host').value;
    const port = document.getElementById('duet-http-port').value;
    
    console.log(`Testing connection to ${host}:${port}...`);
    showToast(`Testing connection to ${host}:${port}...`, 'info');
    
    // Send test connection request
    fetch('/api/connection/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            host: host,
            port: port
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Connection test failed');
        }
        return response.json();
    })
    .then(data => {
        console.log('Connection test result:', data);
        if (data.success) {
            showToast(`Successfully connected to ${host}:${port}`, 'success');
        } else {
            showToast(`Connection failed: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error testing connection:', error);
        showToast(`Connection error: ${error.message}`, 'error');
    });
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (success, error, info)
 */
function showToast(message, type = 'success') {
    // Check if we have the toast container
    let toastContainer = document.getElementById('toast-container');
    
    // If not, create it
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create a unique ID for this toast
    const toastId = 'toast-' + Date.now();
    
    // Set the appropriate background color based on type
    let bgClass = 'bg-success';
    if (type === 'error') bgClass = 'bg-danger';
    if (type === 'info') bgClass = 'bg-info';
    
    // Create the toast HTML
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">H.Airbrush Controller</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add the toast to the container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize the toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    // Show the toast
    toast.show();
    
    // Remove the toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
} 
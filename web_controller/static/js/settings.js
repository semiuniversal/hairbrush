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
});

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
                document.getElementById('duet-port').value = settings.duet.telnet_port || 23;
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
                document.getElementById('brush-a-paint-angle').value = 90; // Default angle
            }
            
            // Populate brush B settings
            if (settings.brushes && settings.brushes.b) {
                document.getElementById('brush-b-offset-x').value = settings.brushes.b.offset_x || 50;
                document.getElementById('brush-b-offset-y').value = settings.brushes.b.offset_y || 50;
                document.getElementById('brush-b-air-pin').value = 1; // Always 1 for brush B
                document.getElementById('brush-b-paint-servo').value = 1; // Always 1 for brush B
                document.getElementById('brush-b-paint-angle').value = 90; // Default angle
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
            telnet_port: parseInt(document.getElementById('duet-port').value),
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
    
    // Create settings object with the brush key
    const settings = {
        brushes: {}
    };
    
    // Add the specific brush settings
    settings.brushes[brush] = {
        offset_x: parseFloat(document.getElementById(`${prefix}-offset-x`).value),
        offset_y: parseFloat(document.getElementById(`${prefix}-offset-y`).value)
    };
    
    console.log(`Saving brush ${brush} settings:`, settings);
    
    saveSettings(settings, `Brush ${brush.toUpperCase()} settings saved successfully`);
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
 */
function saveSettings(settings, successMessage) {
    fetch('/api/settings', {
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
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showToast('Error saving settings: ' + error.message, 'error');
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
/**
 * Connection management for H.Airbrush Controller
 * Handles device connection, IP address management, and connection status
 */

// Connection elements
const connectButton = document.getElementById('connect-button');
const connectionText = document.getElementById('connection-text');
const connectionDot = document.getElementById('connection-indicator');
const deviceIpDisplay = document.getElementById('device-ip-display');

// Connection dialog elements
const connectionModal = new bootstrap.Modal(document.getElementById('connection-modal'));
const deviceIpInput = document.getElementById('device-ip');
const devicePasswordInput = document.getElementById('device-password');
const connectConfirm = document.getElementById('connect-confirm');
const ipHistory = document.getElementById('ip-history');

// Connection states
const CONNECTION_STATES = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    ERROR: 'error'
};

// Connection timeout (in milliseconds)
const CONNECTION_TIMEOUT = 10000;
let connectionTimeoutId = null;
let currentConnectionState = CONNECTION_STATES.DISCONNECTED;
let ipAddresses = [];
let currentIp = '';

// Initialize connection handling
document.addEventListener('DOMContentLoaded', () => {
    loadConnectionStatus();
    loadIpHistory();
    updateConnectionState(CONNECTION_STATES.DISCONNECTED);
    
    // Set up event listeners
    connectButton.addEventListener('click', handleConnectButtonClick);
    connectConfirm.addEventListener('click', handleConnectConfirm);
    
    // Listen for IP selection from history
    ipHistory.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('dropdown-item')) {
            deviceIpInput.value = e.target.textContent;
        }
    });
    
    // Add connection listener to the global WebSocket manager
    if (window.HairbrushWebSocket) {
        window.HairbrushWebSocket.addConnectionListener(handleConnectionChange);
    }
});

/**
 * Handle connection status changes from the WebSocket manager
 */
function handleConnectionChange(isConnected, error) {
    if (isConnected) {
        // Check connection status with the device
        loadConnectionStatus();
    } else {
        // Update UI to show disconnected state
        updateConnectionState(CONNECTION_STATES.DISCONNECTED);
        deviceIpDisplay.textContent = '';
        
        // If there's an error, show it
        if (error) {
            showConnectionError(`Connection error: ${error.message || 'Unknown error'}`);
        }
    }
}

/**
 * Load current connection status from server
 */
function loadConnectionStatus() {
    fetch('/api/connection')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.connected) {
                currentIp = data.host || data.ip; // Handle both host and ip fields
                deviceIpDisplay.textContent = currentIp;
                updateConnectionState(CONNECTION_STATES.CONNECTED);
            } else {
                updateConnectionState(CONNECTION_STATES.DISCONNECTED);
            }
        })
        .catch(error => {
            console.error('Error loading connection status:', error);
            updateConnectionState(CONNECTION_STATES.DISCONNECTED);
        });
}

/**
 * Handle connect button click
 */
function handleConnectButtonClick() {
    if (currentConnectionState === CONNECTION_STATES.CONNECTED) {
        // Disconnect if already connected
        disconnectFromDevice();
    } else {
        // Show connection dialog
        if (!currentIp) {
            // If no IP is set, show the dialog
            connectionModal.show();
        } else {
            // If IP is already set, try to connect directly
            // We don't have the password here, but it might be saved in the server config
            connectToDevice(currentIp, '');
        }
    }
}

/**
 * Handle connect confirmation from dialog
 */
function handleConnectConfirm() {
    const ip = deviceIpInput.value.trim();
    const password = devicePasswordInput.value;
    
    if (ip) {
        connectionModal.hide();
        connectToDevice(ip, password);
    }
}

/**
 * Connect to device with given IP
 * @param {string} ip - Device IP address
 * @param {string} password - Device password (optional)
 */
function connectToDevice(ip, password = '') {
    // Update state to connecting
    updateConnectionState(CONNECTION_STATES.CONNECTING);
    
    // Set current IP
    currentIp = ip;
    deviceIpDisplay.textContent = ip;
    
    // Set connection timeout
    connectionTimeoutId = setTimeout(() => {
        // If connection times out
        updateConnectionState(CONNECTION_STATES.ERROR);
        showConnectionError('Connection timeout');
    }, CONNECTION_TIMEOUT);
    
    // Use the global WebSocket manager to connect to the device
    if (window.HairbrushWebSocket) {
        window.HairbrushWebSocket.connectToDevice(ip, 80, password)
            .then(response => {
                // Clear timeout
                clearTimeout(connectionTimeoutId);
                
                // Connection successful
                updateConnectionState(CONNECTION_STATES.CONNECTED);
                // Refresh IP history
                loadIpHistory();
            })
            .catch(error => {
                // Clear timeout
                clearTimeout(connectionTimeoutId);
                
                // Connection failed
                updateConnectionState(CONNECTION_STATES.ERROR);
                showConnectionError(error.message || 'Failed to connect');
            });
    } else {
        // Fallback to direct socket.io if global manager is not available
        socket.emit('connect_device', { host: ip, port: 80, password: password }, (response) => {
            // Clear timeout
            clearTimeout(connectionTimeoutId);
            
            if (response && response.status === 'success') {
                // Connection successful
                updateConnectionState(CONNECTION_STATES.CONNECTED);
                // Refresh IP history
                loadIpHistory();
            } else {
                // Connection failed
                updateConnectionState(CONNECTION_STATES.ERROR);
                showConnectionError(response?.message || 'Failed to connect');
            }
        });
    }
}

/**
 * Disconnect from device
 */
function disconnectFromDevice() {
    if (window.HairbrushWebSocket) {
        window.HairbrushWebSocket.disconnectFromDevice()
            .then(response => {
                updateConnectionState(CONNECTION_STATES.DISCONNECTED);
                deviceIpDisplay.textContent = '';
            })
            .catch(error => {
                showConnectionError(error.message || 'Failed to disconnect');
            });
    } else {
        // Fallback to direct socket.io if global manager is not available
        socket.emit('disconnect_device', {}, (response) => {
            updateConnectionState(CONNECTION_STATES.DISCONNECTED);
            deviceIpDisplay.textContent = '';
        });
    }
}

/**
 * Update connection state and UI
 * @param {string} state - Connection state
 */
function updateConnectionState(state) {
    currentConnectionState = state;
    
    // Remove all state classes
    connectButton.classList.remove(
        'connection-state-disconnected',
        'connection-state-connecting',
        'connection-state-connected',
        'connection-state-error'
    );
    
    // Add appropriate state class
    connectButton.classList.add(`connection-state-${state}`);
    
    // Update button text
    switch (state) {
        case CONNECTION_STATES.DISCONNECTED:
            connectionText.textContent = 'Connect';
            connectButton.classList.remove('btn-outline-success', 'btn-outline-warning', 'btn-outline-danger');
            connectButton.classList.add('btn-outline-light');
            break;
        case CONNECTION_STATES.CONNECTING:
            connectionText.textContent = 'Connecting...';
            connectButton.classList.remove('btn-outline-light', 'btn-outline-success', 'btn-outline-danger');
            connectButton.classList.add('btn-outline-warning');
            break;
        case CONNECTION_STATES.CONNECTED:
            connectionText.textContent = 'Disconnect';
            connectButton.classList.remove('btn-outline-light', 'btn-outline-warning', 'btn-outline-danger');
            connectButton.classList.add('btn-outline-success');
            break;
        case CONNECTION_STATES.ERROR:
            connectionText.textContent = 'Retry';
            connectButton.classList.remove('btn-outline-light', 'btn-outline-warning', 'btn-outline-success');
            connectButton.classList.add('btn-outline-danger');
            break;
    }
}

/**
 * Show connection error message
 * @param {string} message - Error message
 */
function showConnectionError(message) {
    // Create toast notification
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '11';
    
    const toastElement = document.createElement('div');
    toastElement.className = 'toast';
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    toastElement.innerHTML = `
        <div class="toast-header bg-danger text-white">
            <strong class="me-auto">Connection Error</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toastElement);
    document.body.appendChild(toastContainer);
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toastContainer);
    });
}

/**
 * Load IP address history from server
 */
function loadIpHistory() {
    fetch('/api/connection/history')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            ipAddresses = data || [];
            updateIpHistoryDropdown();
        })
        .catch(error => {
            console.error('Error loading IP history:', error);
            ipAddresses = [];
            updateIpHistoryDropdown();
        });
}

/**
 * Update IP history dropdown
 */
function updateIpHistoryDropdown() {
    // Clear existing items
    ipHistory.innerHTML = '';
    
    if (ipAddresses.length === 0) {
        // No history
        const noHistory = document.createElement('li');
        noHistory.innerHTML = '<span class="dropdown-item text-muted">No history</span>';
        ipHistory.appendChild(noHistory);
    } else {
        // Add history items
        ipAddresses.forEach(ip => {
            const item = document.createElement('li');
            item.innerHTML = `<a class="dropdown-item" href="#">${ip}</a>`;
            ipHistory.appendChild(item);
        });
    }
}

// Additional socket event handlers for connection status
socket.on('connect', () => {
    // Check connection status when socket connects
    console.log('Socket connected - checking connection status');
    loadConnectionStatus();
});

socket.on('disconnect', () => {
    // Update UI to disconnected state
    console.log('Socket disconnected - updating UI');
    updateConnectionState(CONNECTION_STATES.DISCONNECTED);
    deviceIpDisplay.textContent = '';
    
    // Show connection error message
    showConnectionError('Connection to server lost. Please refresh the page.');
});

// Handle connection errors
socket.on('connect_error', (error) => {
    console.error('Socket connection error:', error);
    updateConnectionState(CONNECTION_STATES.ERROR);
    showConnectionError('Connection error: ' + (error.message || 'Unknown error'));
});

// Handle reconnection attempts
socket.on('reconnecting', (attemptNumber) => {
    console.log(`Socket reconnecting (attempt ${attemptNumber})...`);
    updateConnectionState(CONNECTION_STATES.CONNECTING);
});

// Handle successful reconnection
socket.on('reconnect', (attemptNumber) => {
    console.log(`Socket reconnected after ${attemptNumber} attempts`);
    loadConnectionStatus(); // Refresh connection status
});

// Handle reconnection failure
socket.on('reconnect_failed', () => {
    console.error('Socket reconnection failed after multiple attempts');
    updateConnectionState(CONNECTION_STATES.ERROR);
    showConnectionError('Failed to reconnect after multiple attempts. Please refresh the page.');
});

// Handle connection status updates from server
socket.on('connection_status', (data) => {
    if (data.connected) {
        updateConnectionState(CONNECTION_STATES.CONNECTED);
        currentIp = data.ip || data.host;
        deviceIpDisplay.textContent = currentIp;
    } else {
        updateConnectionState(CONNECTION_STATES.DISCONNECTED);
        deviceIpDisplay.textContent = '';
        
        // If there's an error message, show it
        if (data.error) {
            showConnectionError(data.error);
        }
    }
}); 
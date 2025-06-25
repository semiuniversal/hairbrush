/**
 * WebSocket client for H.Airbrush Web Controller
 * Handles real-time communication with the server
 */

// Global WebSocket connection manager
window.HairbrushWebSocket = (function() {
    // Private variables
    let socket = null;
    let connected = false;
    let statusUpdateInterval = null;
    let reconnectingNotificationShown = false;
    let connectionListeners = [];
    let statusListeners = [];
    let jobListeners = [];
    let commandCallbacks = {};
    let commandCounter = 0;
    
    // Initialize socket connection
    function initialize() {
        if (socket) {
            console.log('Socket already initialized');
            return;
        }
        
        console.log('Initializing socket connection');
        
        // Create socket with reconnection options
        socket = io({
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            timeout: 20000
        });
        
        // Set up event listeners
        socket.on('connect', handleConnect);
        socket.on('disconnect', handleDisconnect);
        socket.on('connect_error', handleConnectError);
        socket.on('reconnecting', handleReconnecting);
        socket.on('reconnect', handleReconnect);
        socket.on('reconnect_failed', handleReconnectFailed);
        socket.on('status_update', handleStatusUpdate);
        socket.on('job_update', handleJobUpdate);
        socket.on('connection_status', handleConnectionStatus);
    }
    
    // Connection event handlers
    function handleConnect() {
        console.log('Connected to server');
        connected = true;
        reconnectingNotificationShown = false;
        
        // Start status updates
        startStatusUpdates();
        
        // Emit initial status request
        requestMachineStatus();
        
        // Notify listeners
        notifyConnectionListeners(true);
    }
    
    function handleDisconnect() {
        console.log('Disconnected from server');
        connected = false;
        
        // Stop status updates
        stopStatusUpdates();
        
        // Notify listeners
        notifyConnectionListeners(false);
        
        // Show connection error message
        showConnectionError('Connection to server lost. Please refresh the page.');
    }
    
    function handleConnectError(error) {
        console.error('Connection error:', error);
        connected = false;
        
        // Notify listeners
        notifyConnectionListeners(false, error);
    }
    
    function handleReconnecting(attemptNumber) {
        console.log(`Attempting to reconnect (${attemptNumber})...`);
        
        if (!reconnectingNotificationShown) {
            showReconnectingNotification(attemptNumber);
            reconnectingNotificationShown = true;
        }
    }
    
    function handleReconnect(attemptNumber) {
        console.log(`Reconnected after ${attemptNumber} attempts`);
        connected = true;
        reconnectingNotificationShown = false;
        
        // Notify listeners
        notifyConnectionListeners(true);
    }
    
    function handleReconnectFailed() {
        console.error('Failed to reconnect after multiple attempts');
        showConnectionError('Failed to reconnect to server after multiple attempts. Please refresh the page.');
    }
    
    // Status and job update handlers
    function handleStatusUpdate(data) {
        console.log('Status update:', data);
        notifyStatusListeners(data);
    }
    
    function handleJobUpdate(data) {
        console.log('Job update:', data);
        notifyJobListeners(data);
    }
    
    function handleConnectionStatus(data) {
        console.log('Connection status update:', data);
        // This is handled by connection.js
    }
    
    // Notify listeners
    function notifyConnectionListeners(isConnected, error = null) {
        connectionListeners.forEach(listener => {
            try {
                listener(isConnected, error);
            } catch (e) {
                console.error('Error in connection listener:', e);
            }
        });
    }
    
    function notifyStatusListeners(data) {
        // Ensure data has expected properties to prevent errors
        const safeData = {
            position: data?.position || {},
            state: data?.state || 'unknown',
            is_homed: data?.is_homed !== undefined ? data.is_homed : false,
            motors_state: data?.motors_state || 'unknown',
            brush_state: data?.brush_state || {
                a: { air: false, paint: false },
                b: { air: false, paint: false }
            }
        };
        
        // Notify all status listeners
        statusListeners.forEach(listener => {
            try {
                listener(safeData);
            } catch (error) {
                console.error('Error in status listener:', error);
            }
        });
    }
    
    function notifyJobListeners(data) {
        jobListeners.forEach(listener => {
            try {
                listener(data);
            } catch (e) {
                console.error('Error in job listener:', e);
            }
        });
    }
    
    // Status updates
    function startStatusUpdates() {
        // Clear existing interval if any
        stopStatusUpdates();
        
        // Request status every 2 seconds
        statusUpdateInterval = setInterval(() => {
            if (connected) {
                requestMachineStatus();
            }
        }, 2000);
    }
    
    function stopStatusUpdates() {
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
            statusUpdateInterval = null;
        }
    }
    
    // Request machine status
    function requestMachineStatus() {
        if (!connected) {
            console.warn('Cannot request machine status: not connected to server');
            return Promise.reject(new Error('Not connected to server'));
        }
        
        return new Promise((resolve, reject) => {
            socket.emit('get_status', {}, (response) => {
                if (response && response.status === 'success') {
                    notifyStatusListeners(response.data);
                    resolve(response.data);
                } else {
                    reject(new Error(response?.message || 'Failed to get status'));
                }
            });
        });
    }
    
    // Send command with error handling
    function sendCommand(command) {
        if (!connected) {
            console.error('Not connected to server');
            showConnectionError('Not connected to server. Cannot send command.');
            return Promise.reject(new Error('Not connected to server'));
        }
        
        return new Promise((resolve, reject) => {
            // Set a timeout for the command
            const timeout = setTimeout(() => {
                reject(new Error('Command timed out'));
            }, 10000);
            
            socket.emit('command', { command }, (response) => {
                clearTimeout(timeout);
                
                if (response && response.status === 'success') {
                    resolve(response.result);
                } else {
                    reject(new Error(response?.message || 'Command failed'));
                }
            });
        });
    }
    
    // Send jog command with error handling
    function sendJog(axis, distance, speed) {
        if (!connected) {
            console.error('Not connected to server');
            showConnectionError('Not connected to server. Cannot send jog command.');
            return Promise.reject(new Error('Not connected to server'));
        }
        
        return new Promise((resolve, reject) => {
            // Set a timeout for the command
            const timeout = setTimeout(() => {
                reject(new Error('Jog command timed out'));
            }, 10000);
            
            socket.emit('jog', { axis, distance, speed }, (response) => {
                clearTimeout(timeout);
                
                if (response && response.status === 'success') {
                    resolve(response.result);
                } else {
                    reject(new Error(response?.message || 'Jog command failed'));
                }
            });
        });
    }
    
    // Send job control command with error handling
    function sendJobControl(action, job_id) {
        if (!connected) {
            console.error('Not connected to server');
            showConnectionError('Not connected to server. Cannot send job control command.');
            return Promise.reject(new Error('Not connected to server'));
        }
        
        return new Promise((resolve, reject) => {
            // Set a timeout for the command
            const timeout = setTimeout(() => {
                reject(new Error('Job control command timed out'));
            }, 10000);
            
            socket.emit('job_control', { action, job_id }, (response) => {
                clearTimeout(timeout);
                
                if (response && response.status === 'success') {
                    resolve(response.result);
                } else {
                    reject(new Error(response?.message || 'Job control failed'));
                }
            });
        });
    }
    
    // Connect to device
    function connectToDevice(host, port, password) {
        if (!connected) {
            console.error('Not connected to server');
            return Promise.reject(new Error('Not connected to server'));
        }
        
        return new Promise((resolve, reject) => {
            // Set a timeout for the command
            const timeout = setTimeout(() => {
                reject(new Error('Connect command timed out'));
            }, 10000);
            
            socket.emit('connect_device', { host, port, password }, (response) => {
                clearTimeout(timeout);
                
                if (response && response.status === 'success') {
                    resolve(response);
                } else {
                    reject(new Error(response?.message || 'Connect failed'));
                }
            });
        });
    }
    
    // Disconnect from device
    function disconnectFromDevice() {
        if (!connected) {
            console.error('Not connected to server');
            return Promise.reject(new Error('Not connected to server'));
        }
        
        return new Promise((resolve, reject) => {
            // Set a timeout for the command
            const timeout = setTimeout(() => {
                reject(new Error('Disconnect command timed out'));
            }, 10000);
            
            socket.emit('disconnect_device', {}, (response) => {
                clearTimeout(timeout);
                
                if (response && response.status === 'success') {
                    resolve(response);
                } else {
                    reject(new Error(response?.message || 'Disconnect failed'));
                }
            });
        });
    }
    
    // Show reconnecting notification
    function showReconnectingNotification(attemptNumber) {
        // Create toast notification for reconnection attempts
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '11';
        
        const toastElement = document.createElement('div');
        toastElement.className = 'toast';
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        
        toastElement.innerHTML = `
            <div class="toast-header bg-warning text-white">
                <strong class="me-auto">Connection Warning</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                Connection to server lost. Attempting to reconnect...
            </div>
        `;
        
        toastContainer.appendChild(toastElement);
        document.body.appendChild(toastContainer);
        
        const toast = new bootstrap.Toast(toastElement, {
            autohide: false
        });
        toast.show();
        
        // Store the toast element ID to remove it later if needed
        window.reconnectingToastElement = toastElement;
    }
    
    // Show connection error
    function showConnectionError(message) {
        // Create toast notification for connection errors
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
    
    // Public API
    return {
        initialize: initialize,
        isConnected: function() { return connected; },
        
        // Command functions
        sendCommand: sendCommand,
        sendJog: sendJog,
        sendJobControl: sendJobControl,
        requestMachineStatus: requestMachineStatus,
        connectToDevice: connectToDevice,
        disconnectFromDevice: disconnectFromDevice,
        
        // Event listeners
        addConnectionListener: function(listener) {
            connectionListeners.push(listener);
            // Immediately notify with current status
            if (listener) listener(connected);
        },
        removeConnectionListener: function(listener) {
            const index = connectionListeners.indexOf(listener);
            if (index !== -1) connectionListeners.splice(index, 1);
        },
        
        addStatusListener: function(listener) {
            statusListeners.push(listener);
        },
        removeStatusListener: function(listener) {
            const index = statusListeners.indexOf(listener);
            if (index !== -1) statusListeners.splice(index, 1);
        },
        
        addJobListener: function(listener) {
            jobListeners.push(listener);
        },
        removeJobListener: function(listener) {
            const index = jobListeners.indexOf(listener);
            if (index !== -1) jobListeners.splice(index, 1);
        }
    };
})();

// Initialize the WebSocket manager when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.HairbrushWebSocket.initialize();
    
    // Set up emergency stop button if it exists
    const emergencyStopBtn = document.getElementById('emergency-stop');
    if (emergencyStopBtn) {
        emergencyStopBtn.addEventListener('click', () => {
            window.HairbrushWebSocket.sendCommand('M112'); // Emergency stop command
        });
    }
    
    // Set up machine status display if it exists
    const machineStatus = document.getElementById('machine-status');
    if (machineStatus) {
        window.HairbrushWebSocket.addStatusListener(function(data) {
            if (data && data.state) {
                machineStatus.textContent = `Status: ${data.state}`;
            }
        });
    }
});

// For backward compatibility
window.hairbrushController = {
    sendCommand: function(command) {
        return window.HairbrushWebSocket.sendCommand(command);
    },
    sendJog: function(axis, distance, speed) {
        return window.HairbrushWebSocket.sendJog(axis, distance, speed);
    },
    sendJobControl: function(action, job_id) {
        return window.HairbrushWebSocket.sendJobControl(action, job_id);
    },
    requestMachineStatus: function() {
        return window.HairbrushWebSocket.requestMachineStatus();
    },
    isConnected: function() {
        return window.HairbrushWebSocket.isConnected();
    }
}; 
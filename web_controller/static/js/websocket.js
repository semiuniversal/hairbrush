/**
 * WebSocket client for H.Airbrush Web Controller
 * Handles real-time communication with the server
 */

// Initialize socket connection
const socket = io();
let connected = false;
let statusUpdateInterval;

// Connection status indicator (now handled by connection.js)
const machineStatus = document.getElementById('machine-status');

// Emergency stop button
const emergencyStopBtn = document.getElementById('emergency-stop');
if (emergencyStopBtn) {
    emergencyStopBtn.addEventListener('click', () => {
        sendCommand('M112'); // Emergency stop command
    });
}

// Connection events
socket.on('connect', () => {
    console.log('Connected to server');
    connected = true;
    
    // Start status updates
    startStatusUpdates();
    
    // Emit initial status request
    requestMachineStatus();
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    connected = false;
    
    // Stop status updates
    stopStatusUpdates();
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    connected = false;
});

// Status updates
socket.on('status_update', (data) => {
    console.log('Status update:', data);
    updateMachineStatus(data);
});

// Job updates
socket.on('job_update', (data) => {
    console.log('Job update:', data);
    updateJobStatus(data);
});

// Start periodic status updates
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

// Stop periodic status updates
function stopStatusUpdates() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
        statusUpdateInterval = null;
    }
}

// Request machine status from server
function requestMachineStatus() {
    socket.emit('get_status', {}, (response) => {
        if (response && response.status === 'success') {
            updateMachineStatus(response.data);
        }
    });
}

// Update machine status display
function updateMachineStatus(data) {
    if (!data) return;
    
    // Update machine status text
    if (machineStatus) {
        machineStatus.textContent = `Status: ${data.state || 'Unknown'}`;
    }
    
    // Update position if elements exist
    const xPosition = document.getElementById('x-position');
    const yPosition = document.getElementById('y-position');
    const zPosition = document.getElementById('z-position');
    
    if (data.position) {
        if (xPosition) xPosition.textContent = data.position.X.toFixed(2);
        if (yPosition) yPosition.textContent = data.position.Y.toFixed(2);
        if (zPosition) zPosition.textContent = data.position.Z.toFixed(2);
    }
    
    // Update homed state
    const homedState = document.getElementById('homed-state');
    if (homedState && data.is_homed !== undefined) {
        homedState.textContent = data.is_homed ? 'Yes' : 'No';
    }
    
    // Update machine state
    const machineState = document.getElementById('machine-state');
    if (machineState && data.state) {
        machineState.textContent = data.state;
    }
    
    // Update brush status
    const brushAStatus = document.getElementById('brush-a-status');
    const brushBStatus = document.getElementById('brush-b-status');
    
    if (data.brush_state) {
        if (brushAStatus) {
            const brushA = data.brush_state.a;
            let status = 'Inactive';
            
            if (brushA) {
                if (brushA.air && brushA.paint) {
                    status = 'Active (Air + Paint)';
                } else if (brushA.air) {
                    status = 'Air Only';
                } else if (brushA.paint) {
                    status = 'Paint Only';
                }
            }
            
            brushAStatus.textContent = status;
        }
        
        if (brushBStatus) {
            const brushB = data.brush_state.b;
            let status = 'Inactive';
            
            if (brushB) {
                if (brushB.air && brushB.paint) {
                    status = 'Active (Air + Paint)';
                } else if (brushB.air) {
                    status = 'Air Only';
                } else if (brushB.paint) {
                    status = 'Paint Only';
                }
            }
            
            brushBStatus.textContent = status;
        }
    }
    
    // Call page-specific update function if it exists
    if (typeof onMachineStatusUpdate === 'function') {
        onMachineStatusUpdate(data);
    }
}

// Update job status display
function updateJobStatus(data) {
    if (!data) return;
    
    const noJob = document.getElementById('no-job');
    const activeJob = document.getElementById('active-job');
    const jobName = document.getElementById('job-name');
    const jobProgress = document.getElementById('job-progress');
    const jobProgressText = document.getElementById('job-progress-text');
    const jobTime = document.getElementById('job-time');
    const pauseJobBtn = document.getElementById('pause-job');
    const resumeJobBtn = document.getElementById('resume-job');
    
    if (!noJob || !activeJob) return;
    
    if (data.status === 'running' || data.status === 'paused') {
        // Show active job
        noJob.classList.add('d-none');
        activeJob.classList.remove('d-none');
        
        // Update job details
        if (jobName) jobName.textContent = data.filename;
        if (jobProgress) jobProgress.style.width = `${data.progress}%`;
        if (jobProgressText) jobProgressText.textContent = `${Math.round(data.progress)}%`;
        
        // Update time display
        if (jobTime && data.start_time) {
            const elapsed = Math.floor((Date.now() / 1000) - data.start_time);
            jobTime.textContent = formatTime(elapsed);
        }
        
        // Update pause/resume buttons
        if (pauseJobBtn && resumeJobBtn) {
            if (data.status === 'running') {
                pauseJobBtn.classList.remove('d-none');
                resumeJobBtn.classList.add('d-none');
            } else {
                pauseJobBtn.classList.add('d-none');
                resumeJobBtn.classList.remove('d-none');
            }
        }
    } else {
        // No active job
        noJob.classList.remove('d-none');
        activeJob.classList.add('d-none');
    }
    
    // Call page-specific update function if it exists
    if (typeof onJobStatusUpdate === 'function') {
        onJobStatusUpdate(data);
    }
}

// Format time in HH:MM:SS
function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    
    return [
        h.toString().padStart(2, '0'),
        m.toString().padStart(2, '0'),
        s.toString().padStart(2, '0')
    ].join(':');
}

// Send command to server
function sendCommand(command) {
    if (!connected) {
        console.error('Not connected to server');
        return Promise.reject(new Error('Not connected to server'));
    }
    
    return new Promise((resolve, reject) => {
        socket.emit('command', { command }, (response) => {
            if (response && response.status === 'success') {
                resolve(response.result);
            } else {
                reject(new Error(response?.message || 'Command failed'));
            }
        });
    });
}

// Send jog command
function sendJog(axis, distance, speed) {
    if (!connected) {
        console.error('Not connected to server');
        return Promise.reject(new Error('Not connected to server'));
    }
    
    return new Promise((resolve, reject) => {
        socket.emit('jog', { axis, distance, speed }, (response) => {
            if (response && response.status === 'success') {
                resolve(response.result);
            } else {
                reject(new Error(response?.message || 'Jog command failed'));
            }
        });
    });
}

// Send job control command
function sendJobControl(action, job_id) {
    if (!connected) {
        console.error('Not connected to server');
        return Promise.reject(new Error('Not connected to server'));
    }
    
    return new Promise((resolve, reject) => {
        socket.emit('job_control', { action, job_id }, (response) => {
            if (response && response.status === 'success') {
                resolve(response.result);
            } else {
                reject(new Error(response?.message || 'Job control failed'));
            }
        });
    });
}

// Export functions for use in other scripts
window.hairbrushController = {
    sendCommand,
    sendJog,
    sendJobControl,
    requestMachineStatus
}; 
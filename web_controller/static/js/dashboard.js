/**
 * Dashboard JavaScript for H.Airbrush Web Controller
 * Handles dashboard-specific functionality and job status visualization
 */

// DOM elements
const refreshStatusBtn = document.getElementById('refresh-status');
const homeMachineBtn = document.getElementById('home-machine');
const parkMachineBtn = document.getElementById('park-machine');
const disableMotorsBtn = document.getElementById('disable-motors');
const pauseJobBtn = document.getElementById('pause-job');
const resumeJobBtn = document.getElementById('resume-job');
const stopJobBtn = document.getElementById('stop-job');
const viewTopBtn = document.getElementById('view-top');
const viewFrontBtn = document.getElementById('view-front');
const viewSideBtn = document.getElementById('view-side');

// Visualization elements
const visualizationContainer = document.getElementById('visualization-container');
const canvas = document.getElementById('visualization-canvas');

// Three.js variables
let scene, camera, renderer, machine, currentJob;
let cameraPosition = 'top'; // top, front, side

// Job status elements
const noJobElement = document.getElementById('no-job');
const activeJobElement = document.getElementById('active-job');
const jobNameElement = document.getElementById('job-name');
const jobProgressElement = document.getElementById('job-progress');
const jobProgressTextElement = document.getElementById('job-progress-text');
const jobTimeElement = document.getElementById('job-time');

// Detailed job status elements
const noJobStatusElement = document.getElementById('no-job-status');
const activeJobStatusElement = document.getElementById('active-job-status');
const jobStatusElement = document.getElementById('job-status');
const jobElapsedElement = document.getElementById('job-elapsed');
const jobLinesElement = document.getElementById('job-lines');
const jobRemainingElement = document.getElementById('job-remaining');
const progressCanvas = document.getElementById('progress-canvas');
const brushAUsageElement = document.getElementById('brush-a-usage');
const brushBUsageElement = document.getElementById('brush-b-usage');

// Job status tracking
let jobUpdateInterval = null;
let jobStartTime = null;
let progressCtx = null;

// Initialize dashboard
function initDashboard() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize job status visualization
    initJobVisualization();
    
    // Initial status update
    if (window.HairbrushWebSocket) {
        window.HairbrushWebSocket.addStatusListener(onMachineStatusUpdate);
        window.HairbrushWebSocket.requestStatus();
    } else {
        hairbrushController.requestMachineStatus();
    }
    
    // Load recent files
    loadRecentFiles();
    
    // Check for active job
    checkActiveJob();
}

// Set up event listeners
function setupEventListeners() {
    // Refresh status button
    if (refreshStatusBtn) {
        refreshStatusBtn.addEventListener('click', () => {
            if (window.HairbrushWebSocket) {
                window.HairbrushWebSocket.requestStatus();
            } else {
                hairbrushController.requestMachineStatus();
            }
        });
    }
    
    // Home machine button
    if (homeMachineBtn) {
        homeMachineBtn.addEventListener('click', () => {
            if (window.HairbrushWebSocket) {
                window.HairbrushWebSocket.sendCommand('G28')
                    .then(() => {
                        console.log('Machine homed');
                    })
                    .catch((error) => {
                        console.error('Home failed:', error);
                        alert('Home failed: ' + error.message);
                    });
            } else {
                hairbrushController.sendCommand('G28')
                    .then(() => {
                        console.log('Machine homed');
                    })
                    .catch((error) => {
                        console.error('Home failed:', error);
                        alert('Home failed: ' + error.message);
                    });
            }
        });
    }
    
    // Park machine button
    if (parkMachineBtn) {
        parkMachineBtn.addEventListener('click', () => {
            // First move Z to safe height
            const sendCommand = window.HairbrushWebSocket ? 
                window.HairbrushWebSocket.sendCommand.bind(window.HairbrushWebSocket) : 
                hairbrushController.sendCommand.bind(hairbrushController);
                
            sendCommand('G1 Z10 F500')
                .then(() => {
                    // Then move to park position
                    return sendCommand('G1 X0 Y0 F3000');
                })
                .then(() => {
                    console.log('Machine parked');
                })
                .catch((error) => {
                    console.error('Park failed:', error);
                    alert('Park failed: ' + error.message);
                });
        });
    }
    
    // Disable motors button
    if (disableMotorsBtn) {
        disableMotorsBtn.addEventListener('click', () => {
            const sendCommand = window.HairbrushWebSocket ? 
                window.HairbrushWebSocket.sendCommand.bind(window.HairbrushWebSocket) : 
                hairbrushController.sendCommand.bind(hairbrushController);
                
            sendCommand('M18')
                .then(() => {
                    console.log('Motors disabled');
                })
                .catch((error) => {
                    console.error('Disable motors failed:', error);
                    alert('Disable motors failed: ' + error.message);
                });
        });
    }
    
    // Job control buttons
    if (pauseJobBtn) {
        pauseJobBtn.addEventListener('click', () => {
            sendJobControl('pause')
                .then(() => {
                    console.log('Job paused');
                    updateJobControlButtons('paused');
                })
                .catch((error) => {
                    console.error('Pause job failed:', error);
                    alert('Pause job failed: ' + error.message);
                });
        });
    }
    
    if (resumeJobBtn) {
        resumeJobBtn.addEventListener('click', () => {
            sendJobControl('resume')
                .then(() => {
                    console.log('Job resumed');
                    updateJobControlButtons('running');
                })
                .catch((error) => {
                    console.error('Resume job failed:', error);
                    alert('Resume job failed: ' + error.message);
                });
        });
    }
    
    if (stopJobBtn) {
        stopJobBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to stop the current job?')) {
                sendJobControl('stop')
                    .then(() => {
                        console.log('Job stopped');
                        clearJobStatus();
                    })
                    .catch((error) => {
                        console.error('Stop job failed:', error);
                        alert('Stop job failed: ' + error.message);
                    });
            }
        });
    }
    
    // View buttons
    if (viewTopBtn) {
        viewTopBtn.addEventListener('click', () => {
            cameraPosition = 'top';
            updateCameraPosition();
            
            // Update active button
            viewTopBtn.classList.add('active');
            viewFrontBtn.classList.remove('active');
            viewSideBtn.classList.remove('active');
        });
    }
    
    if (viewFrontBtn) {
        viewFrontBtn.addEventListener('click', () => {
            cameraPosition = 'front';
            updateCameraPosition();
            
            // Update active button
            viewTopBtn.classList.remove('active');
            viewFrontBtn.classList.add('active');
            viewSideBtn.classList.remove('active');
        });
    }
    
    if (viewSideBtn) {
        viewSideBtn.addEventListener('click', () => {
            cameraPosition = 'side';
            updateCameraPosition();
            
            // Update active button
            viewTopBtn.classList.remove('active');
            viewFrontBtn.classList.remove('active');
            viewSideBtn.classList.add('active');
        });
    }
    
    // Window resize
    window.addEventListener('resize', () => {
        if (renderer && camera) {
            const width = visualizationContainer.clientWidth;
            const height = visualizationContainer.clientHeight;
            
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            
            renderer.setSize(width, height);
        }
    });
    
    // Set up WebSocket job status listener
    if (window.HairbrushWebSocket) {
        window.HairbrushWebSocket.socket.on('job_status', onJobStatusUpdate);
    }
}

// Initialize job visualization
function initJobVisualization() {
    if (progressCanvas) {
        progressCtx = progressCanvas.getContext('2d');
        
        // Set canvas width to match container
        const container = progressCanvas.parentElement;
        if (container) {
            progressCanvas.width = container.clientWidth;
        }
        
        // Draw empty grid
        drawProgressGrid();
    }
}

// Draw progress grid
function drawProgressGrid() {
    if (!progressCtx) return;
    
    const width = progressCanvas.width;
    const height = progressCanvas.height;
    
    // Clear canvas
    progressCtx.clearRect(0, 0, width, height);
    
    // Draw background
    progressCtx.fillStyle = '#f8f9fa';
    progressCtx.fillRect(0, 0, width, height);
    
    // Draw grid
    progressCtx.strokeStyle = '#dee2e6';
    progressCtx.lineWidth = 1;
    
    // Draw vertical grid lines
    for (let x = 0; x <= width; x += width / 10) {
        progressCtx.beginPath();
        progressCtx.moveTo(x, 0);
        progressCtx.lineTo(x, height);
        progressCtx.stroke();
    }
    
    // Draw horizontal grid lines
    for (let y = 0; y <= height; y += height / 5) {
        progressCtx.beginPath();
        progressCtx.moveTo(0, y);
        progressCtx.lineTo(width, y);
        progressCtx.stroke();
    }
    
    // Draw "No data" text
    progressCtx.fillStyle = '#6c757d';
    progressCtx.font = '14px Arial';
    progressCtx.textAlign = 'center';
    progressCtx.textBaseline = 'middle';
    progressCtx.fillText('No print data available', width / 2, height / 2);
}

// Update progress visualization
function updateProgressVisualization(progress, lines, totalLines) {
    if (!progressCtx) return;
    
    const width = progressCanvas.width;
    const height = progressCanvas.height;
    
    // Clear canvas
    progressCtx.clearRect(0, 0, width, height);
    
    // Draw background
    progressCtx.fillStyle = '#f8f9fa';
    progressCtx.fillRect(0, 0, width, height);
    
    // Draw grid
    progressCtx.strokeStyle = '#dee2e6';
    progressCtx.lineWidth = 1;
    
    // Draw vertical grid lines
    for (let x = 0; x <= width; x += width / 10) {
        progressCtx.beginPath();
        progressCtx.moveTo(x, 0);
        progressCtx.lineTo(x, height);
        progressCtx.stroke();
    }
    
    // Draw horizontal grid lines
    for (let y = 0; y <= height; y += height / 5) {
        progressCtx.beginPath();
        progressCtx.moveTo(0, y);
        progressCtx.lineTo(width, y);
        progressCtx.stroke();
    }
    
    // Draw progress bar
    const progressWidth = width * progress / 100;
    progressCtx.fillStyle = '#0d6efd';
    progressCtx.fillRect(0, 0, progressWidth, height);
    
    // Draw progress text
    progressCtx.fillStyle = '#000';
    progressCtx.font = '14px Arial';
    progressCtx.textAlign = 'center';
    progressCtx.textBaseline = 'middle';
    progressCtx.fillText(`${lines} / ${totalLines} lines (${progress.toFixed(1)}%)`, width / 2, height / 2);
}

// Format time as HH:MM:SS
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        secs.toString().padStart(2, '0')
    ].join(':');
}

// Calculate estimated time remaining
function calculateTimeRemaining(progress, elapsedSeconds) {
    if (progress <= 0 || elapsedSeconds <= 0) return '--:--:--';
    
    const totalSeconds = elapsedSeconds / (progress / 100);
    const remainingSeconds = totalSeconds - elapsedSeconds;
    
    return formatTime(remainingSeconds);
}

// Send job control command
function sendJobControl(action, jobId = null) {
    const data = { action };
    if (jobId) data.job_id = jobId;
    
    if (window.HairbrushWebSocket) {
        return window.HairbrushWebSocket.socket.emit('job_control', data);
    } else {
        return new Promise((resolve, reject) => {
            fetch('/api/job/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to control job');
                }
                return response.json();
            })
            .then(data => resolve(data))
            .catch(error => reject(error));
        });
    }
}

// Update job control buttons based on job status
function updateJobControlButtons(status) {
    if (!pauseJobBtn || !resumeJobBtn) return;
    
    if (status === 'running') {
        pauseJobBtn.classList.remove('d-none');
        resumeJobBtn.classList.add('d-none');
    } else if (status === 'paused') {
        pauseJobBtn.classList.add('d-none');
        resumeJobBtn.classList.remove('d-none');
    }
}

// Check for active job
function checkActiveJob() {
    fetch('/api/files')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to get files');
            }
            return response.json();
        })
        .then(files => {
            // Check if any job is running or paused
            const activeJob = files.find(file => file.status === 'running' || file.status === 'paused');
            
            if (activeJob) {
                // Update job status
                onJobStatusUpdate(activeJob);
            }
        })
        .catch(error => {
            console.error('Error checking active job:', error);
        });
}

// Load recent files
function loadRecentFiles() {
    const recentFilesList = document.getElementById('recent-files-list');
    if (!recentFilesList) return;
    
    fetch('/api/files')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to get files');
            }
            return response.json();
        })
        .then(files => {
            // Sort files by upload date (newest first)
            files.sort((a, b) => b.upload_date - a.upload_date);
            
            // Take only the 5 most recent files
            const recentFiles = files.slice(0, 5);
            
            // Clear the list
            recentFilesList.innerHTML = '';
            
            if (recentFiles.length === 0) {
                recentFilesList.innerHTML = `
                    <div class="text-center py-3 text-muted">
                        <i class="bi bi-file-earmark"></i> No recent files
                    </div>
                `;
                return;
            }
            
            // Add files to the list
            recentFiles.forEach(file => {
                const fileItem = document.createElement('a');
                fileItem.href = `/files?file=${file.job_id}`;
                fileItem.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
                
                const date = new Date(file.upload_date * 1000);
                const dateStr = date.toLocaleDateString();
                
                fileItem.innerHTML = `
                    <div>
                        <i class="bi bi-file-earmark-code me-2"></i>
                        ${file.filename}
                    </div>
                    <small class="text-muted">${dateStr}</small>
                `;
                
                recentFilesList.appendChild(fileItem);
            });
        })
        .catch(error => {
            console.error('Error loading recent files:', error);
            recentFilesList.innerHTML = `
                <div class="text-center py-3 text-danger">
                    <i class="bi bi-exclamation-triangle"></i> Error loading files
                </div>
            `;
        });
}

// Handle job status update
function onJobStatusUpdate(data) {
    // Store current job
    currentJob = data;
    
    // Update job status elements
    if (data && (data.status === 'running' || data.status === 'paused')) {
        // Show active job
        if (noJobElement) noJobElement.classList.add('d-none');
        if (activeJobElement) activeJobElement.classList.remove('d-none');
        
        // Show active job status
        if (noJobStatusElement) noJobStatusElement.classList.add('d-none');
        if (activeJobStatusElement) activeJobStatusElement.classList.remove('d-none');
        
        // Update job name
        if (jobNameElement) jobNameElement.textContent = data.filename;
        
        // Update progress
        const progress = data.progress || 0;
        if (jobProgressElement) jobProgressElement.style.width = `${progress}%`;
        if (jobProgressTextElement) jobProgressTextElement.textContent = `${progress.toFixed(1)}%`;
        
        // Update status
        if (jobStatusElement) jobStatusElement.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
        
        // Update lines
        const currentLine = data.current_line || 0;
        const totalLines = data.total_lines || 0;
        if (jobLinesElement) jobLinesElement.textContent = `${currentLine} / ${totalLines}`;
        
        // Update progress visualization
        updateProgressVisualization(progress, currentLine, totalLines);
        
        // Update job control buttons
        updateJobControlButtons(data.status);
        
        // Track job time
        if (!jobStartTime && data.start_time) {
            jobStartTime = data.start_time;
        }
        
        // Update elapsed time
        if (jobStartTime) {
            const elapsedSeconds = Math.floor(Date.now() / 1000 - jobStartTime);
            if (jobTimeElement) jobTimeElement.textContent = formatTime(elapsedSeconds);
            if (jobElapsedElement) jobElapsedElement.textContent = formatTime(elapsedSeconds);
            
            // Update remaining time
            if (jobRemainingElement) {
                jobRemainingElement.textContent = calculateTimeRemaining(progress, elapsedSeconds);
            }
        }
        
        // Start update interval if not already running
        if (!jobUpdateInterval) {
            jobUpdateInterval = setInterval(updateJobTime, 1000);
        }
    } else {
        clearJobStatus();
    }
}

// Update job time (called every second)
function updateJobTime() {
    if (!currentJob || !jobStartTime) return;
    
    const elapsedSeconds = Math.floor(Date.now() / 1000 - jobStartTime);
    
    // Update elapsed time
    if (jobTimeElement) jobTimeElement.textContent = formatTime(elapsedSeconds);
    if (jobElapsedElement) jobElapsedElement.textContent = formatTime(elapsedSeconds);
    
    // Update remaining time
    if (jobRemainingElement && currentJob.progress) {
        jobRemainingElement.textContent = calculateTimeRemaining(currentJob.progress, elapsedSeconds);
    }
}

// Clear job status
function clearJobStatus() {
    // Reset job tracking
    currentJob = null;
    jobStartTime = null;
    
    // Clear update interval
    if (jobUpdateInterval) {
        clearInterval(jobUpdateInterval);
        jobUpdateInterval = null;
    }
    
    // Show no job
    if (noJobElement) noJobElement.classList.remove('d-none');
    if (activeJobElement) activeJobElement.classList.add('d-none');
    
    // Show no job status
    if (noJobStatusElement) noJobStatusElement.classList.remove('d-none');
    if (activeJobStatusElement) activeJobStatusElement.classList.add('d-none');
    
    // Reset progress visualization
    drawProgressGrid();
    
    // Reset brush usage
    if (brushAUsageElement) brushAUsageElement.style.width = '0%';
    if (brushBUsageElement) brushBUsageElement.style.width = '0%';
}

// Handle machine status update
function onMachineStatusUpdate(data) {
    // Update position
    const position = data.position || {};
    document.getElementById('x-position').textContent = (position.X || 0).toFixed(2);
    document.getElementById('y-position').textContent = (position.Y || 0).toFixed(2);
    document.getElementById('z-position').textContent = (position.Z || 0).toFixed(2);
    
    // Update machine state
    document.getElementById('machine-state').textContent = data.state || 'Unknown';
    document.getElementById('homed-state').textContent = data.is_homed ? 'Yes' : 'No';
    
    // Update brush status
    const brushState = data.brush_state || {
        a: { air: false, paint: false },
        b: { air: false, paint: false }
    };
    
    const brushAStatus = document.getElementById('brush-a-status');
    const brushBStatus = document.getElementById('brush-b-status');
    
    if (brushAStatus) {
        if (brushState.a.air && brushState.a.paint) {
            brushAStatus.textContent = 'Air & Paint On';
            brushAStatus.classList.add('text-success');
        } else if (brushState.a.air) {
            brushAStatus.textContent = 'Air On';
            brushAStatus.classList.add('text-primary');
            brushAStatus.classList.remove('text-success');
        } else if (brushState.a.paint) {
            brushAStatus.textContent = 'Paint On';
            brushAStatus.classList.add('text-warning');
            brushAStatus.classList.remove('text-success', 'text-primary');
        } else {
            brushAStatus.textContent = 'Inactive';
            brushAStatus.classList.remove('text-success', 'text-primary', 'text-warning');
        }
    }
    
    if (brushBStatus) {
        if (brushState.b.air && brushState.b.paint) {
            brushBStatus.textContent = 'Air & Paint On';
            brushBStatus.classList.add('text-success');
        } else if (brushState.b.air) {
            brushBStatus.textContent = 'Air On';
            brushBStatus.classList.add('text-primary');
            brushBStatus.classList.remove('text-success');
        } else if (brushState.b.paint) {
            brushBStatus.textContent = 'Paint On';
            brushBStatus.classList.add('text-warning');
            brushBStatus.classList.remove('text-success', 'text-primary');
        } else {
            brushBStatus.textContent = 'Inactive';
            brushBStatus.classList.remove('text-success', 'text-primary', 'text-warning');
        }
    }
}

// Update camera position based on selected view
function updateCameraPosition() {
    if (!camera) return;
    
    switch (cameraPosition) {
        case 'top':
            camera.position.set(0, 200, 0);
            camera.up.set(0, 0, -1);
            break;
        case 'front':
            camera.position.set(0, 50, 200);
            camera.up.set(0, 1, 0);
            break;
        case 'side':
            camera.position.set(200, 50, 0);
            camera.up.set(0, 1, 0);
            break;
    }
    
    camera.lookAt(0, 0, 0);
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', initDashboard); 
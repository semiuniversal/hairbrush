/**
 * Dashboard JavaScript for H.Airbrush Web Controller
 * Handles dashboard-specific functionality and visualization
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

// Initialize dashboard
function initDashboard() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize visualization
    initVisualization();
    
    // Initial status update
    hairbrushController.requestMachineStatus();
}

// Set up event listeners
function setupEventListeners() {
    // Refresh status button
    if (refreshStatusBtn) {
        refreshStatusBtn.addEventListener('click', () => {
            hairbrushController.requestMachineStatus();
        });
    }
    
    // Home machine button
    if (homeMachineBtn) {
        homeMachineBtn.addEventListener('click', () => {
            hairbrushController.sendCommand('G28')
                .then(() => {
                    console.log('Machine homed');
                })
                .catch((error) => {
                    console.error('Home failed:', error);
                    alert('Home failed: ' + error.message);
                });
        });
    }
    
    // Park machine button
    if (parkMachineBtn) {
        parkMachineBtn.addEventListener('click', () => {
            // First move Z to safe height
            hairbrushController.sendCommand('G1 Z10 F500')
                .then(() => {
                    // Then move to park position
                    return hairbrushController.sendCommand('G1 X0 Y0 F3000');
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
            hairbrushController.sendCommand('M18')
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
            hairbrushController.sendJobControl('pause')
                .then(() => {
                    console.log('Job paused');
                })
                .catch((error) => {
                    console.error('Pause job failed:', error);
                    alert('Pause job failed: ' + error.message);
                });
        });
    }
    
    if (resumeJobBtn) {
        resumeJobBtn.addEventListener('click', () => {
            hairbrushController.sendJobControl('resume')
                .then(() => {
                    console.log('Job resumed');
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
                hairbrushController.sendJobControl('stop')
                    .then(() => {
                        console.log('Job stopped');
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
}

// Initialize Three.js visualization
function initVisualization() {
    if (!canvas || !visualizationContainer) return;
    
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8f9fa);
    
    // Create camera
    const width = visualizationContainer.clientWidth;
    const height = visualizationContainer.clientHeight;
    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true
    });
    renderer.setSize(width, height);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(0, 1, 1);
    scene.add(directionalLight);
    
    // Create machine representation
    createMachine();
    
    // Set initial camera position
    updateCameraPosition();
    
    // Start animation loop
    animate();
}

// Create machine representation
function createMachine() {
    // Create machine group
    machine = new THREE.Group();
    
    // Create bed
    const bedGeometry = new THREE.BoxGeometry(300, 10, 300);
    const bedMaterial = new THREE.MeshPhongMaterial({ color: 0xcccccc });
    const bed = new THREE.Mesh(bedGeometry, bedMaterial);
    bed.position.y = -5;
    machine.add(bed);
    
    // Create coordinate system
    const axisHelper = new THREE.AxesHelper(50);
    machine.add(axisHelper);
    
    // Create gantry
    const gantryGeometry = new THREE.BoxGeometry(320, 10, 10);
    const gantryMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
    const gantry = new THREE.Mesh(gantryGeometry, gantryMaterial);
    gantry.position.y = 30;
    machine.add(gantry);
    
    // Create carriage
    const carriageGeometry = new THREE.BoxGeometry(20, 20, 20);
    const carriageMaterial = new THREE.MeshPhongMaterial({ color: 0x666666 });
    const carriage = new THREE.Mesh(carriageGeometry, carriageMaterial);
    carriage.position.set(0, 20, 0);
    machine.add(carriage);
    
    // Add machine to scene
    scene.add(machine);
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

// Update machine visualization based on status
function updateMachineVisualization(status) {
    if (!machine || !status || !status.position) return;
    
    // Update carriage position
    const carriage = machine.children[3]; // Assuming carriage is the 4th child
    if (carriage) {
        carriage.position.x = status.position.X;
        carriage.position.z = -status.position.Y; // Y is inverted in Three.js
        carriage.position.y = 20 + status.position.Z;
    }
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    if (renderer && scene && camera) {
        renderer.render(scene, camera);
    }
}

// Machine status update handler
function onMachineStatusUpdate(data) {
    updateMachineVisualization(data);
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', initDashboard); 
/**
 * GCodeViewer - A lightweight G-code visualization library
 * Based on the work by ScorchWorks (https://github.com/scottalford75/gcode-viewer)
 * Modified for H.Airbrush Controller
 * Version: 1.1.0 - Updated UI per mockups (2025-06-22)
 */

class GCodeViewer {
    constructor(canvas) {
        if (!canvas) {
            console.error('Canvas element is null or undefined');
            throw new Error('Canvas element is required');
        }
        
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        
        // Initialize state
        this.gcode = [];
        this.lines = [];
        this.bounds = {
            minX: 0,
            maxX: 0,
            minY: 0,
            maxY: 0,
            minZ: 0,
            maxZ: 0
        };
        this.currentPosition = { x: 0, y: 0, z: 0 };
        this.scale = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        this.layers = [];
        this.currentLayer = -1;
        this.totalDistance = 0;
        this.drawingDistance = 0;
        this.travelDistance = 0;
        this.activeTool = 0; // 0 = Tool A, 1 = Tool B
        
        // Default options
        this.options = {
            showTravel: true,
            showToolhead: true,
            drawColorA: '#000000', // Black for brush A
            drawColorB: '#FFFFFF', // White for brush B
            travelColor: '#FF0000', // Red for rapids
            toolheadColorA: '#000000', // Black for tool A
            toolheadColorB: '#FFFFFF', // White for tool B
            backgroundColor: '#F0F0F0', // Light gray background
            gridColor: '#CCCCCC', // Grid color
            showGrid: true,
            margin: 10
        };
        
        // Set canvas size to match container
        this.resize();
    }
    
    resize() {
        // Update canvas size to match container size
        const container = this.canvas.parentElement;
        if (container) {
            this.canvas.width = container.clientWidth;
            this.canvas.height = container.clientHeight;
            
            // Re-render if we have content
            if (this.lines && this.lines.length > 0) {
                this.render();
            }
        }
    }
    
    setOptions(options) {
        this.options = { ...this.options, ...options };
    }
    
    addGCodeLine(line) {
        // Store original G-code
        this.gcode.push(line);
        
        // Parse G-code command
        const trimmedLine = line.trim();
        
        // Skip comments and empty lines
        if (trimmedLine === '' || trimmedLine.startsWith(';')) {
            // Check for brush indicators in comments
            if (trimmedLine.includes("Brush: A")) {
                this.activeTool = 0;
            } else if (trimmedLine.includes("Brush: B")) {
                this.activeTool = 1;
            }
            return;
        }
        
        // Check for tool change (M42 or M280 commands)
        // M42 P0 S1 -> Air ON for Brush A
        // M42 P1 S1 -> Air ON for Brush B
        // M280 P0 S180 -> Trigger Brush A
        // M280 P1 S180 -> Trigger Brush B
        const match = trimmedLine.match(/M(42|280)\s+P(\d+)/);
        if (match) {
            const brushIndex = parseInt(match[2], 10);
            this.activeTool = brushIndex;
            return;
        }
        
        // Check for tool change (T0 = Brush A, T1 = Brush B)
        if (trimmedLine.startsWith('T')) {
            const toolNumber = parseInt(trimmedLine.substring(1));
            if (!isNaN(toolNumber) && (toolNumber === 0 || toolNumber === 1)) {
                this.activeTool = toolNumber;
            }
            return;
        }
        
        // Process G0/G1 movement commands
        if (trimmedLine.startsWith('G0') || trimmedLine.startsWith('G1')) {
            const isDrawing = trimmedLine.startsWith('G1');
            const parts = trimmedLine.split(' ');
            
            // Create a copy of the current position
            const newPosition = { ...this.currentPosition };
            
            // Parse coordinates
            for (const part of parts.slice(1)) {
                const axis = part[0].toLowerCase();
                const value = parseFloat(part.substring(1));
                
                if (!isNaN(value) && (axis === 'x' || axis === 'y' || axis === 'z')) {
                    newPosition[axis] = value;
                }
            }
            
            // Check for layer change
            if (newPosition.z !== this.currentPosition.z) {
                this.layers.push(this.lines.length);
            }
            
            // Calculate distance
            const dx = newPosition.x - this.currentPosition.x;
            const dy = newPosition.y - this.currentPosition.y;
            const dz = newPosition.z - this.currentPosition.z;
            const distance = Math.sqrt(dx*dx + dy*dy + dz*dz);
            
            // Update total distance
            this.totalDistance += distance;
            if (isDrawing) {
                this.drawingDistance += distance;
            } else {
                this.travelDistance += distance;
            }
            
            // Update bounds
            this.bounds.minX = Math.min(this.bounds.minX, newPosition.x);
            this.bounds.maxX = Math.max(this.bounds.maxX, newPosition.x);
            this.bounds.minY = Math.min(this.bounds.minY, newPosition.y);
            this.bounds.maxY = Math.max(this.bounds.maxY, newPosition.y);
            this.bounds.minZ = Math.min(this.bounds.minZ, newPosition.z);
            this.bounds.maxZ = Math.max(this.bounds.maxZ, newPosition.z);
            
            // Add line segment
            this.lines.push({
                start: { ...this.currentPosition },
                end: { ...newPosition },
                isDrawing: isDrawing,
                layer: this.layers.length,
                tool: this.activeTool // Store which tool was active for this line
            });
            
            // Update current position
            this.currentPosition = { ...newPosition };
        }
    }
    
    getStatistics() {
        return {
            minX: this.bounds.minX,
            maxX: this.bounds.maxX,
            minY: this.bounds.minY,
            maxY: this.bounds.maxY,
            minZ: this.bounds.minZ,
            maxZ: this.bounds.maxZ,
            totalDistance: this.totalDistance,
            drawingDistance: this.drawingDistance,
            travelDistance: this.travelDistance,
            layerCount: this.layers.length
        };
    }
    
    calculateScale() {
        // Calculate width and height of the G-code
        const width = Math.max(1, this.bounds.maxX - this.bounds.minX); // Ensure non-zero width
        const height = Math.max(1, this.bounds.maxY - this.bounds.minY); // Ensure non-zero height
        
        // Calculate scale to fit within canvas with margin
        const margin = this.options.margin;
        const scaleX = (this.canvas.width - margin * 2) / width;
        const scaleY = (this.canvas.height - margin * 2) / height;
        
        // Use the smaller scale to ensure everything fits
        this.scale = Math.min(scaleX, scaleY);
        
        // Calculate center points
        const centerX = (this.bounds.minX + this.bounds.maxX) / 2;
        const centerY = (this.bounds.minY + this.bounds.maxY) / 2;
        
        // Calculate offset to center the drawing
        this.offsetX = this.canvas.width / 2 - centerX * this.scale;
        this.offsetY = this.canvas.height / 2 + centerY * this.scale; // Note: Y is flipped
        
        // We're handling the Y flip directly in the offset calculation
        this.scale = -this.scale; // Flip Y axis so that positive Y is up
    }
    
    transformX(x) {
        return x * Math.abs(this.scale) + this.offsetX;
    }
    
    transformY(y) {
        // Since we're handling the Y flip in the offset calculation,
        // we need to use the absolute value of scale for Y too
        return y * this.scale + this.offsetY;
    }
    
    fitToWindow() {
        console.log("Fitting to window...");
        console.log("Before: Scale =", this.scale, "OffsetX =", this.offsetX, "OffsetY =", this.offsetY);
        console.log("Bounds:", this.bounds);
        
        // Recalculate scale to fit the entire drawing in the window
        this.calculateScale();
        
        console.log("After: Scale =", this.scale, "OffsetX =", this.offsetX, "OffsetY =", this.offsetY);
        
        // Ensure we're showing all layers
        this.currentLayer = -1;
        
        // Render with the new scale and offset
        this.render();
    }
    
    centerView() {
        console.log("Centering view...");
        console.log("Before: Scale =", this.scale, "OffsetX =", this.offsetX, "OffsetY =", this.offsetY);
        
        // Calculate the center of the G-code
        const centerX = (this.bounds.minX + this.bounds.maxX) / 2;
        const centerY = (this.bounds.minY + this.bounds.maxY) / 2;
        
        // Set the offset to center the view (keeping the current scale)
        this.offsetX = this.canvas.width / 2 - centerX * Math.abs(this.scale);
        this.offsetY = this.canvas.height / 2 + centerY * Math.abs(this.scale); // Y is flipped
        
        console.log("After: Scale =", this.scale, "OffsetX =", this.offsetX, "OffsetY =", this.offsetY);
        
        this.render();
    }
    
    showAllLayers() {
        this.currentLayer = -1;
        this.render();
    }
    
    showLayerUpTo(layer) {
        this.currentLayer = layer;
        this.render();
    }
    
    // Find the active tool at a specific layer
    getActiveToolAtLayer(layer) {
        if (this.lines.length === 0) {
            return 0; // Default to tool A
        }
        
        // If showing all layers, use the last line's tool
        if (layer < 0 || layer >= this.layers.length) {
            return this.lines[this.lines.length - 1].tool;
        }
        
        // Find the last line in the specified layer
        const layerStartIndex = this.layers[layer];
        const layerEndIndex = (layer + 1 < this.layers.length) ? this.layers[layer + 1] - 1 : this.lines.length - 1;
        
        // Return the tool of the last line in the layer
        return this.lines[layerEndIndex].tool;
    }
    
    drawGrid() {
        if (!this.options.showGrid) return;
        
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Draw grid lines
        ctx.strokeStyle = this.options.gridColor;
        ctx.lineWidth = 0.5;
        
        // Calculate grid spacing (in mm)
        const gridSpacing = 50; // 50mm grid
        
        // Calculate grid lines positions
        const startX = Math.floor(this.bounds.minX / gridSpacing) * gridSpacing;
        const endX = Math.ceil(this.bounds.maxX / gridSpacing) * gridSpacing;
        const startY = Math.floor(this.bounds.minY / gridSpacing) * gridSpacing;
        const endY = Math.ceil(this.bounds.maxY / gridSpacing) * gridSpacing;
        
        // Draw vertical grid lines
        for (let x = startX; x <= endX; x += gridSpacing) {
            const screenX = this.transformX(x);
            ctx.beginPath();
            ctx.moveTo(screenX, 0);
            ctx.lineTo(screenX, height);
            ctx.stroke();
        }
        
        // Draw horizontal grid lines
        for (let y = startY; y <= endY; y += gridSpacing) {
            const screenY = this.transformY(y);
            ctx.beginPath();
            ctx.moveTo(0, screenY);
            ctx.lineTo(width, screenY);
            ctx.stroke();
        }
    }
    
    render() {
        // Clear canvas
        this.ctx.fillStyle = this.options.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.drawGrid();
        
        // If there are no lines, just return
        if (this.lines.length === 0) {
            return;
        }
        
        // Determine the last visible line based on current layer
        let lastVisibleLineIndex = this.lines.length - 1;
        if (this.currentLayer >= 0 && this.currentLayer < this.layers.length) {
            const nextLayerIndex = this.currentLayer + 1;
            if (nextLayerIndex < this.layers.length) {
                lastVisibleLineIndex = this.layers[nextLayerIndex] - 1;
            }
        }
        
        // Draw lines
        for (let i = 0; i <= lastVisibleLineIndex; i++) {
            const line = this.lines[i];
            
            // Skip if not showing travel moves and this is a travel move
            if (!this.options.showTravel && !line.isDrawing) {
                continue;
            }
            
            // Skip if we're only showing up to a specific layer
            if (this.currentLayer >= 0 && line.layer > this.currentLayer) {
                continue;
            }
            
            // Set line color based on tool and whether it's drawing or travel
            if (line.isDrawing) {
                if (line.tool === 0) {
                    // Brush A - Black
                    this.ctx.strokeStyle = this.options.drawColorA;
                    this.ctx.lineWidth = 1.5;
                    this.ctx.shadowBlur = 0;
                } else {
                    // Brush B - White with shadow for visibility
                    this.ctx.strokeStyle = this.options.drawColorB;
                    this.ctx.lineWidth = 1.5;
                    this.ctx.shadowColor = '#888';
                    this.ctx.shadowBlur = 2;
                }
            } else {
                // Travel move
                this.ctx.strokeStyle = this.options.travelColor;
                this.ctx.lineWidth = 0.75;
                this.ctx.shadowBlur = 0;
            }
            
            // Draw line
            this.ctx.beginPath();
            this.ctx.moveTo(
                this.transformX(line.start.x),
                this.transformY(line.start.y)
            );
            this.ctx.lineTo(
                this.transformX(line.end.x),
                this.transformY(line.end.y)
            );
            this.ctx.stroke();
            
            // Reset shadow
            this.ctx.shadowBlur = 0;
        }
        
        // Draw toolhead position
        if (this.options.showToolhead && this.lines.length > 0) {
            // Get the last visible line
            const lastLine = this.lines[Math.min(lastVisibleLineIndex, this.lines.length - 1)];
            
            // Get the active tool at the current layer
            const activeTool = this.currentLayer >= 0 ? 
                this.getActiveToolAtLayer(this.currentLayer) : 
                lastLine.tool;
            
            // Get position from the last visible line
            const x = this.transformX(lastLine.end.x);
            const y = this.transformY(lastLine.end.y);
            const toolLabel = activeTool === 0 ? 'A' : 'B';
            
            // Draw toolhead marker
            this.ctx.beginPath();
            this.ctx.arc(x, y, 10, 0, Math.PI * 2);
            
            if (activeTool === 0) {
                // Tool A - Black circle with white text
                this.ctx.fillStyle = this.options.toolheadColorA;
                this.ctx.fill();
                
                // Draw label
                this.ctx.fillStyle = '#FFFFFF';
                this.ctx.font = 'bold 12px Arial';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(toolLabel, x, y);
            } else {
                // Tool B - White circle with black outline and black text
                this.ctx.fillStyle = this.options.toolheadColorB;
                this.ctx.fill();
                this.ctx.strokeStyle = '#000000';
                this.ctx.lineWidth = 1;
                this.ctx.stroke();
                
                // Draw label
                this.ctx.fillStyle = '#000000';
                this.ctx.font = 'bold 12px Arial';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(toolLabel, x, y);
            }
        }
        
        // Update dimensions display if it exists
        const dimensionsElement = document.getElementById('canvas-dimensions');
        if (dimensionsElement) {
            const width = Math.abs(this.bounds.maxX - this.bounds.minX).toFixed(1);
            const height = Math.abs(this.bounds.maxY - this.bounds.minY).toFixed(1);
            dimensionsElement.textContent = `${width}mm × ${height}mm`;
        }
    }
}
/**
 * Canvas-based Position Visualization
 * 
 * A simple, reliable visualization of the machine position using HTML5 Canvas
 */

class MachineVisualization {
    constructor(containerId, config = {}) {
        // Get container
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Visualization container not found:', containerId);
            return;
        }
        
        // Default configuration
        this.config = {
            paperWidth: 841,  // A0 width in mm
            paperHeight: 1189, // A0 height in mm
            gridSpacing: 100,  // Grid spacing in mm
            brushAColor: '#000000',
            brushBColor: '#ffffff',
            brushBBorderColor: '#000000',
            brushBOffsetX: 50,
            brushBOffsetY: 0,
            showScaleIndicators: true,
            ...config
        };
        
        // Create canvas
        this.canvas = document.createElement('canvas');
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.display = 'block';
        this.container.appendChild(this.canvas);
        
        // Machine state
        this.position = { X: 0, Y: 0, Z: 0 };
        
        // Initialize
        this.resizeCanvas();
        this.draw();
        
        // Handle window resize
        window.addEventListener('resize', () => this.resizeCanvas());
        
        console.log('Machine visualization initialized with config:', this.config);
    }
    
    resizeCanvas() {
        // Get container dimensions
        const rect = this.container.getBoundingClientRect();
        
        // Set canvas dimensions (with higher resolution for retina displays)
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        
        // Get context and scale for retina
        this.ctx = this.canvas.getContext('2d');
        this.ctx.scale(dpr, dpr);
        
        // Calculate scaling factor to fit paper in visualization
        const margin = 20; // margin in pixels
        const availableWidth = rect.width - (2 * margin);
        const availableHeight = rect.height - (2 * margin);
        
        // Calculate scale (mm to pixels) based on the limiting dimension
        const scaleX = availableWidth / this.config.paperWidth;
        const scaleY = availableHeight / this.config.paperHeight;
        this.scale = Math.min(scaleX, scaleY);
        
        // Calculate paper dimensions in pixels
        this.paperWidthPx = this.config.paperWidth * this.scale;
        this.paperHeightPx = this.config.paperHeight * this.scale;
        
        // Position paper in center of visualization
        this.paperLeft = (rect.width - this.paperWidthPx) / 2;
        this.paperTop = (rect.height - this.paperHeightPx) / 2;
        
        // Set origin (center of paper)
        this.originX = this.paperLeft + (this.paperWidthPx / 2);
        this.originY = this.paperTop + (this.paperHeightPx / 2);
        
        // Redraw
        this.draw();
    }
    
    updatePosition(position) {
        if (!position) return;
        
        // Update position
        if (position.X !== undefined) this.position.X = position.X;
        if (position.Y !== undefined) this.position.Y = position.Y;
        if (position.Z !== undefined) this.position.Z = position.Z;
        
        // Redraw
        this.draw();
    }
    
    draw() {
        if (!this.ctx) return;
        
        const ctx = this.ctx;
        const rect = this.container.getBoundingClientRect();
        
        // Clear canvas
        ctx.clearRect(0, 0, rect.width, rect.height);
        
        // Draw paper
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#cccccc';
        ctx.lineWidth = 1;
        ctx.fillRect(this.paperLeft, this.paperTop, this.paperWidthPx, this.paperHeightPx);
        ctx.strokeRect(this.paperLeft, this.paperTop, this.paperWidthPx, this.paperHeightPx);
        
        // Draw grid
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        
        // Calculate grid spacing in pixels
        const gridSpacingPx = this.config.gridSpacing * this.scale;
        
        // Calculate grid offset from origin
        const halfPaperWidthMm = this.config.paperWidth / 2;
        const halfPaperHeightMm = this.config.paperHeight / 2;
        
        // Find grid line positions relative to origin
        const gridLinesX = [];
        const gridLinesY = [];
        
        // Calculate X grid lines (vertical lines)
        for (let x = 0; x <= halfPaperWidthMm; x += this.config.gridSpacing) {
            // Lines to the right of origin
            if (x > 0) {
                gridLinesX.push({ pos: x, label: `+${x}` });
            }
            // Lines to the left of origin (except at origin)
            if (x > 0) {
                gridLinesX.push({ pos: -x, label: `-${x}` });
            }
        }
        
        // Calculate Y grid lines (horizontal lines)
        for (let y = 0; y <= halfPaperHeightMm; y += this.config.gridSpacing) {
            // Lines above origin
            if (y > 0) {
                gridLinesY.push({ pos: y, label: `+${y}` });
            }
            // Lines below origin (except at origin)
            if (y > 0) {
                gridLinesY.push({ pos: -y, label: `-${y}` });
            }
        }
        
        // Add origin lines
        gridLinesX.push({ pos: 0, label: '0' });
        gridLinesY.push({ pos: 0, label: '0' });
        
        // Sort grid lines
        gridLinesX.sort((a, b) => a.pos - b.pos);
        gridLinesY.sort((a, b) => a.pos - b.pos);
        
        // Draw vertical grid lines (X axis)
        for (const line of gridLinesX) {
            const xPx = this.originX + (line.pos * this.scale);
            ctx.moveTo(xPx, this.paperTop);
            ctx.lineTo(xPx, this.paperTop + this.paperHeightPx);
        }
        
        // Draw horizontal grid lines (Y axis)
        for (const line of gridLinesY) {
            const yPx = this.originY - (line.pos * this.scale);
            ctx.moveTo(this.paperLeft, yPx);
            ctx.lineTo(this.paperLeft + this.paperWidthPx, yPx);
        }
        
        ctx.stroke();
        
        // Draw scale indicators if enabled
        if (this.config.showScaleIndicators) {
            ctx.fillStyle = '#9e9e9e';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            
            // Draw X axis scale indicators (bottom)
            ctx.textBaseline = 'top';
            for (const line of gridLinesX) {
                const xPx = this.originX + (line.pos * this.scale);
                // Only draw if within paper bounds
                if (xPx >= this.paperLeft && xPx <= this.paperLeft + this.paperWidthPx) {
                    ctx.fillText(line.label, xPx, this.paperTop + this.paperHeightPx + 5);
                }
            }
            
            // Draw X axis scale indicators (top)
            ctx.textBaseline = 'bottom';
            for (const line of gridLinesX) {
                const xPx = this.originX + (line.pos * this.scale);
                // Only draw if within paper bounds
                if (xPx >= this.paperLeft && xPx <= this.paperLeft + this.paperWidthPx) {
                    ctx.fillText(line.label, xPx, this.paperTop - 5);
                }
            }
            
            // Draw Y axis scale indicators (left)
            ctx.textAlign = 'right';
            ctx.textBaseline = 'middle';
            for (const line of gridLinesY) {
                const yPx = this.originY - (line.pos * this.scale);
                // Only draw if within paper bounds
                if (yPx >= this.paperTop && yPx <= this.paperTop + this.paperHeightPx) {
                    ctx.fillText(line.label, this.paperLeft - 5, yPx);
                }
            }
            
            // Draw Y axis scale indicators (right)
            ctx.textAlign = 'left';
            for (const line of gridLinesY) {
                const yPx = this.originY - (line.pos * this.scale);
                // Only draw if within paper bounds
                if (yPx >= this.paperTop && yPx <= this.paperTop + this.paperHeightPx) {
                    ctx.fillText(line.label, this.paperLeft + this.paperWidthPx + 5, yPx);
                }
            }
        }
        
        // Draw origin
        ctx.fillStyle = '#dc3545';
        ctx.beginPath();
        ctx.arc(this.originX, this.originY, 4, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw axis labels
        ctx.fillStyle = '#6c757d';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // X axis label
        ctx.fillText('+X', this.originX + 50, this.originY);
        
        // Y axis label
        ctx.fillText('+Y', this.originX, this.originY - 50);
        
        // Paper size label
        ctx.textAlign = 'right';
        ctx.textBaseline = 'bottom';
        ctx.fillText(`A0 (${this.config.paperWidth}mm × ${this.config.paperHeight}mm)`, 
            this.paperLeft + this.paperWidthPx - 10, 
            this.paperTop + this.paperHeightPx - 10);
        
        // Calculate brush positions
        const brushAX = this.originX + (this.position.X * this.scale);
        const brushAY = this.originY - (this.position.Y * this.scale); // Y is inverted
        
        const brushBX = this.originX + ((this.position.X + this.config.brushBOffsetX) * this.scale);
        const brushBY = this.originY - ((this.position.Y + this.config.brushBOffsetY) * this.scale);
        
        // Set opacity based on Z height
        const opacity = this.position.Z > 5 ? 0.5 : 1.0;
        
        // Draw brush A (black)
        ctx.fillStyle = this.config.brushAColor;
        ctx.globalAlpha = opacity;
        ctx.beginPath();
        ctx.arc(brushAX, brushAY, 7.5, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw A label
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('A', brushAX, brushAY);
        
        // Draw brush B (white with border)
        ctx.fillStyle = this.config.brushBColor;
        ctx.strokeStyle = this.config.brushBBorderColor;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(brushBX, brushBY, 7.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        
        // Draw B label
        ctx.fillStyle = '#000000';
        ctx.fillText('B', brushBX, brushBY);
        
        // Reset opacity
        ctx.globalAlpha = 1.0;
        
        // Draw position text
        ctx.fillStyle = '#333333';
        ctx.font = '11px Arial';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText(`Position: X=${this.position.X.toFixed(1)}, Y=${this.position.Y.toFixed(1)}, Z=${this.position.Z.toFixed(1)}`, 
            this.paperLeft + 10, 
            this.paperTop + 10);
        
        // Draw brush offset text
        ctx.fillText(`Brush B Offset: X=${this.config.brushBOffsetX.toFixed(1)}, Y=${this.config.brushBOffsetY.toFixed(1)}`, 
            this.paperLeft + 10, 
            this.paperTop + 25);
    }
    
    updateConfig(config) {
        this.config = { ...this.config, ...config };
        console.log('Updated visualization config:', this.config);
        this.resizeCanvas(); // Recalculate and redraw
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create global instance if container exists
    const container = document.getElementById('visualization-container');
    if (container) {
        // Get machine configuration
        fetch('/api/machine/config')
            .then(response => response.json())
            .then(config => {
                // Create visualization with config
                window.machineVisualization = new MachineVisualization('visualization-container', {
                    paperWidth: config.machine?.paper?.width || 841,
                    paperHeight: config.machine?.paper?.height || 1189,
                    brushBOffsetX: config.brushes?.b?.offsetX || 50,
                    brushBOffsetY: config.brushes?.b?.offsetY || 0
                });
                
                console.log('Canvas visualization initialized with config:', config);
            })
            .catch(error => {
                console.error('Error loading machine configuration:', error);
                // Initialize with defaults
                window.machineVisualization = new MachineVisualization('visualization-container');
            });
    }
}); 
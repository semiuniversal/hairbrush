// Visualization component for machine visualization
// No global state, no direct DOM queries

/**
 * Visualization class
 * Handles rendering of current machine position, brushes, and grid
 */
class Visualization {
    /**
     * @param {HTMLCanvasElement} canvas
     * @param {MachineState} machineState
     */
    constructor(canvas, machineState) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.machineState = machineState;
        this._listenerId = null;
        this._resizeHandler = null;
        this._subscribeState();
        this._bindResize();
        this._render();
    }

    /**
     * Subscribe to machineState for position/brush changes
     * @private
     */
    _subscribeState() {
        this._listenerId = this.machineState.addListener(() => this._render(), ['position', 'brushes']);
    }

    /**
     * Bind resize event for high-DPI support
     * @private
     */
    _bindResize() {
        this._resizeHandler = () => this._render();
        window.addEventListener('resize', this._resizeHandler);
    }

    /**
     * Render the visualization
     * @private
     */
    _render() {
        const dpr = window.devicePixelRatio || 1;
        const width = this.canvas.clientWidth * dpr;
        const height = this.canvas.clientHeight * dpr;
        this.canvas.width = width;
        this.canvas.height = height;
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.clearRect(0, 0, width, height);
        // Draw grid
        this._drawGrid(width, height, dpr);
        // Draw position and brushes
        const state = this.machineState.getFullState();
        this._drawPosition(state.position, width, height, dpr);
        this._drawBrushes(state.brushes, width, height, dpr);
    }

    /**
     * Draw grid
     * @private
     */
    _drawGrid(width, height, dpr) {
        const ctx = this.ctx;
        ctx.save();
        ctx.strokeStyle = '#eee';
        ctx.lineWidth = 1 * dpr;
        const step = 50 * dpr;
        for (let x = 0; x < width; x += step) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
        }
        for (let y = 0; y < height; y += step) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
        }
        ctx.restore();
    }

    /**
     * Draw current position
     * @private
     */
    _drawPosition(pos, width, height, dpr) {
        const ctx = this.ctx;
        ctx.save();
        ctx.fillStyle = '#007bff';
        // Centered origin
        const cx = width / 2 + (pos.X || 0) * dpr;
        const cy = height / 2 - (pos.Y || 0) * dpr;
        ctx.beginPath();
        ctx.arc(cx, cy, 8 * dpr, 0, 2 * Math.PI);
        ctx.fill();
        ctx.restore();
    }

    /**
     * Draw brushes
     * @private
     */
    _drawBrushes(brushes, width, height, dpr) {
        const ctx = this.ctx;
        const baseX = width / 2, baseY = height / 2;
        // Example: offset brushes for display
        ctx.save();
        ctx.fillStyle = '#222';
        ctx.beginPath();
        ctx.arc(baseX - 20 * dpr, baseY, 6 * dpr, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(baseX + 20 * dpr, baseY, 6 * dpr, 0, 2 * Math.PI);
        ctx.fill();
        ctx.restore();
    }

    /**
     * Clean up listeners/resources
     */
    destroy() {
        if (this._listenerId !== null) {
            this.machineState.removeListener(this._listenerId);
            this._listenerId = null;
        }
        if (this._resizeHandler) {
            window.removeEventListener('resize', this._resizeHandler);
            this._resizeHandler = null;
        }
    }
}

export { Visualization }; 
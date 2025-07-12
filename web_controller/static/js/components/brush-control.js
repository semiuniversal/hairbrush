// BrushControl component for brush-specific UI and logic
// No global state, no direct DOM queries

/**
 * BrushControl class
 * Handles air toggle, paint toggle, and paint value slider for a brush
 */
class BrushControl {
    /**
     * @param {'a'|'b'} brushId
     * @param {Object} elements - { airToggleBtn, paintToggleBtn, paintSlider }
     * @param {CommandEngine} commandEngine
     * @param {MachineState} machineState
     */
    constructor(brushId, elements, commandEngine, machineState) {
        this.brushId = brushId;
        this.elements = elements;
        this.commandEngine = commandEngine;
        this.machineState = machineState;
        this._listenerId = null;
        this._bound = false;
        this._bindUI();
        this._subscribeState();
    }

    /**
     * Bind UI event listeners
     * @private
     */
    _bindUI() {
        if (this._bound) return;
        this.elements.airToggleBtn.addEventListener('click', this._onAirToggle = () => {
            const state = this.machineState.getBrushState(this.brushId);
            this.commandEngine.setBrushAir(this.brushId, !state.air);
        });
        this.elements.paintToggleBtn.addEventListener('click', this._onPaintToggle = () => {
            const state = this.machineState.getBrushState(this.brushId);
            this.commandEngine.setBrushPaint(this.brushId, !state.paint, state.paintValue);
        });
        this.elements.paintSlider.addEventListener('input', this._onPaintSlider = (e) => {
            const value = Number(e.target.value);
            this.commandEngine.setBrushPaint(this.brushId, true, value);
        });
        this._bound = true;
    }

    /**
     * Subscribe to machineState for brush changes
     * @private
     */
    _subscribeState() {
        this._listenerId = this.machineState.addListener((state) => {
            const brush = state.brushes[this.brushId];
            this.elements.airToggleBtn.classList.toggle('active', brush.air);
            this.elements.paintToggleBtn.classList.toggle('active', brush.paint);
            this.elements.paintSlider.value = brush.paintValue;
        }, ['brushes']);
    }

    /**
     * Clean up listeners/resources
     */
    destroy() {
        if (this._listenerId !== null) {
            this.machineState.removeListener(this._listenerId);
            this._listenerId = null;
        }
        if (this._bound) {
            this.elements.airToggleBtn.removeEventListener('click', this._onAirToggle);
            this.elements.paintToggleBtn.removeEventListener('click', this._onPaintToggle);
            this.elements.paintSlider.removeEventListener('input', this._onPaintSlider);
            this._bound = false;
        }
    }
}

export { BrushControl }; 
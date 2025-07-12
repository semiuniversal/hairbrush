// MovementControl component for movement and positioning controls
// No global state, no direct DOM queries

/**
 * MovementControl class
 * Handles jog, home, speed/distance, and motor enable/disable controls
 */
class MovementControl {
    /**
     * @param {Object} elements - { jogBtns, homeBtns, speedSelect, distanceSelect, motorToggleBtn }
     * @param {CommandEngine} commandEngine
     * @param {MachineState} machineState
     */
    constructor(elements, commandEngine, machineState) {
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
        // Jog buttons
        this.elements.jogBtns.forEach(btn => {
            btn.addEventListener('click', btn._jogHandler = () => {
                const axis = btn.dataset.axis;
                const dir = btn.dataset.dir === 'minus' ? -1 : 1;
                const distance = Number(this.elements.distanceSelect.value) * dir;
                const speed = Number(this.elements.speedSelect.value);
                this.commandEngine.moveTo(
                    axis === 'X' ? distance : 0,
                    axis === 'Y' ? distance : 0,
                    axis === 'Z' ? distance : 0,
                    speed
                );
            });
        });
        // Home buttons
        this.elements.homeBtns.forEach(btn => {
            btn.addEventListener('click', btn._homeHandler = () => {
                const axis = btn.dataset.axis;
                // For simplicity, just move to 0 for the axis
                this.commandEngine.moveTo(
                    axis === 'X' ? 0 : undefined,
                    axis === 'Y' ? 0 : undefined,
                    axis === 'Z' ? 0 : undefined,
                    Number(this.elements.speedSelect.value)
                );
            });
        });
        // Motor toggle
        this.elements.motorToggleBtn.addEventListener('click', this._onMotorToggle = () => {
            const enabled = !this.machineState.getMotorState().enabled;
            this.commandEngine.setMotorsEnabled(enabled);
        });
        this._bound = true;
    }

    /**
     * Subscribe to machineState for motor state
     * @private
     */
    _subscribeState() {
        this._listenerId = this.machineState.addListener((state) => {
            const enabled = state.motors.enabled;
            // Disable/enable all controls based on motor state
            this.elements.jogBtns.forEach(btn => { btn.disabled = !enabled; });
            this.elements.homeBtns.forEach(btn => { btn.disabled = !enabled; });
            this.elements.motorToggleBtn.classList.toggle('active', enabled);
        }, ['motors']);
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
            this.elements.jogBtns.forEach(btn => btn.removeEventListener('click', btn._jogHandler));
            this.elements.homeBtns.forEach(btn => btn.removeEventListener('click', btn._homeHandler));
            this.elements.motorToggleBtn.removeEventListener('click', this._onMotorToggle);
            this._bound = false;
        }
    }
}

export { MovementControl }; 
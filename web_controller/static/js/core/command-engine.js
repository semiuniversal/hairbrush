// CommandEngine module for hardware command abstraction
// Exposes high-level methods for movement, brush control, etc.

/**
 * CommandEngine class
 * Accepts dependencies via constructor (WebSocketClient, MachineState)
 */
class CommandEngine {
    /**
     * @param {Object} deps - { wsClient, machineState }
     */
    constructor({ wsClient, machineState }) {
        this.wsClient = wsClient;
        this.machineState = machineState;
    }

    /**
     * Move to a position
     * @param {number} x
     * @param {number} y
     * @param {number} z
     * @param {number} feedrate
     * @returns {Promise<void>}
     */
    async moveTo(x, y, z, feedrate) {
        this.#validateNumber(x, 'x');
        this.#validateNumber(y, 'y');
        this.#validateNumber(z, 'z');
        this.#validateNumber(feedrate, 'feedrate');
        const cmd = `G1 X${x} Y${y} Z${z} F${feedrate}`;
        await this.sendCommand(cmd);
        this.machineState.updatePosition({ X: x, Y: y, Z: z });
    }

    /**
     * Set air for a brush
     * @param {'a'|'b'} brushId
     * @param {boolean} on
     * @returns {Promise<void>}
     */
    async setBrushAir(brushId, on) {
        this.#validateBrushId(brushId);
        const cmd = `M106 P${brushId === 'a' ? 0 : 1} S${on ? 255 : 0}`;
        await this.sendCommand(cmd);
        this.machineState.updateBrushState(brushId, { air: on });
    }

    /**
     * Set paint for a brush
     * @param {'a'|'b'} brushId
     * @param {boolean} on
     * @param {number} [paintValue]
     * @returns {Promise<void>}
     */
    async setBrushPaint(brushId, on, paintValue = undefined) {
        this.#validateBrushId(brushId);
        if (paintValue !== undefined) this.#validateNumber(paintValue, 'paintValue');
        // Example: M280 for servo, or custom command
        const cmd = `M280 P${brushId === 'a' ? 0 : 1} S${on ? (paintValue ?? 50) : 0}`;
        await this.sendCommand(cmd);
        this.machineState.updateBrushState(brushId, { paint: on, ...(paintValue !== undefined ? { paintValue } : {}) });
    }

    /**
     * Enable or disable motors
     * @param {boolean} enabled
     * @returns {Promise<void>}
     */
    async setMotorsEnabled(enabled) {
        const cmd = enabled ? 'M17' : 'M18';
        await this.sendCommand(cmd);
        this.machineState.updateMotorState({ enabled });
    }

    /**
     * Send a raw G-code command
     * @param {string} command
     * @returns {Promise<any>} response
     */
    async sendCommand(command) {
        if (typeof command !== 'string') throw new Error('Command must be a string');
        return this.wsClient.sendCommand(command);
    }

    // --- Validation helpers ---
    #validateNumber(val, name) {
        if (typeof val !== 'number' || isNaN(val)) throw new Error(`${name} must be a number`);
    }
    #validateBrushId(brushId) {
        if (brushId !== 'a' && brushId !== 'b') throw new Error('Invalid brushId');
    }
}

// Export singleton and class (singleton requires dependencies, so not instantiated here)
export { CommandEngine }; 
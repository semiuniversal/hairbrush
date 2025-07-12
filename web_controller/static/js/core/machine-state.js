/**
 * MachineState Module
 * 
 * A centralized state management system for the H.Airbrush Web Controller.
 * Provides a single source of truth for machine state with observable changes.
 */

/**
 * MachineState class
 * 
 * Manages the state of the machine including:
 * - Position (X, Y, Z)
 * - Brush states (air, paint, paint value)
 * - Motor state (enabled/disabled)
 * - Endstop states
 * - Machine status
 * - Connection status
 */
class MachineState {
    #state;
    #listeners;
    #nextListenerId;

    /**
     * Create a new MachineState instance
     */
    constructor() {
        this.#state = {
            position: { X: 0, Y: 0, Z: 0 },
            brushes: {
                a: { air: false, paint: false, paintValue: 50 },
                b: { air: false, paint: false, paintValue: 50 }
            },
            motors: { enabled: true },
            endstops: { x: false, y: false, z: false },
            machineStatus: 'idle',
            connection: { connected: false, status: 'disconnected' }
        };
        this.#listeners = new Map();
        this.#nextListenerId = 1;
    }

    /**
     * Get a deep copy of the full state
     * @returns {Object}
     */
    getFullState() {
        return JSON.parse(JSON.stringify(this.#state));
    }

    /**
     * Get the current position
     * @returns {Object}
     */
    getPosition() {
        return { ...this.#state.position };
    }

    /**
     * Get the state of a specific brush
     * @param {string} brushId
     * @returns {Object}
     */
    getBrushState(brushId) {
        if (!this.#state.brushes[brushId]) {
            throw new Error(`Invalid brush ID: ${brushId}`);
        }
        return { ...this.#state.brushes[brushId] };
    }

    /**
     * Get all brush states
     * @returns {Object}
     */
    getAllBrushStates() {
        return JSON.parse(JSON.stringify(this.#state.brushes));
    }

    /**
     * Get the motor state
     * @returns {Object}
     */
    getMotorState() {
        return { ...this.#state.motors };
    }

    /**
     * Get the endstop states
     * @returns {Object}
     */
    getEndstopStates() {
        return { ...this.#state.endstops };
    }

    /**
     * Get the machine status
     * @returns {string}
     */
    getMachineStatus() {
        return this.#state.machineStatus;
    }

    /**
     * Get the connection status
     * @returns {Object}
     */
    getConnectionStatus() {
        return { ...this.#state.connection };
    }

    /**
     * Update the machine position
     * @param {Object} position
     * @returns {MachineState}
     */
    updatePosition(position) {
        this.#validatePosition(position);
        this.#updateState('position', { ...this.#state.position, ...position });
        return this;
    }

    /**
     * Update a brush's state
     * @param {string} brushId
     * @param {Object} state
     * @returns {MachineState}
     */
    updateBrushState(brushId, state) {
        if (!this.#state.brushes[brushId]) {
            throw new Error(`Invalid brush ID: ${brushId}`);
        }
        this.#validateBrushState(state);
        const updatedBrushes = {
            ...this.#state.brushes,
            [brushId]: { ...this.#state.brushes[brushId], ...state }
        };
        this.#updateState('brushes', updatedBrushes);
        return this;
    }

    /**
     * Update the motor state
     * @param {Object} state
     * @returns {MachineState}
     */
    updateMotorState(state) {
        this.#validateMotorState(state);
        this.#updateState('motors', { ...this.#state.motors, ...state });
        return this;
    }

    /**
     * Update the endstop states
     * @param {Object} endstops
     * @returns {MachineState}
     */
    updateEndstops(endstops) {
        this.#validateEndstops(endstops);
        this.#updateState('endstops', { ...this.#state.endstops, ...endstops });
        return this;
    }

    /**
     * Update the machine status
     * @param {string} status
     * @returns {MachineState}
     */
    updateMachineStatus(status) {
        this.#validateMachineStatus(status);
        this.#updateState('machineStatus', status);
        return this;
    }

    /**
     * Update the connection status
     * @param {boolean} connected
     * @param {string} status
     * @returns {MachineState}
     */
    updateConnectionStatus(connected, status = null) {
        const newStatus = status || (connected ? 'connected' : 'disconnected');
        this.#updateState('connection', { connected, status: newStatus });
        return this;
    }

    /**
     * Update the state from server data
     * @param {Object} data
     * @returns {MachineState}
     */
    updateFromServerData(data) {
        const updates = {};
        if (data.position) {
            this.#validatePosition(data.position);
            updates.position = { ...this.#state.position, ...data.position };
        }
        if (data.brush_state) {
            updates.brushes = { ...this.#state.brushes };
            if (data.brush_state.a) {
                this.#validateBrushState(data.brush_state.a);
                updates.brushes.a = { ...updates.brushes.a, ...data.brush_state.a };
            }
            if (data.brush_state.b) {
                this.#validateBrushState(data.brush_state.b);
                updates.brushes.b = { ...updates.brushes.b, ...data.brush_state.b };
            }
        }
        if (data.motors_state) {
            updates.motors = { ...this.#state.motors, enabled: data.motors_state === 'enabled' };
        }
        if (data.endstops) {
            this.#validateEndstops(data.endstops);
            updates.endstops = { ...this.#state.endstops, ...data.endstops };
        }
        if (data.state) {
            this.#validateMachineStatus(data.state);
            updates.machineStatus = data.state;
        }
        if (Object.keys(updates).length > 0) {
            this.#batchUpdate(updates);
        }
        return this;
    }

    /**
     * Add a state change listener
     * @param {Function} callback
     * @param {Array<string>} filterPaths
     * @returns {number}
     */
    addListener(callback, filterPaths = null) {
        const id = this.#nextListenerId++;
        this.#listeners.set(id, { callback, filterPaths });
        return id;
    }

    /**
     * Remove a state change listener
     * @param {number} id
     * @returns {boolean}
     */
    removeListener(id) {
        return this.#listeners.delete(id);
    }

    /**
     * Internal: update a specific path in the state
     * @private
     */
    #updateState(path, value) {
        const oldState = this.#state;
        this.#state = { ...oldState, [path]: value };
        this.#notifyListeners([path]);
    }

    /**
     * Internal: batch update multiple paths
     * @private
     */
    #batchUpdate(updates) {
        if (Object.keys(updates).length === 0) return;
        const oldState = this.#state;
        this.#state = { ...oldState, ...updates };
        this.#notifyListeners(Object.keys(updates));
    }

    /**
     * Internal: notify listeners of state changes
     * @private
     */
    #notifyListeners(changedPaths) {
        const state = this.getFullState();
        this.#listeners.forEach(({ callback, filterPaths }, id) => {
            if (!filterPaths) {
                try {
                    callback(state, changedPaths);
                } catch (err) {
                    // Swallow errors in listeners
                }
                return;
            }
            const paths = Array.isArray(filterPaths) ? filterPaths : [filterPaths];
            const relevantChanges = changedPaths.filter(path => paths.includes(path));
            if (relevantChanges.length > 0) {
                try {
                    callback(state, relevantChanges);
                } catch (err) {
                    // Swallow errors in listeners
                }
            }
        });
    }

    /**
     * Internal: validate position data
     * @private
     */
    #validatePosition(position) {
        if (position === null || typeof position !== 'object') {
            throw new Error('Position must be an object');
        }
        ['X', 'Y', 'Z'].forEach(axis => {
            if (position[axis] !== undefined && typeof position[axis] !== 'number') {
                throw new Error(`Position ${axis} must be a number`);
            }
        });
    }

    /**
     * Internal: validate brush state
     * @private
     */
    #validateBrushState(state) {
        if (state === null || typeof state !== 'object') {
            throw new Error('Brush state must be an object');
        }
        if (state.air !== undefined && typeof state.air !== 'boolean') {
            throw new Error('Brush air state must be a boolean');
        }
        if (state.paint !== undefined && typeof state.paint !== 'boolean') {
            throw new Error('Brush paint state must be a boolean');
        }
        if (state.paintValue !== undefined) {
            if (typeof state.paintValue !== 'number') {
                throw new Error('Brush paint value must be a number');
            }
            if (state.paintValue < 0 || state.paintValue > 100) {
                throw new Error('Brush paint value must be between 0 and 100');
            }
        }
    }

    /**
     * Internal: validate motor state
     * @private
     */
    #validateMotorState(state) {
        if (state === null || typeof state !== 'object') {
            throw new Error('Motor state must be an object');
        }
        if (state.enabled !== undefined && typeof state.enabled !== 'boolean') {
            throw new Error('Motor enabled state must be a boolean');
        }
    }

    /**
     * Internal: validate endstop states
     * @private
     */
    #validateEndstops(endstops) {
        if (endstops === null || typeof endstops !== 'object') {
            throw new Error('Endstop states must be an object');
        }
        ['x', 'y', 'z'].forEach(axis => {
            if (endstops[axis] !== undefined && typeof endstops[axis] !== 'boolean') {
                throw new Error(`Endstop ${axis} state must be a boolean`);
            }
        });
    }

    /**
     * Internal: validate machine status
     * @private
     */
    #validateMachineStatus(status) {
        if (typeof status !== 'string') {
            throw new Error('Machine status must be a string');
        }
        const validStatuses = ['idle', 'printing', 'paused', 'error', 'busy', 'unknown'];
        if (!validStatuses.includes(status)) {
            // Allow unknown status but warn
        }
    }
}

// Export singleton and class for testability
export const machineState = new MachineState();
export { MachineState };

// For CommonJS compatibility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { machineState };
} 
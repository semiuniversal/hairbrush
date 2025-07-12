// EventManager utility for decoupled, testable event handling
// Implements a simple publish/subscribe pattern

/**
 * EventManager class
 * Allows registering, emitting, and removing event listeners by event name
 */
class EventManager {
    constructor() {
        this._listeners = new Map(); // eventName -> Set of callbacks
    }

    /**
     * Register a listener for an event
     * @param {string} eventName
     * @param {Function} callback
     */
    on(eventName, callback) {
        if (!this._listeners.has(eventName)) {
            this._listeners.set(eventName, new Set());
        }
        this._listeners.get(eventName).add(callback);
    }

    /**
     * Remove a listener for an event
     * @param {string} eventName
     * @param {Function} callback
     */
    off(eventName, callback) {
        if (this._listeners.has(eventName)) {
            this._listeners.get(eventName).delete(callback);
            if (this._listeners.get(eventName).size === 0) {
                this._listeners.delete(eventName);
            }
        }
    }

    /**
     * Emit an event to all listeners
     * @param {string} eventName
     * @param {...any} args
     */
    emit(eventName, ...args) {
        if (this._listeners.has(eventName)) {
            for (const cb of this._listeners.get(eventName)) {
                try {
                    cb(...args);
                } catch (err) {
                    // Swallow errors in listeners
                }
            }
        }
    }

    /**
     * Remove all listeners for all events
     */
    removeAll() {
        this._listeners.clear();
    }
}

// Export singleton and class
const eventManager = new EventManager();
export { EventManager, eventManager }; 
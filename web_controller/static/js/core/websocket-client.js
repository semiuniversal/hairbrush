// WebSocketClient module for connection management and command sending
// No UI or DOM dependencies

/**
 * WebSocketClient class
 * Handles connection, command sending, and event emission
 */
class WebSocketClient {
    /**
     * @param {string} url - WebSocket server URL
     */
    constructor(url) {
        this.url = url;
        this.ws = null;
        this._listeners = new Map(); // eventName -> Set of callbacks
        this._connected = false;
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        if (this.ws) return;
        this.ws = new globalThis.WebSocket(this.url);
        this.ws.onopen = () => {
            this._connected = true;
            this._emit('open');
        };
        this.ws.onclose = () => {
            this._connected = false;
            this._emit('close');
            this.ws = null;
        };
        this.ws.onerror = (err) => {
            this._emit('error', err);
        };
        this.ws.onmessage = (msg) => {
            let data = msg.data;
            try { data = JSON.parse(msg.data); } catch {}
            this._emit('message', data);
        };
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * Send a command (string or object)
     * @param {string|Object} command
     * @returns {Promise<any>} Resolves with response or undefined
     */
    sendCommand(command) {
        if (!this._connected || !this.ws) throw new Error('WebSocket not connected');
        const msg = typeof command === 'string' ? command : JSON.stringify(command);
        this.ws.send(msg);
        // For testability, just resolve immediately (real impl would handle response)
        return Promise.resolve();
    }

    /**
     * Register an event listener
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
     * Remove an event listener
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
     * Internal: emit an event
     * @private
     */
    _emit(eventName, ...args) {
        if (this._listeners.has(eventName)) {
            for (const cb of this._listeners.get(eventName)) {
                try { cb(...args); } catch {}
            }
        }
    }

    /**
     * Is the client connected?
     * @returns {boolean}
     */
    isConnected() {
        return this._connected;
    }
}

export { WebSocketClient }; 
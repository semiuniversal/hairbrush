// ErrorHandler module for consistent error handling and recovery
// No UI or DOM dependencies

import { eventManager } from '../event-manager.js';

/**
 * ErrorHandler class
 * Categorizes errors, logs, emits events, and provides recovery hooks
 */
class ErrorHandler {
    /**
     * Log an error (to console or external system)
     * @param {Error|string} error
     * @param {string} [context]
     */
    log(error, context = '') {
        const msg = (error instanceof Error ? error.message : error) + (context ? ` [${context}]` : '');
        // In production, send to external logger if needed
        console.error('[ErrorHandler]', msg);
    }

    /**
     * Emit an error event for UI feedback
     * @param {Error|string} error
     * @param {string} [severity] - 'info' | 'warn' | 'error'
     * @param {string} [context]
     */
    emit(error, severity = 'error', context = '') {
        eventManager.emit('error', {
            message: error instanceof Error ? error.message : error,
            severity,
            context
        });
    }

    /**
     * Handle an error (log, emit, and optionally recover)
     * @param {Error|string} error
     * @param {Object} [opts]
     * @param {string} [opts.severity]
     * @param {string} [opts.context]
     * @param {Function} [opts.recover] - Optional recovery callback
     */
    handle(error, opts = {}) {
        this.log(error, opts.context);
        this.emit(error, opts.severity || 'error', opts.context);
        if (opts.recover && typeof opts.recover === 'function') {
            try { opts.recover(); } catch (e) { this.log(e, 'ErrorHandler.recover'); }
        }
    }

    /**
     * Categorize an error by type/severity
     * @param {Error|string} error
     * @returns {string} category
     */
    categorize(error) {
        const msg = error instanceof Error ? error.message : String(error);
        if (/timeout|network/i.test(msg)) return 'network';
        if (/not found|404/i.test(msg)) return 'not_found';
        if (/unauthorized|forbidden|401|403/i.test(msg)) return 'auth';
        if (/validation|invalid/i.test(msg)) return 'validation';
        return 'general';
    }
}

// Export singleton and class
const errorHandler = new ErrorHandler();
export { ErrorHandler, errorHandler }; 
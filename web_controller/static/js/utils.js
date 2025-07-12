/**
 * Utilities for H.Airbrush Web Controller
 * Common functions that can be reused across the application
 */

/**
 * Debounce function to limit the rate at which a function can fire
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait between calls
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

/**
 * Format a number with specified precision
 * @param {number} num - Number to format
 * @param {number} precision - Decimal precision
 * @returns {string} Formatted number
 */
export function formatNumber(num, precision = 2) {
    return Number(num).toFixed(precision);
}

/**
 * Calculate servo angle from percentage for brush control
 * @param {number} percentage - Percentage value (0-100)
 * @param {Object} brush - Brush configuration
 * @returns {number} Servo angle
 */
export function calculateServoAngle(percentage, brush) {
    if (!brush || typeof percentage !== 'number') return 0;
    
    const min = brush.paint_min || 0;
    const max = brush.paint_max || 90;
    const range = max - min;
    
    // Convert percentage to angle
    return min + (percentage / 100) * range;
}

/**
 * Calculate percentage from servo angle for brush control
 * @param {number} angle - Servo angle
 * @param {Object} brush - Brush configuration
 * @returns {number} Percentage value (0-100)
 */
export function calculatePercentage(angle, brush) {
    if (!brush || typeof angle !== 'number') return 0;
    
    const min = brush.paint_min || 0;
    const max = brush.paint_max || 90;
    const range = max - min;
    
    if (range === 0) return 0;
    
    // Convert angle to percentage
    const percentage = ((angle - min) / range) * 100;
    return Math.max(0, Math.min(100, percentage));
}

/**
 * Parse a command response from the server
 * @param {Object|string} response - Response from server
 * @returns {Object} Parsed response with status and data
 */
export function parseCommandResponse(response) {
    if (typeof response === 'string') {
        try {
            response = JSON.parse(response);
        } catch (e) {
            return { status: 'error', message: 'Invalid response format', raw: response };
        }
    }
    
    if (!response) {
        return { status: 'error', message: 'Empty response' };
    }
    
    return {
        status: response.status || 'unknown',
        data: response.data || response,
        message: response.message || ''
    };
}

/**
 * Generate a unique ID for tracking elements, events, etc.
 * @returns {string} Unique ID
 */
export function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

/**
 * Check if a value is within a range
 * @param {number} value - Value to check
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean} True if value is within range
 */
export function isInRange(value, min, max) {
    return value >= min && value <= max;
}

/**
 * Clamp a value within a range
 * @param {number} value - Value to clamp
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {number} Clamped value
 */
export function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
} 
// ErrorHandler unit tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ErrorHandler } from './error-handler.js';

// Mock the eventManager module that ErrorHandler imports
vi.mock('../event-manager.js', () => {
    return {
        eventManager: {
            emit: vi.fn()
        }
    };
});

// Import the mocked eventManager
import { eventManager } from '../event-manager.js';

describe('ErrorHandler', () => {
    let handler;
    
    beforeEach(() => {
        // Clear all mocks before each test
        vi.clearAllMocks();
        handler = new ErrorHandler();
        
        // Mock console.error for log tests
        vi.spyOn(console, 'error').mockImplementation(() => {});
    });
    
    afterEach(() => {
        vi.restoreAllMocks();
    });
    
    it('logs errors to console', () => {
        handler.log('test error');
        expect(console.error).toHaveBeenCalled();
    });
    
    it('emits error events with severity and context', () => {
        handler.emit('foo', 'warn', 'ctx');
        expect(eventManager.emit).toHaveBeenCalledWith('error', {
            message: 'foo',
            severity: 'warn',
            context: 'ctx'
        });
    });
    
    it('handles errors and calls recovery function', () => {
        let recovered = false;
        handler.handle('err', { 
            severity: 'info', 
            context: 'ctx', 
            recover: () => { recovered = true; } 
        });
        
        expect(eventManager.emit).toHaveBeenCalled();
        expect(recovered).toBe(true);
    });
    
    it('categorizes errors correctly', () => {
        expect(handler.categorize('timeout error')).toBe('network');
        expect(handler.categorize('404 not found')).toBe('not_found');
        expect(handler.categorize('401 unauthorized')).toBe('auth');
        expect(handler.categorize('validation failed')).toBe('validation');
        expect(handler.categorize('something else')).toBe('general');
    });
}); 
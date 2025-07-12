import { describe, it, expect, vi, beforeEach } from 'vitest';
import { 
    debounce, 
    formatNumber, 
    calculateServoAngle, 
    calculatePercentage, 
    parseCommandResponse,
    generateId,
    isInRange,
    clamp
} from './utils.js';

describe('Utilities', () => {
    describe('debounce', () => {
        beforeEach(() => {
            vi.useFakeTimers();
        });
        
        it('should debounce function calls', () => {
            const func = vi.fn();
            const debouncedFunc = debounce(func, 100);
            
            debouncedFunc();
            debouncedFunc();
            debouncedFunc();
            
            expect(func).not.toHaveBeenCalled();
            
            vi.advanceTimersByTime(100);
            
            expect(func).toHaveBeenCalledTimes(1);
        });
        
        it('should use the latest arguments', () => {
            const func = vi.fn();
            const debouncedFunc = debounce(func, 100);
            
            debouncedFunc('first');
            debouncedFunc('second');
            debouncedFunc('third');
            
            vi.advanceTimersByTime(100);
            
            expect(func).toHaveBeenCalledWith('third');
        });
    });
    
    describe('formatNumber', () => {
        it('should format numbers with default precision', () => {
            expect(formatNumber(123.456)).toBe('123.46');
            expect(formatNumber(0)).toBe('0.00');
            expect(formatNumber(-45.678)).toBe('-45.68');
        });
        
        it('should format numbers with custom precision', () => {
            expect(formatNumber(123.456, 0)).toBe('123');
            expect(formatNumber(123.456, 1)).toBe('123.5');
            expect(formatNumber(123.456, 4)).toBe('123.4560');
        });
    });
    
    describe('calculateServoAngle', () => {
        it('should calculate servo angle from percentage', () => {
            const brush = { paint_min: 10, paint_max: 90 };
            
            expect(calculateServoAngle(0, brush)).toBe(10);
            expect(calculateServoAngle(50, brush)).toBe(50);
            expect(calculateServoAngle(100, brush)).toBe(90);
        });
        
        it('should handle invalid inputs', () => {
            expect(calculateServoAngle(null, {})).toBe(0);
            expect(calculateServoAngle(50, null)).toBe(0);
        });
    });
    
    describe('calculatePercentage', () => {
        it('should calculate percentage from servo angle', () => {
            const brush = { paint_min: 10, paint_max: 90 };
            
            expect(calculatePercentage(10, brush)).toBe(0);
            expect(calculatePercentage(50, brush)).toBe(50);
            expect(calculatePercentage(90, brush)).toBe(100);
        });
        
        it('should clamp values to 0-100 range', () => {
            const brush = { paint_min: 10, paint_max: 90 };
            
            expect(calculatePercentage(0, brush)).toBe(0);
            expect(calculatePercentage(100, brush)).toBe(100);
        });
        
        it('should handle invalid inputs', () => {
            expect(calculatePercentage(null, {})).toBe(0);
            expect(calculatePercentage(50, null)).toBe(0);
        });
    });
    
    describe('parseCommandResponse', () => {
        it('should parse JSON string responses', () => {
            const response = parseCommandResponse('{"status":"ok","data":{"position":{"X":10}}}');
            
            expect(response.status).toBe('ok');
            expect(response.data.position.X).toBe(10);
        });
        
        it('should handle object responses', () => {
            const response = parseCommandResponse({ status: 'ok', data: { position: { X: 10 } } });
            
            expect(response.status).toBe('ok');
            expect(response.data.position.X).toBe(10);
        });
        
        it('should handle invalid JSON', () => {
            const response = parseCommandResponse('{invalid json}');
            
            expect(response.status).toBe('error');
            expect(response.message).toBe('Invalid response format');
        });
        
        it('should handle empty responses', () => {
            const response = parseCommandResponse(null);
            
            expect(response.status).toBe('error');
            expect(response.message).toBe('Empty response');
        });
    });
    
    describe('generateId', () => {
        it('should generate unique IDs', () => {
            const id1 = generateId();
            const id2 = generateId();
            
            expect(id1).not.toBe(id2);
            expect(typeof id1).toBe('string');
            expect(id1.length).toBeGreaterThan(5);
        });
    });
    
    describe('isInRange', () => {
        it('should check if value is within range', () => {
            expect(isInRange(5, 0, 10)).toBe(true);
            expect(isInRange(0, 0, 10)).toBe(true);
            expect(isInRange(10, 0, 10)).toBe(true);
            expect(isInRange(-1, 0, 10)).toBe(false);
            expect(isInRange(11, 0, 10)).toBe(false);
        });
    });
    
    describe('clamp', () => {
        it('should clamp values to specified range', () => {
            expect(clamp(5, 0, 10)).toBe(5);
            expect(clamp(-5, 0, 10)).toBe(0);
            expect(clamp(15, 0, 10)).toBe(10);
            expect(clamp(0, 0, 10)).toBe(0);
            expect(clamp(10, 0, 10)).toBe(10);
        });
    });
}); 
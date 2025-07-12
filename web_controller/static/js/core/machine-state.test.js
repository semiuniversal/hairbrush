/**
 * MachineState Module Tests
 * 
 * This file demonstrates the usage of the MachineState module
 * and can be used to verify its functionality.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { MachineState } from './machine-state.js';

describe('MachineState', () => {
    let state;
    
    beforeEach(() => {
        state = new MachineState();
    });
    
    it('initializes with default values', () => {
        const full = state.getFullState();
        expect(full.position.X).toBe(0);
        expect(full.position.Y).toBe(0);
        expect(full.position.Z).toBe(0);
        expect(full.brushes.a.paintValue).toBe(50);
        expect(full.brushes.b.paintValue).toBe(50);
        expect(full.motors.enabled).toBe(true);
        expect(full.machineStatus).toBe('idle');
        expect(full.connection.connected).toBe(false);
    });
    
    it('updates position', () => {
        state.updatePosition({ X: 10, Y: 20 });
        const pos = state.getPosition();
        expect(pos.X).toBe(10);
        expect(pos.Y).toBe(20);
    });
    
    it('updates brush state', () => {
        state.updateBrushState('a', { air: true, paint: true });
        const brush = state.getBrushState('a');
        expect(brush.air).toBe(true);
        expect(brush.paint).toBe(true);
    });
    
    it('updates motor state', () => {
        state.updateMotorState({ enabled: false });
        expect(state.getMotorState().enabled).toBe(false);
    });
    
    it('notifies listeners of changes', () => {
        let notified = false;
        let changedPaths = null;
        
        state.addListener((_, paths) => {
            notified = true;
            changedPaths = paths;
        });
        
        state.updatePosition({ X: 42 });
        
        expect(notified).toBe(true);
        expect(changedPaths).toContain('position');
    });
    
    it('allows path-specific listeners', () => {
        let notifiedPosition = false;
        let notifiedBrush = false;
        
        state.addListener(() => { notifiedPosition = true; }, ['position']);
        state.addListener(() => { notifiedBrush = true; }, ['brushes']);
        
        state.updatePosition({ X: 42 });
        expect(notifiedPosition).toBe(true);
        expect(notifiedBrush).toBe(false);
        
        notifiedPosition = false;
        state.updateBrushState('a', { air: true });
        expect(notifiedPosition).toBe(false);
        expect(notifiedBrush).toBe(true);
    });
    
    it('removes listeners by ID', () => {
        let called = false;
        const id = state.addListener(() => { called = true; });
        
        state.removeListener(id);
        state.updatePosition({ X: 99 });
        
        expect(called).toBe(false);
    });
}); 
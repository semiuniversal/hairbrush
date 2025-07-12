/**
 * CommandEngine Module Tests
 * 
 * This file demonstrates the usage of the CommandEngine module
 * and can be used to verify its functionality.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { CommandEngine } from './command-engine.js';

describe('CommandEngine', () => {
    let engine, wsClient, machineState;
    
    beforeEach(() => {
        wsClient = { 
            sendCommand: vi.fn().mockResolvedValue('ok')
        };
        
        machineState = {
            updatePosition: vi.fn(),
            updateBrushState: vi.fn(),
            updateMotorState: vi.fn(),
        };
        
        engine = new CommandEngine({ wsClient, machineState });
    });

    it('moveTo sends correct command and updates state', async () => {
        await engine.moveTo(1, 2, 3, 1000);
        expect(wsClient.sendCommand).toHaveBeenCalledWith('G1 X1 Y2 Z3 F1000');
        expect(machineState.updatePosition).toHaveBeenCalledWith({ X: 1, Y: 2, Z: 3 });
    });

    it('setBrushAir sends correct command and updates state', async () => {
        await engine.setBrushAir('a', true);
        expect(wsClient.sendCommand).toHaveBeenCalledWith('M106 P0 S255');
        expect(machineState.updateBrushState).toHaveBeenCalledWith('a', { air: true });
    });

    it('setBrushPaint sends correct command and updates state', async () => {
        await engine.setBrushPaint('b', false);
        expect(wsClient.sendCommand).toHaveBeenCalledWith('M280 P1 S0');
        expect(machineState.updateBrushState).toHaveBeenCalledWith('b', { paint: false });
    });

    it('setMotorsEnabled sends correct command and updates state', async () => {
        await engine.setMotorsEnabled(false);
        expect(wsClient.sendCommand).toHaveBeenCalledWith('M18');
        expect(machineState.updateMotorState).toHaveBeenCalledWith({ enabled: false });
    });

    it('sendCommand returns wsClient result', async () => {
        const res = await engine.sendCommand('G28');
        expect(res).toBe('ok');
    });

    it('throws on invalid moveTo', () => {
        expect(() => engine.moveTo('x', 2, 3, 1000)).rejects.toThrow();
    });

    it('throws on invalid setBrushAir', () => {
        expect(() => engine.setBrushAir('bad', true)).rejects.toThrow();
    });

    it('throws on invalid setBrushPaint', () => {
        expect(() => engine.setBrushPaint('bad', true)).rejects.toThrow();
    });

    it('throws on invalid sendCommand', () => {
        wsClient.sendCommand = vi.fn().mockImplementation(() => { throw new Error('fail'); });
        expect(() => engine.sendCommand('bad')).rejects.toThrow();
    });
}); 
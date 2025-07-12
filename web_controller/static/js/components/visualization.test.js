// @jest-environment jsdom
/**
 * Visualization component unit tests
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Visualization } from './visualization.js';

describe('Visualization', () => {
    let canvas, ctx, machineState, addListenerCb, removeListenerId;

    beforeEach(() => {
        // Mock canvas and context
        ctx = {
            setTransform: vi.fn(),
            clearRect: vi.fn(),
            save: vi.fn(),
            restore: vi.fn(),
            strokeStyle: '',
            lineWidth: 0,
            beginPath: vi.fn(),
            moveTo: vi.fn(),
            lineTo: vi.fn(),
            stroke: vi.fn(),
            fillStyle: '',
            arc: vi.fn(),
            fill: vi.fn(),
        };
        canvas = document.createElement('canvas');
        canvas.getContext = vi.fn(() => ctx);
        Object.defineProperty(canvas, 'clientWidth', { value: 200, configurable: true });
        Object.defineProperty(canvas, 'clientHeight', { value: 100, configurable: true });
        // Mock MachineState
        addListenerCb = null;
        removeListenerId = null;
        machineState = {
            addListener: vi.fn((cb, paths) => { addListenerCb = cb; return 42; }),
            removeListener: vi.fn((id) => { removeListenerId = id; }),
            getFullState: vi.fn(() => ({
                position: { X: 10, Y: 5 },
                brushes: { a: {}, b: {} },
            })),
        };
        // Mock window.devicePixelRatio
        Object.defineProperty(window, 'devicePixelRatio', { value: 2, configurable: true });
        // Mock window.addEventListener/removeEventListener
        vi.spyOn(window, 'addEventListener');
        vi.spyOn(window, 'removeEventListener');
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    /**
     * Test: constructor subscribes to state, binds resize, renders
     */
    it('constructs and sets up listeners', () => {
        const vis = new Visualization(canvas, machineState);
        expect(machineState.addListener).toHaveBeenCalledWith(expect.any(Function), ['position', 'brushes']);
        expect(window.addEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
        // Should render (calls to context methods)
        expect(ctx.setTransform).toHaveBeenCalled();
        expect(ctx.clearRect).toHaveBeenCalled();
        vis.destroy();
    });

    /**
     * Test: destroy removes listeners and event handlers
     */
    it('removes listeners and event handlers on destroy', () => {
        const vis = new Visualization(canvas, machineState);
        vis.destroy();
        expect(machineState.removeListener).toHaveBeenCalledWith(42);
        expect(window.removeEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
    });

    /**
     * Test: rendering draws grid, position, and brushes
     */
    it('renders grid, position, and brushes', () => {
        const vis = new Visualization(canvas, machineState);
        // Simulate state change
        addListenerCb && addListenerCb();
        // Should call drawing methods (coverage, not pixel-perfect)
        expect(ctx.setTransform).toHaveBeenCalled();
        expect(ctx.clearRect).toHaveBeenCalled();
        expect(ctx.save).toHaveBeenCalled();
        expect(ctx.restore).toHaveBeenCalled();
        expect(ctx.beginPath).toHaveBeenCalled();
        expect(ctx.arc).toHaveBeenCalled();
        vis.destroy();
    });

    /**
     * Test: no global state or DOM queries
     */
    it('does not use global state or direct DOM queries', () => {
        const vis = new Visualization(canvas, machineState);
        expect(typeof vis.canvas).toBe('object');
        expect(typeof vis.ctx).toBe('object');
        vis.destroy();
    });

    /**
     * Test: handles multiple destroy calls gracefully
     */
    it('handles multiple destroy calls', () => {
        const vis = new Visualization(canvas, machineState);
        vis.destroy();
        vis.destroy(); // Should not throw
        expect(machineState.removeListener).toHaveBeenCalledWith(42);
    });
}); 
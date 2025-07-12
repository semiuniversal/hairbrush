import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BrushControl } from './brush-control.js';

describe('BrushControl', () => {
    let control, brushId, elements, commandEngine, machineState;
    
    beforeEach(() => {
        brushId = 'a';
        
        // Mock elements with proper structure
        elements = {
            airToggleBtn: { 
                addEventListener: vi.fn(), 
                removeEventListener: vi.fn(),
                classList: { toggle: vi.fn() }
            },
            paintToggleBtn: { 
                addEventListener: vi.fn(), 
                removeEventListener: vi.fn(),
                classList: { toggle: vi.fn() }
            },
            paintSlider: { 
                addEventListener: vi.fn(), 
                removeEventListener: vi.fn(),
                value: 50
            }
        };
        
        // Mock commandEngine
        commandEngine = {
            setBrushAir: vi.fn(),
            setBrushPaint: vi.fn()
        };
        
        // Mock machineState
        machineState = {
            getBrushState: vi.fn(() => ({ air: false, paint: false, paintValue: 50 })),
            addListener: vi.fn(() => 1),
            removeListener: vi.fn()
        };
        
        control = new BrushControl(brushId, elements, commandEngine, machineState);
    });
    
    it('binds UI event listeners on construction', () => {
        expect(elements.airToggleBtn.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        expect(elements.paintToggleBtn.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        expect(elements.paintSlider.addEventListener).toHaveBeenCalledWith('input', expect.any(Function));
    });
    
    it('subscribes to machine state on construction', () => {
        expect(machineState.addListener).toHaveBeenCalledWith(expect.any(Function), ['brushes']);
    });
    
    it('toggles air when air button is clicked', () => {
        // Get the click handler that was registered
        const clickHandler = elements.airToggleBtn.addEventListener.mock.calls[0][1];
        
        // Simulate a click
        clickHandler();
        
        expect(machineState.getBrushState).toHaveBeenCalledWith(brushId);
        expect(commandEngine.setBrushAir).toHaveBeenCalledWith(brushId, true);
    });
    
    it('toggles paint when paint button is clicked', () => {
        // Get the click handler that was registered
        const clickHandler = elements.paintToggleBtn.addEventListener.mock.calls[0][1];
        
        // Simulate a click
        clickHandler();
        
        expect(machineState.getBrushState).toHaveBeenCalledWith(brushId);
        expect(commandEngine.setBrushPaint).toHaveBeenCalledWith(brushId, true, 50);
    });
    
    it('updates paint value when slider is adjusted', () => {
        // Get the input handler that was registered
        const inputHandler = elements.paintSlider.addEventListener.mock.calls[0][1];
        
        // Simulate input event
        inputHandler({ target: { value: '75' } });
        
        expect(commandEngine.setBrushPaint).toHaveBeenCalledWith(brushId, true, 75);
    });
    
    it('updates UI when brush state changes', () => {
        // Get the state listener that was registered
        const stateListener = machineState.addListener.mock.calls[0][0];
        
        // Simulate state change
        stateListener({
            brushes: {
                a: { air: true, paint: true, paintValue: 80 }
            }
        });
        
        expect(elements.airToggleBtn.classList.toggle).toHaveBeenCalledWith('active', true);
        expect(elements.paintToggleBtn.classList.toggle).toHaveBeenCalledWith('active', true);
        expect(elements.paintSlider.value).toBe(80);
    });
    
    it('removes listeners on destroy', () => {
        control.destroy();
        
        expect(machineState.removeListener).toHaveBeenCalledWith(1);
        expect(elements.airToggleBtn.removeEventListener).toHaveBeenCalled();
        expect(elements.paintToggleBtn.removeEventListener).toHaveBeenCalled();
        expect(elements.paintSlider.removeEventListener).toHaveBeenCalled();
    });
}); 
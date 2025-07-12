// MovementControl unit tests
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MovementControl } from './movement-control.js';

describe('MovementControl', () => {
    let control, elements, commandEngine, machineState;
    
    beforeEach(() => {
        // Mock elements with proper structure
        elements = {
            jogBtns: [
                { 
                    addEventListener: vi.fn(), 
                    removeEventListener: vi.fn(),
                    dataset: { axis: 'X', dir: 'plus' },
                    disabled: false
                },
                { 
                    addEventListener: vi.fn(), 
                    removeEventListener: vi.fn(),
                    dataset: { axis: 'Y', dir: 'minus' },
                    disabled: false
                }
            ],
            homeBtns: [
                { 
                    addEventListener: vi.fn(), 
                    removeEventListener: vi.fn(),
                    dataset: { axis: 'X' },
                    disabled: false
                }
            ],
            speedSelect: { value: '1000' },
            distanceSelect: { value: '10' },
            motorToggleBtn: { 
                addEventListener: vi.fn(), 
                removeEventListener: vi.fn(),
                classList: { toggle: vi.fn() }
            }
        };
        
        // Mock commandEngine
        commandEngine = {
            moveTo: vi.fn(),
            setMotorsEnabled: vi.fn()
        };
        
        // Mock machineState
        machineState = {
            getMotorState: vi.fn(() => ({ enabled: true })),
            addListener: vi.fn(() => 1),
            removeListener: vi.fn()
        };
        
        control = new MovementControl(elements, commandEngine, machineState);
    });
    
    it('binds UI event listeners on construction', () => {
        expect(elements.jogBtns[0].addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        expect(elements.homeBtns[0].addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        expect(elements.motorToggleBtn.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
    });
    
    it('calls moveTo on jog button click', () => {
        // Get the click handler that was registered
        const clickHandler = elements.jogBtns[0]._jogHandler;
        
        // Simulate a click
        clickHandler();
        
        expect(commandEngine.moveTo).toHaveBeenCalledWith(10, 0, 0, 1000);
    });
    
    it('calls moveTo on home button click', () => {
        // Get the click handler that was registered
        const clickHandler = elements.homeBtns[0]._homeHandler;
        
        // Simulate a click
        clickHandler();
        
        expect(commandEngine.moveTo).toHaveBeenCalledWith(0, undefined, undefined, 1000);
    });
    
    it('toggles motors on motor button click', () => {
        // Extract the click handler from the addEventListener mock
        const clickHandler = elements.motorToggleBtn.addEventListener.mock.calls[0][1];
        
        // Simulate a click
        clickHandler();
        
        expect(machineState.getMotorState).toHaveBeenCalled();
        expect(commandEngine.setMotorsEnabled).toHaveBeenCalledWith(false);
    });
    
    it('updates UI when motors are disabled', () => {
        // Get the state listener that was registered
        const stateListener = machineState.addListener.mock.calls[0][0];
        
        // Simulate state change
        stateListener({
            motors: { enabled: false }
        });
        
        expect(elements.jogBtns[0].disabled).toBe(true);
        expect(elements.homeBtns[0].disabled).toBe(true);
        expect(elements.motorToggleBtn.classList.toggle).toHaveBeenCalledWith('active', false);
    });
    
    it('updates UI when motors are enabled', () => {
        // Get the state listener that was registered
        const stateListener = machineState.addListener.mock.calls[0][0];
        
        // Simulate state change
        stateListener({
            motors: { enabled: true }
        });
        
        expect(elements.jogBtns[0].disabled).toBe(false);
        expect(elements.homeBtns[0].disabled).toBe(false);
        expect(elements.motorToggleBtn.classList.toggle).toHaveBeenCalledWith('active', true);
    });
    
    it('removes state listener on destroy', () => {
        control.destroy();
        
        expect(machineState.removeListener).toHaveBeenCalledWith(1);
        expect(elements.jogBtns[0].removeEventListener).toHaveBeenCalled();
        expect(elements.homeBtns[0].removeEventListener).toHaveBeenCalled();
        expect(elements.motorToggleBtn.removeEventListener).toHaveBeenCalled();
    });
}); 
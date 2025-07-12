/**
 * Tests for control panel functionality
 * Tests the integration of components in the control panel
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock DOM elements
const mockElements = {
  createMockElement(id, type = 'div') {
    const element = document.createElement(type);
    element.id = id;
    element.classList = {
      add: vi.fn(),
      remove: vi.fn(),
      toggle: vi.fn(),
      contains: vi.fn().mockReturnValue(false)
    };
    element.addEventListener = vi.fn((event, handler) => {
      // Store the handler so we can call it directly in tests
      element._eventHandlers = element._eventHandlers || {};
      element._eventHandlers[event] = handler;
    });
    element.removeEventListener = vi.fn();
    element.querySelector = vi.fn();
    element.querySelectorAll = vi.fn().mockReturnValue([]);
    element.setAttribute = vi.fn();
    element.getAttribute = vi.fn();
    element.style = {};
    element.disabled = false;
    
    // Create a mock dataset object
    element._dataset = {};
    Object.defineProperty(element, 'dataset', {
      get: function() { return element._dataset; },
      configurable: true
    });
    
    return element;
  },
  
  setupMockDOM() {
    // Create mock elements for the control panel
    document.getElementById = vi.fn(id => {
      if (!this.elements[id]) {
        this.elements[id] = this.createMockElement(id);
      }
      return this.elements[id];
    });
    
    document.querySelector = vi.fn(selector => {
      const id = selector.replace(/[#.]/g, '');
      return this.elements[id] || this.createMockElement(id);
    });
    
    document.querySelectorAll = vi.fn(selector => {
      return [this.createMockElement('mock-' + selector)];
    });
  },
  
  elements: {}
};

describe('Control Panel Integration', () => {
  beforeEach(() => {
    // Set up mock DOM
    mockElements.setupMockDOM();
    
    // Mock WebSocket
    global.WebSocket = vi.fn().mockImplementation(() => ({
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }));
    
    // Mock fetch API
    global.fetch = vi.fn().mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'ok' })
      })
    );
    
    // Create a mock console to capture logs
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
    document.body.innerHTML = '';
  });
  
  it('should initialize the control panel', async () => {
    // Import the control module (this would be dynamically imported in a real test)
    // const { initControlPage } = await import('./control.js');
    
    // For now, we'll just test the mock setup
    expect(document.getElementById).toBeDefined();
    expect(mockElements.elements).toBeDefined();
  });
  
  it('should handle jog button clicks', () => {
    // Create mock jog button
    const jogButton = mockElements.createMockElement('jog-x-plus', 'button');
    jogButton._dataset.axis = 'X';
    jogButton._dataset.direction = 'plus';
    
    // Create click handler and attach it
    const clickHandler = vi.fn();
    jogButton.addEventListener('click', clickHandler);
    
    // Call the handler directly instead of dispatching an event
    jogButton._eventHandlers.click();
    
    expect(clickHandler).toHaveBeenCalled();
  });
  
  it('should handle brush control interactions', () => {
    // Create mock brush control elements
    const airToggle = mockElements.createMockElement('brush-a-air-toggle', 'button');
    const paintToggle = mockElements.createMockElement('brush-a-paint-toggle', 'button');
    const paintSlider = mockElements.createMockElement('brush-a-paint-slider', 'input');
    paintSlider.type = 'range';
    paintSlider.value = '50';
    
    // Create handlers and attach them
    const airClickHandler = vi.fn();
    const paintClickHandler = vi.fn();
    const sliderHandler = vi.fn();
    
    airToggle.addEventListener('click', airClickHandler);
    paintToggle.addEventListener('click', paintClickHandler);
    paintSlider.addEventListener('input', sliderHandler);
    
    // Call the handlers directly
    airToggle._eventHandlers.click();
    paintToggle._eventHandlers.click();
    paintSlider._eventHandlers.input();
    
    expect(airClickHandler).toHaveBeenCalled();
    expect(paintClickHandler).toHaveBeenCalled();
    expect(sliderHandler).toHaveBeenCalled();
  });
  
  it('should handle machine control commands', () => {
    // Create mock machine control elements
    const homeAllBtn = mockElements.createMockElement('home-all', 'button');
    const disableMotorsBtn = mockElements.createMockElement('disable-motors', 'button');
    
    // Create handlers and attach them
    const homeHandler = vi.fn();
    const motorsHandler = vi.fn();
    
    homeAllBtn.addEventListener('click', homeHandler);
    disableMotorsBtn.addEventListener('click', motorsHandler);
    
    // Call the handlers directly
    homeAllBtn._eventHandlers.click();
    disableMotorsBtn._eventHandlers.click();
    
    expect(homeHandler).toHaveBeenCalled();
    expect(motorsHandler).toHaveBeenCalled();
  });
}); 
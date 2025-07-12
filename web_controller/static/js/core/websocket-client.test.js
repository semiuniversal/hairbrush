/**
 * WebSocketClient Module Tests
 * 
 * This file demonstrates the usage of the WebSocketClient module
 * and can be used to verify its functionality.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketClient } from './websocket-client.js';

describe('WebSocketClient', () => {
    let client;
    let mockWebSocket;
    
    beforeEach(() => {
        // Mock WebSocket class
        mockWebSocket = {
            close: vi.fn(),
            send: vi.fn(),
            onopen: null,
            onclose: null,
            onerror: null,
            onmessage: null,
            sent: []
        };
        
        // Mock global WebSocket constructor
        globalThis.WebSocket = vi.fn(() => mockWebSocket);
        
        client = new WebSocketClient('ws://localhost:8080');
    });
    
    afterEach(() => {
        vi.restoreAllMocks();
    });
    
    it('connects and emits open event', async () => {
        let opened = false;
        client.on('open', () => { opened = true; });
        
        client.connect();
        
        // Simulate WebSocket connection opening
        mockWebSocket.onopen();
        
        expect(opened).toBe(true);
        expect(client.isConnected()).toBe(true);
    });
    
    it('sends commands', async () => {
        client.connect();
        mockWebSocket.onopen();
        
        await client.sendCommand('G28');
        
        expect(mockWebSocket.send).toHaveBeenCalledWith('G28');
    });
    
    it('receives messages and emits events', () => {
        let receivedData = null;
        client.on('message', (data) => { receivedData = data; });
        
        client.connect();
        mockWebSocket.onmessage({ data: '{"status":"ok"}' });
        
        expect(receivedData).toEqual({ status: 'ok' });
    });
    
    it('disconnects and emits close event', () => {
        let closed = false;
        client.on('close', () => { closed = true; });
        
        client.connect();
        mockWebSocket.onopen();
        client.disconnect();
        
        // Simulate WebSocket connection closing
        mockWebSocket.onclose();
        
        expect(closed).toBe(true);
        expect(client.isConnected()).toBe(false);
    });
    
    it('emits error event', () => {
        let errorReceived = false;
        client.on('error', () => { errorReceived = true; });
        
        client.connect();
        mockWebSocket.onerror(new Error('Test error'));
        
        expect(errorReceived).toBe(true);
    });
    
    it('handles on/off event registration', () => {
        const callback = vi.fn();
        
        client.on('test', callback);
        client._emit('test', 'data');
        expect(callback).toHaveBeenCalledWith('data');
        
        client.off('test', callback);
        callback.mockClear();
        client._emit('test', 'more data');
        expect(callback).not.toHaveBeenCalled();
    });
}); 
// EventManager unit tests
import { describe, it, expect, beforeEach } from 'vitest';
import { EventManager } from './event-manager.js';

describe('EventManager', () => {
    let mgr;
    beforeEach(() => {
        mgr = new EventManager();
    });

    it('calls listener on emit', () => {
        let called = false;
        mgr.on('foo', () => { called = true; });
        mgr.emit('foo');
        expect(called).toBe(true);
    });

    it('passes arguments to listener', () => {
        let arg1 = null, arg2 = null;
        mgr.on('bar', (a, b) => { arg1 = a; arg2 = b; });
        mgr.emit('bar', 1, 'x');
        expect(arg1).toBe(1);
        expect(arg2).toBe('x');
    });

    it('removes listener', () => {
        let called = false;
        const fn = () => { called = true; };
        mgr.on('baz', fn);
        mgr.off('baz', fn);
        mgr.emit('baz');
        expect(called).toBe(false);
    });

    it('removeAll removes all listeners', () => {
        let called = false;
        mgr.on('a', () => { called = true; });
        mgr.removeAll('a');
        mgr.emit('a');
        expect(called).toBe(false);
    });

    it('calls all listeners for event', () => {
        let count = 0;
        mgr.on('multi', () => { count++; });
        mgr.on('multi', () => { count++; });
        mgr.emit('multi');
        expect(count).toBe(2);
    });
}); 
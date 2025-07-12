# JavaScript Testing for H.Airbrush Frontend

This directory contains unit and integration tests for the browser-based JavaScript modules of the H.Airbrush project.

## Purpose
- Test frontend JS modules in isolation and integration
- Ensure modularity, correctness, and maintainability
- Node.js and npm are **required for testing only** (not for running the app)

## How to Run Tests
- From the project root, run:
  - `python run_js_tests.py` — run JS tests (Vitest)
- Or from this directory:
  - `npm test` — run tests in watch mode
  - `npm run test:run` — run tests once
  - `npm run test:coverage` — run tests with coverage reporting
  - `npm run test:ui` — run tests with UI interface
- The first run will install Node.js dependencies locally in this directory
- To run Python tests, use `pytest` as usual

## Test Organization
- Tests are organized alongside their implementation files
- Core modules: `core/*.test.js`
- Components: `components/*.test.js`
- Event system: `event-manager.test.js`
- Utilities: `utils.test.js`

## Coverage Reports
After running `npm run test:coverage`, coverage reports will be available in:
- Terminal output (text summary)
- `coverage/` directory (HTML reports)

Current coverage metrics:
- Core modules: ~84% statement coverage
- Components: ~100% statement coverage
- Utilities: 100% statement coverage
- Event manager: ~97% statement coverage

## Modular Architecture
The codebase is organized into the following modules:

### Core Modules
- `machine-state.js` - State management for machine position, brushes, motors
- `command-engine.js` - Command abstraction for hardware control
- `websocket-client.js` - WebSocket communication
- `error-handler.js` - Error handling and recovery

### Components
- `brush-control.js` - UI component for brush air/paint control
- `movement-control.js` - UI component for machine movement
- `visualization.js` - UI component for position visualization

### Utilities
- `utils.js` - Common utility functions
- `event-manager.js` - Event management system

## Adding New Tests
1. Create a new file named `[module-name].test.js` next to the module being tested
2. Import the module and testing utilities:
   ```js
   import { describe, it, expect, vi } from 'vitest';
   import { YourModule } from './your-module.js';
   ```
3. Write tests using the describe/it pattern
4. Use vi.mock() for mocking dependencies
5. Run tests to verify

## Notes
- JS dependencies are managed in this directory (`package.json`, `node_modules`)
- The Python/Flask backend is **unaffected** by JS test tooling
- No Node.js server is used or required for the application
- Python and JS tests are run separately for a unified but decoupled workflow 
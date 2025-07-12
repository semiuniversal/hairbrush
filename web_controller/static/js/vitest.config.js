import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Use jsdom for browser environment simulation
    environment: 'jsdom',
    
    // Configure test file patterns
    include: ['**/*.test.js'],
    
    // Ensure ES modules are properly handled
    globals: true,
    
    // Error handling and reporting
    reporters: ['default'],
    
    // Timeout settings
    testTimeout: 10000,
    
    // Clear mocks between tests
    clearMocks: true,
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/**',
        '**/*.config.js',
        '**/README.md',
      ],
    },
    
    // Group tests by directory
    outputFile: {
      json: './test-results.json',
    },
  },
}); 
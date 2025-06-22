# Vendor Dependencies

This directory contains bundled dependencies for the H.Airbrush Inkscape extension. These dependencies are included directly with the extension to avoid modifying Inkscape's Python environment.

## Included Dependencies

- **PyYAML**: Used for parsing YAML configuration files
  - Located in the `yaml` subdirectory

## Why Bundle Dependencies?

Bundling dependencies directly with the extension has several advantages:

1. **No modification to Inkscape's Python environment**: Avoids potential conflicts with other extensions
2. **Consistent behavior**: Ensures the extension works the same way for all users
3. **Simplified installation**: No need for users to install additional Python packages
4. **Version control**: Guarantees compatibility with the specific versions of dependencies that were tested with the extension

## How it Works

The extension's code adds this directory to Python's module search path at runtime, allowing the bundled modules to be imported just like system-installed modules. 
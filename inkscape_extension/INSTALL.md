# H.Airbrush Extension Installation Guide

This guide provides detailed instructions for installing the H.Airbrush extension for Inkscape on different platforms.

## Windows Installation

### Automatic Installation

1. Download the latest release from the GitHub repository
2. Extract the ZIP file to a temporary location
3. Open a Command Prompt or PowerShell window
4. Navigate to the extracted directory
5. Run the installation script:
   ```
   python install.py
   ```
6. If the script cannot find your Inkscape extensions directory, you can specify it manually:
   ```
   python install.py --extensions-dir "C:\Path\To\Inkscape\share\inkscape\extensions"
   ```
7. Restart Inkscape

### Manual Installation

1. Locate your Inkscape extensions directory:
   - Typical locations:
     - `C:\Program Files\Inkscape\share\inkscape\extensions`
     - `%APPDATA%\inkscape\extensions`
   - You can find it in Inkscape by going to Edit > Preferences > System > User extensions
2. Copy the following files and directories to the extensions directory:
   - `hairbrush.inx`
   - `hairbrush_control.py`
   - `hairbrush.py`
   - `hairbrush_lib\` (entire directory)
   - `hairbrush_deps\` (entire directory)
3. Restart Inkscape

## macOS Installation

### Automatic Installation

1. Download the latest release from the GitHub repository
2. Extract the ZIP file to a temporary location
3. Open Terminal
4. Navigate to the extracted directory
5. Run the installation script:
   ```
   python3 install.py
   ```
6. If the script cannot find your Inkscape extensions directory, you can specify it manually:
   ```
   python3 install.py --extensions-dir "/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions"
   ```
7. Restart Inkscape

### Manual Installation

1. Locate your Inkscape extensions directory:
   - Typical location: `/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions`
   - Or: `~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions`
2. Copy the following files and directories to the extensions directory:
   - `hairbrush.inx`
   - `hairbrush_control.py`
   - `hairbrush.py`
   - `hairbrush_lib/` (entire directory)
   - `hairbrush_deps/` (entire directory)
3. Restart Inkscape

## Linux Installation

### Automatic Installation

1. Download the latest release from the GitHub repository
2. Extract the ZIP file to a temporary location
3. Open Terminal
4. Navigate to the extracted directory
5. Run the installation script:
   ```
   python3 install.py
   ```
6. If the script cannot find your Inkscape extensions directory, you can specify it manually:
   ```
   python3 install.py --extensions-dir "/usr/share/inkscape/extensions"
   ```
   or
   ```
   python3 install.py --extensions-dir "~/.config/inkscape/extensions"
   ```
7. Restart Inkscape

### Manual Installation

1. Locate your Inkscape extensions directory:
   - Typical locations:
     - `~/.config/inkscape/extensions` (user-specific)
     - `/usr/share/inkscape/extensions` (system-wide)
2. Copy the following files and directories to the extensions directory:
   - `hairbrush.inx`
   - `hairbrush_control.py`
   - `hairbrush.py`
   - `hairbrush_lib/` (entire directory)
   - `hairbrush_deps/` (entire directory)
3. Restart Inkscape

## Verifying Installation

After installation, you can verify that the extension is properly installed:

1. Open Inkscape
2. Go to Extensions > H.Airbrush > Check Installation
3. If the extension is properly installed, you will see a confirmation message
4. If there are any issues, check the log file:
   - Windows: `%TEMP%\hairbrush_debug.log`
   - macOS/Linux: `/tmp/hairbrush_debug.log`

## Troubleshooting

### Extension Not Showing Up

1. Verify that all files are in the correct location
2. Check that the file permissions are correct (especially on Linux)
3. Look for error messages in the Inkscape console
4. Check the log file for detailed error information

### Permission Issues

1. On Windows, try running the installation script as Administrator
2. On macOS/Linux, use `sudo` if installing to a system-wide directory:
   ```
   sudo python3 install.py --extensions-dir "/usr/share/inkscape/extensions"
   ```

### Python Issues

1. Make sure you have Python 3.6 or later installed
2. On Windows, you may need to use `py` instead of `python`:
   ```
   py install.py
   ```
3. On macOS/Linux, you may need to use `python3` explicitly:
   ```
   python3 install.py
   ```

### Inkscape Version Compatibility

This extension has been tested with Inkscape 1.0 and later. If you are using an older version, you may encounter compatibility issues. 
# TinyG Tester

A testing and configuration tool for TinyG CNC controllers, specifically designed for dual airbrush control systems. This code is highly specific to my custom hardware and may not be suitable for other applications.

## Installation

# Clone the repository
```bash
cd <directory where you want to install tinyg_tester>
git clone <https://github.com/semiuniversal/hairbrush.git>
```

# Install dependencies using poetry
```bash
cd <directory that contains tinyg_tester>
poetry install
```

# Edit your config file
The most critical part is getting the config file correct. The config file is a yaml file that contains the settings for the application. The config file is located in the config directory. There is a sample config file, example.yaml, that you can use as a template.
You need to determine what settings you want to use for your setup. In particular, you need to select the proper serial port for the TinyG controller. The method for determining the serial port is specific to your operating system.

## Usage

# Activate the virtual environment
```bash
cd <directory that contains tinyg_tester>
poetry run python -m tinyg_tester.cli.main --config config/<your config>.yaml
```
The application will start and you can interact with it using the provided commands. The first thing that will happen is that the app will try to connect to the TinyG controller and query the device for its settings. It will then copy any differences from the config file into the TinyG controller.
Next it will enter an interactive mode where you can enter commands to control the TinyG controller.

The commands are as follows:
```bash 
Available Commands:
  M3 S<pos>  - Control Servo 1 position (0-1580)
  servo1pos <pos> - Same as M3
  M4 S<pos>  - Control Servo 2 position (0-1580)
  servo2pos <pos> - Same as M4
  M7         - Turn on air
  airon      - Same as M7
  M9         - Turn off air
  airoff     - Same as M9
  safe       - Move servos to safe position
  help       - Show this help message
  quit/exit  - Exit the program
```

import asyncio
import json
from typing import Optional
import time

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import yaml

from ..controller import TinyGController, TinyGConfig

class CommandRegistry:
    def __init__(self):
        self.commands = {}

    def register(self, name: str, func: callable):
        """Register a new command"""
        self.commands[name] = func

    def execute(self, controller: TinyGController, command: str) -> Optional[str]:
        """Execute a registered command"""
        parts = command.split()
        if not parts:
            return None
        
        cmd_name = parts[0].lower()  # Make commands case-insensitive
        if cmd_name in self.commands:
            return self.commands[cmd_name](controller, *parts[1:])
        return controller.send_command(command)

def validate_servo_position(s: str) -> int:
    """Validate and convert servo position value"""
    try:
        pos = int(s)
        if pos < 0:
            print("Warning: Position below minimum (0), setting to 0")
            return 0
        if pos > 1580:
            print("Warning: Position above maximum (1580), setting to 1580")
            return 1580
        return pos
    except ValueError:
        print("Error: Invalid position value, using 0")
        return 0

def setup_commands(registry: CommandRegistry):
    """Register custom commands"""
    
    def cmd_m3(controller: TinyGController, s: str = "0"):
        """Control Servo 1 position"""
        pos = validate_servo_position(s)
        return controller.send_command(f"M3 S{pos}")
    
    def cmd_m4(controller: TinyGController, s: str = "0"):
        """Control Servo 2 position"""
        pos = validate_servo_position(s)
        return controller.send_command(f"M4 S{pos}")
    
    def cmd_m7(controller: TinyGController):
        """Turn on air"""
        return controller.send_command("M7")
    
    def cmd_m9(controller: TinyGController):
        """Turn off air"""
        return controller.send_command("M9")
    
    def cmd_safe(controller: TinyGController):
        """Move servos to safe position"""
        controller.safe_servo_init()
        return "Servos moved to safe position"

    def cmd_servo1pos(controller: TinyGController, s: str = "0"):
        """Alias for M3"""
        return cmd_m3(controller, s)

    def cmd_servo2pos(controller: TinyGController, s: str = "0"):
        """Alias for M4"""
        return cmd_m4(controller, s)

    def cmd_airon(controller: TinyGController):
        """Alias for M7"""
        return cmd_m7(controller)

    def cmd_airoff(controller: TinyGController):
        """Alias for M9"""
        return cmd_m9(controller)

    def cmd_help(controller: TinyGController):
        """Show available commands"""
        help_text = """
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
"""
        print(help_text)
        return None

    # Register commands
    registry.register("m3", cmd_m3)
    registry.register("servo1pos", cmd_servo1pos)
    registry.register("m4", cmd_m4)
    registry.register("servo2pos", cmd_servo2pos)
    registry.register("m7", cmd_m7)
    registry.register("airon", cmd_airon)
    registry.register("m9", cmd_m9)
    registry.register("airoff", cmd_airoff)
    registry.register("safe", cmd_safe)
    registry.register("help", cmd_help)

def load_config(config_path: str) -> TinyGConfig:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return TinyGConfig(
        port=config_data['port'],
        baud_rate=config_data['baud_rate'],
        config=config_data['tinyg_config']
    )

async def status_display(controller: TinyGController):
    """Display status updates from TinyG"""
    while True:
        try:
            if not controller.status_queue.empty():
                status = controller.status_queue.get()
                if status:
                    print(f"\nStatus: {json.dumps(status, indent=2)}")
        except Exception as e:
            print(f"Error in status display: {e}")
        await asyncio.sleep(0.1)

async def interactive_shell(controller: TinyGController, registry: CommandRegistry):
    """Interactive command shell"""
    session = PromptSession()
    
    print("\nType 'help' for available commands")
    
    while True:
        try:
            with patch_stdout():
                command = await session.prompt_async("TinyG> ")
                
            command = command.strip()
            if not command:
                continue
                
            if command.lower() in ['exit', 'quit']:
                break
                
            response = registry.execute(controller, command)
            if response:
                print(f"Response: {response}")
                
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

@click.command()
@click.option('--config', required=True, help='Path to config YAML file')
def main(config):
    """TinyG Test Application"""
    try:
        # Load configuration
        config_data = load_config(config)
        
        # Initialize controller and commands
        controller = TinyGController(config_data)
        registry = CommandRegistry()
        setup_commands(registry)
        
        # Connect to TinyG
        if not controller.connect():
            return
        
        # Apply configuration
        controller.apply_config()
        
        # Wait a moment before starting status monitor
        time.sleep(1.0)
        
        # Start status monitoring
        controller.start_status_monitor()
        
        # Run interactive shell and status display
        loop = asyncio.get_event_loop()
        loop.create_task(status_display(controller))
        loop.run_until_complete(interactive_shell(controller, registry))
        
    finally:
        if 'controller' in locals():
            controller.stop_status_monitor()
            controller.disconnect()

if __name__ == '__main__':
    main()
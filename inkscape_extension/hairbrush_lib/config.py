"""
Configuration handling for the hairbrush package.
"""

import os
import yaml


def get_config_path():
    """Return the path to the configuration directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")


def load_command_template(template_name="default"):
    """
    Load a command template from the gcode_backend directory.
    
    Args:
        template_name (str): The name of the template file (without extension)
        
    Returns:
        dict: The loaded template as a dictionary
    """
    # Define possible locations for the template file
    possible_paths = [
        # Original relative path (3 levels up from hairbrush_lib)
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "gcode_backend",
            f"{template_name}.yaml"
        ),
        # Original fallback path
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "gcode_backend",
            "command_templates.yaml"
        ),
        # Look in the same directory as the extension
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "gcode_backend",
            "command_templates.yaml"
        ),
        # Look in the Inkscape user directory
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "gcode_backend",
            "command_templates.yaml"
        )
    ]
    
    # Try each path
    for template_path in possible_paths:
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return yaml.safe_load(f)
    
    # If we get here, we couldn't find the template file
    # Create a default template in the extension directory
    default_template = {
        "brush_a": {
            "offset": [0, 0],
            "air_on": "M42 P0 S1",
            "air_off": "M42 P0 S0",
            "paint_on": "M280 P0 S90",
            "paint_off": "M280 P0 S0"
        },
        "brush_b": {
            "offset": [50, 50],
            "air_on": "M42 P1 S1",
            "air_off": "M42 P1 S0",
            "paint_on": "M280 P1 S90",
            "paint_off": "M280 P1 S0"
        }
    }
    
    # Create the directory if it doesn't exist
    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "gcode_backend"
    )
    os.makedirs(template_dir, exist_ok=True)
    
    # Write the default template
    default_path = os.path.join(template_dir, "command_templates.yaml")
    with open(default_path, "w") as f:
        yaml.dump(default_template, f, default_flow_style=False)
    
    return default_template 
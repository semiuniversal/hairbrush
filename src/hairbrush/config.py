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
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "gcode_backend",
        f"{template_name}.yaml"
    )
    
    if not os.path.exists(template_path):
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "gcode_backend",
            "command_templates.yaml"
        )
    
    with open(template_path, "r") as f:
        return yaml.safe_load(f) 
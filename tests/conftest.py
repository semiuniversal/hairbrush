"""
Pytest configuration and shared fixtures for the hairbrush project.
"""
import os
import pytest
import yaml


@pytest.fixture
def sample_svg_path():
    """Return the path to a sample SVG file for testing."""
    return os.path.join(os.path.dirname(__file__), "fixtures", "sample.svg")


@pytest.fixture
def command_template_path():
    """Return the path to the command template YAML file."""
    return os.path.join(os.path.dirname(__file__), "..", "gcode_backend", "command_templates.yaml")


@pytest.fixture
def command_template():
    """Load and return the command template as a dictionary."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "gcode_backend", "command_templates.yaml")
    with open(template_path, "r") as f:
        return yaml.safe_load(f) 
"""
Tests for the command template parser.
"""
import os
import pytest
import yaml


def test_template_file_exists(command_template_path):
    """Test that the command template file exists."""
    assert os.path.exists(command_template_path)


def test_template_loads(command_template):
    """Test that the command template can be loaded."""
    assert command_template is not None
    assert isinstance(command_template, dict)


def test_template_structure(command_template):
    """Test that the command template has the expected structure."""
    # This is a placeholder test - adjust based on actual template structure
    assert "brush_a" in command_template
    assert "brush_b" in command_template
    
    for brush in ["brush_a", "brush_b"]:
        assert "offset" in command_template[brush]
        assert "air_on" in command_template[brush]
        assert "air_off" in command_template[brush]
        assert "paint_on" in command_template[brush]
        assert "paint_off" in command_template[brush] 
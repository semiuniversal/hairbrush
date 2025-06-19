"""
Tests for the SVG parser functionality.
"""
import os
import pytest
from lxml import etree


def test_svg_file_exists(sample_svg_path):
    """Test that the sample SVG file exists."""
    assert os.path.exists(sample_svg_path)


def test_svg_loads():
    """Test that the SVG file can be loaded."""
    # This is a placeholder test - implement actual SVG parsing logic later
    sample_svg_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sample.svg")
    tree = etree.parse(sample_svg_path)
    root = tree.getroot()
    assert root.tag.endswith("svg")


def test_svg_has_layers():
    """Test that the SVG has the expected layers."""
    # This is a placeholder test - implement actual layer detection logic later
    sample_svg_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sample.svg")
    tree = etree.parse(sample_svg_path)
    root = tree.getroot()
    
    # Find all group elements
    groups = root.findall(".//{http://www.w3.org/2000/svg}g")
    
    # Check that we have at least two groups (layers)
    assert len(groups) >= 2
    
    # Check for layers with expected labels
    layer_labels = [g.get("label") for g in groups if g.get("label")]
    assert "black" in layer_labels
    assert "white" in layer_labels 
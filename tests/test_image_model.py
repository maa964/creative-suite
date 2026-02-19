
import pytest
from PySide6.QtGui import QImage, QColor
from PySide6.QtCore import Qt
from apps.image.core.layer_manager import LayerManager, Layer
from apps.image.core.project_io import ProjectIO
import json
import os

def test_project_io(tmp_path):
    # Setup
    manager = LayerManager(200, 150)
    l1 = manager.add_layer("Layer 1")
    l1.opacity = 0.5
    l1.visible = False
    
    # Save
    save_path = tmp_path / "test_project.json"
    ProjectIO.save_project(manager, str(save_path))
    
    assert save_path.exists()
    
    # Verify JSON content
    with open(save_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data["width"] == 200
        assert data["height"] == 150
        assert len(data["layers"]) == 2 # Background + Layer 1
        assert data["layers"][0]["name"] == "Background"
        assert data["layers"][1]["name"] == "Layer 1"
        assert data["layers"][1]["opacity"] == 0.5
        assert data["layers"][1]["visible"] is False

    # Load
    loaded_manager = ProjectIO.load_project(str(save_path))
    
    assert loaded_manager.width == 200
    assert loaded_manager.height == 150
    assert len(loaded_manager.layers) == 2
    
    l_bg = loaded_manager.layers[0]
    l_1 = loaded_manager.layers[1]
    
    assert l_bg.name == "Background"
    
    assert l_1.name == "Layer 1"
    assert l_1.opacity == 0.5
    assert l_1.visible is False
    manager = LayerManager(800, 600)
    assert manager.width == 800
    assert manager.height == 600
    # Should have 1 background layer by default
    assert len(manager.layers) == 1
    assert manager.layers[0].name == "Background"

def test_layer_add_remove():
    manager = LayerManager()
    initial_count = len(manager.layers)
    
    # Add layer
    l1 = manager.add_layer("L1")
    assert len(manager.layers) == initial_count + 1
    assert manager.active_layer == l1
    
    # Remove layer
    manager.remove_layer(l1)
    assert len(manager.layers) == initial_count
    # Active layer should revert to remaining layer (background)
    assert manager.active_layer is not None
    assert manager.active_layer.name == "Background"

def test_layer_move():
    manager = LayerManager()
    l1 = manager.add_layer("L1")
    l2 = manager.add_layer("L2")
    
    # Order: [Background, L1, L2]
    assert manager.layers[0].name == "Background"
    assert manager.layers[1] == l1
    assert manager.layers[2] == l2
    
    # Move L2 to index 0 (bottom)
    manager.move_layer(2, 0)
    # Order: [L2, Background, L1]
    assert manager.layers[0] == l2
    assert manager.layers[1].name == "Background"
    assert manager.layers[2] == l1

def test_layer_properties():
    manager = LayerManager()
    l1 = manager.add_layer("L1")
    
    l1.opacity = 0.5
    assert l1.opacity == 0.5
    
    l1.visible = False
    assert l1.visible is False
    
    l1.name = "Renamed"
    assert l1.name == "Renamed"

def test_add_image_layer():
    manager = LayerManager(100, 100)
    # Create a red image
    img = QImage(50, 50, QImage.Format.Format_ARGB32)
    img.fill(QColor("red"))
    
    l_img = manager.add_image_layer(img, "Imported")
    assert l_img.name == "Imported"
    # Layer is created with canvas size (100x100), not image size
    assert l_img.image.width() == 100
    assert l_img.image.height() == 100

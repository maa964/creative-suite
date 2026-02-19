
import json
import base64
from pathlib import Path
from PySide6.QtGui import QImage
from PySide6.QtCore import QBuffer, QIODevice
from typing import Dict, Any, List

from .layer_manager import LayerManager, Layer

class ProjectIO:
    """
    Handles saving and loading of Image Editor projects.
    Format: Single JSON file with embedded base64 images (for simplicity).
    Future format: Folder or Zip with separate image files.
    """
    
    @staticmethod
    def save_project(layer_manager: LayerManager, file_path: str):
        data = {
            "version": "1.0",
            "width": layer_manager.width,
            "height": layer_manager.height,
            "layers": []
        }
        
        # Save layers bottom-up (as stored in manager)
        for layer in layer_manager.layers:
            layer_data = {
                "name": layer.name,
                "visible": layer.visible,
                "opacity": layer.opacity,
                "offset_x": layer.offset.x(),
                "offset_y": layer.offset.y(),
                "image_data": ProjectIO._encode_image(layer.image)
            }
            data["layers"].append(layer_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_project(file_path: str) -> LayerManager:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        width = data.get("width", 800)
        height = data.get("height", 600)
        
        manager = LayerManager(width, height)
        # Clear default background layer created by init
        # (Though manager implementation might not expose clear/remove all easily, 
        # let's modify manager to support clearing or just remove the default one)
        initial_layers = list(manager.layers)
        for l in initial_layers:
            manager.remove_layer(l)
            
        for layer_data in data.get("layers", []):
            name = layer_data.get("name", "Layer")
            img = ProjectIO._decode_image(layer_data.get("image_data"))
            
            # Create layer
            # Manager's add_image_layer creates a layer of canvas size and draws image at 0,0.
            # But we want to restore offset and exact image content.
            # We'll use low-level add if possible, or create and modify.
            
            # Since add_layer creates empty, we can set image directly.
            layer = manager.add_layer(name, filled=False)
            if img:
                layer.set_image(img)
            
            layer.visible = layer_data.get("visible", True)
            layer.opacity = layer_data.get("opacity", 1.0)
            
            # Restore offset if supported
            # (Layer class has offset property)
            ox = layer_data.get("offset_x", 0)
            oy = layer_data.get("offset_y", 0)
            layer.offset = type(layer.offset)(ox, oy)
            
        return manager

    @staticmethod
    def _encode_image(image: QImage) -> str:
        ba = QBuffer()
        ba.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(ba, "PNG")
        return base64.b64encode(ba.data()).decode('utf-8')

    @staticmethod
    def _decode_image(b64_str: str) -> QImage:
        if not b64_str:
            return None
        data = base64.b64decode(b64_str)
        image = QImage()
        image.loadFromData(data, "PNG")
        return image

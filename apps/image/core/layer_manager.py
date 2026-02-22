
import logging
from typing import List, Optional
from PySide6.QtCore import QObject, Signal, QPoint, Qt
from PySide6.QtGui import QImage, QColor, QPainter

LOG = logging.getLogger(__name__)

class Layer(QObject):
    """
    A single image layer.
    Holds a QImage and properties like visibility, opacity, and blend mode.
    """
    # Signals
    content_changed = Signal()  # Image content changed
    property_changed = Signal() # Metadata (name, visible, opacity) changed

    def __init__(self, name: str, width: int, height: int, parent=None):
        super().__init__(parent)
        self._name = name
        self._visible = True
        self._opacity = 1.0
        self._offset = QPoint(0, 0)
        
        # Initialize transparent image
        self._image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        self._image.fill(Qt.GlobalColor.transparent)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if self._name != value:
            self._name = value
            self.property_changed.emit()

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        if self._visible != value:
            self._visible = value
            self.property_changed.emit()

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        self._opacity = max(0.0, min(1.0, value))
        self.property_changed.emit()

    @property
    def image(self) -> QImage:
        return self._image

    @property
    def offset(self) -> QPoint:
        return self._offset
    
    @offset.setter
    def offset(self, value: QPoint):
        if self._offset != value:
            self._offset = value
            self.property_changed.emit()

    def set_image(self, image: QImage):
        """Replace the internal image, resizing if necessary or keeping as is."""
        self._image = image
        self.content_changed.emit()


class LayerManager(QObject):
    """
    Manages a stack of Layers.
    """
    # Signals
    layer_added = Signal(Layer, int)      # layer, index
    layer_removed = Signal(Layer, int)    # layer, index
    layer_moved = Signal(int, int)        # from_index, to_index
    active_layer_changed = Signal(Layer)  # new_active_layer
    order_changed = Signal()              # Generic order change
    image_size_changed = Signal(int, int)

    def __init__(self, width=800, height=600, parent=None):
        super().__init__(parent)
        self._width = width
        self._height = height
        self._layers: List[Layer] = []
        self._active_layer: Optional[Layer] = None

        # Add initial layer
        self.add_layer("Background", filled=True)

    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    @property
    def layers(self) -> List[Layer]:
        # Return a copy to prevent external modification of the list structure
        return list(self._layers)

    @property
    def active_layer(self) -> Optional[Layer]:
        return self._active_layer

    @active_layer.setter
    def active_layer(self, layer: Layer):
        if layer in self._layers and self._active_layer != layer:
            self._active_layer = layer
            self.active_layer_changed.emit(layer)

    def add_layer(self, name="New Layer", filled=False) -> Layer:
        layer = Layer(name, self._width, self._height, parent=self)
        if filled:
            layer.image.fill(Qt.GlobalColor.white)
        
        # Add to top of stack
        self._layers.append(layer)
        self.layer_added.emit(layer, len(self._layers) - 1)
        self.active_layer = layer
        return layer

    def add_image_layer(self, qimage: QImage, name="Imported Layer") -> Layer:
        # Create layer of canvas size
        layer = Layer(name, self._width, self._height, parent=self)
        
        # Draw imported image onto layer (centered or top-left)
        # For now, just draw at 0,0
        painter = QPainter(layer.image)
        painter.drawImage(0, 0, qimage)
        painter.end()

        self._layers.append(layer)
        self.layer_added.emit(layer, len(self._layers) - 1)
        self.active_layer = layer
        return layer

    def remove_layer(self, layer: Layer):
        if layer in self._layers:
            index = self._layers.index(layer)
            self._layers.remove(layer)
            self.layer_removed.emit(layer, index)
            
            # Update active layer if needed
            if self._active_layer == layer:
                if self._layers:
                    # Select next available layer (logic can be improved)
                    new_idx = min(index, len(self._layers) - 1)
                    self.active_layer = self._layers[new_idx]
                else:
                    self.active_layer = None

    def move_layer(self, from_index: int, to_index: int):
        if 0 <= from_index < len(self._layers) and 0 <= to_index < len(self._layers):
            item = self._layers.pop(from_index)
            self._layers.insert(to_index, item)
            self.layer_moved.emit(from_index, to_index)
            self.order_changed.emit()

    def get_layer_index(self, layer: Layer) -> int:
        if layer in self._layers:
            return self._layers.index(layer)
        return -1

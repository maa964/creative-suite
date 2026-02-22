
import logging
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QPoint
from PySide6.QtGui import QPainter, QPixmap, QTransform, QWheelEvent, QMouseEvent, QPen, QColor, QBrush

from .layer_manager import LayerManager, Layer

LOG = logging.getLogger(__name__)

class ImageCanvas(QGraphicsScene):
    def __init__(self, layer_manager: LayerManager, parent=None):
        super().__init__(parent)
        self._layer_manager = layer_manager
        self._layer_items = {} # Layer -> QGraphicsPixmapItem

        # Checkerboard background
        self.setBackgroundBrush(QBrush(QColor(200, 200, 200), Qt.BrushStyle.DiagCrossPattern))

        # Connect signals
        self._layer_manager.layer_added.connect(self._on_layer_added)
        self._layer_manager.layer_removed.connect(self._on_layer_removed)
        self._layer_manager.order_changed.connect(self._on_order_changed)
        
        # Init scene rect
        self.setSceneRect(0, 0, layer_manager.width, layer_manager.height)
        
        # Initial population
        for layer in layer_manager.layers:
            self._add_layer_item(layer)

    def _add_layer_item(self, layer: Layer):
        pixmap = QPixmap.fromImage(layer.image)
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(layer.offset)
        item.setOpacity(layer.opacity)
        item.setVisible(layer.visible)
        
        self.addItem(item)
        self._layer_items[layer] = item
        
        # Connect layer signals to item updates (using lambda capture)
        layer.content_changed.connect(lambda l=layer: self._update_item_content(l))
        layer.property_changed.connect(lambda l=layer: self._update_item_props(l))
        
        # Ensure correct z-order
        self._on_order_changed()

    def _on_layer_added(self, layer: Layer, index: int):
        self._add_layer_item(layer)

    def _on_layer_removed(self, layer: Layer, index: int):
        if layer in self._layer_items:
            item = self._layer_items[layer]
            self.removeItem(item)
            del self._layer_items[layer]

    def _update_item_content(self, layer: Layer):
        if layer in self._layer_items:
            pixmap = QPixmap.fromImage(layer.image)
            self._layer_items[layer].setPixmap(pixmap)

    def _update_item_props(self, layer: Layer):
        if layer in self._layer_items:
            item = self._layer_items[layer]
            item.setPos(layer.offset)
            item.setOpacity(layer.opacity)
            item.setVisible(layer.visible)

    def _on_order_changed(self):
        # Update z-values based on layer order
        # Layer 0 is bottom, so z=0. Last layer is top.
        layers = self._layer_manager.layers
        for i, layer in enumerate(layers):
            if layer in self._layer_items:
                self._layer_items[layer].setZValue(i)


class ImageCanvasView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        self._is_panning = False
        self._pan_start = QPoint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            if self.dragMode() != QGraphicsView.DragMode.ScrollHandDrag:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().keyReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

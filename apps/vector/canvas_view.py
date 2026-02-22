"""Vector Editor canvas view with tool delegation and zoom."""

from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

from apps.vector.canvas_scene import VectorCanvasScene
from apps.vector.tools import BaseTool, PenTool


class VectorCanvasView(QGraphicsView):
    def __init__(self, scene: VectorCanvasScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._tool: BaseTool | None = None
        self._zoom = 1.0

    def set_tool(self, tool: BaseTool | None):
        if self._tool:
            self._tool.deactivate()
        self._tool = tool
        if self._tool:
            self._tool.activate()

    def mousePressEvent(self, event):
        if self._tool and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            self._tool.mouse_press(scene_pos, event)
            if not isinstance(self._tool, (type(None),)):
                from apps.vector.tools import SelectTool
                if isinstance(self._tool, SelectTool):
                    super().mousePressEvent(event)
                    return
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._tool:
            scene_pos = self.mapToScene(event.position().toPoint())
            self._tool.mouse_move(scene_pos, event)
            from apps.vector.tools import SelectTool
            if isinstance(self._tool, SelectTool):
                super().mouseMoveEvent(event)
                return
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._tool and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            self._tool.mouse_release(scene_pos, event)
            from apps.vector.tools import SelectTool
            if isinstance(self._tool, SelectTool):
                super().mouseReleaseEvent(event)
                return
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if isinstance(self._tool, PenTool):
            self._tool.finalize()
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if isinstance(self._tool, PenTool) and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._tool.finalize()
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            scene = self.scene()
            for item in scene.selectedItems():
                scene.remove_shape(item, undo=True)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        factor = 1.15
        if event.angleDelta().y() > 0:
            self._zoom *= factor
            self.scale(factor, factor)
        elif event.angleDelta().y() < 0:
            self._zoom /= factor
            self.scale(1 / factor, 1 / factor)

    def zoom_in(self):
        factor = 1.25
        self._zoom *= factor
        self.scale(factor, factor)

    def zoom_out(self):
        factor = 1.25
        self._zoom /= factor
        self.scale(1 / factor, 1 / factor)

    def zoom_reset(self):
        self.resetTransform()
        self._zoom = 1.0

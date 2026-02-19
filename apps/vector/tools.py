"""Vector Editor drawing tools."""

from PySide6.QtWidgets import (QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
                                QGraphicsLineItem, QGraphicsPathItem)
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath

from apps.vector.canvas_scene import VectorCanvasScene, MoveItemCommand


class BaseTool:
    def __init__(self, scene: VectorCanvasScene):
        self._scene = scene

    def mouse_press(self, pos: QPointF, event):
        pass

    def mouse_move(self, pos: QPointF, event):
        pass

    def mouse_release(self, pos: QPointF, event):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass


class SelectTool(BaseTool):
    def __init__(self, scene: VectorCanvasScene):
        super().__init__(scene)
        self._moving_item = None
        self._move_start_pos = QPointF()

    def mouse_press(self, pos: QPointF, event):
        from PySide6.QtGui import QTransform
        item = self._scene.itemAt(pos, QTransform())
        if item:
            self._moving_item = item
            self._move_start_pos = item.pos()
        else:
            self._moving_item = None

    def mouse_release(self, pos: QPointF, event):
        if self._moving_item and self._moving_item.pos() != self._move_start_pos:
            cmd = MoveItemCommand(
                self._moving_item, self._move_start_pos, self._moving_item.pos()
            )
            self._scene.undo_stack.push(cmd)
        self._moving_item = None


class RectTool(BaseTool):
    def __init__(self, scene: VectorCanvasScene):
        super().__init__(scene)
        self._start = QPointF()
        self._rect_item = None

    def mouse_press(self, pos: QPointF, event):
        self._start = pos
        self._rect_item = QGraphicsRectItem()
        self._rect_item.setPen(QPen(QColor("#000000"), 2))
        self._rect_item.setBrush(QBrush(QColor("#cccccc")))
        self._rect_item.setRect(QRectF(pos, pos))
        self._scene.addItem(self._rect_item)

    def mouse_move(self, pos: QPointF, event):
        if self._rect_item:
            r = QRectF(self._start, pos).normalized()
            self._rect_item.setRect(r)

    def mouse_release(self, pos: QPointF, event):
        if self._rect_item:
            r = self._rect_item.rect()
            if r.width() < 2 and r.height() < 2:
                self._scene.removeItem(self._rect_item)
            else:
                self._scene.removeItem(self._rect_item)
                self._scene.add_shape(self._rect_item, undo=True)
            self._rect_item = None


class EllipseTool(BaseTool):
    def __init__(self, scene: VectorCanvasScene):
        super().__init__(scene)
        self._start = QPointF()
        self._ellipse_item = None

    def mouse_press(self, pos: QPointF, event):
        self._start = pos
        self._ellipse_item = QGraphicsEllipseItem()
        self._ellipse_item.setPen(QPen(QColor("#000000"), 2))
        self._ellipse_item.setBrush(QBrush(QColor("#cccccc")))
        self._ellipse_item.setRect(QRectF(pos, pos))
        self._scene.addItem(self._ellipse_item)

    def mouse_move(self, pos: QPointF, event):
        if self._ellipse_item:
            r = QRectF(self._start, pos).normalized()
            self._ellipse_item.setRect(r)

    def mouse_release(self, pos: QPointF, event):
        if self._ellipse_item:
            r = self._ellipse_item.rect()
            if r.width() < 2 and r.height() < 2:
                self._scene.removeItem(self._ellipse_item)
            else:
                self._scene.removeItem(self._ellipse_item)
                self._scene.add_shape(self._ellipse_item, undo=True)
            self._ellipse_item = None


class LineTool(BaseTool):
    def __init__(self, scene: VectorCanvasScene):
        super().__init__(scene)
        self._start = QPointF()
        self._line_item = None

    def mouse_press(self, pos: QPointF, event):
        self._start = pos
        self._line_item = QGraphicsLineItem()
        self._line_item.setPen(QPen(QColor("#000000"), 2))
        self._line_item.setLine(QLineF(pos, pos))
        self._scene.addItem(self._line_item)

    def mouse_move(self, pos: QPointF, event):
        if self._line_item:
            self._line_item.setLine(QLineF(self._start, pos))

    def mouse_release(self, pos: QPointF, event):
        if self._line_item:
            line = self._line_item.line()
            if line.length() < 2:
                self._scene.removeItem(self._line_item)
            else:
                self._scene.removeItem(self._line_item)
                self._scene.add_shape(self._line_item, undo=True)
            self._line_item = None


class PenTool(BaseTool):
    def __init__(self, scene: VectorCanvasScene):
        super().__init__(scene)
        self._points: list[QPointF] = []
        self._path_item = None

    def mouse_press(self, pos: QPointF, event):
        self._points.append(pos)
        if len(self._points) == 1:
            self._path_item = QGraphicsPathItem()
            self._path_item.setPen(QPen(QColor("#000000"), 2))
            self._path_item.setBrush(QBrush(Qt.NoBrush))
            self._scene.addItem(self._path_item)
        self._update_path()

    def mouse_move(self, pos: QPointF, event):
        if self._path_item and self._points:
            path = QPainterPath()
            path.moveTo(self._points[0])
            for p in self._points[1:]:
                path.lineTo(p)
            path.lineTo(pos)
            self._path_item.setPath(path)

    def mouse_release(self, pos: QPointF, event):
        pass

    def _update_path(self):
        if not self._path_item or not self._points:
            return
        path = QPainterPath()
        path.moveTo(self._points[0])
        for p in self._points[1:]:
            path.lineTo(p)
        self._path_item.setPath(path)

    def finalize(self):
        if self._path_item and len(self._points) >= 2:
            self._scene.removeItem(self._path_item)
            self._scene.add_shape(self._path_item, undo=True)
        elif self._path_item:
            self._scene.removeItem(self._path_item)
        self._path_item = None
        self._points.clear()

    def deactivate(self):
        self.finalize()

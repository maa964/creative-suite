"""Vector Editor canvas scene with undo/redo support."""

from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide6.QtGui import QBrush, QColor, QPen, QUndoStack, QUndoCommand
from PySide6.QtCore import QPointF


class AddItemCommand(QUndoCommand):
    def __init__(self, scene: "VectorCanvasScene", item: QGraphicsItem, description: str = "Add shape"):
        super().__init__(description)
        self._scene = scene
        self._item = item

    def redo(self):
        self._scene.addItem(self._item)

    def undo(self):
        self._scene.removeItem(self._item)


class RemoveItemCommand(QUndoCommand):
    def __init__(self, scene: "VectorCanvasScene", item: QGraphicsItem, description: str = "Remove shape"):
        super().__init__(description)
        self._scene = scene
        self._item = item

    def redo(self):
        self._scene.removeItem(self._item)

    def undo(self):
        self._scene.addItem(self._item)


class MoveItemCommand(QUndoCommand):
    def __init__(self, item: QGraphicsItem, old_pos: QPointF, new_pos: QPointF,
                 description: str = "Move shape"):
        super().__init__(description)
        self._item = item
        self._old_pos = old_pos
        self._new_pos = new_pos

    def redo(self):
        self._item.setPos(self._new_pos)

    def undo(self):
        self._item.setPos(self._old_pos)

    def id(self):
        return 1

    def mergeWith(self, other):
        if other.id() != self.id():
            return False
        if other._item is not self._item:
            return False
        self._new_pos = other._new_pos
        return True


class PropertyChangeCommand(QUndoCommand):
    def __init__(self, item: QGraphicsItem, prop: str, old_value, new_value,
                 description: str = "Change property"):
        super().__init__(description)
        self._item = item
        self._prop = prop
        self._old_value = old_value
        self._new_value = new_value

    def redo(self):
        self._apply(self._new_value)

    def undo(self):
        self._apply(self._old_value)

    def _apply(self, value):
        if self._prop == "pen":
            self._item.setPen(value)
        elif self._prop == "brush":
            self._item.setBrush(value)
        elif self._prop == "rect":
            self._item.setRect(value)
        elif self._prop == "pos":
            self._item.setPos(value)


class VectorCanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#ffffff")))
        self.setSceneRect(0, 0, 800, 600)
        self._undo_stack = QUndoStack(self)

    @property
    def undo_stack(self) -> QUndoStack:
        return self._undo_stack

    def add_shape(self, item: QGraphicsItem, undo: bool = True):
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.ItemIsMovable, True)
        item.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        if undo:
            self._undo_stack.push(AddItemCommand(self, item))
        else:
            self.addItem(item)

    def remove_shape(self, item: QGraphicsItem, undo: bool = True):
        if undo:
            self._undo_stack.push(RemoveItemCommand(self, item))
        else:
            self.removeItem(item)

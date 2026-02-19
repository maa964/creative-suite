"""Vector Editor data models."""

from enum import Enum, auto
from dataclasses import dataclass, field
from PySide6.QtGui import QColor


class EditorMode(Enum):
    SELECT = auto()
    NODE = auto()
    PEN = auto()
    RECT = auto()
    CIRCLE = auto()
    LINE = auto()


class ShapeType(Enum):
    RECT = "rect"
    ELLIPSE = "ellipse"
    LINE = "line"
    PATH = "path"


@dataclass
class StrokeStyle:
    color: QColor = field(default_factory=lambda: QColor("#000000"))
    width: float = 2.0


@dataclass
class FillStyle:
    color: QColor = field(default_factory=lambda: QColor("#ffffff"))
    enabled: bool = True

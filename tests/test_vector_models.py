"""Unit tests for vector editor data models."""

from apps.vector.models import EditorMode, ShapeType, StrokeStyle, FillStyle
from PySide6.QtGui import QColor


def test_editor_modes():
    modes = list(EditorMode)
    assert EditorMode.SELECT in modes
    assert EditorMode.PEN in modes
    assert EditorMode.RECT in modes
    assert EditorMode.CIRCLE in modes
    assert EditorMode.LINE in modes
    assert EditorMode.NODE in modes


def test_shape_types():
    assert ShapeType.RECT.value == "rect"
    assert ShapeType.ELLIPSE.value == "ellipse"
    assert ShapeType.LINE.value == "line"
    assert ShapeType.PATH.value == "path"


def test_stroke_style_defaults():
    stroke = StrokeStyle()
    assert stroke.color == QColor("#000000")
    assert stroke.width == 2.0


def test_fill_style_defaults():
    fill = FillStyle()
    assert fill.color == QColor("#ffffff")
    assert fill.enabled is True

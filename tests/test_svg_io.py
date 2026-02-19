"""SVG I/O round-trip tests."""

import tempfile
import os
import pytest

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath
from PySide6.QtCore import QRectF, QLineF

from apps.vector.canvas_scene import VectorCanvasScene
from apps.vector.svg_io import save_svg, load_svg, parse_svg_path_d, path_to_svg_d


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_save_and_load_rect(qapp):
    from PySide6.QtWidgets import QGraphicsRectItem
    scene = VectorCanvasScene()
    item = QGraphicsRectItem(10, 20, 100, 50)
    item.setPen(QPen(QColor("#ff0000"), 3))
    item.setBrush(QBrush(QColor("#00ff00")))
    scene.add_shape(item, undo=False)

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        path = f.name
    try:
        assert save_svg(scene, path)

        scene2 = VectorCanvasScene()
        assert load_svg(scene2, path)
        items = scene2.items()
        assert len(items) == 1
        loaded = items[0]
        assert isinstance(loaded, QGraphicsRectItem)
        r = loaded.rect()
        assert abs(r.x() - 10) < 1
        assert abs(r.y() - 20) < 1
        assert abs(r.width() - 100) < 1
        assert abs(r.height() - 50) < 1
    finally:
        os.unlink(path)


def test_save_and_load_ellipse(qapp):
    from PySide6.QtWidgets import QGraphicsEllipseItem
    scene = VectorCanvasScene()
    item = QGraphicsEllipseItem(50, 50, 80, 60)
    item.setPen(QPen(QColor("#0000ff"), 2))
    item.setBrush(QBrush(QColor("#ffff00")))
    scene.add_shape(item, undo=False)

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        path = f.name
    try:
        assert save_svg(scene, path)

        scene2 = VectorCanvasScene()
        assert load_svg(scene2, path)
        items = scene2.items()
        assert len(items) == 1
        loaded = items[0]
        assert isinstance(loaded, QGraphicsEllipseItem)
    finally:
        os.unlink(path)


def test_save_and_load_line(qapp):
    from PySide6.QtWidgets import QGraphicsLineItem
    scene = VectorCanvasScene()
    item = QGraphicsLineItem(QLineF(10, 10, 200, 150))
    item.setPen(QPen(QColor("#333333"), 2))
    scene.add_shape(item, undo=False)

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        path = f.name
    try:
        assert save_svg(scene, path)

        scene2 = VectorCanvasScene()
        assert load_svg(scene2, path)
        items = scene2.items()
        assert len(items) == 1
        loaded = items[0]
        assert isinstance(loaded, QGraphicsLineItem)
    finally:
        os.unlink(path)


def test_save_and_load_path(qapp):
    from PySide6.QtWidgets import QGraphicsPathItem
    scene = VectorCanvasScene()
    pp = QPainterPath()
    pp.moveTo(10, 10)
    pp.lineTo(50, 80)
    pp.lineTo(100, 20)
    item = QGraphicsPathItem(pp)
    item.setPen(QPen(QColor("#000000"), 2))
    item.setBrush(QBrush(QColor("transparent")))
    scene.add_shape(item, undo=False)

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        path = f.name
    try:
        assert save_svg(scene, path)

        scene2 = VectorCanvasScene()
        assert load_svg(scene2, path)
        items = scene2.items()
        assert len(items) == 1
        loaded = items[0]
        assert isinstance(loaded, QGraphicsPathItem)
    finally:
        os.unlink(path)


def test_parse_svg_path_d():
    path = parse_svg_path_d("M 10 20 L 50 80 L 100 30 Z")
    assert path.elementCount() > 0


def test_path_to_svg_d_roundtrip():
    pp = QPainterPath()
    pp.moveTo(10, 20)
    pp.lineTo(50, 80)
    d = path_to_svg_d(pp)
    assert "M" in d
    assert "L" in d

    pp2 = parse_svg_path_d(d)
    assert pp2.elementCount() == pp.elementCount()


def test_load_nonexistent_file(qapp):
    scene = VectorCanvasScene()
    assert not load_svg(scene, "/nonexistent/path/file.svg")


def test_multiple_shapes_roundtrip(qapp):
    from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem
    scene = VectorCanvasScene()
    scene.add_shape(QGraphicsRectItem(10, 10, 50, 50), undo=False)
    scene.add_shape(QGraphicsEllipseItem(100, 100, 60, 40), undo=False)

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        path = f.name
    try:
        assert save_svg(scene, path)

        scene2 = VectorCanvasScene()
        assert load_svg(scene2, path)
        assert len(scene2.items()) == 2
    finally:
        os.unlink(path)

"""SVG file loading and saving for the Vector Editor."""

import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import defusedxml.ElementTree as SafeET
except ImportError:
    SafeET = None

from PySide6.QtWidgets import (QGraphicsRectItem, QGraphicsEllipseItem,
                                QGraphicsLineItem, QGraphicsPathItem)
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath
from PySide6.QtCore import Qt, QRectF, QLineF

from apps.vector.canvas_scene import VectorCanvasScene

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def _parse_color(value: str, default: str = "#000000") -> QColor:
    if not value or value == "none":
        return QColor(Qt.transparent) if value == "none" else QColor(default)
    return QColor(value)


def _parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _apply_style(item, elem: ET.Element):
    fill = elem.get("fill", "#cccccc")
    stroke = elem.get("stroke", "#000000")
    stroke_width = _parse_float(elem.get("stroke-width"), 2.0)

    if fill == "none":
        if hasattr(item, 'setBrush'):
            item.setBrush(QBrush(Qt.NoBrush))
    else:
        if hasattr(item, 'setBrush'):
            item.setBrush(QBrush(_parse_color(fill)))

    pen_color = _parse_color(stroke) if stroke != "none" else QColor(Qt.transparent)
    if hasattr(item, 'setPen'):
        item.setPen(QPen(pen_color, stroke_width))


def _write_style(elem: ET.Element, item):
    if hasattr(item, 'brush'):
        brush = item.brush()
        if brush.style() == Qt.NoBrush:
            elem.set("fill", "none")
        else:
            elem.set("fill", brush.color().name())

    if hasattr(item, 'pen'):
        pen = item.pen()
        if pen.color().alpha() == 0:
            elem.set("stroke", "none")
        else:
            elem.set("stroke", pen.color().name())
        elem.set("stroke-width", f"{pen.widthF():.1f}")


def parse_svg_path_d(d: str) -> QPainterPath:
    """Parse a subset of SVG path d attribute (M, L, Z) into QPainterPath."""
    path = QPainterPath()
    tokens = d.replace(",", " ").split()
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd in ("M", "m"):
            if i + 2 < len(tokens):
                try:
                    x, y = float(tokens[i + 1]), float(tokens[i + 2])
                except ValueError:
                    i += 3
                    continue
                path.moveTo(x, y)
                i += 3
            else:
                break
        elif cmd in ("L", "l"):
            if i + 2 < len(tokens):
                try:
                    x, y = float(tokens[i + 1]), float(tokens[i + 2])
                except ValueError:
                    i += 3
                    continue
                if cmd == "L":
                    path.lineTo(x, y)
                else:
                    cp = path.currentPosition()
                    path.lineTo(cp.x() + x, cp.y() + y)
                i += 3
            else:
                break
        elif cmd in ("Z", "z"):
            path.closeSubpath()
            i += 1
        else:
            # Skip unknown commands
            i += 1
    return path


def path_to_svg_d(path: QPainterPath) -> str:
    """Convert QPainterPath to SVG path d attribute string."""
    parts = []
    for i in range(path.elementCount()):
        elem = path.elementAt(i)
        if elem.type == QPainterPath.ElementType.MoveToElement:
            parts.append(f"M {elem.x:.2f} {elem.y:.2f}")
        elif elem.type == QPainterPath.ElementType.LineToElement:
            parts.append(f"L {elem.x:.2f} {elem.y:.2f}")
        elif elem.type == QPainterPath.ElementType.CurveToElement:
            # Collect all curve control points
            parts.append(f"C {elem.x:.2f} {elem.y:.2f}")
        elif elem.type == QPainterPath.ElementType.CurveToDataElement:
            parts.append(f"{elem.x:.2f} {elem.y:.2f}")
    return " ".join(parts)


def load_svg(scene: VectorCanvasScene, file_path: str) -> bool:
    """Load SVG file, creating QGraphicsItems in the scene."""
    try:
        parse = SafeET.parse if SafeET else ET.parse
        tree = parse(file_path)
    except (ET.ParseError, FileNotFoundError):
        return False

    root = tree.getroot()
    # Update scene rect from SVG dimensions
    w = _parse_float(root.get("width"), 800)
    h = _parse_float(root.get("height"), 600)
    scene.setSceneRect(0, 0, w, h)

    _load_elements(scene, root)
    return True


def _load_elements(scene: VectorCanvasScene, parent: ET.Element):
    for elem in parent:
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if tag == "rect":
            x = _parse_float(elem.get("x"))
            y = _parse_float(elem.get("y"))
            w = _parse_float(elem.get("width"))
            h = _parse_float(elem.get("height"))
            item = QGraphicsRectItem(x, y, w, h)
            _apply_style(item, elem)
            scene.add_shape(item, undo=False)

        elif tag == "ellipse":
            cx = _parse_float(elem.get("cx"))
            cy = _parse_float(elem.get("cy"))
            rx = _parse_float(elem.get("rx"))
            ry = _parse_float(elem.get("ry"))
            item = QGraphicsEllipseItem(cx - rx, cy - ry, rx * 2, ry * 2)
            _apply_style(item, elem)
            scene.add_shape(item, undo=False)

        elif tag == "circle":
            cx = _parse_float(elem.get("cx"))
            cy = _parse_float(elem.get("cy"))
            r = _parse_float(elem.get("r"))
            item = QGraphicsEllipseItem(cx - r, cy - r, r * 2, r * 2)
            _apply_style(item, elem)
            scene.add_shape(item, undo=False)

        elif tag == "line":
            x1 = _parse_float(elem.get("x1"))
            y1 = _parse_float(elem.get("y1"))
            x2 = _parse_float(elem.get("x2"))
            y2 = _parse_float(elem.get("y2"))
            item = QGraphicsLineItem(QLineF(x1, y1, x2, y2))
            _apply_style(item, elem)
            scene.add_shape(item, undo=False)

        elif tag == "path":
            d = elem.get("d", "")
            if d:
                qpath = parse_svg_path_d(d)
                item = QGraphicsPathItem(qpath)
                _apply_style(item, elem)
                scene.add_shape(item, undo=False)

        elif tag == "g":
            _load_elements(scene, elem)


def save_svg(scene: VectorCanvasScene, file_path: str) -> bool:
    """Save scene items to SVG file."""
    rect = scene.sceneRect()
    root = ET.Element("svg")
    root.set("xmlns", SVG_NS)
    root.set("width", str(int(rect.width())))
    root.set("height", str(int(rect.height())))
    root.set("viewBox", f"0 0 {int(rect.width())} {int(rect.height())}")

    for item in scene.items():
        if isinstance(item, QGraphicsRectItem):
            r = item.rect()
            pos = item.pos()
            elem = ET.SubElement(root, "rect")
            elem.set("x", f"{r.x() + pos.x():.2f}")
            elem.set("y", f"{r.y() + pos.y():.2f}")
            elem.set("width", f"{r.width():.2f}")
            elem.set("height", f"{r.height():.2f}")
            _write_style(elem, item)

        elif isinstance(item, QGraphicsEllipseItem):
            r = item.rect()
            pos = item.pos()
            cx = r.x() + pos.x() + r.width() / 2
            cy = r.y() + pos.y() + r.height() / 2
            elem = ET.SubElement(root, "ellipse")
            elem.set("cx", f"{cx:.2f}")
            elem.set("cy", f"{cy:.2f}")
            elem.set("rx", f"{r.width() / 2:.2f}")
            elem.set("ry", f"{r.height() / 2:.2f}")
            _write_style(elem, item)

        elif isinstance(item, QGraphicsLineItem):
            line = item.line()
            pos = item.pos()
            elem = ET.SubElement(root, "line")
            elem.set("x1", f"{line.x1() + pos.x():.2f}")
            elem.set("y1", f"{line.y1() + pos.y():.2f}")
            elem.set("x2", f"{line.x2() + pos.x():.2f}")
            elem.set("y2", f"{line.y2() + pos.y():.2f}")
            _write_style(elem, item)

        elif isinstance(item, QGraphicsPathItem):
            path = item.path()
            d = path_to_svg_d(path)
            if d:
                elem = ET.SubElement(root, "path")
                elem.set("d", d)
                _write_style(elem, item)

    try:
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(file_path, xml_declaration=True, encoding="unicode")
        return True
    except OSError:
        return False

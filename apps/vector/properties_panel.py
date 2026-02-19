"""Vector Editor properties panel for fill, stroke, position, and size."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QDoubleSpinBox, QPushButton, QCheckBox, QGroupBox,
                                QColorDialog, QGraphicsItem, QGraphicsRectItem,
                                QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPathItem)
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt

from apps.vector.canvas_scene import VectorCanvasScene, PropertyChangeCommand


class PropertiesPanel(QWidget):
    def __init__(self, scene: VectorCanvasScene, parent=None):
        super().__init__(parent)
        self._scene = scene
        self._updating = False  # prevent signal loops
        self._setup_ui()
        self._scene.selectionChanged.connect(self._on_selection_changed)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Transform group
        transform_group = QGroupBox("Transform")
        tl = QVBoxLayout(transform_group)

        row_x = QHBoxLayout()
        row_x.addWidget(QLabel("X:"))
        self._spin_x = QDoubleSpinBox()
        self._spin_x.setRange(-9999, 9999)
        self._spin_x.valueChanged.connect(self._on_position_changed)
        row_x.addWidget(self._spin_x)
        tl.addLayout(row_x)

        row_y = QHBoxLayout()
        row_y.addWidget(QLabel("Y:"))
        self._spin_y = QDoubleSpinBox()
        self._spin_y.setRange(-9999, 9999)
        self._spin_y.valueChanged.connect(self._on_position_changed)
        row_y.addWidget(self._spin_y)
        tl.addLayout(row_y)

        row_w = QHBoxLayout()
        row_w.addWidget(QLabel("W:"))
        self._spin_w = QDoubleSpinBox()
        self._spin_w.setRange(0, 9999)
        self._spin_w.valueChanged.connect(self._on_size_changed)
        row_w.addWidget(self._spin_w)
        tl.addLayout(row_w)

        row_h = QHBoxLayout()
        row_h.addWidget(QLabel("H:"))
        self._spin_h = QDoubleSpinBox()
        self._spin_h.setRange(0, 9999)
        self._spin_h.valueChanged.connect(self._on_size_changed)
        row_h.addWidget(self._spin_h)
        tl.addLayout(row_h)

        layout.addWidget(transform_group)

        # Fill group
        fill_group = QGroupBox("Fill")
        fl = QVBoxLayout(fill_group)

        self._fill_enabled = QCheckBox("Enabled")
        self._fill_enabled.setChecked(True)
        self._fill_enabled.toggled.connect(self._on_fill_toggled)
        fl.addWidget(self._fill_enabled)

        fill_row = QHBoxLayout()
        fill_row.addWidget(QLabel("Color:"))
        self._fill_btn = QPushButton()
        self._fill_btn.setFixedSize(60, 24)
        self._fill_color = QColor("#ffffff")
        self._update_color_button(self._fill_btn, self._fill_color)
        self._fill_btn.clicked.connect(self._pick_fill_color)
        fill_row.addWidget(self._fill_btn)
        fl.addLayout(fill_row)

        layout.addWidget(fill_group)

        # Stroke group
        stroke_group = QGroupBox("Stroke")
        sl = QVBoxLayout(stroke_group)

        stroke_color_row = QHBoxLayout()
        stroke_color_row.addWidget(QLabel("Color:"))
        self._stroke_btn = QPushButton()
        self._stroke_btn.setFixedSize(60, 24)
        self._stroke_color = QColor("#000000")
        self._update_color_button(self._stroke_btn, self._stroke_color)
        self._stroke_btn.clicked.connect(self._pick_stroke_color)
        stroke_color_row.addWidget(self._stroke_btn)
        sl.addLayout(stroke_color_row)

        stroke_w_row = QHBoxLayout()
        stroke_w_row.addWidget(QLabel("Width:"))
        self._stroke_width = QDoubleSpinBox()
        self._stroke_width.setRange(0, 100)
        self._stroke_width.setValue(2.0)
        self._stroke_width.setSingleStep(0.5)
        self._stroke_width.valueChanged.connect(self._on_stroke_width_changed)
        stroke_w_row.addWidget(self._stroke_width)
        sl.addLayout(stroke_w_row)

        layout.addWidget(stroke_group)
        layout.addStretch()

    def _update_color_button(self, btn: QPushButton, color: QColor):
        btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #666;")

    def _selected_item(self) -> QGraphicsItem | None:
        items = self._scene.selectedItems()
        return items[0] if items else None

    def _on_selection_changed(self):
        item = self._selected_item()
        if not item:
            return
        self._updating = True
        try:
            br = item.sceneBoundingRect()
            self._spin_x.setValue(br.x())
            self._spin_y.setValue(br.y())
            self._spin_w.setValue(br.width())
            self._spin_h.setValue(br.height())

            if hasattr(item, 'brush'):
                brush = item.brush()
                self._fill_color = brush.color()
                self._fill_enabled.setChecked(brush.style() != Qt.NoBrush)
                self._update_color_button(self._fill_btn, self._fill_color)

            if hasattr(item, 'pen'):
                pen = item.pen()
                self._stroke_color = pen.color()
                self._stroke_width.setValue(pen.widthF())
                self._update_color_button(self._stroke_btn, self._stroke_color)
        finally:
            self._updating = False

    def _on_position_changed(self):
        if self._updating:
            return
        item = self._selected_item()
        if not item:
            return
        br = item.sceneBoundingRect()
        dx = self._spin_x.value() - br.x()
        dy = self._spin_y.value() - br.y()
        old_pos = item.pos()
        new_pos = item.pos()
        new_pos.setX(old_pos.x() + dx)
        new_pos.setY(old_pos.y() + dy)
        self._scene.undo_stack.push(
            PropertyChangeCommand(item, "pos", old_pos, new_pos, "Move")
        )

    def _on_size_changed(self):
        if self._updating:
            return
        item = self._selected_item()
        if not item:
            return
        if isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
            old_rect = item.rect()
            new_rect = old_rect.__class__(old_rect.x(), old_rect.y(),
                                          self._spin_w.value(), self._spin_h.value())
            self._scene.undo_stack.push(
                PropertyChangeCommand(item, "rect", old_rect, new_rect, "Resize")
            )

    def _pick_fill_color(self):
        color = QColorDialog.getColor(self._fill_color, self, "Fill Color")
        if color.isValid():
            self._fill_color = color
            self._update_color_button(self._fill_btn, color)
            item = self._selected_item()
            if item and hasattr(item, 'setBrush'):
                old_brush = item.brush()
                new_brush = QBrush(color)
                self._scene.undo_stack.push(
                    PropertyChangeCommand(item, "brush", old_brush, new_brush, "Change fill")
                )

    def _on_fill_toggled(self, enabled):
        if self._updating:
            return
        item = self._selected_item()
        if item and hasattr(item, 'setBrush'):
            old_brush = item.brush()
            new_brush = QBrush(self._fill_color) if enabled else QBrush(Qt.NoBrush)
            self._scene.undo_stack.push(
                PropertyChangeCommand(item, "brush", old_brush, new_brush, "Toggle fill")
            )

    def _pick_stroke_color(self):
        color = QColorDialog.getColor(self._stroke_color, self, "Stroke Color")
        if color.isValid():
            self._stroke_color = color
            self._update_color_button(self._stroke_btn, color)
            item = self._selected_item()
            if item and hasattr(item, 'setPen'):
                old_pen = item.pen()
                new_pen = QPen(color, old_pen.widthF())
                self._scene.undo_stack.push(
                    PropertyChangeCommand(item, "pen", old_pen, new_pen, "Change stroke color")
                )

    def _on_stroke_width_changed(self, value):
        if self._updating:
            return
        item = self._selected_item()
        if item and hasattr(item, 'setPen'):
            old_pen = item.pen()
            new_pen = QPen(old_pen.color(), value)
            self._scene.undo_stack.push(
                PropertyChangeCommand(item, "pen", old_pen, new_pen, "Change stroke width")
            )

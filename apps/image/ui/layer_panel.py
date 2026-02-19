
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                               QHBoxLayout, QPushButton, QSlider, QLabel, QCheckBox, 
                               QAbstractItemView)
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap

from apps.image.core.layer_manager import LayerManager, Layer

class LayerPanel(QWidget):
    def __init__(self, layer_manager: LayerManager, parent=None):
        super().__init__(parent)
        self._layer_manager = layer_manager
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(5, 5, 5, 5)
        
        # --- Top Controls (Opacity / Blend Mode) ---
        top_layout = QVBoxLayout()
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(100)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self._opacity_slider)
        
        self._visible_cb = QCheckBox("Visible")
        self._visible_cb.setChecked(True)
        self._visible_cb.toggled.connect(self._on_visible_changed)
        
        top_layout.addLayout(opacity_layout)
        top_layout.addWidget(self._visible_cb)
        self._layout.addLayout(top_layout)
        
        # --- Layer List ---
        self._list_widget = QListWidget()
        self._list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        
        # Connect signals
        self._list_widget.currentRowChanged.connect(self._on_row_changed)
        # Note: model rows moved signal is tricky with QListWidget internal move.
        # We might need to rely on button moves for robustness in this iteration, 
        # or implement a full model/view for drag-drop reordering sync.
        # For simplicity/robustness within this task scope, we'll use buttons for ordering 
        # and just display the list. Enabling drag-drop requires careful sync.
        # Let's disable drag-drop reordering for now to avoid state desync bugs, 
        # and provide Up/Down buttons.
        self._list_widget.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)

        self._layout.addWidget(self._list_widget)
        
        # --- Bottom Buttons ---
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("New")
        add_btn.clicked.connect(self._on_add)
        
        del_btn = QPushButton("Del")
        del_btn.clicked.connect(self._on_remove)
        
        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self._on_move_up)
        
        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self._on_move_down)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        
        self._layout.addLayout(btn_layout)

        # --- Signal Connections ---
        self._layer_manager.layer_added.connect(self._refresh_list)
        self._layer_manager.layer_removed.connect(self._refresh_list)
        self._layer_manager.layer_moved.connect(self._refresh_list_keep_selection)
        self._layer_manager.active_layer_changed.connect(self._on_external_active_change)
        self._layer_manager.order_changed.connect(self._refresh_list_keep_selection)

        self._refresh_list()

    def _refresh_list(self):
        self._list_widget.clear()
        # QListWidget: Item 0 is top visually? Usually list goes top-down.
        # Layers: 0 is bottom (background), N is top.
        # We want Top layer at Top of list? Yes, usually.
        # So we iterate reversed.
        layers = self._layer_manager.layers
        for layer in reversed(layers):
            item = QListWidgetItem(layer.name)
            item.setData(Qt.ItemDataRole.UserRole, layer)
            self._list_widget.addItem(item)
        
        self._update_selection_from_manager()
    
    def _refresh_list_keep_selection(self):
        self._refresh_list()

    def _update_selection_from_manager(self):
        active = self._layer_manager.active_layer
        if not active:
            self._list_widget.clearSelection()
            self._update_controls(None)
            return

        # Find item
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == active:
                self._list_widget.setCurrentRow(i)
                self._update_controls(active)
                break

    def _update_controls(self, layer: Layer):
        if not layer:
            self._opacity_slider.setEnabled(False)
            self._visible_cb.setEnabled(False)
        else:
            self._opacity_slider.setEnabled(True)
            self._visible_cb.setEnabled(True)
            self._opacity_slider.blockSignals(True)
            self._opacity_slider.setValue(int(layer.opacity * 100))
            self._opacity_slider.blockSignals(False)
            
            self._visible_cb.blockSignals(True)
            self._visible_cb.setChecked(layer.visible)
            self._visible_cb.blockSignals(False)

    def _on_row_changed(self, row):
        if row < 0:
            self._layer_manager.active_layer = None
            return
            
        item = self._list_widget.item(row)
        layer = item.data(Qt.ItemDataRole.UserRole)
        self._layer_manager.active_layer = layer
        self._update_controls(layer)

    def _on_external_active_change(self, layer):
        self._update_selection_from_manager()

    def _on_opacity_changed(self, value):
        layer = self._layer_manager.active_layer
        if layer:
            layer.opacity = value / 100.0

    def _on_visible_changed(self, checked):
        layer = self._layer_manager.active_layer
        if layer:
            layer.visible = checked

    def _on_add(self):
        # Add new layer
        self._layer_manager.add_layer("Layer {}".format(len(self._layer_manager.layers) + 1))

    def _on_remove(self):
        layer = self._layer_manager.active_layer
        if layer:
            self._layer_manager.remove_layer(layer)

    def _on_move_up(self):
        # Visual Up = Index Increase (since 0 is bottom)
        layer = self._layer_manager.active_layer
        if not layer: return
        
        idx = self._layer_manager.get_layer_index(layer)
        if idx < len(self._layer_manager.layers) - 1:
            self._layer_manager.move_layer(idx, idx + 1)

    def _on_move_down(self):
        # Visual Down = Index Decrease
        layer = self._layer_manager.active_layer
        if not layer: return
        
        idx = self._layer_manager.get_layer_index(layer)
        if idx > 0:
            self._layer_manager.move_layer(idx, idx - 1)

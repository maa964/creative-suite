"""Vector Editor main window."""

from PySide6.QtWidgets import (QToolBar, QFileDialog, QDockWidget, QGraphicsView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QActionGroup, QKeySequence

try:
    from apps.common.base_window import BaseMainWindow
except ImportError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from apps.common.base_window import BaseMainWindow

from apps.vector.models import EditorMode
from apps.vector.canvas_scene import VectorCanvasScene
from apps.vector.canvas_view import VectorCanvasView
from apps.vector.properties_panel import PropertiesPanel
from apps.vector.tools import SelectTool, RectTool, EllipseTool, LineTool, PenTool
from apps.vector import svg_io


class VectorEditorWindow(BaseMainWindow):
    mode_changed = Signal(EditorMode)

    def __init__(self):
        super().__init__(title="Creative Suite - Vector Editor")

        self.current_mode = EditorMode.SELECT

        # Scene & View
        self.scene = VectorCanvasScene(self)
        self.view = VectorCanvasView(self.scene, self)
        self.setCentralWidget(self.view)

        # Tools
        self._tools = {
            EditorMode.SELECT: SelectTool(self.scene),
            EditorMode.RECT: RectTool(self.scene),
            EditorMode.CIRCLE: EllipseTool(self.scene),
            EditorMode.LINE: LineTool(self.scene),
            EditorMode.PEN: PenTool(self.scene),
        }

        # Toolbar
        self._setup_toolbar()

        # Properties Dock
        self._props_panel = PropertiesPanel(self.scene)
        prop_dock = QDockWidget("Properties", self)
        prop_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        prop_dock.setWidget(self._props_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, prop_dock)

        # View menu
        self._setup_view_menu()

        # Undo/Redo
        self._connect_undo_redo()

        # Set initial tool
        self.set_mode(EditorMode.SELECT)

    def _setup_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        self._action_group = QActionGroup(self)
        self._action_group.setExclusive(True)

        actions = [
            ("Select", EditorMode.SELECT),
            ("Pen", EditorMode.PEN),
            ("Rect", EditorMode.RECT),
            ("Circle", EditorMode.CIRCLE),
            ("Line", EditorMode.LINE),
        ]

        for name, mode in actions:
            action = QAction(name, self)
            action.setCheckable(True)
            if mode == self.current_mode:
                action.setChecked(True)
            action.triggered.connect(lambda checked=False, m=mode: self.set_mode(m))
            self._action_group.addAction(action)
            toolbar.addAction(action)

    def _setup_view_menu(self):
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("&View")

        zoom_in = QAction("Zoom &In", self)
        zoom_in.setShortcut(QKeySequence("Ctrl+="))
        zoom_in.triggered.connect(self.view.zoom_in)
        view_menu.addAction(zoom_in)

        zoom_out = QAction("Zoom &Out", self)
        zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out.triggered.connect(self.view.zoom_out)
        view_menu.addAction(zoom_out)

        zoom_reset = QAction("Zoom &Reset", self)
        zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        zoom_reset.triggered.connect(self.view.zoom_reset)
        view_menu.addAction(zoom_reset)

    def _connect_undo_redo(self):
        if hasattr(self, 'set_undo_stack'):
            self.set_undo_stack(self.scene.undo_stack)

    def set_mode(self, mode: EditorMode):
        old_tool = self._tools.get(self.current_mode)
        if old_tool:
            old_tool.deactivate()

        self.current_mode = mode
        new_tool = self._tools.get(mode)
        self.view.set_tool(new_tool)

        if mode == EditorMode.SELECT:
            self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        else:
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

        self.status_bar.showMessage(f"Mode: {mode.name}")
        self.mode_changed.emit(mode)

    def on_new_file(self):
        self.scene.clear()
        self.scene.undo_stack.clear()
        self.scene.setSceneRect(0, 0, 800, 600)
        self.status_bar.showMessage("New canvas created")

    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open SVG", "", "SVG Files (*.svg);;All Files (*)"
        )
        if file_path:
            self.scene.clear()
            self.scene.undo_stack.clear()
            if svg_io.load_svg(self.scene, file_path):
                self.status_bar.showMessage(f"Opened: {file_path}")
            else:
                self.status_bar.showMessage(f"Failed to open: {file_path}")

    def on_save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save SVG", "", "SVG Files (*.svg)"
        )
        if file_path:
            if not file_path.endswith(".svg"):
                file_path += ".svg"
            if svg_io.save_svg(self.scene, file_path):
                self.status_bar.showMessage(f"Saved: {file_path}")
            else:
                self.status_bar.showMessage(f"Failed to save: {file_path}")

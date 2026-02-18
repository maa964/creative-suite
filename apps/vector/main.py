from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QGraphicsView, QGraphicsScene, QToolBar, QStatusBar, QFileDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon, QColor, QPalette, QBrush, QPen, QPainter
from enum import Enum, auto

# Import BaseMainWindow dynamically if needed, but relative import preferred if package structure allows
try:
    from apps.common.base_window import BaseMainWindow
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from apps.common.base_window import BaseMainWindow

class EditorMode(Enum):
    SELECT = auto()
    NODE = auto()
    PEN = auto()
    RECT = auto()
    CIRCLE = auto()

class VectorEditorWindow(BaseMainWindow):
    mode_changed = Signal(EditorMode)

    def __init__(self):
        super().__init__(title="Creative Suite - Vector Editor")
        
        # Current Mode
        self.current_mode = EditorMode.SELECT
        
        # Toolbar
        self.setup_toolbar()
        
        # Main Canvas Area
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#ffffff")))
        self.scene.setSceneRect(0, 0, 800, 600) # A4 size approx
        
        # Draw some demo shapes
        self.scene.addRect(100, 100, 200, 150, QPen(Qt.black), QBrush(Qt.red))
        self.scene.addEllipse(300, 200, 100, 100, QPen(Qt.blue), QBrush(Qt.yellow))
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        self.setCentralWidget(self.view)
        
        # Properties Dock
        from PySide6.QtWidgets import QDockWidget, QLabel
        prop_dock = QDockWidget("Properties", self)
        prop_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        prop_dock.setWidget(QLabel("Properties Panel\n(Fill, Stroke, etc.)"))
        self.addDockWidget(Qt.RightDockWidgetArea, prop_dock)

        self.status_bar.showMessage(f"Mode: {self.current_mode.name}")

    def setup_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        
        actions = [
            ("Select", EditorMode.SELECT),
            ("Node", EditorMode.NODE),
            ("Pen", EditorMode.PEN),
            ("Rect", EditorMode.RECT),
            ("Circle", EditorMode.CIRCLE),
        ]
        
        for name, mode in actions:
            action = QAction(name, self)
            action.setCheckable(True)
            if mode == self.current_mode:
                action.setChecked(True)
            # Use a lambda to capture the mode correctly
            action.triggered.connect(lambda checked=False, m=mode: self.set_mode(m))
            toolbar.addAction(action)
            
            # Grouping for exclusive check behavior would be good here (QActionGroup)
            
    def set_mode(self, mode):
        self.current_mode = mode
        self.status_bar.showMessage(f"Mode: {mode.name}")
        
        if mode == EditorMode.SELECT:
            self.view.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.view.setDragMode(QGraphicsView.NoDrag)
            
    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG Files (*.svg);;All Files (*)")
        if file_path:
            self.status_bar.showMessage(f"Opened SVG: {file_path}")
            # Stub: Implement SVG loading logic here

    def on_save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save SVG", "", "SVG Files (*.svg)")
        if file_path:
            self.status_bar.showMessage(f"Saved SVG to: {file_path}")

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGraphicsView, QGraphicsScene, QToolBar, QStatusBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QColor, QPalette, QBrush, QPen

class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Creative Suite - Vector Editor")
        self.resize(1200, 800)
        
        # Theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#2d2d2d"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        
        # Toolbar
        toolbar = QToolBar("Tools")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.addAction("Select")
        toolbar.addAction("Node")
        toolbar.addAction("Pen")
        toolbar.addAction("Rect")
        toolbar.addAction("Circle")
        
        # Main Canvas Area
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#ffffff")))
        self.scene.setSceneRect(0, 0, 800, 600) # A4 size approx
        
        # Draw some demo shapes
        self.scene.addRect(100, 100, 200, 150, QPen(Qt.black), QBrush(Qt.red))
        self.scene.addEllipse(300, 200, 100, 100, QPen(Qt.blue), QBrush(Qt.yellow))
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints() | 0x1) # Antialiasing (QPainter.Antialiasing is 0x01)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        self.setCentralWidget(self.view)
        
        # Properties Panel
        dock = QWidget()
        dock.setFixedWidth(250)
        dock.setStyleSheet("background-color: #252525; border-left: 1px solid #3d3d3d;")
        # (We would add property widgets here)
        
        # We need a layout helper to put dock on right if we want, 
        # but QMainWindow has DockWidgets. For simplicity let's stick to simple central widget for now
        # OR add a DockWidget properly.
        from PySide6.QtWidgets import QDockWidget, QLabel
        prop_dock = QDockWidget("Properties", self)
        prop_dock.setWidget(QLabel("Properties Panel\n(Fill, Stroke, etc.)"))
        self.addDockWidget(Qt.RightDockWidgetArea, prop_dock)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
